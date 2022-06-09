#!/bin/env python


"""
SKCMS-1052 changing the salary article code from BOUGHT_B to BOUGHT_BL
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '4'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for entry in fixrunner.dbsearch(dc, 'crew_qualification', "qual_typ='AIRPORT'"):
        entry['validto'] = convert_to_end_of_month(entry['validto'])
        ops.append(fixrunner.createop('crew_qualification', 'U', entry))

    return ops

def convert_to_end_of_month(validto):
    the_date = AbsTime(validto)
    new_date = the_date.month_ceil()
    return int(new_date)


fixit.program = 'skcms_1486.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
