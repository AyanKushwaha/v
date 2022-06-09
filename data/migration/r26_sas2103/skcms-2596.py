"""
SKCMS-2596: Add agreement validity parameter
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-02-09'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("1MAR2021")
valid_to = val_date("31DEC2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'k20_skn_cc_pln_rest_after_3d_p',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'Min 60h planned rest after 3 prod days for SKN CC'}))

    return ops


fixit.program = 'skcms-2596.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
