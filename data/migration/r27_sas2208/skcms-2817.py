#!/bin/env/python

"""
SKCMS-2817 EC: Link FD instructor pay

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-07_24_'

validfrom = int(AbsTime('01AUG2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'071A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_LIFUS_ACT_SVS',
        'note': 'LIFUS FD for DK'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'051A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_LC_SVS',
        'note': 'Line Check FD for DK'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'070A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_SIM_SKILL_BR_SVS',
        'note': 'Simulator Instructor for DK'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'068A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_GD_SVS',
        'note': 'Instructor ground duty for DK'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'2324',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_LIFUS_ACT_SVS',
        'note': 'LIFUS FD for NO'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'2325',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_LC_SVS',
        'note': '   Line Check FD for NO'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'2326',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_SIM_SKILL_BR_SVS',
        'note': 'Simulator Instructor for NO'
    }))
    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'2327',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'INST_GD_SVS',
        'note': 'Instructor ground duty for NO'
    }))

    print "done"
    return ops


fixit.program = 'skcms-2817.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
