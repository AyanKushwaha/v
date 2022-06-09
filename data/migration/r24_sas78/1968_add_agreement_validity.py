#!/bin/env python


"""
SKCMS-1968 Add agreement validity
Sprint: SAS78
"""


import adhoc.fixrunner as fixrunner
import time
import AbsTime

__version__ = '2019-01-28'


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

validfrom = val_date("01Jan2019")
validto = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'snk_contract_groups_validity', 'validfrom': validfrom, 'validto': validto, 'si': 'add contract groups SNK_V851,V852,V853 validity'}))

    return ops


fixit.program = '1968_add_agreement_validity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
