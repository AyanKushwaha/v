#

#
__version__ = "$Revision$"
"""
MiniFilter
Module for doing:
MiniFilter Form from CCT included in CCR aswell
Purpose: Mini filter form which shall provide options for all the most common
          search criterias that a tracker (and planner :) ) uses
@date:05Sep2008
@author: Per Groenberg (pergr), CCT version last touched by salvad
@org: Jeppesen Systems AB
"""
#
# Purpose: Mini filter form which shall provide options for all the most common
#          search criterias that a tracker uses
#

import Cfh as Cfh
import carmusr.tracking.CfhExtension as CfhExtension
import modelserver as M
import os
import re
import tempfile
import Cui
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import carmusr.HelperFunctions as HF
import carmstd
from utils.rave import RaveIterator
import carmstd.studio.area as StdArea
import carmensystems.studio.gui.private.Zoom as Zoom
import Errlog
import carmusr.application as application
import weakref
# set the following to true to get verbose messages in the
# error log.
debugOutput = 0

# the keys of the following dict will be accepted as input
# in the activity codes input field. the rave queries will
# use the values rather than the keys.
activityCodesDict = {
                    "STANDBY":["A, A0*, A1*,A2, A6*, AC, R*, H*, SB, AO, AS, AT, W, WP, WO"],
                    "BLANK DAY":["BL,J7",],
                    "OFF DUTY":["F*,!FLT,VA*,LA5,LA8,LA21,LA31,LA35,LA36,LA37,"+
                                "LA39,LA42,LA44,LA53,LA56,LA57,LA58,LA59,LA66,LA84"],
                    "MEETING":["K*,O*,G*,MT*,M*"],
                    "TRAINING":["B*,!BL*,!B7,!BOA,!BUS,C*,D*,E*,N*,S*,!SB*,!SD,Y*,Z*,!YK,"+
                                "!YK1,!YK5,!YK9,!YX4,!YY"],
                    "GROUND TRANSPORT":[""],
                    "ILLNESS":["IL*,LA91*,LA92*,!ILC"]
                    }


# tracking has a special case, Flight Duty selection as well
if application.isTracking:
    activityCodesDict['FLIGHT DUTY'] = ['FLIGHT_DUTY']


