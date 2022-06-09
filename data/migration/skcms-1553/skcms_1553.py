#!/bin/env python


"""
SKCMS-1553 Modify crew filter
"""


import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    #Modify relevant entity filters
    ops.append(fixrunner.createop("dave_filter_ref", "N", {"selection":"mppcategory", "source_filter":"mppcategory_crew_3", "target_filter":"mppcategory_crew_user_filter_7", "source_columns":"id", "target_columns":"crew", "distinct_req":True, "allow_predicate_pushdown":False}))

    # remove old filter reference
    for entry in fixrunner.dbsearch(dc, 'dave_filter_ref', "selection='mppcategory' AND source_filter='mppcategory_crew_6' AND target_filter='mppcategory_crew_user_filter_7'"):
        ops.append(fixrunner.createop('dave_filter_ref', 'D', entry))

    return ops


fixit.program = 'skcms_1553.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
