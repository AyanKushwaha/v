#!/bin/env python


"""
SKCMS-2820 Add salary articles for SOLD
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-04-5'

validfrom = int(AbsTime('01MAR2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'DK',
        'extartid':    '037A',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'CNLN_SOLD',
        'note':        'Sold day'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '037A',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'CNLN_SOLD',
        'note':        'Sold day'
    }))

    return ops


fixit.program = 'skcms-2820.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
