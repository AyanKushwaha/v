#

#
"""
Functions to assign trip to/from etabs
"""

import os
import Cui
import String
import carmstd.cfhExtensions as cfhExtensions
import carmstd.planning as planning
import carmensystems.rave.api as r
import carmstd.rave as rave
import Errlog
import MenuCommandsExt
import HelperFunctions as HF
        
def tripsToEtab(workArea=Cui.CuiNoArea):
    """
    Stores locked trips starting in the planning period to an etable

    Handles crew position when assigning above/below rank or in extra position
    """
    report="SaveTripAssignments.output"
    dest="studio_assign.%table%"
    MenuCommandsExt.report2etab(report, dest, area=workArea)
         
def tripsFromEtab(workArea=Cui.CuiNoArea, scope='plan', flags=0):
    """
    Assign trips from an etable

    Limitation: Neither lock the trips nor handles work codes...
    """
    tripMap = planning.getTripName2TripId("studio_assign.%trip_unique_string%")
    crewposMap ={}
    
    # Fetch a map of crew function -> crew category (needed by Studio)
    # No context is needed
    raveExpr, = r.eval(r.foreach(r.times(12),r.expr('crew_pos.%index2func%'),r.expr('crew_pos.%index2cat%')))
    for loopId, func, cat in raveExpr:
        if cat:
            crewposMap[func] = cat

    # Fetch trip assignment data for all crew in the plan/window
    rc = rave.Context(workArea,scope)
    raveExpr, = rc.eval(r.foreach(r.iter('iterators.chain_set'),
                                  r.foreach(r.times('studio_assign.%crew_nr_preassignments%'),
                                            'crr_crew_id','studio_assign.%trip_string_ix%','studio_assign.%crew_func_ix%')))
    # Unwrap the data
    for loopId,data in raveExpr:
        for loopId2, crew, trip, func in data:
            # Assign the trips
            try:
                Cui.CuiAssignCrrByIdAt(Cui.gpc_info, crew, tripMap[trip],
                                       flags, crewposMap[func], func)
                Errlog.log("Assigned trip (%s,%s) to crew %s in func %s" % (trip, tripMap[trip], crew, func))
            except Exception, e:
                Errlog.log("Could not assign trip %s to crew %s in func %s" % (trip,crew,func))
                Errlog.log("Exception: %s" % e)            

def pactsToEtab(workArea=Cui.CuiNoArea):
    """
    Stores locked pacts starting in the planning period to an etable
    """
    report="SavePactAssignments.output"
    dest="studio_assign.%pact_table%"
    MenuCommandsExt.report2etab(report, dest, area=workArea)
         
def pactsFromEtab(workArea=Cui.CuiNoArea,scope='plan', flags=0):
    """
    Assign pacts from an etable
    """
    # Fetch trip assignment data for all crew in the plan/window
    rc = rave.Context(scope,workArea)
    raveExpr, = rc.eval(r.foreach(r.iter('iterators.chain_set'),
                                  r.foreach(r.times('studio_assign.%crew_nr_pact_preassignments%'),
                                               'crr_crew_id',
                                               'studio_assign.%pact_code_ix%',
                                               'studio_assign.%pact_start_etab_ix%',
                                               'studio_assign.%pact_end_etab_ix%',
                                               'crew.%homebase%')))
    #Unwrap the data
    for loopId, data in raveExpr:
        for crew, code, start, end, airport in data:
            try:
                #Assign the pact
                planning.assignPact(crew, code, start, end, False, airport)
                Errlog.log("Assigned pact (%s, %s,%s) to crew %s" % (code, start, end, crew))
            except Exception, e:
                Errlog.log("Failed assigning pact (%s, %s,%s) to crew %s" % (code, start, end, crew))
                Errlog.log("Exception: %s" % e)

def splitPacts(workArea=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope="window", selection="True"):
    """
    Splits all PACTs on the chains in the window
    that that matches the selection criteria
    (Rave expression).
    """
    rc = rave.Context(scope,workArea)
    filter = (selection,'studio_assign.%mps_possible_leg%','leg.%air_time% > 24:00')
    for leg_id in rc.getLegIdentifiers(filter):
        planning.splitOnePact(workArea,leg_id)
    return 0                                                             
    
def splitCurrentPact():
    """
    Splits the current PACT in the window
    """
    rc = rave.Context()
    id = rc.getCurrentLegIdentifier()
    return splitPacts(selection="leg_identifier = %s" % id)

def mergePacts(workArea=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope="window", selection="True"):
    """
    Merge all sequences of PACT in the specified scope
    that matches the specified selection criteria
    (a Rave expression).
    """
    rc = rave.Context(scope,workArea)
    filter = (selection,'studio_assign.%mps_first_identical_in_seq%')
    for leg_id in rc.getLegIdentifiers(filter):
        try:
            planning.mergeOnePactSeq(workArea,leg_id)
        except Exception, e:
            Errlog.log("Failed merging pact: %s" % leg_id)
            Errlog.log("%s" % e)
       
def trips2Pacts(workArea=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope="window",selection="True"):
    """
    Convert the current trips in the window to PACTs
    """
    rc = rave.Context(scope,workArea)
    filter = (selection,'not trip.%is_pact%','leg.%is_first_in_trip%')

    # Apply to first leg in each trip
    for leg_id in rc.getLegIdentifiers(filter):
        planning.trip2Pact(workArea,leg_id)
    return 0

def trips2PactsHomebase(workArea=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope="window",selection="True"):
    """
    Convert the current trips/pacts in the window to PACTs assigned at homebase
    """
    rc = rave.Context(scope,workArea)
    filter = (selection,'leg.%is_first_in_trip%')
    # Apply to first leg in each trip
    for leg_id in rc.getLegIdentifiers(filter):
        try:
            planning.trip2Pact(workArea,leg_id,"")
        except Exception, e:
            Errlog.log("Failed moving pact")
    return 0

