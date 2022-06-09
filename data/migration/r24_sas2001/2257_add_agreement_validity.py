#!/bin/env python


"""
SKCMS-2257 Add agreement validity
Release: SK_2001
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-12-20a6'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2020")
validto = val_date("31Dec2022")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'crmc_first_3_year_cycle_valid', 'validfrom': validfrom, 'validto': validto, 'si': 'crmc first 3 year cycle'}))

    return ops


fixit.program = '2257_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

