#!/bin/env python


"""
Fix crew_meal_opt out entries, change the month of optout in meal_opt_out and crew_annotations
"""

import datetime
import fixrunner
from AbsTime import AbsTime


__version__ = "2022-03-23"

def val_date(date_str):
    return int(AbsTime(date_str)) / 24 / 60

newvalid_from =val_date("01Apr2022")
newvalid_to = val_date("01May2022")

date_from = val_date("01Mar2022")
date_to = val_date("01Apr2022")
@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for rec in fixrunner.dbsearch(dc, 'meal_opt_out', "month = 3 and year = 2022"):
        ops.append(fixrunner.createop('meal_opt_out', 'D', rec))
        ops.append(fixrunner.createop('meal_opt_out', 'N',  {
            'id': rec['id'],
            'month': 4,
            'year': rec['year']
        }))
    for rec_ca in fixrunner.dbsearch(dc, 'crew_annotations', "code = 'CM' AND  deleted = 'N' AND next_revid = 0 AND validfrom = %d AND validto = %d "% (date_from, date_to )):
        ops.append(fixrunner.createop('crew_annotations', 'U',  {
            'crew': rec_ca['crew'],
            'seqnr': rec_ca['seqnr'],
            'entrytime': rec_ca['entrytime'],
            'code':'CM',
            'property': rec_ca['property'],
            'validfrom': newvalid_from,
            'validto': newvalid_to,
            'isvisible': rec_ca['isvisible'],
            'text': rec_ca['text'],
            'username': rec_ca['username'],

    }))
    return ops


fixit.program = 'crew_meal_optout_fix.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
