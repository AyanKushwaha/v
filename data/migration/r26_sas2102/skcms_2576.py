
"""
SKCMS-2576 Add new instructor qual SEN-EX
Release: r26_2102_P
"""

import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-01-22a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2102/'
#directory = filepath+'/data/config/models/'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('crew_qual_acqual_set', 'N', {'typ':'INSTRUCTOR', 'subtype':'SEN-EX', 'descshort': 'SEN-EX', 'desclong': 'SEN-EX', 'si': 'Added in SKCMS-2576'}))
    return ops

fixit.program = 'skcms_2576.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

