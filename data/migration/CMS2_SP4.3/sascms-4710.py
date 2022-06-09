#!/bin/env python


"""
SASCMS-4710 add 3 new rows to salary_article.
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validstart = int(AbsDate('01Apr2012'))
    validend = int(AbsDate('31Dec2035'))
    ops = []

    # New rows in the table salary_article.
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='991'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'DK',
                                                              'extartid': '991',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_SKILL_TEST',
                                                              'note': 'Instructor - Skill-Test'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='992'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'NO',
                                                              'extartid': '992',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_SKILL_TEST',
                                                              'note': 'Instructor - Skill-Test'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='993'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'SE',
                                                              'extartid': '993',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_SKILL_TEST',
                                                              'note': 'Instructor - Skill-Test'}))
    else:
        print "Row already exists."
    return ops


fixit.program = 'sascms-4710.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
