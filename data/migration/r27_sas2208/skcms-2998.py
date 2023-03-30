"""
SKCMS-2998: Link CC SCC course set up
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-07-26'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'LINE FLIGHT SCC', 'grp': 'FLT TRAINING', 'si': 'Added in SKCMS-2998'}))

    ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'LINE FLIGHT SCC', 'si': 'Added in SKCMS-2998'}))

    return ops

fixit.program = 'skcms-2998.py (%s)' % __version__
if __name__ == '__main__':
    fixit()