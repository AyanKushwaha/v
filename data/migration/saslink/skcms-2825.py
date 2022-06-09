#!/bin/env/python

"""
SKCMS-2825 New hotel customer entry for SAS Link
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-08'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    
    if len(fixrunner.dbsearch(dc, 'hotel_customer', "region='SVS'")) == 0:
        ops.append(fixrunner.createOp('hotel_customer', 'N',
                                  {'region': 'SVS',
                                   'name': 'SAS Link',
                                   'department': 'CPHOD, P. O. Box 150',
                                   'postalcode': '2770',
                                   'city': 'Kastrup',
                                   'country': 'Denmark',
                                   'contact': 'CBS-CPH',
                                   'phone': '+4532323166',
                                   'email': 'cbs.cpsh@sas.dk'}))

    return ops


fixit.program = 'SKCMS-2825.py (%s)' % __version__
if __name__ == '__main__':
    fixit(None, None, None)
