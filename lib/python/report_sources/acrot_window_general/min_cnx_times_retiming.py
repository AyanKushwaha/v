"""
Simple report to show aircraft minimum connection times 
which are considered in Retiming.

by Stefan Hammar in March 2012.

"""
import carmensystems.publisher.api as p
from RelTime import RelTime

from carmstd import bag_handler
from report_sources.include.SASReport import SASReport

    
class Report(SASReport):

   
    def create(self):
        
        tbh = bag_handler.WindowChains()
        
        #Generate the report header and footer
        
        SASReport.create(self, "Min cnx times for the Aircrafts")
        if tbh.warning:
            self.add(tbh.warning)
        
        if not tbh.bag:
            return 
        
        data = {}
        
        for leg_bag in tbh.bag.atom_set():
            if leg_bag.leg.is_last_in_trip():
                continue
            
            key = (str(leg_bag.retiming.ac_size()).split(".")[-1],
                   leg_bag.arrival_airport_name(),
                   leg_bag.departure_airport_name(),
                   leg_bag.retiming.next_leg_arrival_airport(),
                   leg_bag.retiming.min_ac_cxn_old(),
                   leg_bag.retiming.min_ac_cxn(),
                   leg_bag.leg.is_charter(),
                   str(leg_bag.retiming.connection_type()).split(".")[-1],
                   leg_bag.studio_retiming.len_connection_after_in_ac_with_retiming())
            item = data.setdefault(key, [0, RelTime(1000)])
            item[0] += 1
            item[1] = min(leg_bag.retiming.ac_cxn_time(),
                          item[1])
            
        mc = self.add(p.Column(border=p.border_all()))
        mc.add_header(p.Row("From", "At", "To", 
                            "Ac Size", "Charter", "Con type",
                            p.Text("Min cnx time Rave", width=40),
                            p.Text("New cnx time Rave", width=40),
                            "#",
                             p.Text("Min used cnx time", width=40),
                             p.Text("Retimed cnx time", width=40),
                            font=p.font(weight=p.BOLD),
                            border=p.border_all()))    
        for key, data in sorted(data.iteritems()):
            row = mc.add(p.Row())
            row.add(key[2]) 
            row.add(key[1])
            row.add(key[3])
            row.add(key[0])
            row.add(key[6])
            row.add(key[7])
            row.add(key[4])
            row.add(key[5])
            row.add(data[0])
            row.add(p.Text(data[1], 
                           colour="#000000" 
                                  if data[1] >= key[4] 
                                  else "#FF0000"))
            row.add(key[8])
            mc.page()
            
if __name__ == "__main__":
    from carmstd import report_generation as rg
    rg.reload_and_display_report("HTML")
