'''
Created on Feb 27, 2012

@author: pergr
'''
# Used for debugging when we want flat file response
# import interbids.rostering.dummy_data_repo as dummy_data_repo
import interbids.rostering.roster_trip_response_handler as roster_trip_response_handler
import interbids.rostering.days_off_response_handler as days_off_response_handler
from utils import etree

from interbids.rostering.xml_handler.constants import  GET_ROSTER_REQUEST,\
    GETROSTER_NAMESPACE, GETALLTRIPS_NAMESPACE, GET_ALL_TRIPS_REQUEST,\
    CREW_ID_TAG, GET_AVAILABLE_DAYSOFF_REQUEST, FRAMEWORK_NAMESPACE,\
    CATEGORY_TAG, REQUEST_NAMESPACE, INTERVAL_TAG, FROM_TAG, TO_TAG, GET_ROSTERS,\
    GET_ALL_TRIPS, GET_TRIPS, GET_AVAILABLE_DAYS_OFF, MODEL_ENCODING, VERSION,\
    CREATE_REQUEST, CANCEL_REQUEST, CREATE_DAYSOFF_REQUEST, TYPE_TAG,\
    ATTRIBUTES_TAG, COMMON_NAMESPACE, ATTRIBUTE_TAG, NAME_TAG, STARTTIME_TAG, STARTDATE_TAG,\
    VALUE_TAG, DURATION_TAG, PERIOD, \
    GETROSTERCARRYOUT_NAMESPACE, GET_ROSTER_CARRYOUT_REQUEST
from xml.dom import minidom
import StringIO
import os
import os.path
import time
import Cui
    

