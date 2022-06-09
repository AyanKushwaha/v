# Major Changes:
# v1.9:  It was decided that publishing will cover the days within the
#        rostering publish period strictly:
#        - carry-ins/outs are not taken into account
#        - any leg that overlaps the period is considered published.
#        This means that code that handled the difference between publish
#        and inform in this regard was removed in this version.
# v1.27: There will be no empty days between wops on a roster.
#        The previous default value for such days was F_DAY.
#        If an empty day should (illegaly) exist, we'll consider it a BL_DAY.
#        (Empty days within wops remain to be legal REST days.)
# v1.29  Added handling of the new crew_publish_info.prev_informed_duty_time
#        field. Will contain the the previous value of duty_time.
# v1.39  Pcat REST has been removed, since no empty days between trips are
#        allowed, regardless if they are within a wop or not.

import os
import time
import traceback

from copy import copy

import Cui
import Gui

from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from Variable import Variable

from tm import TM
import carmensystems.rave.api as R
import carmstd.studio.plan as plan

from carmusr.tracking.informedtemptable import InformedTempTable

from utils.rave import RaveIterator as RI
from utils.rave import RaveEvaluator
from utils.guiutil import UpdateManager

#           Operational Mode        Typical use
SEL_MODES = [ROSTER_PUBLISH,        # Original schedule published by planner.
             INFORM_ALL,            # Check-in/out handled by report server.
             ONLY_INFORM_SELECTION, # Interactive inform performed by tracker.
             ] = range(3)

#------------------------------------------------------------------------------
# Studio/ReportServer entry points
#------------------------------------------------------------------------------

def publish(crew_list=None,
            start_date=None,
            end_date=None,
            area=None,
            context=None,
            sel_mode=INFORM_ALL,
            freeze_x_flag=False):
    """
    Generate crew_publish_info data over specified period, or the publish period.

    crew_list: If specified, a "PUBLISH" operation is assumed, which overwrites
          existing crew_publish_info according to sel_mode.
        Otherwise (the default) this is a "SCHEDULED" operation, 
          normally just appending data to the current crew_publish_info.

    start_date, end date: If specified, they form a period
          (end_date not included) over which the rosters are published.
        Otherwise (the default), the whole plan is used.

    area: Set up for roster selection according to 'crew_list'.
        (empty crew_list): If specified, use the contents of 'area'.
           Otherwise (the default) use the whole plan.
        (non-empty crew_list): If specified, display the listed crew in 'area'.
           Otherwise, "display" in Cui.CuiScriptBuffer.
         
    context: if specified, use its contents instead of setting up a context
        according to 'area' and 'crew_list' as described above.
         
    sel_mode:
        INFORM_ALL -> Update all within (start_date,end_date(.
            Typically used at crew check-in/out, when the 'PUBLISHED' roster is
            has been informed (and delivered). The published is assumed to be
            loaded into 'context'.
        ROSTER_PUBLISH -> Update all within (start_date,end_date(.
            Disregard previous contents.
        ONLY_INFORM_SELECTION -> Update all within (start_date,end_date(, that
            is also covered by a crew entry in 'InformedTempTable'.
    """
    Plan.init(sel_mode=sel_mode)
    generator = Generator(start_date=start_date,
                          end_date=end_date,
                          area=area,
                          crew_list=crew_list,
                          context=context,
                          sel_mode=sel_mode,
                          freeze_x_flag=freeze_x_flag)
    generator.generate()
    return 0
    
#------------------------------------------------------------------------------
# Debugging aids: Studio entry points
#------------------------------------------------------------------------------
    
def pubperiod():
    """
    Debugging: Update crew_publish_info for current planning period.
    """
    UpdateManager.start()
    publish()
    UpdateManager.done()
    return 0
    
def pubcrewperiod():
    """
    Debugging: Update one or more crew's
               crew_publish_info for current planning period.
    """
    crewList = Cui.CuiGetCrew(Cui.gpc_info, Cui.CuiWhichArea, "MARKED")
    UpdateManager.start()
    publish(crewList)
    UpdateManager.done()
    return 0
    
def dumpcrew():
    """
    Debugging: Show dialog with dump of one or more crew's
               crew_publish_info for current planning period.
    """
    import os
    import carmstd.studio.cfhExtensions as ext
    fn = "/tmp/stefanh_activity_map_dump"
    Plan.init()
    dump_start = R.eval('fundamental.%loaded_data_period_start%')[0] - RelTime(24,0)
    dump_end = R.eval('fundamental.%loaded_data_period_end%')[0].day_ceil() + RelTime(24,0)
    dump_start_utc =  R.eval('station_utctime("CPH", %s)' % dump_start)[0]
    dump_end_utc = R.eval('station_utctime("CPH", %s)' % dump_end)[0]
    for crewid in Cui.CuiGetCrew(Cui.gpc_info, Cui.CuiWhichArea, "MARKEDLEFT"):
        crew = TM.crew[(crewid,)]
        f = open(fn, "w")
        try:
            f.write("\n[crew_publish_info: generated at latest INFORM (hb times)]\n")
            prev_end_date = None
            for cpi in sorted(crew.referers("crew_publish_info", "crew"),
                              cmp=lambda x,y: cmp(x.start_date, y.start_date)):
                comment = ""
                if prev_end_date and prev_end_date < cpi.start_date:
                    comment += " *** GAP BETWEEN THIS AND PREVIOUS ***"
                if prev_end_date and cpi.start_date < prev_end_date:
                    comment += " *** OVERLAPS WITH PREVIOUS ***"
                prev_end_date = cpi.end_date
                if cpi.end_date <= dump_start: continue
                if cpi.start_date >= dump_end: continue
                f.write("%s%s\n" % (str(Activity(db_entry=cpi))[:-12].rstrip(), comment))
            
            f.write("\n[do_no_publish: potentially locally modified (hb times!)]\n")
            prev_end_time = None
            for dnp in sorted(crew.referers("do_not_publish", "crew"),
                              cmp=lambda x,y: cmp(x.start_time, y.start_time)):
                if dnp.end_time <= dump_start: continue
                if dnp.start_time >= dump_end: continue
                comment = ""
                if prev_end_time and dnp.start_time < prev_end_time:
                    comment += " *** OVERLAPS WITH PREVIOUS ***"
                prev_end_time = dnp.end_time
                f.write("%s - %s%s\n" % (dnp.start_time, dnp.end_time, comment))
            if not prev_end_time:
                f.write("- none -\n")
                
            
            f.write("\n[published_roster: generated at previous save operations]\n")
            ptypes = ("SCHEDULED", "PUBLISHED", "INFORMED", "DELIVERED")
            prdict = {}
            for pr in crew.referers("published_roster", "crew"):
                if (pr.pubstart < dump_end_utc and pr.pubend > dump_start_utc):
                    prdict.setdefault(pr.pubtype.id, []).append(
                        (pr.pubstart, pr.pubend, pr.pubcid, pr.si))
            
            f.write(" %-9s %5s %-15s %-15s %-10s %s\n"
                    % ("pubtype","note","pubstart","pubend","pubcid","si"))
            for ptype in ptypes:
                pend = None
                for pr in sorted(prdict[ptype], cmp=lambda x,y: cmp(x[0], y[0])):
                    if pend and pend < pr[0]:
                        note = "<OVL>"
                    elif pend and pend > pr[0]:
                        note = "<GAP>"
                    else:
                        note = ""
                    f.write("%10s %5s %-15s %-15s %-10s %s\n"
                            % ((ptype,note) + pr))
           
            f.write("\n[crew_notification: generated at latest save]\n")
            cns = sorted(crew.referers("crew_notification", "crew"),
                         cmp=lambda x,y: cmp(x.deadline, y.deadline))
            if not cns:
                f.write("- none -\n")
            else:
                f.write("%-15.15s %-15.15s %-15.15s %-15.15s %-15.15s %-15.15s %-11.11s %s\n"
                        % ("deadline", "alerttime", "st", "firstmodst", "lastmodet", "delivered", "type", "failmsg"))
                for cn in sorted(crew.referers("crew_notification", "crew"),
                                 cmp=lambda x,y: cmp(x.deadline, y.deadline)):
                    if cn.deadline < dump_start: continue
                    if cn.deadline >= dump_end: continue
                    f.write("%-15.15s %-15.15s %-15.15s %-15.15s %-15.15s %-15.15s %-11.11s %s\n"
                            % (cn.deadline,
                               cn.alerttime,
                               cn.st,
                               cn.firstmodst,
                               cn.lastmodet,
                               cn.delivered,
                               "%-.4s+%-6s" % (cn.typ.typ,cn.typ.subtype),
                               cn.failmsg,
                               ))
                           
            r = RaveEvaluator(Cui.CuiWhichArea, Cui.CrewMode, crewid,
                now = "fundamental.%now%",
                v_st = "publish.%notification_valid_start%",
                v_en = "publish.%notification_valid_end%",
                m_dl = "rules_notifications_cct.%notif_manual_deadline%", 
                m_at = "rules_notifications_cct.%notif_manual_alerttime%",
                m_st = "void_abstime",
                m_fm = "rules_notifications_cct.%notif_manual_failmsg%",
                p_dl = "rules_notifications_cct.%notif_pending_deadline%", 
                p_at = "rules_notifications_cct.%notif_pending_alerttime%",
                p_st = "rules_notifications_cct.%notif_pending_st%",
                p_fm = "rules_notifications_cct.%notif_pending_failmsg%",
                p_sc = "rules_notifications_cct.%notif_pending_is_sbycall%",
                p_rr = "rules_notifications_cct.%notif_pending_is_resched_rule%",
                p_ot = "rules_notifications_cct.%notif_pending_is_other%",
                o_dl = "rules_notifications_cct.%notif_overdue_deadline%", 
                o_at = "rules_notifications_cct.%notif_overdue_alerttime%",
                o_st = "rules_notifications_cct.%notif_overdue_st%",
                o_fm = "rules_notifications_cct.%notif_overdue_failmsg%",
                n_dl = "rules_notifications_cct.%notif_notpub_deadline%", 
                n_at = "rules_notifications_cct.%notif_notpub_alerttime%",
                n_st = "rules_notifications_cct.%notif_notpub_st%",
                n_fm = "rules_notifications_cct.%notif_notpub_failmsg%",
                )
                
            f.write("\n[rule state: crew_notification compared to now=%s"
                      " + times in CURRENT roster]\n" % (r.now))
            f.write("[  scheduled/loaded period: (%s,%s(]\n" % (r.v_st, r.v_en))
            f.write("%-11.11s %-15.15s %-15.15s %-15.15s %s\n"
                    % ("rule", "deadline", "alerttime", "st", "failmsg"))
            h_pending = (r.p_sc and "pend-sbyc") \
                     or (r.p_rr and "pend-rrule") \
                     or (r.p_ot and "pend-other") \
                     or "pending"
            for (h,dl,at,st,fm) in (("manual",  r.m_dl, r.m_at, r.m_st, r.m_fm),
                                    (h_pending, r.p_dl, r.p_at, r.p_st, r.p_fm),
                                    ("overdue", r.o_dl, r.o_at, r.o_st, r.o_fm),
                                    ("notpub" , r.n_dl, r.n_at, r.n_st, r.n_fm),
                                    ):
                f.write("%-11.11s %-15.15s %-15.15s %-15.15s %s\n"
                        % (h, dl or "-", at or "-", st or "-", fm or "-"))
            
            f.write("\n[Changes in CURRENT roster compared to latest saved INFORMED roster]\n")
            diffdict = Cui.CuiDiffPublishedRoster(Cui.gpc_info, [crewid], 0, 0, "INFORMED")
            for dcrewid,diffset in diffdict.items():
                if not diffset:
                    f.write("- none -\n")
                    continue
                for c in diffset:
                    tab = c.getTableName()
                    if tab in ("crew_activity", "crew_ground_duty", "crew_flight_duty"):    
                        c_dtl = dict((attr,(org,rev)) for (attr,org,rev) in c)
                        c_key = str(c.getEntityI())
                        legtab = ((tab == "crew_ground_duty" and "ground_task") or
                                  (tab == "crew_flight_duty" and "flight_leg") or
                                  None)
                        if legtab:
                            for leg in [d for d in diffset if d.getTableName() == legtab]:
                                if c_key.startswith(str(leg.getEntityI())):
                                    c_dtl.update(("%s@%s" % (attr,legtab),(org,rev)) for (attr,org,rev) in leg)
                                    break
                        ctyp = ("ADDED", "MODIFIED", "REMOVED")[c.getType()]
                        f.write("%-8s %s\n" % (ctyp, c.uxm().strip()))
                        for attr,(org,rev) in sorted(c_dtl.items()):
                            f.write("%30s: '%s' -> '%s'\n" % (attr,org,rev)) 

            f.close()
            ext.showFile(fn, "ActivityMap CREW: %s. PP: %s - %s" \
                           % (crewid, Plan.pp_start_date, Plan.pp_end_date))
        finally:
            os.remove(fn)
       
