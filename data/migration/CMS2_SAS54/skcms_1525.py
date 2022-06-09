#!/bin/env python


"""
SKCMS-1525 Add AST periods.
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
import datetime

__version__ = '3'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    validfrom = int(AbsTime('01Jan1986'))
    validto = int(AbsTime('31Dec2035'))
    for entry in fixrunner.dbsearch(dc, 'property', "(id='ast_period_start') OR (id='ast_period_end')"):
        ops.append(fixrunner.createop('property', 'D', entry))
    ops.append(fixrunner.createop('property', 'N', {'id' : 'ast_period_start',
                                                    'value_abs' : int(AbsTime('01Nov2017')),
                                                    'validfrom' : validfrom,
                                                    'validto' : validto,
                                                    'si' : 'Date for AST sim session to be started'}))
    ops.append(fixrunner.createop('property', 'N', {'id' : 'ast_period_end',
                                                    'value_abs' : int(AbsTime('01Mar2018')),
                                                    'validfrom' : validfrom,
                                                    'validto' : validto,
                                                    'si' : 'Date for AST sim session to be ended'}))

    return ops


fixit.program = 'skcms_1525.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
