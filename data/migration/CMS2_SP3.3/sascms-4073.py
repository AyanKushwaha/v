#!/bin/env python


"""
CR 4073 CCR TR FC Need value on simulator trip

* Add new simulator types for sim with external instructor.
"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validstart = int(AbsDate('01Jan1986'))
    validend = int(AbsDate('31Dec2035'))/1440
    ops = []
    ops.append(fixrunner.createop('simulator_composition', 'N', {'grp': 'SIM',
                                                                 'special': True,
                                                                 'validfrom': validstart,
                                                                 'validto': validend,
                                                                 'fc': 0,
                                                                 'fp': 0,
                                                                 'fr': 0,
                                                                 'tr': 0,
                                                                 'tl': 2,
                                                                 'si': 'SIM external instructor'}))
    ops.append(fixrunner.createop('simulator_composition', 'N', {'grp': 'FFS',
                                                                 'special': True,
                                                                 'validfrom': validstart,
                                                                 'validto': validend,
                                                                 'fc': 0,
                                                                 'fp': 0,
                                                                 'fr': 0,
                                                                 'tr': 0,
                                                                 'tl': 2,
                                                                 'si': 'FFS external instructor'}))
    return ops


fixit.program = 'sascms-4073.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
