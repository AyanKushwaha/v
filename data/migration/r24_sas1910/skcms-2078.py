#!/bin/env/python

"""
SKCMS-2078 Add FMST activity.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-10-11'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('activity_set', 'N',
                                  {'id': 'FMST',
                                   'grp': 'COD',
                                   'si': 'FMST A5'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N',
                                  {'id': 'FMST',
                                   'validfrom': int(AbsTime('1MAY2019')),
                                   'validto': int(AbsTime('31DEC2035'))}))
    ops.append(fixrunner.createOp('training_log_set', 'N',
                                  {'typ': 'FMST',
                                   'grp': 'FLT TRAINING',
                                   'si': 'Added in SKCMS-2078'}))

    return ops


fixit.program = 'skcms-2078.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
