#

#
__version__ = "$Revision: 1.7 $"
"""
LoadTests
Module for doing:
Testcases for load
@date:03Apr2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import os
import sys
import traceback

import Cui
import AbsTime
import RelTime
import carmensystems.rave.api as R
import utils.ServiceConfig as C
import modelserver
import Errlog

from carmtest.TestBaseClass import PerformanceTest



class LoadAllPublishedRosters(PerformanceTest):

    def __init__(self, *args):
        PerformanceTest.__init__(self, *args)
        self.crews = []
        
    def testPublished(self):
        self.log('Loading version PUBLISHED')
        self.performance_test(self.load_impl, ['PUBLISHED'])

    def testInformed(self):
        self.log('Loading version INFORMED')
        self.performance_test(self.load_impl, ['INFORMED'])

    def testDelivered(self):
        self.log('Loading version DELIVERED')
        self.performance_test(self.load_impl, ['DELIVERED'])
        
    def testScheduled(self):
        self.log('Loading version SCHEDULED')
        self.performance_test(self.load_impl, ['SCHEDULED'])
        
    def load_impl(self, version):
        Cui.CuiLoadPublishedRosters(Cui.gpc_info, self.crews, version)
        
class Load100PublishedRosters(LoadAllPublishedRosters):

    def setUp(self):
        LoadAllPublishedRosters.setUp(self)
        self.crews = [crew.id for crew in modelserver.TableManager.instance().table('crew')][:100]
        print self.crews

class LoadChunkPublishedRosters(LoadAllPublishedRosters):

    def __init__(self, *args):
        LoadAllPublishedRosters.__init__(self, *args)
        self.ix = 1
        
    def setUp(self):
        LoadAllPublishedRosters.setUp(self)
        self.ix = 1
        self.crews = [crew.id for crew in modelserver.TableManager.instance().table('crew')]
        
    def load_impl(self, version):
        failsafe = 0
        while len(self.crews[(self.ix-1)*100:self.ix*100])>0:
            Cui.CuiLoadPublishedRosters(Cui.gpc_info, self.crews[(self.ix-1)*100:self.ix*100], version)
            self.ix += 1
            failsafe += 1
            if failsafe > 1000:
                self.fail('Aborting chunk load pf published rosters, something is wrong in test')
        
class LoadPlanTest(PerformanceTest):

    def setUp(self):
        self.create_bypass()
        
    def create_bypass(self):
        self.log('Opening plan')
        app= (os.environ.get('SK_APP','')).upper()

        s=C.ServiceConfig()
        
        (_, c_file) = s.getProperty('file_prefix')
        (_, c_schema) =  s.getProperty('db/user')
    
        file = os.environ.get('TEST_LP_PREFIX', 'dummy')
        schema = os.environ.get('TEST_SCHEMA', 'dummy')
        
        self.lp_path = os.path.join(file,schema)
        self.sp_path = os.path.join(file,schema,schema)
        plan_path = os.path.join(os.environ.get('CARMDATA',''),'LOCAL_PLAN')
        if not os.path.exists(os.path.join(plan_path,self.lp_path)) or \
               not os.path.exists(os.path.join(plan_path,self.sp_path)):
            self.log('Reverting to configured plan, could not find path "%s" or "%s"'%(self.lp_path,
                                                                                       self.sp_path))
            self.lp_path = os.path.join(c_file,c_schema)
            self.sp_path = os.path.join(c_file,c_schema,c_schema)
     
        self.log('Opening plan, path %s and %s'%(self.lp_path, self.sp_path))   
        
        start_day  = os.environ.get('TEST_START_DAY', '01')
        end_day    = os.environ.get('TEST_END_DAY', '31')
        start_mon  = os.environ.get('TEST_START_MONTH', 'JUL')
        end_mon    = os.environ.get('TEST_END_MONTH', 'AUG')
        start_year = os.environ.get('TEST_START_YEAR', '2008')
        end_year   = os.environ.get('TEST_END_YEAR', '2008')
        area_ccr   = os.environ.get('TEST_CCR_AREA', 'FD_SKS_B737')
        area_cct   = os.environ.get('TEST_CCT_AREA', 'ALL')
        
        if app =='PLANNING':
            self.bypass={"FORM":"OPEN_PLAN",
                         "PERIOD_START_FIELD":'%s%s%s'%(start_day,start_mon,start_year),
                         "PERIOD_END_FIELD":'%s%s%s'%(end_day,end_mon,end_year),
                         'PLANNING_AREA_FIELD':area_ccr,
                         'PRODUCT_FIELD': 'Rostering',
                         'PARAM_SET_FIELD': 'NONE',
                         'OK': ''}
        elif app == 'TRACKING':
            self.bypass={'FORM': 'Load_filter_diag',
                         'START_MONTH': start_mon,
                         'START_YEAR': start_year,
                         'END_MONTH': end_mon,
                         'END_YEAR': end_year,
                         'PLANNINGAREA': area_cct,
                         'B_OK': ''}
            print self.bypass
        else:
            self.fail('Unknown app set in SK_APP')
            
    def run_impl(self):
        Cui.CuiOpenSubPlan(self.bypass,
                           Cui.gpc_info,
                           self.lp_path,
                           self.sp_path)

    def tearDown(self):
        plan = self.check_plan_loaded()
        self.failIf(plan == "", "No subplan loaded")