def reset():
    """
    Call this method whenever a total reset is required.
    Typically used by a developer when:
      - representation of class variables has changed, or
      - rave definitions have been changed.
    """
    import __main__
    Plan.reset()
    reload(__main__.Rescheduling)
    print "Rescheduling was reset and reloaded."

#------------------------------------------------------------------------------
# Global Definitions
#------------------------------------------------------------------------------
    
ONE_DAY = RelTime("24:00")

def daysInRange(time_or_date1, time_or_date2):
    t1 = AbsTime(time_or_date1)
    t1 = t1.day_floor()
    t2 = AbsTime(time_or_date2)
    t2 = t2.day_ceil()
    return int((t2-t1)/ONE_DAY)

def forwardDate(time_or_date, days_forward=1):
    """
    Returns, as an AbsDate, time_or_date + the specified number of days,
      or `None` if time_or_date is `None`.
    """
    if time_or_date is None:
        return None
    else:
        return AbsDate((time_or_date+(ONE_DAY*days_forward)).getRep())

def copyAsTime(time_or_date):
    """
    Returns a copy of time_or_date as a new AbsTime instance,
      or `None` if time_or_date is `None`.
    """
    if time_or_date is None:
        return None
    else:
        return AbsTime(time_or_date)

def copyAsDate(time_or_date):
    """
    Returns a copy of time_or_date as a new AbsDate instance,
      or `None` if time_or_date is `None`.
    """
    if time_or_date is None:
        return None
    else:
        return AbsDate(time_or_date)
    
def isSameDate(t1, t2):
    """
    Return True if the dates of t1 and t2 are the same.
    `None` is a comparable value
    """
    return isEqual((copyAsDate(t1), copyAsDate(t2)))
    
def isNone(v):
    """
    Dave-compatible check.
    (In Dave, an empty string cannot be distinguished from NULL.)
    """
    return v is None \
        or (isinstance(v,str) and v=="")
        
def isEqual(*pairs):
    """
    "Safe" equality check of model values.
    `None` values are correctly taken into account.
    For 'model' compatibility, an empty string is considered equal to `None`.
    Examples:
        isEqual((1,1))               -> True
        isEqual((1,1), ("xyz",None)) -> False
        isEqual((1,1), ("",None))    -> True
    """
    for v1,v2 in pairs:
        if isNone(v1):
            if not isNone(v2): return False
        elif isNone(v2):
            return False
        else:
            if v1 != v2: return False
    return True
    
#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class PubCat(RaveEvaluator):
    """
    Mirrors rave definitions of rescheduling pcat (Publish Categories) values,
      as well as some comparison logic.
    """
    
    @classmethod
    def _cls_init(cls):
        """
        Called by Plan when it is initialised for the first time.
          (Plan is initialised each time the main entry point
          (Rescheduling.publish) is invoked.)
        Contains rave evaluation, which cannot be performed when Studio
          is loaded, because at that point Studio has no access to Rave.
        """
        cls._names = {}
        cls._ids = {}
        for id,name in [(pcat.id, pcat.name.replace("-","_"))
                        for pcat in RI(R.times(9999), {
                 'id':'fundamental.%py_index%',
                 'name':R.expr('rescheduling.%pcat_name%(fundamental.%py_index%)'),
                 }).eval() if pcat.name is not None]:
            cls._names[id] = name
            cls._ids[name] = id
        for id,name in cls._names.items():
            setattr(cls, name, PubCat(id))
        RaveEvaluator.rEvalCls(
           _prod_limit    = "rescheduling.%_pcat_production_limit%",
           _onduty_limit  = "rescheduling.%_pcat_on_duty_limit%")
        #print cls.list()
       
    @classmethod
    def list(cls):
        return "\n".join([PubCat(id).desc() for id in sorted(cls._names)])
                                  
    def __init__(self, key):
        """
        Will throw KeyError if 'key' cannot be evaluated to a str or int value
          defined in rave (table rescheduling.pcat_name).
        """
        try:
            try:
                self._id = int(key)
            except:
                self._id = self._ids[str(key)]
            self._name = self._names[self._id]
        except KeyError:
            raise KeyError("PubCat '%s' is not defined in rave module: rescheduling" % key)
            
    def __int__(self):
        """
        Integer representation of the category.
        Corresponds to a rescheduling.%pcat_xx% rave constant.
        """
        return self._id
        
    def __str__(self):
        """
        String representation of the category.
        Corresponds to a mapping in the rescheduling.pcat_name rave table.
        """
        return self._name
        
    def desc(self):
        s = "str: %-8s int: %4s" % (self._name, self._id)
        prop = []
        if self.isProduction():            prop.append("PRODUCTION")
        if self.isOnDuty():                prop.append("ON-DUTY")
        if self.isOffDuty():               prop.append("OFF-DUTY")
        if PubCat.isInvalidOrIgnore(self): prop.append("IGNORE")
        if prop: s += " props: %s" % ", ".join(prop)
        return s
        
    def __cmp__(self, o):
        """
        'o' may be an other PubCat, an int,
        or anything that can be converted to a PubCat.
        
        Valid expressions:
            PubCat.F_DAY == PubCat("F_DAY")
            PubCat.LEAVE <= "F_DAY"
            PubCat(10) == PubCat("FLIGHT")
            PubCat.FLIGHT == 10
            PubCat("F_DAY") < 919872  *** PubCat(919872) is not defined, but
                                          you can always compare to an int.
        Invalid expressions:
            PubCat("BL_DAY") == "NOTHING" *** There is no PubCat named "NOTHING"
        """
        if isinstance(o,PubCat):
            return cmp(self._id, o._id)
        elif isinstance(o,int):
            return cmp(self._id, o)
        else:
            return cmp(self._id, PubCat(o))

    @classmethod            
    def isInvalidOrIgnore(cls, pcat):
        try:
            return cls(pcat) >= cls.IGNORE
        except:
            return True
            
    @staticmethod
    def dbValue(pcat):
        """
        Return a proper value for db storage.
        
        Empty days between wops are replaced with Blank Days.
        These are actually illegal, but we have to put something there...)
        """
        pcat = PubCat(pcat)
        if pcat == PubCat.EMPTY:
            return int(PubCat.BL_DAY)
        else:
            return int(pcat)
            
    def isProduction(self):
        return self._id <= self._prod_limit

    def isOnDuty(self):
        return self._id <= self._onduty_limit

    def isOffDuty(self):
        return self._id > self._onduty_limit

