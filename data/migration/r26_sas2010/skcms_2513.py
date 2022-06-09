"""
SKCMS-2513: Add qualification for POSITION+AHP
Release: r26_2010_P
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-10-08a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2010/'
#directory = filepath+'/data/config/models/'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('crew_qualification_set', 'N', {'typ': 'POSITION', 'subtype': 'AHP', 'si': None, 'descshort': 'AHP', 'desclong': 'AP downgraded to AH'}))

    return ops


fixit.program = 'skcms_2513.py (%s)' % __version__
if __name__ == '__main__':
    fixit()