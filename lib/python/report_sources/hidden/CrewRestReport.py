#

#
__version__ = "$Revision$"
"""
CrewRestReport
Module for doing:
# -----------------------------------------------------
# This report shall mimic the layout of the Crew Rest
# dialog as well as possible (see crew_rest.xml) while
# maintaining the SAS report basic layout.
# -----------------------------------------------------
# Created:    2006-11-15
# By:         Jeppesen, Yaser Mohamed
@date:21Aug2009
@author: Per Groenberg (pergr) (introduced header)
@org: Jeppesen Systems AB
"""


from RelTime import RelTime
from carmensystems.publisher.api import *
import carmensystems.rave.api as R
import modelserver as M
from report_sources.include.SASReport import SASReport
import Cui
import tm
import carmusr.HelperFunctions as HF

class RestCrew(dict):
    """
    Wrapper for crew lookups used by report, looks in model row and rave
    """
    
    def __init__(self, tm_row):
        self['tm_row'] = tm_row
        
        crew_id = str(self.crew.id)
        for info in tm.TM.tmp_cr_flight_info:
            flight_id = info.activity_id
            break
        else:
            raise Exception('CrewRestReport.py:: Table tmp_cr_flight_info not populated')
        
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   Cui.CuiScriptBuffer,
                                   Cui.CrewMode,
                                   Cui.CrewMode, [str(self.crew.id)])
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
        rob_raw, = R.eval('default_context',
                          R.foreach(R.iter('iterators.leg_set',
                               where='leg.%%activity_id%% = "%s"'%flight_id),
                               'crg_duty_points.%rob_addition%'))
        for ix, rob in rob_raw:
            self['rob_reduction'] = rob
            break
        else:
            raise Exception("CrewRestReport.py:: Unable to lookup reduction in ravecode")
        
    def __getattr__(self, attr):
        try:
            if hasattr(self['tm_row'],attr):
                return getattr(self['tm_row'], attr)
            else:
                return self[attr]
        except:
            raise AttributeError('CrewRestReport.RestCrew has no attribute %s'%attr)
    
