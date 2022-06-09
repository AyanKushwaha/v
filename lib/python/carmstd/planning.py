#######################################################

# Planning.py
# -----------------------------------------------------
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
This module contains functionality for assigning
and deassigning objects. The API is application
independent and an be imported in either studio or
matador. If a certain functionality is not supported
by the application, an exception will be raised.
"""

import carmensystems.rave.api as r
from application import application
if application=="Matador":
    import carmstd.matador.planning as planning
else:
    import carmstd.studio.planning as planning


def splitOnePact(area, leg_id):
    """
    Splits a pact with the specified leg_id
    Only valid for Studio

    Arguments:
      area: Studio area defined in Cui ,e.g. Cui.CuiArea1
      leg_id: string of the leg identifier
    """
    planning.splitOnePact(area,leg_id)
        
def mergeOnePactSeq(area, leg_id):
    """
    Merge identical sequential off duty PACT objects into one large
    Only valid for Studio

    Arguments:
      area: Studio area defined in Cui ,e.g. Cui.CuiArea1
      leg_id: string of the leg identifier
    """
    planning.mergeOnePactSeq(area,leg_id)
        
def assignPact(crewId,code,start,end,dayByDay=False, airport=""):
    """
    Assign a PACT to a crew with crewId specified
    Assigns a Pact or a sequence of identical pacts to a crew member

    Arguments:
      crewId: String crr_crew_id of the crew member
      code:   String Code of the preassignment
      start:  BSIRAP Abstime: Start of the preassignment (in etab format or as an integer)
      end:    BSIRAP Abstime: End of the preassignment   (in etab format or as an integer)
      dayByDay: BOOL split the pact into equal pacts shorter than 24h.
      airport: String "" will default to crew base when the pact starts (from rave)
        
    Ex. assignPact("1234","PTO","AbsTime.AbsTime('1nov2004')", "AbsTime.AbsTime('3nov2004 15:00')" ,True,"CPH")
    """
    planning.assignPact(crewId,code,start,end,dayByDay=False, airport="")
        
def assignTrip(crewId,tripId,flags=2,mcat=0,ccat=0):
    """
    Assigns a trip to a crew member
    
    crewId: crr_crew_id of the crew member
    tripId: carmen_unique_crr_id of the trip
    flags:
    mcat:   Int MainCat of the crew member (0 means use MainCat in the crew table))
    ccat:   Int Crew Position of the crew member (0 means use the MainFunction in the crew table)
    
    returns: 1 if assignment is done, 0 otherwise
    
    ex. assignTrip("1234","12","C","CP")
    """
    planning.assignTrip(crewId,tripId,flags,mcat,ccat)
        
def deassignTrip(crewId,tripId):
    """
    Deassigns the trip with the trip id from the crew with the
    specified crew Id
    Arguments:
      crewId: String
      tripId:
    """
    planning.deassignTrip(crewId,tripId)
    
def trip2Pact(area,leg_id, airport=None):
    """
    Deassign current trip (or pact) and create a pact instead.
    If a trip is locked, the trip is not transformed.
    Only valid for Studio
    
    Arguments:
      area: Studio area defined in Cui ,e.g. Cui.CuiArea1
      leg_id: String of the leg_identifier 
      airport: String. ""   -> use crew.%homebase% 
               other value -> hard code to other value

    """ 
    planning.trip2Pact(area,leg_id, airport)


def getTripName2TripId(trip_name="crr_name"):
    """
    Create a map with trip names ==> carmen_unique_crr_id
    tripname: a rave expression that identifies a trip, default crr_name
    returns: an hashtab containing the map
    """
    resultDict = {}
    raveExp, = r.eval('sp_crrs',r.foreach(r.iter('iterators.trip_set'),r.expr(trip_name),'crr_identifier'))

    for loopId, tripName, identifier in raveExp:
        resultDict[tripName] = identifier

    return resultDict

def getCrewMap(expr):
    """
    Create a map with crewid ==> <expression>
    returns: an hashtab containing the map
    """
    resultDict = {}
    raveExp, = r.eval('sp_crew',r.foreach(r.iter('iterators.chain_set'),'crr_crew_id',r.expr(expr)))

    for loopId, crewId, raveValue in raveExp:
        resultDict[crewId] = raveValue

    return resultDict
