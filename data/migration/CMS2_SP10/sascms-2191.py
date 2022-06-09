"""
* Add entry to crew_restriction_set: 'NEW+REFR'
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []
    ops.append(fixrunner.createOp('crew_restriction_set', 'N', {
            'typ': 'NEW',
            'subtype':'REFR',
            'descshort':'000',
            'desclong': 'Refresher restriction during LC',
        })),

    return ops

fixit.program = 'sascms-2191.py (%s)' % __version__

if __name__ == '__main__':
    try:
    	fixit()
    except ValueError, err:
        print err
