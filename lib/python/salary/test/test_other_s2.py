# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
import salary.api
import salary.fmt
import salary.Overtime
import salary.Budgeted
import salary.type.OTHER
import salary.rpt.OTHER
#import salary.run

reload(salary.api)
reload(salary.fmt)
reload(salary.Overtime)
reload(salary.Budgeted)
reload(salary.type.OTHER)
reload(salary.rpt.OTHER)
#reload(salary.run)

runid = start_run(runtype='OTHER', extsys='S2')
release_run(runid)
