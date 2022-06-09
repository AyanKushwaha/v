#

#
__version__ = "$Revision: 1.17 $"
"""
Tests
Module for doing:
Handle pre, run, post based tests 
@date:02Apr2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import os
import sys
import traceback
import Errlog
import unittest
import carmtest.TestBaseClass


def implemented_tests_dict():
    # Syntax
    # NAME:(module,class)
    return {   'BASIC_TEST':('carmtest.TestBaseClass','PerformanceTest'),
               'ASSIGN_SMALL':('carmtest.RosterChangeTests','AssignSmallTest'),
               'DEASSIGN_SMALL':('carmtest.RosterChangeTests','DeassignSmallTest'),
               'DEASSIGN_LARGE':('carmtest.RosterChangeTests','DeassignLargeTest'),
               'BUYDAYS_TEST':('carmtest.RosterChangeTests','BuyDaysTest'),
               'UNBUYDAYS_TEST':('carmtest.RosterChangeTests','UnBuyDaysTest'),
               'CREATE_PACT':('carmtest.RosterChangeTests','CreatePactTest'),
               'CREATE_R_PACT':('carmtest.RosterChangeTests','CreateRPactTest'),
               'REMOVE_PACT':('carmtest.RosterChangeTests','RemovePactTest'),
               'REMOVE_VA_PACT':('carmtest.RosterChangeTests','RemoveVAPactTest'),
               'CREATE_VA_PACT':('carmtest.RosterChangeTests','CreateVAPactTest'),
               'ACCOUNT_UPDATE':('carmtest.CommonCarmusrTests','AccountHandlerTest'),
               'SAVE_SMALL':('carmtest.SaveTests','SaveSmallTest'),
               'SAVE_SMALL_5':('carmtest.SaveTests','SaveSmall5TimesTest'),
               'SAVE_LARGE':('carmtest.SaveTests','SaveLargeTest'),
               'REFRESH_SMALL':('carmtest.SaveTests', 'RefreshSmallTest'),
               'REFRESH_EMPTY':('carmtest.SaveTests','RefreshEmptyTest'),
               'LOAD_PUBLISHED_ROSTERS':('carmtest.LoadTests','LoadAllPublishedRosters'),
               'LOAD_100_PUBLISHED_ROSTERS':('carmtest.LoadTests','Load100PublishedRosters'),
               'LOAD_CHUNK_PUBLISHED_ROSTERS':('carmtest.LoadTests','LoadChunkPublishedRosters'),
               'LOAD_PLAN':('carmtest.LoadTests','LoadPlanTest'),
               'ROSTER_PUBLISH':('carmtest.RosterPublishTests','RosterPublishTest'),
               'SIMPLE_GUI_TEST':('carmtest.GuiTests','GuiTest'),
               'FULL_GUI_TEST':('carmtest.GuiTests','FullGuiTest'),
               'RAVE_TEST':('carmtest.GuiTests','RaveTest'),
               'CREW_CFH_TEST':('carmtest.FormTests','CrewCFHFormTest'),
               'CREW_WAVE_TEST':('carmtest.FormTests','CrewWaveFormTest'),
               'FIND_ASSIGNABLE_CREW':('carmtest.FormTests','FindAssignableCrewTest'),
               }

def get_testsuite(test_cases=[], modules=[]):
    
    suite = unittest.TestSuite()
    cases = implemented_tests_dict()

    if modules:
        for case, item in implemented_tests_dict().items():
            test_module, test_class = item
            if test_module.upper() not in modules:
                del cases[case]
                
    test_cases = [case for case in cases.keys() if 
                 (test_cases == [] or case in test_cases)]
    
    for case in test_cases:
        try:
            module, class_name = cases[case]
            importStatement = 'import %s' % module
            Errlog.log('carmtest.Tests:: %s'%importStatement)
            exec importStatement in globals()
            buildStatement = "suite.addTests(unittest.makeSuite(%s.%s))"%(module,class_name)
            Errlog.log('carmtest.Tests:: %s'%buildStatement)
            exec buildStatement 
        except Exception, err:
            Errlog.log('carmtest.Tests:: Error setting up case; %s ;  %s'% (case, err))

    if suite.countTestCases() == 0:
        raise Exception("Found no test cases! (looked for %s)"%(test_cases))
    return suite


def run_text_tests(test_cases=[], modules=[]):
    """
    Empty list = run all implemented cases
    """
    suite = get_testsuite(test_cases, modules)
    unittest.TextTestRunner(verbosity=3).run(suite)

def run_performance_tests(test_cases=[],modules=[]):
    
    result = carmtest.TestBaseClass.PerformanceTestResult()
    suite = get_testsuite(test_cases,modules)
    suite.run(result)
    Errlog.log(str(result))
    return result

    
    


    
# Use these lines to manually run tests cases from inside Studio (crtl+0)
#import carmtest.FormTests as F
#import carmtest.TestBaseClass as C
#reload(F)
#import unittest
#suite = unittest.TestSuite()
#result = C.PerformanceTestResult()
#suite.addTest(F.LegFormTest('testRun'))
#suite.run(result)
#print str(result)
#raise 'undo'
