"""
Simple report to show aircraft minimum connection times 
which are considered in Retiming.

by Niklas Johansson in April 2015.

"""
import carmensystems.publisher.api as p
from RelTime import RelTime

from carmstd import bag_handler
from report_sources.include.SASReport import SASReport

    
class Report(SASReport):

   
    def create(self):
        
        tbh = bag_handler.WindowChains()
        
        #Generate the report header and footer
        
        SASReport.create(self, "Report for crew staying with Aircraft")
        if tbh.warning:
            self.add(tbh.warning)
        
        if not tbh.bag:
            return 
        mc = self.add(p.Column(border=p.border_all()))
        mc.add_header(p.Row("Region", "AC changes","AC legs","AC legs excl",
                            font=p.font(weight=p.BOLD),
                            border=p.border_all()))    
        for leg_bag in tbh.bag.report_kpi.ac_region_leg_set():
            if leg_bag.leg.is_oag():
                continue
            row = mc.add(p.Row())
            row.add(leg_bag.leg.ac_region())
            row.add(str(leg_bag.report_kpi.tot_leg_ac_connectivity()))
            row.add(str(leg_bag.report_kpi.tot_ac_legs()))
            row.add(str(leg_bag.report_kpi.tot_ac_legs_excl_first_in_duty()))
        mc.page()
            
if __name__ == "__main__":
    from carmstd import report_generation as rg
    rg.reload_and_display_report("HTML")
