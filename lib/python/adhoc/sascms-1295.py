

"""
Remove faulty old Manpower rule exceptions
"""

import fixrunner

__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    # Search for entries that are no longer valid
    # i.e. ruleid beginning with leave_rules. or VacationBalance
    for entry in fixrunner.dbsearch(dc, 'rule_exception', ' AND '.join((
            "(ruleid like 'leave_rules.%' OR ruleid like 'VacationBalance%')",
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        ops.append(fixrunner.createOp('rule_exception', 'D', entry))
    return ops


fixit.program = 'sascms-1295.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