class MiniSelectForm(Cfh.Box):
    """
        Custom CFH box constituting a mini filter form.
    """
    def __init__(self, *args):
        Cfh.Box.__init__(self, "Mini Filter Form")

        SMALL_FIELD_SIZE = 10
        MIDDLE_FIELD_SIZE = 14
        X_LARGE_FIELD_SIZE = 50
        HUGE_FIELD_SIZE = 80

        # Numbering of the sections is from the spec. They have then
        # been reordered.
        #
        # 0: FORM INFO
        # 0 From date/time selection
        if application.isTracking or application.isDayOfOps:
            rave_start_time = 'round_down(station_localtime("CPH", fundamental.%now%), 24:00)'
            self.default_start = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, "None", rave_start_time))
            self.default_end = self.default_start + RelTime(23, 59)
        else:
            self.default_start = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                                               "None", "fundamental.%pp_start%"))
            self.default_end = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                                             "None", "fundamental.%pp_end%"))
        if application.isTracking:
            self.start_date = SpecialDateStart(self, "START_DATE", time=self.default_start)
        else:
            self.start_date = CfhExtension.SpecialDate(self, "START_DATE", time=self.default_start)
        self.start_date.setMandatory(1)
        self.start_time = Cfh.Clock(self, "START_TIME", RelTime(0))
        self.end_date = CfhExtension.SpecialDate(self, "END_DATE", time=self.default_end)
        self.end_time = Cfh.Clock(self, "END_TIME", RelTime(23, 59))

        # 0 Select method
        self.select_method = Cfh.String(self, "FILTER_METHOD",
                                        SMALL_FIELD_SIZE, "REPLACE")
        self.select_method.setMandatory(1)
        self.select_method.setMenuOnly(1)
        self.select_method.setMenuString("Filter Method;ADD;SUBFILTER;REPLACE")

        # 4th section
        # 4 Rank selection
        #
        # Rank list is hardcoded after request.             Woodpecker 628
        #ranks = CfhExtension.getRankSet()                  Woodpecker 628
        ranks = "Ranks;F*;FC;FP;FR;A*;AP;AS;AH;*"         # Woodpecker 628
        self.rank = CfhExtension.RestrictedString(self, "RANK",
                                                  MIDDLE_FIELD_SIZE, "*", ranks)
        self.rank.setMandatory(1)
        self.rank.setTranslation(Cfh.String.ToUpper)
        self.rank.setMenuString(ranks)

        # 4 Planning Group selection
        planning_groups = CfhExtension.getPlanningGroupSet()
        self.planning_group = CfhExtension.RestrictedString(self, "PLANNING_GROUP",
                                                    MIDDLE_FIELD_SIZE, "*",
                                                    planning_groups)
        self.planning_group.setMandatory(1)
        self.planning_group.setTranslation(Cfh.String.ToUpper)
        self.planning_group.setMenuString(planning_groups)

        # 4 Civic station
        homeBases = CfhExtension.getHomeBaseSet()
        homeBases = homeBases.replace("Homebases","Civic Station")
        homeBases = homeBases.replace("SHA","")         # Woodpecker 796
        homeBases = homeBases.replace("TOS","")         # Woodpecker 796
        self.civic_station = CfhExtension.RestrictedString(self,
                                                            "CIVIC_STATION",
                                                            MIDDLE_FIELD_SIZE,
                                                            "*",
                                                            homeBases)
        self.civic_station.setMandatory(1)
        self.civic_station.setTranslation(Cfh.String.ToUpper)
        self.civic_station.setMenuString(homeBases)


        # 4 Resource crew
        self.resource_crew = CfhExtension.RestrictedString(self,
                                                            "RESOURCE_CREW",
                                                            MIDDLE_FIELD_SIZE,
                                                            "*",
                                                            planning_groups)
        self.resource_crew.setMandatory(1)
        self.resource_crew.setTranslation(Cfh.String.ToUpper)
        self.resource_crew.setMenuString(planning_groups)


        # 1: QUALIFICATION INFO
        # 1 AC qualification selection.
        oldAcQual = CfhExtension.getAcQualSet()      # Woodpecker: 630 08/05/19
        acQual = self.deleteOldQual(oldAcQual)
        self.ac_qual = CfhExtension.RestrictedString(self, "AC_QUAL",
                                                     MIDDLE_FIELD_SIZE, "*",
                                                     acQual,
                                                     separator=",+")
        self.ac_qual.setMandatory(1)
        self.ac_qual.setTranslation(Cfh.String.ToUpper)
        self.ac_qual.setMenuString(acQual)

        # 1 Airport qualification selection.
        # Complete Airport qualification list is used for validation.    # Woodpecker FAT-CCT 251
        apQual1 = CfhExtension.getAirportQualSet()         # Woodpecker FAT-CCT 251
        # Airport list is hardcoded after request.         # Woodpecker FAT-CCT 251
        apQual = "Airports;CFU;FNC;HMV;INN;JKH;LCG;FAE;GZP;SFJ;SMI;*"      # Woodpecker FAT-CCT 251
        #print apQual
        self.ap_qual = CfhExtension.RestrictedString(self,"AP_QUAL",
                                                     MIDDLE_FIELD_SIZE, "*",
                                                     apQual1,      # Woodpecker FAT-CCT 25
                                                     separator=",+")
        self.ap_qual.setMandatory(0)
        self.ap_qual.setTranslation(Cfh.String.ToUpper)
        self.ap_qual.setMenuString(apQual)


        # 1 Crew Qualifications
        # Instructor qualification selection. NOTE: Conversion dictionary
        # needed in search
        self.crewQualInfo = CfhExtension.CrewQualInfo(self,"Crew Qualifications",40,"*")
        (self.menuCrewQualList, self.validCrewQualList) = self.crewQualInfo.getCrewQualMenuString()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | 
        # Hard coded to satisfy Woodpecker FAT-CCT 159.                         |
        # Exception with no logic to relate with the tables design.             |
        self.menuCrewQualList = self.menuCrewQualList[:-2]                    # |
        self.menuCrewQualList += ";ALL (LIFUS TRI/TRE SFI/SFE); ;*"           # |
        self.validCrewQualList += ";ALL (LIFUS TRI/TRE SFI/SFE);"             # |
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | 

        self.crew_qual = CfhExtension.RestrictedString(self, "CREW_QUAL",
                                                       X_LARGE_FIELD_SIZE, "*",
                                                       self.validCrewQualList,
                                                       separator=",+")
        self.crew_qual.setMandatory(1)
        self.crew_qual.setTranslation(Cfh.String.ToUpper)
        self.crew_qual.setMenuString(self.menuCrewQualList)

        # 2: ROSTER INFO
        # 2 Above/Below Rank
        self.above_or_below_rank = Cfh.String(self, "ABOVE_OR_BELOW_RANK",
                                             MIDDLE_FIELD_SIZE,
                                             "*")
        self.above_or_below_rank.setMandatory(1)
        self.above_or_below_rank.setMenuOnly(1)
        self.above_or_below_rank.setEditable(False)
        self.above_or_below_rank.setMenuString("Above/Below Rank;ABOVE;BELOW;*")

        # 2 Overbooked
        if application.isTracking or application.isDayOfOps:
            menu = ["Staffing",
                    "Overstaffed JAR",
                    "Overstaffed SRVC",
                    "Understaffed JAR",
                    "Understaffed SRVC",
                    "Understaffed/Reduced SRVC",
                    "*"]
            self.overbooked = Cfh.String(
                self, "OVERBOOKED", max(len(m) for m in menu), "*")
            self.overbooked.setMandatory(1)
            self.overbooked.setMenuOnly(1)
            self.overbooked.setEditable(False)
            self.overbooked.setMenuString(";".join(menu))
        else:
            self.overbooked = Cfh.String(self, "NOT_IN_USE_1",1,'*')

        # 2 Deadhead
        self.deadhead = Cfh.String(self, "DEADHEAD", SMALL_FIELD_SIZE, "*")
        self.deadhead.setMandatory(1)
        self.deadhead.setMenuOnly(1)
        self.deadhead.setEditable(False)
        self.deadhead.setMenuString("Deadhead;YES;*")

        # 2 dep-station
        self.dep_station = CfhExtension.AirportStringList(self,
                                                        "DEP_STATION",
                                                        MIDDLE_FIELD_SIZE,
                                                        "*")
        self.dep_station.setMandatory(1)
        self.dep_station.setTranslation(Cfh.String.ToUpper)

        # 2 dest-station
        self.dest_station = CfhExtension.AirportStringList(self,
                                                        "DEST_STATION",
                                                        MIDDLE_FIELD_SIZE,
                                                        "*")
        self.dest_station.setMandatory(1)
        self.dest_station.setTranslation(Cfh.String.ToUpper)

        # 3rd section
        # 3 Location
        if application.isTracking or application.isDayOfOps:
            self.location = CfhExtension.AirportStringList(self,"LOCATION",
                                                           MIDDLE_FIELD_SIZE, "*")
            self.location.setMandatory(1)
            self.location.setTranslation(Cfh.String.ToUpper)
        else:
            self.location = Cfh.String(self, "NOT_IN_USE_2",1,'*')

        # 3 Activity code

        activityCodesDict["GROUND TRANSPORT"] = self.getTransportCodes("GT")
        codes = CfhExtension.getActivityCodes()
        choiceList = activityCodesDict.keys()
        choiceList.sort()
        activityChoices = reduce(lambda x, y: x+";"+y, choiceList)
        possibleInput = codes + ";" + activityChoices
        self.activity_code = CfhExtension.RestrictedString(self,
                                                           "ACTIVITY_CODE",
                                                           HUGE_FIELD_SIZE,
                                                           "*",
                                                           possibleInput,
                                                           separator=",+",
                                                           wildcards="*")
        self.activity_code.setMandatory(1)
        self.activity_code.setEditable(1)
        self.activity_code.setTranslation(Cfh.String.ToUpper)
        self.activity_code.setMenuString("Activity code;"+activityChoices+";*")

        # 3 Working days
        working_days_string = "Working Days;1;2;3;4;5;6;7;8;9;*"
        self.working_days = CfhExtension.RestrictedString(self,
                                        "WORKING_DAYS",
                                        MIDDLE_FIELD_SIZE,
                                        "*",
                                        working_days_string,
                                        separator=",+")
        self.working_days.setMandatory(1)
        self.working_days.setMenuString(working_days_string)

        # Buttons
        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")
        self.reset = Cfh.Reset(self, "B_RESET")
        self.default_button = DefaultButton(self,
                                            "B_DEFAULT",
                                            "Default",
                                            "_Default")


        form_layout = """
FORM;MINISELECT_FORM;Mini Filter Form
COLUMN;;10
LABEL
COLUMN
FIELD;FILTER_METHOD;Filter Method
GROUP;;NOSEP
COLUMN;;1
EMPTY
"""
        if application.isTracking or application.isDayOfOps:
            form_layout += """ 
COLUMN;;6
LABEL;STO Start:
EMPTY
COLUMN;;14
FIELD;START_DATE;Date:
FIELD;START_TIME;Time:
COLUMN;;6
LABEL;STO End:
EMPTY
COLUMN;;14
FIELD;END_DATE;Date:
FIELD;END_TIME;Time:
"""
        else:
            form_layout += """ 
COLUMN;;6
LABEL;STO Start:
EMPTY
COLUMN;;14
FIELD;START_DATE;Date:
COLUMN;;6
LABEL;STO End:
EMPTY
COLUMN;;14
FIELD;END_DATE;Date:
"""
        form_layout += """ 
GROUP
COLUMN;;8
LABEL;Civic Station
LABEL;Resource Crew
COLUMN;;16
FIELD;CIVIC_STATION
FIELD;RESOURCE_CREW
COLUMN;;10
LABEL;Rank
LABEL;Planning Group
COLUMN;;16
FIELD;RANK
FIELD;PLANNING_GROUP
GROUP
COLUMN;;8
LABEL;Aircraft Qualif.
LABEL;Airport Qualif.
COLUMN;;16
FIELD;AC_QUAL
FIELD;AP_QUAL
COLUMN;;10
LABEL;Crew Qualification
EMPTY
COLUMN;;16
FIELD;CREW_QUAL
EMPTY
GROUP
COLUMN;;8
LABEL;Deadhead
LABEL;Depart From
LABEL;Arrive To
COLUMN;;16
FIELD;DEADHEAD
FIELD;DEP_STATION
FIELD;DEST_STATION
"""
        if application.isTracking or application.isDayOfOps:
            form_layout += """
COLUMN;;10,BAR
LABEL;Above/Below Rank
EMPTY
LABEL;Staffing
COLUMN;;16
FIELD;ABOVE_OR_BELOW_RANK
EMPTY
FIELD;OVERBOOKED
"""
        else:
            form_layout +="""
COLUMN;;10,BAR
LABEL;Above/Below Rank           
FIELD;ABOVE_OR_BELOW_RANK
EMPTY
"""
        if application.isTracking or application.isDayOfOps:
            form_layout +="""
GROUP
COLUMN;;8
LABEL;Gaps
LABEL;Activity Code
COLUMN;;16
FIELD;LOCATION
FIELD;ACTIVITY_CODE
COLUMN;;10
LABEL;Working Days
EMPTY
COLUMN;;16
FIELD;WORKING_DAYS
EMPTY
"""
        else:
             form_layout +="""
GROUP
COLUMN;;8
LABEL;Activity Code
COLUMN;;16
FIELD;ACTIVITY_CODE
COLUMN;;10
LABEL;Working Days
EMPTY
COLUMN;;16
FIELD;WORKING_DAYS
EMPTY
"""
        form_layout +="""
BUTTON;B_OK;`Ok`;`_OK`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
BUTTON;B_RESET;`Reset`;`_Reset`
BUTTON;B_DEFAULT;`Default`;`_Default`
"""
        miniselect_form_file = tempfile.mktemp()
        f = open(miniselect_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(miniselect_form_file)
        os.unlink(miniselect_form_file)

    def compute(self, *args):

        r = Cfh.Box.compute(self, *args)

        if (self.dep_station.valof().find("+") > 0 or \
            self.dep_station.valof().find(",") > 0) and \
            (self.dest_station.valof().find("+") > 0 or \
            self.dest_station.valof().find(",") > 0):

            return "Depart from/Arrive to: Only one field with a list is allowed."

    def defaultValues(self):
        """
            Resets all values in the form to the default ones.
        """
        self.select_method.assign("REPLACE")
        self.overbooked.assign("*")
        self.location.assign("*")
        if application.isTracking or application.isDayOfOps:
            now = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                        "None", "fundamental.%now%")
            self.start_date.assign(self.default_start)
            self.end_date.assign(self.default_end)
            self.start_time.assign(self.default_start.time_of_day())
            self.end_time.assign(self.default_end.time_of_day())
        else:
            pp_start = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                                  "None", "fundamental.%pp_start%")
            pp_end = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                                "None", "fundamental.%pp_end%")
            self.start_date.assign(pp_start)
            self.end_date.assign(pp_end)


        self.rank.assign("*")
        self.civic_station.assign("*")
        self.planning_group.assign("*")
        self.resource_crew.assign("*")
        self.ac_qual.assign("*")
        self.ap_qual.assign("*")
        self.crew_qual.assign("*")
        self.above_or_below_rank.assign("*")
        self.deadhead.assign("*")
        self.dep_station.assign("*")
        self.dest_station.assign("*")
        self.activity_code.assign("*")
        self.working_days.assign("*")
        if debugOutput:
            print "The form set to default values."

    def resetAllValues(self):
        """
            Meant to be used as action for the reset button.
            Resets the values to what they were when the form was last called.
        """

        self.select_method.getValue()
        self.start_date.getValue()
        self.end_date.getValue()
        self.start_time.getValue()
        self.end_time.getValue()
        self.rank.getValue()
        self.civic_station.getValue()
        self.planning_group.getValue()
        self.resource_crew.getValue()
        self.ac_qual.getValue()
        self.ap_qual.getValue()
        self.crew_qual.getValue()
        self.above_or_below_rank.getValue()
        self.overbooked.getValue()
        self.deadhead.getValue()
        self.dep_station.getValue()
        self.dest_station.getValue()
        self.location.getValue()
        self.activity_code.getValue()
        self.working_days.getValue()
        if debugOutput:
            print "The form set to previously used values."
        return

    def getTransportCodes(self,group="GT"):
        # Get ground transport groups:
        tm = M.TableManager.instance()
        tm.loadTables(["activity_set"])
        ac_set = tm.table("activity_set")

        transp_code = ""
        for row in ac_set:
            try:
                if row.grp.id == group:
                    transp_code += "," + row.id
            except:
                pass
        return [transp_code.strip(",")]

    def setValue(self, property, value):

        if property.upper() == 'ACTIVITY':
            self.activity_code.assign(value)
        else:
            raise Exception("MiniSelectForm.setValue:: property %s not implemented!"%property)

    def getValues(self):
        """
            Function returning the values set in the form. 
        """

        crewQualIn = self.crew_qual.valof().upper()
        if crewQualIn[0:4] == "ALL ": qualValues = crewQualIn
        else: qualValues = crewQualIn.split("(")[0].rstrip()

        return {"select_method":self.select_method.valof().upper(),
                "start_date":AbsDate(self.start_date.valof()),
                "end_date":AbsDate(self.end_date.valof()),
                "start_time":RelTime(self.start_time.valof()),
                "end_time":RelTime(self.end_time.valof()),
                "rank":self.rank.valof().upper(),
                "civic_station":self.civic_station.valof().upper(),
                "planning_group":self.planning_group.valof().upper(),
                "resource_crew":self.resource_crew.valof().upper(),
                "ac_qual":self.ac_qual.valof().upper(),
                "ap_qual":self.ap_qual.valof().upper(),
                "crew_qual":qualValues,
                "above_or_below_rank":self.above_or_below_rank.valof(),
                "overbooked": self.overbooked.valof(),
                "deadhead":self.deadhead.valof(),
                "dep_station":self.dep_station.valof().upper(),
                "dest_station":self.dest_station.valof().upper(),
                "location":self.location.valof().upper(),
                "activity_code":self.activity_code.valof().upper(),
                "working_days":self.working_days.valof()
            }

    def deleteOldQual(self,acQual):

        # Filter old unwanted Aircraft types (Woodpecker: 630 08/05/19)

        newQual = acQual
        oldQual = ["AB;","AH;","AV;","CR;","D8;","FF;","F7;","MD;","M0;","M9;",
                   "Q4;","SO;","S2;","10;","11;","12;","2L;","28;","3L;","30;",
                   "47;","70;","76;","80;","91;","98;","90;","F5;","M8;"
                   ]
        for old in oldQual:
            newQual = newQual.replace(old,"")
        return newQual


