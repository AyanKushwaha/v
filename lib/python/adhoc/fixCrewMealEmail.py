

"""
Update email addresses in CrewMeal tables
Used when copying schema's from PROD to TEST.
"""

import fixrunner
import datetime

__version__ = '$Revision$'

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    # Search for all entries 
    for entry in fixrunner.dbsearch(dc, 'meal_supplier', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['email'] = 'jfa@sas.dk'
        ops.append(fixrunner.createOp('meal_supplier', 'U', entry))
    for entry in fixrunner.dbsearch(dc, 'meal_customer', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['email'] = 'CPHOH.Support@sas.dk'
        ops.append(fixrunner.createOp('meal_customer', 'U', entry))
    return ops


fixit.program = 'fixCrewMealEmail.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