class FlagSet(set,RaveEvaluator):
    """
    Handles a crew_publish_info.flags value.
    
    Contents can be manipulated both as a python 'set' and as a string.
        FlagSet(['a','b']) | FlagSet(":b:c") == FlagSet(['a','b','c'])
        str(FlagSet(['a','b']) --> ":a:b:"
        
    Not a complete override of the 'set' class.
    Only methods required by the current logic in this module are implemented.
    Currently:
        comparison: ==  >=  >  <=  <  !=
        operators:  | |= -  -= & &=
        add()
        remove()
        intersection() (&)
        update() (|=)
        difference_update() (-=)
    Expand when needed.
    
    The flags defined in the rave module 'rescheduling' are implemented as
    class variables.
    
    Examples:
        flags = FlagSet("a:c") | "b"  --> ":a:b:c:"
        flags.update("d:c")           --> ":a:b:c:d:"
        flags -= ['a','d','x']        --> ":b:c:"
        flags |= FlagSet.first_in_wop --> ":b:c:wf:"    
    """
        
    _delim = ':'
    
    @classmethod
    def _cls_init(cls):
        """
        This method is called by Plan when it is initialised for the first time.
        (Plan is initialised each time the main entry point (Rescheduling.publish) is called.)
        Contains rave evaluation, which cannot be performed when Studio is loaded,
          because at that point Studio has no access to Rave.
        """
        RaveEvaluator.rEvalCls(
            first_in_wop       = ("rescheduling.%flag_first_in_wop%"),
            last_in_wop        = ("rescheduling.%flag_last_in_wop%"),
            F7S                = ("rescheduling.%flag_F7S%"),
            standby_at_airport = ("rescheduling.%flag_standby_at_airport%"),
            standby_line       = ("rescheduling.%flag_standby_line%"),
            standby_home       = ("rescheduling.%flag_standby_home%"),
            standby_hotel      = ("rescheduling.%flag_standby_hotel%"),
            homerest           = ("rescheduling.%flag_homerest%"),
            short_stop_1       = ("rescheduling.%flag_short_stop_1%"),
            short_stop_2       = ("rescheduling.%flag_short_stop_2%"),
            long_haul          = ("rescheduling.%flag_long_haul%"),
            published_VA       = ("rescheduling.%flag_vacation%"),
            frz_prev_inf_dt    = ("rescheduling.%flag_freeze_prev_inf_duty_time%"),
            frz_sby_sched_et   = ("rescheduling.%flag_freeze_sby_sched_end_time%"),
            subq_extended_fdp  = ("rescheduling.%flag_extended_fdp%"),
            subq_non_extended_fdp = ("rescheduling.%flag_non_extended_fdp%"),
            sticky_flags       = ("rescheduling.%sticky_flags%", FlagSet),
            )
        cls.wop_delimiters = cls([cls.first_in_wop,cls.last_in_wop])

    def __init__(self, flags):
        self._as_string = ""
        self.update(flags)
        
    def extractSticky(self):
        return self & self.sticky_flags

    def _set_str(self):
        if len(self):
            self._as_string = "%s%s%s" % (self._delim, self._delim.join(sorted(self)), self._delim)
        else:
            self._as_string = ""
        
    def __str__(self):
        return self._as_string

    def applyErrmsg(self, flags):
        s = repr(flags)
        if len(s) > 40: s = s[:37]+"..."
        return "Can't apply %s%s to a %s. " \
               "Only strings and sequence types are allowed." \
               % (s,type(flags),self.__class__.__name__)
        
    def __eq__(self, o): return self.__cmp__(o) == 0
    def __ge__(self, o): return self.__cmp__(o) >= 0
    def __gt__(self, o): return self.__cmp__(o) > 0
    def __le__(self, o): return self.__cmp__(o) <= 0
    def __lt__(self, o): return self.__cmp__(o) < 0
    def __ne__(self, o): return self.__cmp__(o) != 0
        
    def __cmp__(self, o):
        if isinstance(o, FlagSet):
            return cmp(self._as_string, o._as_string)
        else:
            return self.__cmp__(FlagSet(o))
        
    def __or__(self, o):
        result = FlagSet(self)
        result.update(o)
        return result
        
    def __ior__(self, o):
        self.update(o)
        return self
    
    def __and__(self, o):
        return self.intersection(o)
    
    def __sub__(self, o):
        result = FlagSet(self)
        result.difference_update(o)
        return result
        
    def __isub__(self, o):
        self.difference_update(o)
        return self
        
    def __iadd__(self, o):
        self.update(o)
        return self


    def add(self, flag):
        if flag:
            set.add(flag)
            self._set_str()
        
    def remove(self, flag):
        if flag:
            set.remove(flag)
            self._set_str()

    def intersection(self, flags):
        if flags:
            if isinstance(flags, str):
                return self.intersection([f for f in flags.split(':') if f])
            else:
                try:
                    return FlagSet(set.intersection(self, flags))
                except:
                    raise TypeError(self.applyErrmsg(flags))

    def update(self, flags):
        if flags:
            if isinstance(flags, str):
                self.update([f for f in flags.split(':') if f])
            else:
                try:
                    set.update(self, flags)
                    self._set_str()
                except:
                    raise TypeError(self.applyErrmsg(flags))
                
    def difference_update(self, flags):
        if flags:
            if isinstance(flags, str):
                self.difference_update([f for f in flags.split(':') if f])
            else:
                try:
                    set.difference_update(self, flags)
                    self._set_str()
                except:
                    raise TypeError(self.applyErrmsg(flags))

class Plan(RaveEvaluator):
    """
    General info regarding the operational environment.
    Should be initialized each time new data are to be generated.
    """
    
    _init_done = False
    
    @classmethod
    def _cls_init(cls):
        if not cls._init_done:
            PubCat._cls_init()
            FlagSet._cls_init()
            cls._init_done = True
        
    @classmethod
    def reset(cls):
        """
        Call this method whenever a total reset is required.
        Typically used by a developer when:
          - representation of class variables has changed, or
          - rave definitions have been changed.
        """
        cls._init_done = False
        
    @classmethod
    def init(cls, start_date=None, end_date=None, sel_mode=INFORM_ALL):
        cls._cls_init()

        assert sel_mode in SEL_MODES, "Invalid selection mode."
        cls.sel_mode = sel_mode

        cls.rEvalCls(pp_start_date=("rescheduling.%pp_start_date%",AbsDate),
                     pp_end_date=("rescheduling.%pp_end_date%",AbsDate))

        cls.undef_tasks = {}
        cls.maxlogcount = 0
        cls.logcount = 0
        cls._logstr = ""

    @classmethod
    def setDirtyTable(cls, table):
        UpdateManager.setDirtyTable(table)

    @classmethod
    def log(cls, *args):
        if cls.logcount > 0:
            if len(args) and isinstance(args[-1],str) and args[-1][-1:] == "_":
                cls._logstr += " ".join([str(a) for a in args[:-1]]) 
                cls._logstr += " "
                if len(args[-1]) > 1:
                    cls._logstr += args[-1][:-1]
                    cls._logstr += " "
            else:
                cls._logstr += " ".join([str(a) for a in args]) 
                cls._logstr += "\n"

    @classmethod
    def logstep(cls, log):
        if cls.logcount > 0:
            if log:
                print cls._logstr.replace(" \n","\n"),
                cls.logcount -= 1
            cls._logstr = ""

