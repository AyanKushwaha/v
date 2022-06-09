#!/bin/env python


"""
SASCMS-1267 SCHOOLFLIGHT is not displayed in the training log
"""


import adhoc.fixrunner as fixrunner


__version__ = '4'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    print 'entered fixit'
    ops = []

    # add "SCHOOLFLIGHT" to the training_log_set table
    if len(fixrunner.dbsearch(dc, 'training_log_set', "typ='SCHOOLFLIGHT'")) == 0:
        ops.append(fixrunner.createop('training_log_set', 'N',
            {'typ': 'SCHOOLFLIGHT', 'grp': 'FLT TRAINING'}))

    # add "SCHOOLFLIGHT INSTR" to the training_log_set table
    if len(fixrunner.dbsearch(dc, 'training_log_set', "typ='SCHOOLFLIGHT INSTR'")) == 0:
        ops.append(fixrunner.createop('training_log_set', 'N',
            {'typ': 'SCHOOLFLIGHT INSTR', 'grp': 'INSTR'}))

    print 'sucessfully completed fixit'
    return ops


if __name__ == '__main__':
    fixit.program = 'skcms_1267_part1.py (%s)' % __version__
    fixit()   # add the new training types
