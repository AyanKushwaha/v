"""
Wrapper functions for the CARMSYS defined drag and drop functionality.  In this
file the function for double clicking is contained, for allowing modifications
later. Besides that, only the the functions needing validation are defined
(functions used for assigning to crew). 
"""

import os
import tempfile
import time

import Cui
import Cfh
import Gui

import carmensystems.rave.api as rave
import carmensystems.studio.manipulate.DragDrop as CarmsysDD
import carmensystems.studio.Tracking.OpenPlan
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.studio.gui.StudioGui as StudioGui
import hotel_transport.HotelHandler as HotelHandler

import Standby
import carmusr.training_attribute_handler
import carmusr.HelperFunctions as HF
import carmusr.tracking.TripTools as TripTools
import carmstd.area as Area


from AbsTime import AbsTime
from RelTime import RelTime
from Variable import Variable
from tm import TM
from utils.rave import RaveIterator

# These are the references that we have to CARMSYS LegBasedFunctions which are
# 'private' but used anyway
import carmensystems.studio.manipulate.private.LegBasedFunctions as lbf

def selectCrew(with_time=False):
    return lbf._selectCrew(withTime=with_time)

def selectResource():
    return lbf._selectTripOrChain()

def AssignMarkedTrips(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
        ctrlPressed=0, pos=None):
    """
    DragDrop - resource: 'dropCRRs2RostersMain'
    Wrapper for the function moving trips from the trip window to the a
    crew/roster.
    """
    print "DragDrop::AssignMarkedTrips", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos
    return wrapped(CarmsysDD.AssignTrip, fromArea, toArea, srcChain, dstChain,
            srcTime, dstTime, ctrlPressed, pos)

def AssignMarkedTripsAllowOverlaps(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
        ctrlPressed=0, pos=None):
    """
    DragDrop - resource: 'dropCRRs2RostersMain'
    Wrapper for the function moving trips from the trip window to the a
    crew/roster.
    """
    print "DragDrop::AssignMarkedTripsAllowOverlaps", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos
    try:
        StudioGui.getInstance().tmp_allow_overlaps = True
        ret = CarmsysDD.AssignTrip(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos)
    except:
        StudioGui.getInstance().tmp_allow_overlaps = False
        raise
    StudioGui.getInstance().tmp_allow_overlaps = False    
    return ret

def CopyLegs(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0, ctrlPressed=1,
        pos=None):
    """
    DragDrop - Right MB drag and drop 
    Menu - (DragDropMenus.menu)
    """
    print "DragDrop::CopyLegs", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, fromArea)
    returnValue = MoveLegs(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos)
    if returnValue == 0:
        TripTools.tripClean(fromArea, marked_legs)
    return returnValue

def MoveLegs(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0, ctrlPressed=0,
        pos=None):
    """
    DragDrop - resource: 'dropRosters2RostersMain'
    Menu - 'Move' in 'DragDropMenus'.
    Wrapper for moving legs between crew.
    """
    print "DragDrop::MoveLegs", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos

    set_dst_area(toArea)
    result = wrapped(CarmsysDD.Move, fromArea, toArea, srcChain, dstChain,
                     srcTime, dstTime, ctrlPressed, pos)
    set_dst_area(None)

    return result

def CopyLegsAllowOverlaps(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                          ctrlPressed=1, pos=None):
    """
    DragDrop - Right MB drag and drop 
    Menu - (DragDropMenus.menu)
    """
    print "DragDrop::CopyLegsAllowOverlaps", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, fromArea)
    returnValue = MoveLegsAllowOverlaps(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos)
    if returnValue == 0:
        TripTools.tripClean(fromArea, marked_legs)
    return returnValue

def MoveLegsAllowOverlaps(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                          ctrlPressed=0, pos=None):
    """
    DragDrop - resource: 'dropRosters2RostersMain'
    Menu - 'Move, allow overlaps' in 'DragDropMenus'.
    Wrapper for moving legs with overlap between crew.
    """
    print "DragDrop::MoveLegsAllowOverlaps", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos

    # As we do not call wrapped, we need to check for move/copy between main cats.
    toAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, toArea)
    fromAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, fromArea)
    if toAreaMode == Cui.CrewMode and fromAreaMode == Cui.CrewMode:
        Cui.CuiSetSelectionObject(Cui.gpc_info, fromArea, Cui.CrewMode, srcChain)
        srcCat = Cui.CuiCrcEvalString(Cui.gpc_info, fromArea, 'object', 'fundamental.%main_cat%')
        Cui.CuiSetSelectionObject(Cui.gpc_info, toArea, Cui.CrewMode, dstChain)
        dstCat = Cui.CuiCrcEvalString(Cui.gpc_info, toArea, 'object', 'fundamental.%main_cat%')
        if srcCat <> dstCat:
            try:
                srcLegs, dstLegs = getLegs(fromArea, toArea, srcChain, dstChain, dstTime, ctrlPressed)
            except Exception, e:
                print "DragDrop.py: ERROR: %s." % (e,)
                return -1
            for leg in srcLegs:
                if not leg.is_pact:
                    cfhExtensions.show("Not possible to move/copy between crew categories", title="Message")
                    return 1
        
    # Set temp variable to allow overlaps in sys move, and then call sys move.
    # Make sure we restore variable after.
    try:
        StudioGui.getInstance().tmp_allow_overlaps = True
        ret = CarmsysDD.Move(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos)
    finally:
        StudioGui.getInstance().tmp_allow_overlaps = False
    return ret

