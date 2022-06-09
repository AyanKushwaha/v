#!/bin/env python


"""
SKCMS-1052 changing the salary article code from BOUGHT_B to BOUGHT_BL
"""


import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for entry in fixrunner.dbsearch(dc, 'salary_article', "extsys='S3' and extartid='2408' and intartid='BOUGHT_B'"):
        entry['intartid'] = 'BOUGHT_BL'
        ops.append(fixrunner.createop('salary_article', 'U', entry))

    return ops


if __name__ == '__main__':
    fixit.program = 'skcms_1052_article_codes.py (%s)' % __version__
    fixit()