class ActivityMap(list):
    """
    Maps the activites for one crew over a period.
    
    The map is populated in two ways:
    - From 'crew_publish_info' table data, using "populate=True" in the
      constructor. This will fill the map with a crew's activity over
      a given period.
    - From roster data. An empty map is first created for a given period.
      Activity is then added using addWop, addTrip, updateDuty and updateLeg
      calls.
      
    The ActivityMap will hold one Activity entry for each day in the period.
    Empty days are represented by PubCat.EMPTY Activity:s (defaultActivity).
    """

    def __init__(self,
                 crewid,
                 start_date,
                 end_date=None,
                 populate=False):
                    
        self.crewid = crewid
        self.crew = TM.crew[(crewid,)]
        self.start_date = copyAsDate(start_date)
        self.end_date = copyAsDate(end_date)

        self.db_before = self.db_after = None
        if populate:
            self.populateFromDb()

    def __str__(self):
        return "CREW: %s, PERIOD: %s-%s\n  %s" \
                % (self.crewid,
                   self.start_date,
                   self.end_date,
                   "\n  ".join([str(activity) for activity in self]),
                   )

    def __setitem__(self, day, activity):
        """
        Set Activity on specified day index.
        Typically: "map[day] = a".
        Auto-expands this ActivityMap to allow indices beyond current length.
        """
        if day < len(self):
            list.__setitem__(self, day, activity)
        else:
            for d in range(len(self), day):
                self.append(self.defaultActivity(d))
            self.append(activity)

    def __getitem__(self, day):
        """
        Get Activity on specified day index.
        Typically: "a = map[day]" or "map[day].item = value".
        Auto-expands this ActivityMap to allow indices beyond current length.
        """
        if day >= len(self):
            for d in range(len(self), day+1):
                self.append(self.defaultActivity(d))
        return list.__getitem__(self, day)

    def defaultActivity(self, day):
        """
        Default Activity inserted when indexing
          (__getitem__/__setitem__) beyond current length. 
        """
        return Activity(PubCat.EMPTY, self.dateInPeriod(day))

    def dayInPeriod(self, time_or_date):
        """
        Returns calendar day index relative to this ActivityMap's start date.
        This is the index to an activity on a specific day (self[day]) within
            this ActivityMap (which inherits from 'list').
        The returned value is negative on days before the period start date.
        """
        return int((copyAsDate(time_or_date) - self.start_date) / ONE_DAY) 

    def dateInPeriod(self, day):
        """
        Returns the date for a day index, relative to this ActivityMap.
        """
        return forwardDate(self.start_date, day)

    def setDetails(self, start_date, end_date,
                         pcat=None,
                         flags=None,
                         checkin=None,
                         checkout=None,
                         duty_time_per_day=None,
                         prev_informed_duty_time=None,
                         refcheckin=None,
                         refcheckout=None,
                         sched_end_time=None,
                         db_entry=None,
                         do_not_update_prev_inf_duty_time=None):
        """
        Updates or adds Activity entries for the specified day range.
        Days before this ActivityMap's period start are ignored.
        
        - Pcat, is specified, updates Activity.pcat only if it's more
          significant (lower value) than existing Activity.
        - Flags, if specified, are appended to existing Activity.flags.
        - Checkin/checkout are, if specified, copied as is. It is assumed
          that they always are specified either both or none. (This should be
          the case if the values are derived from proper rave value pairs.)
        - Duty_time_per_day is, if specified, a RelTime or a list of RelTime:s
          corresponding to the days within start_date/end_date.
          The value(s) are added to existing Activity.duty_time.
        - prev_informed_duty_time
        - refcheckin 
        - refcheckout 
        - sched_end_time
          
        For a roster, it is assumed that this function is called in 
        chronological wop-trip-duty-dutyrest-leg order, so leg values override
        dutyrest, dutyrest overrides duty, and so on.
        """

        # Day indices covered by the input data (end day not included).
        activity_start_day = self.dayInPeriod(start_date) # NOTE: < 0 if before map period!
        activity_end_day = self.dayInPeriod(end_date)
        
        # Day indices that will be stored in this map (end day not included).
        map_start_day = max(0, activity_start_day)
        map_end_day = min(self.dayInPeriod(self.end_date), activity_end_day)
        
        flags = FlagSet(flags)        
        # If there is a last_in_wop flag, remove it, and save the index where
        # it is to be inserted. Note that the index may be on or after
        # map_end_day, in which case the last_in_wop flag won't be inserted.
        if FlagSet.last_in_wop in flags:
            last_day_in_wop = activity_end_day - 1
            flags -= FlagSet.last_in_wop
        else:
            last_day_in_wop = 9999999
            
        for day in range(map_start_day, map_end_day):
            # When populated from the database, we need to store the original
            # date range; the db_entry itself may be modified during store(). 
            self[day].db_entry = db_entry
            if db_entry:
                self[day].db_original_pcat       = db_entry.pcat
                self[day].db_original_start_date = copyAsDate(db_entry.start_date)
                self[day].db_original_end_date   = copyAsDate(db_entry.end_date)
                self[day].db_original_checkin    = copyAsTime(db_entry.checkin)
                self[day].db_original_checkout   = copyAsTime(db_entry.checkout)
                self[day].db_original_flags      = db_entry.flags
                self[day].db_original_duty_time  = RelTime(db_entry.duty_time)
                self[day].db_original_prev_informed_duty_time = RelTime(db_entry.prev_informed_duty_time)
                self[day].db_original_refcheckin = copyAsTime(db_entry.refcheckin)
                self[day].db_original_refcheckout = copyAsTime(db_entry.refcheckout)
                self[day].db_original_sched_end_time = copyAsTime(db_entry.sched_end_time)

            # Preserve the most significant publish category for the day.
            if pcat and pcat < self[day].pcat:
                self[day].pcat = PubCat(pcat)
                 
            # Checkin/out overrides existing values.
            if checkin:
                self[day].checkin = AbsTime(checkin)
            if checkout:
                self[day].checkout = AbsTime(checkout)
            if sched_end_time:
                self[day].sched_end_time = AbsTime(sched_end_time)
                
            if do_not_update_prev_inf_duty_time:
                if do_not_update_prev_inf_duty_time[day-activity_start_day] == "True":
                    self[day].do_not_update_prev_inf_duty_time = True
            
            # Flags:
            # First_in_wop is only valid on the 1st day (remove if after 1st day) 
            if flags and day > activity_start_day:
                flags -= FlagSet.first_in_wop
            # Last_in_wop is only valid on the last day (add if on last day)
            if day == last_day_in_wop:
                flags |= FlagSet.last_in_wop
            # Now save whatever flags remain.
            if flags:
                self[day].flags |= flags
                
            # And the duty-times-per-day
            if duty_time_per_day:
                try:
                    if isinstance(duty_time_per_day, RelTime):
                        self[day].duty_time += RelTime(duty_time_per_day)
                    else:
                        self[day].duty_time += \
                            RelTime(duty_time_per_day[day - activity_start_day])
                except:
                    pass
            
            # Override existing value for prev_informed_duty_time                        
            if prev_informed_duty_time:
                self[day].prev_informed_duty_time = RelTime(prev_informed_duty_time)

            # Override existing value for refcheckin  
            if refcheckin:
                self[day].refcheckin = AbsTime(refcheckin)
            
    def addWop(self, wop):
        """
        Initialize wop period, flagging first and last day.
        """
        if not wop.is_ignore:
            if wop.duty_times_per_day is None:
                dtpd = None
            else:
                if not wop.duty_times_per_day.endswith(','):
                    wop.duty_times_per_day.rstrip("0123456789")
                dtpd = []
                for dt in wop.duty_times_per_day.rstrip(',').split(','):
                    dt = dt or "000"
                    dtpd.append(RelTime(int(dt[:-2]), int(dt[-2:])))
            self.setDetails(wop.start_hb, wop.end_hb,
                            flags=FlagSet.wop_delimiters,
                            duty_time_per_day=dtpd)
                            
    def addTrip(self, trip):
        """
        Add trip details.
        """
        try:
            if PubCat.isInvalidOrIgnore(trip.pcat):
                duty_codes = tuple([trip.pcat] \
                                   + sorted(set([duty.code for duty
                                                 in trip.chain('duties')])))
                Plan.undef_tasks.setdefault(duty_codes,set()).add(self.crewid)
            else:
                self.setDetails(trip.start_hb, trip.end_hb,
                                pcat=trip.pcat,
                                flags=trip.flags,
                                checkin=trip.checkin_hb,
                                checkout=trip.checkout_hb)
        except:
            print "FAILED TO ADD TRIP",trip,"FOR",self.crewid
            traceback.print_exc()
            
    def updateDuty(self, duty):
        """
        Update trip with duty and rest after duty (stopover or homerest) details.
        The trip already is in the map, so no new entries will be created.
        """
                       
        try:          
            if duty.flags or duty.checkin_hb or duty.checkout_hb:
                self.setDetails(duty.start_hb, duty.end_hb,
                                flags=duty.flags,
                                checkin=duty.checkin_hb,
                                checkout=duty.checkout_hb)
            if duty.rest_flags and duty.rest_end_hb is not None:
                self.setDetails(duty.rest_start_hb, duty.rest_end_hb,
                                flags=duty.rest_flags)
            if duty.reference_check_in and bool(duty.refcheckin_valid):
                self.setDetails(duty.start_hb, duty.end_hb,
                                refcheckin=duty.reference_check_in)  
            if duty.do_not_update_prev_inf_duty_time and "True" in duty.do_not_update_prev_inf_duty_time:
                do_not_update_prev_inf_duty_time_day = duty.do_not_update_prev_inf_duty_time.split(',')
                self.setDetails(duty.start_hb, duty.end_hb,
                                do_not_update_prev_inf_duty_time=do_not_update_prev_inf_duty_time_day)                                    
        except:
            print "FAILED TO UPDATE DUTY",duty,"FOR",self.crewid
            traceback.print_exc()
        
    def updateLeg(self, leg):
        """
        Update leg day(s) with leg flags.
        Assumes the trip already is in the map, so no new entries are created.
        """        
        try:
            if leg.flags:
                self.setDetails(leg.start_hb, leg.end_hb,
                                flags=leg.flags)
        except:
            print "FAILED TO ADD LEG",leg,"FOR",self.crewid
            traceback.print_exc()
       
    def populateFromDb(self):
        """
        Populate this ActivityMap from the crew_publish_info table.
        (Called from __init__() when populate=True.)
        The data will cover the period from start_date (= self[0])
        and forwards, expanded to one Activity entry per day.
        """
        rstart = AbsTime(self.start_date)
        rend = AbsTime(self.end_date)
        Plan.log("Populate crew %s: %9.9s - %9.9s" % (self.crew.id,rstart,rend))
        for db_entry in sorted(self.crew.referers("crew_publish_info", "crew"),
                               cmp=lambda x,y: cmp(x.start_date, y.start_date)):
            if db_entry.end_date <= rstart:
                if db_entry.end_date == rstart:
                    Plan.log("BEFORE %s" % db_entry)
                    self.db_before = Activity(db_entry=db_entry)
            elif db_entry.start_date >= rend:
                if db_entry.start_date == rend:
                    Plan.log(" AFTER %s" % db_entry)
                    self.db_after = Activity(db_entry=db_entry)
            else:
                Plan.log("   INF %s" % db_entry)
                self.setDetails(db_entry.start_date, db_entry.end_date,
                                pcat=db_entry.pcat,
                                flags=db_entry.flags,
                                checkin=db_entry.checkin,
                                checkout=db_entry.checkout,
                                duty_time_per_day=db_entry.duty_time,
                                prev_informed_duty_time=db_entry.prev_informed_duty_time,
                                refcheckin=db_entry.refcheckin,
                                refcheckout=db_entry.refcheckout,
                                sched_end_time=db_entry.sched_end_time,
                                db_entry=db_entry)
       
    def removeFromDb(self):
        """
        Remove all crew_publish_info entries that are fully
        within this map's start/end period.
        """
        rstart = AbsTime(self.start_date)
        rend = AbsTime(self.end_date)
        Plan.log("Remove crew %s: %9.9s - %9.9s" % (self.crew.id,rstart,rend))
        for db_entry in self.crew.referers("crew_publish_info", "crew"):
            if db_entry.start_date >= rstart and db_entry.end_date <= rend:
                if db_entry.remove():
                    Plan.log("REMOVE %s" % db_entry)
            
    def removeOverlapsFromDb(self):
        """
        Remove all overlapping crew_publish_info entries that are fully
        within this map's start/end period.
        """
        rstart = AbsTime(self.start_date)
        rend = AbsTime(self.end_date)
        Plan.log("Remove crew %s overlaps: %9.9s - %9.9s" % (self.crew.id,rstart,rend))
        last_entry = None
        entries_to_remove = []
        for db_entry in sorted(self.crew.referers("crew_publish_info", "crew"),
                               cmp=lambda x,y: cmp(x.start_date, y.start_date)):
            if db_entry.start_date >= rstart and db_entry.end_date <= rend:
                if last_entry != None and db_entry.start_date < last_entry.end_date:
                    if not last_entry in entries_to_remove:
                        entries_to_remove.append(last_entry)
                    entries_to_remove.append(db_entry)
                last_entry = db_entry
        for db_entry in entries_to_remove:
            db_entry.remove()
            Plan.log("REMOVE %s" % db_entry)
            
            
    def store(self):
        t = time.time()
        modified = False
        if self.crewid:
            Plan.log("store() start", "_")
            
            # Expand roster data (with EMPTY)
            # to cover at least the publish/inform period.
            
            self[self.dayInPeriod(self.end_date - ONE_DAY)]
            self.data_end_date = self.dateInPeriod(len(self))

            # Retrieve informed data. Expand (with EMPTY)
            # to cover at least the roster period.
            
            informed = ActivityMap(self.crewid,
                                   self.start_date,
                                   self.data_end_date,
                                   populate=True)
            informed[len(self) - 1]
            
            # Horizontal selection of days within the period.

            if Plan.sel_mode == ONLY_INFORM_SELECTION:
                # Initially set all days to be skipped 
                for day in range(len(self)):
                    self[day].setSkipDayFromRoster()
                    informed[day].setSkipDayFromRoster()
                # Unset skip for days in the table with days to be informed.
                for row in InformedTempTable().search('(crew=%s)'%self.crewid):
                    for day in range(self.dayInPeriod(row.start_time), 
                                     self.dayInPeriod(row.end_time)):
                        if day >= 0 and day < len(self):
                            self[day].clearSkipDayFromRoster()
                            informed[day].clearSkipDayFromRoster()
            
            # Entry is affected by illness even though it's not marked as informed
            dayIsAffectedByIllness = []
            # Copy sticky flags and duty_time from informed to roster data
            lastday = len(self)
            for day, activity in enumerate(self):
                if Plan.sel_mode == ROSTER_PUBLISH:
                    activity.prev_informed_duty_time = RelTime(0)
                    activity.refcheckout = activity.checkout
                    activity.sched_end_time = activity.checkout
                else:
                    activity.flags |= FlagSet(informed[day].flags).extractSticky()
                    
                    # Do not update prev_informed_duty_time if flag frz_prev_inf_dt is set
                    if informed[day].db_entry and (not day in dayIsAffectedByIllness) and (self[day].do_not_update_prev_inf_duty_time or FlagSet.frz_prev_inf_dt in informed[day].flags):
                        activity.prev_informed_duty_time = informed[day].db_original_prev_informed_duty_time
                    else:
                        activity.prev_informed_duty_time = informed[day].duty_time
                    if FlagSet.frz_prev_inf_dt in informed[day].flags:
                        activity.flags |= FlagSet.frz_prev_inf_dt

                    # Do not update sched_end_time if flag frz_sby_sched_et is set
                    if FlagSet.frz_sby_sched_et in activity.flags:
                        activity.sched_end_time = informed[day].sched_end_time
                    else:
                        if (FlagSet.standby_home in activity.flags) or (FlagSet.standby_hotel in activity.flags):
                            activity.sched_end_time = activity.checkout
                        else:
                            activity.sched_end_time = informed[day].sched_end_time

                    activity.refcheckout = informed[day].checkout

                # If day has been marked as informed illness, add 'frz' flag to the following rows in crew_publish_info until the end of the wop
                if (not self[day].isSkipDayFromRoster()) and FlagSet.frz_prev_inf_dt in self[day].flags:
                    i_wl = 1
                    while ((day+i_wl < lastday-1) and
                           (FlagSet.first_in_wop not in self[day+i_wl].flags)):
                        # Make sure not to modify data in crew_publish_info other than marked selection and 'frz' flag until end of wop
                        if self[day+i_wl].isSkipDayFromRoster():
                            self[day+i_wl] = copy(informed[day+i_wl])
                            self[day+i_wl].flags |= FlagSet.frz_prev_inf_dt
                            self[day+i_wl].prev_informed_duty_time = self[day+i_wl].duty_time

                            dayIsAffectedByIllness.append(day+i_wl)
                        i_wl += 1
            for skipDay in dayIsAffectedByIllness:
                self[skipDay].clearSkipDayFromRoster()

            # Compare roster and informed data, day by day.
            # Update db (modify/create/remove entries) where needed.
            # An inner loop "merges" days with the same type of activity.
            # In the outer loop, a merge will occur if the day activity
            # matches any db activity before or after the date period
            # covered by this ActivityMap.

            inf_prevday = informed.db_before
            day = 0
            lastday = len(self) - 1
            Plan.log(inf_prevday,"(inf_prevday)")
            while day <= lastday:
                Plan.log("%-s :%s" % (informed[day],self[day]), "_")
                if self[day].isSkipDayFromRoster():
                    Plan.log(["NOT-ROSTER-PUBLISH","NOT-INFORM-ALL","NOT-INFORM-NOW"][Plan.sel_mode])
                    inf_prevday = None
                    day += 1
                    continue
                elif informed[day].dbExists() and self[day] == informed[day]:
                    Plan.log("EXISTS, NO CHANGE")
                    inf_prevday = informed[day]
                    day += 1
                    continue
                Plan.log("p%.1s x%.1s m%.1s_" % (
                         inf_prevday is not None,
                         (inf_prevday and inf_prevday.dbExists()),
                         (inf_prevday and self[day].canMerge(inf_prevday))))
                if  inf_prevday is not None \
                and inf_prevday.dbExists() \
                and self[day].canMerge(inf_prevday):
                    Plan.log("START MERGE WITH PREV",inf_prevday.pcat,"_")
                    self[day].db_entry = inf_prevday.db_entry
                    self[day].end_date = max(self[day].end_date,
                                             inf_prevday.db_original_end_date)
                    self[day].dbUpdate()
                    if informed[day].dbExists() \
                    and informed[day].db_entry.start_date == AbsTime(self.dateInPeriod(day)):
                        Plan.log("REMOVE CURRENT_")
                        informed[day].dbRemove()
                elif informed[day].dbExists() \
                 and self[day].canMerge(informed[day]):
                    Plan.log("START MERGE WITH SAME",informed[day].pcat,"_")
                    self[day].db_entry = informed[day].db_entry
                    self[day].dbUpdate()
                else:
                    if not informed[day].dbExists():
                        Plan.log("START NEW_")
                        self[day].dbCreate(self.crew)
                        if informed[day].db_entry \
                        and self[day].canMerge(informed[day]):
                            if informed[day].db_original_end_date > self[day].end_date:
                                Plan.log("USE", informed[day].db_original_end_date, "FOR END_")
                                self[day].end_date = informed[day].db_original_end_date
                                self[day].dbUpdate()
                    else:
                        if day == lastday \
                        and informed[day].db_original_end_date > self.data_end_date:
                            Plan.log("SAVE PERIOD TAIL_")
                            informed[day].dbSaveTail(self.crew, self.data_end_date)
                        if AbsTime(self[day].start_date) > informed[day].db_entry.start_date:
                            Plan.log("END PREV_")
                            informed[day].db_entry.end_date = copyAsTime(self[day].start_date)
                            Plan.log("START NEW_")
                            self[day].dbCreate(self.crew)
                        else:
                            Plan.log("START UPDATE CLEAN_")
                            self[day].db_entry = informed[day].db_entry
                            self[day].dbReinit()
                modified = True
                inf_prevday = None
                startday = day
                day += 1
                
                # Merge following day activities matching the current day.
                
                while day <= lastday and self[day].canMerge(self[startday]):
                    Plan.log("\n%-s :%s" % (informed[day],self[day]),"MERGE:_")
                    self[day].db_entry = self[startday].db_entry
                    merge_end_date = AbsDate(self[day].db_entry.end_date)
                    if informed[day].db_entry is None:
                        Plan.log("WITH NEW_")
                    else:
                        if informed[day].db_original_start_date != self[day].start_date:
                            Plan.log("NO OVERLAPPING INF THIS DAY_")
                        else:
                            if informed[day].dbExists():
                                informed[day].dbRemove()
                                Plan.log("REMOVED OVERLAPPING INF_")
                                if self[day].canMerge(informed[day]):
                                    inf_db_orig_end_date = informed[day].db_original_end_date
                                    if inf_db_orig_end_date > merge_end_date:
                                        Plan.log(", USE ITS END DATE_")
                                        merge_end_date = inf_db_orig_end_date
                            else:
                                Plan.log("OVERLAPPING INF ALREADY REMOVED_")
                    self[day].end_date = max(self[day].end_date, merge_end_date)
                    self[day].dbUpdate()
                    day += 1
                
                thisday = day - 1
                nextdate = self.dateInPeriod(thisday) + ONE_DAY
                if thisday < lastday:
                    if self[thisday].end_date > nextdate:
                        Plan.log("ADJUST END DATE %s_" % nextdate)
                        self[thisday].end_date = nextdate
                        self[thisday].dbUpdate()
                    if Plan.sel_mode == ONLY_INFORM_SELECTION \
                    and self[thisday+1].isSkipDayFromRoster():
                        if informed[thisday].db_original_end_date > self[thisday].end_date:
                            Plan.log("SAVE INFORM-NOW TAIL_")
                            informed[thisday+1].dbSaveTail(self.crew, self[thisday].end_date)
                Plan.log()
        
        t = time.time() - t
        if modified:
            Plan.log("store(%.2fs) done" % t)
        else:
            Plan.log("store(%.2fs) done, nothing modified" % t)
            
        return modified

    def dbConsistencyCheck(self):
        """
        Check for date holes or overlaps in the 'crew_publish_info' table
        during this ActivityMap's period + the day before and after.
        """
        Plan.log("dbConsistencyCheck, CREW %s:" % self.crew.id)
        t = time.time()
        ok = True
        check_start = copyAsTime(self.start_date)
        check_end = copyAsTime(self.end_date) 
        entries = []
        for cpi in self.crew.referers("crew_publish_info", "crew"):
            if cpi.end_date < check_start: continue
            if cpi.start_date > check_end: continue
            entries.append((cpi.start_date, cpi.end_date))
        if not entries:
            Plan.log("  EMPTY DATABASE")
            ok = False
        else:
            entries.sort()
            start_date, end_date = entries[0]
            for sd,ed in entries[1:]:
                if sd != end_date:
                    if sd < end_date:
                        Plan.log("  OVERLAP ON", sd,
                                 "PREV IS", start_date,
                                 "TO", end_date)
                    else:
                        Plan.log("  GAP BEFORE",sd,
                                 "PREV IS", start_date,
                                 "TO", end_date)
                    ok = False
                start_date,end_date = sd,ed
        t = time.time() - t
        Plan.log("dbConsistencyCheck %s (%.2fs)" % (("FAILED","OK")[int(ok)], t))
        return ok

