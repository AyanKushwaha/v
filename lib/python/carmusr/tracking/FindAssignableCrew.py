#

#

import traceback
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
import carmensystems.rave.api as R
import carmstd.studio.area as StdArea
import Cui
import Cfh
from Localization import MSGR
import Etab
import Crs
import os
import gc
from time import time
from carmstd.carmexception import CarmException
import carmstd.cfhExtensions as Message
import tempfile
import carmusr.HelperFunctions as HF

debugOutput = 1

MAP_NOW_TIME = "fundamental.%now%"

# Iterators.
MAP_CHAIN_SET = 'iterators.chain_set'
MAP_TRIP_SET = 'iterators.trip_set'
MAP_LEG_SET = 'iterators.leg_set'

# Definitions on open chain (assignChain).
MAP_LEG_AC_TYPE = 'leg.%qual%'
MAP_LEG_REGION = 'leg.%region%'
MAP_LEG_START = 'leg.%start_utc%'
MAP_LEG_END = 'leg.%end_utc%'
MAP_DUTY_START = 'duty.%start_utc%'
MAP_DUTY_END = 'duty.%end_utc%'
MAP_LEG_START_STN = 'departure_airport_name'
MAP_LEG_END_STN = 'arrival_airport_name'
MAP_LEG_IS_ACTIVE = 'leg.%is_active_flight%'
MAP_LEG_IS_PACT = 'leg.%is_pact%'
MAP_TRIP_VOLUNTEER_TYPE = 'studio_fac.%trip_voluntary_type%'
MAP_TRIP_START = 'trip.%start_utc%'
MAP_TRIP_END = 'trip.%end_utc%'
MAP_TRIP_REGION = 'trip.%region%'
MAP_CREW_IS_LATE_FOR_TRIP = 'studio_fac.%crew_is_late%'
MAP_CNX_PROBLEM = 'studio_fac.%leg_cnx_problem%'
MAP_CREW_RANK = 'crew.%rank%'

#NOT IN SAS: (NOW IS):
MAP_CNX_TIME_BEFORE = 'studio_fac.%leg_cnx_time_before%'
MAP_CNX_TIME_AFTER = 'studio_fac.%leg_cnx_time_after%'

# Candidate criterias.
MAP_CANDIDATE_ALLOWED_RANK_FUNC = 'studio_fac.%crew_has_allowed_rank%'
MAP_CANDIDATE_AC_TYPE_FUNC = 'studio_fac.%crew_has_ac_qual%'
MAP_CANDIDATE_ALLOWED_REGION_FUNC = 'studio_fac.%crew_has_region%'
MAP_CANDIDATE_START_STN_FUNC = 'studio_fac.%roster_start_station_candidate%'
MAP_CANDIDATE_END_STN_FUNC = 'studio_fac.%roster_end_station_candidate%'
MAP_CANDIDATE_DAYS_OFF_FUNC = 'studio_fac.%roster_days_off_candidate%'
MAP_CANDIDATE_BLANK_DAYS_FUNC = 'studio_fac.%roster_blankday_and_informed_bl%'

#NOT IN SAS: (WILL NOT BE EITHER):
#MAP_CANDIDATE_REQUEST_DAYS_OFF_FUNC = 'fac.%roster_requested_days_off%'

MAP_CANDIDATE_VOLUNTEER_FUNC = 'studio_fac.%roster_volunteer_candidate%'
MAP_CANDIDATE_STANDBY_FUNC = 'studio_fac.%roster_standby_candidate%'

#NOT IN SAS:
MAP_CANDIDATE_GROUND_DUTY_FUNC = 'studio_fac.%roster_ground_duty_candidate%'
#DONE.
#MAP_CANDIDATE_CANCELLED_DUTY_FUNC = 'fac.%roster_cancelled_duty%'
MAP_CI_EARLIER_FUNC = 'studio_fac.%roster_ci_earlier%'
#DONE.
MAP_ARRIVE_BEFORE_FUNC = 'studio_fac.%roster_arrive_before%'
MAP_DEPART_AFTER_FUNC = 'studio_fac.%roster_depart_after%'

# Sort function.
MAP_CANDIDATE_SORT_FUNC = 'studio_fac.%roster_sort_default%'

#NOT IN SAS (NOW IS):
MAP_CANDIDATE_SORT_COST = 'studio_fac.%roster_sort_work_time%'
MAP_CANDIDATE_SBY_SORT_FUNC = 'studio_fac.%roster_sort_sby%'

# Relaxation critirias with this id, will always be relaxed.
MAP_RELAX_MANDATORY_ID = 'MANDATORY'
# If this is a substring to the relax id, it won't be shown in the form.
MAP_RELAX_HIDDEN_ID = 'HIDDEN'

TIME_IS_LOCAL = 'FALSE'
DEFAULT_REF_AIRPORT = 'CPH'

#Global dictionary that contains the rules in studio
_studioRulesDict = {}
_semi_legal_rules = []
_always_turned_off_rules = []
_form_dependent_turn_off_rules = []


# Map functions.
def pos2func(pos):
    return {1:"FC",2:"FP",3:"FR",4:"FU",5:"AP",6:"AS",7:"AH",
                    8:"AU",9:"TL",10:"TR"}.get(pos,"")

def func2cat(func):
    return {"FC":"F","FP":"F","FR":"F","FU":"F","AP":"C","AS":"C",
                "AH":"C","AU":"C","TL":"T","TR":"T"}.get(func,"")

#
# PROBLEM TYPE HANDLING
# ---------------------
#
# Class ProblemTypeHandler
# Container with all defined problem types.
#
# Class ProblemType
# Base class for a problem type definition.
#

class ProblemTypeHandler:

    """
    Container with all defined problem types.
    """

    def __init__(self,assHandler):
        self.candidates = assHandler.candidates
        self.assHandler = assHandler
        self.checkIn = CheckInProblem(self)
        self.cnx = ConnectionProblem(self)
        self.checkOutLatest = CheckOutOnTimeProblem(self)
        self.checkInEarliest = CheckInOnTimeProblem(self)
        self.coverLegs = CoverLegsProblem(self)
        self.swapLegs = SwapLegsProblem(self)
        self.types = [self.checkIn, self.cnx, self.checkOutLatest,
                      self.checkInEarliest, self.coverLegs, self.swapLegs]
        
        self.initProblemType()

    def getProblemList(self):
        probList = []
        for k in self.__dict__:
            if isinstance(self.__dict__[k],ProblemType):
                probList.append(self.__dict__[k])
        return probList 
        
    def getNameList(self):
        nameList = []
        for i in range(len(self.types)):
            nameList.append(self.types[i].name)
        return nameList

    def initProblemType(self):
        if self.assHandler.assignChainArea.mode == Cui.CrewMode:
            if self.assHandler.assignChain.crewIsLate:
                self.checkIn.isActive = True
            elif self.assHandler.assignChain.cnxProblem:
                self.cnx.isActive = True
            else: self.coverLegs.isActive = True #self.cnx.isActive = True
##            self.pushForward.isActive = True
        else: self.coverLegs.isActive = True

    def __str__(self):
        strOut = "\n...<--- *** PROBLEM TYPE HANDLER\n"
        for k in self.__dict__:
            if isinstance(self.__dict__[k], ProblemType):
                strOut += "...%s:\n%s\n" % (k, str(self.__dict__[k]))
        strOut += "...*** ---> PROBLEM TYPE HANDLER\n"
        return strOut

                    
class ProblemType:

    """
    Base class for a problem type definition.
    initCandidates() & initFlags() are common to all problem types.
    updateCandidates() & updateFlags() maybe redefined to setup
    candidate criterias and flags differently.
    """
    
    def __init__(self,problemHandler,name=""):
        self.candidates = problemHandler.candidates
        self.assFlags = problemHandler.assHandler.flags
        self.problemHandler = problemHandler
        self.name = name
        self.isActive = False

    def activate(self,value):
        self.isActive = value
        
    def writeToModel(self):
        self.initCandidates()
        self.updateCandidates()
        self.initFlags()
        self.updateFlags()
        if debugOutput:
            print "FindAssignableCrew.py::Updating model for problem: ", self.name

    def initCandidates(self):
        self.candidates.standby.period = self.candidates.defaultPeriod
        self.candidates.standby.isActive = True
        self.candidates.checkInEarlier.isActive = False
        self.candidates.daysOff.period = self.candidates.defaultPeriod
        self.candidates.volunteer.period = self.candidates.defaultPeriod
        self.candidates.blankDay.period =  self.candidates.defaultPeriod
        self.candidates.stations.start.period = self.candidates.defaultPeriod
        self.candidates.stations.endDefault.period = self.candidates.defaultPeriod
        self.candidates.stations.end = self.candidates.stations.endDefault
        self.candidates.stations.isAndCond = False
        self.candidates.stations.endIsActive = False
        
    def updateCandidates(self):
        pass

    def initFlags(self):        
        #self.assFlags.setAllowOpenTime(True)
        self.assFlags.setAllowOpenTimeAny()
        self.assFlags.swapOnOverlap = False
        self.assFlags.allowSwapOnly = False
        
        
    def updateFlags(self):
        pass

    def argUpdate(self):
        pass
        
    def getName(self):
        return self.name

    def getRelaxIds(self):
        pass
        #return ['Stand-by']

    def __str__(self):
        
        strOut = "\n......<--- PROBLEM TYPE\n"
        for k in self.__dict__:
            if not isinstance(self.__dict__[k],ProblemTypeHandler) \
                   and not isinstance(self.__dict__[k],AssignmentFlags) \
                   and not isinstance(self.__dict__[k],CandidateHandler):
                strOut += "......%s: %s\n" % (k, str(self.__dict__[k]))
        strOut += "......---> PROBLEM TYPE\n"
        return strOut


