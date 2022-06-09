#!/bin/env python

"""
SKCMS-398 Move the end dates ahead one day for entries in the new hires table to
match modified rave rules.
"""

import adhoc.fixrunner as fixrunner
import os

__version__ = '1'

ONE_DAY = 1440

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **kw):
    ops = []
    for row in fixrunner.dbsearch(dc, 'new_hire_follow_up'):
        row['follow_up_1_end_date'] += ONE_DAY
        row['follow_up_2_end_date'] += ONE_DAY
        row['follow_up_3_end_date'] += ONE_DAY

        ops.append(fixrunner.createop('new_hire_follow_up', 'U', row))
    
    return ops


fixit.program = 'sascms-398.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
