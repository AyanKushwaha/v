#
#$Header:$
#
__version__ = "$Revision:$"
"""
jcr_to_crewportal

Module for doing:

Generates the xml reply to these requests

1. get_rosters, xml tree naming:
       <ROSTER>
         <CRR>
          <RTD>
           <ACTIVITY>
           </ACTIVITY>
          </RTD>
         </CRR>
       </ROSTER>
2. get_all_trips
      <CRR>
       <RTD>
        <ACTIVITY>
        </ACTIVITY>
       </RTD>
      </CRR>
3. get_trips
   Same as get_all_trips

@date:10Feb2012
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


################
            
                    
import os
import xml_handler.treeelement_factory as tt
import  interbids.rostering.response as response_module 

# reload(tt)
# reload(response_module)
TT = tt.TreeElementFactory()

        
### PUBLIC METHODS ########################
def get_rosters(crew_ids):
    """
    Return the xml for crew portal
    If crewid is None, it will generate the rosters for all crew in plan, otherwise only for the one crew
    Will return error tag if crew is not found
    """
    response = RosterResponse()
    # get the rosters
    response.get_response(crew_ids)
    return response


def get_roster_carryout(crew_ids):
    """
    Return the xml for crew portal
    If crewid is None, it will generate the roster carryout for all crew in plan, otherwise only for the one crew
    Will return error tag if crew is not found
    """
    response = RosterCarryoutResponse()
    # get the rosters
    response.get_response(crew_ids)
    return response



def get_trips():
    """
    get all trips
    """
    # sofar just wrap request 'get_all_trips'
    return get_all_trips()

def get_all_trips():
    """
    get the trips xml for crew portal
    Has a filter defined in crr_filter to select subset of trips!
    Uses rave context sp_crr
    """
    # root for reply
    response = TripResponse()
    # create reply
    response.get_response()
    return response

    
#########  METHODS #####################

class RosterResponse(response_module.Response):
    '''
    Overload with the roster response node
    '''
    
    def __init__(self):
        '''
        Init super class and the set root to the getRosterResponse
        '''
        super(RosterResponse,self).__init__()
        self._root = TT.createGetRosterResponseElement()
    
    def get_response(self, crew):
        '''
        Call super class but append result to the root
        '''
        rosters = super(RosterResponse,self).get_rosters(crew)
        if rosters is None:
            self._errors.append('Crew %s not found'%crew)
        elif len(rosters) > 0:
            self.root.append(rosters)
        if self._errors:
            self.set_errors()


class RosterCarryoutResponse(response_module.Response):
    '''
    Overload with the roster carryout response node
    '''

    def __init__(self):
        '''
        Init super class and the set root to the getRosterResponse
        '''
        super(RosterCarryoutResponse, self).__init__()
        self._root = TT.createGetRosterCarryoutResponseElement()


    def get_response(self, crew):
        '''
        Call super class but append result to the root
        '''
        rosters = super(RosterCarryoutResponse, self).get_roster_carryouts(crew)
        if rosters is None:
            self._errors.append('Crew %s not found' % crew)
        elif len(rosters) > 0:
            self.root.append(rosters)
        if self._errors:
            self.set_errors()


class TripResponse(response_module.Response):
    '''
    Overload with the get trips response node
    '''
    
    def __init__(self):
        '''
        Init super class and the set root to the getTripsResponse
        '''
        super(TripResponse,self).__init__()
        self._root = TT.createGetAllTripsResponseElement()
    
    def get_response(self, *args, **kwds):
        '''
        Call super class but append result to the root
        '''
        trips = super(TripResponse,self).get_pbs(*args,**kwds)
        self.root.append(trips)
        if self._errors:
            self.set_errors()
        
################
