import salary.run
from salary.run import RunData
from AbsTime import AbsTime
from tm import TM

def start_run(runtype, extsys='SE', exportformat='FLAT', firstdate=AbsTime(2018, 5, 1, 0, 0), lastdate=AbsTime(2018, 7, 1, 0, 0)):
    print "start_run for %s" % runtype
    rundata = RunData(**{'commands'    : 'start_run',
                         'admcode'     : 'N',
                         'noCheckPP'   : False,
                         'fromStudio'  : True,
                         'spooldir'    : '/home/oscargr/Projects/sk_cms_user.hg/current_carmdata/REPORTS/SALARY_EXPORT',
                         'lastdate'    : lastdate,
                         'starttime'   : AbsTime(2019, 6, 25, 0, 0),
                         'firstdate'   : firstdate,
                         'runtype'     : runtype,
                         'monthsBack'  : 0,
                         'exportformat': exportformat,
                         'extsys'      : extsys})

    return salary.run.run(rundata)

def release_run(runid, exportformat='FLAT'):
    print "release_run for %d" % runid
    runiddata = TM.salary_run_id[runid,]
    rundata = RunData(**{'commands'   : 'release_run',
                         'runid'      : runiddata.runid,
                         'runtype'    : runiddata.runtype,
                         'monthsBack' : 0,
                         'exportformat': exportformat,
                         'extsys'     : runiddata.extsys})

    salary.run.release(rundata)

def start_export(runid):
    print "start_export for %d" % runid
    runiddata = TM.salary_run_id[runid,]
    rundata = RunData(**{'commands'   : 'start_export',
                         'runid'      : runiddata.runid,
                         'runtype'    : runiddata.runtype,
                         'monthsBack' : 0,
                         'extsys'     : runiddata.extsys})

    salary.run.release(rundata)
