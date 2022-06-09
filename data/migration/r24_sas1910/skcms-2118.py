#!/bin/env python


"""
SKCMS-2118: Remove parameter to include IL4 days that replace VA in salary reports
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-06-13a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

#validfrom = val_date("01Jan2016 00:00")
#validto = val_date("31Dec2035 00:00")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_crew_activity', 'D', {'extsys': 'S3', 'intartid': 'F_ACT_IL4'}))

    return ops


fixit.program = 'skcms-2118.py (%s)' % __version__
if __name__ == '__main__':
    fixit()