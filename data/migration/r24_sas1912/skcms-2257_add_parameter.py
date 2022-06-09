#!/bin/env python

"""
SKCMS-2257 Add agreement validity
Release: SAS1912
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = 'ver.1912-01'

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01Jan2020'))
    validto = int(AbsTime('31Dec2022'))

    ops = []


    ops.append(fixrunner.createop('property_set', 'N', {'id': 'crmc_first_3_year_cycle',
                                                        'si': 'CRMS first 3-year cycle for crew employed before 01Jan2020'}))

    ops.append(fixrunner.createop('property', 'N', {'id': 'crmc_first_3_year_cycle',
                                                    'validfrom': validfrom,
                                                    'validto': validto,
                                                    'si': 'Default value'}))
    return ops

fixit.program = 'skcms-2257_add_parameter.py (%s)' % __version__
if __name__ == '__main__':
    fixit()