import sys
import traceback
import os
import time

def setSGEcontext(var, val):
    cmd = 'qalter $JOB_ID -ac %s="%s" > /dev/null || true' % (var,val)
    os.system(cmd)
    
def loadPlan(c_schema, planStart, planEnd, region):
    import carmensystems.common.ServiceConfig as C
    import Cui
    from AbsDate import AbsDate
    
    planStart = str(AbsDate("01"+planStart))
    planEnd = str(AbsDate("01"+planEnd))
    
    app = (os.environ.get('SK_APP', '')).upper()

    s = C.ServiceConfig()
    
    (_, c_file) = s.getProperty('file_prefix')
    if not c_schema:
        (_, c_schema) = s.getProperty('db/user')
    else:
        print "NOTE: How do I change Oracle login programmatically ????"

    
    plan_path = os.path.join(os.environ.get('CARMDATA', ''), 'LOCAL_PLAN')
    
    lp_path = os.path.join(c_file, c_schema)
    sp_path = os.path.join(c_file, c_schema, c_schema)
    if not os.path.exists(os.path.join(plan_path, lp_path)) or \
           not os.path.exists(os.path.join(plan_path, sp_path)):
        raise Exception,'Schema %s does not seem to exist' % c_schema
 
    
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
        raise Exception,'Unknown app set in SK_APP'
    
    print "Will load plan", lp_path, "subplan", sp_path
    Cui.CuiOpenSubPlan(bypass, Cui.gpc_info, lp_path, sp_path)
    
def runTests(testspec):
    import carmtest.framework.TestFunctions as TF
    setSGEcontext("tws_status","BUSY")
    setSGEcontext("studio_teststart",str(int(time.time())))
    try:
        if isinstance(testspec, str):
            testspec = testspec.split(',')
        setSGEcontext("studio_testsspec",",".join(testspec))
        return TF.run(testspec)
    finally:
        setSGEcontext("tws_status","IDLE")
    
def hasPrereqs(prereqList):
    if isinstance(prereqList, str):
        prereqList = prereqList.split(',')
    from carmtest.framework.Case import TestFixture
    for t in prereqList:
        if hasattr(TestFixture, 'is'+t):
            if not getattr(TestFixture, 'is'+t)(t):
                return False
    return True

def startRPCserver(portbase=6700):
    import carmensystems.studio.webserver.WebServer as WS
    import carmensystems.studio.webserver.XMLRPCDispatcher as XD
    from socket import getfqdn
    import carmensystems.studio.private.RaveServer as RaveServer
    port = str(WS.get_port_number(portbase))
    host = getfqdn()
    setSGEcontext("tws_rpc_uri", "http://%s:%s" % (host, port))
    for func in [hasPrereqs, runTests]:
        XD.xmlrpc_registerfunction(func, 'TestFramework.' + func.__name__)
    
def shareEnv():
    if 'DISPLAY' in os.environ and os.environ['DISPLAY'] != "NONE":
        setSGEcontext("tws_xdisplay", os.environ['DISPLAY'])
        
def initStudio():
    setSGEcontext("tws_status","LOAD_PLAN")
    setSGEcontext("tws_params","%s %s %s %s" % (sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[2]))
    shareEnv()
    startRPCserver()
    loadPlan(sys.argv[2], sys.argv[4], sys.argv[5], sys.argv[3])
    setSGEcontext("tws_status","IDLE")
    setSGEcontext("tws_last_refresh",str(int(time.time())))
    
def initReportWorker():
    cb = os.environ.get("CALLBACK_URI","http://localhost:80")
    cbhost = cb.split('/')[-1].split(':')[0]
    setSGEcontext("tws_status","LOAD_PLAN")
    process = sys.argv[2]
    ruleset = sys.argv[3]
    paramfile = sys.argv[4]
    logfile = sys.argv[5]
    rpc_uri = "%s/api/cms/portal/RPC2" % cb
    setSGEcontext("tws_params","%s %s" % (process, rpc_uri))
    setSGEcontext("tws_logfile",logfile)
    shareEnv()
    startRPCserver(6650)
    from carmensystems.studio.Tracking.reportWorkerStudio import ModelSyncerStudio
    ModelSyncerStudio(rpc_uri,
                      ruleset,
                      paramfile,
                      process,
                      cbhost,
                      logfile)
    setSGEcontext("tws_status","IDLE")
    
if __name__ == '__main__':
    if os.environ.get("_RpcInit",""):
        print >>sys.stderr, "I have been run twice!", sys.argv
    else:
        setSGEcontext("tws_pid",str(os.getpid()))
        os.environ["_RpcInit"] = "1"
        if len(sys.argv) < 2:
            print "No command specified"
            sys.exit(1)
        if sys.argv[1] == "init":
            try:
                initStudio()
            except:
                traceback.print_exc()
                sys.exit(1)
        if sys.argv[1] == "initrw":
            try:
                initReportWorker()
            except:
                traceback.print_exc()
                sys.exit(1)
        else:
            print "Bad command:", sys.argv[1]
            print sys.argv
            #sys.exit(1)
        print sys.argv
