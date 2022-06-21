# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).
import os   
from report_sources.report_server.rs_if import argfix
from datetime import datetime as date
import salary.ec.ec_perdiem_statement_mailer.ECExportPerdiem
from salary.ec.ec_perdiem_statement_mailer.ECExportPerdiem import RunData
from AbsTime import AbsTime
from tm import TM
import salary.ec.ec_perdiem_statement_mailer.ECMailApi
import salary.ec.ec_perdiem_statement_mailer.ECfmt
import salary.ec.ECPerDiem
import salary.ec.ec_perdiem_statement_mailer.ECPerDiem
import salary.ec.ec_perdiem_statement_mailer.ECPerdiemInterface

reload(salary.ec.ec_perdiem_statement_mailer.ECMailApi)
reload(salary.ec.ec_perdiem_statement_mailer.ECfmt)
reload(salary.ec.ECPerDiem)
reload(salary.ec.ec_perdiem_statement_mailer.ECPerDiem)
reload(salary.ec.ec_perdiem_statement_mailer.ECPerdiemInterface)

regions = ['DK', 'NO', 'SE']
now = date.now()
firstdate = AbsTime(now.year - 1 if now.month == 1 or now.month == 2 else now.year, 11 if now.month == 1 else (12 if now.month == 2 else now.month - 2), 1, 0, 0)
lastdate = AbsTime(now.year, now.month, 1, 0, 0)

@argfix
def generate(*a, **k):
    print "Starting the EC Perdiem Statement Mailer Functionality...."
    for reg in regions:
        runid = start_run(runtype='ECPerDiem', extsys=reg)
        print "Created runid %s for the region %s" % (runid, reg)
    print "Completed the EC Perdiem Statement Mailer Functionality...."

def start_run(runtype, extsys='SE', exportformat='FLAT', firstdate=firstdate, lastdate=lastdate):
    print "Started_run for %s for the region %s" % (runtype,extsys)
    
    carm_system = os.path.expandvars('$CARMSYSTEMNAME')
    if carm_system in ('SASDEV', 'PROD_TEST'):
        email_allowed = False
    else:
        email_allowed = True
    print "Email allowed is %s for the environment %s" %(email_allowed, carm_system)
    
    rundata = RunData(**{'commands'    : 'start_run',
                         'admcode'     : 'N',
                         'noCheckPP'   : False,
                         'fromStudio'  : False,
                         'sendMail'    : email_allowed,
                         'lastdate'    : lastdate,
                         'starttime'   : AbsTime(now.year, now.month, now.day, 0, 0),
                         'firstdate'   : firstdate,
                         'runtype'     : runtype,
                         'monthsBack'  : 0,
                         'exportformat': exportformat,
                         'extsys'      : extsys})

    return salary.ec.ec_perdiem_statement_mailer.ECExportPerdiem.run(rundata)
