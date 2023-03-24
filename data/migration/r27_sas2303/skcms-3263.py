"""
SSKCMS-3263: Link: CC Instructor should get payed for each leg when instructing on ILC and LC
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-03-07_05'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = int(AbsTime('01JAN2023 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'DK',
        'extartid':    '052A',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'INST_CC_LCS_LINK',
        'note':        'Link CC LCS Instructor'
    }))
    return ops   

fixit.program = 'skcms-3263.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
