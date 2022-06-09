

"""
Remove previous, faulty F7S allots.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NOTE: This script is a "one-timer". Don't run it again without modifications!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

import fixrunner
import datetime


__version__ = '$Revision$'
EPOCH = datetime.datetime(1986, 1, 1)


# Remove F7S assignments from 2009-11-16 02:01
remove_job_run_at = datetime.datetime(2009, 11, 16, 2, 1)


def to_dave_time(dt):
    """Return now as DAVE time."""
    timestamp = dt - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    # Search for entries created in November 2009
    for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
            "source like 'salary.compconv%%'",
            "account = 'F7S'",
            "entrytime = %d" % to_dave_time(remove_job_run_at),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        ops.append(fixrunner.createOp('account_entry', 'D', entry))
    return ops


fixit.program = 'sascms-1027_removal.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
