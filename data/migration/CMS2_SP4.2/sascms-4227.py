#!/bin/env python


"""
SASCMS-4227 Instructor tag missing on 737 FC and legality warning.

"""

import adhoc.fixrunner as fixrunner

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # New entry for special companions in table leg_attr_set.
    if len(fixrunner.dbsearch(dc, 'leg_attr_set', "id='SPEC COMP'")) == 0:
        ops.append(fixrunner.createop('leg_attr_set', 'N', {'id': 'SPEC COMP',
                                                            'category': 'Training',
                                                            'si': 'Special training companions'}))
    else:
        print "Row already exists."

    return ops


fixit.program = 'sascms-4227.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
