#!/bin/env python


"""
SASCMS-5079 Add attribute "NO ATTRIBUTE" to table crew_training_t_set
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
 
    ops = []

    if len(fixrunner.dbsearch(dc, 'crew_training_t_set', "id='NO ATTRIBUTE'")) == 0:
        ops.append(fixrunner.createOp('crew_training_t_set', 'N', {'id': 'NO ATTRIBUTE',
                                                                   'si': '-'}))
    else:
        print 'crew_training_t_set entry "NO ATTRIBUTE" already exist'

    return ops


fixit.program = 'sascms-5079.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
