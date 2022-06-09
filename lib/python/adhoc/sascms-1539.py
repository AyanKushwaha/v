

"""
SASCMS-1539

Add attribute types 'CCBUNKS' and 'FCBUNKS' to 'leg_attr_set'.
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('leg_attr_set', 'N', {
            'id': 'CCBUNKS',
            'category': 'General',
            'si': 'Number of crew bunks for Cabin Crew',
        }),
        fixrunner.createOp('leg_attr_set', 'N', {
            'id': 'FDBUNKS',
            'category': 'General',
            'si': 'Number of crew bunks for Flight Deck',
        }),
    ]


fixit.program = 'sascms-1539.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
