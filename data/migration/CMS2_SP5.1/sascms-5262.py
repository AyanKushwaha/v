"""
Add BOUGHT_8 to account_set

Add intartid BOUGHT_8 to salary_article for SE/DK/NO
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
 
    ops = []

    if len(fixrunner.dbsearch(dc, 'account_set', "id='BOUGHT_8'")) == 0:
        ops.append(fixrunner.createOp('account_set', 'N', {'id': 'BOUGHT_8',
                                                           'si': 'Bought 8%'}))
    else:
        print 'BOUGHT_8 already exists in account_set'

    validstart = int(AbsDate('01Jan2013'))
    validend = int(AbsDate('31Dec2035'))
        
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='1'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'DK',
                                                              'extartid': '1',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'BOUGHT_8',
                                                              'note': 'Bought day (<= 6 hours)'}))
    else:
        print "extartid=1 already exists in salary_article"
    
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='2'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'SE',
                                                              'extartid': '2',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'BOUGHT_8',
                                                              'note': 'Bought day (<= 6 hours)'}))
    else:
        print "extartid=2 already exists in salary_article"
    
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='3'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'NO',
                                                              'extartid': '3',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'BOUGHT_8',
                                                              'note': 'Bought day (<= 6 hours)'}))
    else:
        print "extartid=3 already exists in salary_article"

    return ops


fixit.program = 'sascms-5262.py (%s)' % __version__

if __name__ == '__main__':
    fixit()