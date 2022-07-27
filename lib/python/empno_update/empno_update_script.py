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
    for crew in fixrunner.dbsearch(dc, 'crew_employment', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
            "validfrom <= '%s'" % now,
            "validto > '%s'" % now,
        ))):
        for entry in fixrunner.dbsearch(dc, 'crew', ' AND '.join((
            "id = '%s'" % crew['crew'],
            "empno <> '%s'" % crew['extperkey'],
            "(retirementdate > '%s' OR retirementdate IS NULL)" % now,
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['empno'] = crew['extperkey'] 
        ops.append(createOp('crew', 'U', entry))
    return ops

    
fixit.program = 'empno_update_script.py (2022-07-27)'


if __name__ == '__main__':
    fixit()
