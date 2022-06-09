'''
Created on Feb 21, 2012

@author: pergr

'''
import re
import time
from AbsTime import AbsTime
from AbsDate import AbsDate
from datetime import datetime
from utils import etree

import interbids.rostering.xml_handler.constants as constants
reload(constants)
from constants import TRIP_NAMESPACE,\
    XSI_NAMESPACE, COMMON_NAMESPACE, FRAMEWORK_NAMESPACE, GETALLTRIPS_NAMESPACE,\
    REQUEST_NAMESPACE, GETROSTER_NAMESPACE, GET_ROSTER_RESPONSE,\
    GET_ALL_TRIPS_RESPONSE, GET_AVAILABLE_DAYSOFF_RESPONSE,\
    CREATE_DAYSOFF_RESPONSE, QUANTITY, POSITION,\
    GETROSTERCARRYOUT_NAMESPACE, GET_ROSTER_CARRYOUT_RESPONSE

##
## The ElementTree.register_namespace() method only exists in elementtree 1.3 which is included in
## python 2.7. Python 2.6 uses elementtree 1.2.x.
## This code snippet is introduced to register the namespaces to the elementtree regardless
## which version is currently running.
## more information can be found here: http://effbot.org/zone/element-namespaces.htm

nsmap = {'tp': TRIP_NAMESPACE,
         'xsi': XSI_NAMESPACE,
         'co': COMMON_NAMESPACE,
         'fw': FRAMEWORK_NAMESPACE,
         'gt': GETALLTRIPS_NAMESPACE,
         'rq': REQUEST_NAMESPACE,
         'gr': GETROSTER_NAMESPACE}

for (prefix, ns) in nsmap.items():
    etree.register_namespace(prefix, ns)

