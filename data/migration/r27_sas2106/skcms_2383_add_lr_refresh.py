"""
SKCMS-2383 A2LR: Add LR REFRESH to table training_log_set.
Release: SAS2106
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-06-21'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('training_log_set', 'N', {'typ': 'LR REFRESH', 'grp': 'FLT TRAINING', 'si': 'Added in SKCMS-2383'}))

    return ops


fixit.program = 'skcms_2383_add_lr_refresh.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
