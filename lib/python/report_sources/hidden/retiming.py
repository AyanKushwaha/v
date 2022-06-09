"""
Retiming Report

@date: Feb 2010
@author: Mattias Nolander
@org: Jeppesen Systems AB

Modified for SAS by Stefan Hammar in March 2012.

Note: This report requires that a Pairing rule set is loaded.
      See the Rave module "retiming_leg" for details. 

"""
import carmensystems.studio.reports.CuiContextLocator as CuiContextLocator
import carmensystems.publisher.api as p
import carmensystems.rave.api as r
import Cui
import Gui
from RelTime import RelTime

from report_sources.include.SASReport import SASReport
import report_sources.include.ReportUtilsFromOTS as ReportUtilsFromOTS
from carmstd import bag_handler, retiming_basics
import carmstd.report_generation as rg
import carmstd.studio.area as area

one_day = RelTime("24:00")

def dates2freq_str(dates):
    freq = [0] * 7
    for date in dates:
        freq[int(date.time_of_week()/one_day)] = 1
    return "".join(v and str(n + 1) or "." 
                   for n,v in enumerate(freq))
    
class Report(SASReport):

    def my_show_trips(self, leg_identifiers, replace=True):
        
        # Execute as Studio command for correct undo handling, 
        Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                               "Show from Retiming Report",
                               Gui.POT_REDO,
                               Gui.OPA_OPAQUE)
        
        self.current_context.reinstate()
        if replace:
            Cui.gpc_unmark_all(Cui.gpc_info)
            Cui.CuiSetCurrentArea(Cui.gpc_info, self.filter_area)
            Cui.gpc_unmark_all(Cui.gpc_info)
        
        byp = {'FORM': 'retiming_filter_form',
               'FL_TIME_BASE': 'LDOP',
               'CRC_VARIABLE_0': 'leg_identifier',
               'CRC_VALUE_0': ",".join(leg_identifiers),
               'FILTER_METHOD': replace and "REPLACE" or "ADD",
               'FILTER_MARK': 'LEG'}
            
        Cui.CuiFilterObjects(byp, Cui.gpc_info,
                             self.filter_area, "CrrFilter", 
                             "retiming_filter_form", 0)
        
    def create_pdf(self):
        self.current_context.reinstate()
        rg.display_prt_report(source=__name__,
                              rpt_args={"inter":"NO"},
                              format="PDF")
                 
    def create(self):
        """
        Will create the actual report
        """
        self.current_context = CuiContextLocator.CuiContextLocator().\
                               fetchcurrent()
        self.filter_area = area.getOppositArea()
        
        tbh = bag_handler.WindowChains()
       
        dated_mode, = r.eval("global_is_dated_mode")
        
        w = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea) + 1
     
        self.setpaper(orientation=p.LANDSCAPE)   
        
        #Generate the report header and footer
        SASReport.create(self, "Retiming Report (for legs in window %s)" % w,
                         pageWidth=770, orientation=p.LANDSCAPE)
        if tbh.warning:
            self.add(tbh.warning)
        
        if not tbh.bag:
            return 
        
        # Generate Statistics table
        info_tab = ReportUtilsFromOTS.SimpleTable('Retiming Statistics', 
                                              use_page=False)
        info_tab.add(p.Row(
            p.Text('Possible Retiming Legs: '),
            p.Text(tbh.bag.retiming.num_possible_legs(), align=p.RIGHT)))
        info_tab.add(p.Row(
            p.Text('Actually Retimed Legs: '),
            p.Text(tbh.bag.retiming.num_retimed_legs(), align=p.RIGHT)))
        
        c = p.Column()
        if self.arg("inter") != "NO":
            c.add(p.Text("  Regenerate",
                         link=p.link(__name__)))
            c.add(p.Text("  Create PDF",
                          action=p.action(self.create_pdf)))
        
        self.add(p.Isolate(p.Row(info_tab, c)))
        
        totc = 0
        # Generate the main table
        retimed_tab = ReportUtilsFromOTS.SimpleTable('Retimed legs',
                                                     use_page=True,
                                                     expandable=False)

        retimed_tab.add_sub_title("Flight")
        retimed_tab.add_sub_title('Dep-Arr')
        retimed_tab.add_sub_title('A/C')
        retimed_tab.add_sub_title("Days")
        retimed_tab.add_sub_title('Original Dep-Arr Time  ')
        retimed_tab.add_sub_title('Retimed')
        retimed_tab.add_sub_title('Retimed Dep-Arr Time  ')
        retimed_tab.add_sub_title("Cost")
        retimed_tab.add_sub_title("Cost reg")
        retimed_tab.add_sub_title(' ')
        retimed_tab.add_sub_title(' ')
        retimed_tab.add_sub_title('Alternatives')
        
        _sk = ('flight_carrier', 
               "flight_number",                                 
               "leg_number", 
               "flight_suffix")    
        
        for flight_bag in tbh.bag.report_retiming.flight_set(sort_by=_sk,
                                                             where=("not deadhead",
                                                                    "report_retiming.any_leg_in_bag_has_retiming")):
            
            for ng, group_bag in enumerate(flight_bag.retiming.retiming_group(sort_by="retiming.regularity_key")):
            
                cost_reg = retiming_basics.regularity_cost_in_bag(group_bag)[0]
                for nl, retimed_bag in enumerate(group_bag.report_retiming.dflight_set(\
                        sort_by="report_retiming.first_departure_date_in_bag")):
                    
                    new_flight = nl + ng == 0
                    
                    if new_flight:
                        retimed_tab.table.page()
                        
                    days_col = p.Column()
                    if dated_mode: 
                        for alp_bag in retimed_bag.actual_leg_period():
                            dates = [day_set.retiming_leg.scheduled_start_lc()
                                     for day_set in
                                     alp_bag.report_retiming.day_set()]
    
                            day_str = "%s-%s %s " % (ReportUtilsFromOTS.abs2guidatestr(min(dates)),
                                                     ReportUtilsFromOTS.abs2guidatestr(max(dates)),
                                                     dates2freq_str(dates))
                            days_col.add(p.Text(day_str,
                                            font=p.font(face=p.MONOSPACE)))
                    else:
                        dates = [day_set.retiming_leg.scheduled_start_lc()
                                 for day_set in
                                 retimed_bag.report_retiming.day_set()]
                        days_col.add(p.Text(dates2freq_str(dates),
                                            font=p.font(face=p.MONOSPACE)))
        
                    cost1 = sum(leg_set.retiming.leg_penalty_retiming()
                                for leg_set in
                                retimed_bag.atom_set()) 
                            
                    leg_identifiers = []
                    for leg_bag in retimed_bag.atom_set():
                        leg_identifiers.append(str(leg_bag.leg_identifier()))
                        
                    if retimed_bag.retiming.has_retiming():
                        retimed_str = '%s-%s ' % \
                                (ReportUtilsFromOTS.abs2hhmm(\
                                    retimed_bag.report_retiming.leg_start()),
                                 ReportUtilsFromOTS.abs2hhmm(\
                                    retimed_bag.report_retiming.leg_end()))  
                    else:
                        retimed_str = ""
                    
                    ac_family_info = ",".join(sorted(set([_bag.leg.ac_type() for _bag in 
                                                          retimed_bag.atom_set()])))
                
                    row = retimed_tab.add(p.Row())
                    if new_flight:
                        row.set(border=p.border(top=1))   
                        flight_info = '%s %4.3i%s%s' % \
                               (retimed_bag.report_retiming.leg_flight_carrier(),
                                retimed_bag.report_retiming.leg_flight_number(),
                                retimed_bag.report_retiming.leg_leg_number(),
                                retimed_bag.report_retiming.leg_flight_suffix())
                               
                        station_info =  '%3s-%3s' % \
                               (retimed_bag.report_retiming.leg_start_station(),
                                retimed_bag.report_retiming.leg_end_station())
                    else:
                        flight_info = station_info = ""
                         
                    rg_sep_args = {}
                    if not new_flight and not nl:
                        rg_sep_args["border"] = p.border(top=1, colour="#AAAAAA") 
                            
                    if self.arg("inter") != "NO":
                        show = p.Text("Show",
                                    font=p.font(size=8),
                                    action = p.action(self.my_show_trips,
                                                      args = (leg_identifiers,)))
                        add = p.Text("Add ",
                                     font=p.font(size=8),
                                     action = p.action(self.my_show_trips,
                                                       args = (leg_identifiers, False)))
                    else:
                        show = add = ""
                    
                    
                    row.add(p.Row(
                        p.Text(flight_info),
                        p.Text(station_info),
                        p.Text(ac_family_info),
                        days_col,
                        p.Text('%s-%s ' %
                               (ReportUtilsFromOTS.abs2hhmm(
                                  retimed_bag.report_retiming.leg_start_orig()),
                                ReportUtilsFromOTS.abs2hhmm(
                                  retimed_bag.report_retiming.leg_end_orig())),
                               **rg_sep_args
                               ),
                        p.Text("%s  " % retimed_bag.retiming.retiming_as_string(),
                               align=p.RIGHT),
                        p.Text(retimed_str),
                        p.Text('%s ' % (cost1 and str(cost1) or ""),
                               align=p.RIGHT),
                        p.Text("%s" % (str(cost_reg) if (cost_reg and not nl) else "" ),
                               align=p.RIGHT),
                        show,
                        add,
                        p.Text(retimed_bag.retiming.retiming_alternatives(),
                               font=p.font(size=7)),
                               ))
                    totc += cost1
                    
        self.add('')
        self.add(retimed_tab)
        self.add('')
        
        info_tab.add(p.Row("Total Cost for Retimed Leg:", 
                           p.Text("%s" % totc, align=p.RIGHT),
                           border=p.border(bottom=1)))
        
        info_tab.add(p.Row("Regularity cost considered in APC:", 
                           p.Text(tbh.bag.apc_pac.use_retime_regularity(),       
                                  align=p.RIGHT))) 
        c, _, g = retiming_basics.regularity_cost_in_bag(tbh.bag)
        info_tab.add(p.Row("Number of not regular groups:", 
                           p.Text("%s" % g, 
                                  align=p.RIGHT)))
        info_tab.add(p.Row("Total Cost for not regular groups:", 
                           p.Text("%s" % c, 
                                  align=p.RIGHT)))
                          
                
if __name__ == "__main__":
    rg.reload_and_display_report()
