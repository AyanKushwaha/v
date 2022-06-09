#!/bin/env/python

"""
SKCMS-2083 Add PC/OPCA3A5 to crew document and crew recurrent set.
Sprint: 1904
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-05-16'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = val_date("01Jan1986")
validto = val_date("31Dec2036")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('crew_document_set', 'N',
                                  {'typ': 'REC',
                                   'subtype': 'PCA3A5',
                                   'si': 'Added in SKCMS-2083'}))

    ops.append(fixrunner.createOp('crew_document_set', 'N',
                                  {'typ': 'REC',
                                   'subtype': 'OPCA3A5',
                                   'si': 'Added in SKCMS-2083'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'N',
                                  {'typ': 'PCA3A5',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A3&A5',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Added in SKCMS-2083'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'N',
                                  {'typ': 'OPCA3A5',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A3&A5',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Added in SKCMS-2083'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'U',
                                  {'typ': 'PCA3',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A3&!A5',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Updated in SKCMS-2083'}))

    ops.append(fixrunner.createOp('crew_recurrent_set', 'U',
                                  {'typ': 'OPCA3',
                                   'validfrom': validfrom,
                                   'validto': validto,
                                   'maincat': 'F',
                                   'acquals': 'A3&!A5',
                                   'aoc_sk': True,
                                   'aoc_bu': True,
                                   'validity': 12,
                                   'season1_start': 1,
                                   'season2_start': 7,
                                   'assignment_ival': 3,
                                   'si': 'Updated in SKCMS-2083'}))

    ops.append(fixrunner.createOp('activity_set', 'U',
                                  {'id': 'S5',
                                   'grp': 'OPC',
                                   'si': 'OTS A5 (former OPC)'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N',
                                  {'id': 'S5',
                                   'validfrom': int(AbsTime('1MAY2019')),
                                   'validto': int(AbsTime('31DEC2035'))}))
    ops.append(fixrunner.createOp('activity_set', 'N',
                                  {'id': 'Y5',
                                   'grp': 'PC',
                                   'si': 'OPC (PC) A5'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N',
                                  {'id': 'Y5',
                                   'validfrom': int(AbsTime('1MAY2019')),
                                   'validto': int(AbsTime('31DEC2035'))}))

    return ops


fixit.program = 'skcms-2083.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