def SwapLegs(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0, ctrlPressed=0,
             pos=None, flags=0):
    """
    Menu - 'Swap' in 'DragDropMenus'
    """
    def check_for_non_deassignable(area, chain=None):
        """Check if any marked leg in 'chain' is not deassignable or if no
        chain given, in the whole window (trip buffer)."""
        if chain is None:
            scope = 'window'
        else:
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, chain)
            scope = 'object'
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        legs = RaveIterator(RaveIterator.iter('iterators.leg_set',
            where='marked', sort_by='leg.%start_utc%'),
            {'is_deassignable': 'studio_process.%leg_is_deassignable%'}
            ).eval('default_context')
        rc = len([leg for leg in legs if not leg.is_deassignable]) > 0
        if rc:
            cfhExtensions.show("Not able to deassign legs.\n" 
                    "Try removing assignments manually.",
                    title="Swap error")
        return rc
    if int(srcTime) == 0: srcTime = dstTime
    print int(srcTime), int(dstTime)
    print "DragDrop :: SwapLegs", fromArea, toArea, srcChain, dstChain, str(AbsTime(srcTime)), str(AbsTime(dstTime)), ctrlPressed, pos

    # This is somewhat unclear, CARMSYS mixes None, empty strings, '0', and empty lists as empty objects.
    if not dstChain or not srcChain:
        return 1

    if dstChain == srcChain:
        return 1

    # Don't allow swap FD <-> CC
    main_cat_expr = 'crew.%%maincat_for_rank%%(crew.%%function_for_crew_at_time%%("%s", %s))'
    if dstTime == 0:
        s_src = main_cat_expr % (srcChain, 'fundamental.%now%')
        s_dst = main_cat_expr % (dstChain, 'fundamental.%now%')
    else:
        s_src = main_cat_expr % (srcChain, AbsTime(dstTime))
        s_dst = main_cat_expr % (dstChain, AbsTime(dstTime))
    src_main_cat, dst_main_cat = rave.eval(s_src, s_dst)
    if (src_main_cat, dst_main_cat) == ('F', 'C') or (src_main_cat, dst_main_cat) == ('C', 'F'):
        cfhExtensions.show("Cannot swap assignments between FD and CC.",
                title="Swap error")
        return 1

    flags |= Cui.CUI_MOVE_ASMT_IGNORE_ASMT_POS_CHECK | Cui.CUI_MOVE_ASMT_BREAK_SWAP_AT_DELETE
    ret = CarmsysDD.DropSwap(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, flags)
    print "DragDrop::SwapLegs %s.%s returned %s" % (CarmsysDD.DropSwap.__module__, CarmsysDD.DropSwap.__name__, ret)
    return ret

def assign_training_with_attr(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                              ctrlPressed=0, pos=None):
    """
    Called from DropCRRs2RostersMain (drag with MB3).
    """
    print "DragDrop::assign_training_with_attr", fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos
    assigner = carmusr.training_attribute_handler.DnDManualAttributeAssigner(dstChain, toArea,
                                                                             srcChain, fromArea)
    
    return assigner.assign()

def assign_according_to_need(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                             ctrlPressed=0, pos=None):
    """
    Called from DropCRRs2RostersMain (drag with MB3).
    """
    assigner = carmusr.training_attribute_handler.DnDNeedAttributeAssigner(dstChain, toArea,
                                                                           srcChain, fromArea)
    return assigner.assign()

def assign_in_instr_pos(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                        ctrlPressed=0, pos=None):
    """
    Called from DropCRRs2RostersMain (drag with MB3).
    """
    is_simulator = Cui.CuiCrcEvalBool(Cui.gpc_info, fromArea, "object", 'trip.%is_simulator%')
    if is_simulator:
        crew_obj = HF.CrewObject(str(dstChain),toArea)
        maincat, =  crew_obj.eval('crew.%%main_func_at_date%%(%s)'%AbsTime(dstTime))
        valid_cat = {"F":True}.get(maincat,None)
        if valid_cat:
            print 'DragDrop::assign_in_instr_pos: Assigning simulator'
            return AssignMarkedTrips(fromArea, toArea, srcChain, dstChain, srcTime=0, dstTime=0,
                                 ctrlPressed=0)
        cfhExtensions.show("Simulators must be assigned only to flight deck crew.!", title="Message")
        return 1
    cfhExtensions.show("Action valid only for simulators.!", title="Message")
    return 1

