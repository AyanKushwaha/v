#!/bin/env python


"""
SKCMS-1977: Add agreement validity and BOUGHT_F3 accounts
Sprint: SAS74
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-11-01b'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N',
                                  {'id': 'f3_compensation_skd_cc', 'validfrom': validfrom, 'validto': validto,
                                   'si': 'InShape: F3 compensation for SKD CC'}))
    ops.append(fixrunner.createOp('account_set', 'N',
                                  {'id': 'BOUGHT_F3','si': 'InShape: Bought F3'}))
    ops.append(fixrunner.createOp('account_set', 'N',
                                  {'id': 'BOUGHT_F3_2', 'si': 'InShape: Bought F3, 2 days comp'}))

    return ops


fixit.program = '1911_FX_Compensation.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
