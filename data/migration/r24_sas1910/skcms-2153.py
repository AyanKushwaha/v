#!/bin/env python


"""
SKCMS-2153 Add agreement validity
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-09-25'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'a350_a5_ast_before_pc', 'validfrom': validfrom, 'validto': validto, 'si': 'A5 crew need AST before PC'}))

    return ops


fixit.program = 'skcms-2153.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

