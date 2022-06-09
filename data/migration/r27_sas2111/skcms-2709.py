"""
SKCMS-2709
Release: r27_2111_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-11-10'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2111/'
#directory = filepath+'/data/config/models/'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Jan2022")
valid_to = val_date("31Dec2035")

@fixrunner.\
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'additional_CX6_rec_trng',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': ''}))
                                   

    return ops


fixit.program = 'Skcms-2709.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
