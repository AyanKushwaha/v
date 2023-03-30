#!/bin/env/python

"""
SKCMS-3218 Change AST impl for A3A5 Pilots
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-02-22_1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_start_A3A4'}))
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_end_A3A4'}))
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_start_A5'}))
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_end_A5'}))

    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_start_A3A4',
                                   'validfrom': int(AbsTime('1JAN1986'))/60/24}))
    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_start_A5',
                                   'validfrom': int(AbsTime('1JAN1986'))/60/24}))

    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_end_A3A4',
                                   'validto': int(AbsTime('31DEC2035'))/60/24}))
    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_end_A5',
                                   'validto': int(AbsTime('31DEC2035'))/60/24}))

    ops.append(fixrunner.createOp('property_set', 'N',
                                    {'id':'ast_period_start_A3A5',
                                    'si': 'Date for AST sim session on A3A5 to be started'}))
    ops.append(fixrunner.createOp('property_set', 'N',
                                    {'id': 'ast_period_end_A3A5',
                                    'si': 'Date for AST sim session on A3A5 to be completed'}))
    ops.append(fixrunner.createOp('property', 'N',
                                    {'id': 'ast_period_start_A3A5',
                                    'validfrom': int(AbsTime('1JAN1986')),
                                    'validto': int(AbsTime('31DEC2035')),
                                    'value_abs': int(AbsTime('1JUL2022')),
                                    'si': 'Date for AST sim session on A3A5 to be started'}))
    ops.append(fixrunner.createOp('property', 'N',
                                    {'id': 'ast_period_end_A3A5',
                                    'validfrom': int(AbsTime('1JAN1986')),
                                    'validto': int(AbsTime('31DEC2035')),
                                    'value_abs': int(AbsTime('30JUN2023')),
                                    'si': 'Date for AST sim session on A3A5 to be completed'}))
    return ops


fixit.program = 'skcms-3218.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
