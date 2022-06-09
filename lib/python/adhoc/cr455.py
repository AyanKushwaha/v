

"""
CR 455 - New instructor qualification SUP, used for supervision on simulators.

This script will add a new record:
INSTRUCTOR+SUP
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('crew_qual_acqual_set', 'N', {
        'typ':'INSTRUCTOR',
        'subtype':'SUP',
        'descshort':'SUP',
        'desclong':'SUP',
        'si': ' ',
        }),
    ]


fixit.program = 'cr455.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