class ParseAndServiceRequest(object):
    '''
    Class to parse the message and set call method handler
    '''

    def __init__(self, xml_string):
        # reload(roster_trip_response_handler)
        # reload(days_off_response_handler)
        self._xml = xml_string
        #impl. parsers
        self._parse_impls = [self._get_rosters,
                             self._get_all_trips,
                             self._get_available_days_off,
                             self._create_request,
                             self._get_roster_carryout]
        # check all implementations
        self._crewid='Unknown_crew'
        
    def get_crewid(self):
        '''
        return crew id that we have gotten from parsers
        '''
        return self._crewid
        
    def init_rave_parameters(self):
        """
        set the correct rave parameter set
        """
        #import Variable
        #Cui.CuiCrcLoadRuleset(Cui.gpc_info, "Tracking")
        #print "Before", variable.value
        Cui.CuiCrcLoadParameterSet(Cui.gpc_info,
                                   os.path.join(os.environ.get('CARMUSR'),
                                                'crc',
                                                'parameters',
                                                'tracking',
                                                'request_reportserver'),
                                   Cui.CUI_LOAD_PARAMETERS_NO_SP_CHANGE) 
        
        # variable = Variable.Variable("")
        # Cui.CuiCrcGetParameterSetName(variable)
        # print "after", variable.value    
        
    def __call__(self):
        '''
        Try to parse the request and return the response for correcr method handler
        '''

        self.init_rave_parameters()

        # Minidom can be slow and memory hungry but requests are short and hard like a bodybuilding elf
        doc = minidom.parse(StringIO.StringIO(self._xml))


        # loop through the added methods
        for handler in self._parse_impls:
            response = handler(doc)
            if response is not None:
                if response.use_conflict_handling:
                    (resp_xml, conflicts) = self.format_response(response), response.get_conflicts()
                    return (resp_xml, conflicts)
                else:
                    resp_xml = self.format_response(response) #no conflicts right now
                    return resp_xml

        # ok, this is not where we wanted to end up
        raise NotImplementedError('Handler has no implementation for %s'%self._xml)
                
    def format_response(self, response):
        '''
        @param response: Response
        @type response: L{Response}
        '''
        return etree.tostring(response.root, encoding="UTF-8")

    def _get_rosters(self, doc):
        '''
        Create response if request is get_roster
        XML format example
        is found in test case in inetrbids.rostering.test.test_get_roster.py
            
        @param doc: element root of request
        @type doc: DOM element
        '''
        # see if we find request in message
        # if not just do an empty return
        # Test get_roster 
        request = self._get_first_elementByTagNameNS(doc,
                                                      GETROSTER_NAMESPACE,
                                                      GET_ROSTER_REQUEST)
        if request:
            # get crew id
            # DOM uses unicode decodings
            self._crewid = request.attributes.getNamedItem(CREW_ID_TAG).value.encode(MODEL_ENCODING)
            # get the rosters
            # reload(roster_trip_response_handler)
            return roster_trip_response_handler.get_rosters(self._crewid) #selected crew
        return None


    def _get_roster_carryout(self, doc):
        '''
        Create response if request is get_roster_carryout

        @param doc: element root of request
        @type doc: DOM element
        '''
        request = self._get_first_elementByTagNameNS(doc,
                                                     GETROSTERCARRYOUT_NAMESPACE,
                                                     GET_ROSTER_CARRYOUT_REQUEST)
        # see if we find request in message
        # if not just do an empty return
        if request:
            # get crew id
            # DOM uses unicode decodings
            self._crewid = request.attributes.getNamedItem(CREW_ID_TAG).value.encode(MODEL_ENCODING)
            # get the roster carryout
            # reload(roster_trip_response_handler)
            return roster_trip_response_handler.get_roster_carryout(self._crewid) #selected crew
        return None


    def _get_all_trips(self, doc):
        '''
        Create response if request is get_all_trips
        XML format example
        is found in test case in inetrbids.rostering.test.test_get_roster.py
        @param doc: element root of request
        @type doc: DOM element
        '''
        # see if we find request in message
        # if not just do an empty return
        # test get trips
        request = self._get_first_elementByTagNameNS(doc,
                                                     GETALLTRIPS_NAMESPACE,
                                                     GET_ALL_TRIPS_REQUEST)
        if request:
            return roster_trip_response_handler.get_all_trips()
        return None


    def _get_available_days_off(self, doc):
        '''
        Create response if request is get_available_days_off
        XML format example
        is found in test case in inetrbids.rostering.test.test_get_roster.py
        @param doc: element root of request
        @type doc: DOM element
        '''
        # see if we find request in message
        # if not just do an empty return
 
        request = self._get_first_elementByTagNameNS(doc,
                                                      REQUEST_NAMESPACE,
                                                      GET_AVAILABLE_DAYSOFF_REQUEST)
        # variable init
        bidtype = start = end = None
        
        if request:
            # DOM uses unicode decodings
            self._crewid = request.attributes.getNamedItem(CREW_ID_TAG).value.encode(MODEL_ENCODING)
            bidtype = request.attributes.getNamedItem(CATEGORY_TAG).value.encode(MODEL_ENCODING)
            # Remove prefix (e.g. A_, B_) in bidtype. The prefix is set to do custom sorting of the types in the crew portal
            if "_" in bidtype:
                bidtype = bidtype[bidtype.index("_")+1:]
            interval =  self._get_first_elementByTagNameNS(request,
                                                            REQUEST_NAMESPACE,      
                                                            INTERVAL_TAG)
            # assignment start end time
            if interval:
                start = self._dom_unpack_text_node(self._get_first_elementByTagNameNS(interval,
                                                                                        FRAMEWORK_NAMESPACE,
                                                                                        FROM_TAG),
                                                    transcode=True)                       
                end = self._dom_unpack_text_node(self._get_first_elementByTagNameNS(interval,
                                                                                      FRAMEWORK_NAMESPACE,
                                                                                      TO_TAG),
                                                  transcode=True)  
            return days_off_response_handler.get_available_days_off(self._crewid, bidtype, start, end)
        return None

    def _create_request(self, doc):
        '''
        Try to parse the create days off request
        XML format example
        is found in test case in inetrbids.rostering.test.test_get_roster.py
        @param doc:
        @type doc:
        '''
        # get the request
        request = self._get_first_elementByTagNameNS(doc,
                                                      REQUEST_NAMESPACE,
                                                      CREATE_DAYSOFF_REQUEST)
        # variable init
        bidtype = period_start = period_end = start = end = None
        
        # if we got a request
        if request:
            # DOM uses unicode decodings
            self._crewid = request.attributes.getNamedItem(CREW_ID_TAG).value.encode(MODEL_ENCODING)
            bidtype = request.attributes.getNamedItem(TYPE_TAG).value.encode(MODEL_ENCODING)
            # Remove prefix (e.g. A_, B_) in bidtype. The prefix is set to do custom sorting of the types in the crew portal
            if "_" in bidtype:
                bidtype = bidtype[bidtype.index("_")+1:]
            
            # get the period from request
            period = self._get_first_elementByTagNameNS(request,
                                                         REQUEST_NAMESPACE,
                                                         PERIOD)
            # unpack period start/end (used to get available days off)
            if period:
                # stored as text in node, (convert from UNICODE)
                period_start = self._dom_unpack_text_node(self._get_first_elementByTagNameNS(request,
                                                                                               FRAMEWORK_NAMESPACE,
                                                                                               FROM_TAG),
                                                           transcode=True)
                # stored as text in node, (convert from UNICODE)
                period_end = self._dom_unpack_text_node(self._get_first_elementByTagNameNS(request,
                                                                                             FRAMEWORK_NAMESPACE,
                                                                                             TO_TAG),
                                                           transcode=True)
            # get the assignment period
            interval = self._get_first_elementByTagNameNS(request,
                                                           REQUEST_NAMESPACE,
                                                           ATTRIBUTES_TAG)
            # did we get an interval
            if interval:
                # loop over atttributes and check if we gat a match
                for node in interval.getElementsByTagNameNS(COMMON_NAMESPACE,
                                                            ATTRIBUTE_TAG):
                  
                    # get tags start and duration
                    if node.attributes.getNamedItem(NAME_TAG).value == STARTDATE_TAG:
                        start_date = node.attributes.getNamedItem(VALUE_TAG).value.encode(MODEL_ENCODING)
                    if node.attributes.getNamedItem(NAME_TAG).value == DURATION_TAG:
                        duration = node.attributes.getNamedItem(VALUE_TAG).value.encode(MODEL_ENCODING) 
                                         
            return self._do_request_operation(self._crewid , bidtype, period_start, period_end, start_date, duration)
        return None      
    
    def _do_request_operation(self, crew, bidtype,  period_start,  period_end,   start_date, duration):
        """
         default is create request
        """
        return  days_off_response_handler.create_days_off(crew, bidtype, 
                                                          period_start,
                                                          period_end,
                                                          start_date, duration)
            
    
    def _get_first_elementByTagNameNS(self, element, ns, localname):
        """
        Returns the first element in NodeList matching namespace and localname
        Will return None on empty list
        """
        try:
            return element.getElementsByTagNameNS(ns, localname)[0]
        except IndexError:
            return None
    
    def _dom_unpack_text_node(self, node, transcode=False):
        """
        Python DOM stores text in special way, let's unpack it
        Will return first text section in node
        """
        for childNode in [childNode for childNode in node.childNodes if childNode.nodeType == childNode.TEXT_NODE]:
            if transcode:
                return childNode.data.encode(MODEL_ENCODING)
            else:
                return childNode.data
            
class ParseAndServiceCancelRequest(ParseAndServiceRequest):
    '''
    Overload the behavior to create a cancel response
    '''
    
    


    def _do_request_operation(self, crew, bidtype,  period_start,  period_end,   start_date, duration):
        '''
        overload the impl parsers with just the cancel 
        @type doc:
        '''
        # get the request
        return days_off_response_handler.cancel_days_off(crew, bidtype, period_start, period_end, start_date, duration)