class TreeElementFactory(object):
    """
    Factory class for the ElementTree nodes in the reply
    """
    
    def createCreateRequestResponseElement(self):
        '''
        Create the root tag for create_request in namespace REQUEST_NAMESPACE
        '''
        return self.createNSElement(REQUEST_NAMESPACE,CREATE_DAYSOFF_RESPONSE )
    
    def createGetRosterResponseElement(self):
        '''
        Create root tag for get_roster using namespace GETROSTER_NAMESPACE
        '''
        return self.createNSElement(GETROSTER_NAMESPACE, GET_ROSTER_RESPONSE)

    def createGetRosterCarryoutResponseElement(self):
        '''
        Create root tag for get_roster_carryout using namespace GETROSTER_CARRYOUT_NAMESPACE
        '''
        return self.createNSElement(GETROSTERCARRYOUT_NAMESPACE, GET_ROSTER_CARRYOUT_RESPONSE)

    def createGetAllTripsResponseElement(self):
        '''
        Create root tag for get_roster using namespace GETALLTRIPS_NAMESPACE
        '''
        return self.createNSElement(GETALLTRIPS_NAMESPACE, GET_ALL_TRIPS_RESPONSE) 

    def createGetAvailableDaysOffResponseElement(self):
        '''
        Create root tag for get_roster using namespace REQUEST_NAMESPACE
        '''
        return self.createNSElement(REQUEST_NAMESPACE, GET_AVAILABLE_DAYSOFF_RESPONSE) 

    def createRostersElement(self):
        '''
        Use the GETROSTER_NAMESPACE namespace to create tag ROSTERS
        '''
        return self.createNSElement(GETROSTER_NAMESPACE, 'rosters')

    def createRosterElement(self):
        '''
        Use the GETROSTER_NAMESPACE namespace to create tag ROSTER
        '''
        return self.createNSElement(GETROSTER_NAMESPACE, 'roster')

    def createRosterCarryoutElement(self):
        '''
        Use the GETROSTER_NAMESPACE namespace to create tag ROSTER
        '''
        return self.createNSElement(GETROSTERCARRYOUT_NAMESPACE, 'roster')

    def createDaysOffResponseRosterElement(self):
        '''
        Use the REQUEST_NAMESPACE namespace to create tag ROSTER
        '''
        return self.createNSElement(REQUEST_NAMESPACE, 'roster')
    
    def createTripsElement(self):
        """
        Use the GETALLTRIPS_NAMESPACE namespace to create tag PBS
        """
        return self.createNSElement(GETALLTRIPS_NAMESPACE, 'PBS')

    def createTripElement(self):
        """
        Use the TRIP_NAMESPACE namespace to create tag CRR
        """
        return self.createNSElement(TRIP_NAMESPACE, 'CRR')

    def createDutyElement(self):
        """
        Use the TRIP_NAMESPACE namespace to create tag RTD
        """
        return self.createNSElement(TRIP_NAMESPACE, 'RTD')  

    def createLegElement(self):
        """
        Use the TRIP_NAMESPACE namespace to create tag ACTIVITY
        """
        return self.createNSElement(TRIP_NAMESPACE, 'ACTIVITY')  

    def createAttributesElement(self):
        '''
        Create attributes node in COMMON_NAMESPACE namespace
        @param name: name of attribute
        @type name: string  
        @param value:value to set
        @type value: string
        '''
        return self.createNSElement(TRIP_NAMESPACE, 'attributes')
        
    def createAttributeElement(self, name, value):
        '''
        Create attribute node in COMMON_NAMESPACE namespace
        @param name: name of attribute
        @type name: string  
        @param value:value to set
        @type value: string
        '''
        node =  self.createNSElement(COMMON_NAMESPACE, 'attribute')
        node.set('name', name)
        node.set('value', value)
        return node

    def createWarningsElement(self, warnings):
        '''
        Create the warnings node in correct namespace = FRAMEWORK_NAMESPACE
        @param warnings: list of warnings messages
        @type warnings: list
        '''
        warningElements = self.createNSElement(FRAMEWORK_NAMESPACE, 'warnings')
        for warning in warnings:
            warningElement = self.createNSElement(FRAMEWORK_NAMESPACE, 'warning')
            warningElement.text = warning
            warningElements.append(warningElement)
        return warningElement
    
    def createErrorsElement(self, errors):
        '''
        Create the errors node in correct namespace = FRAMEWORK_NAMESPACE
        @param errors: list of error messages
        @type errors: list
        '''
        errorsElement = self.createNSElement(FRAMEWORK_NAMESPACE, 'errors')
        for error in errors:
            errorElement = self.createNSElement(FRAMEWORK_NAMESPACE, 'error')
            errorElement.text = error
            errorsElement.append(errorElement)
        return errorsElement
    
    def createStatusElement(self, status):
        '''
        Cretae the satus node in GETALLTRIPS_NAMESPACE namespace 
        @param status: status message 
        @type status: string
        '''
        node = self.createNSElement(REQUEST_NAMESPACE, 'status')
        node.text = status
        return node

    def createDecisionTimeElement(self, decisionTime):
        '''
        Create the decisionTime  node in GETALLTRIPS_NAMESPACE namespace 
        @param status:decisionTime as string
        @type status: string
        '''                                                                         
        node = self.createNSElement(REQUEST_NAMESPACE, 'decisionTime')
        node.text = decisionTime
        return node
    
    def createAvailableDaysOffElement(self):
        '''
        Create the node for available days off in GETALLTRIPS_NAMESPACE namespace
        '''
        return self.createNSElement(REQUEST_NAMESPACE, 'availableDays')

    def createDayOffElement(self, date, value):
        '''
        Create the node for available single day off in GETALLTRIPS_NAMESPACE namespace
        @param date: date in string format
        @type date: string 
        @param value: number of days 
        @type value: int
        '''
        node = self.createNSElement(REQUEST_NAMESPACE, 'daysOffAvailable')
        node.set('date',date)
        node.set('slots',str(value))
        return node
    
    def createTripUpdatesElement(self):
        '''
        create the trips crew complement update node  
        '''
        node = self.createNSElement(REQUEST_NAMESPACE, 'tripUpdates')
        return node
    
    def createTripUpdateElement(self, tripid):
        '''
        create the trip crew complement update node
        this node goes under tripsUpdate   
        '''
        node = self.createNSElement(REQUEST_NAMESPACE, 'tripUpdate')
        node.set('uniqueid',tripid)
        return node
    
    def createCrewComplementsElement(self):
        '''
        Create the node for the crew complements 
        '''
        node = self.createNSElement(TRIP_NAMESPACE, 'crewComplementVector')
        return node
    
    def createCrewComplementElement(self, position, quantity):
        '''
        Create the node 
        '''
        node = self.createNSElement(TRIP_NAMESPACE, 'crewComplement')
        node.set(POSITION, position)
        node.set(QUANTITY, quantity)
        return node
    

    def createElement(self, sName):
        return etree.Element(sName)
    
    def createNSElement(self, namespace, name):
        '''
        Create an Element in namespace with tag name
        @param namespace: Name of namespace (full uri)
        @param name: name of tag
        '''
        return etree.createNSElement(namespace, name, nsmap=nsmap)

    @classmethod
    def convertValueToString(cls, val):
        if isinstance(val, AbsTime):
            return datetime(*val.split()).strftime('%Y-%m-%d %H:%M')
        if isinstance(val, AbsDate):
            return datetime(*val.split()).strftime('%Y-%m-%d')
        return str(val)

    @classmethod
    def convertStringToValue(cls, text):
        if re.match('^\d\d\d\d-\d\d-\d\d \d\d:\d\d$', text):
            ts = datetime(*time.strptime(text, '%Y-%m-%d %H:%M')[:6])
            return AbsTime(ts.year, ts.month, ts.day, ts.hour, ts.minute)
        if re.match('^\d\d\d\d-\d\d-\d\d$', text):
            ts = datetime(*time.strptime(text, '%Y-%m-%d')[:6])
            return AbsTime(ts.year, ts.month, ts.day, 0, 0)
        return text
    
