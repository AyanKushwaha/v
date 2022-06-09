#!/bin/env python


"""
SKCMS-1566 Add salary articles for SIM_INSTR_FIXED
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1'

validfrom = int(AbsTime('01JAN2017 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '3221',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SIM_INSTR_FIXED',
        'note':        'Fixed 1000 kr per sim supervision'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'S3',
        'extartid':    '5120',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SIM_INSTR_FIXED',
        'note':        'Fixed 1000 kr per sim supervision'
    }))

    return ops


fixit.program = 'skcms_1566.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
