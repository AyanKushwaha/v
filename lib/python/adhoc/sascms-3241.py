#!/bin/env python


"""
CR 454 - Instructor's allowance

* Add new internal article ID's for the new salary types.
"""

import adhoc.fixrunner as fixrunner

__version__ = '1'

groups = ["Main", "RC", "VG", "FG", "OSL", "TRD", "SVG", "STO", "CPH"]


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for group in groups:
        ops.append(fixrunner.createop('crew_prod_day_groups', 'N', {'groupname': group}))
    return ops


fixit.program = 'sascms-3241.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
