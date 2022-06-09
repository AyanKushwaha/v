

"""
SASCMS-2176

Add attribute types 'FROZEN_EST_BLKOFF' to 'assignment_attr_set'.
"""

try:
    import adhoc.fixrunner as fixrunner
except ImportError:
    import sys
    print >>sys.stderr, "Please source (CARMUSR)/etc/carmenv.sh first!"
    sys.exit(1)
__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('assignment_attr_set', 'N', {
            'id': 'FROZEN_EST_BLKOFF',
            'category': 'General',
            'si': 'Frozen estimated block-off time',
        }),
    ]


fixit.program = 'sascms-2176.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