def menu_copy_roster(dstTime=0, ctrlPressed=1, pos=None):
    """
    Menu - 'Copy' in 'Assignment Object'
    Created to imitate Drag-and-Drop behavior.

    Note that the menu version will keep a hair-cross active so that the leg(s)
    can be copied to several different crew chains in one operation.
    """
    print "DragDrop::menu_copy_roster"
    fromArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)


    # When a copy succeeds, the destination objects are marked so we must get the source chain again
    # but when a copy does not succeed the source objects are already marked and trying to mark
    # them again will cause a crash. That is why we need this variable, to know when to 
    # get the source chain. 
    get_source_chain = True
    
    rc_0_if_ok = 1
    while True:
 
        if get_source_chain:
            try:
                srcChain = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'OBJECT', 'crr_crew_id')
                if srcChain is None:
                    print "DragDrop::menu_copy_roster: leaving since srcChain was None"
                    return 1
            except:
                # Abort the copying if anything goes wrong. There seem to be hard to solve occasions when
                # the statement above fails. Now the copying is aborted instead of "Carmen serious error" 
                break

        try:
            marked_legs = Cui.CuiGetLegs(Cui.gpc_info, fromArea)
            toArea, dstChain, dstTime = target_selection(fromArea, srcChain)
            if dstChain is None:
                print "DragDrop::menu_copy_roster: leaving since dstChain was None"
                return 1
        except HF.RosterSelectionError, rse:
            print "DragDrop::menu_copy_roster: %s" % (rse,)
            break

        try:
            if MoveLegs(fromArea, toArea, srcChain, dstChain, 0, dstTime, ctrlPressed, pos) == 0:
                rc_0_if_ok = 0
                TripTools.tripClean(fromArea, marked_legs)
                get_source_chain = True
            else:
                get_source_chain = False
                                
        except Exception, e:
            print "DragDrop::menu_copy_roster: ERROR: %s" % (e,)
            return 1
    
    return rc_0_if_ok


def menu_move_roster(dstTime=0, ctrlPressed=0, pos=None):
    """
    Menu - 'Move' in 'Assignment Object'
    Created to imitate Drag-and-Drop behavior.
    """
    print "DragDrop::menu_move_roster"
    try:
        Area.promptPush("Select crew member to move assignments.")
        # Note: 'pact=True' has no impact other than that dstTime is returned
        fromArea, toArea, srcChain, dstChain, dstTime = selectCrew(with_time=True)
        if srcChain is None or dstChain is None:
            return 1
    finally:
        Area.promptPush("")
        
    return MoveLegs(fromArea, toArea, srcChain, dstChain, 0, dstTime, ctrlPressed, pos)

def menu_swap_roster(flags=0):
    """
    Menu - 'Swap' in 'Assignment Object'
    """
    print "DragDrop::menu_swap_roster"

    fromArea = toArea = fromCrew = toCrew = None

    for area in range(Cui.CuiAreaN):
        for crew in Cui.CuiGetCrew(Cui.gpc_info, area, "marked"):
            if fromCrew == None:
                fromCrew = crew
                fromArea = area
            elif toCrew == None:
                if fromCrew != crew:
                    toCrew = crew
                    toArea = area
            else:
                if (crew != fromCrew and crew != toCrew):
                    cfhExtensions.show("Must mark assignments from two rosters to swap", title="Message")

    if (fromCrew == None or toCrew == None):
        cfhExtensions.show("Must mark assignments from two rosters to swap", title="Message")

    if SwapLegs(fromArea, toArea, fromCrew, toCrew, flags=flags) < 0:
        cfhExtensions.show("Could not perform swap. Assignments may be locked.", title="Message")


def menu_move_or_assign_trip():
    """
    Created to imitate Drag-and-Drop behavior for trip object menu.
    """
    print "DragDrop::menu_move_or_assign_trip"
    src, dst, src_id, dst_id = selectResource()
    # See Bugzilla BZ 24379, BZ 24403
    if src_id is None or dst_id is None:
        return 1
    dst_mode = Cui.CuiGetAreaMode(Cui.gpc_info, dst)
    if dst_mode == Cui.CrrMode:
        print "DragDrop::menu_move_or_assign_trip moving trip"
        return CarmsysDD.JoinTrips(src, dst, src_id, dst_id, 0, 0)
    elif dst_mode == Cui.CrewMode:
        print "DragDrop::menu_move_or_assign_trip assigning"
        # convert src_id and dst_id to strings (why?)
        return AssignMarkedTrips(src, dst, str(src_id), str(dst_id), 0)
    else:
        print "DragDrop::menu_move_or_assign_trip"\
              " unknown destination area, skipping..."

def MarkTrip(fromArea):
    """
    Wrapper for the function marking trips on double click.
    Accessed via the resources doubleClickRostersMain and doubleClickCRRsMain.
    """
    CarmsysDD.MarkTrip(fromArea)

