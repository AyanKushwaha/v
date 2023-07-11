#!/bin/env/python

"""
SKCMS-2773 TE: Overtime pay for Link crew
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-07_11_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'OTS CHANGE', 'grp': 'SIM REC', 'si': 'Added in SKCMS-3372'}))
    
    print "done"
    return ops


fixit.program = 'skcms_3372.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
