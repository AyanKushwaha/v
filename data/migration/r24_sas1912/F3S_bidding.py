#!/bin/env python


"""
SKCMS-2287 Add driver for F3S limit
Sprint: SAS1912
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2019-11-26c'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    # Setup calc setup node
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Activity___F3S', 'nodetype' : 'STRATEGY', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Driver___d-F3S', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Driver___d-F3S-Prod', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Driver___d-F3S-Prod-LH', 'nodetype' : 'DRIVER', 'caption' : None}))
    # Exists already
    #    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'F3S', 'nodetype' : 'TASKDRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'F3S limit', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Sum_Assigned___F3S', 'nodetype' : 'SUM', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Sum_Planned___F3S', 'nodetype' : 'SUM', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Task_Group___F3S', 'nodetype' : 'SUM', 'caption' : None}))
    # SKCMS-2287 - Added due to errors in Manpower
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Activity_Group___COMPDAYS', 'nodetype' : 'SUM', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Activity___Prod SH',  'nodetype' : 'STRATEGY', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'F', 'name' : 'Activity___Prod LH',  'nodetype' : 'STRATEGY', 'caption' : None}))

    # Setup calc node relation
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Activity_Group___COMPDAYS',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Activity___F3S',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Activity___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Sum_Assigned___F3S',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Activity___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Sum_Planned___F3S',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Request Strategy',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'F3S limit',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Assigned___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Task_Group___F3S',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Planned___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Driver___d-F3S',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Planned___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Driver___d-F3S-Prod',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'Sum_Planned___F3S',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Driver___d-F3S-Prod-LH',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'F',
								  'parent_name'       : 'New Effective Demand',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'F',
								  'child_name'        : 'Activity_Group___COMPDAYS',
								  'factor'            : None}))

    # Update existing F3S relation from Task_Group___Compdays to newly created Task_Group___F3S (create new and delete old)
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name': 'Migrated',
																  'parent_setup_cat': 'F',
																  'parent_name': 'Task_Group___F3S', # changed from Task_Group___Compdays
																  'child_setup_name': 'Migrated',
																  'child_setup_cat': 'F',
																  'child_name': 'F3S',
																  'factor': None}))
    # delete old relation
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name': 'Migrated',
																  'parent_setup_cat': 'F',
																  'parent_name': 'Task_Group___Compdays',
																  'child_setup_name': 'Migrated',
																  'child_setup_cat': 'F',
																  'child_name': 'F3S',
																  'factor': None}))


    # Setup activity
    ops.append(fixrunner.createOp('est_activity', 'N', {'name' : 'F3S',
							'cat' : 'F',
							'ag_name' : 'COMPDAYS',
							'ag_cat' : 'F',
							'displayorder' : 1,
							'display' : True,
							'calc' : True,
							'strategy' : 'MAX',
							'startdate' : 'SR',
							'si' : None})) 
    
    # Setup drivers
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'F3S limit',
                                                      'cat' : 'F',
                                                      'calcorder' : 1,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'F',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'F',
                                                      'calcnode_name' : 'F3S limit'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F3S',
                                                      'cat' : 'F',
						      						  'activity_name' : 'F3S',
						      						  'activity_cat'  : 'F',
                                                      'calcorder' : 262,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'F',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'F',
                                                      'calcnode_name' : 'Driver___d-F3S'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F3S-Prod',
                                                      'cat' : 'F',
												      'activity_name' : 'F3S',
												      'activity_cat'  : 'F',
                                                      'calcorder' : 263,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'F',
						      						  'dependact_name' : 'Prod SH',
                                                      'dependact_cat' :  'F',
                                                      'dependstrat' : 'MAX',
						      						  'si' : '% av Prod',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'F',
                                                      'calcnode_name' : 'Driver___d-F3S-Prod',
						      						  'depnode_setup_name' : 'Migrated',
                                                      'depnode_setup_cat' : 'F',
                                                      'depnode_name' : 'Activity___Prod SH'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F3S-Prod-LH',
                                                      'cat' : 'F',
												      'activity_name' : 'F3S',
												  	  'activity_cat'  : 'F',
                                                      'calcorder' : 261,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'F',
						      						  'dependact_name' : 'Prod LH',
                                                      'dependact_cat' :  'F',
                                                      'dependstrat' : 'MAX',
						      						  'si' : '% av Prod',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'F',
                                                      'calcnode_name' : 'Driver___d-F3S-Prod-LH',
						      						  'depnode_setup_name' : 'Migrated',
                                                      'depnode_setup_cat' : 'F',
                                                      'depnode_name' : 'Activity___Prod LH'}))

    # Setup bid period
    ops.append(fixrunner.createOp('bid_periods_type_set', 'N', {'bid_type' : 'F_F3S'}))

    # Setup layout params for F3S
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Activity___F3S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Activity___F3S',
							   'caption' : 'F3S',
							   'vieworder' : 0,
							   'viewlevel' : 'Activity',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity_Group___COMPDAYS'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F3S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Driver___d-F3S',
							   'caption' : 'd-F3S',
							   'vieworder' : 1,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F3S'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F3S-Prod',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Driver___d-F3S-Prod',
							   'caption' : 'd-F3S-Prod',
							   'vieworder' : 2,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F3S'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F3S-Prod-LH',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Driver___d-F3S-Prod-LH',
							   'caption' : 'd-F3S-Prod-LH',
							   'vieworder' : 0,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F3S'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Assigned___F3S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Sum_Assigned___F3S',
							   'caption' : 'Sum Assigned',
							   'vieworder' : 1,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F3S'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Planned___F3S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Sum_Planned___F3S',
							   'caption' : 'Sum Planned',
							   'vieworder' : 0,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F3S'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task_Group___F3S',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'Task_Group___F3S',
							   'caption' : 'F3S',
							   'vieworder' : 0,
							   'viewlevel' : 'Task Group',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Assigned___F3S'}))
    # Task___F0 C already existing from before. Need to update the parent_name on this one
    ops.append(fixrunner.createOp('est_layout_node', 'U', {'layout_calc_name' : 'Migrated',
                                                            'layout_calc_cat' : 'F',
          						   'layout_name' : 'Standard Layout',
         						   'name' : 'Task___F3S',
         						   'calcnode_setup_name' : 'Migrated',
         						   'calcnode_setup_cat' : 'F',
         						   'calcnode_name' : 'F3S',
         						   'caption' : 'F3S',
         						   'vieworder' : 0,
         						   'viewlevel' : 'Task',
         						   'parent_layout_calc_name' : 'Migrated',
         						   'parent_layout_calc_cat' : 'F',
         						   'parent_layout_name' : 'Standard Layout',
         						   'parent_name' : 'Task_Group___F3S'})) # updated from Task_Group___Compdays
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'F',
	 						   'layout_name' : 'Standard Layout',
							   'name' : '_KPI_3_Request Limit_0_F3S limit_1',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'F',
							   'calcnode_name' : 'F3S limit',
							   'caption' : 'F3S limit',
							   'vieworder' : 1,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'F',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : '_KPI_3_Request Limit_0'}))

    ops.append(fixrunner.createOp('est_param_node', 'N', {'node_setup_name' : 'Migrated',
							  'node_setup_cat'  : 'F',
							  'node_name'       : 'Activity___F3S',
							  'paramname'       : 'StrategyDate',
							  'paramvalue'      : 'SR'}))

    ops.append(fixrunner.createOp('est_task', 'U', {'code' : 'F3S',
						    'cat'  : 'F',
						    'taskgroup_code' : 'F3S', # changed from COMPDAYS
						    'taskgroup_cat'  : 'F',
						    'calcnode_setup_name' : 'Migrated',
						    'calcnode_setup_cat'  : 'F',
						    'calcnode_name'       : 'F3S'}))

    ops.append(fixrunner.createOp('est_task_group', 'N', {'code' : 'F3S',
														  'cat'  : 'F',
														  'activity_name' : 'F3S',
														  'activity_cat'  : 'F'}))

    return ops


fixit.program = 'F3S_bidding.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
