#!/bin/env python


"""
SKCMS-1793 Add "static" data for crew_qual_acqual airport qualifications
Sprint: SAS68
"""


import adhoc.fixrunner as fixrunner

__version__ = '2018-06-14'

#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_qual_acqual_set', 'N', {'typ': 'INSTRUCTOR', 'subtype': 'LIFUS', 'descshort' : '121', 'desclong' : 'LFUS COMMANDER', 'si' : 'Added in SKCMS-1793'}))

    return ops


fixit.program = 'add_to_qual_set_skcms-1793.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
