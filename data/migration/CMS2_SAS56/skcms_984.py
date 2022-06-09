#!/bin/env python


"""
SKCMS-984 Add bid group CC RP to bid_periods_group_set
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1'

validfrom = int(AbsTime('01JAN2017 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('bid_periods_group_set', 'N', {
        'bid_group':      'CC RP'
    }))

    return ops


fixit.program = 'skcms_984.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