class CrewRestReport(SASReport):
    
    def create(self):
        SASReport.create(self, 'Crew Rest Report')

        # The tables used in the xml form are loaded. These tables always
        # exist since the rest-form window must be opened to print the report.
        
        tm.TM(["tmp_cr_flight_info","tmp_cr_active_crew"])

        # Copies of all tmp_cr_active_crew rows,
        # with additional attributes collected via rave lookups.
        active_crew = [RestCrew(crew) for crew in tm.TM.tmp_cr_active_crew]
        
        # Flight information to be printed (compare with the crew rest window)
        for flight in tm.TM.tmp_cr_flight_info:
            break # 'flight' is now the first (and only) tmp_cr_flight_info row

        # Definition of the layout (compare with the crew rest window).
        
        headerBox = Column(Text("Flight information", font=font(weight=BOLD)))
        
        flightBox = Column(Row(Text("Flight",
                                    border=border(top=1, bottom=1),
                                    background='#cdcdcd',
                                    colspan=2)),
                           Row(Text("No:", font=font(weight=BOLD)),
                               Text("%s" %flight.flight_no, align=RIGHT)),
                           Row(Text("AC Type: ", font=font(weight=BOLD)),
                               Text("%s" %flight.ac_type, align=RIGHT)))

        departureBox = Column(Row(Text("Departure",
                                       border=border(top=1, bottom=1),
                                       background='#cdcdcd',
                                       colspan=2)),
                              Row(Text("Time: ", font=font(weight=BOLD)),
                                  Text("%s" %flight.departure_time, align=RIGHT)),
                              Row(Text("Station: ", font=font(weight=BOLD)),
                                  Text("%s" %flight.departure_station, align=RIGHT)))
        
        arrivalBox = Column(Row(Text("Arrival",
                                     border=border(top=1, bottom=1),
                                     background='#cdcdcd',
                                     colspan=2)),
                            Row(Text("Time: ", font=font(weight=BOLD)),
                                Text("%s" %flight.arrival_time, align=RIGHT)),
                            Row(Text("Station: ", font=font(weight=BOLD)),
                                Text("%s" %flight.arrival_station, align=RIGHT)))
        
        activeRequiredCrewBox = Column(Row(Text("Active/Required Crew",
                                                border=border(top=1, bottom=1),
                                                background='#cdcdcd',
                                                colspan=2)),
                                       Row(Text("FC: ", font=font(weight=BOLD)),
                                           Text("%s" %flight.ac_rc_fc, align=RIGHT)),
                                       Row(Text("CC: ", font=font(weight=BOLD)),
                                           Text("%s"%flight.ac_rc_cc, align=RIGHT)))

        crewBunksBox = Column(Row(Text("Crew Bunks",
                                       border=border(top=1, bottom=1),
                                       background='#cdcdcd',
                                       colspan=2)),
                              Row(Text("FC: ", font=font(weight=BOLD)),
                                  Text("%s" %flight.crew_bunks_fc, align=RIGHT)),
                              Row(Text("CC: ", font=font(weight=BOLD)),
                                  Text("%s" %flight.crew_bunks_cc, align=RIGHT)))


        # Put the flight summary box toghether from all the pieces
        flightSummaryBox = Column(headerBox,
                                  Row(flightBox,             Text(" "),
                                      departureBox,          Text(" "),
                                      arrivalBox,            Text(" "),
                                      activeRequiredCrewBox, Text(" "),
                                      crewBunksBox))

        # The crew information part of the report. It shall have the same
        # layout and contain the same information as the crew rest window.
        
        # Add the crew-main-function header and the information headers.
        crew_box = {'F':None, 'C':None}
        for cat,title in ('F',"Flight Crew"),('C',"Cabin Crew"):
            crew_box[cat] = Column(Text(title, font=font(weight=BOLD)),
                                  Row(Text("Emp No"),     Text(" "),
                                      Text("First Name"), Text(" "),
                                      Text("Last Name"),  Text(" "),
                                      Text("Rank"),       Text(" "),
                                      Text("Op. Rank"),   Text(" "),
                                      Text("Rest Start"), Text(" "),
                                      Text("Rest End"),   Text(" "),
                                      Text("Reduction"),
                                      border=border(top=1, bottom=1),
                                      background='#cdcdcd'))
         
        # The paste_box appears on a separate page in the report. Contains
        # info for the trackers to paste into the info sent to the aircraft.
        
        paste_box = Column(
            Text("FDP PLAN:%s ALL TIMES UTC"
                 % (flight.flight_no)),
            Text("DEP:%5s ARR:%5s BLOCKTIME:%s"
                 % (flight.departure_time.time_of_day(),
                    flight.arrival_time.time_of_day(),
                    str(flight.block_time).replace(':','H'))))
        
        # As the crew should be presented according to rank and as the crew
        # table is not sorted (although the sorting order is a part of the
        # table), the relevant information (compare with the crew rest window)
        # for each crew member is added to a list along with the sort order.
        # The list is then sorted according to the order and the result is
        # added to the report. 
        # The crew is handled by main function.
        
        crew_list = {'F':[], 'C':[]}
        min_poss_arr = {'F':None, 'C':None}
        for crew in active_crew:
            cat = (crew.main_func == 'F' and 'F') or 'C'
            crew_list[cat].append(crew)
            if crew.fdp_start and crew.fdp_uc:
                min_poss_arr[cat] = min(
                    min_poss_arr[cat] or AbsTime("31Dec2099"),
                    AbsTime(crew.fdp_start) + RelTime(crew.fdp_uc))
        
        # Latest possible (legal) arrival is departure + minimum fdp_uc (max
        # fdp due to unforseen circumstances) for any F/C crew.
        
        paste_box.add(Text("LATEST POSS ARR FD %s CC %s" % (
            (min_poss_arr['F'] and min_poss_arr['F'].time_of_day()) or "-",
            (min_poss_arr['C'] and min_poss_arr['C'].time_of_day()) or "-")))
    
        # Append individual crew data rows (separate boxes for F and C).        
        # Index determines background color of each row.
        
        for cat in 'F','C':
            for index, crew in enumerate(sorted(crew_list[cat],
                               cmp=lambda x,y: cmp(x.sort_order,y.sort_order))):
                crew_box[cat].add(Row(
                    Text("%s" % crew.crew.empno,     align=LEFT),   Text(" "),
                    Text("%s" % crew.first_name,     align=LEFT),   Text(" "),                     
                    Text("%s" % crew.last_name,      align=LEFT),   Text(" "),                     
                    Text("%s" % crew.rank,           align=CENTER), Text(" "),                     
                    Text("%s" % crew.assigned_rank,  align=CENTER), Text(" "),                     
                    Text("%s" % crew.rest_start_rel, align=CENTER), Text(" "),                     
                    Text("%s" % crew.rest_end_rel,   align=CENTER), Text(" "),                     
                    Text("%s" % crew.rob_reduction,  align=CENTER),
                    background=('#ffffff','#dedede')[index%2]))
                if crew.rest_start_rel and crew.rest_end_rel:
                    paste_box.add(Text("%5s R:%5s-%5s"
                                   % (crew.crew.empno,
                                      str(crew.rest_start_rel).replace(':','H'),
                                      str(crew.rest_end_rel).replace(':','H'))))
                else:                   
                    paste_box.add(Text("%5s R:NO REST" % crew.crew.empno))

        # The entire report is created.
        
        self.add(Isolate(Row(flightSummaryBox)))
        self.add(" ") # Empty spaces added to improve readability
        self.add(crew_box['F'])
        self.add(" ")
        self.add(crew_box['C'])
        self.add(" ")
        self.newpage()
        self.add(paste_box)
        self.add(" ")

