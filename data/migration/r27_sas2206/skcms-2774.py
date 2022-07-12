#!/bin/env/python

"""
SKCMS-2774 TE: Overtime Pay for checkout on day off for Link crew

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02_24_'

validfrom = int(AbsTime('01MAR2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))
intartid = 'CNLN_LAND_DAY_OFF'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'414A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': intartid,
        'note': 'Overtime Pay for checkout on day off'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'414A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': intartid,
        'note': 'Overtime Pay for checkout on day off'
    }))

    print "done"
    return ops


fixit.program = 'skcms-2774.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
