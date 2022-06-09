#

#
__version__ = "$Revision: 1.10 $"
"""
RequestReplyTests.py
Module for doing:
Testing DIG / Report servers /MQ

Each test case will do the following:

setUp:
 start report server and report worker if needed
   rs_worker_name
   rs_worker_node
   rs_portal_name
   rs_portal_node
 wait for workers to connect to portals
   portal_url
 start dig channels
   dig_processes

 clear queues
   queue
   return queue
 select a test object not previously used
   set_bag, which uses
   bag_test 

testRun:
  send request
    get_test_msg
  to
    queue
  read reply from
    return_queue
  if env TEST_SAVE_REPLY, store reply in
    report_hash
  with key
    get_key
  verify xml syntax for reply
  if stored reply exists, compare reply with stored result

tearDown
  clear queues
   queue
   return queue

example:
class CrewBasicTest(ServiceReqReplyTest):
        
    #Crew basic

    def run_impl(self):
        ServiceReqReplyTest.run_impl(self)
        self.failUnless('<crewId>%s</crewId>'%self.crew in self.current_reply,
                        'Missing crewId for crew in reply')
        self.failUnless('<empno>%s</empno>'%self.crew_empno in self.current_reply,
                        'Missing crew empno for crew empno in reply')

    def get_test_msg(self):
        return 'CrewBasic,%s,%s,Y,Y'%(self.crew_empno,
                                      str(self.pp_start)[0:9])
    def get_key(self):
        
        #Report hash key
        
        key = ServiceReqReplyTest.get_key(self)
        key.extend([str(self.pp_start)[0:9]])
        return key


@date:15Dec2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import unittest
import os
import sys
import subprocess
import xmlrpclib
import time
import random
import re
import Cui
import modelserver
import AbsTime
import RelTime
import Errlog
from carmensystems.dig.jmq import jmq

import carmensystems.rave.api as R
import utils.ServiceConfig as C
import carmensystems.studio.Tracking.OpenPlan as OpenPlan
import carmtest.TestBaseClass as TBC
import carmtest.RosterChangeTests as RCT
import carmtest.GuiTests as GT
import carmtest.SaveTests as ST
from tests.crewlists.test_xmllint import XMLLintTestCase


USED_CREW = set()

class Mq(object):
    """
    Small wrapper class for MQ handling
    """
    def __init__(self,
                 mqserver,
                 mqmanager,
                 mqchannel,
                 mqport,  
                 mqqueue,
                 mqreplyq=''):
        self.mqserver = mqserver
        self.mqmanager = mqmanager
        self.mqchannel = mqchannel
        self.mqport =   mqport
        self.mqqueue = mqqueue
        self.mqreplyq = mqreplyq

    def __str__(self):
        return "/".join(list((self.mqserver,
                              self.mqmanager,
                              self.mqchannel,
                              self.mqport,
                              self.mqqueue,
                              self.mqreplyq)))
    def put(self, message):
        """
        Put text message to queue
        """
        q = None
        conn = None
        error = None
        try:
            if not self.mqreplyq :
                message = jmq.Message(content=r'%s'%message)
            else:
                message = jmq.Message(content=r'%s'%message,
                                      msgType=jmq.Message.requestMessageType,
                                      replyToQ=self.mqreplyq,
                                      replyToQMgr=self.mqmanager)
            conn = jmq.Connection(self.mqserver, self.mqport,  self.mqmanager)
            q = conn.openQueue(self.mqqueue, 'w')
            q.writeMessage(message)
            
            conn.commit()
        except Exception, err:
            error = err
            if q:
                q.close()
            if conn:
                conn.rollback()
        if conn:
            conn.disconnect()
        return error
    
    def get(self, remove=False, all=True):
        """
        Read wrapper
        """
        q = None
        conn = None
        errors = []
        answers = []
        try:
            conn = jmq.Connection(self.mqserver, self.mqport,  self.mqmanager)
            q = conn.openQueue(self.mqqueue, 'r')
            cnt = 0

            while True:
                try:
                    msg = q.readNextMessage(destructive = remove)
                except Exception, err:
                    errors.append(err)
                    msg = None
                    
                if not msg:
                    break
                
                answers.append(msg.content.encode('utf-8'))

                if not all:
                    break
        except Exception, err:
            errors.append(err)
            if conn:
                conn.rollback()
        if q:
            q.close()
        if conn:
            if remove:
                conn.commit()
            conn.disconnect()
        return (answers, errors)
  
        

    
    
class ReqReplyBaseClass(TBC.PerformanceTest, XMLLintTestCase):
    """
    Base class for requst reply handling testcases
    """

    def __init__(self, *args):
        TBC.PerformanceTest.__init__(self, *args)
        self._now = None
        
        self.reply_count = 0

        self.current_reply = None
        self.save_reply = bool(os.environ.get('TEST_SAVE_REPLY',False))
        if self.save_reply:
            self.log('Will save reply to %s'%self.report_hash)



        self.sleep_time = 30
        self.log('Build testcase')
    
    def setUp(self):
        """
        Check enviroment, start things if needed
        """
        self.log('setUp')
        self._now = self.now_time
        self.assertTrue(self._now is not None,'Could not set now time')
        self.log('Now-time is %s'%str(self._now))
        self.assertTrue(self.load_plan(), 'No open plan and unable to load plan!')
        self.clear_queues()
        self.start_reportservers()
        self.start_channels()
        

    def tearDown(self):
        """
        clean up
        """
        self.log('tearDown')
        self.clear_queues()
        #self.stop_reportservers()

        
    def stop_reportservers(self):
        """
        Stop RS
        """
        self.call_reportservers('stop')
        
    def start_reportservers(self):
        """
        Start rs if needed
        """
        stat_stdout, stat_stderr = self.call_desmond('stat',node=self.rs_portal_node)

        portal_running = False
        for line in stat_stdout.split('\n'):
            if 'running with PID' in line:
                if self.rs_portal_name in line:
                    portal_running = True
                    self.log(line)
        worker_running = False            
        stat_stdout, stat_stderr = self.call_desmond('stat',node=self.rs_worker_node)
        for line in stat_stdout.split('\n'):
            if 'running with PID' in line:
                if self.rs_worker_name in line:
                    worker_running = True
                    self.log(line)
        if portal_running and worker_running:
            return
        
        self.call_reportservers('start')
        self.log('Sleeping 30 to allow PORTAL to start')
        time.sleep(30)
        rs_url = self.rs_portal_url
        self.log('Waiting for worker to connect to %s'%rs_url)
        max_sleeps = 120 # allow max 2 hrs for worker to start!
        for i in range (0, max_sleeps):
            stat = xmlrpclib.ServerProxy(rs_url).status() # Text string with worker info
            self.log('Iteration %s gave stat %s'%(i, stat))
            if len(stat)>5: # No worker => stat = '{}\n'
                break
            time.sleep(60)
        else:
            self.fail('Reached max number of sleeps without worker registering at portal')
        
        
        
    def call_reportservers(self, cmd):
        """
        Call rs with command cmd
        """
        output = []
        output.extend(self.call_desmond(cmd,
                                        process=self.rs_portal_name,
                                        node=self.rs_portal_node))
        output.extend(self.call_desmond(cmd,
                                        process= self.rs_worker_name,
                                        node=self.rs_worker_node))
        
        error_found = False
        for lines in output:
            for line in lines.split('\n'):
                self.log(line)
                error_found |= ('error' in line.lower())
        if error_found:
            self.fail('Error starting one or more reportserver process')
        return output

    def start_channels(self):
        """
        Start correct dig channel(s)
        """
        for channel in self.dig_processes:
            output = self.call_desmond('start',
                                       process=channel,
                                       node='dig_node')
            for lines in output:
                for line in lines.split('\n'):
                    self.log(line)
        
    def stop_channels(self):
        """
        Stop channel(s)
        """
        for channel in self.dig_processes:
            self.call_desmond('stop', process=channel, mode='dig_node')
            
    def call_desmond(self, cmd, process='', node=''):
        """
        call CARMUSR/bin/desmond.sh with args
        """
        desmond_cmd = '%s/bin/desmond.sh'%os.environ.get('CARMUSR','')
        if process:
            self.log('Dispatching cmd %s -p %s %s -h %s'%(desmond_cmd,process,
                                                          cmd, node))
            output = subprocess.Popen([r'%s'%desmond_cmd,
                                       '-p %s'%process,
                                       cmd,
                                       '-h %s'%node],
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
        else:
            self.log('Dispatching cmd %s %s -h %s'%(desmond_cmd, cmd, node))
            output = subprocess.Popen([r'%s'%desmond_cmd,
                                       cmd,
                                       '-h %s'%node],
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
        return output

    def send_msg(self, msg):
        """
        Send msg (string) to specifed queue
        """
        self.log('Sendning msg %s'%msg)
        return self.get_mq(self.queue,replyq=self.return_queue).put(msg)

    def read_msg(self, remove=True):
        """
        Read from specifed queue, remove msg if remove=True
        """
        return self.get_mq(self.queue).get(remove=remove)
    
    def read_return_msg(self, remove=True):
        """
        Read from specifed return queue, remove msg if remove=True
        """
        return self.get_mq(self.return_queue).get(remove=remove)
    
    def clear_queues(self):
        """
        Read all messages from queues
        """
        self.log('Clearing queues %s and %s'%(self.queue, self.return_queue))
        self.get_mq(self.queue).get(remove=True,all=True)
        self.get_mq(self.return_queue).get(remove=True,all=True)

    def get_test_msg(self):
        """
        Request to send to report server
        """
        raise NotImplementedError

    def send_request_read_reply(self):
        """
        Send request, wait and read reply and xml-verfiy it
        """
        self.send_msg(self.get_test_msg())
        time.sleep(self.sleep_time)
        self.current_reply = self.read_reply()
        self.log(self.current_reply)
        self.xmllint_verify_reply()
        self.verify_reply_vs_stored()
 

        
    def verify_reply_vs_stored(self):
        stored_reply = self.get_report_template(self.get_key())
        if not stored_reply:
            # we found a stored copy!
            self.log('Found no stored reply for key %s'%self.get_key())
            return 
        self.log('Found stored reply, will match with reply')
        st = stored_reply.split('\n')
        rep = self.current_reply.split('\n')
        len_st = len(st)
        len_rep = len(rep)
        
        for i in range(0,max(len_st, len_rep)):
            try:
                st[i]
            except IndexError:
                self.fail('Difference in message length between stored and read reply :: "%s" not in stored'%rep[i])
            try:
                rep[i]
            except IndexError:
                self.fail('Difference in message length between stored and read reply :: "%s" not in reply'%st[i])
            if st[i] != rep[i]:
                # Filter out things that we know will differ using list of regexps, match => list is non-zero length or list is empty to begin with
                if len([regexp for regexp in self.ignore_differences_regexps if regexp.match(st[i])])==0:
                    self.fail('Difference between stored and reply found! Stored "%s" / Reply "%s"'%(st[i],rep[i]))
    
        self.log('Reply matched stored')
    @property
    def dig_processes(self):
        """
        Dig channels process in desmond
        """
        raise NotImplementedError

    @property
    def rs_worker_node(self):
        """
        Dig channels process in desmond
        """
        raise NotImplementedError
    @property
    def rs_portal_node(self):
        """
        Dig channels process in desmond
        """
        raise NotImplementedError
    @property
    def rs_worker_name(self):
        """
        RS worker process in desmond
        """
        raise NotImplementedError
    @property
    def rs_portal_url(self):
        """
        RS portal url in config
        """
        raise NotImplementedError
    @property
    def rs_portal_name(self):
        """
        RS portal process in desmond
        """
        raise NotImplementedError
    @property
    def queue(self):
        """
        Send queue (ie dig channel in queue)
        """
        raise NotImplementedError
    @property
    def return_queue(self):
        """
        Return queue (ie dig channel out queue)
        """ 
        raise NotImplementedError
    
    @property
    def now_time(self):
        """
        Now time from timeserver or studio!
        """
        try:
            import utils.TimeServerUtils
            return utils.TimeServerUtils.now()
        except:
            now, = R.eval('default_context', 'fundamental.%now%')
            return now
            
    @property
    def report_hash(self):
        """
        Path of file to store reports in
        """
        carmdata = os.environ.get('CARMDATA')
        self.assertFalse(carmdata is None,'Error, CARMDATA env is empty')
            
        report_dir = os.path.join(carmdata,'testing')
        if not os.path.exists(report_dir):
            os.path.mkdirs(report_dir)

        report_file = os.path.join(report_dir, self.__class__.__name__)
        if not os.path.exists(report_file):
            os.system("touch %s"%report_file)

        return report_file
    
    @property
    def ignore_differences_regexps(self):
        return []
    
    def run(self, result=None):
        """
        Run correct method
        """
        TBC.PerformanceTest.run(self, result)
        
    def load_plan(self):
        """
        Load configured plan if needed!
        """
        if self.check_plan_loaded() == "":
            self.assertTrue(self._now is not None,'Could not find now time')
            plan_start_day = str(self._now.month_floor())[0:2]
            plan_end_day = str(self._now.month_ceil())[0:2]
            plan_start_month = str(self._now)[2:5]
            plan_end_month = str(self._now)[2:5]
            plan_start_year = str(self._now)[5:9]
            plan_end_year = str(self._now)[5:9]
            os.environ['TEST_START_DAY'] = plan_start_day
            os.environ['TEST_END_DAY'] = plan_end_day
            os.environ['TEST_START_MONTH'] = plan_start_month
            os.environ['TEST_END_MONTH'] = plan_end_month
            os.environ['TEST_START_YEAR'] = plan_start_year
            os.environ['TEST_END_YEAR'] = plan_end_year
            os.environ['TEST_CCT_AREA'] = 'ALL'
            
            import carmtest.LoadTests as LT
            result = TBC.PerformanceTestResult()
            test = LT.LoadPlanTest('testRun')
            test.run(result)
            Errlog.log(str(result))
            return self.check_plan_loaded() != ""
        else:
            return True

    def get_mq(self, queue, replyq=''):
        """
        Get Mq object connected to corrent things
        """
        import utils.ServiceConfig as C
        s=C.ServiceConfig()
        (_, mqp) =  s.getProperty('site/mq/port')
        (_, mqs) =  s.getProperty('site/mq/server')
        (_, mqm) =  s.getProperty('site/mq/manager')
        (_, mqc) =  s.getProperty('site/mq/channel')
        mq = Mq(mqs,
                mqm,
                mqc,
                mqp,  
                queue,
                mqreplyq=replyq)
        self.log('Created MQ to %s'%str(mq))
        return mq

    def get_model_rows(self, table):
        """
        Get a string set of model rows for current crew in table
        """
        rows = set([])
        
        for row in modelserver.TableManager.instance().table('crew')[(self.crew,)].referers(table,'crew'):
            rows.add(str(row))
        self.log('Found row(s):: \n%s'%('\n'.join(rows)))
        return rows

    def read_reply(self):
        """
        Read service reply
        """
        self.log('Reading reply')
        reply, errors = self.read_return_msg(remove=True)

        if errors:
            self.fail('Error reading from MQ:%s'%str(errors))
        reply = '\n'.join(reply)
        self.reply_count += 1
        if self.save_reply and self.get_report_template(self.get_key()) == '':
            self.save_report_to_template(self.get_key(), reply)
        return reply


    def get_key(self):
        """
        Report hash key
        """
        return [self.id(),
                self.crew_empno,
                str(self.reply_count),
                self.check_plan_loaded(),
                os.environ.get('TEST_START_COMMITID','')]

    
    def get_report_template(self, key):
        """
        Get stored report for key (if any)
        """
        key = ':'.join(key)
        fd = None
        report = []
        append_line = False
        try:
            fd = open(self.report_hash, 'r')
            for line in fd:
                if line.rstrip('\n') == key:
                    append_line = True
                elif append_line and line.startswith('-'):
                    report.append(line.lstrip('-'))
                elif append_line and not line.startswith('-'):
                    break
        except Exception, err:
            self.log(err)
        if fd:
            fd.close()

        if report:
            report[-1] = report[-1].rstrip('\n')
        return ''.join(report)

    def save_report_to_template(self, key, report):
        """
        Save report to hash with key
        """
        fd = None
        try:
            fd = open(self.report_hash, 'a')
            fd.write(":".join(key)+"\n")
            report = report.replace("\n","\n-")
            fd.write('-')
            fd.write(report)
            fd.write('\n')
        finally:
            if fd:
                fd.close()
                

    def xmllint_verify_reply(self):
        """
        Syntax-ically check reply
        """
        (response, output) =  self.xmllint(None, None)
        self.log("Reply verfied with code %s"%response)
        
        return self.xmllint(None, None) # Dummy arguments, since we have the report already!

    def report(self, dummy):
        """
        Return reply as wrapped report
        """
        # Dummy arguments, since we have the report already!
        self.assertFalse(self.current_reply is None, 'Current reply is None!')
        return ([{'content':self.current_reply}],None)


         

class ServiceReqReplyTest(ReqReplyBaseClass, GT.GuiTest):
    """
    Baseclass for testing the crew services interface!
    """

    def __init__(self, *args):
        ReqReplyBaseClass.__init__(self, *args)
        self.crew = None
        self.crew_empno = None
        self.pp_start = None
        self.pp_end  = None
        
    @property
    def dig_processes(self):
        return ['SAS_SERVICES']
    @property
    def rs_worker_node(self):
        return 'dig_node'
    @property
    def rs_portal_node(self):
        return 'dig_node' 
    @property
    def rs_worker_name(self):
        return 'SAS_RS_WORKER_PUBLISH1'
    @property
    def rs_portal_url(self):
        s=C.ServiceConfig()
        return s.getServiceUrl('portal_publish')
    @property
    def rs_portal_name(self):
        return 'SAS_RS_PORTAL_PUBLISH'
    @property
    def queue(self):
        return 'CQFREQ'
    @property
    def return_queue(self):
        return 'SLASK'
    
    def setUp(self):
        ReqReplyBaseClass.setUp(self)
        R.param('fundamental.%use_now_debug%').setvalue(True)
        R.param('fundamental.%now_debug%').setvalue(self._now)
        self.pp_start, = R.eval('default_context','fundamental.%pp_start%')
        self.pp_end, = R.eval('default_context','fundamental.%pp_end%')
        # Select crew
        if self.crew is None:
            self.set_bag()
            
    def tearDown(self):
        ReqReplyBaseClass.tearDown(self)

    def run(self, result=None):
        """
        Run correct test method
        """
        ReqReplyBaseClass.run(self, result)
 
    def set_bag(self):
        """
        Select crew by applying bag_test to candidates
        """
        self.reset_areas()
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
        default_bag = R.context('default_context').bag()
        
        for roster_bag in default_bag.iterators.roster_set():
            if self.bag_test(roster_bag):
                break
        else:
            self.fail('Found no crew to test!')
            return
        self.display_crews([self.crew])
        self.select_crew(self.crew)
        USED_CREW.add(self.crew)
        
    def bag_test(self, roster_bag):
        """
        Test if we want crew and store vital info
        """

        crew_id = roster_bag.crew.id()
                
        # make sure we test different crew
        if crew_id in USED_CREW:
            return False
        self.crew = crew_id
        self.crew_empno = roster_bag.crew.extperkey()
        return True


        
        
    def run_impl(self):
        """
        Basic test implementation
        """
        self.send_request_read_reply()

class LatestServiceReqReplyTest(ServiceReqReplyTest):
    @property
    def rs_worker_node(self):
        return 'dig_node_slave'
    @property
    def rs_worker_name(self):
        return 'SAS_RS_WORKER_LATEST'
    @property
    def rs_portal_url(self):
        s=C.ServiceConfig()
        return s.getServiceUrl('portal_latest')
    @property
    def rs_portal_name(self):
        return 'SAS_RS_PORTAL_LATEST'
    
class CheckInOutBaseTest(ServiceReqReplyTest):
    """
    Send cio request via MQ
    """

                    
    def __init__(self, *args):
        ServiceReqReplyTest.__init__(self, *args)
        
        self.sleep_time = 60
        self.checkin_time = None
        self.checkout_time = None
        self.pre_ci_event_rows = None
        self.pre_ci_status_rows = None

    def bag_test(self, roster_bag):

        if not ServiceReqReplyTest.bag_test(self, roster_bag):
            return False
        if str(roster_bag.checkinout.cio_report()) == self.cio_status:
            self.crew = roster_bag.crew.id()
            self.checkin_time = roster_bag.report_cio.next_checkin()
            self.checkout_time = roster_bag.report_cio.next_checkout()
            self.log('Found crew to check in/out , crewid = %s, time = %s'%(self.crew,
                                                                            self.checkin_time))
            
            self.crew_empno = roster_bag.crew.extperkey_at_date(self.checkin_time)
            return True
        return False


    def get_test_msg(self):
        return "CheckInOut,%s"%self.crew_empno
        
    def run_impl(self):

        # Cache pre model state
        pre_ci_event_rows = self.get_model_rows('cio_event')
        pre_ci_status_rows = self.get_model_rows('cio_status')
    
        # Send actual request
        self.send_request_read_reply()
        OpenPlan.refreshGui()

        # get post model state
        post_ci_event_rows = self.get_model_rows('cio_event')
        post_ci_status_rows = self.get_model_rows('cio_status')

        # Diff pre oand post model states
        cio_event_change = pre_ci_event_rows^post_ci_event_rows
        cio_status_change = pre_ci_status_rows^post_ci_status_rows

        
        if not cio_event_change:
            self.fail('No change to cio_event')
        else:
            self.log('Found change to cio_event %s'%str(cio_event_change))
            
        if not cio_status_change:
            self.fail('No change to cio_status')
        else:
            self.log('Found change to cio_status %s'%str(cio_status_change))

        self.failUnless(self.cio_reply_verification_1st in self.current_reply,
                        'Incorrect first CIO reply!')

        # Test when already checked in
        self.send_request_read_reply()
        self.failUnless(self.cio_reply_verification_2nd in self.current_reply,
                        'Incorrect second CIO reply!')
            
    @property
    def ignore_differences_regexps(self):
        return [re.compile(r'.*[0-9][0-9][A-Z]{3}[0-9]{4} [0-9][0-9]:[0-9][0-9].*')] #10DEC2009 06:20
    
    @property
    def cio_status(self):
        """
        Rave variable lookup paramter
        """
        raise NotImplementedError
    @property
    def cio_reply_verification_1st(self):
        """
        Find in 1st reply
        """
        raise NotImplementedError
    
    @property
    def cio_reply_verification_2nd(self):
        """
        Find in 2nd reply
        """
        raise NotImplementedError
    
class CheckInTest(CheckInOutBaseTest):
    """
    Test checkin in
    """
    @property
    def cio_status(self):
        return 'checkinout.ci'
    @property
    def cio_reply_verification_1st(self):
        return 'CHECK IN VERIFICATION'
    @property
    def cio_reply_verification_2nd(self):
        return 'Already checked in'

    def get_key(self):
        """
        Report hash key
        """
        key = CheckInOutBaseTest.get_key(self)
        key.append(str(self.checkin_time))
        return key

class CheckInWithPublishTest(CheckInTest):
    """
    Test checkin in
    """
    def setUp(self):
        self.call_desmond('start',
                          process='SAS_EXT_PUBLISH_SERVER',
                          node=self.rs_portal_node)
        
        CheckInTest.setUp(self)
        

class CheckOutTest(CheckInOutBaseTest):
    """
    Test checkin in
    """
    @property
    def cio_status(self):
        return 'checkinout.co'
    @property
    def cio_reply_verification_1st(self):
        return 'CHECK OUT VERIFICATION'
    @property
    def cio_reply_verification_2nd(self):
        return 'Already checked out'

    def get_key(self):
        """
        Report hash key
        """
        key = CheckInOutBaseTest.get_key(self)
        key.append(str(self.checkout_time))
        return key
    
        
class CrewRosterTest(ServiceReqReplyTest):
    """
    Test crew roster report
    """
        
    NR_ACTIVTITES_IN_PP = 5
    def bag_test(self, roster_bag):
        if not ServiceReqReplyTest.bag_test(self, roster_bag):
            return False
        if len([leg_bag for leg_bag in roster_bag.iterators.leg_set() \
                if leg_bag.leg.in_pp()])>= CrewRosterTest.NR_ACTIVTITES_IN_PP:
            self.crew = roster_bag.crew.id()
            self.crew_empno = roster_bag.crew.extperkey()
            self.log('Found crew %s with enought legs in pp'%self.crew)
            return True
        return False

    
                
    def run_impl(self):
        ServiceReqReplyTest.run_impl(self)
        self.failUnless('<crewId>%s</crewId>'%self.crew in self.current_reply,
                        'Missing crewId for crew in reply')
        self.failUnless('<empno>%s</empno>'%self.crew_empno in self.current_reply,
                        'Missing crew empno for crew empno in reply')

    def get_test_msg(self):
        return 'CrewRoster,%s,Y,Y,N,Y,N,%s,%s'%(self.crew_empno,
                                                str(self.pp_start)[0:9],
                                                str(self.pp_end)[0:9])
    def get_key(self):
        """
        Report hash key
        """
        key = ServiceReqReplyTest.get_key(self)
        key.extend([str(self.pp_start)[0:9],
                    str(self.pp_end)[0:9]])
        return key
    
class CrewBasicTest(ServiceReqReplyTest):
    
    """
    Crew basic
    """
    def run_impl(self):
        ServiceReqReplyTest.run_impl(self)
        self.failUnless('<crewId>%s</crewId>'%self.crew in self.current_reply,
                        'Missing crewId for crew in reply')
        self.failUnless('<empno>%s</empno>'%self.crew_empno in self.current_reply,
                        'Missing crew empno for crew empno in reply')

    def get_test_msg(self):
        return "CrewBasic,%s,%s,Y,Y"%(self.crew_empno,
                                      str(self.pp_start)[0:9])
    def get_key(self):
        """
        Report hash key
        """
        key = ServiceReqReplyTest.get_key(self)
        key.extend([str(self.pp_start)[0:9]])
        return key

                                                   
class CrewListTest(ServiceReqReplyTest):
    
    """
    Crew list
    """
    
    def __init__(self, *args):
        ServiceReqReplyTest.__init__(self, *args)
        self.fd = None
        self.udor = None
        self.adep = None
        self.ades = None
        self.flight_id = None
        
    def bag_test(self, roster_bag):
        if not ServiceReqReplyTest.bag_test(self, roster_bag):
            return False
        for leg_bag in roster_bag.iterators.leg_set():
            if leg_bag.leg.in_pp() and leg_bag.leg.is_active_flight():
                self.fd = leg_bag.leg.fd_or_uuid()
                self.flight_id = leg_bag.leg.flight_id()
                self.udor = leg_bag.leg.udor()
                self.adep = leg_bag.leg.start_station()
                self.ades = leg_bag.leg.end_station()
                self.log('Found leg <%s/%s/%s/%s>'%(self.fd,self.udor,self.adep, self.ades))
                
                self.crew = leg_bag.crew.id()
                self.crew_empno = leg_bag.crew.extperkey()
                return True
        return False
    
    def run_impl(self):
        ServiceReqReplyTest.run_impl(self)
        self.failUnless('<flightId>%s</flightId>'%self.flight_id in self.current_reply,
                        'Incorrect flight descriptor in reply!')
        self.failUnless('<crewId>%s</crewId>'%self.crew in self.current_reply,
                        'Missing crewId for crew in reply')
        self.failUnless('<empno>%s</empno>'%self.crew_empno in self.current_reply,
                        'Missing crew empno for crew empno in reply')

    def get_test_msg(self):
        return 'CrewList,%s,%s,N,Y,%s,%s,00:00,,Y,Y,Y,N,Y,N,N,N,,'%(self.fd,
                                                                    str(self.udor)[0:9],
                                                                    self.adep,
                                                                    self.ades)
    def get_key(self):
        """
        Report hash key
        """
        
        key = ServiceReqReplyTest.get_key(self)
        key.extend([self.fd,
                    str(self.udor)[0:9],
                    self.adep,
                    self.ades])
        return key
    
class GetReportListTest(ServiceReqReplyTest):
    
    """
    Get Report List
    """
    
        
    def get_test_msg(self):
        return 'GetReportList,%s'%(self.crew_empno)
    
class GetReportPilotLogTest(LatestServiceReqReplyTest, CrewListTest):
    
    """
    Get Report List
    """
   
    def __init__(self, *args):
        LatestServiceReqReplyTest.__init__(self,*args)
        self.test_msg = ""
        self.fd = None
        self.udor = None
        self.adep = None
        self.ades = None
        self.flight_id = None
        self.limit = None
        self.test = ''
        
    def testRun(self):
        """ disable main test"""
        pass


    
    def bag_test(self, roster_bag):
        result = CrewListTest.bag_test(self, roster_bag)
        if not result:
            return False
        if self.udor >= self._now:
            return False
        return CrewListTest.bag_test(self, roster_bag)

    def test_PILOTLOGFLIGHT(self):
        (year, month, day, hr, min) = self.udor.split()
        self.test_msg ='GetReport,PILOTLOGFLIGHT,3,%s,%s,%s'%(self.crew_empno,
                                                              self.fd.rstrip(' '),
                                                              "%s%s%.2d"%(year,month,day))
        LatestServiceReqReplyTest.run_impl(self)
        
    def test_PILOTLOGFLIGHT_future(self):
        (year, month, day, hr, min) = self.udor.split()
        year += 1
        self.test_msg ='GetReport,PILOTLOGFLIGHT,3,%s,%s,%s'%(self.crew_empno,
                                                              self.fd.rstrip(' '),
                                                              "%s%s%.2d"%(year,month,day))
        LatestServiceReqReplyTest.run_impl(self)
        
    def test_PILOTLOGSIM(self):
        date = self.udor.ddmonyyyy(True)
        year = date[5:9]
        month = date[2:5]
        self.test_msg ='GetReport,PILOTLOGSIM,3,%s,%s,%s'%(self.crew_empno,
                                                           month,
                                                           year)
        LatestServiceReqReplyTest.run_impl(self)
       
        
    def test_PILOTLOGCREW(self):
        date = self.udor.ddmonyyyy(True)
        year = date[5:9]
        month = date[2:5]
        self.test_msg ='GetReport,PILOTLOGCREW,3,%s,%s,%s'%(self.crew_empno,
                                                            month,
                                                            year)
        LatestServiceReqReplyTest.run_impl(self)
         
    def test_PILOTLOGACCUM(self):
        
        self.test_msg ='GetReport,PILOTLOGACCUM,1,%s'%self.crew_empno
        LatestServiceReqReplyTest.run_impl(self)

    def get_test_msg(self):
        return self.test_msg
    
    def get_key(self):
        """
        Report hash key
        """
        
        return CrewListTest.get_key(self)
        
class GetReportCOMPDAYSTest(ServiceReqReplyTest):

    def __init__(self, *args):
        ServiceReqReplyTest.__init__(self, *args)
        self.account = ""
        
    def get_test_msg(self):
        (year, month, day, hr, min) = self.pp_end.split()
        
        return 'GetReport,COMPDAYS,3,%s,%s,%s'%(self.crew_empno,
                                                self.account,
                                                year)
  

    def testRun(self):
        """Disable main test"""
        self.account = 'XX'
        self.performance_test(self.run_impl)
        
    def test_f7s(self):
        self.account = 'F7S'
        self.performance_test(self.run_impl)

    def test_f3(self):
        self.account = 'F3'
        self.performance_test(self.run_impl)
        
    def test_f3s(self):
        self.account = 'F3S'
        self.performance_test(self.run_impl)

    def test_f0(self):
        self.account = 'F0'
        self.performance_test(self.run_impl)

    def get_key(self):
        """
        Report hash key
        """
        
        key = ServiceReqReplyTest.get_key(self)
        key.extend([self.account, str(self.pp_end)[0:9]])
        return key
    
class GetReportVACATIONTest(ServiceReqReplyTest):

    def get_test_msg(self):
        (year, month, day, hr, min) = self.pp_end.split()
        
        return 'GetReport,VACATION,3,%s,%s,%s'%(self.crew_empno,
                                                self.account,
                                                year)
     
    def testRun(self):
        """Disable main test"""
        self.account = 'XX'
        self.performance_test(self.run_impl)
        
    def test_VA(self):
        self.account = 'VA'
        self.performance_test(self.run_impl)

    def test_F7(self):
        self.account = 'F7'
        self.performance_test(self.run_impl)
        
    def test_VA_SAVED_1(self):
        self.account = 'VA_SAVED_1'
        self.performance_test(self.run_impl)

    def test_F32(self):
        self.account = 'F32'
        self.performance_test(self.run_impl)   

    def get_key(self):
        """
        Report hash key
        """
        
        key = ServiceReqReplyTest.get_key(self)
        key.extend([self.account, str(self.pp_end)[0:9]])
        return key

def get_random_suite(nr_tests=50):
    test_classes = [CheckInTest,
                    CheckOutTest,
                    CheckInWithPublishTest,
                    CrewRosterTest,
                    CrewBasicTest,
                    CrewListTest,
                    GetReportListTest,
                    GetReportPilotLogTest,
                    GetReportCOMPDAYSTest,
                    GetReportVACATIONTest]
    suite = unittest.TestSuite()
    for i in range(0, nr_tests):
        test_class = random.choice(test_classes)
        test_cases = unittest.TestLoader().getTestCaseNames(test_class)
        suite.addTest(test_class(random.choice(test_cases)))
    return suite
    
 
def get_testsuite(testcase_list=[]):
    if 'RANDOM' in testcase_list:
        return get_random_suite()
    
    test_classes = [CheckInTest,
                    CheckOutTest,
                    CrewRosterTest,
                    CrewBasicTest,
                    CrewListTest,
                    GetReportListTest,
                    GetReportPilotLogTest,
                    GetReportCOMPDAYSTest,
                    GetReportVACATIONTest]
    
    if testcase_list and not 'ALL' in testcase_list:
        test_classes = [test_class for test_class in test_classes if \
                        test_class.__name__.upper() in testcase_list]
        
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))

    return suite
    
#GetReportList,35162
#GetReport,PILOTLOGFLIGHT,3,18704,SK 0972,20100103
#GetReport,PILOTLOGFLIGHT,3,18704,SK 0972,20100104
#GetReport,PILOTLOGFLIGHT,3,37315,SK 0972,20100108
#GetReport,PILOTLOGFLIGHT,3,37315,SK 0972,20100109
#GetReport,PILOTLOGFLIGHT,3,37315,SK 0973,20100108
#GetReport,COMPDAYS,3,37294,SELECT TYPE,2009
#GetReport,VACATION,3,37294,SELECT TYPE,2010
#GetReport,COMPDAYS,3,37294,SELECT TYPE,SELECT
#GetReport,CREWSLIP,3,14415,JAN,2010

# Use these lines to manually run tests cases from inside Studio (crtl+0)
#import carmtest.RequestReplyTests as F
#import carmtest.TestBaseClass as C
#reload(F)
#import unittest
#suite = unittest.TestSuite()
#result = C.PerformanceTestResult()
#suite.addTest(F.CheckInOutTest('testRun'))
#suite.run(result)
#print str(result)
#raise 'undo' #If create undo in studio
