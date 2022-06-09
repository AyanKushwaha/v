
#
# Purpose: Get transport, displays in a new view all rosters with transport arriving/departing before/after
#          the pointed leg 
#

from utils.rave import RaveIterator
import Cui
import carmusr.HelperFunctions as HF
import carmstd.studio.area as StdArea
import modelserver as M
import RelTime

debugOutput = 0

def selectCrew(fromStation= ""):

    # The info fields needs to be defined within a class. 
    class CrewInfo:
        fields = {"id": "crew.%id%"}
    class LegInfo:
        fields = {
            "leg_id": "leg_identifier",
            "arr_station": "arrival_airport_name",
            "dep_station": "departure_airport_name",
            "arr_time": "arrival",
            "dep_time": "departure"
            }
    
    # Set the area
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # Find some key values regarding the selected leg.
    baseLegId = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "leg_identifier") 
    departureTime = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "departure") 
    arrivalTime = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "arrival")
    arrivalAirport = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "arrival_airport_name")
    departureAirport = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "departure_airport_name")
        # Get the current leg crew id.
    Cui.CuiGetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, str(baseLegId))
    
    # Gap where ground transport legs are to be found (+/- 12 hours).
    timeGap = RelTime.RelTime(1*12,0)
    latestDeparture = arrivalTime + timeGap
    earliestArrival = departureTime - timeGap
    
    # Get the ground transportation codes.
    transType = tuple(getTransportCodes("GT"))

    if debugOutput == 1:
        print
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print 'Selected leg departure airport:      ', departureAirport
        print 'Selected leg arrival airport:        ', arrivalAirport
        print 'Ids for ground transport group (GT): ', transType
        print 'Earliest arrival:                    ', earliestArrival
        print 'Latest departure:                    ', latestDeparture
        print 'Ground transport:'
        
    flight_condition = ('fundamental.%is_roster%', \
                        'pp_start_time<=departure', \
                        'pp_end_time>=arrival', \
                        'studio_select.%%leg_has_activity_code%%("%s")' % transType)
    crew_condition = list(flight_condition)
    if fromStation:
        crew_condition.append('departure>%s' % arrivalTime)
        crew_condition.append('departure<=%s' % latestDeparture)
        crew_condition.append('leg.%%start_station%% = "%s"' % arrivalAirport)
        sortStm = ('leg.%start_UTC%')
    else:
        crew_condition.append('arrival<%s' % departureTime)
        crew_condition.append('arrival>=%s' % earliestArrival)
        crew_condition.append('leg.%%end_station%% = "%s"' % departureAirport)
        sortStm = ('leg.%end_UTC%')

    crew_condition = tuple(crew_condition)

    # Find all crew using the rave util.        
    fi = RaveIterator(RaveIterator.iter("iterators.leg_set",
                                     where=flight_condition,
                                     sort_by=sortStm), LegInfo())
    ci = RaveIterator(RaveIterator.iter('iterators.leg_set',
                                     where=crew_condition,
                                     ), CrewInfo())
    fi.link(ci)
    legs = fi.eval('sp_crew')

    crewList = []
    legIdlist = []
    for leg in legs:
        for crew in leg.chain():
            
            if debugOutput == 1:
                print '   Crew id: ', crew.id
                
            legIdlist.append(leg.leg_id)
            crewList.append(crew.id)
            
        if debugOutput == 1:
            print '       Departure station: ', leg.dep_station
            print '       Arrival station:   ', leg.arr_station
            print '       Departure time:    ', leg.dep_time
            print '       Arrival time:      ', leg.arr_time
            print '       Leg Ident:         ', leg.leg_id
    
    if debugOutput == 1:
        print 'List of crew with ground transport conditions: ', crewList
        
    if len(crewList) > 0:

        # Mark ground transport legs.
        
        if debugOutput == 1:
            print 'List of leg ids for ground transport conditions:'
            
        for legId in legIdlist:
            
            if debugOutput == 1:
                print '                          ', legId
        
            area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(legId))
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'OBJECT')
            Cui.CuiMarkLegs(Cui.gpc_info, area, "object", Cui.CUI_MARK_SET)
        
    displayListOfCrew(crewList)

    if debugOutput == 1:
        print
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
            
def displayListOfCrew(crewIds):
    """
        Displays the crew in crewIds in the current window.
    """
    numCrews = len(crewIds)

    # Get the first available/empty area.
    useArea = findArea()
    Cui.CuiSetCurrentArea(Cui.gpc_info, useArea)
    useArea = Cui.CuiAreaIdConvert(Cui.gpc_info, useArea)
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                useArea,
                                Cui.CrewMode,
                                Cui.CrewMode,
                                crewIds)
    if numCrews > 0:
        HF.redrawAreaScrollHome(useArea)

    StdArea.promptPush(str(numCrews)+" crew selected and "+ \
                                                "replaced the content"+\
                        " in the window.")
def areaExists(area):
    """
        Verifies if a window area exists.
    """
    return not Cui.CuiAreaExists({"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info, area)

def findArea():
    """
        Find an available area, if none, use first with crew mode, but not the current one.
    """
    currArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    useArea = -1
    areaCtrl = {}
    for area in range(Cui.CuiAreaN):
        mode = Cui.CuiGetAreaMode(Cui.gpc_info, area)
        exists = areaExists(area)
        areaCtrl[area] = [mode, exists]
        
        if debugOutput == 1:
            print 'Area: %s - Mode: %s - Exists: %s' % (area, areaCtrl[area][0], areaCtrl[area][1])
            
        if mode == 0:
            useArea = area 
            break
    if not areaExists(useArea):            
        try:
            Cui.CuiOpenArea(Cui.gpc_info)
        except:
            useArea = Cui.CuiAreaN - 1
            for selArea in areaCtrl.keys():
                if areaCtrl[selArea][0] == 5 and not selArea == currArea:
                    useArea = selArea
                    break                    
    return useArea

def selectTo(loc=0):
    selectCrew(fromStation=loc)

def selectFrom(loc=1):
    selectCrew(fromStation=loc)

