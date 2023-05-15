#!/bin/env/python

"""
SKCMS-2773 TE: Overtime pay for Link crew
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-05_15_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'SE',
        'extartid':'5025',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'ABS_PR_LOA_D',
        'note': 'PR Days for SE'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'S3',
        'extartid':'5025',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'ABS_PR_LOA_D',
        'note': 'PR Days for SE'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'3056',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'ABS_PR_LOA_D',
        'note': 'PR Days for DK'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3056',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'ABS_PR_LOA_D',
        'note': 'PR Days for NO'
    }))

    print "done"
    return ops


fixit.program = 'skcms_3097.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
