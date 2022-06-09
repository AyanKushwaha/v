#

#
"""
Implementations for Reserve- and Standby-handling
The functions are referenced in the menu_source files and
some tracking reports.

Sections:
1. Common classes and global variables
2. Private functions
3. User accessible functions

"""

import os
import tempfile
import traceback
import re

# Sys imports
import Cui
import Cfh
from AbsTime import AbsTime
from RelTime import RelTime
from AbsDate import AbsDate
import carmensystems.rave.api as R
import Errlog
import Variable as V
import modelserver as M

# User imports
import carmstd.cfhExtensions as cfhExtensions
import carmstd.rave as rave
from carmstd.parameters import parameter
import Select
import carmusr.HelperFunctions as HelperFunctions
import carmusr.tracking.TripTools as TripTools
import carmusr.Attributes as Attributes
from tm import TM
from utils.rave import RaveIterator, RaveEvaluator
import carmusr.ActivityManipulation as AM
import utils.Names as Names

WAITING_AT_AIRPORT_NUM = 0
STANDBY_AT_AIRPORT_NUM = 1
STANDBY_AT_HOME_NUM = 2

##################################################
# 3. User accessible functions
#

##################################################################
# Functions for converting marked legs to standby
#

def station_localtime(station, utc_time):
    """ mirror rave functionality """
    expr = 'station_localtime("%s", %s)' % (station, utc_time)
    return AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info,
                                         Cui.CuiNoArea,
                                         "none",
                                         expr))
    
def station_utctime_at_local_date(station, utc_time, local_tod=RelTime(0,0)):
    local_time = AbsTime(AbsDate(station_localtime(station, utc_time))) \
               + local_tod
    expr = 'station_utctime("%s", %s)' % (station, local_time)
    return AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info,
                                         Cui.CuiNoArea,
                                         "none",
                                         expr))

def station_base(station, area):
    """ mirror rave functionality """
    expr = 'fundamental.%%station2base%%("%s")' % station
    return Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", expr)

import time
    
def createSbyPact(crew_id, sby_code, start_utc, end_utc, sbyPeriod):
    station = sbyPeriod['station']
    print "  createSbyPact: %s @ %s" % (sby_code, station),
    if start_utc < sbyPeriod['cut_start_utc']:
        print " [Fix start overlap %s]" % start_utc,
        start_utc = sbyPeriod['cut_start_utc']
    if end_utc > sbyPeriod['cut_end_utc']:
        print " [Fix end overlap %s]" % end_utc,
        end_utc = sbyPeriod['cut_end_utc']
    start_lc = station_localtime(station, start_utc)
    end_lc = station_localtime(station, end_utc)
    print " (local time %s - %s)" % (start_lc, end_lc),
    if sby_code == "BL" and (end_lc - start_lc) < RelTime(24, 0):
        print "Skip: only whole-day blank-days allowed."
        return
    elif (sby_code == "W" or sby_code == "WP" or sby_code == "WO") and (end_lc - start_lc) > RelTime(5, 0):
        end_lc = start_lc + RelTime(5, 0)

    def create(overlap_flags):
        """Just used in the try-except block below."""
        Cui.CuiCreatePact(Cui.gpc_info,
                          crew_id,
                          sby_code,
                          "",
                          start_lc.getRep(),
                          end_lc.getRep(),
                          station,
                          overlap_flags |
                          #Cui.CUI_CREATE_PACT_FORCE |
                          Cui.CUI_CREATE_PACT_DONT_CONFIRM |
                          Cui.CUI_CREATE_PACT_SILENT |
                          Cui.CUI_CREATE_PACT_NO_LEGALITY |
                          Cui.CUI_CREATE_PACT_TASKTAB)
    try:
        t = time.time()
        try:
            create(0)
        except:
            print "CuiCreatePact failed, retry with cut",
            create(Cui.CUI_CREATE_PACT_REMOVE_OVERLAPPING_LEGS)
    finally:
        t = time.time() - t
        print "(time: %ss)" % t
        
class OverlapException(Exception):
    def __init__(self, *args):
        Exception.__init__(self,
            *(args or ["Function cannot be performed with overlapping legs"]))
        
class StandbyDoesNotFitException(Exception):
    def __init__(self, *args):
        Exception.__init__(self,
            *(args or ["The standby does not fit on the roster"]))

def convertToStandby(reserve=0, currentArea=Cui.CuiWhichArea):
    """
    Allows for multiple legs to be converted to standby
    """

    import carmusr.tracking.Publish as Publish
    Publish.markCancelled(currentArea)

    nowTime = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                    "None", "fundamental.%now%")
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, currentArea)
    
    markedCrew = {}
    markedLegs = Cui.CuiGetLegs(Cui.gpc_info, currentArea,"marked")
    # crewId and maincat
    for leg in markedLegs:
        legObject = HelperFunctions.LegObject(str(leg),currentArea)
        crewId, = legObject.eval("crew.%id%")
        mainFunc, = legObject.eval("crew.%main_func%")
        if not markedCrew.has_key(crewId):
            markedCrew[crewId] = mainFunc

    try:
        deassigned_legs = []
        for (crewId,mainFunc) in markedCrew.items():
            leg_ids = convertToStandbyForCrew(
                          nowTime, crewId, mainFunc, reserve, currentArea)
            deassigned_legs.extend(leg_ids)
    except OverlapException:
        traceback.print_exc()
        cfhExtensions.show("Can't convert to standby when there are overlapping legs.", "Error")
        return 1
    except StandbyDoesNotFitException:
        traceback.print_exc()
        cfhExtensions.show("There is not enough room on the roster to create the standby.", "Error")
        return 1

    # Display the deassigned legs in tripmode in the scriptbuffer.
    # Call the trp cleaner for all the deassigned legs.
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               Cui.CuiScriptBuffer,
                               Cui.CrrMode,
                               Cui.LegMode,
                               [str(leg_id) for leg_id in deassigned_legs],
                               )
    TripTools.tripClean(Cui.CuiScriptBuffer, deassigned_legs)

    return 0    
    
