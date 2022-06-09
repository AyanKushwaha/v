#!/bin/env python


"""
SKCMS-2068: Add validity parameter for SAS to control when jira changes go live
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-05-23'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("30Dec2035")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'resched_SB', 'validfrom': validfrom, 'validto': validto, 'si': 'Live date for changes regarding rescheduling in relation to standby.'}))

    return ops


fixit.program = 'skcms-2068.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
