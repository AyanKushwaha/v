#!/bin/env python


"""
SKCMS-2555 Add agreement validity
Release: SAS2012
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2020-11-25'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("17Dec2020")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'alf_forbidden_for_skd_sks_fp', 'validfrom': validfrom, 'validto': validto, 'si': 'SKCMS-2555: ALF is forbidden destination for SKD/SKS FP'}))

    return ops


fixit.program = 'skcms-2555.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
