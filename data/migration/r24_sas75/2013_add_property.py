#!/bin/env python


"""
SKCMS-2013: JCRT: FTL Max 2000 duty hours per calendar year
Sprint: SAS75
"""


import adhoc.fixrunner as fixrunner
import time
from AbsTime import AbsTime
from RelTime import RelTime

__version__ = '2018-11-14-d'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('property', 'N',
                                  {'id': 'oma16_duty_time_in_calendar_year_buffer', 
                                   'validfrom': int(AbsTime('01Jan2018 0:00')), 
				   'validto': int(AbsTime('31Dec2035 0:00')),
                                   'value_rel': int(RelTime('5:00')),
				   'si': 'Max duty time per calendar year early warning'
                                   }))

    return ops


fixit.program = '2013_add_property.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
