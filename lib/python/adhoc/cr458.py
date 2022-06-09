

"""
CR 458 - New instructor qualification REC & OAA, used for instructors on CC REC.

This script will add a two new records:
INSTRUCTOR+REC
INSTRUCTOR+OAA
"""

import adhoc.fixrunner as fixrunner

__version__ = '$Revision$'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('crew_qualification_set', 'N', {
        'typ':'INSTRUCTOR',
        'subtype':'REC',
        'descshort':'REC',
        'desclong':'REC',
        'si': 'Instructor for cabin recurrent',
        }),
        fixrunner.createOp('crew_qualification_set', 'N', {
        'typ':'INSTRUCTOR',
        'subtype':'OAA',
        'descshort':'OAA',
        'desclong':'OAA',
        'si': 'Instructor OAA',
        }),
    ]


fixit.program = 'cr458.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
