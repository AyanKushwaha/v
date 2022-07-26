
import os
import adhoc.fixrunner as fixrunner

__version__ = '2022_05_11_a'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):


    ops = list()
    ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'ETOPS LIFUS', 'si': '-'}))
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'ETOPS LIFUS', 'grp': 'FLT TRAINING', 'si': ''}))
    ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'ETOPS LC', 'si': '-'}))
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'ETOPS LC', 'grp': 'FLT TRAINING', 'si': ''}))
    return ops


fixit.program = 'skcms_2922_100.py (%s)' % __version__
if __name__ == '__main__':
    fixit()