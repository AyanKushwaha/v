#!/bin/env python


"""
SKCMS-2135: Remove agreement validity
Sprint: SK_1906
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-06-17a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'D', {'id': 'max_lh_per_month_pt_skn_cc', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: Max 1 LH trip per month for 60% part time crew CC SKN'}))

    return ops


fixit.program = 'skcms-2135.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
