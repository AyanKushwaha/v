

"""
Remove problematic record from crew_document table


This script is a one-timer.
"""

import os
import sys
from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer


debug = False


def fixit(connstr, schemastr):
    dc = DaveConnector(connstr, schemastr)
    dc.getConnection().setProgram('INC0171948.py (2021-05-28)')
    print dc_info(dc)

    ops = []
    for entry in dbsearch(dc, 'crew_document', " ".join((
            "deleted = 'N'",
            "AND crew = '25189'",
            "AND validfrom = '17529120'", 
            "AND doc_typ = 'REC'", 
            "AND doc_subtype = 'LC'",
        ))):
        ops.append(createOp('crew_document', 'D', entry))
    print "*** Total %d ops" % len(ops)
    if ops:
        if debug:
            for op in ops:
                print op
        else:
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
