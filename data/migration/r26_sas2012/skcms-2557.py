"""
SKCMS-2557 A2LR: Add position A2_OW for A2 crew.
Release: SAS2012
"""


import adhoc.fixrunner as fixrunner

__version__ = '2020-11-26'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_qualification_set', 'N', {'typ': 'POSITION', 'subtype': 'A2_OW', 'si': 'Added in SKCMS-2557'}))

    return ops

fixit.program = 'skcms-2557.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
