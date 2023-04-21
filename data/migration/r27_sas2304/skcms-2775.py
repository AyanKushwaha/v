#!/bin/env/python

"""
SKCMS-2775 TE: Link Bought day paycodes for production, standby and additional duty

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-04-21_'

validfrom = int(AbsTime('01APR2023 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941A',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FDAY',
        'note': 'Link Free days bought as StandBy and Production'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941B',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for FC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941C',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for FP'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941D',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for CC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941E',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for FC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941F',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for FP'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'DK',
        'extartid':'941G',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for CC'
    }))


    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3243',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FDAY',
        'note': 'Link Free days bought as StandBy and Production'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3244',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for FC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3245',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for FP'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3246',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHR_DUTY',
        'note': 'Link F days bought as Prod and Bought Additional Duty for CC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3247',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for FC'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3248',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for FP'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys': 'NO',
        'extartid':'3249',
        'validfrom': validfrom,
        'validto':  validto,
        'intartid': 'CNLN_BOUGHT_FHOUR_SB',
        'note': 'Link Free day bought as Standby for CC'
    }))



    print "done"
    return ops


fixit.program = 'skcms-27751.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
