"""
SKCMS-3218: Change AST implementation for A3A5 qualified pilots
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-01-24'


def val_date(date_str):
    return int(AbsTime(date_str))/24/60

validfrom = int(AbsTime('01JAN1986 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))
abs = int(AbsTime('01Jul2022 00:00'))
time = int(AbsTime('01Jul2022 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('property', 'N', {
        'id'        :   'ast_period_end_A3A5',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A3A5 to be completed'
    }))
    ops.append(fixrunner.createOp('property', 'N', {
        'id'        :   'ast_period_start_A3A5',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A3A5 to be started'
    }))
    ops.append(fixrunner.createOp('property', 'D', {
        'id'        :   'ast_period_start_A3A4',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A3A5 to be started'
    }))

    ops.append(fixrunner.createOp('property', 'D', {
        'id'        :   'ast_period_end_A3A4',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A3A5 to be completed'
    }))
    ops.append(fixrunner.createOp('property', 'D', {
        'id'        :   'ast_period_start_A5',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A5 to be started'
    }))
    ops.append(fixrunner.createOp('property', 'D', {
        'id'        :   'ast_period_end_A5',
        'validfrom' :   validfrom,
        'validto'   :   validto,
        'value_rel' :   time,
        'value_abs' :   abs,
        'value_int' :    1,
        'value_str' :    '',
        'value_bool':    '',
        'si'        :    'Date for AST sim session on A5 to be completed'
    }))
   
    return ops   

fixit.program = 'skcms-3218.py (%s)' % __version__

if __name__ == '__main__':
    fixit()