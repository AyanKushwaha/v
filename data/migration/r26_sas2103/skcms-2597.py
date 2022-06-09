"""
SKCMS-2597: Add agreement parameter
Release: r26_2102_P
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-02-16a'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01MAY2021")
valid_to = val_date("01JAN2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'k20_skn_cc_weekend_is_3day',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'SKN CC weekend is Fri 00:00 - Sun 24:00 or Sat 00:00 - Mon 24:00'}))
    return ops


fixit.program = '%s (%s)' % (os.path.basename(__file__), __version__)
if __name__ == '__main__':
    fixit()
