''''
Created on Feb 22, 2012

@author: pergr
'''

import AbsTime
import os
import os.path
import time
import xml_handler.treeelement_factory as tt
import interbids.rostering.response as response_module 
from utils import etree

import tm
import modelserver
import Cui

import carmensystems.rave.api as rave
import carmensystems.publisher.api as publisher

from interbids.rostering.xml_handler.constants import MODEL_ENCODING, REJECTED, AWARDED, CANCELLED,\
    GRANTED, LOCK_GRACE_TIME, LOCK_TIMEOUT
import RelTime
from carmusr.TimeUtil import _24_HOURS
import carmusr.AccountHandler
from interbids.rostering.crew_request_attribute_set import CrewRequestAttributeSet

from interbids.rostering.roster_trip_response_handler import RosterResponse
import AbsDate

import utils.Names as Names
import tempfile


#reload(tt)
#reload(response_module)
TT = tt.TreeElementFactory()

# handled codes
FS = 'FS'
F7S = 'F7S'
FW = 'FW'
FS1 = 'FS1'


def _get_period_date_list(start, end):
    '''
    Return a list of date in range, start needs to be AbsDate (i.e. 00:00)
    Inclusive end date!!
    @param start: Start time
    @type start: AbsTime (i.e. 00:00)
    @param end: EndTime
    @type end:AbsTime (i.e. 00:00)
    '''
    
    return [start.adddays(ix) for ix in range(0,int((end-start)/_24_HOURS)+1)]

def time_range(start, end, step=RelTime.RelTime("24:00")):
    x = start
    while x < end:
        yield x
        x = x + step

class DaysOffRejectedError(Exception):
    '''
    Mark that we reject this create request
    '''
    def __init__(self, msg):
        super(DaysOffRejectedError, self).__init__(msg)
        self._msg = msg
        
    def __str__(self):
        '''
        just return message
        '''
        return self._msg

class GetAvailableDaysOffResponse(response_module.Response):
    '''
    Class to create a response to the get_available_daysoff query
    Will use lookup in DaysOffLimitHandler class to get available days
    '''
    
    def __init__(self, crew, daysoff_type, start, end):
        '''
        init class
        Set root tag to availableDaysOffResponse
        @param crew: crew id
        @type crew: string
        @param daysoff_type: activity type
        @type daysoff_type: string
        @param start: start time 
        @type start: string
        @param end: end time
        @type end: string
        '''

        super(GetAvailableDaysOffResponse, self).__init__()
        self._root = TT.createGetAvailableDaysOffResponseElement()
        self._crew_e = None
        self._activity_e = None
        self._start = None
        self._end = None
        self._check_and_set_arguments(crew, daysoff_type, start, end)

        self.attributes = CrewRequestAttributeSet(tm.TM, self._crew_e)
        # for (validfrom,validto,group) in self.attributes.attributes["RequestGroup"]:
        #    print "RequestGroup", validfrom, validto, group.name

    def _check_and_set_arguments(self, crew, daysoff_type, start, end):
        '''
        Check the parameters by converting to correct type   
        @param crew: crew id
        @type crew: string
        @param daysoff_type: activity type
        @type daysoff_type: string
        @param start: start time 
        @type start: string
        @param end: end time
        @type end: string
        '''
        try:
            self._crew_e = tm.TM.table('crew')[(crew,)]
        except modelserver.EntityNotFoundError:
            raise Exception("Crew %s not found in table crew"%crew)

        try:
            self._activity_e = tm.TM.table('activity_set')[(daysoff_type,)]
        except modelserver.EntityNotFoundError:
            raise Exception("Activity %s not found in table activty_set"%daysoff_type)

        self._start_hb = TT.convertStringToValue(start)
        self._end_hb = TT.convertStringToValue(end)
        self._start = self.crew_rave_eval(crew,
                                          'interbids.crew_local_to_utc', 
                                          self._start_hb)
        self._end = self.crew_rave_eval(crew,
                                        'interbids.crew_local_to_utc', 
                                        self._end_hb)

    def get_days_off_node(self):
        days_off_node = TT.createAvailableDaysOffElement()
        days_off_node.append(etree.Comment("Limit request groups at %s: %s"%(self._start_hb, ", ".join([x.name for x in self.get_request_groups(self._start_hb)]))))
        days_off_node.append(etree.Comment("\nAll attributes:\n%s\n"%("\n".join(["%-20s %s %s %s"%x for x in self.attributes.list_values()]))))

        for date in time_range(self._start_hb, self._end_hb + RelTime.RelTime("24:00")):
            value = self.get_available_days(date)
            if value is None or value < 0:
                value = 0
            days_off_node.append(TT.createDayOffElement(TT.convertValueToString(AbsDate.AbsDate(date)),
                                                        value))

        return days_off_node

    def get_available_days(self, date):
        """
        Return number of available days at a single date for the current request type.
        If crew belongs to several request groups, return the lowest number.
        If crew doesn't belong to any group or limit is undefined for all groups, None is returned.
        """
        available = None
        for crew_group in self.get_request_groups(date):
            limit = get_limit(tm, crew_group, self._activity_e, date)
            awarded = get_awards(tm, crew_group, self._activity_e, date)

            # print "%s request limit at %s: crewgroup=%s, limit=%s, awarded=%s"%(type.id, date, crew_group.name, limit, awarded)
            print "Logging the date: " , date, " crewgroup: ", crew_group.name , " limit: " , limit , " awarded: " , awarded
            if limit is None:
                continue
            if awarded is None:
                awarded = 0

            _available = limit - awarded
            if available is None or _available < available:
                available = _available

        return available

    def get_request_groups(self, date):
        return self.attributes.get_values("RequestGroup", date)

    def get_response(self):
        """Create the xml, will be empty if errors is nonempty

        The bid is put on the roster (as a trip) temporarily before this rule is evaluated.
        If the rule passes, then the roster is commited.
        """
    
        # do nothing if we get errors
        if self._errors:
            self.set_errors()
            return None

        self.root.append(self.get_days_off_node())

    
