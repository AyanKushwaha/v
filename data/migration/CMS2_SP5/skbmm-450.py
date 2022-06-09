#!/bin/env python


"""
SKBMM-450 Add attribute "EXTRAVAC" to table vacation_status_set
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
 
    ops = []

    if len(fixrunner.dbsearch(dc, 'vacation_status_set', "id='EXTRAVAC'")) == 0:
        ops.append(fixrunner.createOp('vacation_status_set', 'N', {'id': 'EXTRAVAC',
                                                                   'si': 'Extra Vacation'}))
    else:
        print 'vacation_status_set entry "EXTRAVAC" already exist'

    return ops


fixit.program = 'skbmm-450.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
