#######################################################

# Planning.py
# -----------------------------------------------------
# Application: Studio
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
This module contains functionality for assigning
and deassigning objects. 
"""
import AbsTime
import carmensystems.rave.api as r
import Errlog
import Cui


def splitOnePact(area,leg_id):
    """
    Splits a pact with the leg_id
    """
    # Get values for the pact
    # Note: We have to use Cui functions for evaluating rave code here since
    #       we want to evaluate the code on a segement in e.g. a roster and
    #       this is not possible in the Rave Api
    flags=Cui.CUI_CREATE_PACT_DONT_CONFIRM|Cui.CUI_CREATE_PACT_SILENT|Cui.CUI_CREATE_PACT_NO_LEGALITY|Cui.CUI_CREATE_PACT_TASKTAB 
    Cui.CuiSetSelectionObject(Cui.gpc_info,area,Cui.LegMode,leg_id)

    crewid     = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "crr_crew_id")
    code        = Cui.CuiCrcEvalString(Cui.gpc_info, area,
                                       "OBJECT", "trip.%code%")
    start      = Cui.CuiCrcEval(Cui.gpc_info, area,
                                "OBJECT", 'studio_assign.%trip_departure_time_lt%')
    end        = Cui.CuiCrcEval(Cui.gpc_info, area,
                                "OBJECT", 'studio_assign.%trip_arrival_time_lt%')
    airport     = Cui.CuiCrcEvalString(Cui.gpc_info, area,
                                       "OBJECT", "arrival_airport_name")
    # Remove the PACT
    Cui.CuiDeassignCrr(Cui.gpc_info, area, Cui.CUI_DEASSIGN_SILENT|Cui.CUI_DEASSIGN_NO_REDRAW)  
    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crewid)

    # Create a new object.
    assignPact(crewid,code,start,end,True,airport,flags)

def mergeOnePactSeq(area,first_leg_id,flags=Cui.CUI_CREATE_PACT_DONT_CONFIRM|Cui.CUI_CREATE_PACT_SILENT|Cui.CUI_CREATE_PACT_NO_LEGALITY|Cui.CUI_CREATE_PACT_TASKTAB):
    """
    Merge identical sequential off duty PACT objects into one large
    """

    # Get values for the pact sequence	

    Cui.CuiSetSelectionObject(Cui.gpc_info,area,Cui.LegMode,first_leg_id)
 
    crewid     = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "crr_crew_id")
    code        = Cui.CuiCrcEvalString(Cui.gpc_info, area,
                                       "OBJECT", "trip.%code%")
    start      = Cui.CuiCrcEval(Cui.gpc_info, area,
                                       "OBJECT", 'studio_assign.%trip_departure_time_lt%')
    end        = Cui.CuiCrcEval(Cui.gpc_info, area,
                                       "OBJECT", 'studio_assign.%mps_end_abstime%')
    airport     = Cui.CuiCrcEvalString(Cui.gpc_info, area,
                                       "OBJECT", "arrival_airport_name")

    # Remove all objects in the pact seq.
    num_objects = Cui.CuiCrcEvalInt(Cui.gpc_info, area,
                                    "OBJECT", 'studio_assign.%pact_split_nr_legs%')

    if num_objects>1:
        for i in xrange(num_objects):
            id = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "studio_assign.%mps_next_leg_id%")
            Cui.CuiDeassignCrr(Cui.gpc_info, area, Cui.CUI_DEASSIGN_SILENT|Cui.CUI_DEASSIGN_NO_REDRAW)  
            if id: Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, id)

        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crewid)

        # Create a new large object.
        assignPact(crewid,code,start,end,False,airport,flags)
 

def assignPact(crewId,code,start,end,dayByDay=False, airport="",flags=Cui.CUI_CREATE_PACT_DONT_CONFIRM|Cui.CUI_CREATE_PACT_SILENT|Cui.CUI_CREATE_PACT_NO_LEGALITY|Cui.CUI_CREATE_PACT_TASKTAB):
    """
    Assigns a Pact or a sequence of identical pacts to a crew member

    crewId: String crr_crew_id of the crew member
    code:   String Code of the preassignment
    start:  BSIRAP Abstime: Start of the preassignment (in etab format or as an integer)
    end:    BSIRAP Abstime: End of the preassignment   (in etab format or as an integer)
    dayByDay: BOOL split the pact into equal pacts shorter than 24h.
    airport: String "" will default to crew base when the pact starts (from rave)
    flags:  see the man page for Cui

    returns: 1 if assignment is done, 0 otherwise

    Ex. assignPact("1234","PTO","AbsTime.AbsTime('1nov2004')", "AbsTime.AbsTime('3nov2004 15:00')" ,True,"CPH")
    """
    if isinstance(start,AbsTime.AbsTime):
        s = start.getRep()
    else:
        s = AbsTime.AbsTime(start).getRep()

    if isinstance(end,AbsTime.AbsTime):
        e = end.getRep()
    else:
        e = AbsTime.AbsTime(end).getRep()

    n=1
    try:
        if dayByDay:
            # Let each dayByDay pact be <= 24h
            n=(e-s+23*60+59)/(24 * 60)

            # time of day
            s1=s % (24*60)
            e1=e % (24*60)
            # calculate the end of the first small pact
            if e1 > s1:
                e=s+e1-s1
            # Add 24h if the time_of_day for start is after the end
            else:
                e=s+e1-s1+(24*60)
                
            # print "AssignPact(legX%s): start: %s, end: %s)" % (n,s,e)
        for i in range(n):
            # print "AssignPact(%d): start: %s, end: %s)" % (i,s,e)
            Cui.CuiCreatePact(Cui.gpc_info,crewId,code,"",int(s),int(e),airport,flags)
            s+=24*60
            e+=24*60
    except Exception, e1:
        Errlog.log("assignPact(%s,%s,%s,%s,%s,%s)" % (crewId, code,start,end,airport,flags))
        Errlog.log("assignPact(%s): start: %s, end: %s)" % (n,s,e))
        raise e1    

def assignTrip(crewId,tripId,flags=2,mcat=0,ccat=0):
    """
    Assigns a trip to a crew member

    crewId: crr_crew_id of the crew member
    tripId: carmen_unique_crr_id of the trip
    flags:
    mcat:   MainCat of the crew member (0 means use MainCat in the crew table))
    ccat:   Crew Position of the crew member (0 means use the MainFunction in the crew table)

    returns: 1 if assignment is done, 0 otherwise

    ex. assignTrip("1234","12","C","CP")
    """
    try:
        Cui.CuiAssignCrrByIdAt(Cui.gpc_info, crewId, tripId, flags, mcat, ccat)
    except:
        Errlog.log("assigningTrip(%s,%s,%s,%s,%s)" % (crewId, tripId, glags, mcat, ccat))

def deassignTrip(crewId,tripId):
    """
    Deassigns a trip from a crew member

    crewId: crr_crew_id of the crew member
    tripId: camren_unique_crr_id of the trip to deassign
    """
    try:
        print "Not yet implemented!!!!"
    except:
        Errlog.log("deassigningTrip(%s,%s)" %  (crewId, tripId))

def trip2Pact(area,leg_id, airport=None, flags=Cui.CUI_CREATE_PACT_DONT_CONFIRM|Cui.CUI_CREATE_PACT_SILENT|Cui.CUI_CREATE_PACT_NO_LEGALITY):
    """
    Deassign current trip (or pact) and create a pact instead.
    airport: ""   -> use crew.%homebase% 
             other value -> hard code to other value
    Locked trips: If a trip is locked, the trip is not transformed. 
    """

    # Get values for the pact	
    Cui.CuiSetSelectionObject(Cui.gpc_info,area,Cui.LegMode,leg_id)

    crewid = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "crr_crew_id")
    code = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "trip.%code%")
    start = Cui.CuiCrcEval(Cui.gpc_info, area, "OBJECT", 'studio_assign.%trip_departure_time_lt%')
    end = Cui.CuiCrcEval(Cui.gpc_info, area, "OBJECT", 'studio_assign.%trip_arrival_time_lt%')

    if airport=="":
        airport    = Cui.CuiCrcEvalString(Cui.gpc_info, area, "OBJECT", "crew.%homebase%")
        
    try:
        # Remove the Trip
        Cui.CuiDeassignCrr(Cui.gpc_info, area, Cui.CUI_DEASSIGN_SILENT|Cui.CUI_DEASSIGN_NO_REDRAW)  
        # Should also decrease booked value
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crewid)
        # Create a new object.
        assignPact(crewid,code,start,end,False,airport,flags)
    except:
        #Locked trips
        pass
    
if __name__=="__main__":
    assignments={
        "1234":[["VA",12,13],["Trip","12R1891"]]
        }
    for crew in assignments.keys():
        for ass in assignments[crew]:
            if ass[0]=="Trip": 
                print "trip" 
            else:
                print ass[0] 
    assignPact("1234","PTO",1475,1675,"CPH")
    assignTrip("1234","12","C","CP")
    deassignTrip("1234","12")
