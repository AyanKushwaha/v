#!/bin/env python


"""
SASCMS-4960 Remove table editor filters for mcl, crew_rehearsal_rec, salary_convertable_data


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    
    ops = []

    # Populate valid_qual_interval_set
    tables = ["mcl", 
              "crew_rehearsal_rec", 
              "salary_convertable_data",
              "crew_contact"]

    for table in tables:
        for entry in fixrunner.dbsearch(dc, 'dave_entity_select', "selection='te_period_%s' or selection='te_crew_%s' or selection='te_flight_%s' " % (table,table,table)):
            ops.append(fixrunner.createop('dave_entity_select', 'D', entry))

    return ops


fixit.program = 'sascms-4690.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
