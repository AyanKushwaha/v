#!/bin/env python

print "********************************************"
print "*   - Running SASCMS-2040"
print "*     Updating attribute update and sita_email"
print "*     in the meal_supplier table. "
print "********************************************"

import adhoc.fixrunner as fixrunner

__version__ = '1'

@fixrunner.run
def fixit(dc,*a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, "meal_supplier"):
        entry['update_support'] = False
        entry['sita_email'] = ""
                        
        ops.append(fixrunner.createOp("meal_supplier", 'U', entry))

    return ops


fixit.program = 'SASCMS-2040.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
