#!/bin/env python


"""
SKCMS-1687 Modify instances of F7S in establishment
Sprint: SAS74
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2018-11-01k'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

# Modify F7S. To be placed under Activity_Group___Compdays instead of Activity_Group___F7S. Removing instances of Activity___F7S, Task_Group___F7S and moving F7S under Compdays.


    # Remove F7S calc node
    ops.append(fixrunner.createOp('est_calc_setup_node', 'D', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Activity___F7S', 'nodetype' : 'STRATEGY', 'caption' : None})) # F7S items to be placed under Activity___Compdays instead

    ops.append(fixrunner.createOp('est_calc_setup_node', 'D', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Task_Group___F7S', 'nodetype' : 'SUM', 'caption' : None})) # F7S tasks to be placed under Task_Group___Compdays instead

	# Add Task_Group___Compdays for FC
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Task_Group___Compdays', 'nodetype' : 'SUM', 'caption' : None}))

    

    # Remove relation between Activity___F7S and Activity_Group___COMPDAYS
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity_Group___COMPDAYS',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Activity___F7S',
								  'factor'            : None}))


    # Removed since Sum_Assigned___Compdays shall be used instead
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity___F7S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Sum_Assigned___F7S',
								  'factor'            : 1}))

    # Removed since Activity___Compdays is used instead
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity___F7S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Sum_Planned___F7S',
								  'factor'            : 1}))

	# Removed since Sum_Assigned___Compdays shall be used instead
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Sum_Assigned___F7S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Task_Group___F7S',
								  'factor'            : None}))

    # needed for showing up under Task_Group___Compdays. Note already existant
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Task_Group___Compdays',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'F7S'}))


    # remove old relation between CC F7S and Task_Group___F7S. No need to create new as it is already existant in db
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Task_Group___F7S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
							          'child_name'        : 'F7S'}))
    # create new relation between FC VA-F7 and Task_Group___F7S. NOTE already existant
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Assigned___VA-F7',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
							          'child_name'        : 'Task_Group___Compdays'}))
    # remove old relation between FC Va-F7 and Task_Group___F7S
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Assigned___VA-F7',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
							          'child_name'        : 'Task_Group___F7S'}))
    # create new relation between FC F7S and Task_Group___Compdays. NOTE already existant
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Task_Group___Compdays',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
							          'child_name'        : 'F7S'}))
    # remove old relation between FC F7S and Task_Group___F7S
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Task_Group___F7S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
							      'child_name'        : 'F7S'}))






    # Removed since Activity___F7S shall not exist, all F7S to be put under Activity___Compdays
	# and therefore Sum_Planned and Sum_Assigned related to Compdays should be used instead
    ops.append(fixrunner.createOp('est_layout_node', 'D', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Activity___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Activity___F7S',
							   'caption' : 'F7S',
							   'vieworder' : 0,
							   'viewlevel' : 'Activity',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity_Group___COMPDAYS'}))
							   
    ops.append(fixrunner.createOp('est_layout_node', 'D', {'layout_calc_name' : 'Migrated',
                               'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Assigned___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Sum_Assigned___F7S',
							   'caption' : 'Sum Assigned',
							   'vieworder' : 1,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F7S'}))

    ops.append(fixrunner.createOp('est_layout_node', 'D', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Planned___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Sum_Planned___F7S',
							   'caption' : 'Sum Planned',
							   'vieworder' : 0,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F7S'}))

	# Not needed since all F7S tasks should be put under Task_Group___Compdays
    ops.append(fixrunner.createOp('est_layout_node', 'D', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task_Group___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Task_Group___F7S',
							   'caption' : 'F7S',
							   'vieworder' : 0,
							   'viewlevel' : 'Task',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Assigned___F7S'}))

    # update F7S. Put under Task_Group___Compdays
    ops.append(fixrunner.createOp('est_layout_node', 'U', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'F7S',
							   'caption' : 'F7S',
							   'vieworder' : 0,
							   'viewlevel' : 'Task',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Task_Group___Compdays'})) # Changed this from Task_Group___FS7

    # Not needed since Task_Group___F7S will not be used
    ops.append(fixrunner.createOp('est_layout_node', 'D', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task_Group___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Task_Group___F7S',
							   'caption' : 'F7S',
							   'vieworder' : 4,
							   'viewlevel' : 'Task Group',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Assigned___F Spec'}))

    # update F7S. Put under Task_Group___Compdays
    ops.append(fixrunner.createOp('est_layout_node', 'U', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task___F7S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'F7S',
							   'caption' : 'F7S',
							   'vieworder' : 0,
							   'viewlevel' : 'Task',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Task_Group___Compdays'})) # Changed this from Task_Group___FS7

    # Not needed since Activity___F7S should not exist
    ops.append(fixrunner.createOp('est_param_node', 'D', {'node_setup_name' : 'Migrated',
							  'node_setup_cat'  : 'C',
							  'node_name'       : 'Activity___F7S',
							  'paramname'       : 'StrategyDate',
							  'paramvalue'      : 'SR'}))

	# update F7S. Put under Compdays
    ops.append(fixrunner.createOp('est_task', 'U', {'code' : 'F7S',
						    'cat'  : 'C',
						    'taskgroup_code' : 'Compdays', # Changed from F7S
						    'taskgroup_cat'  : 'C',
						    'calcnode_setup_name' : 'Migrated',
						    'calcnode_setup_cat'  : 'C',
						    'calcnode_name'       : 'F7S'}))
    ops.append(fixrunner.createOp('est_task', 'U', {'code' : 'F7S',
						    'cat'  : 'F',
						    'taskgroup_code' : 'Compdays', # Changed from F7S
						    'taskgroup_cat'  : 'F',
						    'calcnode_setup_name' : 'Migrated',
						    'calcnode_setup_cat'  : 'F',
						    'calcnode_name'       : 'F7S'}))

    # update F7S. Make relation between F7S and Compdays
    ops.append(fixrunner.createOp('est_task_group', 'U', {'code' : 'F7S',
							  'cat' : 'C',
							  'activity_name' : 'Compdays',
							  'activity_cat'  : 'C'}))

    return ops


fixit.program = 'F7S_modify.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
