"""
Remove wrongly migrated data from account_entry.

See CR 249

From 090101 no more F7s should be awarded to pilots.
"""

import os
import sys
from AbsTime import AbsTime
from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer

# Pilot availability
date_from = int(AbsTime(2009, 1, 1, 0, 0))


def fixit(connstr, schemastr):
    dc = DaveConnector(connstr, schemastr)
    dc.getConnection().setProgram('cr249.py (2009-06-02)')
    print dc_info(dc)

    pilots = set()
    for crew in dbsearch(dc, 'crew_employment', " ".join((
            "deleted = 'N'",
            "AND next_revid = 0", 
            "AND validfrom <= %d" % date_from,
            "AND validto > %d" % date_from,
            "AND titlerank like 'F%'",
        ))):
        pilots.add(crew['crew'])
    print "total", len(pilots), "pilots"

    ops = []
    for ac_rec in dbsearch(dc, 'account_entry', " ".join((
            "deleted = 'N'",
            "AND next_revid = 0",
            "AND account = 'F7S'",
            "AND si LIKE 'QUOTA 2009%'",
        ))):
        if ac_rec['crew'] in pilots:
            ops.append(createOp('account_entry', 'D', ac_rec))
            print "%(crew)-10.10s %(account)s %(amount)d" % ac_rec
                
    print "*** Total %d ops" % len(ops)
    if ops:
        commitid = DaveStorer(dc).store(ops, returnCommitId=True) 
        print "Saved with commitid = %d" % commitid
    dc.close()

    

def dbsearch(dc, entity, expr=[], withDeleted=False):
    """Search entity and return list of DCRecord objects."""
    if isinstance(expr, str):
        expr = [expr]
    return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))


def dc_info(dc):
    connstr, schema = dc.getConnectionInfo()[:2]
    return "Connection: %s, Schema %s" % (connstr, schema)
   


if __name__ == '__main__':
    fixit(os.environ['DB_URL'], os.environ['DB_SCHEMA'])

# eof
