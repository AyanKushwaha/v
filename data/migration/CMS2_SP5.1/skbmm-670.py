#!/bin/env python


"""
SKBMM-670 Populate new column bid_leave_types.available_in_cp
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
 
    ops = []

    for entry in fixrunner.dbsearch(dc, 'bid_leave_types'):
        if entry['id'] in ('EXTRAVACATION','JOINVACATION','NOVACATION','POSTPONE','TRANSFER','VACATION'):
            entry['available_in_cp'] = True
            ops.append(fixrunner.createOp('bid_leave_types', 'U', entry))

    return ops


fixit.program = 'skbmm-670.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
