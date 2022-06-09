# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
import salary.api
import salary.fmt
import salary.Overtime
import salary.Budgeted
import salary.type.OVERTIME
import salary.rpt.OVERTIME
#import salary.run

reload(salary.test.common)
reload(salary.api)
reload(salary.fmt)
reload(salary.Overtime)
reload(salary.Budgeted)
reload(salary.type.OVERTIME)
reload(salary.rpt.OVERTIME)
#reload(salary.run)

runid = start_run(runtype='OVERTIME', extsys='S2')
release_run(runid)
