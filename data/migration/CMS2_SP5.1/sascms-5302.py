

"""
SASCMS-5302

Adds F36 account and activity
"""

import datetime
import adhoc.fixrunner as fixrunner
import subprocess
import os

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    """Adds F36 account and activity"""
    ops = []

    if len(fixrunner.dbsearch(dc, 'activity_set', "id='F36'")) == 0:
        ops.append(fixrunner.createop('activity_set', 'N', {'id' : 'F36',
                                                            'grp' : 'FRE',
                                                            'si' : 'Compensated day off'}))
    else:
        print "Activity F36 already exists"

    if len(fixrunner.dbsearch(dc, 'account_set', "id='F36'")) == 0:
        ops.append(fixrunner.createop('account_set', 'N', {'id' : 'F36',
                                                           'si' : 'Compensation day F36'}))
    else:
        print "Account F36 already exists"

    return ops

fixit.remark = 'SASCMS-5302'


if __name__ == '__main__':
    fixit()
