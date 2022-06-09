"""
SKCMS-2821
Release: r27_2112_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = '2021-12-15'


filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2112/'
#directory = filepath+'/data/config/models/'



def val_date(date_str):
    return int(AbsTime(date_str))/24/60


valid_from = val_date("01Dec2021")
valid_to = val_date("31Dec2035")


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'oma16_weekly_rest_RL',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': ''}))
                                                  


    return ops



fixit.program = 'skcms-2821.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
 









