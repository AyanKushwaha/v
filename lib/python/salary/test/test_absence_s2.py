# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
import salary.api
import salary.Activity
import salary.Budgeted
import salary.Absence
import salary.type.ABSENCE

#reload(salary.api)
#reload(salary.Activity)
#reload(salary.Budgeted)
#reload(salary.Absence)
#reload(salary.type.ABSENCE)

runid = start_run(runtype='ABSENCE', extsys='S2')
release_run(runid)

