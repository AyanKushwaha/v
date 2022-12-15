"""
SKCMS-3137: Changed instructor pay at A2NX ETOPS flights
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-12-06'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = int(AbsTime('01MAR2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '3255',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'INST_ETOPS_LIFUS_ACT',
        'note':        ''
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '3283',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'INST_ETOPS_LC_ACT',
        'note':        ''
    }))
    return ops   

fixit.program = 'skcms-3137.py (%s)' % __version__

if __name__ == '__main__':
    fixit()