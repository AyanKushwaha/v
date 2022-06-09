#
# KPI definitions. 
# So far only used to display retiming related KPIs.
#
# There is also some code for to enable for debugging 
# of Rave definitions in APC.
# 
# Created by Stefan Hammar in March 2012. 
#
import os
import time

import carmensystems.kpi as k
import carmensystems.rave.api as r #@UnusedImport

from RelTime import RelTime

from carmstd import retiming_basics

RET_WITHOUT_ALT = " Retimed without alt."

def _my_sort_key(val):
    return retiming_basics.get_retimings_as_list(val in ("-", RET_WITHOUT_ALT) and "500:0" or val)

class CustomKPI(k.KPI):
    
    def create(self):
        
        # Get bag        
        try:  
            # Studio version
            from carmstd import bag_handler
            tbh = bag_handler.WindowChains()
            if not tbh.bag:
                self.add(k.KpiValue("Problem to generate:", tbh.warning))
                return 
            cbag = tbh.bag
            self.in_studio = True
            
        except ImportError:
            # APC version
            cbag = r.context("default_context").bag()      
            self.in_studio = False
            
        self.create_retiming_info(cbag)
        self.create_debug(cbag)    
            
            
    def create_retiming_info(self, cbag):    
        """
        Some retiming Statistics.
        """
        if not r.param("apc_pac.consider_retiming_of_flights").value():
            return
        
            
        # The statistics matrix        
        d = {}
        for sleg_bag in cbag.retiming.unique_leg_set():
            if not sleg_bag.retiming.has_possible_retiming() and \
               not sleg_bag.retiming.has_retiming():
                continue
            key = (sleg_bag.retiming.retiming_alternatives() or RET_WITHOUT_ALT, 
                   sleg_bag.retiming.retiming_as_string())
            d[key] = d.get(key, 0) + 1 
        
        alts = sorted(list(set([key[0] for key in d])), key=_my_sort_key) 
        retimings = list(set([key[1] for key in d]))
        for alt in alts:
            if alt != RET_WITHOUT_ALT:
                retimings += retiming_basics.get_retiming_array(alt)
        retimings = list(set(retimings))
        retimings.sort(key=_my_sort_key)

        m1 = []
        for alt in alts:
            tot = 0
            for retiming in retimings:
                v = d.get((alt, retiming), 0)
                if retiming == "-":
                    m1.append(((alt, "Yes"), tot)) 
                    m1.append(((alt, "No"), v))
                else:
                    m1.append(((alt, retiming), v))
                tot += v         
            m1.append(((alt, "Tot"), tot))   
        
        tot = 0
        for retiming in retimings:
            v = sum([d.get((alt, retiming), 0) for alt in alts])
            if retiming == "-":
                m1.append((("Tot", "Yes"), tot))
                m1.append((("Tot", "No"), v))
            else:
                m1.append((("Tot", retiming), v))
            tot += v
        m1.append((("Tot", "Tot"), tot))           
         
        self.add(k.KpiMatrix("Retiming Statistics", m1,  
                             "Ret. Alt.", "Retimed",  "Legs"))
    
        #
        # Find the number of inconsistent retimings and
        # illegal ac-rotations because of retiming
        # in a way that works also in APC. 
        #
        
        def ukey(leg_bag):
            return (leg_bag.leg.flight_carrier(),
                    leg_bag.leg.flight_nr(),
                    leg_bag.leg.start_station(),
                    leg_bag.leg.leg_number(),
                    leg_bag.leg.flight_suffix(),
                    leg_bag.retiming_leg.normalized_scheduled_start_date_utc())
        
        num_incon = 0
        d = {}
        for uleg_bag in cbag.retiming.unique_leg_set():
            st = [leg_bag.retiming_leg.amount_retimed_start().getRep() for 
                  leg_bag in 
                  uleg_bag.atom_set()]
            en = [leg_bag.retiming_leg.amount_retimed_end().getRep() for 
                  leg_bag in 
                  uleg_bag.atom_set()]
            
            if max(st) != min(st) or max(en) != min(en):
                num_incon += 1
            
            d[ukey(uleg_bag)] = (max(st), min(en))    
        
        num_illegal_ac = 0     
        for ac_chain_bag in r.context("ac_rotations").bag().chain_set():
            pv = None
            for ac_leg_bag in ac_chain_bag.atom_set(sort_by="departure"):
                cv = d.get(ukey(ac_leg_bag), (0, 0))
                if pv:
                    mod_ct = cv[0] - pv[1]
                    if mod_ct < 0 and org_ct.getRep() + mod_ct < min_ct.getRep(): #@UndefinedVariable
                        num_illegal_ac += 1 
                min_ct = ac_leg_bag.retiming.min_ac_cxn()                         #@UnusedVariable
                org_ct = ac_leg_bag.retiming.ac_cxn_time_scheduled()              #@UnusedVariable       
                pv = cv
                
        self.add(k.KpiValue("Num inconsistently retimed legs", num_incon))  
        self.add(k.KpiValue("Num illegal AC rotations because of retiming", num_illegal_ac))                     
        
        #             
        # Retiming Regularity Groups.
        #
        
        no_ret = set([(RelTime("0:00"), 
                       RelTime("0:00"))])
        
        ndgr = nngr = negr = 0 
        for reg_gr_bag in cbag.retiming.retiming_group():
            if not reg_gr_bag.retiming.any_active_leg_in_bag():
                continue
            if not reg_gr_bag.retiming.any_possible_retiming_in_bag():
                continue
            
            rets = set((leg_bag.retiming_leg.amount_retimed_start(), 
                        leg_bag.retiming_leg.amount_retimed_end())
                        for leg_bag in
                        reg_gr_bag.atom_set())

            if len(rets) > 1:
                ndgr += 1
            elif rets == no_ret:
                nngr += 1
            else:                
                negr += 1 
                     
        self.add(k.KpiVector("Retiming Regularity Groups",
                             [("not regular", ndgr),
                              ("regularly retimed", negr),
                              ("without retiming", nngr),
                              ("total", ndgr + negr + nngr)],
                              "Groups", "Count"))
        
        self.add(k.KpiValue("Cost for violated regularity", 
                            retiming_basics.regularity_cost_in_bag(cbag)[0]))
  
    def create_debug(self, cbag):     
        """
        To make debugging possible.
        Set the parameter "kpi.debug_file_basename"
        to activate this code. "
        """
        
        try:
            basename = r.param("kpi.debug_file_basename").value()
            
            if not basename: 
                return
        except:
            return
        
        nump = r.param("kpi.debug_file_num")
        num = nump.value()
        nump.setvalue(num + 1)
        
        kwns = ("flight_number", "arrival", "departure", "activity_scheduled_start_time",
                "activity_scheduled_end_time","global_lp_period_start", "global_lp_period_end",
                #"turnout_leg_arrival", "turnin_leg_arrival", "aircraft_change",
                )
        vars = ("retiming_leg.normalized_scheduled_start_date_utc",)
        
        kwos = [r.keyw(kwn) for kwn in kwns] + [r.var(vv) for vv in vars]
              
        kwdir = os.path.expandvars("$CARMTMP/kpi_debug")
        if not os.path.exists(kwdir):
            os.mkdir(kwdir)
        
        try:
            r.keyw("global_sp_name")
            product = "STUDIO"
        except:
            product = "APC"
            
        fn = "%s_%s_%03i__%s" % (basename, product, num, 
                                 "%i%02i%02i_%02i_%02i_%02i" % time.localtime()[:6])
        fp = os.path.join(kwdir, fn)
        
        f = open(fp, "w")
        f.write("  " + ", ".join(kwns + vars) + "\n")
        for chain_bag in cbag.chain_set(sort_by=r.first(r.Level.atom(), "trip.name")):
            f.write("NEW CHAIN\n")
            for trip_bag in chain_bag.gpc_iterators.trip_set(sort_by="trip.start"):
                f.write("TRIP:%s\n" % trip_bag.trip.name())
                for leg_bag in trip_bag.atom_set(sort_by="departure"):
                    f.write("  ")
                    f.write(", ".join(str(item) for item in r.eval(leg_bag, *kwos)))
                    f.write("\n")
                
        self.add(k.KpiValue("Debug file", fn))        
