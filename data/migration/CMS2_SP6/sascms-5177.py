#!/bin/env python


"""
SASCMS-5177: Add some new activities to activity_set
"""

import adhoc.fixrunner as fixrunner

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    acts = []
    actsperiod = []

    for i in range(2,10):
        acts.append({'id': 'EX1%s'% i,
                     'grp': 'PGT',
                     'si': 'PGT refresher'})
        acts.append({'id': 'EX2%s'% i,
                     'grp': 'PGT',
                     'si': 'PGT refresher'})
        acts.append({'id': 'EX3%s'% i,
                     'grp': 'PGT',
                     'si': 'PGT refresher'})
        acts.append({'id': 'AC%s'% i,
                     'grp': 'PGT',
                     'si': 'AC Demo'})
        actsperiod.append({'id': 'EX1%s'% i,
                           'validfrom': 0,
                           'validto': 26295840})
        actsperiod.append({'id': 'EX2%s'% i,
                           'validfrom': 0,
                           'validto': 26295840})
        actsperiod.append({'id': 'EX3%s'% i,
                           'validfrom': 0,
                           'validto': 26295840})
        actsperiod.append({'id': 'AC%s'% i,
                           'validfrom': 0,
                           'validto': 26295840})
        

    for a in acts:
        if len(fixrunner.dbsearch(dc, 'activity_set', "id='%s'"% a['id'])) == 0:
            ops.append(fixrunner.createop('activity_set', 'N', a))
        else:
            print 'activity_set [%s] already exists'% a['id']

    for a in actsperiod:
        if len(fixrunner.dbsearch(dc, 'activity_set_period', "id='%s'"% a['id'])) == 0:
            ops.append(fixrunner.createop('activity_set_period', 'N', a))
        else:
            print 'activity_set_period [%s] already exists'% a['id']


    return ops


fixit.program = 'sascms-5177.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
