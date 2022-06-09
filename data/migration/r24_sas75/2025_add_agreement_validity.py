#!/bin/env python


"""
SKCMS-2025: Add agreement validity
Sprint: SAS75
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2018-11-15'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'skn_cc_F0_entitlement_valid', 'validfrom': validfrom, 'validto': validto, 'si': 'SKN cc f0 change validity param added in SKCMS-2025'}))

    return ops


fixit.program = '2025_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
