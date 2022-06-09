# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
import salary.api
import salary.Activity
import salary.Budgeted
import salary.type.BUDGETED

#reload(salary.test.common)
#reload(salary.api)
#reload(salary.Activity)
#reload(salary.Budgeted)
#reload(salary.type.BUDGETED)

runid = start_run(runtype='BUDGETED', extsys='S3')
release_run(runid)

