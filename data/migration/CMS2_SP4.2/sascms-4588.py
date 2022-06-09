#!/bin/env python


"""
SASCMS-4588 Add a new qualification.

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # New row in the table crew_qualification_set.
    if len(fixrunner.dbsearch(dc, 'crew_qualification_set', "subtype='OL'")) == 0:
        ops.append(fixrunner.createop('crew_qualification_set', 'N', {'typ': 'INSTRUCTOR',
                                                              'subtype': 'OL',
                                                              'descshort': 'OL',
                                                              'desclong': 'OL',
                                                              'si': 'Instructor OL'}))
    else:
        print "Row already exists."

    # New rows in the table training_log_set.
    if len(fixrunner.dbsearch(dc, 'training_log_set', "typ='SUPERVISION'")) == 0:
        ops.append(fixrunner.createop('training_log_set', 'N', {'typ': 'SUPERVISION',
                                                              'grp': 'INSTR',
                                                              'si': ' '}))
    else:
        print "Row already exists."
    
    # New rows in the table training_log_set.
    if len(fixrunner.dbsearch(dc, 'training_log_set', "typ='SUPERVISOR'")) == 0:
        ops.append(fixrunner.createop('training_log_set', 'N', {'typ': 'SUPERVISOR',
                                                              'grp': 'INSTR',
                                                              'si': ' '}))
    else:
        print "Row already exists."

    return ops


fixit.program = 'sascms-4588.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
