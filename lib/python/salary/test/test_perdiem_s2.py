# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
import salary.api
import salary.fmt
import salary.Budgeted
import salary.PerDiem
import salary.type.PERDIEM
import salary.rpt.PERDIEM
#import salary.run

reload(salary.api)
reload(salary.fmt)
reload(salary.Budgeted)
reload(salary.PerDiem)
reload(salary.type.PERDIEM)
reload(salary.rpt.PERDIEM)
#reload(salary.run)

runid = start_run(runtype='PERDIEM', extsys='S2')
release_run(runid)
