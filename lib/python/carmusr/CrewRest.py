

__version__ = "$Revision$"
"""
CrewRest
Module for doing:
# Purpose: Creates temporary tables to store crew rest data in.
@date:21Aug2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import Cui
import modelserver as M
import StartTableEditor
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import Errlog
import carmusr.HelperFunctions as HF
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as R
import utils.Names as Names
#import CrewNotificationFunctions as CNF
import Gui
import copy
import utils.wave
import carmusr.Attributes as Attributes

class CrewRest:
    # The class that contains temporary tables to connect Rave, DB and the XML-forms.
    
    def __init__(self):

        self.tm = M.TableManager.instance()
        
        # These variables are properties of the class
        self.raveValues = {}
        self.airportRef = None
        self.flightRef = None
        self.lockedCrew = []
        self.crewIdList = []
        self.crewValues = None
        self.pilot_in_command = ""
        self.crewStartValues = {}
        self.crewStartIdList = []
        # Creates the structure of the temporary tables
        self.createTables()
        
    def createTables(self):
        try: 
            self.tm.createTable("tmp_cr_flight_info",
                [M.StringColumn("flight_descriptor", "Flight Descriptor")],
                [M.StringColumn("flight_no", "Flight No"),
                 M.TimeColumn("departure_time", "Departure Time"),
                 M.StringColumn("departure_station", "Departure Station"),
                 M.TimeColumn("arrival_time", "Arrival Time"),
                 M.StringColumn("arrival_station", "Arrival Station"),
                 M.RelTimeColumn("block_time", "Block Time Hours"),
                 M.StringColumn("ac_type", "AC Type"),
                 M.StringColumn("crew_bunks_fc", "Number of crew bunks FC"),
                 M.StringColumn("crew_bunks_cc", "Number of crew bunks CC"),
                 M.StringColumn("rest_class_cc", "Class of rest facilities for CC"),
                 M.RelTimeColumn("rest_start_cc", "Start of rest period after block-off"),
                 M.RelTimeColumn("rest_end_cc", "End of rest period before block-on"),
                 M.RelTimeColumn("rest_start_fc", "Start of rest period after block-off"),
                 M.RelTimeColumn("rest_end_fc", "End of rest period before block-on"),
                 M.StringColumn("ac_rc_fc", "Active and required crew FC"),
                 M.StringColumn("ac_rc_cc", "Active and required crew CC"),
                 M.StringColumn("activity_id", "Activity Id")])
        except:
            pass
        self.flightInfo = self.tm.table("tmp_cr_flight_info")
        
        try:
            # The "background_color" field is a property of the XML window. It must be set here since
            # there is no possibility to place logic in the XML window.
            self.tm.createTable("tmp_cr_form_info",
                [M.StringColumn("flight_descriptor", "Flight Descriptor"), ],
                [M.StringColumn("recalculate_message", "Recalculate Message"),
                 M.StringColumn("send_message", "Send Message"),
                 M.StringColumn("print_message", "Print Message"),
                 M.StringColumn("background_color", "Background Color"),
                 M.StringColumn("form_header", "Form header"),
                 M.RelTimeColumn("rest_period_start_fc", "Start limit for rest period (FC)"),
                 M.RelTimeColumn("rest_period_end_fc", "End limit for rest period (FC)"),
                 M.RelTimeColumn("rest_period_start_cc", "Start limit for rest period (CC)"),
                 M.RelTimeColumn("rest_period_end_cc", "End limit for rest period (CC)"),
                 M.BoolColumn("disable_fc", "Disable rest calculations for fc"),
                 M.BoolColumn("disable_cc", "Disable rest calculations for cc")])
        except:
            pass
        self.formInfo = self.tm.table("tmp_cr_form_info")
        
        try: 
            self.tm.createTable("tmp_cr_active_crew",
                [M.RefColumn("crew", "crew", "Crew Id")],
                [M.StringColumn("first_name", "First Name"),
                 M.StringColumn("last_name", "Last Name"),
                 M.StringColumn("rank", "Rank"),
                 M.StringColumn("main_func", "Main Func"),
                 M.RelTimeColumn("rest_start_rel", "Rest Start"),
                 M.RelTimeColumn("rest_end_rel", "Rest End"),
                 M.BoolColumn("lock_times", "Lock times"),
                 M.StringColumn('rest_time', "Rest time"),
                 M.StringColumn('fdp_act', "FDP Actual (* appended if >fdp_max)"),
                 M.StringColumn('fdp_max', "FDP Max"),
                 M.StringColumn('fdp_uc', "FDP UC"),
                 M.StringColumn('fdp_start', "FDP start. Exceptions regarded"),
                 M.IntColumn("sort_order", "Sort order"),
                 M.StringColumn("assigned_rank", "Assigned Rank")])

        except:
            pass
        self.activeCrew = self.tm.table("tmp_cr_active_crew")


    def loadDBTables(self):
        # Load the interesting tables from DB to the Table Manager.
        self.tm.loadTables(["crew", "crew_rest", "flight_leg", "airport",
                            "crew_notification", "notification_set"])
        self.crew = self.tm.table("crew")
        self.crewRest = self.tm.table("crew_rest")
        self.flightLeg = self.tm.table("flight_leg")
        self.airport = self.tm.table("airport")
        self.crewNotification = self.tm.table("crew_notification")
        self.notificationSet = self.tm.table("notification_set")

    def addFlightInfo(self, departureStation, arrivalStation, acType,):
        # Adds the flight info to the table tmp_cr_flight_info.
        # This table is used to allow the form to present flight specific info.
        self.flightInfo.removeAll()
        record = self.flightInfo.create((self.raveValues["flightDescriptor"],))
        record.flight_no = self.raveValues["flightNo"]
        record.departure_time = self.raveValues["departureTime"]
        record.departure_station = departureStation
        record.arrival_time = self.raveValues["arrivalTime"]
        record.arrival_station = arrivalStation
        record.block_time = self.raveValues["blockTime"]
        record.ac_type = acType
        record.crew_bunks_fc = str(self.raveValues["crewBunksFC"])
        record.crew_bunks_cc = str(self.raveValues["crewBunksCC"])
        record.rest_class_cc = str(self.raveValues["crewRestClassCC"])
        record.ac_rc_fc = "%s/%s" % (self.AlgV["AC"]["F"], self.AlgV["RC"]["F"])
        record.ac_rc_cc = "%s/%s" % (self.AlgV["AC"]["C"], self.AlgV["RC"]["C"])
        record.activity_id = self.raveValues["activityId"]
        record.rest_start_cc = self.raveValues["ccRestStart"]
        record.rest_end_cc = self.raveValues["ccRestEnd"]
        record.rest_start_fc = self.raveValues["fcRestStart"]
        record.rest_end_fc = self.raveValues["fcRestEnd"]
        
    def addFormInfo(self, formHeader):
        # Adds the form info to the table tmp_cr_form_info. This table
        # allows interaction between the form and the python script.
        self.formInfo.removeAll()
        record = self.formInfo.create((self.raveValues["flightDescriptor"],))
        record.form_header = formHeader
        record.rest_period_start_fc = self.raveValues["fcRestStart"]
        record.rest_period_end_fc = self.raveValues["fcRestEnd"]
        # Read from rest_on_board_cc table
        record.disable_fc = False
        record.disable_cc = False
        
        record.rest_period_start_cc = self.getStartTimeWithDefault(self.raveValues["ccRestStart"])
        record.rest_period_end_cc = self.getStartTimeWithDefault(self.raveValues["ccRestEnd"])
        
    def getStartTimeWithDefault(self, time):
        if time == None or time == RelTime(0):
            return RelTime("00:45")
        return time
                
    def collectCrew(self):
        """
        Collects the crew that flies active on the activity with activityId.
        """
        try:          
            crew_details = R.foreach(R.iter('iterators.leg_set',
                    where=('fundamental.%is_roster%',
                           'leg.%is_active_flight%',
                           'activity_id="%s"' % (self.raveValues["activityId"])),
                    sort_by='crew.%sort_key%'),
                "crew.%id%", # [1]
                'crew.%rank_trip_start%', # [2]
                'crew.%main_func_trip_start%', # [3]
                'report_crew_rest.%sched_rob%', # [4]
                'report_crew_rest.%fdp_actual%', # [5]
                'report_crew_rest.%fdp_max%', # [6]
                'report_crew_rest.%fdp_uc%', # [7]
                'crew_pos.%acting_commander%', # [8]
                'crew.%seniority%', # [9]
                'crew_pos.%assigned_function%', # [10]
                'crew_pos.%chief_of_cabin%', # [11]
                'report_crew_rest.%fdp_start_utc%', # [12]
             )
            equal_legs_expr = R.foreach(R.iter('equal_legs'), crew_details)
            try:
                # The fast way to collect crew.
                # This use Cui.CuiSetSelectionObject and set the default context
                #   to the leg where the rest planning form were started from.
                # This does not always work. When it fails, the collection is
                #   done by iterating over the roster context.
                Cui.CuiSetSelectionObject(Cui.gpc_info,
                                          self.raveValues["area"],
                                          Cui.LegMode,
                                          str(self.raveValues["key"]))
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
                                            self.raveValues["area"],
                                            'OBJECT')
                
                crewValues, = R.eval('default_context',
                   R.foreach(R.iter('iterators.leg_set',
                                    where='fundamental.%%is_roster%%'
                                          ' and leg.%%is_active_flight%%'
                                          ' and activity_id="%s"'
                                          % self.raveValues["activityId"]),
                             equal_legs_expr))
                crewValues = crewValues[0][1][0][1]
                Errlog.log("REST PLANNING: Crew collected using CuiSetSelectionObject.")
                
            except Exception, err:
                # Collection done in a slower way that doesn't seem to fail.
                leg_set = R.foreach(R.iter('iterators.leg_set',
                    where='fundamental.%%is_roster%%'
                          ' and leg.%%is_active_flight%%'
                          ' and activity_id="%s"'
                          % (self.raveValues["activityId"])), equal_legs_expr)
                crewValues, = R.eval('sp_crew',
                    R.foreach(R.iter('iterators.roster_set',
                              where='crew.%%id%% = "%s"' 
                                    % self.raveValues["crewId"]), leg_set))
                crewValues = crewValues[0][1][0][1][0][1]
                Errlog.log("REST PLANNING: Crew collected via roster iteration.")

            crewIdList = []
            crewRestDict = {}
            for crewData in crewValues:
                crewId = crewData[1]
                crewIdList.append(crewId)
                if crewData[8]:
                    self.pilot_in_command = crewId
                crewRestDict[crewId] = self.getAssignedRest(crewId)
                
            self.crewValues = crewValues
            self.crewIdList = crewIdList
            self.crewRestDict = crewRestDict
            return (1, "Crew collected.")

        except:
            import traceback
            traceback.print_exc()
            return (0, "Error when collecting crew.")

    def getAssignedRest(self, crewId):
        try:
            crewRestRow = self.crewRest[(self.crew[crewId], self.flightRef)]
        except M.EntityNotFoundError:
            return (None, None)
        st, en = crewRestRow.reststart, crewRestRow.restend 
        return ((st and st - self.raveValues["sobt"]) or None,
                (en and en - self.raveValues["sobt"]) or None)
            

    def cacheCrewValues(self):
        # Saves the values in self.crewValues and self.crewIdList
        # for future reference (ie cancel operation)
        self.crewStartValues = [copy.copy(i) for i in self.crewValues]
        self.crewStartIdList = [copy.copy(i) for i in self.crewIdList]
        self.crewStartRestDict = {}
        for c in self.crewRestDict.keys():
            self.crewStartRestDict[c] = (copy.copy(self.crewRestDict[c][0]),
                                         copy.copy(self.crewRestDict[c][1]))


    def restoreValuesFromCacheToDB(self):
        """
        Updates temp table with previously saved values.
        Then saves to DB.
        """
        self.crewValues = self.crewStartValues
        self.crewIdList = self.crewStartIdList
        self.crewRestDict = self.crewStartRestDict  
        self.updateActiveCrewTempTable()
        self.saveRestTimesDB()

        

    def updateActiveCrewTempTable(self):
        """
        Updates the table tmp_cr_active_crew with the values in self.crewValues
        """
        self.activeCrew.removeAll()
        for i, val in enumerate(self.crewValues):
            crewId = val[1]
            crewRow = self.crew[(crewId,)]
            record = self.activeCrew.create((crewRow,))
            record.first_name = crewRow.forenames
            record.last_name = crewRow.name
            record.rank = val[2]
            record.main_func = val[3]
            record.rest_time = "    %s" % val[4]
            record.fdp_act = "    %s%s" % (val[5], ((val[5] > val[6]) and '*') or '')
            record.fdp_max = "    %s" % val[6]
            record.fdp_uc = "    %s" % val[7]
            record.fdp_start = "    %s" % val[12]
            record.sort_order = i # Already correctly sorted. Save the order
            record.assigned_rank = val[10]
            if val[8] or val[11]:
                record.assigned_rank += " (C)" # assigned_commander/chief_of_cabin
            record.lock_times = (crewId in self.lockedCrew)
            record.rest_start_rel = self.crewRestDict[crewId][0]
            record.rest_end_rel = self.crewRestDict[crewId][1]
    
    def returnCrewIdInActiveCrew(self):
        # Returns the crew Id:s in the table tmp_cr_active_crew.
        crewIdActiveCrew = []
        for xmlRow in self.activeCrew:
            crewIdActiveCrew.append(xmlRow.crew.id)
        return crewIdActiveCrew
            

    def setAlgorithmValues(self):
        """
        Sets the algorithm specific values and constants in self.AlgV.
        This depends on that cabin/flight crew have main_func=C/F
        """
        self.F = "F"
        self.C = "C"
        blocktime = self.raveValues["blockTime"]
        
        for row in self.formInfo:
            rest_start_fc = row.rest_period_start_fc
            rest_start_cc = row.rest_period_start_cc
            rest_end_fc = blocktime - row.rest_period_end_fc
            rest_end_cc = blocktime - row.rest_period_end_cc
             
        if rest_start_fc < RelTime(0) or rest_end_fc < RelTime(0) \
        or rest_start_cc < RelTime(0) or rest_end_cc < RelTime(0):
            Errlog.log("REST PLANNING: Wrong input type. Rest start/end must be positive")
            self.setRecalculateMessage("Wrong start/end rest time(s)."
                                       " Only positive numbers allowed", True)
            return False
        
        if rest_start_fc > blocktime or rest_end_fc > blocktime \
        or rest_start_cc > blocktime or rest_end_cc > blocktime:
            self.setRecalculateMessage("Rest may only be planned for time"
                                       " between departure and arrival", True)
            return False
                
        self.AlgV = {
            "RestPeriodStart":      {self.F:rest_start_fc, self.C:rest_start_cc},
            "RestPeriodEnd":        {self.F:rest_end_fc, self.C:rest_end_cc},
            "minRestLength":        {self.F:self.raveValues["minRestFC"], self.C:self.raveValues["minRestCC"]},
           }
            
        self.AlgV["RC"] = {self.F: 2,
                           self.C: self.raveValues["cabinCrewNeed"]}

        self.AlgV["AC"] = {self.F: 0, self.C: 0}
        for row in self.activeCrew:
            if row.main_func in (self.F, self.C):
                self.AlgV["AC"][row.main_func] += 1

        for row in self.flightInfo:
            self.AlgV["NB"] = {self.F: int(row.crew_bunks_fc),
                               self.C: int(row.crew_bunks_cc)}
            break
        else:
            self.AlgV["NB"] = {self.F: int(self.raveValues["crewBunksFC"]),
                               self.C: int(self.raveValues["crewBunksCC"])}
        
        return True

    def checkLockedRestTimes(self):
        """
        Checks that the locked rest times are according to the requirements i.e.
        not to many overlaps, at least an hour rest,
        no rest start after the rest end etc.
        """
        Errlog.log("REST PLANNING: Start checking locked rest times.")
        lockedRestTimesList = {self.F:[], self.C:[]}
        remainingRestTimesList = {self.F:[], self.C:[]}
        interestingTimePoints = {self.F:[], self.C:[]}
        lockedCrew = []
        for xmlRow in self.activeCrew:
            if xmlRow.lock_times:
                msg = self.checkStartAndEnd(xmlRow.rest_start_rel,
                                            xmlRow.rest_end_rel,
                                            xmlRow.main_func) 

                if msg:
                    return (0, msg)
                    
                if xmlRow.rest_start_rel and xmlRow.rest_end_rel:
                    interestingTimePoints[xmlRow.main_func].append(xmlRow.rest_start_rel)
                    interestingTimePoints[xmlRow.main_func].append(xmlRow.rest_end_rel)
                lockedCrew.append(xmlRow.crew.id)
                lockedRestTimesList[xmlRow.main_func].append(xmlRow)
            else:
                remainingRestTimesList[xmlRow.main_func].append(xmlRow)

        # Compute the maximum overlap.
        maxCrewOverlap = {self.F:0, self.C:0}
        for mainFunc in [self.F, self.C]:
            for timePoint in interestingTimePoints[mainFunc]:
                crewOverlapThisTimePoint = 0
                for lockedRow in lockedRestTimesList[mainFunc]:
                    if lockedRow.rest_start_rel and lockedRow.rest_end_rel \
                    and lockedRow.rest_start_rel < timePoint \
                    and lockedRow.rest_end_rel >= timePoint \
                    and lockedRow.rest_start_rel != lockedRow.rest_end_rel:
                        crewOverlapThisTimePoint += 1

                    if crewOverlapThisTimePoint > maxCrewOverlap[mainFunc]:
                        maxCrewOverlap[mainFunc] = crewOverlapThisTimePoint

        # Checks that the maximum overlap is less than the number of crew bunks
        # and the number of crew possible to rest at the same time.
        for mainFunc in [self.F, self.C]:
            overlapLimitRequiredCrew = max(0, self.AlgV["AC"][mainFunc] - \
                                           self.AlgV["RC"][mainFunc])
            if maxCrewOverlap[mainFunc] > self.AlgV["NB"][mainFunc]:
                failString = "%s crew: Number of overlapping rest periods" % mainFunc + \
                             " is %s." % (str(maxCrewOverlap[mainFunc])) + \
                             " The number of bunks are %s." % str(self.AlgV["NB"][mainFunc])
                return (0, failString)
            elif maxCrewOverlap[mainFunc] > overlapLimitRequiredCrew:
                failString = "%s crew: Number of overlapping rest periods" % mainFunc + \
                             " is %s." % (str(maxCrewOverlap[mainFunc])) + \
                             " The max allowed number due to crew requirements is %s." \
                             % overlapLimitRequiredCrew
                return (0, failString)

        self.lockedRestTimesList = lockedRestTimesList
        self.remainingRestTimesList = remainingRestTimesList
        self.interestingTimePoints = interestingTimePoints
        self.lockedCrew = lockedCrew
        
        return (1, "All locked rest times are according to the requirements.")

    def checkStartAndEnd(self, start, end, main_func):
        """
        Checks rest start and rest end for a rest period.
        The requirements must be followed.
        """
        if not start and not end:
            return None # Ok with empty rest start and rest end on locked times.
            
        if not start:
            return "%s crew: Specify rest start when rest end is specified." % main_func
        if not end:
            return "%s crew: Specify rest end when rest start is specified." % main_func
        if start < RelTime(0) or start >= self.raveValues["blockTime"]:
            return "%s crew: Rest start must be during the flight time." % main_func
        if end < RelTime(0) or end >= self.raveValues["blockTime"]:
            return "%s crew: Rest end must be during the flight time." % main_func
        if end < start:
            return "%s crew: Rest end must be after rest start." % main_func
          
        if (start < self.AlgV["RestPeriodStart"][main_func]):
            return "%s crew: No rest the first %s after departure." \
                 % (main_func, self.AlgV["RestPeriodStart"][main_func])
        if end > self.AlgV["RestPeriodEnd"][main_func]:
            return "%s crew: No rest the last %s before arrival." \
                 % (main_func, self.AlgV["RestPeriodEnd"][main_func])

        if end - start < self.AlgV["minRestLength"][main_func]:
            return "%s crew: No rest shorter than %s is allowed." \
                 % (main_func, self.AlgV["minRestLength"][main_func])
                      
        return None # Rest start and rest end ok

    def computeRemainingRestTimes(self):
        """
        Computes the rest period for the crew not locked in the form.
        The remaining time is distributed fair between the remaining
        crew following the requirements. The idea is to represent
        crew bunks with arrays and pack them with the locked rest
        periods. After that, the maximum, fair distributed, rest
        period is evaluated and given to the remaining crew.
        """
        Errlog.log("REST PLANNING: Start computing rest times not locked.")
        computeMessage = {self.F:[], self.C:[]}
        isWarning = False
        
        # Initiate crew bunks represented by empty vectors.
        # The maximum number of crew bunks that can be used is min(NB, AC - RC)
        crewBunks = {self.F:[], self.C:[]}
        freeTimeInCrewBunks = {self.F:[], self.C:[]}

        # Make sure only to recalculate rest times for those crew categories
        # that are not disabled.
        
        categories = [self.F, self.C]
        for row in self.formInfo:
            if row.disable_fc == True:
                categories.remove(self.F)
            if row.disable_cc == True:
                categories.remove(self.C)
            
        for mainFunc in categories:
            Errlog.log("REST PLANNING: Considering %s crew." % mainFunc)
            crewBunks[mainFunc] = {}
            restPossible = True
            maxCrewBunks = min(self.AlgV["NB"][mainFunc],
                               self.AlgV["AC"][mainFunc] - self.AlgV["RC"][mainFunc])
            if maxCrewBunks <= 0:
                message = "%s crew: %s active, %s required," \
                          % (mainFunc, self.AlgV["AC"][mainFunc], self.AlgV["RC"][mainFunc]) + \
                          " %s crew bunks, no rest is possible." % self.AlgV["NB"][mainFunc]
                computeMessage[mainFunc].append(message)
                isWarning = True
                restPossible = False
                Errlog.log("REST PLANNING: " + message)
                # No rest possible. Reset all rest times for the mainFunc-crew.
                for lockedRestTime in self.lockedRestTimesList[mainFunc]:
                    lockedRestTime.rest_start_rel = None
                    lockedRestTime.rest_end_rel = None
                for remainingRestTime in self.remainingRestTimesList[mainFunc]:
                    remainingRestTime.rest_start_rel = None
                    remainingRestTime.rest_end_rel = None

            crewBunks[mainFunc] = \
                dict([str(i + 1), []] for i in range(maxCrewBunks))

            # Start pack locked rest times in the crew bunks
            lockedRestTime = RelTime(0)
            index = 0
            while restPossible \
              and index < len(self.interestingTimePoints[mainFunc]):
                start = self.interestingTimePoints[mainFunc][index]
                end = self.interestingTimePoints[mainFunc][index + 1]
                j = 0
                periodPacked = False
                while j < len(crewBunks[mainFunc]) and not periodPacked:
                    j += 1
                    bunk = crewBunks[mainFunc][str(j)]
                    periodFitsInBunk = self.periodFitsInBunk(start, end, bunk)
                    if periodFitsInBunk:
                        bunk.append(start)
                        bunk.append(end)
                        periodPacked = True
                        lockedRestTime = lockedRestTime + (end - start)
                index += 2

            freeTimeLeft = ((self.AlgV["RestPeriodEnd"][mainFunc]
                             - self.AlgV["RestPeriodStart"][mainFunc]
                            ) * len(crewBunks[mainFunc])) - lockedRestTime
                
            # The times stored in the bunks are sorted to make it more easy to
            # calculate free time available to the rest of the crew.
            bunkIndex = 0
            while bunkIndex < len(crewBunks[mainFunc]):
                bunkIndex += 1
                crewBunks[mainFunc][str(bunkIndex)].sort()

            # freeTimeInCrewBunks are arrays indicating the free time in each
            # bunk. These are studied when we compute the length of the rest
            # period for the remaining crew.
            freeTimeInCrewBunks[mainFunc] = {}
            freeTimeInCrewBunks[mainFunc] = \
                self.getFreeTimeInCrewBunks(crewBunks[mainFunc], mainFunc)
                    
            # Start finding maximum rest time for the remaining crew.
            remainingCrew = len(self.remainingRestTimesList[mainFunc])
                        
            if remainingCrew > 0 and restPossible:
                # First test if it is possible to fill with the minRestLength.
                fairDistributionPossible = self.fairDistributionPossible(
                    freeTimeInCrewBunks[mainFunc],
                    self.AlgV["minRestLength"][mainFunc],
                    remainingCrew)
                
                if not fairDistributionPossible:
                    message = "%s crew: Unlocked time not enough for fair" \
                              " distribution of %s rest (minimum)." \
                              % (mainFunc, self.AlgV["minRestLength"][mainFunc])
                    isWarning = True
                    computeMessage[mainFunc].append(message)
                    Errlog.log("REST PLANNING: " + message)

                    # Reset the remaining rest periods.
                    i = 0
                    while i < len(self.remainingRestTimesList[mainFunc]):
                        self.remainingRestTimesList[mainFunc][i].rest_start_rel = None
                        self.remainingRestTimesList[mainFunc][i].rest_end_rel = None
                        i += 1

                else:
                    # Find the longest rest period possible with a fair 
                    # distribution between the remaining crew.
                    periodResolution = RelTime(1)
                    periodLength = self.AlgV["minRestLength"][mainFunc] 
                    while fairDistributionPossible:
                        periodLength += periodResolution 
                        fairDistributionPossible = self.fairDistributionPossible(
                            freeTimeInCrewBunks[mainFunc], periodLength, remainingCrew)

                    # periodLength is the longest rest period we can give to the
                    # remaining crew in a fair way.
                    # This is not computed exactly correct, but this is not needed.
                    periodLength = periodLength - periodResolution

                    # Start pack the crew bunks with the rest periods of the remaining crew.
                    remainingCrewIndex = 0
                    while remainingCrewIndex < remainingCrew:
                        j = 0
                        periodPacked = False
                        while j < len(crewBunks[mainFunc]) and not periodPacked:
                            j += 1
                            bunk = crewBunks[mainFunc][str(j)]

                            if len(bunk) < 2 or \
                                   self.periodFitsInBunk(self.AlgV["RestPeriodStart"][mainFunc], \
                                                         self.AlgV["RestPeriodStart"][mainFunc] + periodLength, \
                                                         bunk): # Empty bunk or fits before the first locked period.
                                bunk.append(self.AlgV["RestPeriodStart"][mainFunc])
                                bunk.append(self.AlgV["RestPeriodStart"][mainFunc] + periodLength)
                                self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_start_rel = \
                                        self.AlgV["RestPeriodStart"][mainFunc]
                                self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_end_rel = \
                                        self.AlgV["RestPeriodStart"][mainFunc] + periodLength
                                periodPacked = True
                            elif self.periodFitsInBunk(self.AlgV["RestPeriodEnd"][mainFunc] - periodLength, \
                                                       self.AlgV["RestPeriodEnd"][mainFunc], \
                                                       bunk): # Possible to pack the period in the end of the bunk.
                                bunk.append(self.AlgV["RestPeriodEnd"][mainFunc] - periodLength)
                                bunk.append(self.AlgV["RestPeriodEnd"][mainFunc])
                                self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_start_rel = \
                                        self.AlgV["RestPeriodEnd"][mainFunc] - periodLength
                                self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_end_rel = \
                                        self.AlgV["RestPeriodEnd"][mainFunc]
                                periodPacked = True
                            else:
                                i = 0
                                while i < len(bunk) and not periodPacked:
                                    start = bunk[i] - periodLength
                                    end = bunk[i]
                                    if start >= self.AlgV["RestPeriodStart"][mainFunc] and \
                                           end <= self.AlgV["RestPeriodEnd"][mainFunc] and \
                                           self.periodFitsInBunk(start, end, bunk):
                                        bunk.append(start)
                                        bunk.append(end)
                                        self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_start_rel = start
                                        self.remainingRestTimesList[mainFunc][remainingCrewIndex].rest_end_rel = end
                                        periodPacked = True
                                    i += 2

                        remainingCrewIndex += 1

                    Errlog.log("REST PLANNING: %s crew. Locked rest time is %s on %s crew." \
                               % (mainFunc, lockedRestTime, len(self.lockedRestTimesList[mainFunc])) + \
                               " %s remaining crew with rest period of %s." \
                               % (remainingCrew, periodLength))
                    
            else:
                Errlog.log("REST PLANNING: No remaining %s crew to compute rest periods for." % mainFunc)

                message = "No remaining %s crew to compute rest periods for." % mainFunc
                computeMessage[mainFunc].append(message)

            # Add an empty string to the arrays of status messages.
            # The empty string is prompted when no info to the user is needed.
            computeMessage[mainFunc].append("")

        return [computeMessage, isWarning]
        
    def periodFitsInBunk(self, start, end, bunk):
        # Checks if a period specified by start and stop fits in bunk.
        # bunk is an array consisting of start and stop times for
        # rest periods already packed.
        i = 0
        while i < len(bunk):
            if start < bunk[i + 1] and end > bunk[i]:
                return False
            i += 2
        return True

    def getFreeTimeInCrewBunks(self, crewBunks, mainFunc):
        # Returns arrays representing crew bunks but instead of start and
        # stop times for rest periods, these arrays contain the free time
        # available in the bunks.
        print "crewBunks", mainFunc
        for k, v in sorted(crewBunks.items()):
            print "  ", k, v
        print "restPeriod", self.AlgV["RestPeriodStart"][mainFunc], self.AlgV["RestPeriodEnd"][mainFunc]
        i = 0
        freeTimeInCrewBunks = {}
        while i < len(crewBunks):
            i += 1
            freeTimeInCrewBunks[str(i)] = []
            bunk = crewBunks[str(i)]
            if len(bunk) <= 1: # No rest period in bunk
                freeTimeInCrewBunks[str(i)].append(
                        self.AlgV["RestPeriodEnd"][mainFunc]
                        - self.AlgV["RestPeriodStart"][mainFunc])
            else:
                j = 2
                freeTimeInCrewBunks[str(i)].append(
                        bunk[0] - self.AlgV["RestPeriodStart"][mainFunc])
                while j < len(crewBunks[str(i)]):
                    freeTimeInCrewBunks[str(i)].append(bunk[j] - bunk[j - 1])
                    j += 2
                freeTimeInCrewBunks[str(i)].append(
                        self.AlgV["RestPeriodEnd"][mainFunc] - bunk[-1])
        print "freeTimeInCrewBunks", mainFunc
        for k, v in sorted(freeTimeInCrewBunks.items()):
            print "  ", k, v
        return freeTimeInCrewBunks

    def fairDistributionPossible(self, freeTimeInCrewBunks, periodLength, remainingCrew):
        # Checks if it is possible to do a fair distribution of rest periods with length
        # periodLength to the remainig crew. Input is the free time left, the period
        # length and the number of remaining crew.
        possibleCrew = 0
        i = 0
        while i < len(freeTimeInCrewBunks):
            i += 1
            for x in freeTimeInCrewBunks[str(i)]:
                possibleCrew += int(x / periodLength)
        return possibleCrew >= remainingCrew

    def saveRestTimesDB(self):
        # Save the entries in the XML form. 
        Errlog.log("REST PLANNING: Start saving rest times.")
        modified = False
        for crewId in self.crewIdList:
            crewIdRef = self.crew.getOrCreateRef((crewId))
            xmlRow = self.activeCrew[(crewIdRef,)]
            try:
                dbRow = self.crewRest[(crewIdRef, self.flightRef)]
                if not xmlRow.rest_start_rel or not xmlRow.rest_end_rel:
                    dbRow.remove()
                    modified = True
                else:
                    reststart = self.raveValues["sobt"] + xmlRow.rest_start_rel
                    restend = self.raveValues["sobt"] + xmlRow.rest_end_rel
                    if reststart != dbRow.reststart:
                        dbRow.reststart = reststart
                        modified = True
                    if restend != dbRow.restend:
                        dbRow.restend = restend
                        modified = True
            except:
                # Only create entries with non void rest times in crew rest.
                if xmlRow.rest_start_rel and xmlRow.rest_end_rel:
                    dbRow = self.crewRest.create((crewIdRef, self.flightRef))
                    dbRow.reststart = self.raveValues["sobt"] + xmlRow.rest_start_rel
                    dbRow.restend = self.raveValues["sobt"] + xmlRow.rest_end_rel
                    modified = True
            self.crewRestDict[crewId] = (
                xmlRow.rest_start_rel, xmlRow.rest_end_rel)

        if modified:
            Errlog.log("REST PLANNING: Rest times saved.")
            Cui.CuiReloadTable("crew_rest", 1)
            HF.redrawAllAreas(Cui.CrewMode)
        else:
            Errlog.log("REST PLANNING: Nothing to save.")

    def saveRestPeriod(self):
        # Save the allowed rest period from the XML form.
        Errlog.log("REST PLANNING: Start saving rest period")

    def removeFalseDBEntries(self):
        # Removes false entries from the DB. In the case:
        # Rest Planning -> Change assignments -> Rest Planning the DB is
        # to contain false entries from the first Rest Planning. These are
        # removed.
        Errlog.log("REST PLANNING: Checks for false rest planning entries in DB.")
        counter = 0 
        for row in self.crewRest.search("(flight=%s)" % self.flightRef):
            if row.crew.id not in self.crewIdList:
                row.remove()
                counter += 1
        Errlog.log("REST PLANNING: %s old entries from flight %s removed." \
                   % (counter, self.flightRef))

    def removeDBEntriesForFlight(self):
        # Removes all DB entries for the flight of interest. This is done when assignment
        # changes in the plan makes a rest plan illegal.
        Errlog.log("REST PLANNING: Removing all entries for flight %s." % self.flightRef)
        for row in self.crewRest.search("(flight=%s)" % self.flightRef):
           row.remove()
           
    def removeAllEntriesInActiveCrew(self):
        # Function to remove all table entries. This is done to prevent a
        # user from planning rest i several forms.
        self.activeCrew.removeAll()

    def checkForConsistencyAfterPlanChanges(self):
        # This function checks the active and required number of crew on the flight. If
        # changes are made in the plan that makes rest impossible, the DB entries are
        # removed and the crew info updated.
        Errlog.log("REST PLANNING: Checks if previous rest periods are legal after changes to the plan.")
        self.removeFalseDBEntries()
        totalResetIsNeeded = 0
        for mainFunc in [self.F, self.C]:
            if self.AlgV["RC"][mainFunc] >= self.AlgV["AC"][mainFunc]:
                for row in self.activeCrew:
                    if row.main_func == mainFunc:
                        crewId = row.crew.id
                        crewIdRef = row.crew
                        try:
                            crewRestRow = self.crewRest[(crewIdRef, self.flightRef)]
                            crewRestRow.remove()
                            totalResetIsNeeded = 1
                        except:
                            pass

        if not totalResetIsNeeded:
            Errlog.log("REST PLANNING: Manually locking existing rest times and checks them.")
            for row in self.activeCrew:
                row.lock_times = True
            checkVektor = crewRestTables.checkLockedRestTimes()
            totalResetIsNeeded = not checkVektor[0]
        
        msg = ""
        if totalResetIsNeeded:
            Errlog.log("REST PLANNING: Illegal rest periods due to flight or assignment changes in the plan.")
            #self.removeDBEntriesForFlight()
            msg = "Flight or assignment changed. Rest planning should redone."
            
        Cui.CuiReloadTable("crew_rest", 1)
        HF.redrawAllAreas(Cui.CrewMode)
        if totalResetIsNeeded:
            self.collectCrew()
            self.updateActiveCrewTempTable()
        else:
            for row in self.activeCrew:
                row.lock_times = False
            Errlog.log("REST PLANNING: No illegal rest periods found.")               
            
        return msg
       
    def setRecalculateMessage(self, recalculateMessage, isWarning):
        # Sets the message prompted in the XML form.
        Errlog.log("REST PLANNING: Set the Recalculate message.")
        for row in self.formInfo:
            row.recalculate_message = recalculateMessage
            if isWarning:
                row.background_color = "red"
            else:
                row.background_color = "transparent"


    def setSendMessage(self, sendMessage, isWarning):
        #Sets the message prompted in the XML form.
        Errlog.log("REST PLANNING: Set the Send message.")
        for row in self.formInfo:
            row.send_message = sendMessage
        if isWarning:
            row.background_color = "red"
        else:
            row.background_color = "transparent"

            
    def setPrintMessage(self, printMessage):
        #Sets the message prompted in the XML form.
        Errlog.log("REST PLANNING: Set the Print message.")
        for row in self.formInfo:
            row.print_message = printMessage
            row.background_color = "transparent"
            
    def saveCrewBunks(self):
        udor = self.raveValues['legUdor']
        fd = self.raveValues['flightDescriptor']
        adep = self.raveValues['departureStation']
        for row in self.flightInfo:
            crewBunksFC = {'int':int(row.crew_bunks_fc)}
            crewBunksCC = {'int':int(row.crew_bunks_cc)}
            break
        # check if attribute has changed!
        if crewBunksFC['int'] != int(self.raveValues["crewBunksFC"]):
            attr_fc = self.raveValues["attr_name_fc"]
            Errlog.log('REST PLANNING: Saving Crew Bunks FC:%s' % crewBunksFC['int'])
            Attributes.SetFlightLegAttr(udor, fd, adep, attr_fc, refresh=True, **crewBunksFC)
            
        if crewBunksCC['int'] != int(self.raveValues["crewBunksCC"]):
            rest_class_cc = self.raveValues["crewRestClassCC"]
            if rest_class_cc == 1:
                attr_cc = self.raveValues["attr_name_cc_1"]
            if rest_class_cc == 2:
                attr_cc = self.raveValues["attr_name_cc_2"]
            if rest_class_cc == 3:
                attr_cc = self.raveValues["attr_name_cc_3"]
            Errlog.log('REST PLANNING: Saving Crew Bunks CC:%s' % crewBunksCC['int'])
            Attributes.SetFlightLegAttr(udor, fd, adep, attr_cc, refresh=True, **crewBunksCC)
            
        
crewRestTables = None

def recalculateRestTimes(plan, activity_id):
    """
    The function you run from the XML form. It checks the locked rest periods,
    computes rest periods for the remaining crew, saves to DB, removes false
    DB entries, update the variables calculated via Rave.
    """
    global crewRestTables
    isWarning = True
    Cui.CuiExecuteFunction("CuiNop(0)", "Crew_rest_recalculate", 3, 2)
    collectResult = crewRestTables.collectCrew()
    if not collectResult[0]:
        recalculateMessage = \
          "Error when collecting crew. Possibly because of assignment changes." \
          " No rest changes applied. Please restart the Rest Planning form."
        Errlog.log("REST PLANNING: " + recalculateMessage)
    else:
        crewIdInActiveCrew = crewRestTables.returnCrewIdInActiveCrew()
        crewIdInActiveCrew.sort()
        crewRestTables.crewIdList.sort()
        crewRestTables.saveRestPeriod()
        
        # Attempt to set the algorithm values according to the xml form.If there is some error in the
        # form the function below will handle the resulting outputs.
        if not crewRestTables.setAlgorithmValues():
            return
    
        if not (activity_id == crewRestTables.raveValues["activityId"]):
            recalculateMessage = \
              "You can not do rest planning in multiple forms." \
              " Please close all forms and run one instance of Rest Planning."
            Errlog.log("REST PLANNING: " + recalculateMessage)
            crewRestTables.removeAllEntriesInActiveCrew()
    
        elif crewIdInActiveCrew == crewRestTables.crewIdList:
            checkVektor = crewRestTables.checkLockedRestTimes()
            lockedRestTimesCorrect = checkVektor[0]
            if lockedRestTimesCorrect:
                Errlog.log("REST PLANNING: " + checkVektor[1])
                [computeMessage, isWarning] = crewRestTables.computeRemainingRestTimes()
                crewRestTables.saveRestTimesDB()
                crewRestTables.removeFalseDBEntries()
                crewRestTables.collectCrew()
                crewRestTables.updateActiveCrewTempTable()
                recalculateMessage = ""
                for message in computeMessage:
                    try:
                        recalculateMessage = recalculateMessage + computeMessage[message][0] + " "
                    except IndexError:
                        pass
                Errlog.log("REST PLANNING: Recalculation successful.")
            
            else:
                recalculateMessage = checkVektor[1]
                Errlog.log("REST PLANNING: " + recalculateMessage)
 
        else:
            recalculateMessage = \
              "Assignment changes made in the plan. No rest changes applied." \
              " Please restart the Rest Planning form."
            Errlog.log("REST PLANNING: " + recalculateMessage)

    crewRestTables.setRecalculateMessage(recalculateMessage, isWarning)

    
def generateReport(planning_name):
    # This function is responsible for generating the crew rest report
    rpt = "CrewRestReport.py"
    # The flight descriptor should be used as an argument to the report.The argument may,
    # however not contain any spaces and thus it needs formating.
    ##The following two lines should be used as soon as it is possible to send an argument to the report.
    ##tempStr = crewRestTables.flightDescriptor.replace(" ", "_")
    ##tempStr = "FLIGHTDESCRIPTOR=" + tempStr
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiWhichArea, "Window", rpt, 0)
    message = "Printable report generated in new window"
    global crewRestTables
    crewRestTables.setPrintMessage(message)

def closeRestForm(planning_name):
    # When closing the Crew Rest window, this function will be executed.
    # Setting the crewRestTables to "None" allows us to open another CR window (see below)
    global crewRestTables
    Gui.GuiCallListener(Gui.ActionListener)
    crewRestTables = None

def cancelRestForm(planning_name):
    if crewRestTables:
        crewRestTables.restoreValuesFromCacheToDB()
    closeRestForm(planning_name)


def okRestForm(planning_name):
    global crewRestTables
    #In case planner has overridden the number of crew bunks (Cr145) / pergr
    crewRestTables.saveCrewBunks()
    closeRestForm(planning_name)


# Register functions to make it possible for the XML-form to call them. 
from utils.wave import LocalService, ModelChangeService, unicode_args_to_latin1 as u2l
class cr_recalculate_rest_times(ModelChangeService): func = u2l(recalculateRestTimes)
class cr_cancel_rest_form(ModelChangeService):       func = cancelRestForm
class cr_generate_report(LocalService):              func = generateReport
class cr_close_rest_form(LocalService):              func = closeRestForm
class cr_ok_rest_form(LocalService):                 func = okRestForm


crewRestTables = None

def startCrewRestForm(formName, cpsName=""):
    
    # Function that starts the Crew rest form.
    
    if cpsName == "":
        cpsName = formName
    Errlog.log("REST PLANNING: The Rest planning form is started")  
    StartTableEditor.StartTableEditor(['-f', '$CARMUSR/data/form/' + formName], cpsName)     

def raveEvaluation():
    # Used to get all necessary rave variables that are evaluated on "object".
    # This to prevent the object from changing before the evaluation.

    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    leg_id = Cui.CuiCrcEvalInt(Cui.gpc_info, area, "object", "leg_identifier")
    leg_object = HF.LegObject(str(leg_id), area)
    # {key:[rave lookup-variable', default-case]}
    dflt_time = AbsTime("01Jan1989")
    lookups = {'flightDescriptor':["leg.%flight_descriptor%", "Unknown"],
               'flightIsLongHaul':["leg.%is_long_haul%", False],
               'legUdor':['leg.%udor%', dflt_time],
               'attr_name_cc_1':['attributes.%crew_bunks_1_attr_cc%', "CCBUNKS_CLASS_1"],
               'attr_name_cc_2':['attributes.%crew_bunks_2_attr_cc%', "CCBUNKS_CLASS_2"],
               'attr_name_cc_3':['attributes.%crew_bunks_3_attr_cc%', "CCBUNKS_CLASS_3"],
               'attr_name_fc':['attributes.%crew_bunks_attr_fc%', "FCBUNKS_CLASS_1"],
               'activityId':["activity_id", "Unknown"],
               'sobt':['leg.%activity_scheduled_start_time_UTC%', dflt_time],
               "arrivalTime":["leg.%end_UTC%", dflt_time],
               "departureTime":["leg.%start_UTC%", dflt_time],
               "key":[leg_id, 0],
               "flightNo":["crg_basic.%flight_nr_string%", "Unknown"],
               "departureStation":["leg.%start_station%", "Unknown"],
               "arrivalStation":["leg.%end_station%", "Unknown"],
               "acType":["leg.%ac_type%", "Unknown"],
               "cabinCrewNeed":["report_crew_rest.%rob_on_duty%", 6],
               "crewBunksFC":["studio_process.%number_of_crew_bunks_FC%", 2],
               "crewBunksCC":["studio_process.%number_of_crew_bunks_CC%", 4],
               "crewRestClassCC":["leg.%rest_class_cc%", "None"],
               "ccRestStart":["report_crew_rest.%rest_on_board_start_ca%", RelTime(45)],
               "ccRestEnd":["report_crew_rest.%rest_on_board_end_ca%", RelTime(45)],
               "crewId":["crew.%id%", "Unknown"],
               "blockTime":['leg.%block_time%', RelTime(0)],
               "minRestCC":['report_crew_rest.%min_inflight_rest_cc%', RelTime(90)],
               "minRestFC":['report_crew_rest.%min_inflight_rest_fc%', RelTime(120)],
               "fcRestStart":["report_crew_rest.%inflight_rest_start_fc%", RelTime(45)],
               "fcRestEnd":["report_crew_rest.%inflight_rest_end_fc%", RelTime(45)]}
    result = {"area":area}
    for key, lookup in lookups.items():
        try:
            result[key] = leg_object.eval(lookup[0])[0]
        except:
            result[key] = lookup[1]

    return result

def startCrewRest():
    if not HF.isDBPlan():
        message = 'Crew Rest Form only available in database plan'
        cfhExtensions.show(message)
        Errlog.log('REST PLANNING: ' + message)
        return 1
    
    # The function that start the creation of the temporary tables.
    global crewRestTables
    
    if crewRestTables != None:
        # When opening a crew rest window, the crewRestTables is set to be an
        #   instance of the CrewRest class.
        # When closing the crew rest window, the crewRestTables is set to None
        Errlog.log("REST PLANNING: Only one Crew Rest window may be open.")
        cfhExtensions.show("Only one Crew Rest window may be open.")
        return 1
    
    try:
        
        raveValues = raveEvaluation()
        crewRestTables = CrewRest()
        crewRestTables.raveValues = raveValues

        try:
            currentTime, = R.eval("fundamental.%now%")
        except:
            currentTime = AbsTime("1Jan1986")

        print "RAVEVALS"
        for k, v in sorted(raveValues.items()):
            print " %s=%s (%s)" % (k, v, type(v))
        if raveValues["flightDescriptor"] == "Unknown" \
        or not raveValues["flightIsLongHaul"] \
        or raveValues["activityId"] == "Unknown" \
        or raveValues["blockTime"] < RelTime(4, 0):
            m = "Only applicable on long haul flights" \
                " with a block time exceeding 4 hours."
            Errlog.log("REST PLANNING: %s" % m)
            cfhExtensions.show(m)
            crewRestTables = None
            return 1
            
        if raveValues["arrivalTime"] < currentTime:
            cfhExtensions.show("Note: the selected flight has already arrived")
        elif raveValues["departureTime"] < currentTime:
            cfhExtensions.show("Note: the selected flight has already departed")
            
        formHeader = "Rest Planning, Flight %s %s." % (
                crewRestTables.raveValues["flightNo"],
                AbsDate(crewRestTables.raveValues["departureTime"]))

        Errlog.log("REST PLANNING: Collecting data and setting up the tables.")
        crewRestTables.loadDBTables()
        crewRestTables.airportRef = crewRestTables.airport.getOrCreateRef(
                (raveValues["departureStation"],))
        crewRestTables.flightRef = crewRestTables.flightLeg.getOrCreateRef(
                (crewRestTables.raveValues["legUdor"],
                 crewRestTables.raveValues["flightDescriptor"],
                 crewRestTables.airportRef))
        
        Cui.CuiExecuteFunction("CuiNop(0)", "Crew_rest_startup", 3, 2)
        collectResult = crewRestTables.collectCrew()
        if not collectResult[0]:
            m = "Error when collecting crew. Please restart Rest Planning form."
            Errlog.log("REST PLANNING: %s" % m)
            cfhExtensions.show(m)
            crewRestTables = None
            return 1
        
        msg = ""
        crewRestTables.updateActiveCrewTempTable()
        crewRestTables.cacheCrewValues()
        crewRestTables.addFormInfo(formHeader)
        crewRestTables.setAlgorithmValues()
        crewRestTables.addFlightInfo(raveValues["departureStation"],
                                     raveValues["arrivalStation"],
                                     raveValues["acType"])
        msg += " %s" % crewRestTables.checkForConsistencyAfterPlanChanges()
        
        msg = msg.strip() or None
        crewRestTables.setRecalculateMessage(msg, msg is not None)
        
        Errlog.log("REST PLANNING: Setup of tables completed.")
        startCrewRestForm("crew_rest.xml", cpsName=formHeader)

    except Exception as e:
        msg = "Something went wrong while loading up the Crew Rest dialog."
        Errlog.log(msg[0:14] + "horribly" + msg[15:] + " Attempting to clean up globally scoped variables.")
        cfhExtensions.show(msg)

        # Something went wrong while opening the CrewRest dialog, so we must reset crewRestTables,
        # so that it doesn't block re-opening the CrewRest dialog.
        crewRestTables = None

        import traceback
        traceback.print_exc()
        # Friends always re-raise friends exceptions.
        raise e

    # FYI: The crewRestTables variable is unset from the close function, when the CrewRest dia

    return 0


