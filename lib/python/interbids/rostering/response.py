'''
Created on Feb 22, 2012

@author: pergr
'''
            
                    
import os
from copy import deepcopy
import uuid
import datetime
from utils import etree
import carmensystems.rave.api as rave
import xml_handler.treeelement_factory as tt
import AbsTime
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import Cui
from interbids.rostering.xml_handler.constants import TRIP_NAMESPACE,\
    COMMON_NAMESPACE, GETROSTER_NAMESPACE, ENDDATETIME_TAG, STARTDATETIME_TAG,\
    ATTRIBUTES_TAG, ATTRIBUTE_TAG, NAME_TAG, VALUE_TAG, TRIP_TAG, ROSTER_TAG,\
    TYPE_TAG, CODE_TAG, GETROSTERCARRYOUT_NAMESPACE
from carmusr.tracking.Publish import TRACKING_PUBLISHED_TYPE, TRACKING_DELIVERED_TYPE, TRACKING_INFORMED_TYPE

# reload(tt)
TT = tt.TreeElementFactory()

        

    
######### "PRIVATE" METHODS #####################

class Response(object):
    '''
    Class to hold the response
    '''

    def __init__(self):
        '''
        Init object and set all member variables to None/empty
        '''
        self._errors = []
        self._warnings = []
        self._status = ""
        self._decision_time = ""
        self._root = None
        self._conflicts = []
        self._crewid = None
    
    @property
    def root(self):
        '''
        Return the root of xml response message
        '''
        return self._root
    
    @property
    def use_conflict_handling(self):
        '''
        Return true if response has conflict handling!
        Base response doesn't use conflicts!
        '''
        return False
    
    def get_conflicts(self): 
        '''
        Return a list of possible conflicting model entities
        Will return None if no conflicts can arise!
        '''
        return None
    
    
    def __set_root(self, node):
        '''
        If response has no root, we are set it to node
        @param node: Element
        '''
        if self._root is None:
            self._root = node

    def set_warnings(self):
        '''
        Add warnings  node to root
        '''
        node = self.get_warnings()
        if not node is None:
            self.root.append(node)
        
    def get_warnings(self):
        '''
        Make the xml node for warnings
        '''
        if self._warnings:
            node= TT.createWarningsElement(self._warnings)
            return node      
        return None   
    
    def set_decision_time(self, crewid=None):
        '''
        Add descision time node to root
        '''
        self.root.append(self.get_decision_time(crewid))

    def get_decision_time(self, crewid=None):
        '''
        Make the xml node for decision time based on now time
        will use convert method in treefactory
        '''
        
        node = TT.createDecisionTimeElement(TT.convertValueToString(self.get_now_time(crewid)))
        return node

    def get_now_time(self, crewid=None):
        '''
        return now as abstime
        '''
        now = datetime.datetime.now()
        now = AbsTime.AbsTime(now.year, now.month, now.day, now.hour, now.minute)
        
        '''
        Return local time if crewid is given
        '''
        if not crewid is None:
            now = self.crew_rave_eval(crewid,
                                      'interbids.crew_utc_to_local', 
                                      now)
        
        return now      
 
    def set_status(self):
        '''
        Add status node to tree
        '''
        self.root.append(self.get_status())
        
    def get_status(self):
        '''
        Will create the xml node for status message based on self._status
        '''
        node = TT.createStatusElement(self._status)
        return node
    
    def set_errors(self):
        '''
        Append errors to root node
        '''
        if self._errors:
            self.root.append(self.get_errors())
    
    def get_errors(self):
        '''
        Return the errors node
        '''
        return TT.createErrorsElement(self._errors)
    
    def create_crew_bag(self, crewid, type="latest"):
        if crewid <> self._crewid:
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            if type == "published":
                Cui.gpc_set_one_published_crew_chain(Cui.gpc_info, crewid)
            else:
                Cui.gpc_set_one_crew_chain(Cui.gpc_info, crewid)
            self._crewid = crewid

        return rave.context("default_context").bag()

    def crew_rave_eval(self, crewid, variable, args=None):
        '''
        Eval the variable on crew bag passing args
        @param variable: module and name of variable
        @type variable: string
        @param args: arguments to eval
        @type args: argument (only one)
        '''
        for crew_bag in self.create_crew_bag(crewid).iterators.chain_set():
            # return subtree with all roster
            return self._bag_eval(crew_bag, variable, args)

    def get_fixed_pattern_preassignments(self, crewid):
        """
        Append fixed patterns to message if found in $CARMDATA
        
        Will parse stored file message and append it to outgoing message to mimic real pre assignments
        
        It will basically just convert one xml format to another by first unpacking and then creating a fake trips-node
            
        The stored file format is:
        <?xml version="1.0" encoding="UTF-8"?>
            <ns0:getRosterResponse xmlns:ns0="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster" 
                xmlns:ns1="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" 
                xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip">
            <ns0:roster>
                <ns2:CRR endDateTime="2012-01-07 00:00" startDateTime="2012-01-03 00:00" type="personal">
                    <ns2:attributes>
                        <ns1:attribute name="code" value="F"/>
                    </ns2:attributes>
                </ns2:CRR>
           </ns0:roster>
            </ns0:getRosterResponse>       
        """
        trips = []

        filepath = os.path.join(os.environ['CARMDATA'],
                                'crewportal',
                                'datasource',
                                'fixed_pattern',
                                crewid)

        # if we have export, add it to our list of trips
        if os.path.exists(filepath):
            try:
                # parse xml
                fixed_pattern_tree = etree.parse(filepath)
                # get correct name space {namespace}tag is ElementTree syntax 
                pattern_roster = fixed_pattern_tree.find('{%s}%s'%(GETROSTER_NAMESPACE,ROSTER_TAG))
                # if found, let's traverse to get attributes
                if not pattern_roster is None:
                    # if found, let's traverse to get attributes with correct namespace
                    for node in pattern_roster.findall('{%s}%s'%(TRIP_NAMESPACE, TRIP_TAG)):
                        # get the value at this level
                        endDateTime  =  node.get(ENDDATETIME_TAG)
                        startDateTime = node.get(STARTDATETIME_TAG)
                        endDate = AbsTime.AbsTime(endDateTime.replace("-","")).ddmonyyyy()[:9]
                        startDate = AbsTime.AbsTime(startDateTime.replace("-","")).ddmonyyyy()[:9]
                        _type =  'personal'
                        crrid = _type

                        # fake trip root element
                        trip = TT.createTripElement()

                        # add id and the other attributes for this node
                        trip.set('uniqueid',str(uuid.uuid4()))
                        trip.set(STARTDATETIME_TAG,str(startDateTime))
                        trip.set(ENDDATETIME_TAG,str(endDateTime))
                        trip.set(TYPE_TAG, _type)
                        # add sub tree
                        # crew portal need all levels of xml tags to not fail in xml parsing
                        fake_leg = TT.createLegElement()
                        fake_rtd = TT.createDutyElement()
                       
                        # if found, let's traverse to get attributes with correct namespace
                        for attributes in node.findall('{%s}%s'%(TRIP_NAMESPACE,ATTRIBUTES_TAG)):
                            attributes_node =  TT.createAttributesElement()
                            # if found, let's traverse to get attributes with correct namespace
                            for attribute in attributes.findall('{%s}%s'%(COMMON_NAMESPACE, ATTRIBUTE_TAG)):
                                # add all the time attributes to prevent crew portal from freaking out
                                # actual information is irrelevant, not visible in crew portal
                                attributes_node.append(TT.createAttributeElement("startdate",startDate))
                                attributes_node.append(TT.createAttributeElement("enddate_utc",endDate))
                                attributes_node.append(TT.createAttributeElement("enddate",endDate))
                                attributes_node.append(TT.createAttributeElement("startdate_local",startDate))
                                attributes_node.append(TT.createAttributeElement("starttime_utc","23:00"))
                                attributes_node.append(TT.createAttributeElement("enddate_local",endDate))
                                attributes_node.append(TT.createAttributeElement("starttime_local","00:00"))
                                attributes_node.append(TT.createAttributeElement("endtime_local","00:00"))
                                attributes_node.append(TT.createAttributeElement("startdate_utc",startDate))
                                attributes_node.append(TT.createAttributeElement("starttime","00:00"))
                                attributes_node.append(TT.createAttributeElement("endtime","00:00"))
                                attributes_node.append(TT.createAttributeElement("endtime_utc","00:00"))
                                # innermost level, here are the goodies!
                                name = attribute.get(NAME_TAG)
                                value = attribute.get(VALUE_TAG)
                                # get code of assignment, we need to add it to top trip attribute level
                                if name  == CODE_TAG:
                                    crrid = value
                                # add to new nodes (fake pre assignments)
                                attribute_node = TT.createAttributeElement(name, value)
                                attributes_node.append(attribute_node)
                            # add attributes node to trip node
                            # set the crrid , which will be shown in preassignment view
                            
                            trip.set('crrid',crrid)
                            trip.append(attributes_node)
                            # and to the fake ones
                            fake_rtd.append(deepcopy(attributes_node))
                            fake_leg.append(deepcopy(attributes_node))
                        # add fake leg in fake rtd
                        fake_rtd.append(fake_leg)
                        # add to actual trip
                        trip.append(fake_rtd)
 
                        # Add to roster node 
                        trips.append(trip)    
            except Exception, err:
                print err
        else:
            print "response: File not found"

        return trips
        

    def get_carryout_preassignments(self, crewid):
        """
        Append carryout preassignments to message if found in $CARMDATA

        Will parse stored file message and append it to outgoing message to mimic real pre assignments

        It will basically just convert one xml format to another by first unpacking and then creating trip nodes
        """
        trips = []

        filepath = os.path.join(os.environ['CARMDATA'],
                                'crewportal',
                                'datasource',
                                'preassignments',
                                crewid)

        # if we have export, add it to our list of trips
        if os.path.exists(filepath):
            try:
                # parse xml
                fixed_pattern_tree = etree.parse(filepath)
                # get correct name space {namespace}tag is ElementTree syntax
                pattern_roster = fixed_pattern_tree.find('{%s}%s'%(GETROSTERCARRYOUT_NAMESPACE, ROSTER_TAG))
                # if found, let's traverse to get attributes
                if not pattern_roster is None:
                    # if found, let's traverse to get attributes with correct namespace
                    for trip in pattern_roster.findall('{%s}%s'%(TRIP_NAMESPACE, TRIP_TAG)):
                        trips.append(trip)
            except Exception, err:
                print err
        else:
            print "response: File not found"

        return trips
        
    def get_response(self, *args, **kwds):
        '''
        Main call point for framework
        '''
        raise NotImplementedError('Base class response has no meaning')
    
    def get_rosters(self, crewid):
        """
        Generate roster xml for given crew
        Had defined dict with rave attributes to be added as xml-attributes to node
        Also has crr_filter for selection of trips to include in reply!
        """
        Cui.CuiSyncModels(Cui.gpc_info)

        # sub tree root
        roster = TT.createRosterElement()
        self.__set_root(roster)     

        # append jmp fixed patterns (if any)
        roster.append(etree.Comment("Roster part: Fixed pattern"))
        for trip in self.get_fixed_pattern_preassignments(crewid):
            roster.append(trip)

        # append assigned roster
        roster.append(etree.Comment("Roster part: Assigned roster"))
        for trip in self.get_assigned_roster(crewid):
            roster.append(trip)

        # append carryout preassignments (if any)
        roster.append(etree.Comment("Roster part: Carryout"))
        for trip in self.get_carryout_preassignments(crewid):
            roster.append(trip)

        return roster
             
    def get_assigned_roster(self, crewid):
        trips = []

        if "PUBLISH" in os.environ.get("CARM_PROCESS_NAME", ""):
            # Running in the PUBLISH report server, return all assignemnts on the published roster
            trips.append(etree.Comment("Published roster"))
            context_type = "published"
            crr_filter = 'True'
        else:
            # Running in the LATEST report server, return activities probably published on the latest roster
            trips.append(etree.Comment("Probably published activities on latest roster"))
            context_type = "latest"
            crr_filter = 'interbids.%trip_considered_published%'
        for crew_bag in self.create_crew_bag(crewid, type=context_type).iterators.chain_set():
            for trip_bag in crew_bag.iterators.trip_set(where=crr_filter):
                # get sub tree
                trips.append(self.get_crr(trip_bag))
        return trips

    def get_roster_carryouts(self, crewid):
        """
        Generate roster xml for given crew
        Had defined dict with rave attributes to be added as xml-attributes to node
        Also has crr_filter for selection of trips to include in reply!
        """
        Cui.CuiSyncModels(Cui.gpc_info)

        # sub tree root
        roster = TT.createRosterCarryoutElement()
        self.__set_root(roster)

        # append assigned roster
        roster.append(etree.Comment("Roster part: Assigned roster"))
        for trip in self.get_roster_carryout(crewid):
            roster.append(trip)

        return roster

    def get_roster_carryout(self, crewid):
        trips = []

        if "PUBLISH" in os.environ.get("CARM_PROCESS_NAME", ""):
            # Running in the PUBLISH report server, return all assignemnts on the published roster
            trips.append(etree.Comment("Published roster: no carryouts"))
            context_type = "published"
            crr_filter = 'False'
        else:
            # Running in the LATEST report server, return activities probably published on the latest roster
            trips.append(etree.Comment("Carryout activities on latest roster"))
            context_type = "latest"
            crr_filter = 'interbids.%trip_partly_published% and crew.%is_temporary_at_date%(trip.%start_utc%)'

        for crew_bag in self.create_crew_bag(crewid, type=context_type).iterators.chain_set():
            try:
                for trip_bag in crew_bag.iterators.trip_set(where=crr_filter):
                    # get sub tree
                    trips.append(self.get_carryout(trip_bag))
            except:
                print "WARN: Got exception in trip loop. Will carry on."
        return trips


    def get_pbs(self):
        """
        generate root node for reply xml
        """
        # root for all request to crew portal from rostering
        trips = TT.createTripsElement()
        self.__set_root(trips)
        # define crr filter
        where_filter = 'interbids.%trip_in_export%'
        # create context bag
        all_trip_bag = rave.context("sp_crrs").bag()
        # get subtrees for all trips in filter
        for trip_bag in all_trip_bag.iterators.trip_set(where=where_filter):
            # insert subtree
            trips.append(self.get_crr(trip_bag))
        # return the string repr (xmplprc channel cannot send ElementTree
        return trips

    def get_crr(self, trip_bag):
        """
        Get the trip xml from bag
        Had defined dict with rave attributes to be added as xml-attributes to node
        Also has rtd_filter for selection of duties to include in reply!
        """

        # trip root element
        trip = TT.createTripElement()
        # if no root, then we set this one
        self.__set_root(trip) 
        # attributes on the actual trip node
        trip_node_attrs = {'type':'interbids.trip_type',
                           'crrid':'interbids.trip_name',
                           'startDateTime':'interbids.trip_startdatetime_local',
                           'endDateTime':'interbids.trip_enddatetime_local'}
        
        for name, variable in trip_node_attrs.iteritems():
            trip.set(name, str(self._bag_eval(trip_bag, variable)))
        
        # defined attrs to add
        trip_sub_attrs = {'crr_crew_id':'keywords.crr_crew_id',
                          'type':'interbids.trip_type',
                          'crrid':'interbids.trip_name',  
                          'length':'interbids.trip_length',
                          'startdate':'interbids.trip_startdate_hb',
                          'starttime':'interbids.trip_starttime_hb',
                          'startdate_local':'interbids.trip_startdate_local',
                          'starttime_local':'interbids.trip_starttime_local',
                          'enddate':'interbids.trip_enddate_hb',
                          'endtime':'interbids.trip_endtime_hb',
                          'enddate_local':'interbids.trip_enddate_local',
                          'endtime_local':'interbids.trip_endtime_local',
                          'startdate_utc':'interbids.trip_startdate_utc',
                          'starttime_utc':'interbids.trip_starttime_utc',
                          'enddate_utc':'interbids.trip_enddate_utc',
                          'endtime_utc':'interbids.trip_endtime_utc',
                          'dutytime':'interbids.trip_dutytime',
                          'blocktime':'interbids.trip_blocktime',
                          'region':'interbids.trip_region',
                          'longhaul':'interbids.trip_is_longhaul',
                          'code':'interbids.trip_code',
                          'homebase':'interbids.trip_homebase',
                          'layovers':'interbids.trip_layovers',
                          'crewcompl':'interbids.trip_cc',
                          'cc_acqual':'interbids.trip_cc_acqual',
                          'fd_acqual':'interbids.trip_fc_acqual'}
    
        # defined sub attributes
        attributes = TT.createAttributesElement()
        attributes.append(TT.createAttributeElement("uniqueid", str(uuid.uuid4())))
        for name, variable in trip_sub_attrs.iteritems():
            value = str(self._bag_eval(trip_bag, variable))
            attributes.append(TT.createAttributeElement(name, value))

        if len(attributes) > 0:
            trip.append(attributes)
    
        # add duties, no filter at the moment
        rtd_filter = None
        # need some counter
        duty_id_counter = 0
        for duty_bag in trip_bag.iterators.duty_set(where=rtd_filter):
            # get subtree
            duty = self.get_rtd(duty_bag)
            # add id
            # duty.set('id',str(duty_id_counter))
            # add subtree
            trip.append(duty)
            duty_id_counter += 1
        # return subtree trip with subnodes duties (CRR -> RTD)
        return trip


    def get_carryout(self, trip_bag):
        """
        Fake flight preassignment for the unpublished part of a trip that is partially published
        """

        # get the value at this level
        endDateTime  = "%04d-%02d-%02d %02d:%02d" % trip_bag.interbids.trip_unpublished_end_day_hb().split()
        startDateTime = "%04d-%02d-%02d %02d:%02d" % trip_bag.interbids.trip_unpublished_start_day_hb().split()
        endDate = trip_bag.interbids.trip_unpublished_end_day_hb().ddmonyyyy()[:9]
        startDate = trip_bag.interbids.trip_unpublished_start_day_hb().ddmonyyyy()[:9]
        _type =  'personal'
        crrid = "FLT"

        # fake trip root element
        trip = TT.createTripElement()

        # add id and the other attributes for this node
        trip.set('uniqueid', str(uuid.uuid4()))
        trip.set(STARTDATETIME_TAG, str(startDateTime))
        trip.set(ENDDATETIME_TAG, str(endDateTime))
        trip.set(TYPE_TAG, _type)
        # add sub tree
        # crew portal need all levels of xml tags to not fail in xml parsing
        fake_leg = TT.createLegElement()
        fake_rtd = TT.createDutyElement()

        attributes_node = TT.createAttributesElement()
        attributes_node.append(TT.createAttributeElement("code", "FLT"))
        attributes_node.append(TT.createAttributeElement("startdate", startDate))
        attributes_node.append(TT.createAttributeElement("enddate_utc", endDate))
        attributes_node.append(TT.createAttributeElement("enddate", endDate))
        attributes_node.append(TT.createAttributeElement("startdate_local", startDate))
        attributes_node.append(TT.createAttributeElement("starttime_utc", "23:00"))
        attributes_node.append(TT.createAttributeElement("enddate_local", endDate))
        attributes_node.append(TT.createAttributeElement("starttime_local", "00:00"))
        attributes_node.append(TT.createAttributeElement("endtime_local", "00:00"))
        attributes_node.append(TT.createAttributeElement("startdate_utc", startDate))
        attributes_node.append(TT.createAttributeElement("starttime", "00:00"))
        attributes_node.append(TT.createAttributeElement("endtime", "00:00"))
        attributes_node.append(TT.createAttributeElement("endtime_utc", "00:00"))

        trip.set('crrid', crrid)

        trip.append(attributes_node)
        fake_rtd.append(deepcopy(attributes_node))
        fake_leg.append(deepcopy(attributes_node))

        # add fake leg in fake rtd
        fake_rtd.append(fake_leg)
        # add to actual trip
        trip.append(fake_rtd)
        return trip


    def get_rtd(self, duty_bag):
        """
        Get's the duty xml
        Had defined dict with rave attributes to be added as xml-attributes to node
        Also has rtd_filter for selection of duties to include in reply!   
        """
        # root for duties
        duty = TT.createDutyElement()
        # if no root, then we set this one
        self.__set_root(duty) 
        # duty attributes
        duty_sub_attrs = {'startdate':'interbids.duty_startdate_hb',
                      'starttime':'interbids.duty_starttime_hb',
                      'startdate_local':'interbids.duty_startdate_local',
                      'starttime_local':'interbids.duty_starttime_local',
                      'startdate_utc':'interbids.duty_startdate_utc',
                      'starttime_utc':'interbids.duty_starttime_utc',
                      'enddate':'interbids.duty_enddate_hb',
                      'endtime':'interbids.duty_endtime_hb',
                      'enddate_local':'interbids.duty_enddate_local',
                      'endtime_local':'interbids.duty_endtime_local',
                      'enddate_utc':'interbids.duty_enddate_utc',
                      'endtime_utc':'interbids.duty_endtime_utc',
                      'splitduty':'interbids.duty_is_split',
                      'resttime':'interbids.duty_resttime',
                      'nightstop':'interbids.duty_followed_by_nightstop'}
    
        # defined sub attributes
        attributes = TT.createAttributesElement()
        for name, variable in duty_sub_attrs.iteritems():
            value = str(self._bag_eval(duty_bag, variable))
            attributes.append(TT.createAttributeElement(name, value))
        duty.append(attributes)
    
        # add legs, no filter at the moment
        leg_filter = None
        # need some counter
        leg_id_counter = 0
        for leg_bag in duty_bag.iterators.leg_set(where=leg_filter):
            # get leg subtree
            leg = self.get_leg(leg_bag)
            # add id
            # leg.set('id',str(leg_id_counter))
            # add leg subtree
            duty.append(leg)
            leg_id_counter += 1
        # return subtree duty with subnodes leg (CRR -> RTD)
        return duty
    
    def get_leg(self, leg_bag):
        """
        get the leg xml
        Had defined dict with rave attributes to be added as xml-attributes to node
        leg_type will affect added attrs
        """  
        # root element
        leg = TT.createLegElement()
        # if no root, then we set this one
        self.__set_root(leg) 
        # Generate leg section
    
        # leg_type
        # defines added attributes
        leg_type=leg_bag.interbids.activity_type()
    
        # defined attrs
        leg_sub_attrs = {'type':'interbids.activity_type',
                     'startdate':'interbids.activity_startdate_hb',
                     'starttime':'interbids.activity_starttime_hb',
                     'startdate_local':'interbids.activity_startdate_local',
                     'starttime_local':'interbids.activity_starttime_local',
                     'startdate_utc':'interbids.activity_startdate_utc',
                     'starttime_utc':'interbids.activity_starttime_utc',
                     'endstation':'interbids.activity_endstation',
                     'enddate':'interbids.activity_enddate_hb',
                     'endtime':'interbids.activity_endtime_hb',
                     'enddate_local':'interbids.activity_enddate_local',
                     'endtime_local':'interbids.activity_endtime_local',
                     'enddate_utc':'interbids.activity_enddate_utc',
                     'endtime_utc':'interbids.activity_endtime_utc'}
        # split defined attrs on leg_type
        if leg_type in ('flight', 'deadhead'):
            leg_sub_attrs.update({'carrier':'interbids.activity_carrier',
                              'number':'interbids.activity_number',
                              'suffix':'interbids.activity_suffix',
                              'startstation':'interbids.activity_startstation',
                              'cnxtime':'interbids.activity_cnx_time',
                              'blocktime':'interbids.activity_block_time',
                              'charter':'interbids.activity_is_non_scand_charter'
                              })
        else:
            leg_sub_attrs.update({'code':'interbids.activity_code',
                              'location':'interbids.activity_startstation'
                              })
    
        # defined attributes
        attributes = TT.createAttributesElement()
        for name, variable in leg_sub_attrs.iteritems():
            value = str(self._bag_eval(leg_bag, variable))
            attributes.append(TT.createAttributeElement(name, value))
        if len(attributes) > 0:
            leg.append(attributes)
        # return leg node
        return leg
        
        
    def _bag_eval(self, bag, variable, args=None):
        """
        Hack to evaluate the defined variable-strings on the bag
        """
        if args is None:
            return  eval('bag.%s()'%variable)
        else:
            return eval('bag.%s(args)'%variable)
        


        
################
