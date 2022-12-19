#!/bin/env/python

"""
SKCMS-3022 TE: Overtime pay for Link crew
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-06_22_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    
    for entry in fixrunner.dbsearch(dc, 'salary_article'):
        if entry['extartid'] == '410A' and entry['extsys'] == 'DK':
            entry['intartid'] = 'CNLN_OT_50_PLUS'
            ops.append(fixrunner.createop('salary_article', 'U', entry))
         
        if entry['extartid'] == '410A' and entry['extsys'] == 'NO':
            entry['intartid'] = 'CNLN_OT_50_PLUS'
            ops.append(fixrunner.createop('salary_article', 'U', entry))



    print "done"
    return ops


fixit.program = 'skcms_3022.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