class CreateDaysOffResponseHandler(GetAvailableDaysOffResponse):
    '''
    Class to handle to handle the create_request-request, will check available limit and so
    '''
    
    def __init__(self, crew, daysoff_type, period_start, period_end, activity_start, activity_duration):
        '''
        Main method
        @param crew: crew id
        @type crew: string
        @param daysoff_type: activity type
        @type daysoff_type: string
        @param start: start time 
        @type start: string
        @param duration: duration in number of days
        @type duration: string
        '''
        super(CreateDaysOffResponseHandler,self).__init__(crew, 
                                                          daysoff_type, 
                                                          period_start, 
                                                          period_end)
        # need the members defined here
        # full period used in request
        self._period_start = None
        self._period_end = None 
        self._errors = []
        # the airport of activity
        self._station_e = None

        self._activity_start = self.crew_rave_eval(crew,
                                                   'interbids.crew_local_to_utc', 
                                                   TT.convertStringToValue(activity_start))

        # SKCMS-1744: Change to how self._activity_end is calculated. By adding the duration before changing to UTC,
        # daylight savings problematics will be handled in rave, which handles this automatically compared to python.
        self._activity_end = self.crew_rave_eval(crew,
                                                   'interbids.crew_local_to_utc',
                                                 TT.convertStringToValue(activity_start).adddays(int(activity_duration)))

        # validate period
        self._check_and_set_period(period_start,
                                   period_end)

        # store local time to avoid rave lookups
        self._activity_start_local = self.crew_rave_eval(self._crew_e.id,
                                                         'interbids.crew_utc_to_local', 
                                                         self._activity_start)
        self._activity_end_local = self.crew_rave_eval(self._crew_e.id,
                                                       'interbids.crew_utc_to_local', 
                                                       self._activity_end)

        station = self.crew_rave_eval(self._crew_e.id,
                                      'interbids.crew_station', 
                                      self._activity_start)
        if station is None:
            raise Exception("Crew id=%s has no station at date=%s"%(self._crew_e.id, self._activity_start))
        self._station_e = tm.TM.table('airport')[(station,)]

        # new main tag
        self._root = TT.createCreateRequestResponseElement()
        
        #conflict model entities
        self._conflicts = None
        
        # new activity
        self._new_activity_e = None
        # and new account entry
        self._new_account_e = None
        # log roster request
        self._new_roster_request_e  = None

    @property
    def use_conflict_handling(self):
        '''
        Return true if response has conflict handling!
        create response uses conflicts!
        '''
        return True
    
    def get_conflicts(self): 
        '''
        Return a list of possible conflicting model entities
        Will return None if no conflicts can arise!
        '''
        return self._conflicts or None
    
    def _create_activity(self):
        '''
        Create the model entity
        will convert self._start/_end to utc using rave eval on crew
        Will also update the number of awarded days off
        Will return False if not possible to create new activity, otherwise True
        '''
        
        try:
            new_activity = tm.TM.table('crew_activity').create((self._activity_start,
                                                                self._crew_e,
                                                                self._activity_e))
        except modelserver.EntityError:
            raise DaysOffRejectedError('Activity already exists')

     
        for date in time_range(self._activity_start_local , self._activity_end_local ):
            for crew_group in self.get_request_groups(date):
                # print "Limit request group: %s"%crew_group.name
                try:
                    award_row = tm.TM.table("roster_request_awards")[(crew_group, self._activity_e.id, date)]
                    award_row.awarded = award_row.awarded + 1
                except modelserver.EntityNotFoundError:
                    award_row = tm.TM.table("roster_request_awards").create((crew_group, self._activity_e.id, date))
                    award_row.awarded = 1

        new_activity.et = self._activity_end
        new_activity.adep = self._station_e
        new_activity.ades = self._station_e
        self._new_activity_e = new_activity
        self._new_account_e = None
        Cui.CuiSyncModels(Cui.gpc_info)
    
    def _undo_create_activity(self):
        '''
        Remove the newly created activity in case we got illegality
        '''
        if not self._new_activity_e is None:
            self._new_activity_e.remove()
      
        if not self._new_account_e is None:
            self._new_account_e.remove()
            
        if not self._new_roster_request_e is None:
            self._new_roster_request_e.remove()
        
        Cui.CuiSyncModels(Cui.gpc_info)
        
    def _check_legality(self):
        '''
        Check the roster legality
        '''
        rule_set_name = self.crew_rave_eval(self._crew_e.id, "rule_set_name")  

        days_off_type = self._activity_e.id
    
        for crew_bag in self.create_crew_bag(self._crew_e.id).iterators.chain_set():
            text = ''
            for f_bag, fail in crew_bag.rulefailures(where='interbids.%%check_days_off_bid_legality%%("%s")' %(days_off_type),
                                                     group=rave.group("interbids.request_rules_message")):
                #print ("FAIL",
                #       rule_set_name,
                #       fail.rule.name(),
                #       str(fail.startdate),
                #       fail.failtext,
                #       fail.rule.remark(),
                #       fail.failobject,
                #       fail.limitvalue,
                #       fail.actualvalue,
                #       fail.overshoot)
                rulename = fail.rule.name().lower()
                # use mapping for better error message
                crew_failtext = f_bag.interbids.crew_readable_failtext(rulename)
                limit_type = f_bag.interbids.crew_rule_limit_type(rulename)
                limit_scale_factor = f_bag.interbids.crew_rule_limit_scale_factor(rulename)

                if crew_failtext:
                    limitvalue = ('%.2f' % (float(fail.limitvalue or 0) / limit_scale_factor,)).rstrip('0').rstrip('.')

                    fail_actualvalue = fail.actualvalue

                    # SKCMS-2001: Fix sign for compdays balance actual value
                    if rulename == 'rules_studio_ccr.sft_nr_comp_days_must_not_exceed_balance_all':
                        fail_actualvalue = -fail_actualvalue

                    actualvalue = ('%.2f' % (float(fail_actualvalue or 0) / limit_scale_factor,)).rstrip('0').rstrip('.')

                    if limit_type == "MAX":
                        text = "Rule violation: %s - Max limit is %s, request gives %s" % (crew_failtext, limitvalue, actualvalue)
                    elif limit_type == "MIN":
                        text = "Rule violation: %s - Min limit is %s, request gives %s" % (crew_failtext, limitvalue, actualvalue)
                    else:
                        text = "Rule violation: %s" % (crew_failtext)
                        
                elif fail.failtext is not None:
                    text = fail.failtext
                else:
                    text = fail.rule.name()
                raise DaysOffRejectedError(text)

            for f_bag, fail in crew_bag.rulefailures(where='interbids.%%check_days_off_bid_legality%%("%s")' %(days_off_type)):
                #print ("FAIL",
                #       rule_set_name,
                #       fail.rule.name(),
                #       str(fail.startdate),
                #       fail.failtext,
                #       fail.rule.remark(),
                #       fail.failobject,
                #       fail.limitvalue,
                #       fail.actualvalue,
                #       fail.overshoot)
                if days_off_type not in (FS, F7S, FW, FS1):  # Ignore illegal roster only for instant reply request types in IB
                    raise DaysOffRejectedError("Your request is in conflict with other planned activities and/or rules")

    def _create_account_entry(self):
        '''
        If the type of assignment matches FS, we create manual account entry manually
        '''

        # these codes have normal account handling
        if self._activity_e.id not in (FS, FS1,):
            carmusr.AccountHandler.updateAccountsForCrewInWindow([self._crew_e.id], 
                                                                 [self._activity_e.id])
            return 
            #carmusr.AccountHandler.updateChangedCrew([self._crew_e.id])
        # FS handled "manually" since they cannot be deassigned
        days = int((self._new_activity_e.et - self._new_activity_e.st)/RelTime.RelTime('24:00'))
        now = self.crew_rave_eval(self._crew_e.id, 'fundamental.now')
        
        for day in range(days):
            tim = self.crew_rave_eval(self._crew_e.id,
                                      'interbids.crew_utc_to_local',
                                      self._new_activity_e.st) + day * RelTime.RelTime('24:00')
            account_type = self._activity_e.id
            si_text = "Created by daysoffrequest %s" % now
            if self._activity_e.id == 'FS1':
                # FS1 and FS shall share the same individual quota.
                account_type = 'FS'
                # Used to distinguish between FS and FS1 activities in table.
                si_text = "Created FS1 by daysoffrequest %s" % now

            entry={'crew':self._crew_e.id,
                   'amount':-100,
                   'account':account_type,
                   'tim':tim,
                   'reason':'OUT Correction',
                   'source':"Granted daysoff",
                   'si':si_text,
                   'nowtime':now,
                   'username':Names.username(),
                   'rate':100,
                   'published':False
                   }
           
            self._new_account_e = carmusr.AccountHandler._create_account_entry(entry)
            self._new_account_e.man = True
            
        Cui.CuiReloadTable('account_entry',1)

             
    def _create_conflicts(self):
        '''
        Create the conflict model entities based on attributes
        Will create an entity in table conflcit_trigger for each date with associated type
        The conflicts are used by repoertWorker when saving data!
        '''

        self._conflicts = []

        # Horizontal conflict key to avoid two request by same crew without a refresh
        key = "crew:%s"%self._crew_e.id
        try:
            conflict = tm.TM.table('conflict_trigger').create((key,))
        except modelserver.EntityError:
            conflict = tm.TM.table('conflict_trigger')[(key,)]
        conflict.data = tm.TM.createUUID()
        self._conflicts.append(conflict)

        # Vertical conflict key on the request days
        for date in _get_period_date_list(self._activity_start_local, self._activity_end_local):
            key = "%s:%s"%(self._activity_e.id,
                           date)
            try:
                conflict = tm.TM.table('conflict_trigger').create((key,))
            except modelserver.EntityError:
                conflict = tm.TM.table('conflict_trigger')[(key,)]
            conflict.data = tm.TM.createUUID()
            self._conflicts.append(conflict)
            
    def _create_crew_roster_request(self):
        '''
        Create a log of a success full daysoff request
        '''
        self._new_roster_request_e = tm.TM.table("crew_roster_request").create((self._crew_e, tm.TM.createUUID()))
        self._new_roster_request_e.type = self._activity_e.id
        self._new_roster_request_e.st = self._activity_start_local
        self._new_roster_request_e.et = self._activity_end_local
        self._new_roster_request_e.si = 'Created by request report server : %s'%self.get_now_time()
        
    def _generate_request_receipt_report(self):
        '''
        Create the report
        '''
        #import report_sources.report_server.rs_RequestReciept
        Cui.CuiReloadTable("crew_roster_request")
        dir_path = os.path.join(os.environ['CARMDATA'],
                                'crewportal',
                                'datasource',
                                'reports',
                                'interbids',
                                'user',
                                self._crew_e.id[:3],
                                self._crew_e.id)
        # check if exists
        try:
            os.stat(dir_path)
        except OSError:
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path,'RequestReciept')
        publisher.generateReport("report_sources.report_server.rs_RequestReciept",
                                 file_path,
                                 reportparams={"crew_id":self._crew_e.id})
        
    def _check_limit(self):
        '''
        Check the available limit against period
        Will return False if less then 1 on any day in period
        Otherwise returns True
        (uses the class member objects)
        '''
        
        override = self._activity_e.id == F7S and self.crew_rave_eval(self._crew_e.id,
                                                                        'interbids.override_request_f7s_limit_check', 
                                                                        self._activity_start_local)
                
        if not override:
            for date in time_range(self._activity_start_local, self._activity_end_local):
                available_days = self.get_available_days(date)
                limit_groups = list(self.get_request_groups(date))
                print "Logging the day off request for the date: ", date
                print "Logging the available dayoff quota days: ", available_days
                print "Logging the crew group for limit: ", limit_groups
                if limit_groups == [] or available_days is None or available_days < 0:
                    msg = 'No quota available on day %s'%AbsDate.AbsDate(date)
                    if self._activity_e.id == F7S:
                        msg += ', try normal compdays bid in PBS'
                    raise DaysOffRejectedError(msg)

    def _check_and_set_period(self, period_start, period_end):
        '''
        Overload base validation with period argument check
        @param period_start: Full request period start
        @type period_start:string
        @param period_end:Full request period end
        @type period_end:string
        '''

        try:
            self._period_start = TT.convertStringToValue(period_start)
            self._period_end = TT.convertStringToValue(period_end)
        except Exception, err:
            self._errors.append(str(err)+" in period start/end")
  
        # success?
        if self._errors:
            raise AttributeError("Not correct arguments :: %s"%(os.linesep.join(self._errors)))
        
    def _try_acquire_temporary_lock(self):
        '''
        Tries to acquire the lock by checking the temporary files lock-<crew_id> and then grace-<crew_id>.
        If they exist and are new enough DaysOffRejectedError is raised. Otherwise the lock is successful and
        the lock is activated by creating the file lock-<crew_id>.
        '''
        # If the request is still being processed the user probably clicked cancel and is now trying a new request.
        error_message = "Your previous request is still processing, please try again in a few seconds (timeout in {0:.0f} seconds)..."
        self._check_lock_file_age("lock-{0}".format(self._crew_e.id), error_message, LOCK_TIMEOUT)

        
        error_message = "Your previous request is just finishing up, please wait a few (about {0:.0f}) more seconds..."
        self._check_lock_file_age("grace-{0}".format(self._crew_e.id), error_message, LOCK_GRACE_TIME)

        # If the lock file did not exist, or the lock has expired, activate it now so that no other
        # requests can be processed while this one is being handled.
        # As of SASCMS-5991 the assumption is that a request cannot take longer than 120 seconds.
        self._touch_lock_file("lock-{0}".format(self._crew_e.id))

    def _release_temporary_lock(self):
        self._remove_lock_file("lock-{0}".format(self._crew_e.id))

    def _start_grace_period(self):
        self._touch_lock_file("grace-{0}".format(self._crew_e.id))

    def _check_lock_file_age(self, file, error_message, timeout):
        '''
        If the lock file does not exist or is old enough this function does nothing,
        however if the lock file is newer than 'timeout' a DaysOffRejectedError is raised.
        '''
        lock_file_age = self._get_lock_file_age(file)

        if lock_file_age > 0 and lock_file_age < timeout:
            raise DaysOffRejectedError(error_message.format(timeout - lock_file_age))

    def _remove_lock_file(self, filename):
        '''
        When the given lock file is no longer needed it can be removed.
        This operation at the same time in essence removes the lock itself.
        '''
        file = self._get_lock_file_path(filename)
        if os.path.exists(file):
            os.remove(file)

    def _touch_lock_file(self, file):
        '''
        Touches a given lock file to activate the lock for a certain amount of time
        defined by the function that checks the lock.
        '''
        open(self._get_lock_file_path(file), "w").close()

    def _get_lock_file_age(self, filename):
        '''
        Finds how old a given lock file is.
        Returns -1 if the file (and thereby the lock) does not exist.
        '''
        file_path = self._get_lock_file_path(filename)
        try:
            os.stat(os.path.dirname(file_path))
        except OSError:
            os.makedirs(os.path.dirname(file_path))
        
        if os.path.exists(file_path):
            return time.time() - os.stat(file_path).st_mtime
        else:
            return -1

    def _get_lock_file_path(self, filename):
        return os.path.join(os.environ["CARMTMP"],"days_off_requests-locks", filename)


    def _publish_granted_freeday(self):
        '''
        Since the granted freedays must be visible in reportserver PUBLISHED, we
        use the same publish call as publish in pre-studio does!
        (i.e. CuiPublishRoster )
        
        We hardcoded the published tag to PUBLISHED!
        This need to be maintained
        '''
        #cannot publish if no activity exists
        if self._new_activity_e is None:
            return
        
        pub_item = [(self._crew_e.id,
                     "PUBLISHED",
                     int(self._new_activity_e.st),
                     int(self._new_activity_e.et))]
        # cannot use proper publish due to no refresh in tm
        # hence all the flags
        # wrapper will handle that
        flags = Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
        flags |= Cui.CUI_PUBLISH_ROSTER_SKIP_SAVE
        flags |= Cui.CUI_PUBLISH_ROSTER_SKIP_REFRESH
        Cui.CuiPublishRosters(Cui.gpc_info, pub_item, 
                              "REPORT SERVER - GRANTED REQUEST PUBLISH",
                              flags)
 
    def get_response(self):
        '''
        Main method
        will first check errors, then will 
        1. check limit
        2. try to create activity
        3. build response
           3.1 status
           3.2 decision time
           3.3 available days off
        '''
        # we have errors, let's abort and regroup!
        if self._errors:
            self.set_errors()
            return None

        days_off_node = self.get_days_off_node()

        try:
            # Try to acquire the lock for this operation.
            # Throws DaysOffRejectedError on failure.
            self._try_acquire_temporary_lock()
            # create the pacts
            self._create_activity()
            # create account entry
            self._create_account_entry()
            # check limit 
            self._check_limit()
            # check legality
            self._check_legality()
            # create conflict to trigger save
            self._create_conflicts()      
            # set correct status
            self._status = GRANTED
            # on success, create the roster request log row
            self._create_crew_roster_request()
            # generate report
            self._generate_request_receipt_report()
            # create the new days off in reply
            days_off_node = self.get_days_off_node()
            
            # publish the freeday
            self._publish_granted_freeday()
            # update the lock. It will be automatically "released" after LOCK_GRACE_TIME seconds
            self._start_grace_period()
            self._release_temporary_lock()

        except DaysOffRejectedError, err:
            # well, something didn't want the activity
            self._errors.append(str(err))
            # Remove the lock
            self._release_temporary_lock()
            # set rejected status
            self._status = REJECTED
            # remove activity before get roster
            self._undo_create_activity()
        
        # set the info nodes
        self.set_errors()
        self.set_status()
        self.set_decision_time(self._crew_e.id)
        self.root.append(days_off_node)
        return


    
