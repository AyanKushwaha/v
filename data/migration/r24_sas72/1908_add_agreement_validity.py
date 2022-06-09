#!/bin/env python


"""
SKCMS-1908: Add agreement validity
Sprint: SAS72
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-09_17b'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'f36_entitlemnts_skn_cc_inshape', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: F36 entitlemnts shall be zero for all SKN CC'}))

    return ops


fixit.program = '1908_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
