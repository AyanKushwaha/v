"""
SKCMS-2613: Update aircraft_type table
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
    for entry in fixrunner.dbsearch(dc, 'aircraft_type', "(id='321')"):
       ops.append(fixrunner.createop('aircraft_type', 'U',
           {'id': '321',
           'version': 'NX',
           'maintype': 'A320',
           'crewbunkfc': 0,
           'crewbunkcc': 0,
           'maxfc': 4,
           'maxcc': 6,
           'class1fc': 0,
           'class2cc': 0,
           'class3cc': 0,
           'si': 'Added in SKCMS-2613'}))



    return ops


fixit.program = 'skcms_2613c.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