def convertToStandbyForCrew(nowTime=None,
                            crewId = None,
                            mainFunc=None,
                            reserve=0,
                            currentArea=Cui.CuiWhichArea):
    # Use cases:
    # Single leg -> ap sby
    # Multiple leg not whole duty -> ap sby
    # Multiple leg whole duty close to %now% -> ap sby
    # Multiple/single leg whole duty before %now% -> A or R
    # Several duties SH, loop over above
    # Several duties LH, apply scheme

    # A reserve can be created if a whole or a series of whole duties are selected

    if nowTime is None or crewId is None or mainFunc is None:
        print "STANDBY: in convertToStandbyForCrew, one argument is None" 
        return []
        
    print "STANDBY: in convertToStandbyForCrew %s" % crewId
    
    ## Analyze the situation

    print "+1+START+ Crewid", crewId
    t = time.time()
    
    # Get identifiers for marked stuff on line
    Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.CrewMode, crewId)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, currentArea, 'OBJECT')

    legs = RaveIterator(R.iter('iterators.leg_set',
                                where="marked",
                                sort_by="leg.%start_UTC%"),{
        "trip_start_utc"      : "trip.%start_utc%",         
        "trip_end_utc"        : "trip.%end_utc%",           
        "trip_num_legs"       : "trip.%num_legs%",          
        "trip_index"          : "leg.%trip_index%",         
        "trip_days"           : "trip.%days%",              
        "trip_num_duties"     : "trip.%num_duties%",        
        "duty_is_long_haul"   : "studio_process.%convert_to_standby_long_haul%",      
        "leg_identifier"      : "leg_identifier",
        "is_on_duty"          : "leg.%is_on_duty%",
        "duty_start_utc"      : "leg.%duty_start_utc%",
        "duty_end_utc"        : "leg.%duty_end_utc%",  
        "duty_num_legs"       : "duty.%num_legs%", 
        "duty_index"          : "leg.%duty_index%",    
        "start_utc"           : "leg.%start_utc%",          
        "end_utc"             : "leg.%end_utc%",            
        "start_station"       : ("leg.%start_station%","leg.%start_station%","studio_process.%replacing_standby_start_station%")[reserve],
        "arrives_at_homebase" : "leg.%arrives_at_homebase%",
        "sby_cut_start_utc"   : "studio_process.%replacing_standby_cut_start_utc%",
        "sby_cut_end_utc"     : "studio_process.%replacing_standby_cut_end_utc%",
        "any_overlap"         : "studio_overlap.%leg_overlap%",
        "full_overlap"        : "studio_overlap.%leg_entirely_overlapped%"
        }).eval("default_context")
    legdic = dict()
    for leg in legs: legdic[leg.leg_identifier] = leg
    for leg in legs:
        if leg.any_overlap:
            print "Warning: Legs overlap"
            # Check that no unselected legs overlap completely
            overlappedlegs = RaveIterator(R.iter('iterators.leg_set', where="leg.%start_UTC% >= " + str(leg.start_utc) + " and leg.%end_UTC% <= " + str(leg.end_utc)), {"leg_identifier" : "leg_identifier"}).eval("default_context")
            for overlappedleg in overlappedlegs:
                if not overlappedleg.leg_identifier in legdic:
                    raise OverlapException()
            
        leg.trip_start_utc    = AbsTime(leg.trip_start_utc)    
        leg.trip_end_utc      = AbsTime(leg.trip_end_utc)
        leg.duty_start_utc    = AbsTime(leg.duty_start_utc)
        leg.duty_end_utc      = AbsTime(leg.duty_end_utc)
        leg.start_utc         = AbsTime(leg.start_utc)
        leg.end_utc           = AbsTime(leg.end_utc)
        leg.sby_cut_start_utc = AbsTime(leg.sby_cut_start_utc)
        leg.sby_cut_end_utc   = AbsTime(leg.sby_cut_end_utc)

    #--------------------------------------------------------------------------
    # Group marked legs into sections (sbyPeriods)
    #--------------------------------------------------------------------------
    
    offDutyLegs = []
    sbyPeriods = []
    lastBlockMem = None
    start_leg_ix = 0
    while start_leg_ix < len(legs):
        blockFirstLeg = legs[start_leg_ix]
        if not blockFirstLeg.is_on_duty:
            offDutyLegs.append(blockFirstLeg.leg_identifier)
            start_leg_ix += 1
            continue
            
        if blockFirstLeg.full_overlap:
            print "Leg %s is overlapped by other legs. Will not create standby for this leg" % (start_leg_ix)
            start_leg_ix += 1
            continue
            
        print "block start at",blockFirstLeg.start_utc,"limit",blockFirstLeg.sby_cut_start_utc
        
        #
        # Check for whole trip with only longhaul duties and more than one duty
        #
        
        if blockFirstLeg.trip_index == 1 \
        and blockFirstLeg.duty_is_long_haul \
        and blockFirstLeg.trip_num_duties > 1:
            # Possibly whole longhaul trip, start scan
            blockLastLeg = blockFirstLeg
            scan_ix = start_leg_ix + 1
            while scan_ix < len(legs) \
            and legs[scan_ix].trip_start_utc == blockFirstLeg.trip_start_utc \
            and legs[scan_ix].duty_is_long_haul:
                blockLastLeg = legs[scan_ix]
                scan_ix += 1
                
            if scan_ix - start_leg_ix == blockFirstLeg.trip_num_legs:
                print "We had a complete longhaul trip",blockFirstLeg.trip_start_utc,"-",blockFirstLeg.trip_end_utc
                sbyPeriods.append({
                    'type':          "TRIP",
                    'start_utc':     blockFirstLeg.trip_start_utc,
                    'end_utc':       blockFirstLeg.trip_end_utc,
                    'cut_start_utc': blockFirstLeg.sby_cut_start_utc,
                    'cut_end_utc':   blockLastLeg.sby_cut_end_utc,
                    'station':       blockFirstLeg.start_station,
                    'longhaul':      blockFirstLeg.duty_is_long_haul,
                    'days':          blockFirstLeg.trip_days,
                    'duties':        blockFirstLeg.trip_num_duties,
                   })
                lastBlockMem = {
                    'trip_start_utc': blockFirstLeg.trip_start_utc,
                    'trip_leg':       blockLastLeg.trip_index,
                    'block_station':  blockFirstLeg.start_station,
                    }
                # Update start_leg_ix and continue to fetch next part
                start_leg_ix = scan_ix
                continue
            else:
                print "Not a complete longhaul trip, got",scan_ix-start_leg_ix,"of",blockFirstLeg.trip_num_legs

        #
        # The block wasn't a complete longhaul trip. Check for whole duty.
        #
        
        if blockFirstLeg.duty_index == 1:
            # Possibly whole duty, start scan
            blockLastLeg = blockFirstLeg
            scan_ix = start_leg_ix + 1
            while scan_ix < len(legs) \
            and legs[scan_ix].duty_start_utc == blockFirstLeg.duty_start_utc:
                blockLastLeg = legs[scan_ix]
                scan_ix += 1
                
            if scan_ix - start_leg_ix == blockFirstLeg.duty_num_legs:
                print "We had a complete duty",blockFirstLeg.duty_start_utc,"-",blockFirstLeg.duty_end_utc
                
                # If duty blocks and or part blocks are connected,
                # they shall have same station
                if lastBlockMem is not None \
                and blockFirstLeg.trip_start_utc == lastBlockMem['trip_start_utc'] \
                and blockFirstLeg.trip_index == lastBlockMem['trip_leg'] + 1:
                    station = lastBlockMem['block_station']
                else:
                    station = blockFirstLeg.start_station

                # check overnight, not ends at homebase
                overnight = (not blockLastLeg.arrives_at_homebase)
                sbyPeriods.append({
                    'type':          "DUTY",
                    'start_utc':     blockFirstLeg.duty_start_utc,
                    'end_utc':       blockFirstLeg.duty_end_utc,
                    'cut_start_utc': blockFirstLeg.sby_cut_start_utc,
                    'cut_end_utc':   blockLastLeg.sby_cut_end_utc,
                    'station':       station,
                    'longhaul':      overnight,
                    })
                lastBlockMem = {
                    'trip_start_utc': blockFirstLeg.trip_start_utc,
                    'trip_leg':       blockLastLeg.trip_index,
                    'block_station':  station,
                    }
                # Update start_leg_ix and continue to fetch next part
                start_leg_ix = scan_ix
                continue
            else:
                print "Not a complete duty, got",scan_ix-start_leg_ix,"of",blockFirstLeg.duty_num_legs

        #
        # The block is not a complete longhaul trip, nor is it a whole duty.
        # It must be a part of a duty.
        #
        
        blockLastLeg = blockFirstLeg
        scan_ix = start_leg_ix + 1
        # Break on new duty and on other activities not removed in duty
        while scan_ix < len(legs) \
        and legs[scan_ix].duty_start_utc == blockFirstLeg.duty_start_utc \
        and legs[scan_ix].duty_index <= blockLastLeg.duty_index + 1:
            blockLastLeg = legs[scan_ix]
            scan_ix += 1            
            
        # Set start time; if at start of duty, check-in is to be included
        if blockFirstLeg.duty_index == 1:
            print "  Start is on first leg, duty_start_utc",blockFirstLeg.duty_start_utc
            part_start_utc = blockFirstLeg.duty_start_utc
        else:
            print "  Start is not on first leg, start_utc",blockFirstLeg.start_utc
            part_start_utc = blockFirstLeg.start_utc

        # Set end time; if at end of duty, check-out is to be included
        if blockLastLeg.duty_index == blockFirstLeg.duty_num_legs:
            print "  End is on last leg, duty_end_utc",blockLastLeg.duty_end_utc
            part_end_utc = blockLastLeg.duty_end_utc
        else:
            print "  not end on last leg, end_utc", blockLastLeg.end_utc
            part_end_utc = blockLastLeg.end_utc
        
        # If duty blocks and or part blocks are connected,
        # they shall have same station
        if lastBlockMem is not None \
        and blockFirstLeg.trip_start_utc == lastBlockMem['trip_start_utc'] \
        and blockFirstLeg.trip_index == lastBlockMem['trip_leg'] + 1:
            part_start_station = lastBlockMem['block_station']
        else:
            part_start_station = blockFirstLeg.start_station
            
        print "We had a part of a duty,",scan_ix-start_leg_ix,"legs",part_start_utc,part_end_utc

        # If last in duty and not at homebase means overnightable
        overnight = (not blockLastLeg.arrives_at_homebase) and \
                    blockLastLeg.duty_num_legs == blockLastLeg.duty_index
                    
        sbyPeriods.append({
            'type':          "PART",
            'start_utc':     part_start_utc,
            'end_utc':       part_end_utc,
            'cut_start_utc': blockFirstLeg.sby_cut_start_utc,
            'cut_end_utc':   blockLastLeg.sby_cut_end_utc,
            'station':       part_start_station,
            'longhaul':      overnight,
            })
        lastBlockMem = {
            'trip_start_utc': blockFirstLeg.trip_start_utc,
            'trip_leg':       blockLastLeg.trip_index,
            'block_station':  part_start_station,
            }
                        
        # Update start_leg_ix and continue to fetch next part
        start_leg_ix = scan_ix
        
    print "+2+EVALUATED+", time.time() - t
   
    # -------------------------------------------------------------------------
    # Now the sbyPeriods are calculated, so we know where to build sby:s
    # -------------------------------------------------------------------------
    
    if not sbyPeriods:
        if len(legs) == 1 and legs[0].full_overlap:
            raise OverlapException() # Trying to convert single overlapping leg to standby
        return []
        
    # Remove all legs to be converted, preparing for standby assignment.
    
    HelperFunctions.unmarkLegs(currentArea, offDutyLegs)
    leg_ids = []
    flags = 0
    Cui.CuiRemoveAssignments(Cui.gpc_info, currentArea, crewId, 0, leg_ids)
    HelperFunctions.markLegs(currentArea, offDutyLegs)
        
    print "+3+REMOVED+", time.time() - t

    # Each sbyPeriod contains a standby period.
    # The periods are "clean" - no overlapping activity
    
    # Determines if the first standby for this crew shall be an airport standby.
    standby_at_airport = (reserve == STANDBY_AT_AIRPORT_NUM)
    waiting_at_airport = (reserve == WAITING_AT_AIRPORT_NUM)

    for sbyPeriod in sbyPeriods:
        print "-------------------", sbyPeriod['type']
        
        if sbyPeriod['type'] == "TRIP" and sbyPeriod['duties'] > 1:
            # Create standby pacts for this long haul trip
            #   first day:
            #     BL-day
            #   days between first and last:
            #     RC 06-16 local time
            #   last day, cabin crew:
            #     RC 06-16 local time
            #   last day, flight crew:
            #     RC 04-14 local time, cut at original trip end
            
            print "LONG HAUL, DUTIES =",sbyPeriod['duties']

            local_date_utc = station_utctime_at_local_date(
               sbyPeriod['station'], sbyPeriod['start_utc'])
            next_local_date_utc = local_date_utc + RelTime(24, 0)
               
            createSbyPact(crewId,
                          "BL",
                          local_date_utc,
                          next_local_date_utc,
                          sbyPeriod)
                        
            for day in range(1, sbyPeriod['days']-1):
                local_date_utc += RelTime(24, 0)
                createSbyPact(crewId,
                              "RC",
                              local_date_utc + RelTime(6, 0),
                              local_date_utc + RelTime(16, 0),
                              sbyPeriod)
                            
            local_date_utc += RelTime(24, 0)                       
            if mainFunc == "F":
                start_utc = local_date_utc + RelTime(4, 0)
                end_utc = min(local_date_utc + RelTime(14, 0), 
                              sbyPeriod['end_utc'])
            else:
                start_utc = local_date_utc + RelTime(6,0)
                end_utc = local_date_utc + RelTime(16, 0)
            createSbyPact(crewId,
                          "RC",
                          start_utc,
                          end_utc,
                          sbyPeriod)
        else:          
            print "(duty or trip or part of duty)"
            # Whole duties or one duty trips, This can be converted to reserves

            start_utc = sbyPeriod['start_utc']
            localTransport = RelTime(0, 0)
            if standby_at_airport:
                sby_code = ("AC","AO")[bool(sbyPeriod['longhaul'])]
                standby_at_airport = False
            elif waiting_at_airport:
                sby_code = ("WP","WO")[bool(sbyPeriod['longhaul'])]
                waiting_at_airport = False
            else:
                # The below must be calculated at this point, since the station
                # might have switched since the original marked-legs evaluation.
                Cui.CuiSetSelectionObject(
                    Cui.gpc_info, currentArea, Cui.CrewMode, str(crewId))
                homebase = Cui.CuiCrcEvalString(Cui.gpc_info, currentArea,
                              "Object", 'crew.%%base_at_date%%(%s)' % start_utc)
                is_hotel = (station_base(sbyPeriod['station'], currentArea) != homebase)
                sby_code = ("RC","HC")[is_hotel]
                localTransport = RelTime(Cui.CuiCrcEval(Cui.gpc_info, currentArea, "Object",
                                     'standby.%%local_transport_time_func%%("%s",%s,%s)' \
                                     % (sbyPeriod['station'], start_utc,sbyPeriod['longhaul'])))
                print "Start @ %s, local transport time is %s" % (start_utc, localTransport)
                
            
            if sbyPeriod['cut_end_utc'] - sbyPeriod['cut_start_utc'] <= localTransport:
                raise StandbyDoesNotFitException()
            
            start_utc -= localTransport
            
            if sbyPeriod['end_utc'] <= start_utc:
                raise OverlapException() # Could happen if duty was moved from current leg
            
            createSbyPact(crewId,
                          sby_code,
                          start_utc,
                          sbyPeriod['end_utc'],
                          sbyPeriod)

    print "+4+CREATED", time.time() - t
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, [crewId])
    Cui.CuiUpdateLevelsAccordingToRaveAreaId(Cui.gpc_info, Cui.CuiScriptBuffer)
    Cui.CuiSyncModels(Cui.gpc_info)
    print "+5+SYNCED", time.time() - t, "Done."
    return leg_ids


