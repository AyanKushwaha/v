#!/bin/env/python

"""
SKCMS-2237 Update PC/OPC filters in crew recurrent set.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-03-11'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = val_date("01Jan1986")
validto = val_date("31Dec2036")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_recurrent_set', 'U',
                                  {'typ': 'PC',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': '38|A2',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Updated in SKCMS-2327'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'U',
                                  {'typ': 'OPC',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': '38|A2',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Updated in SKCMS-2327'}))

    return ops


fixit.program = 'skcms-2327.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
