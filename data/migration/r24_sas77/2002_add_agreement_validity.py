#!/bin/env python


"""
SKCMS-2002: Add agreement validity
Sprint: SAS76
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-11-22a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'f36_entitlemnts_skd_cc_inshape', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: SKD CC - change entitlement to F36'}))

    return ops


fixit.program = '2002_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
