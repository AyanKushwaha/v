#!/bin/env python


"""
SKCMS-1879: Add agreement validity
Sprint: SAS72
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-08-16b'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Sep2018")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'limit_sh_to_one_before_lh', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: Max 1 SH before LH with max FDP 11h CC SKD SKCMS-1879'}))

    return ops


fixit.program = '1879_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
