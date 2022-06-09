#!/bin/env python


"""
SASCMS-4932 Update freedayspassive row in the freeday_requirement table

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
 
   
    # Update freedayspassive row in the freeday_requirement table.
    for entry in fixrunner.dbsearch(dc, 'freeday_requirement'):
        entry['freedayspassive'] = entry['minfreedays']
        ops.append(fixrunner.createop('freeday_requirement', 'U', entry))

    return ops

fixit.program = 'sascms-4932.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
