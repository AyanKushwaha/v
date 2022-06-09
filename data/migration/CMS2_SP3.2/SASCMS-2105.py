#!/bin/env python

print "***********************************************"
print "*   - Running SASCMS-2105"
print "*     Adding roster attribute 'PRIVATELYTRADED'"
print "*     to the roster_attr_set table. "
print "***********************************************"

import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.run
def fixit(dc,*a, **k):
    ops = []
    ops.append(fixrunner.createOp('roster_attr_set', 'N', {
                            'id': 'PRIVATELYTRADED',
                            'si': 'Privately Traded Day'
                    }))
    return ops


fixit.program = 'SASCMS-2105.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