class CheckInProblem(ProblemType):

    """
    Crew is late for check-in.
    """

    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Solve check-in problem')

    def updateCandidates(self):
        self.candidates.blankDay.isActive = False #pass
        self.candidates.stations.startDefault.setCnxTol('0:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('2:00')


    def updateFlags(self):
        self.assFlags.setAllowOpenTime(True)
        self.assFlags.setAllowOpenTimeLater(True)
        self.assFlags.swapOnOverlap = True
        self.assFlags.allowSwapLater = True
        
    def getRelaxIds(self):
        pass
        
class ConnectionProblem(ProblemType):

    """
    Crew is late for cnx.
    """

    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Solve connection problem')
        #self.assFlags.setAllowOpenTimeLater(True)
        
    def updateCandidates(self):
        self.candidates.blankDay.isActive = True
        #self.candidates.checkInEarlier.isActive = True
        self.candidates.stations.startDefault.setCnxTol('2:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('0:00')
        

    def updateFlags(self):
        self.assFlags.setAllowOpenTime(True)
        self.assFlags.setAllowOpenTimeLater(True)
        self.assFlags.swapOnOverlap = True
        self.assFlags.allowSwapLater = True

class CheckOutOnTimeProblem(ProblemType):

    """
    Crew must check-out before a specific time.
    """
    
    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Find check-out latest')
        #self.assFlags.setAllowOpenTimeEarlier(True)
        
    def argUpdate(self,val):
        """
        Sets end time on end station to the value from input field.
        """
        # Convert chain end to local time. (It is assumed that input from form is local.)
        chainEndLc = timeConvert(self.problemHandler.assHandler.assignChain.end, 'local')
        chainEndDate = AbsTime(AbsDate(chainEndLc))
        chainEndTime = chainEndLc - AbsTime(AbsDate(chainEndLc))
        coEndTime = RelTime(str(val))
        if coEndTime > chainEndTime: coEnd = chainEndDate + coEndTime
        else: coEnd = chainEndDate + coEndTime
        self.candidates.stations.endBefore.t_max = timeConvert(coEnd, 'utc')

    def updateCandidates(self):
        #Find all crew that are at the departure station 
        self.candidates.stations.end = self.candidates.stations.endBefore
        self.candidates.stations.isAndCond = True
        self.candidates.stations.startIsActive = True
        self.candidates.stations.endIsActive = True
        #Set the tolerance time for "Find check-out latest"
        # cnx1=0:00 and cnx2=0:00 (According to specification no tolerance times)
        self.candidates.stations.startDefault.setCnxTol('2:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('1:00')
        #Search criteria that the user can choose
        self.candidates.standby.isActive = True
        self.candidates.blankDay.isActive = False
        
    def updateFlags(self):
        self.assFlags.setAllowOpenTime(False)
        self.assFlags.setAllowOpenTimeAny()
        self.assFlags.allowSwapOnly = True
        self.assFlags.allowSwapEarlier = True


class CheckInOnTimeProblem(ProblemType):

    """
    Crew must check-in after a specific time.
    """
    
    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Find check-in earliest')
        #self.assFlags.setAllowOpenTimeLater(True)
        
    def argUpdate(self,val):
        """
        Sets end time on end station to the value from input field.
        """
        # Convert chain start to local time. (It is assumed that input from form is local.)
        chainStartLc = timeConvert(self.problemHandler.assHandler.assignChain.start,'local')
        chainStartDate = AbsTime(AbsDate(chainStartLc))
        chainStartTime = chainStartLc - AbsTime(AbsDate(chainStartLc))
        ciStartTime = RelTime(str(val))
        if ciStartTime < chainStartTime: ciStart = chainStartDate + ciStartTime
        else: ciStart = chainStartDate + ciStartTime
        self.candidates.stations.startAfter.t_min = timeConvert(ciStart,'utc')
          
    def updateCandidates(self):
        #Find all crew that are at the departure station at most
        #one hour before the departure within 5 hours after the departure
        #self.candidates.stations.start = self.candidates.stations.startAfter
        self.candidates.stations.end = self.candidates.stations.startAfter        
        self.candidates.stations.startIsActive = True
        self.candidates.stations.endIsActive = True
        self.candidates.stations.isAndCond = True
        #Set the tolerance time for "Find check-in earliest"
        # cnx1=1:00 and cnx2=5:00
        self.candidates.stations.startDefault.setCnxTol('1:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('5:00')
        #Search criteria that the user can choose
        self.candidates.standby.isActive = True 
        self.candidates.blankDay.isActive = True
        
    def updateFlags(self):
        self.assFlags.setAllowOpenTime(False)
        self.assFlags.setAllowOpenTimeAny()
        self.assFlags.allowSwapOnly = True
        self.assFlags.allowSwapLater = True
        
    def getRelaxIds(self):
        pass 
        #return ProblemType.getRelaxIds(self)+['Check-in']

      
class CoverLegsProblem(ProblemType):

    """
    Assign open legs.
    """
    
    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Cover legs')
    
    def argUpdate(self,val):
        self.problemHandler.assHandler.assignChain.assignRank = val
        
    def updateCandidates(self):
        self.candidates.stations.startDefault.setCnxTol('2:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('1:00')
        self.candidates.stations.endIsActive = True
        self.candidates.blankDay.isActive = True

    def updateFlags(self):
        self.assFlags.setAllowOpenTime(False)
        self.assFlags.setAllowOpenTimeAny()
        self.assFlags.swapOnOverlap = False
        self.assFlags.allowSwapOnly = False
        self.assFlags.allowSwapLater = False
        self.assFlags.allowSwapEarlier = False

class SwapLegsProblem(ProblemType):

    """
    Swap legs.
    """
    
    def __init__(self,problemHandler):
        ProblemType.__init__(self,problemHandler,'Swap legs')

    def updateCandidates(self):
        self.candidates.stations.startDefault.setCnxTol('2:00')
        self.candidates.stations.startDefault.setCnxTolFwdBwd('1:00')
        self.candidates.stations.endIsActive = True
        self.candidates.standby.isActive = False
        self.candidates.blankDay.isActive = False
        
    def updateFlags(self):
        self.assFlags.allowSwapOnly = True
        self.assFlags.allowSwapEarlier = False 
        self.assFlags.allowSwapLater = False        
        self.assFlags.setAllowOpenTime(False)
        
class AssignmentFlags:

    """
    Container for flags to CuiFilterAssignable().
    May be updated by the problem types.
    """

    def __init__(self):

        # Open time options.
        self.allowOpenTime=False
        self.allowOpenTimeShorter=False
        self.allowOpenTimeEarlier=False
        self.allowOpenTimeLater=False
        self.removeOverlappingTrips=False
        
        # Swap options.
        self.swapOnOverlap=False
        self.allowSwapEarlier=False
        self.allowSwapLater=False
        self.allowSwapOnly=False

        # Gui options.
        self.showDialog=False
        self.markDeassignedLegs=True

        # General assignment options.
        self.useRemovableObjects=True
        self.checkLegality=True
        self.respectStations=True
        self.cutPacts=True

    def setCheckLegality(self, value):
        self.checkLegality = value

    def setShowDialog(self, value):
        self.showDialog = value

    def setAllowOpenTimeShorter(self,value):
        self.allowOpenTimeShorter = value
        
    def setAllowOpenTime(self,value):
        self.allowOpenTime=value
        
    def setAllowOpenTimeShorter(self,value):
        self.allowOpenTimeShorter=value

    def setAllowOpenTimeEarlier(self,value):
        self.allowOpenTimeEarlier=value
        self.allowOpenTimeLater={True:False,False:True}[value]

    def setAllowOpenTimeLater(self,value):
        self.allowOpenTimeLater=value
        self.allowOpenTimeEarlier={True:False,False:True}[value]

    def setAllowOpenTimeAny(self):
        self.allowOpenTimeEarlier=True
        self.allowOpenTimeLater=True

    def getAllowOpenTimeAny(self):
        return self.allowOpenTime and self.allowOpenTimeEarlier and self.allowOpenTimeLater

    def getAllowOpenTimeEarlier(self):
        return self.allowOpenTime and self.allowOpenTimeEarlier and not self.allowOpenTimeLater

    def getAllowOpenTimeLater(self):
        return self.allowOpenTime and self.allowOpenTimeLater and not self.allowOpenTimeEarlier
    
    def getFlagsToFilterAssignable(self):
        if debugOutput:
            if True == self.markDeassignedLegs: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_MARK_DEASSIGNED                       ', self.markDeassignedLegs,hex(Cui.CUI_FILT_ASS_MARK_DEASSIGNED)
            if True == self.showDialog: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_LOG_TO_DIALOG                         ',self.showDialog, hex(Cui.CUI_FILT_ASS_LOG_TO_DIALOG)
            if True == self.allowSwapEarlier: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_SWAP_EARLIER                    ',self.allowSwapEarlier, hex(Cui.CUI_FILT_ASS_ALLOW_SWAP_EARLIER)
            if True == self.allowSwapLater: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_SWAP_LATER                      ',self.allowSwapLater, hex(Cui.CUI_FILT_ASS_ALLOW_SWAP_LATER)
            if True == self.swapOnOverlap: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_SWAP_ON_OVERLAP                       ',self.swapOnOverlap, hex(Cui.CUI_FILT_ASS_SWAP_ON_OVERLAP)
            if True == self.allowSwapOnly: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_SWAP_ONLY                             ',self.allowSwapOnly, hex(Cui.CUI_FILT_ASS_SWAP_ONLY)
            if True == self.allowOpenTime and not self.allowOpenTimeShorter: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_PLUS_MINUS_24H       ', \
                self.allowOpenTime, self.allowOpenTimeShorter, Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_PLUS_MINUS_24H
            if True == self.getAllowOpenTimeAny(): print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_ANY_UNASSIGNED                  ',self.getAllowOpenTimeAny(), hex(Cui.CUI_FILT_ASS_ALLOW_ANY_UNASSIGNED)
            if True == self.getAllowOpenTimeEarlier(): print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_EARLIER              ',self.getAllowOpenTimeEarlier(), hex(Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_EARLIER)
            if True == self.getAllowOpenTimeLater(): print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_LATER                ',self.getAllowOpenTimeLater(), hex(Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_LATER)
            if True == self.allowOpenTime and self.allowOpenTimeShorter: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOWED_UNASSIGNED_MUST_BE_SHORTER    ', \
                self.allowOpenTime, self.allowOpenTimeShorter, hex(Cui.CUI_FILT_ASS_ALLOWED_UNASSIGNED_MUST_BE_SHORTER)
            if True == self.useRemovableObjects: print 'FindAssignableCrew.py::Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_CONTAINING_REMOVABLE ',self.useRemovableObjects, hex(Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_CONTAINING_REMOVABLE)
            print  'FindAssignableCrew.py::getFlagsToFilterAssignable:                           --- > ', hex({True:Cui.CUI_FILT_ASS_MARK_DEASSIGNED,False:0}[self.markDeassignedLegs] \
                   + {True:Cui.CUI_FILT_ASS_LOG_TO_DIALOG,False:0}[self.showDialog] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_SWAP_EARLIER,False:0}[self.allowSwapEarlier] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_SWAP_LATER,False:0}[self.allowSwapLater] \
                   + {True:Cui.CUI_FILT_ASS_SWAP_ON_OVERLAP,False:0}[self.swapOnOverlap] \
                   + {True:Cui.CUI_FILT_ASS_SWAP_ONLY,False:0}[self.allowSwapOnly] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_PLUS_MINUS_24H,False:0}[
                self.allowOpenTime and not self.allowOpenTimeShorter] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_ANY_UNASSIGNED,False:0}[self.getAllowOpenTimeAny()] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_EARLIER,False:0}[self.getAllowOpenTimeEarlier()] \
                   + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_LATER,False:0}[self.getAllowOpenTimeLater()] \
                   + {True:Cui.CUI_FILT_ASS_ALLOWED_UNASSIGNED_MUST_BE_SHORTER,False:0}[
                self.allowOpenTime and self.allowOpenTimeShorter] \
                + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_CONTAINING_REMOVABLE,False:0}[self.useRemovableObjects])
            
        return {True:Cui.CUI_FILT_ASS_MARK_DEASSIGNED,False:0}[self.markDeassignedLegs] \
               + {True:Cui.CUI_FILT_ASS_LOG_TO_DIALOG,False:0}[self.showDialog] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_SWAP_EARLIER,False:0}[self.allowSwapEarlier] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_SWAP_LATER,False:0}[self.allowSwapLater] \
               + {True:Cui.CUI_FILT_ASS_SWAP_ON_OVERLAP,False:0}[self.swapOnOverlap] \
               + {True:Cui.CUI_FILT_ASS_SWAP_ONLY,False:0}[self.allowSwapOnly] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_PLUS_MINUS_24H,False:0}[
            self.allowOpenTime and not self.allowOpenTimeShorter] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_ANY_UNASSIGNED,False:0}[self.getAllowOpenTimeAny()] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_EARLIER,False:0}[self.getAllowOpenTimeEarlier()] \
               + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_LATER,False:0}[self.getAllowOpenTimeLater()] \
               + {True:Cui.CUI_FILT_ASS_ALLOWED_UNASSIGNED_MUST_BE_SHORTER,False:0}[
            self.allowOpenTime and self.allowOpenTimeShorter] \
            + {True:Cui.CUI_FILT_ASS_ALLOW_UNASSIGNED_CONTAINING_REMOVABLE,False:0}[self.useRemovableObjects]
    
    def getFlagsToMoveAssignments(self):
        if debugOutput:
            if True == self.respectStations: print 'FindAssignableCrew.py::Cui.CUI_MOVE_ASMT_RESPECT_STATIONS                     ',self.respectStations, hex(Cui.CUI_MOVE_ASMT_RESPECT_STATIONS)
            if True == self.cutPacts: print 'FindAssignableCrew.py::Cui.CUI_MOVE_ASMT_CUT_PACTS                            ', self.cutPacts, hex(Cui.CUI_MOVE_ASMT_CUT_PACTS)
            if True == self.removeOverlappingTrips: print 'FindAssignableCrew.py::CUI_MOVE_ASMT_REMOVE_OVERLAPPING_CRRS               ', self.removeOverlappingTrips, hex(Cui.CUI_MOVE_ASMT_REMOVE_OVERLAPPING_CRRS)
            print  'FindAssignableCrew.py::FlagsToMoveAssignments:                               --- > ', hex({True:Cui.CUI_MOVE_ASMT_RESPECT_STATIONS,False:0}[self.respectStations] \
                + {True:Cui.CUI_MOVE_ASMT_CUT_PACTS,False:0}[self.cutPacts] \
                + {True:Cui.CUI_MOVE_ASMT_REMOVE_OVERLAPPING_CRRS,False:0}[self.removeOverlappingTrips])
            
        return {True:Cui.CUI_MOVE_ASMT_RESPECT_STATIONS,False:0}[self.respectStations] \
               + {True:Cui.CUI_MOVE_ASMT_CUT_PACTS,False:0}[self.cutPacts] \
               + {True:Cui.CUI_MOVE_ASMT_REMOVE_OVERLAPPING_CRRS,False:0}[self.removeOverlappingTrips]

    def __str__(self):
        strOut = "\n......<--- ASSIGNMENT FLAGS\n"
        for k in self.__dict__:
            strOut += "......%s: %s\n" % (k, str(self.__dict__[k]))
        strOut += "......---> ASSIGNMENT FLAGS\n"
        return strOut
        
