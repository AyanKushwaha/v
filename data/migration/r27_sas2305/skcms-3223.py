#!/bin/env/python

"""
SKCMS-2773 TE: Overtime pay for Link crew
S
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2023-05_29_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'DK',
        'maincat': 'C',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'DKK'
    }))
    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'DK',
        'maincat': 'F',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'DKK'
    }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'SE',
        'maincat': 'C',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'SEK'
    }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'SE',
        'maincat': 'F',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'SEK'
    }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'NO',
        'maincat': 'C',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'NOK'
    }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', {
        'stop_country': 'MSV2',
        'home_country':'NO',
        'maincat': 'F',
        'validfrom': int(AbsTime('01Jan2023 00:00')),
        'validto': int(AbsTime('31DEC2035 00:00')),
        'compensation': 8000,
        'currency': 'NOK'
    }))

    print "done"
    return ops


fixit.program = 'skcms_3223.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
