#!/bin/env python


"""
SASCMS-5424: New database table freeday_requirement_cc and servicegrade_set
             This script pupulates the new table servicegrade_set and adds * to crew_region_set.
"""

import adhoc.fixrunner as fixrunner


__version__ = '2'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    # Populate servicegrade_set
    servicegrades = ['100%',
                     '80%',
                     '75%',
                     '60%',
                     '50%']

    for sg in servicegrades:
        if len(fixrunner.dbsearch(dc, 'servicegrade_set', "id='%s'" % sg)) == 0:
            ops.append(fixrunner.createop('servicegrade_set', 'N', {'id': sg}))
        else:
            print "Servicegrade %s already exists" % sg


    if len(fixrunner.dbsearch(dc, 'crew_region_set', "id='*'")) == 0:
        ops.append(fixrunner.createop('crew_region_set', 'N', {'id': '*',
                                                                'name': 'All'}))
    else:
        print "Crew region '*' already exists"



    return ops


fixit.program = 'sascms-5424.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
