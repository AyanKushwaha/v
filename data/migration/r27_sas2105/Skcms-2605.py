"""
SKCMS-2605
Release: r27_2105_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-05-13'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2105/'
#directory = filepath+'/data/config/models/'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Feb2021")
valid_to = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'K20_skn_cc_meal_stop',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': ''}))
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'K20_sks_cc_meal_stop',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': ''}))  
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'K20_skd_cc_meal_stop',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': ''}))                                                

    return ops


fixit.program = 'Skcms-2605.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
