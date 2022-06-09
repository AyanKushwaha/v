#!/bin/env python


"""
SKCMS-1891: Add agreement validity
Sprint: SAS70
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-08-16a'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Sep2018")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'cau_inshape_3_RP', 'validfrom': validfrom, 'validto': validto, 'si': 'InShape: Allow 3rd RP to be assigned for SKD'}))

    return ops


fixit.program = '1891_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
