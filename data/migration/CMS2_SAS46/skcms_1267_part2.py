#!/bin/env python


"""
SASCMS-1267 SCHOOLFLIGHT is not displayed in the training log
"""


import adhoc.fixrunner as fixrunner


__version__ = '4'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    print 'entered fixit'
    ops = []

    # update the crew_training_log table - changing typ from "SCHOOL FLIGHT" to "SCHOOLFLIGHT"
    for entry in fixrunner.dbsearch(dc, 'crew_training_log', "typ='SCHOOL FLIGHT'"):
        ops.append(fixrunner.createop('crew_training_log', 'D', entry))
        ops.append(fixrunner.createop('crew_training_log', 'N', 
            {'crew': entry['crew'],
            'typ': 'SCHOOLFLIGHT',
            'code': entry['code'],
            'tim': entry['tim'],
            'attr': entry['attr']}))

    # update the crew_training_log table - changing typ from "SCHOOL FLIGHT INSTR" to "SCHOOLFLIGHT INSTR"
    for entry in fixrunner.dbsearch(dc, 'crew_training_log', "typ='SCHOOL FLIGHT INSTR'"):
        ops.append(fixrunner.createop('crew_training_log', 'D', entry))
        ops.append(fixrunner.createop('crew_training_log', 'N', 
            {'crew': entry['crew'],
            'typ': 'SCHOOLFLIGHT INSTR',
            'code': entry['code'],
            'tim': entry['tim'],
            'attr': entry['attr']}))

    print 'sucessfully completed fixit'
    return ops


if __name__ == '__main__':
    fixit.program = 'skcms_1267_part2.py (%s)' % __version__
    fixit()   # update existing references
