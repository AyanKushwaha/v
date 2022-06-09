#!/bin/env python


"""
SASCMS-4773 - Status UNKNOWN in vacation_status_set was missing. Not sure if we should ever have
any, but better have status UNKNOWN on vacations rather than exploding on reference errors.

"""

import adhoc.fixrunner as fixrunner

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # New entry for special companions in table leg_attr_set.
    if len(fixrunner.dbsearch(dc, 'vacation_status_set', "id='UNKNOWN'")) == 0:
        ops.append(fixrunner.createop('vacation_status_set', 'N', {'id': 'UNKNOWN',
                                                                   'si': ''}))
    else:
        print "Row already exists."

    return ops


fixit.program = 'sascms-47773.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
