import os

#import salary.Overtime as O
#import Cui
#import carmensystems.rave.api as R

#print "START LOG"

def d(v):
    if not v: return 0
    return int(v)

def runFromStudio():
    import salary.Overtime as O
    import Cui
    import carmensystems.rave.api as R
    from AbsTime import AbsTime
    print "LOAD PLAN"
    bypass = {'FORM': 'Load_filter_diag',
                     'START_MONTH': 'MAY',
                     'START_YEAR': '2010',
                     'END_MONTH': 'JUN',
                     'END_YEAR': '2010',
                     'PLANNINGAREA': 'ALL'}
    
    c_schema='cms_production'
    c_file = "Database/Production"
    lp_path = os.path.join(c_file, c_schema)
    sp_path = os.path.join(c_file, c_schema, c_schema)
    Cui.CuiOpenSubPlan(bypass, Cui.gpc_info, lp_path, sp_path)
    for stam,endm in [("1May2010","1Jun2010"),("1Jun2010","1Jul2010")]:
       print "START %s - %s" % (stam, endm)
       R.param("salary.salary_month_start_p").setvalue(AbsTime(stam))
       R.param("salary.salary_month_end_p").setvalue(AbsTime(endm))
       Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0,Cui.CrewMode,Cui.CuiShowAll)
       Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0,'WINDOW')
       outfile = file("/users/carmadm/jira2218/out_%s.csv" % stam,"w")
       CD = {}
       CP = {}
       CINF = {}
       o = O.OvertimeManager('default_context')
       R.param("parameters.HACKY_ENABLED").setvalue(True)
       otr = o.getOvertimeRosters()
       print "# of rosters:",len(otr)
       for r in otr:
          if "F" in r.rank and not r.isSKN:
             rgn = r.isSKS and "SKS" or (r.isSKN and "SKN" or "SKD")
             CD[r.crewId] = d(r.getCalendarWeek()) + d(r.get7x24())
             CINF[r.crewId] =  (r.crewId, r.empNo, rgn, r.rank)

       R.param("parameters.HACKY_ENABLED").setvalue(False)
       for r in o.getOvertimeRosters():
          if "F" in r.rank and not r.isSKN:
             rgn = r.isSKS and "SKS" or (r.isSKN and "SKN" or "SKD")
             CP[r.crewId] = d(r.getCalendarWeek()) + d(r.get7x24())

       for crewId in CD:
          if CD[crewId] != CP[crewId]:
             st = "%s; %s; %s; %s; " % CINF[crewId]
             cc = 1/60.0
             st += "%.2f; %.2f; %.2f" % (cc*(CD[crewId]), (cc*CP[crewId]), (cc*(CD[crewId]-CP[crewId])))
             print st
             print >> outfile, st

       print "END LOG"
    outfile.close()
    Cui.CuiExit(Cui.gpc_info,1)

def startStudio():
    CARMUSR = os.path.realpath(os.path.dirname(__file__) + "../../../..")
    startStudioCmd = r'%s/bin/startStudio.sh -S t -p "PythonRunFile(\"adhoc/sascms-2218.py\")"' % (CARMUSR)
    print startStudioCmd
    os.system(startStudioCmd)
    
try:
    import Cui
    try:
        runFromStudio()
    except:
        traceback.print_exc()
        sys.exit(0)
except:
    startStudio()
    
