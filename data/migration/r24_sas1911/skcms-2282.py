# -*- coding: utf-8 -*-

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019_11_11__01'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('account_set', 'N', {'id': 'F38','si': 'Compensation day F38'}))

    print "done"
    return ops


fixit.program = 'skcms_2282.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


