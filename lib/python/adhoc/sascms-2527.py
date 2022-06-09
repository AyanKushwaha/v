

"""
SASCMS-2527

Script to recreate data as it was before revid 23611513, which was a session
that destroyed data for crew '18920'.

A problem with this revid is that a lot of other data was created/deleted with
this revid so the function fixrunner.backout() cannot be used here.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


revid = 23611513
crewid = '18920'
tables_to_restore = (
    'crew_contract',
    'crew_document',
    'crew_qualification',
    'crew_restr_acqual',
    'crew_restriction',
    'crew_seniority',
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
        for entry in fixrunner.dbsearch(dc, table, 'revid = %s AND crew = %s' % (
                revid, crewid), withDeleted=True):
            ops.append(restore_op(table, entry))
    return ops


fixit.remark = 'sascms-2527.py (%s)' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
