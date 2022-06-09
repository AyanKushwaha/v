

"""
Add rave parameterset data that had to be introduced for CR 388.
"""

import fixrunner
from carmensystems.dig.framework.dave import DaveSearch


def dbsearch(dc, entity, expr=[], withDeleted=False):
    """Search entity and return list of DCRecord objects."""
    if isinstance(expr, str):
        expr = [expr]
    return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))

@fixrunner.run
def fixit(dc, *a, **k):
    done = False
    for post in dbsearch(dc, 'rave_paramset_set', " ".join((
            "deleted = 'N'",
            "AND id = 'salary_exclude_crew'",
        ))):
        done = True
        print "Already has data: ", post['description']
    if done: return []
    return [
        fixrunner.createOp('rave_paramset_set', 'N', {
            'id': 'salary_exclude_crew',
            'description': 'Crew ID excluded from salary files',
        }),
    ]


fixit.program = 'cr388.py'

if __name__ == '__main__':
    fixit()
