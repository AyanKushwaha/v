#!/bin/env python


"""
SASCMS-3990 add 3 new rows to salary_article.
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

    # New rows in the table salary_article.
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='996'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'DK',
                                                              'extartid': '996',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CC',
                                                              'note': 'Instructor - CC'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='997'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'NO',
                                                              'extartid': '997',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CC',
                                                              'note': 'Instructor - CC'}))
    else:
        print "Row already exists."
    if len(fixrunner.dbsearch(dc, 'salary_article', "extartid='998'")) == 0:
        ops.append(fixrunner.createop('salary_article', 'N', {'extsys': 'SE',
                                                              'extartid': '998',
                                                              'validfrom': validstart,
                                                              'validto': validend,
                                                              'intartid': 'INST_CC',
                                                              'note': 'Instructor - CC'}))
    else:
        print "Row already exists."
    return ops


fixit.program = 'sascms-3990.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
