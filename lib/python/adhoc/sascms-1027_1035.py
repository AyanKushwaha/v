

"""
Script to repair a couple of issues found when running yearly conversion jobs.

SASCMS-1027: Wrong 'tim' for increment of F7S (2009-01-01 instead of
             2010-01-01).

SASCMS-1035: Field 'rate' was never entered by salary.compconv jobs.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NOTE: This script is a "one-timer". Don't run it again without modifications!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

import fixrunner
import datetime


__version__ = '$Revision$'
EPOCH = datetime.datetime(1986, 1, 1)


def to_dave_time(year, month, day):
    """Return now as DAVE time."""
    timestamp = datetime.datetime(year, month, day) - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60
    

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    new_tim_for_f7s = to_dave_time(2010, 1, 1)
    # Search for entries created in November 2009
    for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
            "source like 'salary.compconv%%'",
            "entrytime >= %d" % to_dave_time(2009, 11, 1),
            "entrytime < %d" % to_dave_time(2009, 12, 1),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        if entry['account'] == 'F7S':
            # Fix for SASCMS-1027
            entry['tim'] = new_tim_for_f7s
        # Fix for SASCMS-1035
        entry['rate'] = 100 * entry['amount'] / abs(entry['amount'])
        ops.append(fixrunner.createOp('account_entry', 'U', entry))
    return ops


fixit.program = 'sascms-1027_1035.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
