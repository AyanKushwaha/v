

"""
Script to repair account entries with rate zero or None, which cause problems later on
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
    for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
            "(rate = 0 OR rate IS NULL)",
            "next_revid = 0",
            "deleted = 'N'"
        ))):
        try:
            100 * entry['amount'] / abs(entry['amount'])
        except:
            entry['rate'] = 100
        ops.append(fixrunner.createOp('account_entry', 'U', entry))
    return ops


fixit.program = 'sascms-4229.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
