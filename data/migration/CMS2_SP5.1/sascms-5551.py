"""
* Add entry to account set
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate
from AbsTime import AbsTime

__version__ = '1'
 
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = [
        fixrunner.createOp('account_set', 'N', {
        'id': 'BOUGHT_COMP_F3S',
        'si': 'Bought 0% +F3S',
        }),
        ]

    return ops


fixit.program = 'sascms-5551.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