#
# CANDIDATE HANDLING
# ---------------------
#
# Class CandidateHandler
# Container of all defined candidate criterias.
#
# Class CandidateCriteria
# Base class for a candidate criteria definition.
#   
    
class CandidateHandler:
    
    """
    Container of all defined candidate criterias.
    """
    
    def __init__(self,assignChain):
        self.assignChain = assignChain
        self.defaultPeriod = TimePeriod(assignChain.start,assignChain.end)
        self.stations = StationsCandidate(assignChain.startStn,assignChain.endStn,
                                          self.defaultPeriod,self.defaultPeriod)
        # manyDuties is not considered in SAS according to Requirenment Specification Find Assignable
        self.daysOff = DaysOffCandidate(self.defaultPeriod)
        self.blankDay = BlankDaysCandidate(self.defaultPeriod)
        self.volunteer = VolunteerCandidate(self.defaultPeriod, assignChain.volunteerType)
        self.standby = StandbyCandidate(self.defaultPeriod)
        self.crewFunc = CrewFuncCandidate(self.defaultPeriod.start,assignChain)
        self.acQual = AcQualCandidate(self.defaultPeriod, assignChain.acTypes)
        self.region = CrewRegionCandidate(self.defaultPeriod.start, assignChain.regions)
        self.checkInEarlier = CheckInEarlierCandidate(assignChain.startStn,assignChain.endStn,
                                                      self.defaultPeriod, max_duty='14:00')
        self.types = self.getCandidateList()

    def getCandidateList(self):
        candList = []
        for k in self.__dict__:
            if isinstance(self.__dict__[k],Candidate):
                candList.append(self.__dict__[k])
        candList.sort(self.sortFunc)
        return candList

    def sortFunc(self,x,y):
        if x.visibleSortIx < y.visibleSortIx: return -1
        elif x.visibleSortIx == y.visibleSortIx: return 0
        else: return 1
        
    def setAssignChain(self, assignChain):
        self.crewFunc.setSelectCriteria(assignChain)
        
    def selectCriteria(self):

        """
        Not 100% safe for all combinations.
        """

        criteria = ""
        mandatory = []
        userSelection = []
        hiddenSelection = []
        notSelected = []
        
        for candidate in self.types:
            if candidate.isActive:
                if candidate.isMandatory:
                    mandatory.append(candidate)
                else:
                    userSelection.append(candidate)
            else: notSelected.append(candidate)

        # Collect mandatory candidates (=AND)
        for candidate in mandatory:
            criteria += candidate.selectCriteria()
            if candidate != mandatory[-1]:    criteria += " and "
            else:    criteria += " and ("
        
        # Append the rest (=OR)
        for ix,candidate in zip(range(len(userSelection)),userSelection):
            criteria += candidate.selectCriteria()
            if ix <> len(userSelection)-1:
                criteria += " or "
        if len(notSelected) > 0:
            criteria += ") and not "
        else:
            criteria += ")"
        
        #Append not selected items from the include section Find Assignable form
        for ix,candidate in zip(range(len(notSelected)), notSelected):
            if not candidate.name in ['Day off']:
                criteria += candidate.selectCriteria()
                if ix <> len(notSelected)-1:
                    if not notSelected[ix+1].name == notSelected[-1].name in ['Day off']:
                        criteria += " and not "
        if ix == 0:
            criteria += "false"

        if debugOutput:
            print "FindAssignableCrew.py::Select criteria: START"
            print "\n            or ".join("and (".join("\n        and ".join(criteria.strip().split(" and ")).split("and (")).split("or "))
            print "FindAssignableCrew.py::Select criteria: END"
        return criteria

    def sortCriteria(self):    
        sort_criteria = MAP_CANDIDATE_SORT_FUNC +"(%s,%s)" % (str(self.assignChain.start),
                                                            str(self.assignChain.end))
        #if debugOutput:
            #print "FindAssignableCrew.py::Sort criteria: ", sort_criteria
        return sort_criteria

    
    def __str__(self):
        strOut = "\n...<--- *** CANDIDATE HANDLER\n"
        for k in self.__dict__:
            if isinstance(self.__dict__[k], Candidate):
                strOut += "...%s: %s\n" % (k, str(self.__dict__[k]))
        strOut += "...*** ---> CANDIDATE HANDLER\n"
        return strOut


class Candidate:

    """
    Mandatory: The crew must have this criteria (=and condition).
    Visible: The Tracker may access criteria from GUI.
    Active: The criteria is in use.
    """
    
    def __init__(self,name="",isMandatory=False,isVisible=False,isActive=True):
        self.isMandatory = isMandatory
        self.isVisible = isVisible
        self.visibleSortIx = 0
        self.isActive = isActive
        self.name = name

    def selectCriteria(self):
        pass
    
    def activate(self,value):
        self.isActive = value

    def getIsActive(self):
        return self.isActive
    
    def __str__(self):
        strOut = "\n......<--- CANDIDATE\n"
        for k in self.__dict__:
            strOut += "......%s: %s\n" % (k, str(self.__dict__[k]))
        strOut += "......---> CANDIDATE\n"
        return strOut

class BlankDaysCandidate(Candidate):
    
    def __init__(self, period):
        Candidate.__init__(self,'Blank day', False, True, False)
        self.period = period
        self.visibleSortIx = 20
        
    def selectCriteria(self):
        return MAP_CANDIDATE_BLANK_DAYS_FUNC+"(%s, %s)" % (str(self.period.start),
                                                           str(self.period.end))
    
class DaysOffCandidate(Candidate):

    def __init__(self, period):
        Candidate.__init__(self,'Day off', False, True, False)
        self.period = period
        self.visibleSortIx = 40

    def selectCriteria(self):            
        return MAP_CANDIDATE_DAYS_OFF_FUNC +"(%s,%s)" % (str(self.period.start),
                                                         str(self.period.end))

class VolunteerCandidate(Candidate):

    """
    Crew is volunteer for work.
    """

    def __init__(self, period, type):
        Candidate.__init__(self,'Volunteer', False, True, False)
        self.period = period
        self.type = type
        self.visibleSortIx = 10
       
    def selectCriteria(self):
        return MAP_CANDIDATE_VOLUNTEER_FUNC +"(%s,%s,\"%s\")" % (str(self.period.start),
                                                                 str(self.period.end),
                                                                 str(self.type))

class StandbyCandidate(Candidate):

    """
    Crew has standby in interval.
    """

    def __init__(self, period):
        Candidate.__init__(self,'Standby / Reserve', False, True, True)
        self.period = period
        self.visibleSortIx = 30

    def selectCriteria(self):
        return MAP_CANDIDATE_STANDBY_FUNC +"(%s,%s)" % (str(self.period.start),
                                                        str(self.period.end))

    
class StationsCandidate(Candidate):

    """
    Crew is on the right place & time.
    """

    def __init__(self,stn1,stn2,period1,period2,cnx1='2:00',cnx2='1:00',manyDuties=False,isAndCond=False):
        Candidate.__init__(self,"Stations",False,False,True)
        # If several duties have been marked there is no use in limit the duty time.
        #if manyDuties: max_duty = '168:00'
        #else: max_duty = '14:00'

        #FOLLOWING TWO ARE DEBUG HACKS! /OLOF       
        #t_max = period2.start + RelTime('24:00')
        #t_min = period1.end - RelTime('24:00')
    
        #StartStationCandidate and EndStationCandidate is used in solve check-in problem
        #Solve connection problem, Find check-out latest, Find check-out earliest
        #Cover legs, swap legs
        self.startDefault = StartStationCandidate(stn1,period1,cnx1,cnx2)
        self.endDefault = EndStationCandidate(stn2,period2,cnx2,cnx1)

        #Find check-out latest
        self.endBefore = ArriveBeforeCandidate(stn1,stn2,period2.start,cnx1)
        
        #Find check-in earliest
        self.startAfter = DepartAfterCandidate(stn1,stn2,period2.end,cnx1)#t_min)
        
        self.start = self.startDefault
        self.end = self.endDefault
        self.isAndCond = isAndCond
        self.startIsActive = True
        self.endIsActive = False

    def selectCriteria(self):
        startStationCriteria = self.start.selectCriteria()
        endStationCriteria = self.end.selectCriteria()
        if self.startIsActive and self.endIsActive:            
            condStr = {True:" and ",False:" or "}[self.isAndCond]
            return startStationCriteria+condStr+endStationCriteria
        elif self.startIsActive: return startStationCriteria
        elif self.endIsActive: return endStationCriteria
        else: return ''


