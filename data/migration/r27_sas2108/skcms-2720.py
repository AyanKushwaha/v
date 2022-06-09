"""
SKCMS-2720
Release: r27_2108_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = '2021-08-01'


filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2108/'
#directory = filepath+'/data/config/models/'



def val_date(date_str):
    return int(AbsTime(date_str))/24/60


valid_from = val_date("01Aug2021")
valid_to = val_date("31Dec2035")


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': '2_landings_every_45_days',
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              'si': 'SKCMS-2720 JCRT MFF: Changed recency requirements'}))
                                                  


    return ops



fixit.program = 'skcms-2720.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
 









