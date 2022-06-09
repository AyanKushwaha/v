#!/bin/env python


"""
SASCMS-2984 Add a new taskcodes in est_task

"""

import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
 
   
    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='NEW_SH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'NEW_SH', 'cat': 'C','taskgroup_cat': 'C', 
                                                        'taskgroup_code':'Prod SH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."
    
    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='NEW_LH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'NEW_LH', 'cat': 'C',
                                                        'taskgroup_cat': 'C',
                                                        'taskgroup_code':'Prod LH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."

    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='FLIGHT INSTR_SH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'FLIGHT INSTR_SH', 'cat': 'C',
                                                        'taskgroup_cat': 'C',
                                                        'taskgroup_code':'Prod SH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."
    
    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='FLIGHT INSTR_LH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'FLIGHT INSTR_LH', 'cat': 'C',
                                                        'taskgroup_cat': 'C',
                                                        'taskgroup_code':'Prod LH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."
        
    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='RELEASE_SH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'RELEASE_SH',
                                                        'taskgroup_cat': 'C', 'cat': 'C',
                                                        'taskgroup_code':'Prod SH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."
    
    # New row in the table est_task.
    if len(fixrunner.dbsearch(dc, 'est_task', "code='RELEASE_LH'")) == 0:
        ops.append(fixrunner.createop('est_task', 'N', {'code': 'RELEASE_LH', 'cat': 'C',
                                                        'taskgroup_cat': 'C',
                                                        'taskgroup_code':'Prod LH', 'si': None, 
                                                        'calcnode_setup_cat': None, 'calcnode_setup_name': None, 
                                                        'calcnode_name': None}))
    else:
        print "Row already exists."

    return ops


fixit.program = 'sascms-2984.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
