#!/bin/env python


"""
Remove entries from 'account_entry' that comes from from OVERTIME.
"""

import adhoc.fixrunner as fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    # Remove stuff that was entered at installation of CR 435.
    # See SASCMS-2010
    for rec in fixrunner.dbsearch(dc, 'account_entry',
            "source = 'Migration for CR435'"):
        ops.append(fixrunner.createop('account_entry', 'D', rec))
    for rec in fixrunner.dbsearch(dc, 'account_entry',
            "source = 'salary.type.OVERTIME'"):
        ops.append(fixrunner.createop('account_entry', 'D', rec))
    for rec in fixrunner.dbsearch(dc, 'account_entry', 
            "account in ('F0', 'F0_BUFFER') AND source = 'cr435_03_migrate.py'"):
        ops.append(fixrunner.createop('account_entry', 'D', rec))
    for rec in fixrunner.dbsearch(dc, 'salary_extra_data', 
            "runid in (3725, 3776, 3814, 3859)"):
        ops.append(fixrunner.createop('salary_extra_data', 'D', rec))
    return ops


fixit.program = 'cr435_00_cleanup.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
