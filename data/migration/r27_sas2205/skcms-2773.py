#!/bin/env/python

"""
SKCMS-2773 TE: Overtime pay for Link crew
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-05_13_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
   
    for entry in fixrunner.dbsearch(dc, 'salary_article'):
        if entry['extartid'] == '409A' and entry['extsys'] == 'DK':
            entry['intartid'] = 'CNLN_OT_45_50'
            entry['note'] = 'CNLN Overtid > 45 and CNLN Overtid < 50'
            ops.append(fixrunner.createop('salary_article', 'U', entry))

        if entry['extartid'] == '410A' and entry['extsys'] == 'DK':
            entry['intartid'] = 'CNLN_OT_50_Plus'
            entry['note'] = 'CNLN Overtid >=50'
            ops.append(fixrunner.createop('salary_article', 'U', entry))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'409A',
        'validfrom': int(AbsTime('01Jan2022 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'CNLN_OT_45_50',
        'note': ' CNLN Overtid > 45 and CNLN Overtid < 50'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid': '410A',
        'validfrom': int(AbsTime('01Jan2022 00:00')),
        'validto':  int(AbsTime('31DEC2035 00:00')),
        'intartid': 'CNLN_OT_50_Plus',
        'note': 'CNLN Overtid >=50'
    }))

    print "done"
    return ops


fixit.program = 'skcms_2773.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
