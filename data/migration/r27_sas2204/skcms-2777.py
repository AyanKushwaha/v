"""
SKCMS-2777 Link Meal cost
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-03_23_'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01Jan2022")
valid_to = val_date("31Dec2022")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'DK',
            'maincat':'C',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'DKK'
        }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'DK',
            'maincat':'F',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'DKK'
        }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'NO',
            'maincat':'C',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'NOK'
        }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'NO',
            'maincat':'F',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'NOK'
        }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'SE',
            'maincat':'C',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'SEK'
        }))

    ops.append(fixrunner.createOp('per_diem_compensation', 'N', 
        {
            'stop_country': 'MSVS',
            'home_country':'SE',
            'maincat':'F',
            'validfrom': valid_from,
            'validto':  valid_to,
            'compensation': 4500,
            'currency': 'SEK'
        }))

    return ops


fixit.program = 'skcms-2777.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