##################################################################
# Class for handling standbys
#

class StandbyHandler:
    """
    This class handles the usage of standbys. Given a list of standby where
    each standby has a list of production which is to be assigned over it,
    there is functionality for collecting Callout and Local Transport times
    and then cutting the standby to a correct size.
    """
    
    def __init__(self, to_area=None, dstChain=None):
        self.to_area = to_area
        self.dstChain = dstChain
        self.__replacementMapping = {}

    ##
    ## Public members
    ##

    class Standby:
        """
        Standby structure. Contains all the necessary information regarding
        the standbys needed to be able to cut it
        """
        def __init__(self, startTime=None, startUtc=None, endTime=None, endUtc=None,
                     isAirportStandby=False, isCancelStandby=False, defaultCallout=None,
                     defaultTransport=None, standbyCrew=None,
                     airport=None, code=None, leg_id=None):
            self.startTime = startTime
            self.endTime = endTime
            self.isAirportStandby = isAirportStandby
            self.isCancelStandby = isCancelStandby
            self.defaultCallout = defaultCallout
            self.defaultTransport = defaultTransport
            self.crew = standbyCrew
            self.airport = airport
            self.code = code
            self.startUtc = startUtc
            self.endUtc = endUtc
            self.leg_id = leg_id

        def __hash__(self):
            hashString = str(self.startTime) + \
                         str(self.endTime) + \
                         str(self.isAirportStandby) + \
                         str(self.defaultCallout) + \
                         str(self.defaultCallout) + \
                         str(self.defaultTransport) +\
                         str(self.crew) + \
                         str(self.airport)+\
                         str(self.code)
            return hashString.__hash__()
        
        def __eq__(self, other):
            return self.startTime == other.startTime and \
                   self.endTime == other.endTime and \
                   self.isAirportStandby == other.isAirportStandby and \
                   self.defaultCallout == other.defaultCallout and \
                   self.defaultTransport == other.defaultTransport and \
                   self.crew == other.crew and \
                   self.airport == other.airport and \
                   self.code == other.code
    #end Standby class

    class Production:
        """
        Production structure. This represents one element (leg) in the
        production that is to replace a standby.
        """
        def __init__(self,
                     startTime=None,
                     startUtc=None,
                     endTime=None,
                     endUtc=None,
                     isLastInTrip=False,
                     crew_id=None,
                     check_in_reltime=None,
                     scheduled_start = None):
            
            self.startTime = startTime
            self.endTime = endTime
            self.isLastInTrip = isLastInTrip
            self.startUtc = startUtc
            self.endUtc = endUtc
            self.crew_id = crew_id
            self.check_in_reltime = check_in_reltime
            self.scheduled_start = scheduled_start
    #end Production class

    def addToReplacementMap(self, standby, production):
        try:
            self.__replacementMapping[standby].append(production)
        except KeyError:
            self.__replacementMapping[standby] = [production]

    ##
    ##  Private members
    ##
    
    class StandbyForm(Cfh.Box):
        """
        The form is used when assigning production to standby. The user is
        prompted for callout time and local transport time
        """
        class CfhCheckString(Cfh.String):
            def __init__(self, *args):
                Cfh.String.__init__(self, *args)
                self._check_methods = []
            def register_check(self,check_func, arg=None):
                if check_func not in self._check_methods:
                    self._check_methods.append([check_func, arg])
                    
            def check(self,text):
                message = Cfh.String.check(self, text)
                if message:
                    return message
                for func,arg in self._check_methods:
                    if arg:
                        message = func(arg)
                    else:
                        message = func()
                    if message:
                        return message
                return None
            
        class CfhCheckDone(Cfh.Done):
            def __init__(self, *args):
                Cfh.Done.__init__(self, *args)
                self._check_methods = []
            def register_check(self,check_func, arg=None):
                if check_func not in self._check_methods:
                    self._check_methods.append([check_func, arg])

            def action(self):
                message = ""
                for func,arg in self._check_methods:
                    if arg:
                        message = func(arg)
                    else:
                        message = func()
                    if message:
                        break    
                else: 
                    Cfh.Done.action(self)
                        
        def __init__(self, check_in_start, sby_start,  *args):
            Cfh.Box.__init__(self, *args)
            self.first_sby_start = Cfh.String(self, "SBY_START",20,sby_start.ddmonyyyy())
            self.first_sby_start.setEditable(0)
            self.first_sby_start.setStyle(Cfh.CfhSLabelNormal)
            
            self.check_in_string = Cfh.String(self, "CHECK_IN",20,check_in_start.ddmonyyyy())
            self.check_in_string.setEditable(0)
            self.check_in_string.setStyle(Cfh.CfhSLabelNormal)

            self.calloutTime_string = Cfh.String(self, "MIN_CALLOUT",20,)
            self.calloutTime_string.setEditable(0)
            self.calloutTime_string.setStyle(Cfh.CfhSLabelNormal)
            # starttimes!
            self.check_in_start = check_in_start
            self.sby_start = sby_start
            self.prod_start_utc = None
            # Alert time
            self.now, = R.eval("fundamental.%now%")
            self.now = AbsTime(self.now)
            self.alertTime = self.CfhCheckString(self, "ALERT_TIME", 20, self.now.ddmonyyyy())
            self.alertTime.setMandatory(1)
            self.alertTime.register_check(self.alert_time_check)
            # Transport time
            self.local_transport = self.CfhCheckString(self, "LOCALTRANSPORT", 5, "01:00")
            self.old_transport_time = RelTime("01:00")
            self.local_transport.setMandatory(1)
            self.local_transport.register_check(self.transport_check) 
            #OK and CANCEL buttons
            self.ok = self.CfhCheckDone(self, "B_OK")
            self.ok.register_check(self.check_ok)
            
            self.cancel = Cfh.Cancel(self, "B_CANCEL")
            self.warning = Cfh.String(self, "WARNING",80, "")
            self.warning.setEditable(0)
            self.warning.setStyle(Cfh.CfhSLabelNormal)
            # The form layout
            form_layout ="""
FORM;SBY_CALLOUT_FORM;Standby Callout Form
GROUP
COLUMN;15
LABEL;Standby start UTC:
COLUMN;
FIELD;SBY_START;``
GROUP
COLUMN;15
LABEL;Callout UTC:
COLUMN;
FIELD;MIN_CALLOUT;``
GROUP
COLUMN;15
LABEL;Flight check-in UTC:
COLUMN;
FIELD;CHECK_IN;``
GROUP
COLUMN;15
FIELD;ALERT_TIME;Alert time UTC:
FIELD;LOCALTRANSPORT;Local transport time:
GROUP
COLUMN;20
FIELD;WARNING;``
EMPTY
EMPTY
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""
            standby_form_file = tempfile.mktemp()
            f = open(standby_form_file, "w")
            f.write(form_layout)
            f.close()
            self.load(standby_form_file)
            os.unlink(standby_form_file)
            
        def transport_check(self):
            try:
                transport = RelTime(self.local_transport.getValue())
            except:
                return "Enter transport as valid reltime, e.g. 01:00"
            if transport < RelTime('00:00'):
                return "Please enter a positive reltime"
            callout_time = AbsTime(self.calloutTime_string.getValue())
            alertTime = AbsTime(self.alertTime.getValue())
            check_in_time = AbsTime(self.check_in_start.getValue())
            
            transport_diff = transport - self.old_transport_time
            if callout_time == alertTime:
                alertTime -= transport_diff
                self.alertTime.assign(str(alertTime))
            self.warning.assign("")
            callout_time -= transport_diff
            
            if callout_time <= self.now:
                callout_time = self.now
                transport = max(RelTime('00:00'),(check_in_time-callout_time))
                self.local_transport.assign(str(transport))
                if alertTime <= self.now:
                    alertTime = self.now
                    self.alertTime.assign(str(alertTime))
            self.calloutTime_string.assign(str(callout_time))
            self.old_transport_time = transport
            return ""
        
        def alert_time_check(self):
            try:
                time = AbsTime(self.alertTime.getValue())
                self.warning.assign("")
                if time <= self.now:
                    time = self.now
                    self.alertTime.assign(str(time))
                    self.warning.assign("Alert time set to NOW time.")
            except:
                return "Enter Alert Time as valid abstime, e.g. 01Jan2007 10:00"
            if self.prod_start_utc:
                if time > self.prod_start_utc:
                    return "Not possible to set alert after production's actual starttime!"
            return ""
        
        def check_ok(self):
            """
            First errors, then warnings!!
            """
            self.warning.assign("")
            message = ""
            time = AbsTime(self.alertTime.getValue())
            if time > (self.check_in_start-RelTime(self.local_transport.getValue())):
               self.warning.assign("Alert time after default,\n minimum callout time.")
            return message
        
        def setDefaultValues(self, callout, transport, prod_start_utc):
            self.alertTime.assign(str(callout))
            self.calloutTime_string.assign(str(callout))
            self.local_transport.assign(str(transport))
            self.old_transport_time = transport
            if callout and transport:
                self.alertTime.check(str(callout))
                self.local_transport.check(str(transport))
            self.prod_start_utc = prod_start_utc
         
        def getValues(self):
            """
            Function returning the values set in the form
            """
            calloutTime = AbsTime(self.calloutTime_string.valof() or 0)
            alert = AbsTime(self.alertTime.valof() or 0)
            transport = RelTime(self.local_transport.valof() or 0)
            return (alert,transport,calloutTime)

    def saveAlertTime(self, sby, alertTime, si, sby_exists):
        if sby_exists:
            legObject = HelperFunctions.LegObject(str(sby.leg_id), self.to_area)
            hb_st_date_utc, = legObject.eval("crew.%utc_time%(leg.%start_date%)")            
        else:
            expr = 'leg.%%start_day_hb_utc%%("%s",%s)' % (sby.airport, sby.startUtc)
            hb_st_date_utc = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info,Cui.CuiNoArea,"none",expr))

        crewRef = TM.crew.getOrCreateRef((sby.crew,))
        key = (crewRef, hb_st_date_utc)
        mod = None
        try:
            row = TM.alert_time_exception.create(key)
            mod = "create"
        except M.EntityError:
            row = TM.alert_time_exception[key]
            if str(alertTime) != str(row.alerttime) \
            or (si or "") != (row.si or ""):
                mod = "update"
        if mod:
            print "saveAlertTime:",mod,"alert time exception @",alertTime
            row.alerttime = AbsTime(alertTime)
            row.si = si
            Cui.CuiReloadTable("alert_time_exception", 1)
        
    def removeAlertTime(self, sby, sby_exists):
        if sby_exists:
            legObject = HelperFunctions.LegObject(str(sby.leg_id), self.to_area)
            hb_st_date_utc, = legObject.eval("crew.%utc_time%(leg.%start_date%)")            
        else:
            expr = 'leg.%%start_day_hb_utc%%("%s",%s)' % (sby.airport, sby.startUtc)
            hb_st_date_utc = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info,Cui.CuiNoArea,"none",expr))

        crewRef = TM.crew.getOrCreateRef((sby.crew,))
        key = (crewRef, hb_st_date_utc)
        try:
            row = TM.alert_time_exception[key].remove()
            print "removeAlertTime: removed alert time exception @",row.alerttime
            Cui.CuiReloadTable("alert_time_exception", 1)
        except M.EntityNotFoundError:
            pass

    def storeSby(self, standby):
        """
        Store standby.start, standby.end, crewId if it does not exist.
        Otherwise ignore
        """
        start_time = standby.startTime or standby.startUtc
        end_time = standby.endTime or standby.endUtc
        searchCriteria = "(&(crew.id=%s)(sby_start<=%s)(sby_end>=%s))" \
                         %(standby.crew, start_time, end_time)
        for entryFound in  TM.published_standbys.search(searchCriteria):
            return
        
        crewRef = TM.crew.getOrCreateRef((standby.crew,))
        key = (crewRef, start_time, end_time)
        try:
            TM.published_standbys.create(key)
        except M.EntityError:
            pass

    def sortfunc(self, standby1, standby2):
        try:
            return int(standby1.startTime - standby2.startTime)
        except:
            return int(standby1.startUtc - standby2.startUtc)

    def handleStandby(self):

        standbyListSorted = self.__replacementMapping.keys()
        standbyListSorted.sort(self.sortfunc)
        if len(standbyListSorted) == 0:
            return 0

        sby = standbyListSorted[0]
        prd = self.__replacementMapping[sby][0]

        check_in_time, activity_id = self.get_first_prod_leg_check_in(sby, prd)

        last_sby = standbyListSorted[-1]
        last_prd = self.__replacementMapping[last_sby][-1]
 
        prodStart = prd.scheduled_start - check_in_time
        min_callout_time = prodStart - sby.defaultTransport
                
        now_time = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info,
                                                 Cui.CuiNoArea,
                                                 "none",
                                                 "fundamental.%now%"))
        # No production assigned after NOW time.
        if now_time > prd.startUtc:
            cfhExtensions.show("Cannot assign leg with start time earlier than NOW time.")
            return 1
            
        # Callout cannot be before now,
        # unless the called-out-to leg actual start is before now. 
        max_callout_time = min(max(min_callout_time, now_time),
                               prd.startUtc)
        
        # If actual leg start time is before the standby, it's not a callout.
        if prd.startUtc <= sby.startUtc:
            self.remove_sby_pacts(sby, last_sby)
            return 0

        sby_dialog = self.StandbyForm(prodStart, sby.startUtc, "Standby Form")
        sby_dialog.setDefaultValues(max_callout_time,
                                    sby.defaultTransport,
                                    prd.startUtc )
        sby_dialog.show(1)
        if sby_dialog.loop() == Cfh.CfhOk:
            (alertTime, transport_time, calloutTime) = sby_dialog.getValues()
        else:
            return 1

        # Set 'callout' attribute on standby leg
        si = "Created by %s at %s" % (Names.username(), AbsTime(*time.gmtime()[:5]))
        Attributes.SetCrewActivityAttr(sby.crew,
                                       sby.startUtc,
                                       sby.code,
                                       "CALLOUT",
                                       rel=transport_time,
                                       si=si)

        if calloutTime <= sby.startUtc:
            # Save one minute for duty points calculations
            print "handleStandby: callout before sby start; keep one minute"
            calloutTime = sby.startUtc + RelTime('00:01')

        sby_exists = self.update_first_sby(sby, calloutTime)
        try:
            if alertTime and alertTime != calloutTime:
                # Save standby callout alert time.
                self.saveAlertTime(sby, alertTime, si, sby_exists)
            else:
                # If there is an alert_time_exception, remove it.
                self.removeAlertTime(sby, sby_exists)
        except Exception, err:
            Errlog.log("Standby.py::handleStandby: alert_time_exception error:\n%s" % err)
        
        for sby in standbyListSorted:
            self.storeSby(sby)
        return 0
        
    def update_first_sby(self, sby, callout_time):
        create_msg = self.create_sby_pact(sby, sby.startUtc, callout_time)
        if create_msg is None:
            print "update_first_sby: created new",sby.code,sby.startUtc,"-",callout_time
            return False
            
        # Could not create sby - assume it's because it already exists.
        # This is a normal case: end time was adjusted by d&d functionality.
        try:
            Cui.CuiSetSelectionObject(Cui.gpc_info,
                                      self.to_area,
                                      Cui.LegMode,
                                      str(sby.leg_id))
            (start_date, start_time) = sby.startUtc.ddmonyyyy().split()
            start_time = start_time.replace(":","")
            (end_date, end_time) = callout_time.ddmonyyyy().split()
            end_time = end_time.replace(":","")
            Cui.CuiUpdateTaskLeg(
                {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
                {'FORM':'TASK_LEG','TASK_CODE_STRICT': sby.code},
                {'FORM':'TASK_LEG','LOCATION': sby.airport},
                {'FORM':'TASK_LEG','START_DATE': start_date},
                {'FORM':'TASK_LEG','END_DATE': end_date},
                {'FORM':'TASK_LEG','DEPARTURE_TIME': start_time},
                {'FORM':'TASK_LEG','ARRIVAL_TIME': end_time},
                {'FORM':'TASK_LEG','OK': ''},
                Cui.gpc_info,
                self.to_area,
                "object",
                Cui.CUI_UPDATE_TASK_RECALC_TRIP |\
                Cui.CUI_UPDATE_TASK_SILENT |\
                Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK |\
                Cui.CUI_UPDATE_TASK_TASKTAB)
                
            print "update_first_sby: updated",sby.code,sby.startUtc,"-",callout_time
            return True
        except:
            print "update_first_sby, create_sby_pact() failed:", create_msg
            print "update_first_sby: failed to update standby leg"
            raise
            
            
    def create_sby_pact(self, sby, start_time_utc, end_time_utc):
        try:
            Cui.CuiCreatePact(Cui.gpc_info,
                              sby.crew,
                              sby.code,
                              '',
                              station_localtime(sby.airport,start_time_utc),
                              station_localtime(sby.airport,end_time_utc),
                              sby.airport,
                              Cui.CUI_CREATE_PACT_DONT_CONFIRM|\
                              Cui.CUI_CREATE_PACT_SILENT|\
                              Cui.CUI_CREATE_PACT_NO_LEGALITY)
            return None
        except Exception, err:
            return err

    def create_trailing_pact(self, added_trip, max_wait):
        """
        Waiting at Airport type W is to be created and assigned after standby call-out if certain criteria are met.
        This function only handles certain situations that are not handled in DragDrop::postFunction
           e.g. where the flight duty ends after the original standby ends.
        The function creates a private activity of type Waiting at Airport with code W
        if the following conditions are met:
            - if the added production is 6 hours or less
            - if production takes place on days with standby and overlaps with it.
            - if following by a freeday at least 2 hours between production end and freeday start is required
        The return value 0 (zero) is used for consistency with the other calls in DragDrop::postFunction.

        Note: as of Jira SKCMS-2136 it was decided to bring back A category codes, i.e. Standby at airport.
        For certain conditions A/AC/AO can be used instead of W for waiting. Kept the old comment for historical reasons.

        The main decider if A or W can be used is:
            * waiting time is just allowed to be assigned on the day of operation
            * airport standby can be assigned in Tracking but not on the day of operation


        """

        # Waiting is not assigned if max_wait is zero e.g. QA or there the trip is empty
        if max_wait <= RelTime(0, 0) or len(added_trip) <= 0:
            return 0

        trip_end = added_trip[-1].end or added_trip[-1].leg_start
        trip_end_date = trip_end.day_floor()
        added_legs_last_day = [al for al in added_trip if al.leg_end.day_floor() == trip_end_date]
        last_prd_dur_ci_co = added_legs_last_day[-1].leg_co - added_legs_last_day[0].leg_ci

        # Waiting is assigned only when production is 6hrs or less
        if last_prd_dur_ci_co > RelTime(6, 0):
            return 0

        standbyListSorted = self.__replacementMapping.keys()
        standbyListSorted.sort(self.sortfunc)
        if len(standbyListSorted) == 0:
            return 0
        # Get the standby(s) on the day of the last trip
        sby_last_day = [sb for sb in standbyListSorted if sb.endUtc.day_floor() == trip_end_date]

        # Return if there isn't any standby on the last day of the trip
        if len(sby_last_day) < 1:
            return 0

        # Do not assign trailing W for call-out on cancellation standby or existing waiting time
        if sby_last_day[-1].isAirportStandby or sby_last_day[-1].isCancelStandby:
            return 0

        sby = sby_last_day[-1]
        trip_end_loc = station_localtime(sby.airport, trip_end)
        trip_end_loc_date = trip_end_loc.day_floor()
        sby_end_loc = station_localtime(sby.airport, sby.endUtc)
        sby_end_loc_date = sby_end_loc.day_floor()
        sby_end_utc = sby.endUtc
        sby_two_days_after = sby_end_utc.day_ceil() + RelTime(24, 0)
        w_start_loc = trip_end_loc
        w_end_latest = sby_end_loc_date + RelTime(23, 59)
        w_end_loc = min(w_start_loc + max_wait, w_end_latest)
        w_dur = w_end_loc - w_start_loc

        # Waiting at Airport (W) is not assigned if:
        #  - the trip ends on a date later than the date of the standby/standby block end.
        #  - or its duration is less than 5 minutes
        if trip_end_loc_date > sby_end_loc_date or w_dur < RelTime(0, 5):
            return 0

        last_added_leg_end = added_trip[-1].leg_end

        Cui.CuiSetSelectionObject(Cui.gpc_info, self.to_area, Cui.CrewMode, self.dstChain)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.to_area, "object")
        act_after_sby = RaveIterator(RaveIterator.iter('iterators.leg_set',
                        where=('leg.%%start_utc%%>=%s' % last_added_leg_end, 'leg.%%start_utc%%<%s' % sby_two_days_after),
                        sort_by='leg.%start_utc%'), {'is_freeday':'leg.%is_freeday%',
                                                     'start_utc':'leg.%start_utc%',
                                                     'activity_id':'leg.%activity_id%',
                                                     'is_flight_duty':'leg.%is_flight_duty%',
                                                     'is_waiting':'leg.%is_waiting_at_airport%'}).eval('default_context')


        # Do not assign trailing A if there is an overlap with existing assignment
        if len(act_after_sby) > 0 and w_end_loc > station_localtime(sby.airport, act_after_sby[0].start_utc):
            return 0

        has_waiting_already = any([act.is_waiting for act in act_after_sby])
        # Return if W is already assigned by DragDrop::postFunction.
        # Do not assign W after call-out production that ends less than two hours before a day off.
        if len(act_after_sby) > 0 and (has_waiting_already or (act_after_sby[0].is_freeday and act_after_sby[0].start_utc - added_legs_last_day[-1].leg_co < RelTime(2, 0))):
            return 0

        print "Standby::create_trailing_pact Assignment of Airport Standby"
        try:
            Cui.CuiCreatePact(Cui.gpc_info,
                              sby.crew,
                              'A',
                              '',
                              w_start_loc,
                              w_end_loc,
                              sby.airport,
                              Cui.CUI_CREATE_PACT_DONT_CONFIRM|\
                              Cui.CUI_CREATE_PACT_SILENT|\
                              Cui.CUI_CREATE_PACT_NO_LEGALITY)
            return 0
        except Exception, err:
            return err

    def get_first_prod_leg_check_in(self, sby, prd):
        
        check_in_time = activity_id = None
        
        # Select the destination roster as default context
        Cui.CuiSetSelectionObject(Cui.gpc_info, self.to_area, Cui.CrewMode, self.dstChain)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.to_area, "object")
        trip = RaveIterator(RaveIterator.iter('iterators.leg_set',
                                              where=('leg.%%start_utc%%=%s'%prd.startUtc,
                                                     'leg.%%end_utc%%=%s'%prd.endUtc),
                                              sort_by='leg.%start_utc%'),
                            {'check_in':'leg.%check_in%',
                             'activity_id':'leg.%activity_id%'}
                            ).eval('default_context')
        if len(trip)>0:
            check_in_time = trip[0].check_in
            activity_id = trip[0].activity_id
        
        return (check_in_time or RelTime(0, 0),
                activity_id or "")
    
    def remove_sby_pacts(self, first_sby, last_sby):
        # Note: if there is any CALLOUT attribute on the removed standby(s),
        #   they will be handled (removed/modified) a save.
        #   See carmusr.tracking.FileHandlingExt::preSaveProc() for details.
        Cui.CuiSetSelectionObject(Cui.gpc_info, self.to_area, Cui.CrewMode, self.dstChain)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.to_area, "object")
        sbys = RaveIterator(RaveIterator.iter('iterators.leg_set',
                                              where=('leg.%is_standby%=True',
                                                     'leg.%%start_utc%%>=%s'%first_sby.startUtc,
                                                     'leg.%%end_utc%%<=%s'%last_sby.endUtc),
                                              sort_by='leg.%start_utc%'),
                            {'start_hb':'leg.%start_hb%',
                             'end_hb':'leg.%end_hb%',
                             'crew_id':'crew.%id%'
                             }
                            ).eval('default_context')
        for sby in sbys:
            try:
                AM.deleteActivityInPeriod(sby.crew_id, sby.start_hb, sby.end_hb, area=self.to_area)
            except Exception, err:
                Errlog.log("Standby.py::%s"%err)
                pass
         
class RestoreInformedStandby:
    
    def __init__(self, *args):
        self.pointedSbyInfo = {}
        
    def restoreInformedStandby(self):
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        
        # We assume the current leg is a standby, that has been verified as a
        # standby callout (standby.%can_restore_standby% is True). Get rave data.
        
        self.getPointedSbyInfo(area)

        # Clear the activity "CALLOUT" attribute. Unless the restore is marked 
        # as do-not-publish at save time, the attribute itself will be removed
        # at that point. See Publish::publishPreSave for details.

        Attributes.SetCrewActivityAttr(self.crew_id,
                                       self.sby_start_utc,
                                       self.sby_task_code,
                                       "CALLOUT",
                                       refresh=False,
                                       rel=None)
        Cui.CuiReloadTable("crew_activity_attr")

        # If there is an alert_time_exception, remove it.

        try:
            key = (TM.crew[self.crew_id], self.sby_start_day_hb_utc_time)
            TM.alert_time_exception[key].remove()
        except:
            pass
            
        # Trick: Temporarily change the task code to "IL", to get a trip break.
        # That way, CuiDeassignCrrs can be used to remove the callout part only.
         
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(self.sby_leg_identifier))
        Cui.CuiUpdateTaskLeg(
            {'FORM':'TASK_LEG','TASK_CODE_STRICT': "IL"},
            {'FORM':'TASK_LEG','OK': ''},
            Cui.gpc_info,
            area,
            "object",
            Cui.CUI_UPDATE_TASK_RECALC_TRIP
            | Cui.CUI_UPDATE_TASK_SILENT
            | Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK
            | Cui.CUI_UPDATE_TASK_TASKTAB)
            
        # Now, the leg after the standby starts a separate trip which consists
        # of the legs we want to remove. Note that by using CuiDeassignCrr, the
        # legs will be kept together in one Trip window object; if the legs are
        # removed as legs, ther will be one separate open time trip per leg.
        
        if self.callout_leg_identifier:
            Cui.CuiUnmarkAll(Cui.gpc_info)
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, self.callout_leg_identifier)
            Cui.CuiMarkCrrs(Cui.gpc_info, Cui.CuiWhichArea, 'OBJECT')
            Cui.CuiDeassignCrr(Cui.gpc_info, area, Cui.CUI_DEASSIGN_SILENT)        

        # Restore end time (+ original standby task code) of the pointed-to sby.
        # In case we have a standby on the INFORMED roster, this will be the
        # INFORMED time, otherwise it is the standby leg's current end time.
            
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(self.sby_leg_identifier))
        st_date,st_time = str(self.sby_start_utc).split()
        en_date,en_time = str(self.sby_restore_end_utc).split()
        Cui.CuiUpdateTaskLeg(
            {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
            {'FORM':'TASK_LEG','TASK_CODE_STRICT': self.sby_task_code},
            {'FORM':'TASK_LEG','START_DATE': st_date},
            {'FORM':'TASK_LEG','DEPARTURE_TIME': st_time.replace(':','')},
            {'FORM':'TASK_LEG','END_DATE': en_date},
            {'FORM':'TASK_LEG','ARRIVAL_TIME': en_time.replace(':','')},
            {'FORM':'TASK_LEG','OK': ''},
            Cui.gpc_info,
            area,
            "object",
            Cui.CUI_UPDATE_TASK_RECALC_TRIP
            | Cui.CUI_UPDATE_TASK_SILENT
            | Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK
            | Cui.CUI_UPDATE_TASK_TASKTAB)
    
        # If the called-out-to trip (now removed) continues into the following
        # days, and there is INFORMED standby during the now-empty period,
        # then restore that standby also.
                
        day_after_sby = self.sby_end_date_hb
        while day_after_sby <= self.callout_trip_end_day:
            self.restoreAdditionalSby(area, day_after_sby)
            day_after_sby += RelTime(24, 0)
        
        return 0

    def getPointedSbyInfo(self, area):
        """
        Get values for standby pointed leg.
        """
        try:
            leg_object = HelperFunctions.LegObject(area=area)
            
            (   self.crew_id,
                self.sby_leg_identifier,
                self.sby_task_code,
                self.sby_location,
                self.sby_start_utc,
                self.sby_end_utc,
                self.sby_start_day_hb_utc_time,
                self.sby_end_date_hb,
                self.long_haul,
                self.sby_restore_end_utc,
                self.callout_leg_identifier,
                self.callout_trip_end_day,
            ) = leg_object.eval(
                'crew.%id%',
                'leg_identifier',
                'task.%code%',
                'leg.%start_station%',
                'leg.%start_utc%',
                'leg.%end_utc%',
                'crew.%utc_time%(leg.%start_date%)',
                'rescheduling.%leg_end_date_hb%',
                'rescheduling.%duty_inf_long_haul%',
                'standby.%leg_standby_restore_end_utc%',
                'standby.%callout_leg_identifier%',
                'standby.%callout_trip_end_day%',
            )
        except Exception, e:
            Errlog.log("%s" % e)
            Errlog.set_user_message("Error: Not possible to get default information from RAVE!\n")
            return -1
        
        return 0

    def restoreAdditionalSby(self, area, restore_date):
        inf = RaveEvaluator(area, Cui.CrewMode, self.crew_id,
                            standby = 'rescheduling.%%pcat_is_standby%%(rescheduling.%%dt_inf_pcat%%(%s))' % restore_date,
                            apsby   = 'rescheduling.%%dt_inf_any_flag%%(rescheduling.%%flag_standby_at_airport%%, %s)' % restore_date,
                            chkin   = 'rescheduling.%%dt_inf_checkin%%(%s)' % restore_date,
                            chkout  = 'rescheduling.%%dt_inf_checkout%%(%s)' % restore_date,
                            ttime   = 'standby.%%local_transport_time_func%%("%s",%s,%s)' % (self.sby_location, restore_date, self.long_haul),
               )
        if not inf.standby:
            return
            
        if inf.apsby:
            task_code = "A"
            sby_start = inf.chkin
        else:
            task_code = "R"
            # The check-in stored for a home sby is actually the earliest
            #   POSSIBLE check-in (standby start + local transport time).
            # To get the standby start, we need to subtract transport time.
            sby_start = inf.chkin - inf.ttime
            
        Cui.CuiCreatePact(Cui.gpc_info,
                          self.crew_id,
                          task_code,
                          '',
                          sby_start,
                          inf.chkout,
                          self.sby_location,
                          Cui.CUI_CREATE_PACT_DONT_CONFIRM
                          | Cui.CUI_CREATE_PACT_FORCE
                          | Cui.CUI_CREATE_PACT_SILENT
                          | Cui.CUI_CREATE_PACT_NO_LEGALITY)

def restoreStandby():
    RIS = RestoreInformedStandby()
    return RIS.restoreInformedStandby()

