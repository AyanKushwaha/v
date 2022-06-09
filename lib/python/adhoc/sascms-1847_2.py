

"""
SASCMS-1847

Remove duplicate entries. (part 2)

Search for entries in 'account_entry' which have the same bookingdate, crew,
account and value. These have been duplicated by the problem described in
SASCMS-1847.  Find the duplicates and remove all except one of them.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    remove = []
    keep = set()
    # Get list of duplicates
    for r in list(fixrunner.level_1_query(dc, " ".join((
        "SELECT DISTINCT",
            "a.crew, a.account, a.id, a.tim, a.amount",
        "FROM",
            "account_entry a,",
            "account_entry b",
        "WHERE",
            "a.deleted = 'N'",
            "AND",
            "a.next_revid = 0",
            "AND",
            "b.deleted = 'N'",
            "AND",
            "b.next_revid = 0",
            "AND",
            "a.man = 'N'",
            "AND",
            "b.man = 'N'",
            "AND",
            "a.reasoncode = 'OUT Roster'",
            "AND",
            "b.reasoncode = 'OUT Roster'",
            "AND",
            "a.id <> b.id ",
            "AND",
            "a.crew = b.crew",
            "AND",
            "a.account = b.account",
            "AND",
            "a.tim = b.tim",
        )), ('crew', 'account', 'id', 'tim', 'amount'))):
        # Keep one of the records
        key = (r['crew'], r['account'], r['tim'])
        if key in keep:
            remove.append(r['id'])
        else:
            keep.add(key)

    ops = []
    for entry in fixrunner.dbsearch(dc, 'account_entry', 'id IN %s' % (tuple(remove),)):
        ops.append(fixrunner.createop('account_entry', 'D', entry))
    return ops


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