class Activity(object):
    """
    Defines one crew activity within an ActivityMap.
    Each activity covers one or more calendar days.
    """

    def __init__(self,
                 pcat=None,
                 start_date=None, end_date=None,
                 checkin=None, checkout=None, 
                 flags=None,
                 duty_time=None,
                 prev_informed_duty_time=None,
                 refcheckin=None,
                 refcheckout=None,
                 sched_end_time=None,
                 db_entry=None,
                 do_not_update_prev_inf_duty_time=None):
        if db_entry is not None:
            self.pcat       = PubCat(db_entry.pcat)
            self.start_date = copyAsDate(db_entry.start_date)
            self.end_date   = copyAsDate(db_entry.end_date) \
                              or forwardDate(db_entry.start_date)
            self.checkin    = copyAsTime(db_entry.checkin)
            self.checkout   = copyAsTime(db_entry.checkout)
            self.flags      = FlagSet(db_entry.flags)
            self.duty_time  = RelTime(db_entry.duty_time)
            self.prev_informed_duty_time = RelTime(db_entry.prev_informed_duty_time)
            self.refcheckin = copyAsTime(db_entry.refcheckin)
            self.refcheckout = copyAsTime(db_entry.refcheckout)
            self.sched_end_time = copyAsTime(db_entry.sched_end_time)
            self.db_entry   = db_entry
            self.db_original_pcat       = db_entry.pcat
            self.db_original_start_date = copyAsDate(db_entry.start_date)
            self.db_original_end_date   = copyAsDate(db_entry.end_date)
            self.db_original_checkin    = copyAsTime(self.db_entry.checkin)
            self.db_original_checkout   = copyAsTime(self.db_entry.checkout)
            self.db_original_flags      = self.db_entry.flags
            self.db_original_duty_time  = RelTime(self.db_entry.duty_time)
            self.db_original_prev_informed_duty_time = RelTime(self.db_entry.prev_informed_duty_time)
            self.db_original_refcheckin = copyAsTime(self.db_entry.refcheckin)
            self.db_original_refcheckout = copyAsTime(self.db_entry.refcheckout)
            self.db_original_sched_end_time = copyAsTime(self.db_entry.sched_end_time)
        else:
            self.pcat       = PubCat(pcat)
            self.start_date = copyAsDate(start_date)
            self.end_date   = copyAsDate(end_date) or forwardDate(start_date)
            self.checkin    = copyAsTime(checkin)
            self.checkout   = copyAsTime(checkout)
            self.flags      = FlagSet(flags)
            self.duty_time  = RelTime(duty_time)
            self.prev_informed_duty_time = RelTime(prev_informed_duty_time)
            self.refcheckin = copyAsTime(refcheckin)
            self.refcheckout = copyAsTime(refcheckout)
            self.sched_end_time = copyAsTime(sched_end_time)
            self.db_entry   = None
        self.do_not_update_prev_inf_duty_time = bool(do_not_update_prev_inf_duty_time)
        self.clearSkipDayFromRoster()

    def __cmp__(self, o):
        return (cmp(self.start_date, o.start_date)
                or cmp(self.end_date, o.end_date)
                or cmp(PubCat.dbValue(self.pcat), PubCat.dbValue(o.pcat))
                or cmp(self.checkin or AbsTime(0),  o.checkin or AbsTime(0))
                or cmp(self.checkout or AbsTime(0), o.checkout or AbsTime(0))
                or cmp(self.flags, o.flags)
                or cmp(self.duty_time or RelTime(0), o.duty_time or RelTime(0))
                or cmp(self.prev_informed_duty_time or RelTime(0), o.prev_informed_duty_time or RelTime(0))
                or cmp(self.refcheckin or AbsTime(0), o.refcheckin or AbsTime(0))
                or cmp(self.refcheckout or AbsTime(0), o.refcheckout or AbsTime(0))
                or cmp(self.sched_end_time or AbsTime(0), o.sched_end_time or AbsTime(0))
                )

    def _stime(self, date_or_time):
        s = str(date_or_time)
        if date_or_time:
            s = (s[:5]+s[9:])
        return s.lower()
        
    def __str__(self):
        if self.db_entry:
            db_dates = " %5s-%-5s" % (self._stime(self.db_original_start_date),
                                      self._stime(self.db_original_end_date))
            if self.dbExists():
                db_state = " "
            elif self.db_entry.getI().getCurrentP():
                db_state = "<"
            else:
                db_state = "*" 
        else:
            db_dates = " %5s %-5s" % ("","")
            db_state = "-"
        return "%8s %5s-%5s [%11s/%-11s] %5s/%5s %5s / %-11s %-20s%s%1s" % (
            self.pcat,
            self._stime(self.start_date),
            self._stime(self.end_date),
            self._stime(self.checkin),
            self._stime(self.checkout),
            self.duty_time,
            self.prev_informed_duty_time,
            self._stime(self.refcheckin),
            self._stime(self.refcheckout),
            self.flags,
            db_dates,
            db_state)
            
    def setSkipDayFromRoster(self):
        self.skip_day_from_roster = True
        
    def clearSkipDayFromRoster(self):
        self.skip_day_from_roster = False
        
    def isSkipDayFromRoster(self):
        return self.skip_day_from_roster
        
    def canMerge(self, other):
        """
        Check if this Activity can be merged with another Activity.
        A merge can be made if both Activity:s have:
            - same pcat and checkin, and
            - same duty_time and prev_informed_duty_time, and
            - same flags, except for wop_delimiters flags.
            - same prev_informed_duty_time
            - same refcheckin
            - same refcheckout
        unless one of the Activity:s:
            - has a first_in_wop flag, and
            - starts AFTER the other.
        """
        return (
           not (self.isSkipDayFromRoster() | other.isSkipDayFromRoster())
           and isEqual((self.pcat, other.pcat),
                       (self.checkin, other.checkin),
                       (self.flags - FlagSet.wop_delimiters,
                        other.flags - FlagSet.wop_delimiters),
                       (self.duty_time, other.duty_time),
                       (self.prev_informed_duty_time, other.prev_informed_duty_time),
                       (self.refcheckin, other.refcheckin),
                       (self.refcheckout, other.refcheckout),
                       (self.sched_end_time, other.sched_end_time)
                       )
           and not (self.start_date > other.start_date and self.flags & FlagSet.first_in_wop)
           and not (other.start_date > self.start_date and other.flags & FlagSet.first_in_wop)
           )
            
    def dbExists(self):
        """
        True if there, for the start_date of this Activity:
        - originally existed an entry covering this date, and
        - that entry hasn't been removed, and
        - its date range still covers this date.
        """
        return self.db_entry is not None \
           and self.db_entry.getI().getCurrentP() is not None \
           and self.db_entry.end_date > AbsTime(self.start_date)
       
    def dbCreate(self, crew):
        """
        Create a crew_publish_info entry with data from this Activity.
        Referred in self.db_entry.
        """
        self.db_entry = TM.crew_publish_info.create(
                                (crew, AbsTime(self.start_date)))
        return self.dbReinit()
        
    def dbSaveTail(self, crew, new_start_date):
        """
        Save a copy of the original db entry for this Activity, with the only
          difference that the start_date is modified.
        This is required when the original db entry was removed/modified,
          but it was only partially covered by the publishing period used in
          the current run. Whatever was outside the period must be preserved.
        """
        db_tail = TM.crew_publish_info.create((crew, copyAsTime(new_start_date)))
        Plan.setDirtyTable("crew_publish_info")
        db_tail.end_date  = copyAsTime(self.db_original_end_date)
        db_tail.pcat      = self.db_original_pcat
        db_tail.checkin   = copyAsTime(self.db_original_checkin)
        db_tail.checkout  = copyAsTime(self.db_original_checkout) 
        db_tail.flags     = self.db_original_flags 
        db_tail.duty_time = RelTime(self.db_original_duty_time)
        db_tail.prev_informed_duty_time = RelTime(self.db_original_prev_informed_duty_time)
        db_tail.refcheckin = copyAsTime(self.db_original_refcheckin)
        db_tail.refcheckout = copyAsTime(self.db_original_refcheckout)
        db_tail.sched_end_time = copyAsTime(self.db_original_sched_end_time)
        return True
        
    def dbReinit(self):
        """
        Populate self.db_entry with data from this Activity.
        Self.db_entry refers to crew_publish_info in the model.
        """
        Plan.setDirtyTable("crew_publish_info")
        self.db_entry.end_date  = AbsTime(self.end_date)
        self.db_entry.pcat      = PubCat.dbValue(self.pcat)
        self.db_entry.checkin   = copyAsTime(self.checkin)
        self.db_entry.checkout  = copyAsTime(self.checkout)
        self.db_entry.flags     = str(self.flags)
        self.db_entry.duty_time = RelTime(self.duty_time)
        self.db_entry.prev_informed_duty_time \
                                = RelTime(self.prev_informed_duty_time)
        self.db_entry.refcheckin = copyAsTime(self.refcheckin)
        self.db_entry.refcheckout = copyAsTime(self.refcheckout)
        self.db_entry.sched_end_time = copyAsTime(self.sched_end_time)
        return True
        
    def dbUpdate(self, modified=False):
        """
        Update, if needed, self.db_entry with data from this Activity.
        Self.db_entry refers to crew_publish_info in the model.
        """
        
        # End date from this Activity.
        if not isSameDate(self.db_entry.end_date, self.end_date):
            self.db_entry.end_date = copyAsTime(self.end_date)
            modified = True
            
        # Pubcat from this Activity
        newpcat = PubCat.dbValue(self.pcat)
        if not isEqual((self.db_entry.pcat, newpcat)):
            self.db_entry.pcat = newpcat
            modified = True
            
        # Checkin/out from this Activity.
        if not isEqual((self.db_entry.checkin, self.checkin)):
            self.db_entry.checkin = copyAsTime(self.checkin)
            modified = True
        if not isEqual((self.db_entry.checkout, self.checkout)):
            self.db_entry.checkout = copyAsTime(self.checkout)
            modified = True
        
        # Flags - some special considerations:
        # - If updating from start day of db entry, then 
        #     first-in-wop flag shall be taken from this Activity.
        # - Otherwise (merge - this start > db start),
        #     keep first-in-wop from db entry.
        # - (The case when this activity is first-in-wop in a merge should not
        #     occur due to save() logic involving canMerge(); but we don't check
        #     for that here.)
        dbflags = FlagSet(self.db_entry.flags)
        if isSameDate(self.db_entry.start_date, self.start_date):
            if FlagSet.first_in_wop in dbflags:
                if not FlagSet.first_in_wop in self.flags:
                    dbflags -= FlagSet.first_in_wop
                    self.db_entry.flags = str(dbflags)
                    modified = True
            else:
                if FlagSet.first_in_wop in self.flags:
                    dbflags |= FlagSet.first_in_wop
                    self.db_entry.flags = str(dbflags)
                    modified = True
        if not isEqual((dbflags - FlagSet.first_in_wop, self.flags - FlagSet.first_in_wop)):
            self.db_entry.flags = str((dbflags & FlagSet.first_in_wop) | self.flags)
            modified = True
           
        # Current and previously informed duty time from this Activity.
        if not isEqual((self.db_entry.duty_time, self.duty_time)):
            self.db_entry.duty_time = RelTime(self.duty_time)
            modified = True
        if not isEqual((self.db_entry.prev_informed_duty_time, self.prev_informed_duty_time)):
            self.db_entry.prev_informed_duty_time = RelTime(self.prev_informed_duty_time)
            modified = True
        
        # Reference checkin
        if not isEqual((self.db_entry.refcheckin, self.refcheckin)):
            self.db_entry.refcheckin = copyAsTime(self.refcheckin)
            modified = True

        # Reference checkout
        if not isEqual((self.db_entry.refcheckout, self.refcheckout)):
            self.db_entry.refcheckout = copyAsTime(self.refcheckout)
            modified = True

        # Scheduled end time
        if not isEqual((self.db_entry.sched_end_time, self.sched_end_time)):
            self.db_entry.sched_end_time = copyAsTime(self.sched_end_time)
            modified = True
        
        if modified:
            Plan.setDirtyTable("crew_publish_info")
        return modified
        
    def dbRemove(self):
        """
        Remove self.db_entry from crew_publish_info in the model.
        Will only occur if self.dbExists() returns True.
        """
        if not self.dbExists():
            return False
        else:
            self.db_entry.remove()
            Plan.setDirtyTable("crew_publish_info")
            return True
        