def postFunction(dstCrewId=None, addedLegs=[], area=Cui.CuiNoArea):
    """
    Set by a resource (config.MoveAssignmentsPostFunction).
    Called by CuiMoveAssignments, which actually includes both move and create.
    Not restricted to DnD operations!
    Mainly performes cutting of personal activities according to rave values.
    """

    print "DragDrop::postFunction: area (src) = %s" % area
    area = get_dst_area(area)
    print "DragDrop::postFunction: area (dst) = %s" % area

    if None in (dstCrewId, area, addedLegs):
        return

    if len(addedLegs) == 0:
        return
          
    if StudioGui.getInstance().tmp_allow_overlaps:
        print "DragDrop::postFunction: allow-overlap-mode -> SKIPPED"
        return
        
    print "DragDrop::postFunction: crew=%s,area=%s,addedLegs=%s" \
          % (dstCrewId, area, addedLegs)
        
    t = time.time()

    # Get information on all legs on the crew roster
    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, dstCrewId)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
    legs = RaveIterator(
        RaveIterator.iter('iterators.leg_set', sort_by='leg.%start_utc%'),
        {'name': 'leg.%flight_id%',
         'id': 'leg_identifier',
         'is_pact': 'personal_activity and not ground_transport',
         'is_flight_duty': 'leg.%is_flight_duty%',
         'is_ground_transport': 'leg.%is_ground_transport%',
         'is_standby': 'leg.%is_standby%',
         'is_airport_sby': 'leg.%is_standby_at_airport%',
         'is_cancel_sby': 'leg.%is_cancellation_standby%',
         'arr_stn':'arrival_airport_name',
         'start_utc': 'leg.%start_utc%',
         'end_utc': 'leg.%end_utc%',
         'check_in': 'leg.%ci_start_utc%',
         'check_out': 'leg.%co_end_utc%',
         'pact_cut_start': 'studio_process.%assignment_pact_cut_start%',
         'pact_cut_end': 'studio_process.%assignment_pact_cut_end%',
         'max_wait': 'leg.%limit_waiting_at_airport_when_callout%',
         'is_freeday':'leg.%is_freeday%',
         'activity_id':'leg.%activity_id%',
        }).eval('default_context')

    # Determine the production time to mimic duty.%time% that doesn't give the correct duty time when using drag and drop.
    # The added legs are checked for at least one flight leg.
    # It is an improvement to the existing where no check of the production duration.
    prd_duration_ci_co = RelTime(0, 0)
    list_of_added_legs = [leg for leg in legs if leg.id in addedLegs]
    if len(list_of_added_legs) > 0:
        added_legs_has_prd = any([al.is_flight_duty for al in list_of_added_legs])
        if added_legs_has_prd:
            max_end_co = max(add_leg.check_out for add_leg in list_of_added_legs)
            max_end_date = max_end_co.day_floor()
            added_legs_last_day = [al for al in list_of_added_legs if al.end_utc.day_floor() == max_end_date]
            ci_last_date = min(add_leg_ld.check_in for add_leg_ld in added_legs_last_day)
            prd_duration_ci_co = max_end_co - ci_last_date

    # Loop through the legs, check cutting for pacts
    for ix in range(len(legs)):
        if not legs[ix].is_pact:
            continue
        modify = False
        trailing_sby = False
        trailing_cancel_or_airport_sby = False
        time_btwn_addedLegs_Freeday = RelTime(0, 0)
        followed_by_freeday = False
        if ix > 0 and len(legs) > ix+1 and legs[ix-1].id in addedLegs:
            if legs[ix+1].is_freeday:
                followed_by_freeday = True
                time_btwn_addedLegs_Freeday = legs[ix+1].start_utc - legs[ix-1].end_utc

        if ix > 0 and legs[ix-1].id in addedLegs and legs[ix].start_utc < legs[ix].pact_cut_start:
            # We need to adjust start time of a pact following the dropped legs.
            print "DragDrop::postFunction: Cutting %s start [%s - %s] to %s" % (legs[ix].name, legs[ix].start_utc, legs[ix].end_utc, legs[ix].pact_cut_start)
            legs[ix].start_utc = legs[ix].pact_cut_start
            # If previous leg is flight duty and this leg is standby (or previous leg is ground transport) ####
            if legs[ix].is_standby and legs[ix-1].is_flight_duty or legs[ix-1].is_ground_transport:
                # The adjusted pact was a standby after a call out: convert to Waiting at Airport at the arrival station.
                if legs[ix].is_airport_sby or legs[ix].is_cancel_sby:
                    trailing_cancel_or_airport_sby = True
                else:
                    print "                        Changing trailing sby to 'W'"
                trailing_sby = True
            modify = True
        if (len(legs) > ix+1 and legs[ix+1].id in addedLegs
            and legs[ix].end_utc > legs[ix].pact_cut_end):
            # We need to adjust end time of the leg.
            # For a standby, at least 1 minute must remain.
            print "DragDrop::postFunction: Cutting %s end [%s - %s] to %s" % (legs[ix].name, legs[ix].start_utc, legs[ix].end_utc, legs[ix].pact_cut_end)
            legs[ix].end_utc = legs[ix].pact_cut_end
            if legs[ix].is_standby and legs[ix].end_utc < legs[ix].start_utc + RelTime(0,1):
                legs[ix].end_utc = legs[ix].start_utc + RelTime(0,1)
                print "                        Standby adjust: keep one minute"
            modify = True

        if modify:

            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(legs[ix].id))
            if (legs[ix].start_utc >= legs[ix].end_utc and not trailing_sby)\
                    or (trailing_sby and prd_duration_ci_co > RelTime(6, 0)) \
                    or (trailing_sby and followed_by_freeday and time_btwn_addedLegs_Freeday < RelTime(2, 0))\
                    or (trailing_sby and legs[ix].max_wait <= RelTime(0, 0))\
                    or (trailing_sby and trailing_cancel_or_airport_sby):
                # CuiUpdateTaskLeg can not handle 0:00 time legs, so we need to remove legs with CuiRemoveAssignments instead
                print "DragDrop::postFunction: Removing %s %s" % (legs[ix].name, legs[ix].start_utc)

                # The added legs are now marked and will be removed unless they are unmarked.
                # We will temporarily unmark them when removing the pact, we will mark them again
                # afterwards 
                Cui.CuiUnmarkAllLegs(Cui.gpc_info, area, "WINDOW")
                
                # Mark the personal activity
                Cui.CuiMarkLegs(Cui.gpc_info, area, "object", Cui.CUI_MARK_SET)
                Cui.CuiRemoveAssignments(Cui.gpc_info, area, dstCrewId)
                
                # Marks the destination legs again.
                for leg_id in addedLegs:
                    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(leg_id))
                    Cui.CuiMarkLegs(Cui.gpc_info, area, "object", Cui.CUI_MARK_SET)
                                                
            else:
                # Update the pact. One version include activity code, one does not.
                if trailing_sby:
                    print "DragDrop::postFunction: Updating %s %s, task code -> A" % (legs[ix].name, legs[ix].start_utc)
                    wait_end = legs[ix].start_utc + legs[ix].max_wait
                    wait_end_tod = str(wait_end)[10:12] + str(wait_end)[13:15]
                    wait_end_date = str(legs[ix].end_utc)[0:9]
                    print "WAITING UPD wait_end %r tod %r date %r" % (wait_end, wait_end_tod, wait_end_date)
                    Cui.CuiUpdateTaskLeg(
                        {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
                        {'FORM':'TASK_LEG','TASK_CODE_STRICT': 'A'},
                        {'FORM':'TASK_LEG','LOCATION': legs[ix-1].arr_stn},
                        {'FORM':'TASK_LEG','START_DATE': str(legs[ix].start_utc)[0:9]},
                        {'FORM':'TASK_LEG','END_DATE': wait_end_date},
                        {'FORM':'TASK_LEG','DEPARTURE_TIME': str(legs[ix].start_utc)[10:12] + str(legs[ix].start_utc)[13:15]},
                        {'FORM':'TASK_LEG','ARRIVAL_TIME': wait_end_tod},
                        {'FORM':'TASK_LEG','OK': ''},
                        Cui.gpc_info,
                        area,
                        "object",
                        Cui.CUI_UPDATE_TASK_RECALC_TRIP |\
                        Cui.CUI_UPDATE_TASK_SILENT |\
                        Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK |\
                        Cui.CUI_UPDATE_TASK_TASKTAB)
                else:
                    print "DragDrop::postFunction: Updating %s %s" % (legs[ix].name, legs[ix].start_utc)
                    Cui.CuiUpdateTaskLeg(
                        {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
                        {'FORM':'TASK_LEG','START_DATE': str(legs[ix].start_utc)[0:9]},
                        {'FORM':'TASK_LEG','END_DATE': str(legs[ix].end_utc)[0:9]},
                        {'FORM':'TASK_LEG','DEPARTURE_TIME': str(legs[ix].start_utc)[10:12] + str(legs[ix].start_utc)[13:15]},
                        {'FORM':'TASK_LEG','ARRIVAL_TIME': str(legs[ix].end_utc)[10:12] + str(legs[ix].end_utc)[13:15]},
                        {'FORM':'TASK_LEG','OK': ''},
                        Cui.gpc_info,
                        area,
                        "object",
                        Cui.CUI_UPDATE_TASK_RECALC_TRIP |\
                        Cui.CUI_UPDATE_TASK_SILENT |\
                        Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK |\
                        Cui.CUI_UPDATE_TASK_TASKTAB)
                
    t = time.time() - t     
    print "DragDrop::postFunction done in %0.2fs" % t

AREA=None

def set_dst_area(area):
    global AREA
    AREA = area
    print "DragDrop::set_dst_area: area (dst) was set to %s" % AREA

def get_dst_area(area):
    global AREA
    if AREA != None:
        print "DragDrop::get_dst_area: area (dst) was set to %s" % AREA
        return AREA
    else:
        print "DragDrop::get_dst_area: area (dst) was not set, using area (src) %s" % area
        return area

class CrewPositionError(Exception):
    """Signal crew position error."""
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)

def wrapped(func, fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos):
    """
    The argument 'func' is a reference to the (SYS) function that is wrapped.

    This function prepares for assignment movements. Overlapping activities are
    not allowed and thus this function checks for possible overlap problems and
    either resolves or returns if unable to solve the problem.  The solution to
    overlaps is simple: if the source legs involved in the overlaps are
    standbys, these are either cut into suitable chuncks or deassigned. In case
    of correctly used standbys, the user will be prompted for callout and
    transport times.

    The function returns 0 if ok, 1 on user intercept or -1 on error.
    """
    toAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, toArea)
    fromAreaMode = Cui.CuiGetAreaMode(Cui.gpc_info, fromArea)

    print "DragDrop::wrapped area %s, mode %s, chain %s --> %s, %s, %s @ %s" % (
        fromArea, fromAreaMode, srcChain, toArea, toAreaMode, dstChain, AbsTime(dstTime))

    dstTime = AbsTime(dstTime)
    
    # Get source and destination legs
    try:
        srcLegs, dstLegs = getLegs(fromArea, toArea, srcChain, dstChain, dstTime, ctrlPressed)
    except CrewPositionError, cpe:
        cfhExtensions.show(str(cpe))
        return 1
    except Exception, e:
        # [acosta:08/022@10:15] In case no rosters where found, etc.
        print "DragDrop.py: ERROR: %s." % (e,)
        return -1

        
    if srcChain == dstChain:
        if min([leg.is_pact for leg in srcLegs]) == False:
            cfhExtensions.show("Only personal activities can be\nmoved/copied within a roster.")
            return 1
        if len(srcLegs) > 1:
            cfhExtensions.show("Only one activity at a time\ncan be moved/copied within a roster.")
            return 1
        
    if toAreaMode == Cui.CrewMode and fromAreaMode == Cui.CrewMode:
        Cui.CuiSetSelectionObject(Cui.gpc_info, fromArea, Cui.CrewMode, srcChain)
        srcCat = Cui.CuiCrcEvalString(Cui.gpc_info, fromArea, 'object', 'fundamental.%main_cat%')
        Cui.CuiSetSelectionObject(Cui.gpc_info, toArea, Cui.CrewMode, dstChain)
        dstCat = Cui.CuiCrcEvalString(Cui.gpc_info, toArea, 'object', 'fundamental.%main_cat%')
        if srcCat <> dstCat:
            for leg in srcLegs:
                if not (leg.is_pact or leg.is_deadhead or leg.is_ground_transport):
                    cfhExtensions.show("Not possible to move/copy legs between crew categories")
                    return 1

    standbyHandler = Standby.StandbyHandler(toArea, dstChain)

    # Find out which src leg is being overlapped by which dst leg:
    # build "trips" by ccr_id to cover "holes" between legs
    src_trips = {}
    for leg in srcLegs:
        if leg.crr_id in src_trips:
            src_trips[leg.crr_id].append(leg)
        else: 
            src_trips[leg.crr_id] = [leg]
            
    overlapsExist = False
    usedSbyForTripId = None
    handleSbys = True
    
    if srcChain == dstChain:

        crr_id = srcLegs[0].crr_id
        leg = srcLegs[0]

        for dst in dstLegs:
            overlapsExist = True
            handleSbys = False

            if not dst.is_deassignable:
                cfhExtensions.show("Not able to deassign legs.\nTry removing assignments manually.",
                        title="Overlapping assignment")
                return 1
            elif dst.is_standby:
                cfhExtensions.show("Cannot assign personal activity to standbys in same roster.\nTry removing assignments manually.",
                                   title="Info")
                return 1        
    else:
    
        for (crr_id, trip) in src_trips.iteritems():
            trip_start = trip[0].start or trip[0].leg_start
            trip_end = trip[-1].end or trip[-1].leg_start
            # Check if trip contains both ground and flight activities
            mixed_trip = (len([x for x in trip if x.is_flight_duty or x.is_ground_transport]) > 0 
                    and len([x for x in trip if not (x.is_flight_duty or x.is_ground_transport)]) > 0)
    
            for dst in dstLegs:
                dst_start = dst.start or dst.leg_start
                dst_end =  dst.end or dst.leg_end
                if dst.is_standby:
                    # Include standby transport time in end time
                    dst_end += dst.local_transport
                
                # Check if the trip to be coopies has any overlaps
                if dst_start <= trip_end and dst_end >= trip_start:
                    overlapsExist = True
                             
                    if not dst.is_deassignable:
                        cfhExtensions.show("Not able to deassign legs.\nTry removing assignments manually.",
                                title="Overlapping assignment")
                        return 1
                    elif dst.is_standby:
                        # Assign either flight-production or ground duties
                        if mixed_trip:
                            cfhExtensions.show("Trips with both flight and ground duties\ncannot be assigned to standbys.")
                            return 1
                        if dst.locked:
                            cfhExtensions.show("Cannot assign to locked standbys.")
                            return 1
                        if not dst.is_pact:
                            cfhExtensions.show("Standby object is not personal activity.\nCan only perform standby callout for personal activities.")
                            return 1
                        # Off duty activities doesn't use standby, replace pact
                        # [acosta:08/127@16:11] Shouldn't this be handled in Standby?
                        if not trip[0].is_on_duty or trip[0].is_pact:
                            handleSbys = False
        
                        # Only assign one trip per time since cancel on last dialog
                        # in standbyHandler will cancel whole operation
                        if usedSbyForTripId is None or crr_id == usedSbyForTripId:
                            standbyHandler.addToReplacementMap(standbyInst(dst,dstChain),
                                    productionInst(trip[0]))
                            usedSbyForTripId = crr_id
                        else:
                            cfhExtensions.show("Please assign one trip\nat a time to standbys.")
                            return 1

    # Perform the Move/Assign/...
    print "DragDrop::wrapped Calling %s.%s%s" % (func.__module__, func.__name__, 
            (fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos))
    rc = func(fromArea, toArea, srcChain, dstChain, srcTime, dstTime, ctrlPressed, pos)
    print "DragDrop::wrapped %s.%s returned %s" % (func.__module__, func.__name__, rc)
    # Handle standbys after the move/assign.
    if rc == 0 and overlapsExist and handleSbys:
        print "DragDrop::wrapped Calling %s.%s.handleStandby" % (standbyHandler.__module__, standbyHandler.__class__.__name__)
        rc = standbyHandler.handleStandby()
        print "DragDrop::wrapped %s.%s.handleStandby returned %s" % (standbyHandler.__module__, standbyHandler.__class__.__name__, rc)
        if rc == 0:
            cw = standbyHandler.create_trailing_pact(trip, dst.max_wait)
            if cw <> 0:
                print "create_trailing_pact error %r %r" % (cw, type(cw))
            rc = 0 if cw is None else cw
    return rc

