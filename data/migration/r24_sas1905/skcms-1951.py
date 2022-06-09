#!/bin/env/python

"""
SKCMS-1951 Split AST periods into qualification groups
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2019-05-09'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_start'}))
    ops.append(fixrunner.createOp('property_set', 'D',
                                  {'id': 'ast_period_end'}))
    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_start',
                                   'validfrom': int(AbsTime('1JAN1986'))/60/24}))
    ops.append(fixrunner.createOp('property', 'D',
                                  {'id': 'ast_period_end',
                                   'validto': int(AbsTime('1JAN1986'))/60/24}))

    for qual_group in ['38', 'A2', 'A3A4']:
        start_id = 'ast_period_start_%s' % qual_group
        end_id = 'ast_period_end_%s' % qual_group
        start_si = 'Date for AST sim session on %s to be started' % qual_group
        end_si = 'Date for AST sim session on %s to be completed' % qual_group

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
                                       'value_abs': int(AbsTime('1JUL2019')),
                                       'si': start_si}))
        ops.append(fixrunner.createOp('property', 'N',
                                      {'id': end_id,
                                       'validfrom': int(AbsTime('1JAN1986')),
                                       'validto': int(AbsTime('31DEC2035')),
                                       'value_abs': int(AbsTime('30JUN2020')),
                                       'si': end_si}))
    return ops


fixit.program = 'skcms-1951.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