class CancelDaysOffResponseHandler(CreateDaysOffResponseHandler):
    """
    Just do an empty return with roster an available days off
    """
    
    def get_response(self):
        '''
        Overload to not make anything
        '''
        self._status = CANCELLED
        self.set_status()
        self.set_decision_time(self._crew_e.id)
        days_off_node = self.get_days_off_node()
        self.root.append(days_off_node)
        
    @property
    def use_conflict_handling(self):
        '''
        Return true if response has conflict handling!
        create response uses conflicts!
        '''
        return False

def get_awards(tm, crew_group, type, date):
    try:
        award_row = tm.TM.table("roster_request_awards")[(crew_group, type.id, date)]
        return award_row.awarded
    except modelserver.EntityNotFoundError:
        return None

def get_limit(tm, crew_group, type, date):
    try:
        limit_row = tm.TM.table("roster_request_limit")[(crew_group, type.id, date)]
        return limit_row.limit
    except modelserver.EntityNotFoundError:
        return None

def cancel_days_off(crew, daysoff_type, period_start, period_end, start, duration):
    '''
    Handle the request 
    @param crew:
    @type crew:
    @param daysoff_type:
    @type daysoff_type:
    @param start:
    @type start:
    @param end:
    @type end:
    '''
    # print crew, daysoff_type, period_start, period_end, start, duration
    response = CancelDaysOffResponseHandler(crew, daysoff_type, period_start, period_end, start, duration)
    response.get_response()
    return response

def create_days_off(crew, daysoff_type, period_start, period_end, start, duration):
    '''
    Handle the request 
    @param crew:
    @type crew:
    @param daysoff_type:
    @type daysoff_type:
    @param start:
    @type start:
    @param end:
    @type end:
    '''
    Cui.CuiReloadTable("roster_request_limit")
    Cui.CuiReloadTable("roster_request_awards")
    response = CreateDaysOffResponseHandler(crew, daysoff_type, period_start, period_end, start, duration)
    response.get_response()
    return response

def get_available_days_off(crew, daysoff_type, start, end):
    Cui.CuiReloadTable("roster_request_limit")
    Cui.CuiReloadTable("roster_request_awards")
    print "Logging the crew and dayoff request details- crew: " , crew , " daysoff_type:  " , daysoff_type , " start: " , start ," end:", end
    response = GetAvailableDaysOffResponse(crew, daysoff_type, start, end)
    response.get_response()
    return response
