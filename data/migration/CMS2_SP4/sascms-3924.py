#!/bin/env python


"""
SASCMS-3924 Add a new qualification.

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # New rows in the table salary_article.
    if len(fixrunner.dbsearch(dc, 'crew_qual_acqual_set', "subtype='OL'")) == 0:
        ops.append(fixrunner.createop('crew_qual_acqual_set', 'N', {'typ': 'INSTRUCTOR',
                                                              'subtype': 'OL',
                                                              'descshort': 'OL',
                                                              'desclong': 'OL',
                                                              'si': ' '}))
    else:
        print "Row already exists."

    return ops


fixit.program = 'sascms-3924.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
