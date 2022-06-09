#!/bin/env/python

"""
SKCMS-2702 Add PCA5/OPCA5 to crew document and crew recurrent set.
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-10-29'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = val_date("01Jan1986")
validto = val_date("31Dec2036")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    
    ops.append(fixrunner.createOp('crew_recurrent_set', 'N',
                                  {'typ': 'PCA5',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A5&!A3',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Added in SKCMS-2702'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'N',
                                  {'typ': 'OPCA5',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A5&!A3',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Added in SKCMS-2702'}))

    
    
    return ops


fixit.program = 'SKCMS-2702.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