class StationCandidate(Candidate):
    
    def __init__(self,station,period,cnx_tol='2:00',cnx_tol_fwd_bwd='1:00'):
        self.station = station
        self.start = period.start
        self.end = period.end
        self.cnx_tol = cnx_tol
        self.cnx_tol_fwd_bwd = cnx_tol_fwd_bwd
        
    def getCnxTol(self):
        return self.cnx_tol
    
    def setCnxTol(self, cnx):
        self.cnx_tol = cnx
    
    def getCnxTolFwdBwd(self):
        return self.cnx_tol_fwd_bwd 
    
    def setCnxTolFwdBwd(self, cnx):
        self.cnx_tol_fwd_bwd = cnx
        
class StartStationCandidate(StationCandidate):

    def selectCriteria(self):
        return MAP_CANDIDATE_START_STN_FUNC+"(\"%s\",%s,%s,%s,%s)" % (str(self.station),
                                                                      str(self.start),
                                                                      str(self.end),
                                                                      str(self.cnx_tol),
                                                                      str(self.cnx_tol_fwd_bwd))
class EndStationCandidate(StationCandidate):
    
    def selectCriteria(self):
        return MAP_CANDIDATE_END_STN_FUNC+"(\"%s\",%s,%s,%s,%s)" % (str(self.station),
                                                                    str(self.start),
                                                                    str(self.end),
                                                                    str(self.cnx_tol),
                                                                    str(self.cnx_tol_fwd_bwd))
class CheckInEarlierCandidate(Candidate):
    
    def __init__(self, stn1, stn2, period, max_duty='14:00'):
        Candidate.__init__(self,"Check-in after",False,True,False)
        self.period = period
        self.stn1 = stn1
        self.stn2 = stn2
        self.max_duty = max_duty
        self.visibleSortIx = 50

    def selectCriteria(self):
        return MAP_CI_EARLIER_FUNC +"(\"%s\",\"%s\",%s,%s,%s)" % (str(self.stn1),
                                                                  str(self.stn2),
                                                                  str(self.period.start),
                                                                  str(self.period.end),
                                                                  str(self.max_duty))


class ArriveBeforeCandidate:
    def __init__(self, stn1, stn2, t, t_max=None, cnx_tol='4:00'):
        self.t = t
        self.t_max = t_max
        self.stn1 = stn1
        self.stn2 = stn2
        self.cnx_tol = cnx_tol
            
    def selectCriteria(self):
        return MAP_ARRIVE_BEFORE_FUNC +"(\"%s\",\"%s\",%s,%s,%s)" % (str(self.stn1),
                                                                     str(self.stn2),
                                                                     str(self.t),
                                                                     str(self.t_max),
                                                                     str(self.cnx_tol))
                                                                     
class DepartAfterCandidate:
    def __init__(self, stn1, stn2, t, t_min=None, cnx_tol='5:00'):
        self.t = t
        self.t_min = t_min
        self.stn1 = stn1
        self.stn2 = stn2
        self.cnx_tol = cnx_tol
            
    def selectCriteria(self):
        return MAP_DEPART_AFTER_FUNC +"(\"%s\",\"%s\",%s,%s,%s)" % (str(self.stn1),
                                                                    str(self.stn2),
                                                                    str(self.t_min),
                                                                    str(self.t),
                                                                    str(self.cnx_tol))
    
class CrewFuncCandidate(Candidate):

    """
    Crew has right function for trip.
    """
    
    def __init__(self,start,assignChain,allowBelowRank=True):
        Candidate.__init__(self, 'Crew Func', True, False, True)
        self.start = start
        self.func = assignChain.assignRank
        self.allowBelowRank = allowBelowRank
    
    def setSelectCriteria(self, assignChain):
        """
        After update assigChain FAC has to set the value
        """
        self.func = assignChain.assignRank
        
    def selectCriteria(self):
        return MAP_CANDIDATE_ALLOWED_RANK_FUNC+"(%s,\"%s\",%s)" % (str(self.start),
                                                                   str(self.func),
                                                                   bool2str(self.allowBelowRank))


class AcQualCandidate(Candidate):

    """
    Crew is qualified for A/C type.
    """

    def __init__(self,period,acTypes):
        Candidate.__init__(self, 'Ac Qual', True, False, True)
        self.start = period.start
        self.end = period.end
        self.acTypes = acTypes
    
    def selectCriteria(self):
        criteria = ""
        for acType in self.acTypes:
            if criteria <> "":
                criteria += " and "
            criteria += MAP_CANDIDATE_AC_TYPE_FUNC+"(%s, %s, \"%s\")" % (str(self.start),str(self.end),acType)
        if criteria == "":
            criteria = "True"
        return criteria
    
class CrewRegionCandidate(Candidate):

    """
    Crew has right region for trip.
    """
    
    def __init__(self,start,assignChain):
        Candidate.__init__(self, 'Crew Region', True, False, True)
        self.start = start
        self.regions = assignChain
                
    def selectCriteria(self):
        criteria = ""
        for region in self.regions:
            if criteria <> "":
                criteria += " or "
            criteria += MAP_CANDIDATE_ALLOWED_REGION_FUNC+"(%s,\"%s\")" % (str(self.start),
                                                                 str(region))            
        return criteria

#
# FORM DEFINITIONS
# ----------------
#

class FindAssignableCrewForm(Cfh.Box):

    """
    All fields which should get updated depending on selected problem type
    should be appended to the 'updateFields' list. Each such fields must
    have a updateFromModel() & writeToModel() member function defined.
    writeToModel() is executed on press OK. updateFromModel() is executed
    on a problem type click.
    'problemTypeFields' is a collection of all problem types. Fields are
    automatically generated for max 9 problem types.
    'candidateTypeFields' is a collection of candidates marked as 'isVisible'.
    'relaxFields' is a collection of relax criteries generated from the
    relax table used.
    """
    
    def __init__(self,handler):
        Cfh.Box.__init__(self,"Find Assignable Crew")
        self.handler = handler
        self.candidates = self.handler.candidates
        self.updateFields = []
        self.relaxIds = RuleRelaxationTable().getOptionalRelaxationKeys()
        self.createForm()
        self.initFieldsForActiveProblem()
        
    def createForm(self):
        
        self.problemTypeFields = []
        self.candidateTypeFields = []
        self.relaxFields = []

        # Rule relaxation fields 1...9
        for ix,relaxId in zip(range(len(self.relaxIds)),self.relaxIds):
            self.relaxFields.append(CfhRuleRelaxationFields(self,relaxId,ix+1))
        
        # Visible candidate criteria fields 1...9
        for ix,candidate in zip(range(len(self.handler.candidates.types)),self.handler.candidates.types):
            if candidate.isVisible:
                self.candidateTypeFields.append(CfhCandidateTypeFields(self,candidate,ix+1))
        
        # Problem type fields 1...9
        for ix,problem in zip(range(len(self.handler.problems.types)),self.handler.problems.types):
            self.problemTypeFields.append(CfhProblemTypeFields(self,problem,ix+1))

        # Other fields
       
        self.openTimeType = CfhOpenTimeTypeRadio(self,"ALLOW_OPEN_TIME_TYPE")
        self.openTimeShorter = CfhToggle(self,"ALLOW_OPEN_TIME_SHORTER",
                                         self.handler.flags.setAllowOpenTimeShorter,
                                         self.handler.flags.allowOpenTimeShorter)
        self.allowOpenTime = CfhOpenTimeToggle(self,"ALLOW_OPEN_TIME")
        self.allowSwapType = CfhAllowSwapTypeRadio(self,"ALLOW_SWAP_TYPE")
        self.workLevel = CfhWorkLevelRadio(self,"WORK_LEVEL")
        self.allowSwap = CfhAllowSwapRadio(self,"ALLOW_SWAP")
        self.assignmentTest = CfhToggle(self, "ASSIGNMENT_TEST",
                                        self.handler.flags.setCheckLegality,
                                        self.handler.flags.checkLegality)
        self.logIllegal = CfhToggle(self, "ASSIGNMENT_LOG",
                                    self.handler.flags.setShowDialog,
                                    self.handler.flags.showDialog)
        self.maxHits = Cfh.Number(self, "ASSIGNMENT_MAX_HITS", 0, False)

        # Buttons.
        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")

        # Load form template...
        self.loadFormFile()

    def getAllowSwapValue(self):
        try:
            return self.allowSwap.getValue()
        except:
            return None

    def initFieldsForActiveProblem(self):
        for problemField in self.problemTypeFields:
            if problemField.problem.isActive:
                problemField.toggle.compute()

    def updateFieldsFromModel(self):
        for field in self.updateFields:
            field.updateFromModel();
        
    def loadFormFile(self):
        fname = tempfile.mktemp()
        f = open(fname,"w")
        layout = """
        FORM;FindAssignableCrewForm;Find Assignable Crew
        PAGE;MAIN_PAGE;`Main`;CTRL,HIDE
        GROUP
        LABEL;Presets:;
        FIELD;P1_LABEL;
        FIELD;P2_LABEL;
        FIELD;P3_LABEL;
        FIELD;P4_LABEL;
        FIELD;P5_LABEL;
        FIELD;P6_LABEL;
        FIELD;P7_LABEL;
        FIELD;P8_LABEL;
        FIELD;P9_LABEL;
        COLUMN
        LABEL;
        FIELD;P1_VALUE;
        FIELD;P2_VALUE;
        FIELD;P3_VALUE;
        FIELD;P4_VALUE;
        FIELD;P5_VALUE;
        FIELD;P6_VALUE;
        FIELD;P7_VALUE;
        FIELD;P8_VALUE;
        FIELD;P9_VALUE;
        COLUMN
        LABEL;
        FIELD;P1_ARG;
        FIELD;P2_ARG;
        FIELD;P3_ARG;
        FIELD;P4_ARG;
        FIELD;P5_ARG;
        FIELD;P6_ARG;
        FIELD;P7_ARG;
        FIELD;P8_ARG;
        FIELD;P9_ARG;
        COLUMN;
        LABEL;Include:;
        FIELD;C1_LABEL;
        FIELD;C2_LABEL;
        FIELD;C3_LABEL;
        FIELD;C4_LABEL;
        FIELD;C5_LABEL;
        FIELD;C6_LABEL;
        FIELD;C7_LABEL;
        FIELD;C8_LABEL;
        FIELD;C9_LABEL;
        FIELD;C10_LABEL;
        FIELD;C11_LABEL;
        FIELD;C12_LABEL;
        FIELD;C13_LABEL;
        FIELD;C14_LABEL;
        FIELD;C15_LABEL;
        COLUMN;
        LABEL;
        FIELD;C1_VALUE;
        FIELD;C2_VALUE;
        FIELD;C3_VALUE;
        FIELD;C4_VALUE;
        FIELD;C5_VALUE;
        FIELD;C6_VALUE;
        FIELD;C7_VALUE;
        FIELD;C8_VALUE;
        FIELD;C9_VALUE;
        FIELD;C10_VALUE;
        FIELD;C11_VALUE;
        FIELD;C12_VALUE;
        FIELD;C13_VALUE;
        FIELD;C14_VALUE;
        FIELD;C15_VALUE;
        GROUP
        COLUMN;
        FIELD;ALLOW_OPEN_TIME;Allow open time
        FIELD;ALLOW_OPEN_TIME_TYPE;of type
        FIELD;ALLOW_OPEN_TIME_SHORTER;but only shorter
        COLUMN;
        FIELD;ALLOW_SWAP;Swap
        FIELD;ALLOW_SWAP_TYPE;of type
        COLUMN;
        FIELD;WORK_LEVEL;Work with
        FIELD;ASSIGNMENT_MAX_HITS;Max assignment hits
        PAGE;TECH_PAGE;`Technical`;CTRL,HIDE
        FIELD;ASSIGNMENT_TEST;Verify assignment legality
        FIELD;ASSIGNMENT_LOG;Show assignment log
        BUTTON;B_OK;`OK`;`_OK`
        BUTTON;B_DEFAULT;`Default`;`_Default`
        BUTTON;B_CANCEL;`Cancel`;`_Cancel`"""
        try:
            f.write("\n".join((map(lambda s: s.strip(), layout.strip().split("\n")))))
            f.close()
            self.load(fname)
        finally:
            os.unlink(fname)

    def writeToModel(self):
        """
        Run the update function for all candidate criterias registered in
        the list self.candidateFields.
        """
        if debugOutput:
            print 'FindAssignableCrew.py::writeToModel ..... START: '
            
        for field in self.updateFields:
            field.writeToModel()
            
        if debugOutput:
            print 'FindAssignableCrew.py::writeToModel ..... END: '


