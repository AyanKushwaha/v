"""
SKCMS-2613: Update course_type table
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
    for entry in fixrunner.dbsearch(dc, 'course_type', "id='ETOPS A2LR'"):
        ops.append(fixrunner.createop('course_type', 'D', entry))
        

    return ops


fixit.program = 'skcms_2613a.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
