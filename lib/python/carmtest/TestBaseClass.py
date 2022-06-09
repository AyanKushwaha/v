#

#
__version__ = "$Revision: 1.9 $"
"""
TestBaseClass
Module for doing:
Provide basic clss for testcases (pre, run, post actions)
@date:02Apr2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


import os
import subprocess
import time
import unittest

import Cui
import Variable
import carmensystems.rave.api as R
import carmensystems.studio.MacroRecorder.PlayMacro as PM
import Errlog
import AbsTime
import RelTime
import modelserver

import TestUtils as TU

class PerformanceTestResult(unittest.TestResult):

    def __init__(self):
        unittest.TestResult.__init__(self)
        self.results = []


    def header(self,test):
        return 'TESTCASE :: %s :: '%test.id()
        
    def addError(self, test, err):
        result = [self.header(test)+'FAILED',
                  self.header(test)+'MESSAGE:']
        
        for line in self._exc_info_to_string(err, test).split('\n'):
            result.append(self.header(test)+line)
            
        self.errors.append('\n'.join(result)+'\n')

    def addFailure(self, test, err):
        self.addError(test, err)

    def addSuccess(self, test):

        real = abs(test.after['TIME']-test.before['TIME'])
        cpu = abs(test.after['CPU']-test.before['CPU'])
        sz = abs(test.after['SZ']-test.before['SZ'])
        rss = abs(test.after['RSS']-test.before['RSS'])
        result=[self.header(test)+'FINISHED OK',
                self.header(test)+'MESSAGE:',
                self.header(test)+'REAL: %.3f s'%real,
                self.header(test)+'CPU: %.3f s'%cpu,
                self.header(test)+'MEM_SYS: %d m' %sz,
                self.header(test)+'MEM_RSS: %d m'%rss]
        
        self.results.append('\n'.join(result)+'\n')
        
    def __str__(self):
        ret = "TESTCASE SUMMARY : %s ; runs=%i ; successes=%i ; errors=%i ; failures=%i \n" % \
              (self.__class__.__name__, self.testsRun,
               len(self.results),
               len(self.errors),
               len(self.failures))
        for result in self.results:
            ret += result
        for error in self.errors:
            ret += str(error)
        return ret
    
class PerformanceTest(unittest.TestCase):
    """
    Basic test object
    """
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.pid = os.getpid()
        self.before = {'TIME':0, 'CPU':0 , 'SZ':0, 'RSS':0}
        self.after = {'TIME':0, 'CPU':0 , 'SZ':0, 'RSS':0}


        
    def setUp(self):
        self.log("setUp")
        plan = self.check_plan_loaded()
        self.failIf(plan == "", "No subplan loaded")

                        
        
    def tearDown(self):
        self.log("tearDown")


    def testRun(self):
        self.performance_test(self.run_impl)

    def performance_test(self, func, args=[]):
        self.before = self.get_measure_dict()
        func(*args)
        self.after = self.get_measure_dict()
        
    def check_plan_loaded(self):
        plan = Variable.Variable("")
        Cui.CuiGetSubPlanName(Cui.gpc_info, plan)
        self.log('Working in plan %s'%str(plan.value ))
        return plan.value
        
    def run_impl(self):
        time.sleep(1)
            
    def get_measure_dict(self):
        return {'SZ':self.getfree(),
                'RSS':self.getmem("rss"),
                'TIME':time.time(),
                'CPU':time.clock()}
    
    def getmem(self,s="size"):
        # unit=MB
        p = subprocess.Popen("ps -p %d -o %s " % ( self.pid,s ), shell="False", stdout=subprocess.PIPE)
        return int(p.stdout.readlines()[1])/1024
    

    def getfree(self, opt=0, flags="-m"):
        # use the 'free' command to determine the available system memory
        # unit = MB
        x=subprocess.Popen("free "+flags, shell="False", stdout=subprocess.PIPE).stdout.readlines()
        mem=int(x[1].split()[3])
        withbuff=int(x[2].split()[3])
        swap=int(x[3].split()[3])
        if opt==0:
            return withbuff+swap
        if opt==1:
            return mem+swap
        return

    def is_tracking(self):
        try:
            import carmusr.application as application
            return application.isTracking
        except ImportError, err:
            self.fail(err)

    def is_planning(self):
        try:
            import carmusr.application as application
            return application.isPlanning
        except ImportError, err:
            self.fail(err) 
        
    def log(self, msg):
        Errlog.log("%s :: %s"%(self.id(), msg))


class MacroTest(PerformanceTest):

    def __init__(self, *args):
        PerformanceTest.__init__(self, *args)
        self.macro = ''
        self.tmp_macro = None
        self.tmp_macro_class = EmptyTmpMacro
            
    def setUp(self):
        PerformanceTest.setUp(self)
        self.set_macro(self.get_macro_file())

    def tearDown(self):
        PerformanceTest.tearDown(self)
        if self.tmp_macro:
            del self.tmp_macro
            self.tmp_macro = None
        
    def get_macro_file(self, values={}):
        if self.tmp_macro is None:
            self.tmp_macro = self.tmp_macro_class()
        return self.tmp_macro.generate_tmp(values)

    
    def set_macro(self, macro_file):
        
        if not os.path.exists(macro_file):
            self.fail('Could not find macrofile %s'%macro_file)
        self.macro = macro_file
        return self.macro
    
    def run_impl(self):
        PM.PlayMacroFile(self.macro)
    
        

################ Empty Macro ############
class EmptyTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
</All>
"""
#########################################
