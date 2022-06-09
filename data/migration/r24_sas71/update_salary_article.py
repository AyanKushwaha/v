#!/bin/env python


"""
SKCMS-1830 Changes to MEAL Order update
Sprint: SAS65
"""


import adhoc.fixrunner as fixrunner
import time
from AbsTime import AbsTime
from RelTime import RelTime
from AbsDate import AbsDate

__version__ = '2018-08-28a'

#validfrom = int(AbsTime(str(time.strftime("%d%b%Y", time.localtime(time.time()))+' 00:00')))
validfrom = int(AbsTime('01Dec2012 00:00'))
validto = int(AbsTime('31Dec2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'U', {'extsys': 'DK', 'extartid': '0718', 'validfrom': validfrom, 'validto': validto, 'intartid': 'INST_SIM_SKILL_BR'}))
    ops.append(fixrunner.createOp('salary_article', 'U', {'extsys': 'NO', 'extartid': '3224', 'validfrom': validfrom, 'validto': validto, 'intartid': 'INST_SIM_SKILL_BR'}))
    ops.append(fixrunner.createOp('salary_article', 'U', {'extsys': 'S3', 'extartid': '5108', 'validfrom': validfrom, 'validto': validto, 'intartid': 'INST_SIM_SKILL_BR'}))

    return ops


fixit.program = 'update_salary_artical.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
