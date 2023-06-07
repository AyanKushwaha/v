"""
SKCMS-3150: Appending Salary Article 4802 (Perdium Without Tax for Norwegian Crew)
            Also appending the number of nughts that accounts to this taxfree Perdium
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

#__version__ = '2022-11-23'
__version__ = '2023-05-16'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = int(AbsTime('01Jan2022 00:00'))
validto = int(AbsTime('31Dec2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '4802',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'PERDIEM_NO_WO_TAX',
        'note':        ''
    }))

    return ops   

fixit.program = 'skcms-3150.py (%s)' % __version__

if __name__ == '__main__':
    fixit()