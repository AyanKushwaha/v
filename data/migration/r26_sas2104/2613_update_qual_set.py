"""
SKCMS-2613: Update crew_qualification_set table
Release: r26_2104_P
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-04-17'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2104/'
#directory = filepath+'/data/config/models/'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    for entry in fixrunner.dbsearch(dc, 'crew_qualification_set', "(typ='POSITION') AND (subtype='A2LR')"):
       ops.append(fixrunner.createop('crew_qualification_set', 'D', entry))
       ops.append(fixrunner.createop('crew_qualification_set', 'N',
           {'typ': 'POSITION',
           'subtype': 'A2NX',
           'si': 'Added in SKCMS-2613'}))



    return ops


fixit.program = 'skcms_2613b.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
