# -*- coding: utf-8 -*-

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022_05_05__01'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('account_set', 'N', {'id': 'BOUGHT_SBY','si': 'Bought standby on day off'}))
    ops.append(fixrunner.createOp('account_set', 'N', {'id': 'BOUGHT_Prod','si': 'Bought Production on day off'}))
    ops.append(fixrunner.createOp('account_set', 'N', {'id': 'BOUGHT_DUTY','si': 'Bought additional duty'}))

    print "done"
    return ops


fixit.program = 'skcms_2822.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


