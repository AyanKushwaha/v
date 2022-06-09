
#
#######################################################
#
# Duty Points Calculations Report
#
# -----------------------------------------------------
# This report shall show how the duty points have been
# calculated.
# -----------------------------------------------------
# Created:    2007-01-24
# By:         Jeppesen, Yaser Mohamed
#
#######################################################
from __future__ import division
from carmensystems.publisher.api import *
import carmensystems.rave.api as R
import modelserver as M
from report_sources.include.SASReport import SASReport
import Cui
import carmstd.rave
from utils.rave import RaveIteratorClassic
import Cfh
import RelTime
import tempfile
import os
global_context = "default_context"

def collectCrew(startTime):
    global global_context
    context = global_context
    
    # Show the crew info first.
    crewInfo, = context.eval(R.foreach(R.iter("iterators.chain_set"),
                                       "crew.%id%", "crew.%firstname%",
                                       "crew.%surname%",
                                       "crew.%%rank_at_date%%(%s)" % startTime,
                                       "crew.%%base_at_date%%(%s)" % startTime))
    return crewInfo[0][1:]

def collectRosterInfo(startTime, endTime, oma16_valid = False):
    # Extract all information regarding the roster that is necessary:
    
    class LegInfo(RaveIteratorClassic):
        fields = {"number": "leg.%flight_nr%",
                  "activity_code": "leg.%code%",
                  "deadhead": "leg.%is_deadhead%",
                  "start_station": "leg.%start_station%",
                  "start_time": "leg.%activity_scheduled_start_time_UTC%",
                  "end_time": "leg.%end_UTC%",
                  "end_station": "leg.%end_station%",
                  "stop_time": "leg.%time_to_next_leg%"}
        iterator = RaveIteratorClassic.iter('iterators.leg_set')
        
        
    class DutyInfo(RaveIteratorClassic):
        context = global_context
        fields = {"start_time": "crg_duty_points.%duty_start%",
                  "end_time": "crg_duty_points.%duty_end%",
                  "pass_time": "crg_info.%_duty_time%",
                  "pass_no_night_upg": "crg_info.%_duty_time_no_night_upg%",
                  "day_points": "duty_time.%1x24_hrs%",
                  "seven_day_duty": "crg_duty_points.%duty_in_7x24_hrs%",
                  "time_to_next": "duty.%time_to_next_duty%",
                  "is_long_haul": "duty.%is_long_haul%", 
                  "next_duty_is_flight_duty": "duty.%next_duty_is_flight_duty%", 
                  "rest_in_24": "rest.%in_24hrs_duty%",
                  # SubpartQ definitions used in the Subq section
                  "fdp": "crg_duty_points.%fdp_time%",
                  "max_fdp": "crg_duty_points.%max_duty_fdp%",
                  "extended": "crg_duty_points.%extended_fdp_flag%",
                  "dp": "crg_duty_points.%dp_time%",
                  "min_req_rest": "crg_duty_points.%required_rest%",
                  "act_rest": "crg_duty_points.%actual_rest%",
                  "check_in": "crg_duty_points.%dp_start%",
                  "block_on": "crg_duty_points.%block_on%",
                  "check_out": "crg_duty_points.%dp_end%",
                  "sector_reduction": "crg_duty_points.%sector_reduction%",
                  "wocl_reduction": "crg_duty_points.%wocl_reduction%",
                  "sby_reduction": "crg_duty_points.%sby_reduction%",
                  "rob_addition": "crg_duty_points.%rob_addition%",
                  "break_reduction": "crg_duty_points.%break_reduction%",
                  "dp_7days": "crg_duty_points.%dp_7days%",
                  "dp_28days": "crg_duty_points.%dp_28days%",
                  "check_in_diff": "crg_duty_points.%check_in_diff_cc_fdp_extension%",
                  "use_dp": "crg_duty_points.%use_dp%",
                  "privately_traded": "duty.%is_privately_traded%",
                  "J3_code": "rescheduling.%duty_J3_code%",
                  "blh_28days_end": "report_common.%end_28_days_fwd_day%",
                  "blh_year": "crg_duty_points.%block_time_in_calendar_year%",
                  "blh_28days": "report_common.%block_time_28_days_fwd%"}
        
        nextlevels = {'legs': LegInfo()}
        # endTime is expected to be a dreaded "... 23:59"-time ... 
        iterator = RaveIteratorClassic.iter('iterators.duty_set',
                                            where=('duty.%is_on_duty% and not duty.%is_off_duty_cmp%',
                                                   'duty.%%start_UTC%%>=%s' % str(startTime),
                                                   'duty.%%start_UTC%%<%s' % str(endTime)))
    
    class OMA16DutyInfo(RaveIteratorClassic):
        context = global_context
        fields = {"start_time": "crg_duty_points.%duty_start%",
                  "end_time": "crg_duty_points.%duty_end%",
                  "pass_time": "crg_info.%_duty_time%",
                  "pass_no_night_upg": "crg_info.%_duty_time_no_night_upg%",
                  "day_points": "duty_time.%1x24_hrs%",
                  "seven_day_duty": "crg_duty_points.%duty_in_7x24_hrs%",
                  "time_to_next": "duty.%time_to_next_duty%",
                  "is_long_haul": "duty.%is_long_haul%", 
                  "next_duty_is_flight_duty": "duty.%next_duty_is_flight_duty%", 
                  "rest_in_24": "rest.%in_24hrs_duty%",
                  # OMA16 definitions used in the OMA16 section
                  "fdp": "crg_duty_points.%fdp_time%",
                  "max_fdp": "crg_duty_points.%max_duty_fdp%",
                  "extended": "crg_duty_points.%extended_fdp_flag%",
                  "dp": "crg_duty_points.%dp_time%",
                  "min_req_rest": "oma16.%min_rest_after_dp%",
                  "act_rest": "crg_duty_points.%actual_rest%",
                  "check_in": "crg_duty_points.%dp_start%",
                  "block_on": "crg_duty_points.%block_on%",
                  "check_out": "crg_duty_points.%dp_end%",
                  "sectors_num": "fdp.%num_sectors%",
                  "sby_reduction": "oma16.%standby_reduction_all%",
                  "rob_addition": "oma16.%rest_on_board_addition%",
                  "break_addition": "oma16.%split_duty_addition%",
                  "dp_7days": "crg_duty_points.%dp_7days%",
                  "dp_14days": "crg_duty_points.%dp_14days%",
                  "dp_28days": "crg_duty_points.%dp_28days%",
                  "check_in_diff": "crg_duty_points.%check_in_diff_cc_fdp_extension%",
                  "use_dp": "crg_duty_points.%use_dp%",
                  "privately_traded": "duty.%is_privately_traded%",
                  "J3_code": "rescheduling.%duty_J3_code%",
                  "blh_28days_end": "report_common.%end_28_days_fwd_day%",
                  "blh_year": "oma16.%block_time_in_calendar_year%",
                  "blh_12months": "oma16.%block_time_in_12_calendar_months%",
                  "blh_28days": "report_common.%block_time_28_days_fwd%"
                  }
        
        nextlevels = {'legs': LegInfo()}
        # endTime is expected to be a dreaded "... 23:59"-time ... 
        iterator = RaveIteratorClassic.iter('iterators.duty_set',
                                            where=('duty.%is_on_duty% and not duty.%is_off_duty_cmp% and duty_period.%is_last_duty_in_duty_period%',
                                                   'duty.%%start_UTC%%>=%s' % str(startTime),
                                                   'duty.%%start_UTC%%<%s' % str(endTime)))
    
    if oma16_valid:
        return OMA16DutyInfo().eval("default_context")
    else:
        return DutyInfo().eval("default_context")


