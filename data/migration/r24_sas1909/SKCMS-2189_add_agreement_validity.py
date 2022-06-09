#!/bin/env python


"""
SKCMS-2189: Add agreement validity
Sprint: 
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-09-01'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Nov2020")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': '3_pilots_MIA', 'validfrom': validfrom, 'validto': validto, 'si': 'K19: remove MIA from set two_pilot_destinations_set SKCMS-2189'}))

    return ops


fixit.program = '2189_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
