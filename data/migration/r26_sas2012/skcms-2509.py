"""
SKCMS-2513: Add agreement parameter
Release: r26_2011_P
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2020-11-09a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2011/'
#directory = filepath+'/data/config/models/'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01JAN2021")
valid_to = val_date("01JAN2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'cau_co_on_freeday_comp',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'F32 compensation'}))

    return ops


fixit.program = 'skcms-2509.py (%s)' % __version__
if __name__ == '__main__':
    fixit()