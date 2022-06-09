#!/bin/env python


"""
SKCMS-1830 Changes to MEAL Order update
Sprint: SAS65
"""


import adhoc.fixrunner as fixrunner
import time
from AbsTime import AbsTime
from RelTime import RelTime
from AbsDate import AbsDate

__version__ = '2018-04-25a'

validfromOrig = int(AbsTime('15May2012 00:00'))
validfrom = int(AbsTime(str(time.strftime("%d%b%Y", time.localtime(time.time()))+' 00:00')))
validto = int(AbsTime('31Dec2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('property', 'U', {'id': 'meal_order_update_offset', 'validfrom': validfromOrig, 'validto': validfrom}))
    ops.append(fixrunner.createOp('property', 'N', {'id': 'meal_order_update_offset', 'validfrom': validfrom, 'validto': validto, 'value_rel': int(RelTime('0:15'))}))

    return ops


fixit.program = 'update_meal_order_update_offsets.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