class SpecialDateStart(CfhExtension.SpecialDate):
    """
        Adds a compute step to SpecialDate used for the start_date that
        updates the parent end_date field to match the new start_date
    """
    def __init__(self, *args, **kwargs):
        self.parent = weakref.ref(args[0])
        CfhExtension.SpecialDate.__init__(self, *args, **kwargs)

    def compute(self):
        self.computeIt()
        self.parent().end_date.assign(self.getValue())


class DefaultButton(Cfh.Function):
    """
        Defines a default button, resetting all values to the default ones.
    """

    def __init__(self, miniSelectObj, name, text, mnemonic):
        Cfh.Function.__init__(self, miniSelectObj, name, text, mnemonic)
        self.miniSelectObject = miniSelectObj
    def action(self):
        self.miniSelectObject.defaultValues()

def displayListOfCrew(crewIds, selectionMethod, area, startTime, endTime):
    """
        Displays the crew in crewIds in the current window,
        using the method specified by selectionMethod = [ADD|REPLACE|SUBFILTER].
    """
    is_ADD = (selectionMethod == "ADD")

    numCrews = len(crewIds)
    if debugOutput:
        print "MiniSelect: Filter method " + selectionMethod

    crewsInWindow = Cui.CuiGetCrew(Cui.gpc_info, area, "window")

    if debugOutput:
        print "MiniFilter: rosters selected with form:    %s"%len(crewIds)
        print "MiniFilter: rosters present in the window: %s"%len(crewsInWindow)

    if is_ADD:
        # First get a list of crew currently shown.
        # Then display this set in addition to crewIds
        for crewId in crewIds:
            if crewId in crewsInWindow:
                crewsInWindow.remove(crewId)
        crewIds.extend(crewsInWindow)

    if debugOutput:
        print "MiniFilter: displaying this many rosters:  %s"%len(crewIds)

    # For REPLACE the crew that should be displayed are exactly the ones in crewIds:        
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, crewIds)
    if numCrews > 0:
        HF.redrawAreaScrollHome(area)

        if debugOutput:
            print 'Zoomed window (minus/plus one day):: ', startTime, endTime
        timeMargin = RelTime(1440)
        minTime = AbsTime((startTime - AbsTime("01Jan1986") - timeMargin) / RelTime("00:01"))
        maxTime = AbsTime((endTime - AbsTime("01Jan1986") + timeMargin) / RelTime("00:01"))
        minTime = minTime.day_floor()
        maxTime = maxTime.day_ceil()

        Zoom.zoomArea(area,int(minTime),int(maxTime))

    StdArea.promptPush("%s crew selected and %s in the window"
                       % (numCrews,
                          is_ADD  and "added" or "replaced the content"))

