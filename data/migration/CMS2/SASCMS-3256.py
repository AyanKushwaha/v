#!/bin/env python

print "********************************************"
print "*   - Running SASCMS-3256"
print "********************************************"

import datetime
import utils.dt
import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    blanks = 0
    bought = 0
    if len(fixrunner.dbsearch(dc, 'roster_attr_set', "id = 'OUTSIDEOWN'")):
        print "SASCMS-3256: It appears migration is already done"
    else:
        print "SASCMS-3256: Adding row to roster_attr_set"
        return [fixrunner.createOp('roster_attr_set', 'N', {
                'id': 'OUTSIDEOWN',
                'si': 'Outside own schedule',
            })]


fixit.program = 'sascms-3356.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