class Generator(object):
    """
    Generate crew activity data for a specified period or
        the publishing period currently set in Plan.
    """
    
    def __init__(self, start_date, end_date, crew_list, area, context, sel_mode, freeze_x_flag=False):
        print "SETUP RESCHEDULING GENERATOR:",
        t1 = time.time()
        if start_date or end_date:
            assert (start_date and end_date), \
                   "Both start and end date must be specified."
            assert (start_date < end_date), \
                   "End date must be greater than start date."
            print "[PERIOD: %s-%s]" % (start_date, end_date),
        else:
            print "[PERIOD: PP]",
        self.start_date = copyAsDate(start_date or Plan.pp_start_date)
        self.end_date = copyAsDate(end_date or Plan.pp_end_date)
        self.freeze_x_flag = freeze_x_flag
        
        if context is not None:
            self.context = context
            print "[GIVEN CONTEXT: %s]" % context
        else:
            if crew_list:
                if area is None or area == Cui.CuiNoArea:
                    area = Cui.CuiScriptBuffer
                if isinstance(crew_list, str):
                    crew_list = [crew.strip() for crew in crew_list.split(",")]
                # Make 'area' contain the rosters for the listed crew.
                t2 = time.time()
                Cui.CuiDisplayGivenObjects(
                      Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, crew_list)
                print "[%s CREW IN AREA %s: %0.2fs]" % (
                        len(crew_list),area,time.time()-t2),
                
            if area is None:
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, 'PLAN')
                self.context = 'sp_crew'
            else:
                Cui.CuiSetCurrentArea(Cui.gpc_info, area)
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
                self.context = 'default_context'
            print "[CONTEXT: %s]" % self.context
        print "SETUP DONE. (%0.2fs)" % (time.time() - t1)            

    def generate(self):
        print "READING PLAN DATA, COVERING PERIOD %s-%s..." \
              % (self.start_date, self.end_date)
        t = time.time()
        roster_select = 'rescheduling.%%crew_is_active_in_period%%(%s,%s)' \
                        % (self.start_date,self.end_date)
        wop_select = 'rescheduling.%%wop_has_homebase_in_period%%(%s,%s)' \
                     % (self.start_date,self.end_date)
                         
        rosters = RI(R.iter('iterators.roster_set', where=roster_select),{
            'crewid':      'crew.%id%',
            },{
            'wops':RI(R.iter('iterators.wop_set', where=wop_select),{
                'start_hb':   'rescheduling.%wop_start_date_hb%',
                'end_hb':     'rescheduling.%wop_end_date_hb%',
                'is_on_duty': 'wop.%is_on_duty%',
                'is_ignore':  'rescheduling.%wop_pcat_ignore%',
                'duty_times_per_day': 'rescheduling.%wop_duty_times_per_day%',
                  # format: "1102,510,000,000,1014,442," covering start_hb/end_hb
                },{
                'trips':RI(R.iter('iterators.trip_set'),{
                    'pcat':         'rescheduling.%trip_pcat%',
                    'start_hb':     'rescheduling.%trip_start_date_hb%',
                    'end_hb':       'rescheduling.%trip_end_date_hb%',
                    'checkin_hb':   'rescheduling.%trip_checkin_hb%',
                    'checkout_hb':  'rescheduling.%trip_scheduled_checkout_hb%',
                    'flags':        'rescheduling.%trip_flags%',
                    },{
                    'duties':RI(R.iter('iterators.duty_set'),{
                        'pcat':               'rescheduling.%duty_pcat%',
                        'code':               'concat(default(duty.%code%,"?CODE?"),"/",default(duty.%group_code%,"?GRP?"))',
                        'start_hb':           'rescheduling.%duty_start_date_hb%',
                        'end_hb':             'rescheduling.%duty_end_date_hb%',
                        'rest_start_hb':      'rescheduling.%duty_start_date_hb%',
                        'rest_end_hb':        'rescheduling.%duty_rest_end_date_hb%',
                        'flags':              'rescheduling.%duty_flags%',
                        'rest_flags':         'rescheduling.%duty_rest_flags%',
                        'checkin_hb':         'rescheduling.%duty_closest_checkin%',
                        'checkout_hb':        'rescheduling.%duty_closest_scheduled_checkout_hb%',
                        'reference_check_in': 'rescheduling.%reference_check_in%',
                        'refcheckin_valid':   'rescheduling.%reference_check_in_valid%', 
                        'do_not_update_prev_inf_duty_time':'rescheduling.%do_not_update_prev_inf_duty_time%',
                        },{
                        'legs':RI(R.iter('iterators.leg_set'),{
                            'start_hb': 'rescheduling.%leg_start_date_hb%',
                            'end_hb':   'rescheduling.%leg_end_date_hb%',
                            'flags':    'rescheduling.%leg_flags%',
                            })
                        })
                    })
                })
            }).eval(self.context)
            
        t = time.time() - t
        print "READ DONE. FOUND",len(rosters),"ROSTERS (%.2fs)." % t
        
        t = time.time()
        r = 0
        m = 0
        e = 0
        Plan.logcount = min(Plan.maxlogcount, len(rosters))
        print "MAPPING PLAN DATA," \
              "LOGGING UP TO", Plan.logcount, "MODIFIED ROSTERS..."
        for roster in rosters:
            if not roster.crewid:
                continue
            r += 1
            wops = roster.chain('wops')
            
            # Update the crew_publish_info according to the activity map.
            #
            # If there is any inconsistency, before or after updating the data,
            # retry (once) with removing any existing crewinfo before updating.
            # (Any inconsistency remaining after one retry will remain...)
            # NOTE: can only be performed if the whole roster period is informed.
            
            done = False
            can_fix_inconsistency = Plan.sel_mode in (ROSTER_PUBLISH,INFORM_ALL)
            retrying = False
            while not done:
                activities = ActivityMap(roster.crewid,
                                         self.start_date,
                                         self.end_date)
                for wop in wops:
                    activities.addWop(wop)
                    for trip in wop.chain('trips'):
                        activities.addTrip(trip)
                        for duty in trip.chain('duties'):
                            activities.updateDuty(duty)
                            for leg in duty.chain('legs'):
                                activities.updateLeg(leg)

                try:
                    if can_fix_inconsistency and not retrying:
                        if not activities.dbConsistencyCheck():
                            # This roster was stored with inconsistencies.
                            activities.removeOverlapsFromDb()
                            retrying = True
                            continue
                    # Update, then check for consistency.
                    modified = activities.store()
                    if activities.dbConsistencyCheck():
                        # This roster is dealt with and consistent.
                        if modified:
                            m += 1
                            Plan.logstep(True)
                        else:
                            Plan.logstep(retrying)
                        done = True
                    else:
                        # This roster is dealt with BUT INCONSISTENT.
                        if can_fix_inconsistency and not retrying:
                            # Try to fix the inconsistency.
                            activities.removeOverlapsFromDb()
                            retrying = True
                        else:
                            # Couldn't fix the inconsistency. Leave as is.
                            m += int(modified)
                            Plan.logstep(True)
                            done = True
                    
                except:
                    Plan.logstep(True)
                    raise
                
        t = time.time() - t
        print "MAPPING DONE.",r,"ROSTERS,",m,"MODIFIED (%.2fs)" % t

        if len(Plan.undef_tasks):
            print "DETECTED",len(Plan.undef_tasks),"UNDEFINED TASKS."
            for code,crew in sorted(Plan.undef_tasks.items()):
                print "  %s, %d crew: %s" % (code,len(crew),sorted(crew)[:10]),
                if len(crew) > 9: print "..."
                else: print


