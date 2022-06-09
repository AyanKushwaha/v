#!/bin/env/python

"""
SKCMS-2067 Add FAM FLT course type to JMP.
Sprint: 1903
"""

import adhoc.fixrunner as fixrunner

__version__ = '2019-03-21'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('course_type', 'N',
                                  {'id': 'CTR-A3A5',
                                   'si': 'Added in SKCMS-2067'}))

    ops.append(fixrunner.createOp('course_block_type', 'N',
                                  {'id': 'FAM FLT',
                                   'color': 'LightYellow',
                                   'text': 'FAM FLT',
                                   'resourceneed': 'DEFAULT',
                                   'participantprod': True,
                                   'si': 'Added in SKCMS-2067'}))

    ops.append(fixrunner.createOp('training_log_set', 'N',
                                  {'typ': 'FAM FLT',
                                   'grp': 'FLT TRAINING',
                                   'si': 'Added in SKCMS-2067'}))

    ops.append(fixrunner.createOp('crew_training_t_set', 'N',
                                  {'id': 'FAM FLT',
                                   'si': 'Added in SKCMS-2067'}))

    return ops


fixit.program = 'FAM_FLT.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