def get_crr_ids_and_mark(legs):
    """
    Return list of trip IDs given list of leg IDs.
    The legs will also be marked (important, since otherwise CuiAddAssignments,
    will not work).
    """
    # Convert to string
    s_legs = [str(leg) for leg in legs]

    # Using ScriptBuffer in CrrMode to get trip ID, note the legs are a list of
    # legID so the ID type is LegMode
    #Cui.CuiClearArea(Cui.gpc_info, Cui.CuiScriptBuffer)
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrrMode,
            Cui.LegMode, s_legs, 0)
    # Mark legs
    for leg in s_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer,
                Cui.LegMode, leg)
        Cui.CuiMarkLegs(Cui.gpc_info, Cui.CuiScriptBuffer, 'OBJECT',
                Cui.CUI_MARK_SET)
    # Return trip IDs
    return Cui.CuiGetTrips(Cui.gpc_info, Cui.CuiScriptBuffer)

def getLegs(fromArea, toArea, srcChain, dstChain, dstTime, ctrlPressed):
    """
    Function which gets properties for source and destination legs. Returns
    a chain of objects which have the properties as attributes. The chain may
    be iterated over and is sorted by departure time.

    ctrlPressed = 1 
    when the function is called from a "Copy" operation, in that case we will
    not check if the trip is made for a certain position.

    ctrlPressed = 0
    when the function is called from a "Move" operation.
    """
    print "DragDrop::getLegs", fromArea, toArea, srcChain, dstChain, ctrlPressed

    # Select the source chain as default context
    Cui.CuiSetSelectionObject(Cui.gpc_info, fromArea,
            Cui.CuiGetAreaMode(Cui.gpc_info, fromArea), srcChain)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, fromArea, "object")

    fields = {
        'start': 'publish.%leg_start_utc%',
        'end': 'publish.%leg_end_utc%',
        'scheduled_start':'leg.%activity_scheduled_start_time_UTC%',
        'leg_start': 'leg.%start_utc%',
        'leg_end': 'leg.%end_utc%',
        'leg_ci': 'leg.%ci_start_utc%',
        'leg_co': 'leg.%co_end_utc%',
        'check_in_reltime': 'leg.%check_in%',
        'is_last_in_trip': 'publish.%leg_is_last_in_trip%',
        'is_standby': 'leg.%is_standby%',
        'is_airport_standby': 'leg.%is_standby_at_airport%',
        'is_cancel_sby': 'leg.%is_cancellation_standby%',
        'is_pact': 'leg.%is_pact%',
        'code': 'task.%code%',
        'local_transport': 'standby.%default_local_transport_time%',
        'callout_time': 'standby.%default_callout_time%',
        'airport': 'leg.%start_station%',
        'is_deassignable': 'studio_process.%leg_is_deassignable%',
        'has_assigned_fc': 'crew_pos.%leg_has_assigned_fc%',
        'has_assigned_cc': 'crew_pos.%leg_has_assigned_cc%',
        'crr_id':'crr_identifier',
        'leg_id':'leg_identifier',
        'crew_id':'crew.%id%',
        'is_on_duty':'leg.%is_on_duty%',
        'is_flight_duty':'leg.%is_flight_duty%',
        'is_deadhead':'leg.%is_deadhead%',
        'is_ground_transport':'leg.%is_ground_transport%',
        'locked':'preassigned_activity',
        'max_wait':'leg.%limit_waiting_at_airport_when_callout%'
    }
    
    srcLegs = RaveIterator(RaveIterator.iter('iterators.leg_set',
        where='marked', sort_by='leg.%start_utc%'),
        fields).eval('default_context')
    
    start_time = srcLegs[0].start
    end_time = srcLegs[-1].end
    if not start_time:
        print "DragDrop.py:: first sourceleg's publish.%leg_start_utc% was VOID, "+\
              "using leg.%start_utc%"
        start_time = srcLegs[0].leg_start
    if not end_time:
        print "DragDrop.py:: last sourceleg's publish.%leg_end_utc% was VOID, "+\
              "using leg.%end_utc%"
        end_time = srcLegs[0].leg_end
    
    # Select the destination roster as default context
    Cui.CuiSetSelectionObject(Cui.gpc_info, toArea, Cui.CrewMode, dstChain)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, toArea, "object")

    # Check if only personal activities, if so than use the destination day when looking 
    # overlapping legs. If not only personal activities, then the destination day will
    # be the same as the source day.
    if len(srcLegs) == 1 and srcLegs[0].is_pact:
        dstDay = AbsTime(dstTime).day_floor()
        dstStartTime = AbsTime(start_time).time_of_day()
        dstEndTime = AbsTime(end_time).time_of_day()
    
        dstLegs = RaveIterator(RaveIterator.iter('iterators.leg_set',
                                                         where=('leg.%%start_utc%% < %s' % (dstDay + dstEndTime),
                                                                'leg.%%end_utc%%+standby.%%default_local_transport_time_with_extra_minute%% > %s' %\
                                                                (dstDay + dstStartTime)), # Inlude standby transport time in end time
                                                         sort_by='leg.%start_utc%'), fields).eval('default_context')            
    else:  
        dstLegs = RaveIterator(RaveIterator.iter('iterators.leg_set',
                    where=('leg.%%start_utc%% < %s' % end_time,
                           'leg.%%end_utc%%+standby.%%default_local_transport_time_with_extra_minute%% > %s' %\
                           start_time), # Inlude standby transport time in end time
                    sort_by='leg.%start_utc%'), fields).eval('default_context')
                  
    if len(dstLegs) == 0:
        dstLegs = None

    
    # [acosta:08/022@09:56] If first leg is a PACT, then no positions are assigned.
    #f = srcLegs[0]
    #if not f.is_pact and not ctrlPressed:
    #    dstCat = RaveIterator(RaveIterator.iter('iterators.chain_set'),
    #        {'func':'crew.%main_func%'}).eval('default_context')[0].func
    #    if ((dstCat == 'F' and not f.has_assigned_fc) or 
    #        (dstCat == 'C' and not f.has_assigned_cc)):
    #        raise CrewPositionError("The trip is not made for this position.")

    return srcLegs or [], dstLegs or []

