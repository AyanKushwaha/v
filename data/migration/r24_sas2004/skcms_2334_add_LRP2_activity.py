"""
SKCMS-2334 A2LR: Add LRP2 to table activity_set.
Release: SAS2004
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-03-23a'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    valid_from = int(AbsTime('01Jan1986'))
    valid_to = int(AbsTime('31Dec2035'))

    ops = list()
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'LRP2', 'grp': 'COD', 'si': 'Added in SKCMS-2334'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'LRP2',
                                                               'validfrom': valid_from,
                                                               'validto': valid_to,
                                                               'si': 'Added in SKCMS-2334'}))

    return ops


fixit.program = 'skcms_2334_add_LRP2_activity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
