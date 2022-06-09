#!/bin/env python


"""
SKBMM-325 Crew Portal data migration

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    if len(fixrunner.dbsearch(dc, 'account_set', "id='FS'")) == 0:
        ops.append(fixrunner.createop('account_set', 'N', {'id': 'FS',
                                                           'si': 'Free, super'}))
    else:
        print "account_set row already exists."

    if len(fixrunner.dbsearch(dc, 'crew_filter_type_set', "id='REQUEST'")) == 0:
        ops.append(fixrunner.createop('crew_filter_type_set', 'N', {'id': 'REQUEST',
                                                                    'si': 'Filter used when evaluating request legality'}))
    else:
        print "crew_filter_type row already exists."

    return ops


fixit.program = 'skbmm-326.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
