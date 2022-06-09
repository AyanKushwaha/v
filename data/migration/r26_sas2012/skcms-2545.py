"""
SKCMS-2545 Introduce training attribute ETOPS LIFUS/LC
Release: r26_2012_P
"""
import os
import adhoc.fixrunner as fixrunner

from AbsDate import AbsDate
import AbsTime

__version__ = '2020-11-23a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2012/'
#directory = filepath+'/data/config/models/'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):


    ops = list()
    ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'ETOPS LIFUS/LC', 'si': '-'}))
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'ETOPS LIFUS/LC', 'grp': 'FLT TRAINING', 'si': ''}))
    return ops


fixit.program = 'skcms_2545.py (%s)' % __version__
if __name__ == '__main__':
    fixit()