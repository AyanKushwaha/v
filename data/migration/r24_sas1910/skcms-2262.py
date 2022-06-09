#!/bin/env/python

"""
SKCMS-2262 Add MAY season for cabin crew.
"""

import adhoc.fixrunner as fixrunner

__version__ = '2019-10-24'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('leave_season_set', 'N',
                                  {'id': 'C MAY',
                                   'si': 'Added in SKCMS-2262'}))

    return ops


fixit.program = 'skcms-2262.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
