#!/bin/env python


"""
SKCMS-2214 Add JP overtime attribute
"""


import adhoc.fixrunner as fixrunner
import os
import time
import AbsTime

__version__ = '2019-10-21'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('assignment_attr_set', 'N', {'id': 'JP_OVERTIME', 'category': 'Salary', 'si': 'JP cabin crew assignment is eligible for overtime'}))

    return ops


fixit.program = 'skcms-2214.py (%s)' % __version__
if __name__ == '__main__':
    report_dir = "/samba-share/reports/JpOvertimeStatement"
    try:
        os.makedirs(report_dir)
    except OSError:
        print "Directory %s already exists" % report_dir
    os.chmod("/samba-share/reports/JpOvertimeStatement", 0o777)
    fixit()

