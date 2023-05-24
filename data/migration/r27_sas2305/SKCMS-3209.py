# -*- coding: utf-8 -*-

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023_01_01__01'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('estr_layout_param_type', 'N', {'name': 'bool'}))
    ops.append(fixrunner.createOp('estr_layout_param_type', 'N', {'name': 'int'}))
    ops.append(fixrunner.createOp('estr_layout_param_key', 'N', {'name': 'ShowAsPercent','idx': 0,'caption': 'As Percent' ,'paramtype': 'bool'}))
    ops.append(fixrunner.createOp('estr_layout_param_key', 'N', {'name': 'Decimals','idx': 1,'caption': 'Decimals' ,'paramtype': 'int'}))

    print "done"
    return ops


fixit.program = 'SKCMS_3209.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


