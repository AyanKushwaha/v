#!/bin/env python


"""
SKCMS-2121 Add agreement validity
Release: SK_1906
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-06-24'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Sep2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'scca_co_on_freeday_comp', 'validfrom': validfrom, 'validto': validto, 'si': 'F32 compensation given from date'}))

    return ops


fixit.program = '2121_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

