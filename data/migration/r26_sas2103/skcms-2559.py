"""
SKCMS-2559: Increase number of allowed CC on ac qual AL Release/ New flights
Release: r26_2103_P
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-03-05a'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r26_sas2103/'
#directory = filepath+'/data/config/models/'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("19JAN2021")
valid_to = val_date("01JAN2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'dispensation_al_cc_new_release',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'Increase number of allowed CC on ac qual AL Release/ New flights'}))

    return ops


fixit.program = 'skcms-2559.py (%s)' % __version__
if __name__ == '__main__':
    fixit()