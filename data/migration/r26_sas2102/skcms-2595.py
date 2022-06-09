"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-02-04a'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01FEB2021")
valid_to = val_date("01JAN2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'k20_skn_cc_co_on_freeday_comp',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'F3 compensation'}))

    return ops

fixit.program = 'skcms-2509.py (%s)' % __version__
if __name__ == '__main__':
    fixit()