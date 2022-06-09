
# [acosta:08/101@11:38] Slightly modified, uses selection utility in different module.

"""
Functions for manipulating (removing) activities
"""

import Cui
import Select
import carmstd.cfhExtensions
import carmstd.rave
import carmusr.HelperFunctions as HF
import carmensystems.rave.api as R
import carmusr.tracking.Deassign as Deassign

def removeActivities(day_by_day=False):
    """ 
    Removes all assignments for crew between selected start and end time.
    Start and end time are rounded to whole days (home base days).  UTC is used
    when deassigning activities.  If the day_by_day variable is set to True
    only one click is done and the selected day will be removed.

    PACTs that are covering several days will be adjusted (cut) and the selected
    interval will appear as a "hole" in the roster.
    """
    crewArea = Cui.CuiGetAreaInMode(Cui.gpc_info, Cui.CrewMode, Cui.CuiNoArea)
    if crewArea == Cui.CuiNoArea:
        carmstd.cfhExtensions.show("There must be an open Roster window")
        return 1
    
    if day_by_day:
        selection = HF.RosterDaySelection
    else:
        selection = HF.RosterDateSelection

    try:
        sel = selection(hb=True)
        return deleteActivityInPeriod(sel.crew, HF.utc2hb(sel.crew, sel.st),
                                      HF.utc2hb(sel.crew, sel.et), area=crewArea)
    except Exception, e:
        print "removeActivities: Exception:", e
        return -1


def deleteActivityInPeriod(crewId, startTimeHB, endTimeHB,
                           beforeCode=None, afterCode=None, area=Cui.CuiWhichArea, codesToDelete=None, keptLegs=None):
    """
    Remove activities within selected interval.
    IMPORTANT: startTimeHB and endTimeHB must be in local (homebase) time!

    If a PACT is partly covered by the selected interval, then the activity
    will be adjusted.

    E.g.
        |========VA=========|      before
            x---------x            selected time interval
        |VA|           |=VA=|      after
    """

    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    
    crew_object = HF.CrewObject(str(crewId), area)
    
    beforeStart = None
    beforeEnd = None
    beforeAirport = None
    afterStart = None
    afterEnd = None
    afterAirport = None
    

    leg_ids, =  crew_object.eval(R.foreach(R.iter('iterators.leg_set',
                                                  where=('leg.%%start_hb%%< %s' % endTimeHB,
                                                         'leg.%%end_hb%% > %s' % startTimeHB)),
                                           'leg_identifier'))
    leg_ids = [leg_id for (ix, leg_id) in leg_ids]
    leg_to_delete_ids = []
    legs_to_keep = []
    
    for legId in leg_ids:
        leg_object = HF.LegObject(str(legId), area)
        (start,end,code, airport) = leg_object.eval('leg.%start_hb%',
                                                    'leg.%end_hb%',
                                                    'leg.%code%',
                                                    'arrival_airport_name')

        if codesToDelete != None:
            if not code in codesToDelete:
                if keptLegs != None:
                    keptLegs.append((start, end, code, airport))
                continue

        leg_to_delete_ids.append(legId)

        if code != 'FLT':
            if start < startTimeHB and end > endTimeHB:
                beforeStart = start
                beforeEnd = startTimeHB
                if not beforeCode:
                    beforeCode = code
                beforeAirport = airport
                afterStart = endTimeHB
                afterEnd = end
                if not afterCode:
                    afterCode = code
                afterAirport = airport
                break
            elif start < startTimeHB:
                beforeStart = start
                beforeEnd = startTimeHB
                if not beforeCode:
                    beforeCode = code
                beforeAirport = airport
            elif end > endTimeHB:
                afterStart = endTimeHB
                afterEnd = end
                if not afterCode:
                    afterCode = code 
                afterAirport = airport
        else:
            continue

        if beforeStart and afterStart:
            break
            
    # Remove pact (requires marking of legs; restore existing marks afterwards)
    marked_legs_to_retain = HF.getMarkedLegs(area)
    HF.unmarkAllLegs(area)
    try:
        HF.markLegs(area, leg_to_delete_ids)
        Deassign.deassign(area)
    finally:
        HF.markLegs(area, marked_legs_to_retain)
        
    # Recreate part of pact
    if beforeStart is not None:
        Cui.CuiCreatePact(Cui.gpc_info, crewId, str(beforeCode), '',
                beforeStart.getRep(), beforeEnd.getRep(), str(beforeAirport),
                Cui.CUI_CREATE_PACT_DONT_CONFIRM | Cui.CUI_CREATE_PACT_SILENT \
                | Cui.CUI_CREATE_PACT_NO_LEGALITY)

    if afterStart is not None:
        Cui.CuiCreatePact(Cui.gpc_info, crewId, str(afterCode), '',
                afterStart.getRep(), afterEnd.getRep(), str(afterAirport),
                Cui.CUI_CREATE_PACT_DONT_CONFIRM | Cui.CUI_CREATE_PACT_SILENT \
                | Cui.CUI_CREATE_PACT_NO_LEGALITY)
        
    return 0


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
