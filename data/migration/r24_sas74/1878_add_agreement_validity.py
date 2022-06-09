#!/bin/env python


"""
SKCMS-1878: Add agreement validity
Sprint: SAS74
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-10-10a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'max_lh_per_month_pt_skd_cc', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: Max nr of LH trips per month for part time crew CC SKD SKCMS-1878'}))

    return ops


fixit.program = '1878_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
