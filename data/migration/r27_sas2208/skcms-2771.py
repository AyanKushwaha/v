#!/bin/env/python

"""
SKCMS-2771 TE: Link Salary addition for flight duty hours

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-07_24_'

validfrom = int(AbsTime('01MAR2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'411A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_WEEKDAY',
        'note': 'Link Salary addition for flight duty hours'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'412A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_WEEKEND_HOLIDAY',
        'note': 'Link Salary addition for flight duty hours'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'413A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_SICK',
        'note': 'Link Salary addition for flight duty hours'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'411A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_WEEKDAY',
        'note': 'Link Salary addition for flight duty hours'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'412A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_WEEKEND_HOLIDAY',
        'note': 'Link Salary addition for flight duty hours'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'413A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_PROD_SICK',
        'note': 'Link Salary addition for flight duty hours'
    }))

    

    print "done"
    return ops


fixit.program = 'skcms-2771.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
