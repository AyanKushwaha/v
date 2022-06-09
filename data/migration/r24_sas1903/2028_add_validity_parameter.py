#!/bin/env python


"""
SKCMS-2028: Add agreement validity
Sprint: SAS78
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-03-01'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01May2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'additional_briefing_skn_skd_cc', 'validfrom': validfrom, 'validto': validto, 'si': 'SKN and SKD additional briefing time'}))

    return ops


fixit.program = '2028_add_validity_parameter.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
