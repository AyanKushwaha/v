#################################################
# Definitions needed by functions in the CARMSYS
#

import os

import carmensystems.studio.gui.TrackingGui as TrackingGui
import traceback

import AbsTime
import Cui

import carmensystems.rave.api as R
import modelserver as M
from tm import TM
import carmstd.cfhExtensions as cfhExtensions
import carmusr.modcrew

class TrackingGuiExt(TrackingGui.TrackingGui):
    def __init__(self):
        # This flag is used in getPactCutFlag. It is set by
        # carmusr.tarcking.DragDrop to allow overlaps temporarely.
        self.tmp_allow_overlaps = False
        
    def getCats(self, fromArea, toArea, srcChain="", dstChain="", dstTime=0,
                ctrlPressed=0, pos=None):
        """
        Calculate the crew position for crew (dstChain), with the trip
        (srcChain) assigned. The optional argument dstTime indicates where in
        the roster the trip is dropped, and ctrlPressed indicates in the
        Ctrl-key was pressed during the drop, which will result in a
        copy-drag&drop. If a pos is sent in as the last parameter this is set
        as the default pos if no other position is calculated.
        """

        try:
            return getCategory(fromArea, toArea, srcChain, dstChain,
                               dstTime, ctrlPressed, pos)
        except Exception:
            traceback.print_exc()
    
    def getcrewLegSetIterator(self):
        return self.getCrewLegSetIterator()

    def getMoveAsmtFlag(self):
        "Workaround for STUDIO-14693"
        return self.getPactCutFlag()

    def getPactCutFlag(self):
        """The flags to CuiMoveAssignments as specified in the man page."""
        if self.tmp_allow_overlaps:
            return Cui.CUI_MOVE_ASMT_IGNORE_ASMT_POS_CHECK + \
                   Cui.CUI_MOVE_ASMT_ALLOW_OVERLAP
            
        return Cui.CUI_MOVE_ASMT_CUT_PACTS + \
               Cui.CUI_MOVE_ASMT_IGNORE_ASMT_POS_CHECK +\
               Cui.CUI_MOVE_ASMT_ALLOW_SPECIFIED_OVERLAP +\
               Cui.CUI_MOVE_ASMT_REMOVE_OVERLAPPING_SEGMENTS

    def getCreateTripFlag(self):
        """
        Returns the flags used when creating trips.
        This is in turn used by create flight
        """
        # Create separate cockpit and cabin trips
        return Cui.CUI_CREATE_TRIP_SPLIT_IN_MAIN_CATS

    def getSpecificOverlapTypes(self):
        return []
    
    def getMoveTripLegsFlag(self):
        """The flags to CuiMoveTripLegs as specified in the man page."""
        return Cui.CUI_MOVE_TRIP_LEGS_NO_LEGALITY_CHECK + Cui.CUI_MOVE_TRIP_LEGS_USE_MAX_CREW_COMP
    
    def getLegSetIterator(self):
        """Returns the leg set iterator, used by rave."""
        return 'iterators.leg_set'
    
    def getTripSetIterator(self):
        """Return the trip set iterator, used by rave."""
        return 'iterators.trip_set'
    
    def getTripAssignedCheck(self):
        """
        Returns a rave tuple of rave expressions that is used to check if a
        trip is fully assigned. Default is: 'crew_pos.%trip_assigned%','>0'
        """
        return  "studio_config.%trip_assigned_check%","T"

    def getNextPrevPreProcessing(self):
        """A function called before studio does Get Next/Previous."""
        print "get Next/Previous Pre-processing"

    def getNextPrevPostProcessing(self):
        """A function called after studio does Get Next/Previous."""
        print "get Next/Previous Pre-processing"

    def getCrewPositions(self,area,leg):
        """Return a list of crew positions not yet covered for a given leg."""
        posList = Cui.int_list()
        posList.append(0)
        posList.append(0)
        posList.append(0)
        posList.append(0)
        posList.append(0)
        posList.append(0)
        posList.append(0)
        return posList

    def ownCarriers(self):
        return ['SK']

    def createCrewDescription(self,crewId):
        desc = ""
        try:
            crewTable = TM.table("crew")
            crew = crewTable[crewId]
            if crew:
                desc = crew.id
                desc = desc + " " + (crew.name or "No Name")
        except:
            traceback.print_exc()
        return desc
   
    def getCrewId(self, area=Cui.CuiWhichArea, crewId=None):
        try:
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crewId)
            return Cui.CuiCrcEvalString(Cui.gpc_info, area, 'object', 'crew.%employee_number%')
        except:
            return "DATA ERROR"

    def getCrewInfo(self,area=Cui.CuiWhichArea,crewId=None):
        try:
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crewId)
            try:
                name = Cui.CuiCrcEvalString(Cui.gpc_info, area, 'object',
                       'crew.%login_name%')
                if name: return name
            except:
                pass
            return Cui.CuiCrcEvalString(Cui.gpc_info, area, 'object',
                   'concat(crew.%surname%, ", ", crew.%firstname%)')
        except:
            return "DATA ERROR"

    def getManualFlightCode(self):
        return "M"

    def postOpenTask(self):
        """ Called last in openTask() in studio. Performs
        actions needed on alert monitor refresh. Currently,
        cleaning modified crew. """
        carmusr.modcrew.clear()
        return ""
    
####################################################
# Actual functions used.
#
 
def getCategory(fromArea, toArea, srcChain, dstChain, dstTime, ctrlPressed, pos):
    toAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, toArea)
    fromAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, fromArea)
    func = ""

    if pos:
        func = pos
    elif fromAreaMode == Cui.CrrMode and toAreaMode == Cui.CrewMode:
        # Trip to roster
        Cui.CuiSetSelectionObject(Cui.gpc_info, fromArea, Cui.CrrMode, str(srcChain))
        try:
            dstRank = Cui.CuiCrcEvalString(Cui.gpc_info, fromArea, 'object',
                                        'crew_contract.%%crewrank_at_date_by_id%%("%s", trip.%%start_utc%%)' % dstChain)
        except:
            cfhExtensions.show("Unable to determine crew rank at start of trip")
            return ("", "")            
        func = Cui.CuiCrcEvalString(Cui.gpc_info, fromArea, 'object',
                                    'default(studio_process.%%assignable_position%%("%s"), "")' % dstRank)
        print 'studio_process.%%assignable_position%%("%s") = %s' % (dstRank, func) #For SP2 testing

    if func:
        cat, = R.eval('crew_pos.%%func2cat%%("%s")' % func)
    else:
        cat, func = ("", "")
    print "TrackingGuiExt::GetCategory:: return value: (%s, %s)" % (cat, func)
    return cat, func

print "TrackingGuiExt loaded" #For SP2 testing
