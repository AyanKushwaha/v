

"""
SASCMS-1209 - "CMS legality soft rule gives warning for low F7S saldo when real
    balance is +"


Problem: Automated batch jobs had set the 'man' flag to False, where it should
    be True.

Solution: This script will set the flag 'man' to True for all entries created
    by 'salary.compconv'.


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NOTE: This script is a "one-timer". Don't run it again without modifications!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, 'account_entry', ' AND '.join((
            "source like 'salary.compconv%%'",
            "man = 'N'",
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['man'] = 'Y'
        ops.append(fixrunner.createOp('account_entry', 'U', entry))
    return ops


fixit.remark = 'SASCMS-1209 (%s)' % __version__


if __name__ == '__main__':
    fixit()
