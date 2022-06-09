#!/bin/env python


"""
SASCMS-4887 Enable consume strategy for Establishment View (adding new strategies in est_trategy_set)

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
 
   
    # Update row in the est_strategy_set.
    for entry in fixrunner.dbsearch(dc, 'est_strategy_set', "id='PLANNED'"):
        if entry['si'] != 'Planned value':
            entry['si'] = 'Planned value'
            ops.append(fixrunner.createop('est_strategy_set', 'U', entry))
        else:
            print "Row already updated."
    
    # Update row in the est_strategy_set.
    for entry in fixrunner.dbsearch(dc, 'est_strategy_set', "id='ASSIGNED'"):
        if entry['si'] != 'Assigned value':
            entry['si'] = 'Assigned value'
            ops.append(fixrunner.createop('est_strategy_set', 'U', entry))
        else:
            print "Row already updated."

    # Update row in the est_strategy_set.
    for entry in fixrunner.dbsearch(dc, 'est_strategy_set', "id='MAX'"):
        if entry['si'] != 'Max of Planned and Assigned value':
            entry['si'] = 'Max of Planned and Assigned value'
            ops.append(fixrunner.createop('est_strategy_set', 'U', entry))
        else:
            print "Row already updated."
    
    # Update row in the est_strategy_set.
    for entry in fixrunner.dbsearch(dc, 'est_strategy_set', "id='ADJUSTED'"):
        if entry['si'] != 'Difference of Planned and Assigned value':
            entry['si'] = 'Difference of Planned and Assigned value'
            ops.append(fixrunner.createop('est_strategy_set', 'U', entry))
        else:
            print "Row already updated."
        
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='WEEK'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'WEEK', 'si': 'Planned surplus on week period'}))
    else:
        print "Row already exists."
    
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='WEEK-INT'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'WEEK-INT', 'si': 'Planned surplus on week period in integer values'}))
    else:
        print "Row already exists."
        
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='MONTH'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'MONTH', 'si': 'Planned surplus on month period'}))
    else:
        print "Row already exists."
    
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='MONTH-INT'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'MONTH-INT', 'si': 'Planned surplus on month period in integer values'}))
    else:
        print "Row already exists."
        
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='YEAR'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'YEAR', 'si': 'Planned surplus on year period'}))
    else:
        print "Row already exists."
    
    # Update row in the est_strategy_set.
    if len(fixrunner.dbsearch(dc, 'est_strategy_set', "id='YEAR-INT'")) == 0:
        ops.append(fixrunner.createop('est_strategy_set', 'N', {'id': 'YEAR-INT', 'si': 'Planned surplus on year period in integer values'}))
    else:
        print "Row already exists."
        
    return ops


fixit.program = 'sascms-4887.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
