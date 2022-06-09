"""
SKCMS-2333 A2LR: Add Q2LR to table activity_set.
Release: SAS2003
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-03-10a'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    valid_from = int(AbsTime('01Jan1986'))
    valid_to = int(AbsTime('31Dec2035'))

    ops = list()
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'Q2LR', 'grp': 'COD', 'si': 'Added in SKCMS-2333'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'Q2LR',
                                                               'validfrom': valid_from,
                                                               'validto': valid_to,
                                                               'si': 'Added in SKCMS-2333'}))

    return ops


fixit.program = 'skcms_2333_add_Q2LR_activity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()