class CfhOpenTimeToggle(Cfh.Toggle):

    def __init__(self,box,name):
        self.box = box
        self.box.updateFields.append(self)
        Cfh.Toggle.__init__(self,box,name,0)
        self.updateFromModel()
        
    def updateFromModel(self):
        self.assign(self.box.handler.flags.allowOpenTime)
        self.check({True:"True",False:"False"}[self.box.handler.flags.allowOpenTime])

    def writeToModel(self):
        if self.box.handler.flags.allowOpenTime:
            self.box.handler.flags.setAllowOpenTime(self.valof())
        else:
            self.box.handler.flags.allowOpenTimeLater = False
            self.box.handler.flags.allowOpenTimeEarlier = False
        if debugOutput:
            print 'FindAssignableCrew.py::Open Time: ................. ', self.valof()
            print 'FindAssignableCrew.py::  allowOpenTime         ', self.box.handler.flags.allowOpenTime
            print 'FindAssignableCrew.py::  allowOpenTimeEarlier  ', self.box.handler.flags.allowOpenTimeEarlier
            print 'FindAssignableCrew.py::  allowOpenTimeLater    ', self.box.handler.flags.allowOpenTimeLater

        
    def check(self, str) :
        r = Cfh.Toggle.check(self, str)
        if str == "False":
            self.box.openTimeType.setEnable(False)
            self.box.openTimeShorter.setEnable(False)
            try:
                if self.box.allowSwap.getValue() == "Forbidden":
                    self.box.workLevel.setEnable(False)
            except:
                pass
            self.box.handler.flags.allowOpenTime = False
        else:
            self.box.openTimeType.setEnable(True)
            self.box.openTimeShorter.setEnable(True)
            self.box.workLevel.setEnable(True)
            self.box.handler.flags.allowOpenTime = True
        return r


class CfhOpenTimeTypeRadio(Cfh.String):

    def __init__(self,box,name):
        self.box = box
        self.box.updateFields.append(self)
        Cfh.String.__init__(self,box,name,0,"")
        self.setMenuString("Select;Any;Earlier;Later")
        self.setStyle(Cfh.CfhSChoiceRadioCol)
        self.updateFromModel()

    def updateFromModel(self):
        if self.box.handler.flags.allowOpenTimeEarlier and self.box.handler.flags.allowOpenTimeLater:
            self.assign("Any")
        elif self.box.handler.flags.allowOpenTimeEarlier:
            self.assign("Earlier")
        elif self.box.handler.flags.allowOpenTimeLater:
            self.assign("Later")
        else: self.assign("Any")

    def writeToModel(self):
        if self.box.handler.flags.allowOpenTime:
            if self.valof() == "Earlier":
                self.box.handler.flags.setAllowOpenTimeEarlier(True)
            elif self.valof() == "Later":
                self.box.handler.flags.setAllowOpenTimeLater(True)
            else:
                self.box.handler.flags.setAllowOpenTimeAny()
                
        if debugOutput:
            print 'FindAssignableCrew.py::Open Time Type: ............ ', self.valof()
            print 'FindAssignableCrew.py::  allowOpenTime         ', self.box.handler.flags.allowOpenTime
            print 'FindAssignableCrew.py::  allowOpenTimeEarlier  ', self.box.handler.flags.allowOpenTimeEarlier
            print 'FindAssignableCrew.py::  allowOpenTimeLater    ', self.box.handler.flags.allowOpenTimeLater

class CfhAllowSwapRadio(Cfh.String):

    def __init__(self,box,name):
        self.box = box
        self.box.updateFields.append(self)
        Cfh.String.__init__(self,box,name,0,"")
        self.setMenuString("Select;Required;Allowed;Forbidden")
        self.setStyle(Cfh.CfhSChoiceRadioCol)
        self.updateFromModel()

    def updateFromModel(self):        
        if self.box.handler.flags.allowSwapOnly:
            self.assign("Required")
            self.check("Required")
        elif self.box.handler.flags.swapOnOverlap:
            self.assign("Allowed")
            self.check("Allowed")
        else:
            self.assign("Forbidden")
            self.check("Forbidden")
            
    def writeToModel(self):
        if self.valof() == "Required":
            self.box.handler.flags.allowSwapOnly = True
            self.box.handler.flags.swapOnOverlap = False
        elif self.valof() == "Allowed":
            self.box.handler.flags.swapOnOverlap = True
            self.box.handler.flags.allowSwapOnly = False
        else:
            self.box.handler.flags.swapOnOverlap = False
            self.box.handler.flags.allowSwapOnly = False
            
        if debugOutput:
            print 'FindAssignableCrew.py::Allow Swap: ................ ', self.valof()
            print 'FindAssignableCrew.py::  swapOnOverlap         ', self.box.handler.flags.swapOnOverlap
            print 'FindAssignableCrew.py::  allowSwapOnly         ', self.box.handler.flags.allowSwapOnly

    def check(self, str) :
        r = Cfh.String.check(self, str)
        if str == "Forbidden":
            self.box.allowSwapType.setEnable(False)
            self.box.workLevel.assign('Legs')
            try:
                if self.box.allowOpenTime.getValue() == "False":
                    self.box.workLevel.setEnable(False)
            except:
                pass
        else:
            self.box.allowSwapType.setEnable(True)
            self.box.workLevel.setEnable(True)
            self.box.workLevel.assign("Trips")
        return r

class CfhAllowSwapTypeRadio(Cfh.String):
    def __init__(self,box,name):
        self.box = box
        self.box.updateFields.append(self)
        Cfh.String.__init__(self,box,name,0,"")
        self.setMenuString("Select;Any;Earlier;Later")
        self.setStyle(Cfh.CfhSChoiceRadioCol)
        self.updateFromModel()

    def updateFromModel(self):
        if self.box.handler.flags.allowSwapEarlier:
            self.assign("Earlier")
        elif self.box.handler.flags.allowSwapLater:
            self.assign("Later")
        else:
            self.assign("Any")
                
    def writeToModel(self):
        if not self.box.allowSwap.getValue() == "Forbidden":
            if self.valof() == "Earlier":
                self.box.handler.flags.allowSwapEarlier = True
                self.box.handler.flags.allowSwapLater = False
            elif self.valof() == "Later":
                self.box.handler.flags.allowSwapEarlier = False
                self.box.handler.flags.allowSwapLater = True
            else:
                self.box.handler.flags.allowSwapEarlier = True
                self.box.handler.flags.allowSwapLater = True
        else:
            self.box.handler.flags.allowSwapEarlier = False
            self.box.handler.flags.allowSwapLater = False
        if debugOutput:
            print 'FindAssignableCrew.py::Allow Swap Type: ........... ', self.valof()
            print 'FindAssignableCrew.py::  allowSwapEarlier      ', self.box.handler.flags.allowSwapEarlier
            print 'FindAssignableCrew.py::  allowSwapLater        ', self.box.handler.flags.allowSwapLater
            

class CfhWorkLevelRadio(Cfh.String):
    def __init__(self,box,name):
        self.box = box
        self.box.updateFields.append(self)
        Cfh.String.__init__(self,box,name,0,"")
        self.setMenuString("Select;Legs;Trips")
        self.setStyle(Cfh.CfhSChoiceRadioCol)
        self.updateFromModel()

    def updateFromModel(self):
        if self.box.handler.flags.removeOverlappingTrips:
            self.assign("Trips")
        else:
            self.assign("Legs")
        
    def writeToModel(self):
        if self.box.handler.flags.allowOpenTime or not self.box.handler.flags.allowOpenTime and(not self.box.allowSwap.getValue() == "Forbidden"):
            if self.valof() == "Trips":
                self.box.handler.flags.removeOverlappingTrips = True
        else:
            self.box.handler.flags.removeOverlappingTrips = False
            
        if debugOutput:
            print 'FindAssignableCrew.py::Work Level ................. ', self.valof()
            

class CfhToggle(Cfh.Toggle):
    
    def __init__(self,box,name,writeToModelFunc,initValue=0,updateFromModelFunc=None):
        self.box = box
        self.name = name
        self.writeToModelFunc = writeToModelFunc
        self.updateFromModelFunc = updateFromModelFunc
        self.box.updateFields.append(self)
        Cfh.Toggle.__init__(self,box,name,initValue)
        self.updateFromModel()
        
    def updateFromModel(self):
        if self.updateFromModelFunc is None: pass
        else: self.assign(self.updateFromModelFunc())
       
    def writeToModel(self):
        if self.name == 'ALLOW_OPEN_TIME_SHORTER':
            if self.box.handler.flags.allowOpenTime:
                self.writeToModelFunc(self.valof())
            else:
               self.box.handler.flags.allowOpenTimeShorter = False 
        else:
            self.writeToModelFunc(self.valof())


class CfhProblemTypeFields:

    def __init__(self,box,problem,ix):
        self.box = box
        self.problem = problem
        self.label = CfhLabel(self.box,"P"+str(ix)+"_LABEL",0,self.problem.name)
        self.toggle = CfhProblemRadio(self.box,"P"+str(ix)+"_VALUE",self.box.problemTypeFields,self.problem)
        self.argField = self.createArgField(self.box,"P"+str(ix)+"_ARG",self.problem)
        
    def createArgField(self, box, name, problem):
        if isinstance(self.problem, CheckInOnTimeProblem):
            return CfhProblemTypeTimeField(box, name, problem,
                         timeConvert(self.box.handler.assignChain.start,'local'))
        elif isinstance(self.problem, CheckOutOnTimeProblem):
            return CfhProblemTypeTimeField(box, name, problem,
                         timeConvert(self.box.handler.assignChain.end,'local'))
        elif isinstance(self.problem, CoverLegsProblem):
            return CfhProblemTypeMenuField(box, name, problem, self.box.handler.assignChain.openRanks)       
        else: return CfhLabel(box, name, 0, "")


