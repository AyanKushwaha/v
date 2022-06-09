# This script needs to be started with a plan loaded, e.g. from Tracker Studio
# (the menu Special / Scripts / Python Code Manager).

from salary.test.common import start_run, release_run
from AbsTime import AbsTime
import salary.api
import salary.Activity
import salary.Schedule
import salary.type.SCHEDULE

reload(salary.test.common)
reload(salary.api)
reload(salary.Activity)
reload(salary.Schedule)
reload(salary.type.SCHEDULE)

runid = start_run(runtype='TCSCHEDULE', extsys='S3', exportformat='FLAT', firstdate=AbsTime(2019, 5, 1, 0, 0), lastdate=AbsTime(2019, 6, 1, 0, 0))
release_run(runid, exportformat='FLAT')
