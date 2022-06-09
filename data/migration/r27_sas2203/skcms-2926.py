"""
SKCMS-2926
Release: r27_2203_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = '2022-03-15'


filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/r27_sas2203/'
#directory = filepath+'/data/config/models/'



def val_date(date_str):
    return int(AbsTime(date_str))/24/60


valid_from = val_date("01Feb2022")
valid_to = val_date("30Dec2030")


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    ops.append(fixrunner.createOp('annotation_set', 'N', {'code': 'CM',
                                                              'descript':'Crew Meal Opt Out',
                                                              'forcrew':True,
                                                              'incct':True,
                                                              'inccr':False,
                                                              'hasprop':False,
                                                              'isvisible':True,
                                                              'validfrom': valid_from ,
                                                              'validto': valid_to,
                                                              }))
                                                  


    return ops



fixit.program = 'skcms-2926.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
 









