#!/bin/env python


"""
SASCMS-3278 Update 3 rows and add 3 new.
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validstart = int(AbsDate('01Jan2006'))
    validend = int(AbsDate('31Dec2035'))
    ops = []
    # Change data in three current rows in salary_article.
    for entry in fixrunner.dbsearch(dc, 'salary_article'):
        if entry['extartid'] == '0680':
            entry['intartid'] = 'INST_CLASS'
            entry['note'] = 'Instructor - Classroom'
            ops.append(fixrunner.createop('salary_article', 'U', entry))

        if entry['extartid'] == '3228':
            entry['intartid'] = 'INST_CLASS'
            entry['note'] = 'Instructor - Classroom'
            ops.append(fixrunner.createop('salary_article', 'U', entry))

        if entry['extartid'] == '378':            
            entry['intartid'] = 'INST_CLASS'
            entry['note'] = 'Instructor - Classroom'
            ops.append(fixrunner.createop('salary_article', 'U', entry))


    # New rows in the table salary_article.
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='991'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'DK',
                                                              'extartid': '991',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CRM',
                                                              'note': 'Instructor - CRM'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='992'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'NO',
                                                              'extartid': '992',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CRM',
                                                              'note': 'Instructor - CRM'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='993'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'SE',
                                                              'extartid': '993',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CRM',
                                                              'note': 'Instructor - CRM'}))
    else:
        print "Row already exists."
    return ops


fixit.program = 'sascms-3278.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
