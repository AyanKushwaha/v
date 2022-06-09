#!/bin/env python


"""
SASCMS-4948. Move accumulator_int where name='accumulators.half_freeday_acc' to half_freeday_carry_over
             if 'tim' is 2012 or later.
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for row in fixrunner.dbsearch(dc, 'accumulator_int', "name='accumulators.half_freeday_acc'"):
        if row['tim'] > 13674239:        
            ops.append(fixrunner.createop('half_freeday_carry_over','N',{'crew' : row['acckey'],
                                                                         'tim' : row['tim'],
                                                                         'carry_over' : row['val']%2 == 0}))
        ops.append(fixrunner.createop('accumulator_int','D',row))


    return ops


fixit.program = 'sascms-4948.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