def startMiniSelectForm(pre_set={}):
    """
        Creates a mini filter form
    """

    global mini_select_form
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    if debugOutput:
        mini_select_form = MiniSelectForm("Mini_Select_Form")
    else:
        try:
            mini_select_form == mini_select_form
        except:
            mini_select_form = MiniSelectForm("Mini_Select_Form")

    if pre_set:
        for property, value in pre_set.items():
            try:
                mini_select_form.setValue(property,value)
            except Exception, err:
                Errlog.log("Start MiniFilter From:: %s"%err)
    #mini_select_form.convertIn()
    mini_select_form.show(1)

    if mini_select_form.loop() == Cfh.CfhOk:
        values = mini_select_form.getValues()

        startTime = AbsTime(values["start_date"])+values["start_time"]
        endTime = AbsTime(values["end_date"])+values["end_time"]

        from utils.timezones import CET
        from datetime import datetime

        today = datetime.now()
        today = today.replace(tzinfo=CET)
        today += CET.dst(today)

        min_utc_offset = RelTime(CET.utcoffset(today).seconds/60)
        startTime = startTime - min_utc_offset
        endTime = endTime - min_utc_offset

        where_string = "true"
        if values["civic_station"] != "*":
            # Lookup time. Locate (Emp. tab)
            where_string += selectAndOrStatements("civic_station",values["civic_station"],
                                        startTime, endTime)
        if values["rank"] != "*":
            # Lookup time. Locate (Emp. tab)
            where_string += selectAndOrStatements("rank",values["rank"],
                                        startTime, endTime)
        if values["planning_group"] != "*":
            # Lookup time. Locate (Emp. tab)
            where_string += selectAndOrStatements("planning_group",values["planning_group"],
                                        startTime, endTime)
        if values["resource_crew"] != "*":
            # Locate
            where_string += " and studio_select.%%is_resource_crew%%(%s, \"%s\")"% \
                                (startTime, values["resource_crew"])
        if values["ac_qual"] != "*":
            # "ACQUAL" + subtype in period between starting and ending date-times.
            where_string += selectAndOrStatements("ac_qual",values["ac_qual"],
                                        startTime, endTime, "ACQUAL")
        if values["ap_qual"] != "*":
            # "AIRPORT" + subtype in period between starting and ending date-times.
            where_string += selectAndOrStatements("ap_qual",values["ap_qual"],
                                        startTime, endTime, "AIRPORT")
        if values["crew_qual"] != "*":
            # supertype + subtype in period between starting and ending date-times.
            if debugOutput:
                print "MiniFilter: values[crew_qual] = " + values["crew_qual"]
            # first, loop through arguments and check
            # if "ALL SUPERTYPE" exist somewhere.
            cq = values["crew_qual"].replace("+",",").split(",")
            mainType = []
            ctrl = cq[0]
            if ctrl[0:4] == "ALL " and not ctrl[3:5] == " (":
                # replace this one with a
                # list of all subtypes, comma-separated:
                mainType = [ctrl[4:]]
                subtypes = mini_select_form.crewQualInfo.getCrewQualSubTypesList((ctrl[4:]))
                replacer = ",".join(subtypes)
                replacer = replacer.strip(",")
                values["crew_qual"] = values["crew_qual"].replace(ctrl,replacer)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | 
            # Hard coded to satisfy Woodpecker FAT-CCT 159.                         |
            # Exception with no logic to relate with the tables design.             |
            if ctrl[3:5] == " (":                                                 # |
                values["crew_qual"] = "LIFUS,TRI,TRE,SFI,SFE"                     # |
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | 
            if debugOutput:
                print "MiniFilter: values[crew_qual] = " + values["crew_qual"]

            where_string += selectAndOrStatements("crew_qual",values["crew_qual"],
                                        startTime, endTime, mainType)

        if values["above_or_below_rank"] != "*":
            # Higher/lower rank in any leg that touches interval.
            where_string += " and studio_select.%%above_below_rank%%(\"%s\", %s, %s)"% \
                                (values["above_or_below_rank"], startTime, endTime)
        staffing_code = "*"
        if values["overbooked"] != "*":
            # Assigned more/less than needed for crew's assig. position in any leg that touches interval.
            opt_list = values["overbooked"].split()
            staffing_code = opt_list[-1]
            if opt_list[0].lower().startswith("over"):
                where_string += " and studio_select.%%too_much_crew%%(\"%s\", %s, %s)"% \
                                    (staffing_code, startTime, endTime)
            else:
                reduced = "reduced" in values["overbooked"].lower()
                where_string += " and studio_select.%%too_few_crew%%(\"%s\", %s, %s, %s)"% \
                                    (staffing_code, reduced, startTime, endTime)
        if values["deadhead"] != "*":
            # Any deadhead in roster that touches period and with from or to station.
            if values["dest_station"].find(",") == -1 and \
                            values["dest_station"].find("+") == -1:
                where_string += selectAndOrStatements("deadhead1",values["dep_station"],
                                            startTime, endTime, values["dest_station"])
            elif values["dep_station"].find(",") == -1 and \
                            values["dep_station"].find("+") == -1:
                where_string += selectAndOrStatements("deadhead2",values["dest_station"],
                                            startTime, endTime, values["dep_station"])
            else:
                where_string += " and false"

        else:
            #deadhead is "*".
            # Any flight in roster that touches period and with from or to station.
            if values["dep_station"] != "*" or values["dest_station"] != "*":
                if values["dest_station"].find(",") == -1 and \
                                values["dest_station"].find("+") == -1:
                    where_string += selectAndOrStatements("flight1",values["dep_station"],
                                                startTime, endTime, values["dest_station"])
                elif values["dep_station"].find(",") == -1 and \
                                values["dep_station"].find("+") == -1:
                    where_string += selectAndOrStatements("flight2",values["dest_station"],
                                                startTime, endTime, values["dep_station"])
                else:
                    where_string += " and false"
        if values["location"] != "*":
            # Any gap in roster for leg in period and with 'Locate' string for station (location/airport)
            where_string += selectAndOrStatements("location",values["location"],
                                        startTime, endTime)
        act_codes = values["activity_code"]
        informed_blank_days = False
        if act_codes != "*":
            # Any leg that touches period and with matching activity code.
            # The field contains a comma-separated list of items.
            # If an item is a valid activityCodesDict key, 
            #   it is expanded to the corresponding item list.
            # Each item in the resulting list may have:
            # - a trailing "*", which serves as a wildcard.
            # - a leading "!", which means that matching activities are excluded 
            act_list = []
            for ac in re.split(r"\s*[,+]+\s*", act_codes):
                act_list += activityCodesDict.get(ac, [ac])
            act_codes = ",".join(act_list).replace(" ","")
            where_string += ' and (studio_select.%%activity_code%%' \
                            '("%s", %s, %s))' % (act_codes, startTime, endTime)

            # Searching for informed blank days:
            # If any of the specified activity codes starts with "BL", then
            # the selection shall include informed blank days.
            # The logic here doesn't cover all aspects of mixing activity
            # inclusion and exclusion, but it's good enough. For example:
            # - "!BL" will NOT exclude informed blank days.
            # - "BL*,!BL7" will NOT exclude informed BL7-days.
            for ac in act_list:
                if ac.startswith("BL"):
                    informed_blank_days = True
                    break
            if informed_blank_days and (application.isTracking or application.isDayOfOps): #Only CCT uses published period lookup
                where_string = where_string[:-1] \
                             + ' or studio_select.%%has_informed_blank_day_in_period%%(%s, %s))' \
                             % (startTime, endTime)

        if values["working_days"] != "*":
            # Number of touch days in trip starting at date.
            where_string += selectAndOrStatements("working_days",values["working_days"],
                                        startTime, endTime)

        if debugOutput:
            where_list = []
            where_list = where_string.split("studio_select.")
            print '----------------------------------------------------------------------'
            print "MiniFilter: " +  "where string: \n" + where_string
            for element in where_list:
                print element

        sort_strings = ('studio_select.%%planning_group_at_date%%(%s)' % startTime,
                        'default(crew.%%civicstation_at_date%%(%s),"{")' % startTime,
                        'crew_pos.%%func2pos%%(crew.%%rank_at_date%%(%s))' % startTime,
                        'studio_select.%%sort_mini_selection%%(%s)' % ','.join((
                                '"%s"'  % values["above_or_below_rank"],
                                '"%s"'  % values["deadhead"],
                                '"%s"'  % values["dep_station"],
                                '"%s"'  % values["dest_station"],
                                '"%s"'  % values["location"],
                                '"%s"'  % act_codes,
                                '"%s"'  % staffing_code,
                                '%s,%s' % (startTime, endTime))),
                        )

        if debugOutput:
            sort_string = "MiniFilter: sort_strings: \n"
            for s in sort_strings:
                sort_string += s + ", "
            print sort_string
            print '----------------------------------------------------------------------'

        context = "sp_crew"
        if values["select_method"] == "SUBFILTER":
            context = carmstd.rave.Context("window", area)

        fields = {"id": "crew.%id%", "emp": "crew.%employee_number%"}
        crewIter = RaveIterator(RaveIterator.iter("iterators.roster_set",
                                                    where=where_string,
                                                    sort_by=sort_strings),
                                                    fields)
        StdArea.promptPush("Evaluating matching rosters...")
        rosters = crewIter.eval(context)
        StdArea.promptPush("Evaluating matching rosters... done.")

        if debugOutput:
            stri = "Matching rosters: "
            for roster in rosters:
                stri = stri + str(roster.id) + " (" + str(roster.emp) + ") "
            print "MiniFilter: " +  stri
            print "MiniFilter: Number of matching rosters: " + str(len(rosters))

        displayListOfCrew([roster.id for roster in rosters], values["select_method"], area, startTime, endTime)

