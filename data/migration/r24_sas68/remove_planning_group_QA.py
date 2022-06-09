#!/bin/env python




"""
SKCMS-1836  remove QA planning group from the table 'planning_group_set'
sprint SAS68
"""



import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
from decorators import dec

__version__ = "2018-06-20"




@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('planning_group_set', 'D', {'id':'QA', 'si':'Cimber Air'}))
    return ops



fixit.program = "remove_planning_group_QA"
if __name__ == "__main__":
    dec(fixit)
