########################################################################

#
"""



"""
import os
import signal
import time
import random
import unittest

import Cui
import Cps
import Errlog
import Gui
import AbsTime

import carmtest.TestBaseClass



# coverage_path was outdated. Get new path if needed.
coverage_path = None


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
               'FIND_ASSIGNABLE_CREW':('carmtest.FormTests','FindAssignableCrewTest')
               }

def get_testsuite(test_cases=[]):
    
    suite = unittest.TestSuite()
    impl_cases = implemented_tests_dict()

    if not test_cases:
        test_cases = impl_cases.keys()   
    
    for case in test_cases:
        try:
            if case not in impl_cases:
                test = case.split('.')
                class_name = test[-1]
                module = '.'.join(test[0:-1])
                
            else:
                module, class_name = impl_cases[case]
            importStatement = 'import %s' % module
            Errlog.log('carmtest.Tests:: %s'%importStatement)
            exec importStatement 
            buildStatement = "suite.addTests(unittest.TestLoader().loadTestsFromTestCase(%s.%s))"%(module,class_name)
            Errlog.log('carmtest.Perftests:: %s'%buildStatement)
            exec buildStatement
        except Exception, err:
            Errlog.log('carmtest.Perftests:: Error setting up case; %s ;  %s'% (case, err))

    if suite.countTestCases() == 0:
        raise Exception("Found no test cases! (looked for %s)"%(test_cases))
    return suite


def run():

    testcase_list = []
    module_list = []
    try:
        runs = int(sys.argv[1])
        testcase_list = [_ for _ in sys.argv[2].split("|")  if _]
        
    except Exception, err:
        Errlog.log(err)
        return 1


    
    Errlog.log("===========  Open Plan START ==========")
    try:
        suite = get_testsuite(testcase_list)
        Errlog.log("===========  Suite contains Test cases %s =========="%str(suite))
        Errlog.log("===========  Open Plan START ==========")
        run_tests(get_testsuite(['LOAD_PLAN']))
    except Exception, err:
        Errlog.log('carmtest.Perftests :: ERROR : %s'%err)
        return 1
        
    if len(testcase_list) == 1 and testcase_list[0] == "LOAD_PLAN":
        return 0

    Errlog.log("===========  Test suite START ==========")
    completed_runs = 1
    while completed_runs <= runs:
        Errlog.log("===========  Test suite run %s=========="%completed_runs)
        try:
            run_tests(suite)
            kill_jvm()
        except Exception, err:
            Errlog.log('============= :: ERROR : %s =========='%err)
        completed_runs += 1 
   
    return 0

def run_tests(suite):
    coverage_file = os.environ.get('TEST_COVERAGE_FILE',None)
    if coverage_file:
        Errlog.log("===========  Logging coverage  (tmpfile: %s) =========="%str(coverage_file))
        run_tests_with_coverage(suite,coverage_file )
    else:
        run_performance_tests(suite) 
    
def run_tests_with_coverage(suite, coverage_file=None):

    try:
        if os.path.exists(coverage_path) and coverage_path not in sys.path:
            path = [coverage_path]
            path += sys.path
            sys.path = path
        import coverage
        cov = coverage.coverage(data_file=coverage_file,  auto_data=True)
    except ImportError, err:
        Errlog.log('carmtest.Perftests :: %s'%err)
        return 1
    if cov is None:
        Errlog.log('carmtest.Perfests :: ERROR : No created coverage object!')
        return 1
    # start measurement
    cov.load()
    Errlog.log('carmtest.Perftests :: Started coverage tool')
    cov.start()
    # run tests
    run_performance_tests(suite) 
    #stop and report
    cov.stop()
    Errlog.log('carmtest.Perftests :: Stopped coverage tool')
    cov.save()
    outdir = os.path.join(os.environ.get('CARMDATA','/tmp'),'REPORTS', 'COVERAGE')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    cov.html_report(directory=outdir, ignore_errors=True)
    
def run_text_tests(test_cases=[]):
    """
    Empty list = run all implemented cases
    """
    suite = get_testsuite([])
    unittest.TextTestRunner(verbosity=3).run(suite)

def run_performance_tests(suite):
    
    result = carmtest.TestBaseClass.PerformanceTestResult()
    suite.run(result)
    Errlog.log(str(result))
    return result

def kill_jvm():
    pid = Cps.Find('','Launcher')
    if pid>0:
        os.kill(pid,signal.SIGTERM) #First nicely!
        pid = Cps.Find('','Launcher')
        if pid>0:
            os.kill(pid,signal.SIGKILL) # Then not so nicely...
        Errlog.log("Killed jvm with pid %s"%pid)

if __name__ == '__main__':
    run()
    Cui.CuiExit(Cui.gpc_info,1)