class CfhLabel(Cfh.String):

    def __init__(self,box,name,fieldLenth,text):
        Cfh.String.__init__(self,box,name,fieldLenth,text)
        self.setStyle(Cfh.CfhSLabelNormal)


class CfhProblemRadio(Cfh.Toggle):
    """
    Radio toggle object. This object syncronizes it self with
    a number of other toggles. Each time one toggle in the
    group is presses, the others are depressed, so that
    always only one toggle is pressed.

    The list of other Radio toggles to synchrounize with
    is supplied as an extra last argument to the constructor.

    Example:
        b=Cfh.Box('Test')
        radio_list = []
        radio_list.append(Radio(self, 'T1',0, radio_list))
        radio_list.append(Radio(self, 'T2',1, radio_list))
     """

    def __init__(self,box,name,problemFields,problem):

        self.box = box
        self.problemFieldList = problemFields
        self.problem = problem
        self.box.updateFields.append(self)
        Cfh.Toggle.__init__(self,box,name,self.problem.isActive)
         
    #def verify(self,buf):
    #    if not 1 in [self.toRepr(t.getValue()) for t in self.radio_list]:
        #   buf.value = self.toString(1)
 
    def compute(self):
        for problemField in self.problemFieldList:
            if problemField.toggle <> self:
                problemField.toggle.assign(0)
                problemField.argField.setEnable(False)
            else:
                problemField.toggle.assign(1)
                problemField.argField.setEnable(True)
        self.problem.writeToModel()
        self.box.updateFieldsFromModel()
        return Cfh.Toggle.compute(self)

    def writeToModel(self):
        pass
        #if self.valof():
        #    self.box.handler.relaxList += self.problem.getRelaxIds()
        
    def updateFromModel(self):
        pass
    
class CfhProblemTypeTimeField(Cfh.Clock):
    
    def __init__(self,box,name,problemType,initValue=AbsTime(0)):
        self.box = box
        self.problemType = problemType
        self.box.updateFields.append(self)
        Cfh.Clock.__init__(self,box,name,int(initValue))
    
    def writeToModel(self):
        """
        This function will execute the update function
        if the field is enabled.
        """   
        if self.getEnable():
            self.problemType.argUpdate(RelTime(self.valof()))

    def updateFromModel(self):
        pass

    
class CfhProblemTypeMenuField(Cfh.String):
    
    def __init__(self,box,name,problemType,menu):
        self.box = box
        self.problemType = problemType
        self.menu = menu
        self.box.updateFields.append(self)
        Cfh.String.__init__(self,box,name,0,menu[0])
        self.setMenuString(self.createMenu())
        self.setMenuOnly(True)

    def createMenu(self):
        menuTxt = "Select"
        for txt in self.menu:
            menuTxt += ";%s" % str(txt)
        return menuTxt
    
    def writeToModel(self):
        self.problemType.argUpdate(self.valof())

    def updateFromModel(self):
        pass
    

class CfhCandidateTypeFields:
    
    def __init__(self,box,candidate,ix):
        self.box = box
        self.candidate = candidate
        self.label = CfhLabel(self.box,"C"+str(ix)+"_LABEL",0,self.candidate.name)
        self.toggle = CfhToggle(self.box,"C"+str(ix)+"_VALUE",self.candidate.activate,self.candidate.isActive,self.candidate.getIsActive)


class CfhRuleRelaxationFields:
    
    def __init__(self,box,relaxId,ix):
        self.box = box
        self.relaxId = relaxId
        self.label = CfhLabel(self.box,"R"+str(ix)+"_LABEL",0,self.relaxId)
        self.toggle = CfhToggle(self.box,"R"+str(ix)+"_VALUE",self.writeRelaxationList,0)

    def writeRelaxationList(self,value):
        if value: self.box.handler.relaxList.append(self.relaxId)
        else: pass
                 

#
# ASSIGNMENT HANDLING
# -------------------
#
# Class AssignmentHandler
# 
# Class Area
#
# Class AssignChain
#

class AssignmentHandler:

    """
    Main container for various things used by findAssignable.
    """

    def __init__(self):
        #self.now = TimeUtil.getNow()
        self.now = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, 'NONE', MAP_NOW_TIME)
        self.assignChainArea = Area()
        StudioRules().getAllStudioRulesAndValues()
        StudioRules().getAllTurnOffRulesBeforeFindAssignable(self.assignChainArea.id)
        StudioRules().getRulesThatAreFacFormDependent(self.assignChainArea.id)
        StudioRules().getAllLegalitySubsetRules(self.assignChainArea.id)
        self.candidateArea = None
        self.flags = AssignmentFlags()
        self.assignChain = AssignChain(self.assignChainArea)
        self.candidates = CandidateHandler(self.assignChain)
        self.candidateList = []
        self.relaxList = []
        mKey = RuleRelaxationTable().mandatoryKey()
        if not mKey is None: self.relaxList.append(mKey)
        self.problems = ProblemTypeHandler(self)
    
    def getDataFromForm(self, test_mode):
        """
        Get data from form input.
        """
        gc.collect()
        self.form = FindAssignableCrewForm(self)
        if not test_mode:
            self.form.show(1)
        if self.form.loop() == 0:            
            StudioRules().turnOffRulesBeforeFindAssignable()
            StudioRules().checkAllRulesAreAvailable()            
            self.form.writeToModel()            
            self.candidates.setAssignChain(self.assignChain)            
            self.candidateList = self.generateCandidates()
        elif self.form.loop() == 1:
            raise KeyboardInterrupt

    def generateCandidates(self):
        StdArea.promptPush('Searching candidates...')
        t = time()
        crewCands=[]
        crew = R.eval('sp_crew',R.foreach(R.iter(MAP_CHAIN_SET,
                                                 where = self.candidates.selectCriteria(),
                                                 sort_by = self.candidates.sortCriteria()),
                                          'crr_crew_id'))[0]
        for cand in crew:
            #crewCands.append(cand['CREW_ID'])
            crewCands.append(cand[1])
        print "FindAssignableCrew.py::Time for RAVE API: "+str(time()-t)
        StdArea.promptPush('Searching candidates...done')
        return crewCands

    def activateCandidateArea(self):
        candArea = StdArea.getFirstArea(Cui.CrewMode, self.assignChainArea.id)
        if candArea == Cui.CuiNoArea:
            candArea = StdArea.getFirstArea(Cui.NoMode)
            if candArea == Cui.CuiNoArea:
                candArea = StdArea.createNewArea()
        if candArea == Cui.CuiNoArea:
            Message.show(MSGR('Could not retrieve or create a crew area!\n'+
                                'Too many non-crew areas are active.\n'+
                                'Please close an area before proceeding!'))
            raise KeyboardInterrupt
        else:
            Cui.CuiDisplayObjects(Cui.gpc_info, candArea, Cui.CrewMode, Cui.CuiShowNone)
            self.candidateArea = Area(candArea,Cui.CrewMode)
                                                                                                                            

#    def activateCandidateArea(self):
#
#        area = Util.getArea(Cui.CrewMode,self.assignChainArea.id)
#        if area is None: raise KeyboardInterrupt
#        else: self.candidateArea = Area(area, Cui.CrewMode)

    def __str__(self):
        strOut = "\n<--- *** *** ASSIGNMENT HANDLER\n"
        for k in self.__dict__:
            try: strOut += "%s: %s\n==================================\n" % (k, str(self.__dict__[k]))
            except: strOut += "%s: Unknown value" % k
        strOut += "*** *** ---> ASSIGNMENT HANDLER\n"
        return strOut
        
        
class TimePeriod:

    def __init__(self,start=None,end=None):
        self.start = start
        self.end = end

    def __str__(self):
        return "%s - %s" % (str(self.start), str(self.end)) 


class Area:

    def __init__(self,id=None,mode=None):
        if id is None:
            self.id = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        else: self.id = id
        if mode is None:
            self.mode = StdArea.getAreaMode(self.id)
        else: self.mode = mode
        
