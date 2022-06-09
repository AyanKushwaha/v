"""
SASCMS-5437
* Add entry to roster_attr_set: 'CANCELLEDFLIGHT'
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    
    ops = [
        fixrunner.createOp('roster_attr_set', 'N', {
            'id': 'CANCELLEDFLIGHT',
            'si': 'Cancelled flight',
        }),
    ]

    return ops


fixit.program = 'sascms-5437.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

    
