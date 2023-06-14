#!/bin/env python


"""
SKCMS-3388 Remove alerts
"""


import adhoc.fixrunner as fixrunner




@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # remove old filter reference
    for entry in fixrunner.dbsearch(dc, 'track_alert', "rule='rules_indust_ccr.ind_check_out_before_summer_va' AND empno='94858'"):
        ops.append(fixrunner.createop('track_alert', 'D', entry))

    for entry in fixrunner.dbsearch(dc, 'track_alert', "rule='rules_indust_ccr.ind_check_out_before_summer_va' AND empno='96040'"):
        ops.append(fixrunner.createop('track_alert', 'D', entry))


    return ops


fixit.program = 'track_alert.py' 
if __name__ == '__main__':
    fixit()
