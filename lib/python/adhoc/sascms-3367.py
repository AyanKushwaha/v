#!/bin/env python

"""
Updates null account_name in bought_days based on day_type. This can be run multiple times, but
it will not take into account changes made by SASCMS-3367 later on, however since it will not
touch non-null entries everything should be allright.
"""

import datetime
import utils.dt
import adhoc.fixrunner as fixrunner

__version__ = '1'

EXTARTIDS = {'SE':'208', 'DK':'9495', 'NO':'4525'}

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    blanks = 0
    bought = 0
    for entry in fixrunner.dbsearch(dc, 'bought_days'):
        if not entry['account_name']:
            up = entry.copy()
            if entry['day_type'][:2] == 'BL':
                blanks += 1
                up['account_name'] = "BOUGHT_BL"
            else:
                bought += 1
                up['account_name'] = "BOUGHT"
            ops.append(fixrunner.createop('bought_days', 'U', up))
    if len(fixrunner.dbsearch(dc, 'salary_article', "intartid = 'BOUGHT_COMP'")) == 0:
        for b in ['SE','NO','DK']:
            ops.append(fixrunner.createOp('salary_article', 'N', {
                'extsys': b,
                'extartid': EXTARTIDS[b],
                'validfrom': 10519200,
                'validto': 25770240,
                'intartid': 'BOUGHT_COMP',
                'note': 'Bought day (w/compday)',
            }))
    if len(fixrunner.dbsearch(dc, 'account_set', "id = 'BOUGHT_COMP'")) == 0:
        ops.append(fixrunner.createOp('account_set', 'N', {
            'id': 'BOUGHT_COMP',
            'si': 'Bought + Compday',
        }))
    print "Updating %d rows (%d BOUGHT, %d BOUGHT_BL)" % (bought+blanks, bought, blanks)
    return ops


fixit.program = 'sascms-3367.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
