"""
SKCMS-2457 A2LR: Add LRSB to table activity_set.
Release: SAS2006
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-05-25a'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    valid_from = int(AbsTime('01Jan1986'))
    valid_to = int(AbsTime('31Dec2035'))

    ops = list()
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'LRSB', 'grp': 'COD', 'si': 'Added in SKCMS-2457'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'LRSB',
                                                               'validfrom': valid_from,
                                                               'validto': valid_to,
                                                               'si': 'Added in SKCMS-2457'}))

    return ops


fixit.program = 'skcms_2457_add_lrsb_code.py (%s)' % __version__
if __name__ == '__main__':
    fixit()