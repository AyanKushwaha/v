"""
SKCMS-2516 Latest checkout before long hauld
Release: r26_2012_P
"""
import os
import adhoc.fixrunner as fixrunner

from AbsDate import AbsDate
import AbsTime

__version__ = '2020-11-23a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2012/'
#directory = filepath+'/data/config/models/'

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2021")
validto = val_date("01Jan2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):


    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'K20_cau_co_before_LH', 'validfrom': validfrom, 'validto': validto, 'si': 'New rule for latest checkout before longhaul valid from 01Jan2021'}))
    return ops


fixit.program = 'skcms_2516.py (%s)' % __version__
if __name__ == '__main__':
    fixit()