class AssignChain:

    def __init__(self,area=None,id=None):
    
        if area is None:
            self.area = Area()
        else: self.area = area
        
        if id is None:
            self.id = Cui.CuiCrcEvalInt(Cui.gpc_info, self.area.id, 'object','crr_identifier')
        else: self.id = id

        self.info = self.getChainInfo()[0]
        
        if self.info[18] == []:
            Message.show(MSGR('No legs have been marked!\nMark the legs to assign before proceeding.'))
            raise KeyboardInterrupt
        
        #Check if the selected activity is an activity where FAC is not possible to run
        for i in range( len( self.info[18] ) ):
            if self.info[18][i][11]:
                Message.show(MSGR("Find Assignable Crew cannot be run on a personal activity."))
                raise Exception("Find Assignable Crew cannot be run on a personal activity.")
            
        self.numLegs = len(self.info[18])
        self.start = self.info[18][0][4]
        self.startStn = self.info[18][0][7]
        self.end = self.info[18][-1][16]
        self.endStn = self.info[18][-1][8]
        self.acTypes = self.getAircraftTypes()
        self.regions = self.getRegions()
        self.openPos = self.getOpenPos()
        self.openRanks = self.getOpenRanks()
        self.assignRank = self.openRanks[0]
        self.crewIsLate = self.info[1]
        self.volunteerType = self.info[2]
        self.checkIn = self.info[3]
        self.checkOut = self.info[4]
        self.cnxTimeBefore = self.info[18][0][5]
        self.cnxTimeAfter = self.info[18][-1][6]
        self.cnxProblem = self.info[18][-1][13]
        self.crewId = self.info[18][0][14]

        if self.info[18][0][4] <> self.info[18][-1][4]:
            self.manyDuties = True
        else: self.manyDuties = False
        #Check if the leg(s) is missing two important searc criteria
        #ac type and crew region
        if not self.regions or not self.acTypes:
            Message.show(MSGR("Find Assignable Crew can not be run on this activity."))
            raise Exception("Find Assignable Crew can not be run on this activity.")
                                                                    
    def getRuleValue(self, expr):
        return getRuleValue(expr,self.area.id, self.area.mode, self.id)

    def getOpenRanks(self):

        openRanks = []
        openPos = self.getOpenPos()
        for i in range(len(openPos)):
            if openPos[i] > 0: 
                openRanks.append(pos2func(i+1))
        #Check if the leg(s) has assigned positions.
        if openRanks == []:
            Message.show(MSGR("Leg has no assigned positions.\n\n" +\
                            "Find Assignable Crew can not be run on this activity."))
            raise Exception("Leg has no assigned positions.")
        return openRanks

    def getOpenPos(self):
        openPos = []
        for i in range(12): openPos.append(self.info[(i+6)])
        return openPos
       

    def getChainInfo(self):
        Cui.CuiSetSelectionObject(Cui.gpc_info, self.area.id, Cui.CrrMode, str(self.id))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.area.id, 'OBJECT')
        info, =  R.eval('current_context',
                        R.foreach(R.iter(MAP_TRIP_SET, where='crr_identifier='+str(self.id)),
                        MAP_CREW_IS_LATE_FOR_TRIP,                             # 1 CREW_IS_LATE
                        MAP_TRIP_VOLUNTEER_TYPE,                               # 2 VOLUNTEER_TYPE
                        MAP_TRIP_START,                                        # 3 START
                        MAP_TRIP_END,                                          # 4 END
                        MAP_TRIP_REGION,                                       # 5 REGION

                        R.first(R.Level.atom(), 'assigned_crew_position_1'),      # 6 OPEN_POS_1
                        R.first(R.Level.atom(), 'assigned_crew_position_2'),      # 7 OPEN_POS_2
                        R.first(R.Level.atom(), 'assigned_crew_position_3'),      # 8 OPEN_POS_3
                        R.first(R.Level.atom(), 'assigned_crew_position_4'),      # 9 OPEN_POS_4
                        R.first(R.Level.atom(), 'assigned_crew_position_5'),      # 10 OPEN_POS_5
                        R.first(R.Level.atom(), 'assigned_crew_position_6'),      # 11 OPEN_POS_6
                        R.first(R.Level.atom(), 'assigned_crew_position_7'),      # 12 OPEN_POS_7
                        R.first(R.Level.atom(), 'assigned_crew_position_8'),      # 13 OPEN_POS_8
                        R.first(R.Level.atom(), 'assigned_crew_position_9'),      # 14 OPEN_POS_9
                        R.first(R.Level.atom(), 'assigned_crew_position_10'),     # 15 OPEN_POS_10
                        R.first(R.Level.atom(), 'assigned_crew_position_11'),     # 16 OPEN_POS_11
                        R.first(R.Level.atom(), 'assigned_crew_position_12'),     # 17 OPEN_POS_12
                        R.foreach(R.iter(MAP_LEG_SET, where='marked'),         # 18
                                    'leg_identifier',                              # 1 ID
                                    MAP_LEG_START,                                 # 2 START
                                    MAP_LEG_END,                                   # 3 END
                                    MAP_DUTY_START,                                # 4 DUTY_START
                                    MAP_CNX_TIME_BEFORE,                           # 5 CNX_TIME_BEFORE
                                    MAP_CNX_TIME_AFTER,                            # 6 CNX_TIME_AFTER
                                    MAP_LEG_START_STN,                             # 7 START_STN
                                    MAP_LEG_END_STN,                               # 8 END_STN
                                    MAP_LEG_AC_TYPE,                               # 9 AC_TYPE
                                    MAP_LEG_IS_ACTIVE,                             # 10 IS_ACTIVE
                                    MAP_LEG_IS_PACT,                               # 11
                                    MAP_LEG_REGION,                                # 12 REGION
                                    MAP_CNX_PROBLEM,                               # 13 CNX_PROBLEM
                                    'crr_crew_id',                                 # 14 Crew id
                                    'activity_id',                                 # 15 activity id
                                    MAP_DUTY_END)))                                # 16 DUTY_END
        return info

    
#    def getChainInfo(self):
#        w = RaveWrap.RaveEvalWrap(self.area.id, Cui.CrrMode, self.id)
#        return w.dicteval(R.eval('current_context',
#                                 R.foreach(w.iter('TRIP', MAP_TRIP_SET,
#                                                  where = 'crr_identifier='+str(self.id)),
#                                           w.expr('CREW_IS_LATE', MAP_CREW_IS_LATE_FOR_TRIP),
#                                           w.expr('VOLUNTEER_TYPE', MAP_TRIP_VOLUNTEER_TYPE),
#                                           w.expr('START', MAP_TRIP_START),
#                                           w.expr('END', MAP_TRIP_END),
#                                           w.expr('OPEN_POS_1',R.first(R.Level.atom(),'assigned_crew_position_1')),
#                                           w.expr('OPEN_POS_2',R.first(R.Level.atom(),'assigned_crew_position_2')),
#                                           w.expr('OPEN_POS_3',R.first(R.Level.atom(),'assigned_crew_position_3')),
#                                           w.expr('OPEN_POS_4',R.first(R.Level.atom(),'assigned_crew_position_4')),
#                                           w.expr('OPEN_POS_5',R.first(R.Level.atom(),'assigned_crew_position_5')),
#                                           w.expr('OPEN_POS_6',R.first(R.Level.atom(),'assigned_crew_position_6')),
#                                           w.expr('OPEN_POS_7',R.first(R.Level.atom(),'assigned_crew_position_7')),
#                                           w.expr('OPEN_POS_8',R.first(R.Level.atom(),'assigned_crew_position_8')),
#                                           w.expr('OPEN_POS_9',R.first(R.Level.atom(),'assigned_crew_position_9')),
#                                           w.expr('OPEN_POS_10',R.first(R.Level.atom(),'assigned_crew_position_10')),
#                                           w.expr('OPEN_POS_11',R.first(R.Level.atom(),'assigned_crew_position_11')),
#                                           w.expr('OPEN_POS_12',R.first(R.Level.atom(),'assigned_crew_position_12')),
#                                           R.foreach(w.iter('LEGS', MAP_LEG_SET,
#                                                            where='marked'), 
#                                                     w.expr('ID','leg_identifier'),
#                                                     w.expr('START',MAP_LEG_START),
#                                                     w.expr('END',MAP_LEG_END),
#                                                     w.expr('DUTY_START',MAP_DUTY_START),
#                                                     w.expr('CNX_TIME_BEFORE',MAP_CNX_TIME_BEFORE),
#                                                     w.expr('CNX_TIME_AFTER',MAP_CNX_TIME_AFTER),
#                                                     w.expr('START_STN',MAP_LEG_START_STN),
#                                                     w.expr('END_STN',MAP_LEG_END_STN),
#                                                     w.expr('AC_TYPE',MAP_LEG_AC_TYPE),
#                                                     w.expr('IS_ACTIVE',MAP_LEG_IS_ACTIVE)))))

    def getAircraftTypes(self):
        acs = []
        for leg in self.info[18]:
            ac = leg[9]
            if leg[10] and acs.count(ac)<=0:
                acs.append(ac)
        return acs

    def getRegions(self):
        regions = []
        regions.append(self.info[5])
        return regions
    
    def __str__(self):
        strOut = "\n......<--- ASSIGN CHAIN\n"
        for k in self.__dict__:
            strOut += "......%s: %s\n" % (k, str(self.__dict__[k]))
        strOut += "......---> ASSIGN CHAIN\n"
        return strOut

#
# RULE RELAXATION TABLE
#

class RuleRelaxationTable(Etab.Etable):
    def __init__(self):
        self.path = self.getPath()
        if self.path is None:
            Message.show(MSGR('Resource not found: gpc.config.FilterAssignableRelaxationEtab'))
            raise CarmException('Resource not found: gpc.config.FilterAssignableRelaxationEtab')
        if not os.access(self.path, os.F_OK):
            Message.show(MSGR('Could not find rule relaxation etab:\n'+self.path))
            raise CarmException('Missing rule relaxation etab:'+self.path)
        Etab.Etable.__init__(self, self.path)
        
    def getPath(self):
        return Crs.CrsGetAppModuleResource("gpc",Crs.CrsSearchAppDef,"config",
                                           Crs.CrsSearchModuleDef,"FilterAssignableRelaxationEtab")

    def getOptionalRelaxationKeys(self):
        relaxList = []
        for i in range(len(self)):
            relaxKey = self.getRow(i+1)[0]
            relaxType = self.getRow(i+1)[4]
            if relaxList.count(relaxKey)<=0 and relaxType != MAP_RELAX_MANDATORY_ID \
                   and relaxType != MAP_RELAX_HIDDEN_ID:
                relaxList.append(relaxKey)
        return relaxList

    def mandatoryKey(self): 
        for i in range(len(self)):
            relaxKey = self.getRow(i+1)[0]
            relaxType = self.getRow(i+1)[4]
            if relaxType == MAP_RELAX_MANDATORY_ID: return relaxKey
        return None
    
    def getHiddenRelaxationKeys(self):
        hiddenRelaxList = []
        relaxRuleNameList = []
        for i in range(len(self)):
            relaxKey = self.getRow(i+1)[0]
            relaxType = self.getRow(i+1)[4]
            relaxRuleName = self.getRow(i+1)[2]
            if hiddenRelaxList.count(relaxKey)<=0 and relaxType == MAP_RELAX_HIDDEN_ID:
                hiddenRelaxList.append(relaxKey)
            if relaxRuleNameList.count(relaxRuleName) <= 0 and relaxType == MAP_RELAX_HIDDEN_ID:
                relaxRuleNameList.append(relaxRuleName)
        return hiddenRelaxList, relaxRuleNameList
        
