

"""
Remove old reset runs

See WP NonCore-FAT 465

This script is a one-timer.
"""

import os
import sys
from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer


debug = False


def fixit(connstr, schemastr):
    dc = DaveConnector(connstr, schemastr)
    dc.getConnection().setProgram('wp_nc_465-2.py (2009-07-22)')
    print dc_info(dc)

    ops = []
    for entry in dbsearch(dc, 'account_entry', " ".join((
            "deleted = 'N'",
            "AND next_revid = 0", 
            "AND account = 'SOLD'", 
            "AND source = 'salary.accounts.Reset'",
        ))):
        ops.append(createOp('account_entry', 'D', entry))
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
