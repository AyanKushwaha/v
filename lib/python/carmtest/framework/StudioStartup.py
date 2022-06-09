'''
Created on 16 feb 2010

@author: rickard
'''
import sys
from AbsTime import AbsTime
from AbsDate import AbsDate
import carmensystems.studio.webserver.WebServer as WS
import os, os.path
from socket import getfqdn
import atexit
import carmusr.FileHandlingExt
import Cui

def loadPlan(planStart, planEnd, region):
    file = os.environ.get('TEST_LP_PREFIX', 'dummy')
    schema = os.environ.get('TEST_SCHEMA', 'dummy')
    loadPlanExt(planStart, planEnd, region, file, schema)

def loadPlanExt(planStart, planEnd, region, localPlanPrefix, localPlanSchema):
    import utils.ServiceConfig as C
    
    planStart = str(AbsDate(planStart))
    planEnd = str(AbsDate(planEnd))
    
    app = (os.environ.get('SK_APP', '')).upper()

    s = C.ServiceConfig()
    
    (_, c_file) = s.getProperty('data_model/plan_path')
    (_, c_schema) = s.getProperty('db/schema')

    if not c_file or not c_schema:
        raise ValueError,"Bad config plan_path or schema not set"
    
    lp_path = os.path.join(localPlanPrefix, localPlanSchema)
    sp_path = os.path.join(localPlanPrefix, localPlanSchema, localPlanSchema)
    plan_path = os.path.join(os.environ.get('CARMDATA', ''), 'LOCAL_PLAN')
    c_file = os.path.join(plan_path, c_file)
    
    if not os.path.exists(os.path.join(plan_path, lp_path)) or \
           not os.path.exists(os.path.join(plan_path, sp_path)):
        print 'Reverting to configured plan, could not find path "%s" or "%s"' % (lp_path, sp_path)
        lp_path = os.path.join(c_file, c_schema)
        sp_path = os.path.join(c_file, c_schema, c_schema)
 
    
    start_mon = planStart[-7:-4]
    end_mon = planEnd[-7:-4]
    start_year = planStart[-4:]
    end_year = planEnd[-4:]
    if not region: region = "ALL"
    
    bypass = None
    if app == 'PLANNING':
        if region == "SKD":
            region = "FD_SKD_M8"
        elif region == "SKS":
            region = "FD_SKS_B737"
        elif region == "SKN":
            region = "FD_SKN_B737"
        bypass = {"FORM":"OPEN_PLAN",
                     "PERIOD_START_FIELD":planStart,
                     "PERIOD_END_FIELD":planEnd,
                     'PLANNING_AREA_FIELD':region,
                     'PRODUCT_FIELD': 'Rostering',
                     'PARAM_SET_FIELD': 'NONE',
                     'OK': ''}
    elif app == 'TRACKING':
        
        bypass = {'FORM': 'Load_filter_diag',
                     'START_MONTH': start_mon,
                     'START_YEAR': start_year,
                     'END_MONTH': end_mon,
                     'END_YEAR': end_year,
                     'PLANNINGAREA': region}
    else:
        raise 'Unknown app set in SK_APP'
    
    print "Will load plan", lp_path, "subplan", sp_path
    Cui.CuiOpenSubPlan(bypass, Cui.gpc_info, lp_path, sp_path)

def rpc_mode(doLoadPlan, planStart, planEnd, region):
    port = str(WS.get_port_number(6700))
    if doLoadPlan.isdigit():
        doLoadPlan = int(doLoadPlan)
    elif doLoadPlan.lower() == 'false':
        doLoadPlan = False
    host = getfqdn()
    pid = os.getpid()
    fileName = os.path.expandvars("$CARMTMP/run/rpc.%s.%s" % (host, port))
    print "Creating %s" % fileName
    if os.path.islink(fileName) or os.path.exists(fileName): os.unlink(fileName)
    app = (os.environ.get('SK_APP', '')).upper()
    tgt = ';'.join(map(str, [host, pid, app, planStart, planEnd, region]))
    os.symlink(tgt, fileName)
    def delete_file():
        try:
            os.unlink(fileName)
        except:
            pass
    atexit.register(delete_file)
    if doLoadPlan:
        loadPlan(planStart, planEnd, region)

def run_tests(doLoadPlan, planStart, planEnd, region, *cmdline):
    if doLoadPlan:
        loadPlan(planStart, planEnd, region)
    import carmtest.framework.TestFunctions as TF
    return TF.run_cmdline(cmdline)

if sys.argv[1] == 'rpc_mode':
    rpc_mode(*tuple(sys.argv[2:]))
elif sys.argv[1] == 'load_and_run_tests':
    ret = run_tests(True, *tuple(sys.argv[2:])) or 0
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT | (ret and Cui.CUI_EXIT_ERROR))
elif sys.argv[1] == 'run_tests':
    ret = run_tests(False, None, None, None, *tuple(sys.argv[2:])) or 0
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT | (ret and Cui.CUI_EXIT_ERROR))
