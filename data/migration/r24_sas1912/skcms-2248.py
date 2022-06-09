#!/bin/env/python

"""
SKCMS-2248 Add MAY season for cabin crew.
"""

import adhoc.fixrunner as fixrunner

__version__ = '2019-10-24'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('activity_set', 'D', {'id': 'F0', 'grp': 'CMP', 'si': 'Biddable day off, CC', 'recurrent_typ': ''}))
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'F0', 'grp': 'F4XNG', 'si': 'Biddable day off, CC', 'recurrent_typ': ''}))

    return ops


fixit.program = 'skcms-2248.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
