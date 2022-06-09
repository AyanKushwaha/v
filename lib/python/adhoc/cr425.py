

"""
Add rave parameterset data that had to be introduced for CR 425.
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
    for post in dbsearch(dc, 'assignment_attr_set', " ".join((
            "deleted = 'N'",
            "AND id = 'HOTEL_BOOKING'",
        ))):
        done = True
        print "Already has data: ", post['si']
    if done: return []
    return [
        fixrunner.createOp('assignment_attr_set', 'N', {
            'id': 'HOTEL_BOOKING',
            'category': 'General',
            'si': 'Hotel booking flags',
        }),
    ]


fixit.program = 'cr3425.py'

if __name__ == '__main__':
    fixit()
