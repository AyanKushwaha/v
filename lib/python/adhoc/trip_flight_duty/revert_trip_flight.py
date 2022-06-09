

"""
SKAM-1071

Script to recreate data as it was before revid 23611513

A problem with this revid is that a lot of other data was created/deleted with
this revid so the function fixrunner.backout() cannot be used here.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'

#Dummy revid is given below: Modifiy it
revid = 00178585037
tables_to_restore = (
    'trip_flight_duty',
)


def restore_op(table, entry):
    """Revert the operation given in 'entry'. Return a DaveOperation object."""
    if entry['deleted'] == 'Y':
        del entry['deleted']
        return fixrunner.createop(table, 'W', entry)
    else:
        return fixrunner.createop(table, 'D', entry)


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    """Revert changes."""
    ops = []
    for table in tables_to_restore:
        for entry in fixrunner.dbsearch(dc, table, 'revid = %s' % (
                revid), withDeleted=True):
            ops.append(restore_op(table, entry))
    return ops


fixit.remark = 'skam-1071.py (%s)' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
