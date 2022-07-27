"""
Update empno similar to extperkey wherever it is not already matching .

Rewritten to use fixrunner.
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    crewids = []
    now = get_now()
    ops = []
    for rec in fixrunner.dbsearch(dc, 'crew_employment', ' AND '.join((
                'validfrom <= %s' % now,
                'validto > %s' % now,
        ))):
        crewids.append(rec['crew'])
    for entry in fixrunner.dbsearch(dc, 'crew', ' AND '.join((
            "mcl = '%s'" % country,
            "id IN (%s)" % ', '.join(["'%s'" % x for x in crewids]),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        ops.append(createOp('ground_task', 'W', gtrec))
    return ops

    
fixit.program = 'empno_update_script.py (2022-07-27)'


if __name__ == '__main__':
    fixit()