class StudioRules: 
    """
       This class give the findAssignable function all the rules defined for studio.
    """
    def restoreAllStudioRules(self):
        """This function restore all the studio rules back as they were
           before FindAssignable call. 
        """
        global _studioRulesDict
        for ruleKey in _studioRulesDict.keys():
            try:
                _studioRulesDict[ruleKey][1].setswitch(_studioRulesDict[ruleKey][2])
            except:
                print "Can not restore rule %s due to not valid" % ruleKey
                continue
    def getAllTurnOffRulesBeforeFindAssignable(self, id):
        """This function collects all the rules thar are supposed to 
           be turned off before FAC is running. It stores the variable
           in a global variable _always_turned_off_rules
        """   
        #Get rules from Rave file
        for count_always_turn_off in range(1,10):
            turn_off_rule = Cui.CuiCrcEvalString(Cui.gpc_info, id, "object", "studio_fac.%%always_turned_off_rules%%(%d)" % count_always_turn_off)
            if turn_off_rule != "" and _always_turned_off_rules.count(turn_off_rule) <= 0:
                _always_turned_off_rules.append(turn_off_rule)

    def turnOffRulesBeforeFindAssignable(self):
        """This function turns off the rules that must be turned off
           before CT runs Find Assignable.
        """  
        global _studioRulesDict
        global _always_turned_off_rules         
                       
        for ruleKey in _studioRulesDict.keys():
            if ruleKey in _always_turned_off_rules:
                try:
                    _studioRulesDict[ruleKey][1].setswitch(False)
                except:
                    print "Could not turn off rule %s due to this is not a valid rule" % ruleKey
                    continue

    def getRulesThatAreFacFormDependent(self, id):
        """This function collects all rules that is FAC dependent
           Volunteer needs to turn off rules like "C/I resched is not
           allowed for day off" to become legal
        """
        global _form_dependent_turn_off_rules        
        for count_form_dependent_turn_off in range(1,10):
            form_dependent_rule = Cui.CuiCrcEvalString(Cui.gpc_info, id, "object", "studio_fac.%%form_dependent_rules%%(%d)" % count_form_dependent_turn_off)     
            if form_dependent_rule != "" and _form_dependent_turn_off_rules.count(form_dependent_rule) <= 0:
                _form_dependent_turn_off_rules.append(form_dependent_rule)
                
    def turnOffFormRules(self, candidates):
        """This function turns off the rules that is form dependent
           before CT runs Find Assignable.
        """  
        global _studioRulesDict
        global _form_dependent_turn_off_rules
        form_rule_count = 0         
        
        if candidates.volunteer.isActive:
            form_rule_count = len(_form_dependent_turn_off_rules) + 1

        for count_form_rule in range(1,form_rule_count):
            try:
                _studioRulesDict[_form_dependent_turn_off_rules[count_form_rule-1]][1].setswitch(False)
            except:
                print "Could not turn off rule %s due to this is not a valid rule" % _form_dependent_turn_off_rules[count_form_rule-1]
                continue

    def getAllLegalitySubsetRules(self, id):
        """This function collects all semi legal rules that are 
           aviable for the object(FC has different setups than CC. 
           It stores the rules in a global varable that is used 
           when turning the rules off all.
        """
        global _semi_legal_rules        
        #Get rules from RAVE
        for count_semi_legal_rules in range(1,110):
            semi_legal_rule = Cui.CuiCrcEvalString(Cui.gpc_info, id, "object", "studio_fac.%%semi_legal_rules_for_FAC%%(%d)" % count_semi_legal_rules)
            if semi_legal_rule != "" and _semi_legal_rules.count(semi_legal_rule) <= 0:
                _semi_legal_rules.append(semi_legal_rule)
                                               
    def turnOnAllLegalitySubsetRules(self):
        """This function turns off all studio rules except those that
           SAS has defined in the requirement specification for Find Assignable.
           All rules are defind in the global variable _semi_legal_rules
        """
        global _studioRulesDict
        global _semi_legal_rules        
        #Turn off the rules that are not in the semi_legal_rules list
        #Let the rules in semi_legal_rules be as they were before CT run FAC        
        for ruleKey in _studioRulesDict.keys():
            if ruleKey in _semi_legal_rules:
                continue
                #_studioRulesDict[ruleKey][1].setswitch(True)
            else:
                try:
                    _studioRulesDict[ruleKey][1].setswitch(False) 
                except:
                    print "Could not turn off rule %s due to this is not a valid rule" % ruleKey
                    continue
                  
    def getAllStudioRulesAndValues(self):  
        """ This function returns a dictonary with all the rules that are present in studio
            The key is the <modulename>.<rule_name>. The values contains the remark text,
            the rave object and the state of the rule(True/False).
            
            Example: {'rules_training_ccr.trng_initial_flight_training_performed_all': 
                      ('(CCR) OMA: New entrant CC must perform initial flight training',
                      <rule rules_training_ccr.trng_initial_flight_training_performed_all>,
                      False)}
        """
        global _studioRulesDict
        #Get all rules
        for ruleName in R.rules():
            keyName = str(ruleName)
            if not _studioRulesDict.has_key(keyName):
                _studioRulesDict[keyName] = (R.rule(keyName).remark(), R.rule(keyName), R.rule(keyName).on())
     
    def checkAllRulesAreAvailable(self):
        """This function compare the studio rules with the rules defined by the user so 
           that all rules exists.        
        """
        global _studioRulesDict
        global _semi_legal_rules
        global _always_turned_off_rules
        global _form_dependent_turn_off_rules
        
#        print len(_studioRulesDict.keys())
#        print len(_semi_legal_rules)
#        print len(_always_turned_off_rules)
        
        rules = _studioRulesDict
        ruleName = _studioRulesDict.keys()
        relaxationRuleRemarks, relaxationRuleNames = RuleRelaxationTable().getHiddenRelaxationKeys()
        
        #Test the always turned off rules so that they exist
        for rule in _always_turned_off_rules:
            if rule in ruleName:
                continue
            else:
                print "The rule name \"%s\" defined in _always_turned_off_rules does not exist in the rule name list defined in Studio." % rule
         
        for rule in _form_dependent_turn_off_rules:
            if rule in ruleName:
                continue
            else:
                print "The rule name \"%s\" defined in the _form_dependent_turn_off_rules does not exist in the rule name list in Studio." % rule
                     
        for rule in _semi_legal_rules:
            #Test if the rules in the _semi_legal_rules exist
            if rule in ruleName:
                continue
            else:
                print "The rule name \"%s\" defined in _semi_legal_rules does not exist in the rule name list defined in Studio." % rule
                
        for rule in relaxationRuleNames:
            if rule in ruleName:
                continue
            else:
                print "The rule name \"%s\" defined in the FARelaxation.etab file does not exist in the rule name list in Studio." % rule
                
        
#
# MAIN FUNCTION...
#

def findAssignableCrew(test_mode=False):

    """
    The function...
    """
    try:
        assignable = []
        endSearch = False        
        fac = AssignmentHandler()
        
        if fac.now > fac.assignChain.end:
            Message.show(MSGR('Not possible to use on historical data!'))
            return
        fac.getDataFromForm(test_mode)
        fac.activateCandidateArea()   
        
        if test_mode: return
        
        if debugOutput:
            for k in fac.flags.__dict__.keys():
                print "FindAssignableCrew.py::Flags/Options: %-25s: %s" % (k, fac.flags.__dict__[k])
                
        if fac.candidateList == []:
            Message.show(MSGR('Sorry, no candidates found...'))
            return
        elif fac.flags.checkLegality:
            if fac.assignChain.crewId in fac.candidateList:
                fac.candidateList.remove(fac.assignChain.crewId)
                
            StudioRules().turnOffFormRules(fac.candidates)
            max_semi_legal = 0
            
            # Reference: /nfs/vm/master/User_Interface/manipulate/CuiFilterAssignable.3
            assignable = Cui.CuiFilterAssignable(Cui.gpc_info,
                                                 fac.assignChain.id,
                                                 fac.candidateList,
                                                 func2cat(fac.assignChain.assignRank),
                                                 fac.assignChain.assignRank,
                                                 int(fac.form.maxHits.valof()),
                                                 fac.relaxList,
                                                 fac.flags.getFlagsToMoveAssignments(),
                                                 fac.flags.getFlagsToFilterAssignable(),
                                                 fac.now)
            #Remove all legal crew so they do not make two matches
            total_crew = len(fac.candidateList)
            for crew in assignable:
                fac.candidateList.remove(crew)
            maxHitsValue = fac.form.maxHits.getValue()
            if len(assignable) == int(maxHitsValue) > 0:
                endSearch = True
                status_message = "There were %i legal candidates found.    \n" % len(assignable)
                statusbar_message = "%i legal candidates, " % len(assignable)
            elif len(assignable) < int(maxHitsValue) > 0:
                status_message = "There were only found %i legal candidates. (Maximun hits of candidates were set to %i).\n" %(len(assignable), int(maxHitsValue))
                statusbar_message = "There were only found %i legal candidates. (Maximun hits of candidates were set to %i).\n" %(len(assignable), int(maxHitsValue))
                max_semi_legal = int(maxHitsValue) - len(assignable)
            else:
                status_message = "There were %i legal candidates found.    \n" % len(assignable)
                statusbar_message = "%i legal candidates, " % len(assignable)
                
            if not endSearch:
                #Turn off and on the rules 
                StudioRules().turnOnAllLegalitySubsetRules()
                #Get the relaxation rules from the FARelaxation.etab
                fac.relaxList.extend(RuleRelaxationTable().getHiddenRelaxationKeys()[0])
                if debugOutput:
                    print "FindAssignableCrew.py::Relaxation rules ================================="
                    for i in fac.relaxList:
                        print 'FindAssignableCrew.py::Relaxation rules ', i
                    print "FindAssignableCrew.py::Relaxation rules ================================="
                    
                # Reference: /nfs/vm/master/User_Interface/manipulate/CuiFilterAssignable.3
                semi_assignable = (Cui.CuiFilterAssignable(Cui.gpc_info,
                                                     fac.assignChain.id,
                                                     fac.candidateList,
                                                     func2cat(fac.assignChain.assignRank),
                                                     fac.assignChain.assignRank,
                                                     max_semi_legal,
                                                     fac.relaxList,
                                                     fac.flags.getFlagsToMoveAssignments(),
                                                     fac.flags.getFlagsToFilterAssignable(),
                                                     fac.now))
                
                assignable.extend(semi_assignable)
                for crew in semi_assignable:
                    fac.candidateList.remove(crew)
                #Create message
                status_message += "There were %i semi-legal candidates found.    \n" % len(semi_assignable)
                statusbar_message += "%i semi-legal candidates, " % len(semi_assignable)
                
            #If no legal or semi-legal canditaes are found. 
            #FindAssignable shows the candidates that were found
            if not assignable:
                status_message = "There were 0 legal candidates found.    \n"
                status_message += "There were 0 semi-legal candidates found.\n" 
                assignable.extend(fac.candidateList)
            else:
                assignable.extend(fac.candidateList)
        
        else:
            total_crew = len(fac.candidateList)
            assignable = fac.candidateList
            status_message = "There were %i possible candidates found. \n" % len(assignable)
            statusbar_message = "%i possible candidates found. " % len(assignable)        
        
        status_message += "There were %i crew in the selection.    \n" % total_crew
        statusbar_message += " %i crew in the selection." % total_crew                    
        if debugOutput:
            print "FindAssignableCrew.py::Cui.CuiFilterAssignable::Assignable crew list: \n", str(assignable)       
        #Zoom up the window so the user can see the first legal/semi-legal or first row in the window 
        HF.redrawAreaScrollHome(fac.candidateArea.id)
        #Cui.CuiRedrawArea(Cui.gpc_info, fac.candidateArea.id, Cui.CuiRedrawHome) ---> Not implemented yet
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   fac.candidateArea.id,
                                   Cui.CrewMode,
                                   Cui.CrewMode,
                                   assignable,
                                   Cui.CUI_DISPLAY_GIVEN_OBJECTS_ZOOM)
        
        #Show status message
        StdArea.promptPush(statusbar_message)
        Message.show(MSGR(status_message), title = "Find Assignable Result")
        
        #Set all studio rules as they were before find assignable call
        StudioRules().restoreAllStudioRules()
    except KeyboardInterrupt:
        StudioRules().restoreAllStudioRules()
    except:
        StudioRules().restoreAllStudioRules()
        traceback.print_exc()

#
# MISC FUNCTIONS
#

def getRuleValue(expr,area=None,mode=None,chainId=None):
    #w = RaveWrap.RaveEvalWrap(area, mode, chainId)
    return R.eval(expr)

def bool2str(boolVal):
    return {True:"True",False:"False"}[boolVal]


# Function for converting time to or from reference time.
# The toType variable should be set to 'UTC' or 'local'.
def timeConvert(absTime, toType='UTC'):
    func = 'station_%stime' % toType.lower()
    if TIME_IS_LOCAL.upper() == 'TRUE':
        refAP = Crs.CrsGetModuleResource('preferences', Crs.CrsSearchModuleDef, 'DstAirport')
        if not refAP or refAP == "***":
            refAP = DEFAULT_REF_AIRPORT
        return Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, 'NONE', \
                            '%s(%s, %s)' %(func, refAP, str(absTime)))
    return absTime
                                                        
