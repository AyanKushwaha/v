"""
SKCMS-2975: Add LC AP-POS to table training_log_set and crew_training_t_set
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-05-28'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'LC AP-POS', 'grp': 'FLT TRAINING', 'si': 'Added in SKCMS-2975'}))
    ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'LC AP-POS', 'si': 'Added in SKCMS-2975'}))

    return ops


fixit.program = 'skcms-2975.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