def isOMA16valid(startDate):
    return R.eval('parameters.%%oma16_a_valid%%(%s)' % startDate)[0]


class DutyPointsReport(SASReport):

    def create(self):
        startTime, = R.eval('station_utctime("CPH", %s)' % self.arg("startDate"))
        endTime, = R.eval('station_utctime("CPH", %s + 24:00)' % self.arg("endDate"))
        oma16_valid, = R.eval('parameters.%%oma16_a_valid%%(%s)' % self.arg("startDate"))

        # Collect all info first to prevent context trouble
        crewInfo = collectCrew(startTime)
        title = 'Duty Report'
        showPlanData = False
        #SASReport.create(self, title, showPlanData, 520, PORTRAIT,
        SASReport.create(self, title, showPlanData, 770, LANDSCAPE,
                            True)
        
        items = SASReport.getTableHeader(self,[
                                "Crew: " + (crewInfo[0]+"  -  "+crewInfo[1]+" "+crewInfo[2]),
                                "Period: %s - %s" % (startTime, endTime),
                                "Cat: " + crewInfo[3],
                                "Base: " + crewInfo[4]
                            ],
                            vertical=False, widths=None, aligns=None)

        SASReport.getHeader(self).add(items)
        SASReport.getHeader(self).add(Text(""))
        SASReport.getHeader(self).set(border=border(bottom=0))

        global HEADER
        global FBOLD

        HEADER = Font(size=12, weight=BOLD)
        FBOLD = Font(weight=BOLD)
        
        tm = M.TableManager.instance()
        
        crewTable = tm.table("crew")
        crewEmpTable = tm.table("crew_employment")

        global crewId
        global global_context

        context = global_context
        
        rosterInfo = collectRosterInfo(startTime, endTime, oma16_valid)

        activityBox = Column()
        dutyTimeBox = Column()
        subqBox     = Column()
        subqBox2     = Column()      
        linesA = linesT = linesS = linesSC = 57
        linesLimit = 55
        linesALimit = 33
        firstPage = 1
        acc_duty = 0

        for duty in rosterInfo:
            # Fill in activityBox values
            i = 0
            dutyStr = ""
            for leg in duty.chain("legs"):
                row = ["", "","",dutyStr]
                if i == 0:
                    # If first leg in duty, show dep date and time
                    row[0] = str(duty.start_time)[:-5] # Start Date
                    row[1] = str(duty.start_time)[-5:] # Start Time
                if i == (len(duty.chain("legs")) - 1):
                    # if last, show arr time
                    row[2] = str(duty.end_time)[-5:] # End Time

                # Complete the row by adding and formatting the leg information
                i = i + 1

                # Add the row information to the report
                if linesA > linesALimit:
                    if firstPage == 0:
                        activityBox.newpage()
                    firstPage = 0
                    activityBox.add(self.displayActivityHead())
                    linesA = 0
                linesA += 1
                deadhead = ""

                if duty.privately_traded:
                    if duty.J3_code == "J3P F":
                        leg_activity = "J3P F"
                    elif duty.J3_code == "J3P P":
                        leg_activity = "J3P %s" % leg.number
                    elif duty.J3_code == "J3F P":
                        leg_activity = "J3F %s" % leg.number
                else:
                    if leg.activity_code == 'FLT': 
                        leg_activity = leg.number 
                        if leg.deadhead:
                            deadhead = "(DH)"
                    else: 
                        leg_activity = leg.activity_code
                    
                if leg.stop_time is None:
                    leg.stop_time = "-"
                activityBox.add(Row(Text("%s" %row[0]),
                                    Text("%s" %row[1]),
                                    Text("%s" %row[2]),
                                    #Text("%s" %row[3]),
                                    Text("%s %s" % (leg_activity,deadhead), align=RIGHT), 
                                    Text("%s" %leg.start_station), 
                                    Text("%s" %str(leg.start_time)[-5:]),
                                    Text("%s" %str(leg.end_time)[-5:]),
                                    Text("%s" %leg.end_station),
                                    Text("%s" %leg.stop_time, align=RIGHT),
                                    Text("")))
            # end for leg
            # Done creating activityBox
            
            # Fill in dutyTimeBox values
            night = str(duty.pass_time - duty.pass_no_night_upg)
            if duty.is_long_haul and duty.next_duty_is_flight_duty:
                slippingTime = duty.time_to_next
            else:
                slippingTime = "00:00"
            
            if linesT > linesLimit:
                dutyTimeBox.newpage()
                dutyTimeBox.add(self.displayDutyTimeHead())
                linesT = 0
            linesT += 2
            if acc_duty:
                acc_duty = acc_duty + duty.pass_time
            else:
                acc_duty = duty.pass_time
            dutyTimeBox.add(Row(Text("%s" %str(duty.start_time)[:-5]),
                                Text("%s" %str(duty.pass_time)),
                                Text("%s" %night),
                                Text("%s" %str(duty.day_points)),
                                Text("%s" %str(duty.seven_day_duty)),
                                Text("%s" %str(acc_duty)),
                                Text("%s" %duty.time_to_next),
                                Text("%s" %slippingTime),
                                Text("%s" %duty.rest_in_24)))
            # Done creating dutyTimeBox

            # Fill in subqBox values
        for duty in rosterInfo:
            if duty.use_dp:
                if linesS > linesLimit:
                    subqBox.newpage()
                    if(oma16_valid):
                        subqBox.add(self.displayOMA16Head())
                    else:
                        subqBox.add(self.displaySubqHead())
                    linesS = 0
                linesS += 2
                if(oma16_valid):
                    subqBox.add(Isolate(Row(Text("%s" %str(duty.check_in)[:-5], width=50),
                                Text("%s%s / (%s)" % (str(duty.fdp)[-5:],str(duty.extended),str(duty.max_fdp)[-5:]), width=55),
                                Text("%s" % str(duty.dp)[-5:], width=25),
                                Text("%s" % str(duty.min_req_rest), width=25),
                                Text("%s" % str(duty.act_rest), width=25),
                                Text("%s" % str(duty.check_in)[-5:], width=25),
                                Text("%s" % str(duty.block_on)[-5:], width=25),
                                Text("%s" % str(duty.check_out)[-5:], width=25),
                                Text("%s" % str(duty.sectors_num), width=30),
                                Text("%s" % str(duty.sby_reduction), width=25),
                                Text("%s" % str(duty.rob_addition), width=25),
                                Text("%s" % str(duty.break_addition), width=25),
                                Text("%s" % str(duty.check_in_diff)[-5:], width=25),
                                Text("%s" % str(duty.dp_7days), width=60),
                                Text("%s" % str(duty.dp_14days), width=60),
                                Text("%s" % str(duty.dp_28days), width=60),
                                )))
                else:
                    subqBox.add(Isolate(Row(Text("%s" %str(duty.check_in)[:-5], width=50),
                                Text("%s%s / (%s)" % (str(duty.fdp)[-5:],str(duty.extended),str(duty.max_fdp)[-5:]), width=55),
                                Text("%s" % str(duty.dp)[-5:], width=25),
                                Text("%s" % str(duty.min_req_rest), width=25),
                                Text("%s" % str(duty.act_rest), width=25),
                                Text("%s" % str(duty.check_in)[-5:], width=25),
                                Text("%s" % str(duty.block_on)[-5:], width=25),
                                Text("%s" % str(duty.check_out)[-5:], width=25),
                                Text("%s" % str(duty.sector_reduction), width=30),
                                Text("%s" % str(duty.wocl_reduction), width=25),
                                Text("%s" % str(duty.sby_reduction), width=25),
                                Text("%s" % str(duty.rob_addition), width=25),
                                Text("%s" % str(duty.break_reduction), width=25),
                                Text("%s" % str(duty.dp_7days), width=60),
                                Text("%s" % str(duty.dp_28days), width=60),
                                Text("%s" % str(duty.check_in_diff)[-5:], width=25),
                                )))
            # Fill in subqBox2 values
        for duty in rosterInfo:
            if duty.use_dp:
                if linesSC > linesLimit:
                    subqBox2.newpage()
                    if(oma16_valid):
                        subqBox2.add(self.displayOMA16Head2())
                    else:
                        subqBox2.add(self.displaySubq2Head())
                    linesSC = 0
                linesSC += 2
                if(oma16_valid):
                    subqBox2.add(Isolate(Row(
                        Text("%s" % str(duty.check_in)[:-5], width=50),
                        Text("%s" % str(duty.blh_year)[-6:], width=55, align=RIGHT),
                        Text("%s" % str(duty.blh_12months)[-6:], width=55, align=RIGHT),
                        Text("%s  [<-%5s]" % (str(duty.blh_28days), str(duty.blh_28days_end)), width=85, align=RIGHT),
                    )))
                else:
                    subqBox2.add(Isolate(Row(
                        Text("%s" % str(duty.check_in)[:-5], width=50),
                        Text("%s" % str(duty.blh_year)[-6:], width=55, align=RIGHT),
                        Text("%s  [<-%5s]" % (str(duty.blh_28days), str(duty.blh_28days_end)), width=85, align=RIGHT),
                    )))
                                
        # end for duty
        
        # The entire report is created.
        self.add(activityBox)       
        self.add(dutyTimeBox)
        self.add(subqBox)
        self.add(subqBox2)

    def displayActivityHead(self):
        
        global HEADER
        global FBOLD
        
        return Column(
                    Text(""),
                    Row(Text("Activities",
                        font=HEADER)),
                    Text(""),
                    Row(Text("Date"),
                        Text("Start"),
                        Text("End"),
                        #Text("Duty"),
                        Text("Activity"),
                        Text("From"),
                        Text("STD"),
                        Text("STA/ETA/ATA"),
                        Text("To"),
                        Text("Stop time"),
                        font=FBOLD),colspan=9)
    
    def displayDutyTimeHead(self):
        
        global HEADER
        global FBOLD
        
        return Column(
                    Text(""),
                    Isolate(
                        Row(Text("Union agreements calculation"),font=HEADER)),
                    Row(Text("Duty Time"),
                        Text(""),
                        Text(""),
                        Text(""),
                        Text(""),
                        Text(""),
                        Text("Time off"),
                            font=HEADER),
                    Row(Text("")),
                    Row(Text("Date"),
                        Text("Pass"),
                        Text("Night"),
                        Text("24 hours"),
                        Text("7 days"),
                        Text("Acc Duty"),
        # Create the time off cells
                        Text("To next duty"),
                        Text("Slipping time"),
                        Text("24 hours"),
                        font=FBOLD))
    
    def displayDutyCalcHead(self):
        
        global HEADER
        global FBOLD
        
        return Column(
                    Text(""),
                    Text("Points - FOM calculations",
                            font=HEADER),
                    Row(Text(
                            "")),
                    Row(Text("Date"),
                        Text("CheckIn"),
                        Text("BlockOn"),
                        Text("Per hour"),
                        Text("DutyTime"),
                        Text("Points"),
                        Text("Landing"),
                        Text("Passive"),
                        Text("Rest"),
                        Text("At block on"),
                        Text("At C/O"),
                        Text("7 days"),
                        Text("Remaining"),
                        font=FBOLD))
    
    def displaySubqHead(self):
        
        global HEADER
        global FBOLD
        
        return Isolate(Column(
                    Text(""),
                    Text("Duty calculations", font=HEADER),
                    Row(Text("")),
                    Row(Text("Date", width=50),
                        Text("FDP/(MAX)", width=55),
                        Text("DP", width=25),
                        Text("Req rest", width=25),
                        Text("Act rest", width=25),
                        Text("C/I", width=25),
                        Text("B/O", width=25),
                        Text("C/O", width=25),
                        Text("Sector red", width=30),
                        Text("WOCL red", width=25),
                        Text("SBY red", width=25),
                        Text("ROB add", width=25),
                        Text("Break red", width=25),
                        Text("DP 7 days", width=30),
                        Text("DP 28 days", width=60),
                        Text("FDP CI diff", width=25),
                        font=FBOLD)))
    
    def displaySubq2Head(self):
        
        global HEADER
        global FBOLD
        
        return Isolate(Column(
                    Text(""),
                    Text("Duty calculations continued", font=HEADER),
                    Row(Text("")),
                    Row(Text("Date", width=50),
                        Text("BLH in c. year", width=55),
                        Text("BLH 28 days fwd", width=85),
                        font=FBOLD)))
    
    def displayOMA16Head(self):
        
        global HEADER
        global FBOLD
        
        return Isolate(Column(
                    Text(""),
                    Text("OMA16 - Duty calculations",
                            font=HEADER),
                    Row(Text(
                            "")),
                    Row(Text("Date", width=50),
                        Text("FDP/(MAX)", width=55),
                        Text("DP", width=25),
                        Text("Req rest", width=25),
                        Text("Act rest", width=25),
                        Text("C/I", width=25),
                        Text("B/O", width=25),
                        Text("C/O", width=25),
                        Text("Sectors num", width=30),
                        Text("SBY red", width=25),
                        Text("ROB add", width=25),
                        Text("Break add", width=25),
                        Text("FDP CI diff", width=25),
                        Text("DP 7 days", width=60),
                        Text("DP 14 days", width=60),
                        Text("DP 28 days", width=60),
                        font=FBOLD)))
    
    def displayOMA16Head2(self):
        
        global HEADER
        global FBOLD
        
        return Isolate(Column(
                    Text(""),
                    Text("OMA16 - Duty calculations continued",
                            font=HEADER),
                    Row(Text(
                            "")),
                    Row(Text("Date", width=50),
                        Text("BLH in c. year", width=55),
                        Text("BLH in 12 c. months", width=85),
                        Text("BLH 28 days fwd", width=85),
                        font=FBOLD)))
    