def assignDummyPacts(workArea=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope="window",selection="True",
                     code="F", start=None):
    """
    Assign dummy pacts required by matador, fandango and homebase keywords
    """
    crewBaseMap = planning.getCrewMap("crew.%homebase%")
    if start==None:
        start = cfhExtensions.inputString("Date for dummy pacts (etab format)", 20)

    if start:
        end=start+" 0:01"
        rc = rave.Context(scope,workArea)
        for crew in rc.getCrewIdentifiers(selection):
            try:
                Errlog.log("Assigning pact (%s,%s,%s,%s) to crew %s" % (code, start, end, crewBaseMap[crew],crew))
                planning.assignPact(crew, code, start, end, False, crewBaseMap[crew])
            except Exception, e:
                Errlog.log("Failed assigning pact (%s, %s,%s) to crew %s" % (code, start, end, crew))
                Errlog.log("Exception: %s" % e)
    return 0

def currentTrip2Pact():
    """
    Convert the current trip in the window to a PACT
    """
    rc = rave.Context()
    leg_id = rc.getCurrentLegIdentifier()
    planning.trip2Pact(Cui.CuiWhichArea,"%s" % leg_id)

if __name__=='__main__':
    mergePacts()
    

def assign_any_position():
    FUNCTION = "Assign:: assign_any_position:: "
    trip_object = HF.TripObject()
    (school_flight, date, trip_id) = trip_object.eval(
        'trip.%has_school_flight%',
        'trip.%start_utc%',
        'crr_identifier')
    assign_positions = {}
    for i in range(7):
        (func, assign_func) = trip_object.eval(
            'crew_pos.%%pos2func%%(%s)' %(i+1),
            'studio_assign.%%assign_position%%(%s)' %(i+1))
        assign_positions[func] = assign_func
    # Wait for crew selection
    try:
        crew_area, crew_id, _ = HF.roster_selection()
    except HF.RosterSelectionError:
        quitMessage = "Interrupted by keyboard"
        Errlog.log(FUNCTION + quitMessage)
        return 1
    crew_object = HF.CrewObject(crew_id, crew_area)

    if school_flight:
        trip_type = "SCHOOL_FLIGHT"
    else:
        trip_type = "-"

    func, = crew_object.eval(
            'studio_assign.%%assign_rank%%("%s", %s)' %(trip_type, date))

    assign_func = assign_positions[func]
    if assign_func:
        try:
            Cui.CuiAssignCrrByIdAt(Cui.gpc_info,
                                   crew_id,
                                   str(trip_id),
                                   Cui.CUI_ASSIGN_CRR_BY_ID_CHECK_LEGALITY,
                                   assign_func,
                                   assign_func)
            remove_trip_if_no_need(trip_object)
            return 0
        except:
            Errlog.log(FUNCTION + ": User cancel, not assigned")
            return 1
    else:
        quitMessage = "No valid positions to assign in"
        Errlog.log(FUNCTION + quitMessage)
        cfhExtensions.show(quitMessage)
        return 1


def move_assignment(mode="KEEP_POS"):
    FUNCTION = "Assign:: move_assignment:: "
    area = Cui.CuiWhichArea

    trip_object = HF.TripObject()
    (src_crew, assigned_func, school_flight, date, trip_id) = trip_object.eval(
        'crew.%id%',
        'crew_pos.%trip_assigned_function%',
        'trip.%has_school_flight%',
        'trip.%start_utc%',
        'crr_identifier')

    # Wait for crew selection
    try:
        crew_area, crew_id, _ = HF.roster_selection()
    except HF.RosterSelectionError:
        quitMessage = "Interrupted by keyboard"
        Errlog.log(FUNCTION + quitMessage)
        return 1
    crew_object = HF.CrewObject(crew_id, crew_area)

    if school_flight:
        trip_type = "SCHOOL_FLIGHT"
    else:
        trip_type = "-"

    func, = crew_object.eval('studio_assign.%%assign_rank%%("%s", %s)' % (trip_type, date))

    flags = Cui.CUI_MOVE_ASMT_REMOVE_OVERLAPPING_CRRS | Cui.CUI_MOVE_ASMT_IGNORE_ASMT_POS_CHECK | Cui.CUI_MOVE_ASMT_CHANGE_POS_OK
    if mode == "KEEP_POS":
        assign_func = assigned_func
    elif mode == "CHANGE_POS":
        assign_func = func
    else:
        raise Exception('Faulty mode (%s) specified' % mode)

    try:
        Cui.CuiMoveAssignments(Cui.gpc_info, area, src_crew, crew_id, assign_func, assign_func, flags)
        return 0
    except:
        Errlog.log(FUNCTION + ": User cancel, not assigned")
        return 1


def remove_trip_if_no_need(trip_object):
    """Remove from trip window if need is zero. As fix for BZ 26445."""
    cc_vector, = trip_object.eval("crg_crew_pos.%trip_assigned_vector%"+\
                                  "(crg_crew_pos.AllCat, crg_crew_pos.SingleTrip)")
    cc = cc_vector.split("/")
    # Assumes a "n/n/n/n//n/n/n/n//n/n" vector, the "//" between
    # pos 4 and 5 means we can use self.pos (6 or 7) as index in cc.
    if len([x for x in cc if x not in ('', '0')]) == 0:
        # No crew complement, remove trip
        # kind == 3 -> chain is dissolved
        # last argument (flags) is currently ignored
        Cui.CuiRemoveCrr(Cui.gpc_info, trip_object.area, 3, 0)
        Cui.CuiScratchRefresh(Cui.gpc_info, trip_object.area)
