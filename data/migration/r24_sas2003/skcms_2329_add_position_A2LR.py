"""
SKCMS-2329 A2LR: Add Pos A2LR for A2 crew.
Release: SAS2003
"""


import adhoc.fixrunner as fixrunner

__version__ = '2020-03-05'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_qualification_set', 'N', {'typ': 'POSITION', 'subtype': 'A2LR', 'si': 'Added in SKCMS-2329'}))

    return ops

fixit.program = 'skcms_2329_add_position_A2LR.py (%s)' % __version__
if __name__ == '__main__':
    fixit()