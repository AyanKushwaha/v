#!/bin/env/python

"""
SKCMS-2807 EC: Senior Cabin Crew (SCC) pay for Link
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-03_04_'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', 
        {
            'extsys': 'DK',
            'extartid':'032A',
            'validfrom': int(AbsTime('01Jan2022 00:00')),
            'validto':  int(AbsTime('31DEC2035 00:00')),
            'intartid': 'SCCSVS',
            'note': 'Acting Purser CA1 CC'
        }))

    ops.append(fixrunner.createOp('salary_article', 'N', 
        {
            'extsys': 'NO',
            'extartid':'032A',
            'validfrom': int(AbsTime('01Jan2022 00:00')),
            'validto':  int(AbsTime('31DEC2035 00:00')),
            'intartid': 'SCCSVS',
            'note': 'Acting Purser CA1 CC'
        }))

    return ops


fixit.program = 'skcms-2807.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