"""
A form used for selecting information needed to create a duty points report
"""

class DutyPointsForm(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)
        
        now, = R.eval('station_localtime("CPH", fundamental.%now%)')

        startDate = int(now)
        self.startDate = Cfh.Date(self, "STARTDATE", startDate)
        self.startDate.setMandatory(1)

        endDate = int(now + RelTime.RelTime(6,0,0))
        self.endDate = Cfh.Date(self, "ENDDATE", endDate)
        self.endDate.setMandatory(1)

        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")

        form_layout =  """
FORM;DUTYPOINTS_FORM;Duty Report

FIELD;STARTDATE;Start (CET)
FIELD;ENDDATE;End (CET)

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""

        duty_points_form_file = tempfile.mktemp()
        f = open(duty_points_form_file, 'w')
        f.write(form_layout)
        f.close()
        self.load(duty_points_form_file)
        os.unlink(duty_points_form_file)

    def getValues(self):
        """
        Function returning the values set in the form
        """
        return (self.startDate.convertIn(), self.endDate.convertIn())

def setEnvironment():
    """
    Collects the necessary information about the context
    """
    global crewId
    global global_context
    
    currentArea = Cui.CuiGetCurrentArea(Cui.gpc_info)
    crewId = Cui.CuiCrcEvalString(Cui.gpc_info, currentArea, "object", "crew.%id%")
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, [crewId], 0)
    global_context = carmstd.rave.Context("window", Cui.CuiScriptBuffer)

def runReport():
    """
    Creates a select form
    """
    setEnvironment()

    global duty_points_form
    try:
        duty_points_form == duty_points_form
    except:
        duty_points_form = DutyPointsForm("Duty_Points")

    duty_points_form.show(1)
    # OK button pressed
    if duty_points_form.loop() == Cfh.CfhOk:
        dates = duty_points_form.getValues()

        # Format the argument to fit the publisher api. Also set default values
        # for start and end date if no values where given.
        arg = "startDate=" + dates[0]
        arg += " endDate=" + dates[1]
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, "plan", "DutyPointsReport.py", 0, arg)
