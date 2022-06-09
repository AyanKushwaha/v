"""
SKCMS-2820: Update salary arcticle for link crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-05-23'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = int(AbsTime('01MAR2022 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for rec in fixrunner.dbsearch(dc, 'salary_article', "intartid = 'CNLN_SOLD'"):
        ops.append(fixrunner.createop('salary_article', 'D', rec))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'DK',
        'extartid':    '941A',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'CNLN_SOLD',
        'note':        'Sold day'
    }))

    ops.append(fixrunner.createOp('salary_article', 'N', {
        'extsys':      'NO',
        'extartid':    '941A',
        'validfrom':   validfrom,
        'validto':     validto,
        'intartid':    'CNLN_SOLD',
        'note':        'Sold day'
    }))
    
        
                                    
        
    
    
    return ops   
    

fixit.program = 'skcms-2820_1.py (%s)' % __version__
if __name__ == '__main__':
    fixit()