def selectAndOrStatements(fieldOption, valuesList, startTime, endTime, additionalValues=[]):

    # 'valueList' field accepts both comma and plus-separated
    # lists of options. comma means OR, plus means AND.

    where_string = " and ("
    or_strings = valuesList.split(",")
    outerfirst = True
    for or_string in or_strings:
        if not outerfirst: where_string += " or "
        else: outerfirst = False
        and_strings = or_string.split("+")
        innerfirst = True
        for new_string in and_strings:
            if not innerfirst: where_string += " and "
            else: innerfirst = False
            # Quialification selects: "???_qual"
            if fieldOption[-5:] == "_qual":
                if len(additionalValues) == 1:
                    complementValues = additionalValues[0]
                elif len(additionalValues) == 0:
                    complementValues = mini_select_form.crewQualInfo.getCrewQualTypesForSubType(new_string)
                else:
                    complementValues = additionalValues
                where_string += "studio_select.%%qln_at_time%%(\"%s\", \"%s\", %s, %s)" % \
                            (complementValues, new_string, startTime, startTime)
            # Civic Station selects
            elif fieldOption == "civic_station":
                where_string += "studio_select.%%civicstation_at_time%%(%s, \"%s\")" % \
                            (startTime, new_string)
            # Rank selects
            elif fieldOption == "rank":
                where_string += "studio_select.%%rank_at_time%%(%s, \"%s\")" % \
                            (startTime, new_string)
            # Planning Group selects
            elif fieldOption == "planning_group":
                where_string += "studio_select.%%planning_group_at_time%%(%s, \"%s\")" % \
                            (startTime, new_string)
            # Deadhead selects
            elif fieldOption == "deadhead1":
                where_string += "studio_select.%%deadhead%%(\"%s\", \"%s\", %s, %s)" % \
                        (new_string, additionalValues, startTime, endTime)
            elif fieldOption == "deadhead2":
                where_string += "studio_select.%%deadhead%%(\"%s\", \"%s\", %s, %s)" % \
                        (additionalValues, new_string, startTime, endTime)
            # Deadhead selects and deadhead is "*"
            elif fieldOption == "flight1":
                where_string += "studio_select.%%flight%%(\"%s\", \"%s\", %s, %s)" % \
                        (new_string, additionalValues, startTime, endTime)
            elif fieldOption == "flight2":
                where_string += "studio_select.%%flight%%(\"%s\", \"%s\", %s, %s)" % \
                        (additionalValues, new_string, startTime, endTime)
            # Gap (location) selects
            elif fieldOption == "location":
                where_string += "studio_select.%%location%%(\"%s\", %s, %s)" % \
                        (new_string, startTime, endTime)
            # Activity selects
            elif fieldOption == "activity_code":
                where_string += "studio_select.%%activity_code%%(\"%s\", %s, %s)" % \
                        (new_string, startTime, endTime)
            # Working days selects
            elif fieldOption == "working_days":
                where_string += "studio_select.%%working_days_no_rounding%%(\"%s\", %s, %s)" % \
                        (new_string, startTime, endTime)

    where_string += ")"
    return where_string
