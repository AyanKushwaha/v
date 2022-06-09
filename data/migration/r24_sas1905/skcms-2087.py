#!/bin/env/python

"""
SKCMS-2087 Cabin crew training for A350
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-05-16'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('activity_set_period', 'N',
                                  {'id': 'TW99',
                                   'validfrom': int(AbsTime('1MAY2019')),
                                   'validto': int(AbsTime('31DEC2035'))}))
    return ops


fixit.program = 'skcms-2087.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
