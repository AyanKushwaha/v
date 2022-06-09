#

#
__version__ = "$Revision: 1.5 $"
"""
SystemTests
Module for doing:
Test system rather than specific functionallity
Current tests
  RequestReply
@date:22Dec2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import os
import signal
import time
import unittest

import Cui
import Cps
import Errlog
import Gui
import AbsTime

import carmtest.RequestReplyTests as PythonTests
import carmtest.TestBaseClass as T
import carmtest.Perftest as PT

try:
    RUNS = int(os.environ.get('TEST_NR_OF_RUNS',1))
except:
    RUNS = 1
    
def run():
    testcase_list = []
    module_list = []
    try:
        print sys.argv
        testcase_list = [_ for _ in sys.argv[1].split("|")  if _]
    except Exception, err:
        Errlog.log(err)
        return 1 
    Errlog.log("===========  Test cases %s =========="%str(testcase_list))
    Errlog.log("===========  Test suite START ==========")
  
    try:
        for i in range(0,RUNS):
            run_tests(testcase_list)
            PT.kill_jvm()
    except Exception, err:
        Errlog.log('============= :: ERROR : %s =========='%err)

   
    return 0

def run_tests(testcase_list=[]):
    res = T.PerformanceTestResult()

    suite = PythonTests.get_testsuite(testcase_list) 
        
    suite.run(res)
    
    Errlog.log(str(res))


    
if __name__ == '__main__':
    run()
    PT.kill_jvm()
    # Comment out these rows when debugging

    Cui.CuiExit(Cui.gpc_info,1)
#Run follwoing lines in studio (crtl+0)
#import carmtest.SystemTests as S
#reload(S)
#S.run_tests()
