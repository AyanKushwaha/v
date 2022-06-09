#!/bin/env/python

"""
SKCMS-2173 Add AST handling for A5
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-05-13'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    start_id = 'ast_period_start_A5'
    end_id = 'ast_period_end_A5'
    start_si = 'Date for AST sim session on A5 to be started'
    end_si = 'Date for AST sim session on A5 to be completed'

    ops.append(fixrunner.createOp('property_set', 'N',
                                  {'id': start_id,
                                   'si': start_si}))
    ops.append(fixrunner.createOp('property_set', 'N',
                                  {'id': end_id,
                                   'si': end_si}))
    ops.append(fixrunner.createOp('property', 'N',
                                  {'id': start_id,
                                   'validfrom': int(AbsTime('1JAN1986')),
                                   'validto': int(AbsTime('31DEC2035')),
                                   'value_abs': int(AbsTime('1JAN2020')),
                                   'si': start_si}))
    ops.append(fixrunner.createOp('property', 'N',
                                  {'id': end_id,
                                   'validfrom': int(AbsTime('1JAN1986')),
                                   'validto': int(AbsTime('31DEC2035')),
                                   'value_abs': int(AbsTime('30JUN2020')),
                                   'si': end_si}))
    ops.append(fixrunner.createOp('activity_set', 'U',
                                  {'id': 'K5',
                                   'grp': 'AST',
                                   'si': 'AST A5'}))
    ops.append(fixrunner.createOp('activity_set_period', 'N',
                                  {'id': 'K5',
                                   'validfrom': int(AbsTime('1MAY2019')),
                                   'validto': int(AbsTime('31DEC2035'))}))
    return ops


fixit.program = 'skcms-2173.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
