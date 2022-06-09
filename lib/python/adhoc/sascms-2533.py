"""
SASCMS-2533

Creates a activity_set_period record for each activity in activity_set.
"""

import datetime
import os
import subprocess

import adhoc.fixrunner as fixrunner

__version__ = '$Revision$'

script = os.path.join(os.environ['CARMUSR'], 'bin', 'salary_batch.sh')


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, 'activity_set_period'):
        ops.append(fixrunner.createOp('activity_set_period', 'D', entry))
    for entry in fixrunner.dbsearch(dc, 'activity_set'):
        ops.append(
            fixrunner.createOp('activity_set_period', 'N', {
                'id': entry['id'],
                'validfrom': 0,
                'validto': 18261*1440,
                }
            ),
        )

    return ops
    #print ops


fixrunner.program = 'sascms-2533.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
