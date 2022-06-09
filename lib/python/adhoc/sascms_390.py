

"""
One time only script.

Re-run 'crew_landings' job with time interval.
"""

import adhoc.batchstudio as batchstudio
import crewlists.crewlanding as crewlanding

from AbsTime import AbsTime
from tm import TM


class conf:
    plan = "TestPlans/Tracking/sk_master_090925/sk_master_090925"
    plan_start = AbsTime(2009, 8, 1, 0, 0)
    plan_end = AbsTime(2009, 9, 30, 0, 0)
    start = AbsTime(2009, 8, 19, 0, 0)
    end = AbsTime(2009, 9, 24, 0, 0)


@batchstudio.run(plan=conf.plan, plan_start=conf.plan_start, plan_end=conf.plan_end)
def run():
    TM('crew_landing')
    TM.newState()
    crewlanding.run(conf.start, conf.end)


if __name__ == '__main__':
    run()

# eof
