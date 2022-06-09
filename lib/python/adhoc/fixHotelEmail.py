

"""
Update email addresses in Hotel & Transport tables
Used when copying schema's from PROD to TEST.
"""

import fixrunner
import datetime

__version__ = '$Revision$'

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    # Search for all entries 
    for entry in fixrunner.dbsearch(dc, 'hotel', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['si'] = entry['email'][:200]
        entry['email'] = 'CPHOH.Support@sas.dk'
        ops.append(fixrunner.createOp('hotel', 'U', entry))
    for entry in fixrunner.dbsearch(dc, 'hotel_customer', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['si'] = entry['email'][:200]
        entry['email'] = 'CPHOH.Support@sas.dk'
        ops.append(fixrunner.createOp('hotel_customer', 'U', entry))
    for entry in fixrunner.dbsearch(dc, 'transport', ' AND '.join((
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['si'] = entry['email'][:200]
        entry['email'] = 'CPHOH.Support@sas.dk'
        entry['emailupd'] = 'CPHOH.Support@sas.dk'
        ops.append(fixrunner.createOp('transport', 'U', entry))
    return ops


fixit.program = 'fixHotelEmail.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
