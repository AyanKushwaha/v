#!/bin/env python


"""
SKCMS-1968 Add agreement validity
Release: SK_1905
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-05-27'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Aug2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': '60h_rest_3_day_wops_cc', 'validfrom': validfrom, 'validto': validto, 'si': 'Start date of also counting 3 production days (previously 4)'}))

    return ops


fixit.program = '2178_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

