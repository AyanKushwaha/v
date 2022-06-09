#!/bin/env python

print "********************************************"
print "*   - Running SASCMS-4543"
print "*     Updating filter entry for table editor"
print "*     and spec_local_trans "
print "********************************************"

import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.run
def fixit(dc,*a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, "dave_entity_select", "selection='te_period_spec_local_trans'"):
        entry['wtempl'] = "(TO_DATE(REGEXP_SUBSTR($.leg,'[0-9]{2}[A-Za-z]{3}[0-9]{4}'))-TO_DATE('1JAN1986')) >= %:1"                        
        ops.append(fixrunner.createOp("dave_entity_select", 'U', entry))

    return ops


fixit.program = 'SASCMS-4543.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
