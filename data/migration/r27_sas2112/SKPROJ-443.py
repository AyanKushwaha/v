"""
SKPROJ-443
Release: r27_2112_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2021-12-07'

filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2112/'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Feb2021")
valid_to = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('salary_article', 'N', 
                                    {'extsys': 'NO',
                                    'extartid': '3234',
                                    'validfrom': valid_from,
                                    'validto': valid_to,
                                    'intartid': 'PUBL_HOLIDAY_COMP',
                                    'note': "Norway's public holiday compensation for CC"}))
                                   

    return ops


fixit.program = 'SKPROJ-443.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