def standbyInst(sby, crewId):
    """Standby - Return Standby object."""
    return Standby.StandbyHandler().Standby(sby.start, sby.leg_start, sby.end,
            sby.leg_end, sby.is_airport_standby, sby.is_cancel_sby, sby.callout_time,
            sby.local_transport, crewId, sby.airport, sby.code, sby.leg_id)

def productionInst(prd):
    """Standby - Return Production object.""" 
    return Standby.StandbyHandler().Production(prd.start, prd.leg_start,
            prd.end, prd.leg_end, prd.is_last_in_trip, prd.crew_id,
            prd.check_in_reltime, prd.scheduled_start)

def target_selection(area=None, crew=None):
    """Let user click on roster to select crew member and time point."""
    while True:
        try:
            crew_variable = Variable("", 30)
            time_variable = Variable(0)
            Cui.CuiSelectTimeAndRow(Cui.gpc_info, Cui.CuiWhichArea,
                    Cui.CrewMode, time_variable, crew_variable, 30)
            clicked_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            clicked_crew = crew_variable.value
            clicked_time = AbsTime(time_variable.value)
            return clicked_area, clicked_crew, clicked_time
        except Cui.CancelException:
            raise HF.RosterSelectionError("User cancelled operation (right click, or clicked outside).")
        except:
            if not cfhExtensions.confirm(
                    "Please click in a window.\n"
                    "Continue?"):
                raise HF.RosterSelectionError("User cancelled operation (not a roster).")
        
def can_swap_activities():
    crews = []

    for area in range(Cui.CuiAreaN):
        crews += Cui.CuiGetCrew(Cui.gpc_info, area, "marked")

    return len(set(crews)) == 2
