#!/bin/env python


"""
SKCMS-2257
"""


import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = 'ver.20-01-22'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan1986")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_recurrent_set', 'N', {'typ': 'CRMC', 'validfrom': validfrom, 'validto': validto, 'maincat': 'C', 'acquals': '', 'aoc_sk': True, 'aoc_bu': True, 'validity': 36, 'season1_start': 0, 'season2_start': 0, 'assignment_ival': 3, 'si': 'Created in SKCMS-2257'}))
    ops.append(fixrunner.createOp('crew_recurrent_set', 'N', {'typ': 'OCRC', 'validfrom': validfrom, 'validto': validto, 'maincat': 'C', 'acquals': '', 'aoc_sk': True, 'aoc_bu': True, 'validity': 12, 'season1_start': 0, 'season2_start': 0, 'assignment_ival': 3, 'si': 'Created in SKCMS-2257'}))

    return ops


fixit.program = 'skcms-2257_crew_recurrent_set.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
