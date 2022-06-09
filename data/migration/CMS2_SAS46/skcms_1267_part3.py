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

    # remove "SCHOOL FLIGHT" from the training_log_set table
    for entry in fixrunner.dbsearch(dc, 'training_log_set', "typ='SCHOOL FLIGHT'"):
        ops.append(fixrunner.createop('training_log_set', 'D', entry))

    # remove "SCHOOL FLIGHT INSTR" from the training_log_set table
    for entry in fixrunner.dbsearch(dc, 'training_log_set', "typ='SCHOOL FLIGHT INSTR'"):
        ops.append(fixrunner.createop('training_log_set', 'D', entry))

    print 'sucessfully completed fixit'
    return ops


if __name__ == '__main__':
    fixit.program = 'skcms_1267_part3.py (%s)' % __version__
    fixit()   # remove the old training types
