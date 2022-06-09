#!/bin/env python


"""
SKCMS-1378 Add salary articles for SOLD
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1'

validfrom = int(AbsTime('01MAY2017 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'DK',
        'extartid':    '0377',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SOLD_FC',
        'note':        'Sold day'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'S3',
        'extartid':    '2421',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SOLD',
        'note':        'Sold day'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '3055',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SOLD_CC',
        'note':        'Sold day'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '3050',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'SOLD_FC',
        'note':        'Sold day'
    }))

    return ops


fixit.program = 'skcms_1378.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
