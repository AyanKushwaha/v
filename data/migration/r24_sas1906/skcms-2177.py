#!/bin/env python


"""
SKCMS-2177Add agreement validity
Release: SAS1905
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-05-27'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Sep2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'k19_160hrs_duty_rule', 'validfrom': validfrom, 'validto': validto, 'si': 'SKCMS-2177: 160hrs duty per month rule should be invalid'}))

    return ops


fixit.program = 'skcms-2177.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
