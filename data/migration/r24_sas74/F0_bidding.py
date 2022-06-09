#!/bin/env python


"""
SKCMS-1687 Add driver for F0 limit
Sprint: SAS74
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2018-11-02e'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    # Setup calc setup node
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Activity___F0', 'nodetype' : 'STRATEGY', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Driver___d-F0', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Driver___d-F0-Prod', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Driver___d-F0-Prod-LH', 'nodetype' : 'DRIVER', 'caption' : None}))
# Exists already
#    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'F0', 'nodetype' : 'TASKDRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'F0 limit', 'nodetype' : 'DRIVER', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Sum_Assigned___F0', 'nodetype' : 'SUM', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Sum_Planned___F0', 'nodetype' : 'SUM', 'caption' : None}))
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated', 'setup_cat': 'C', 'name' : 'Task_Group___F0', 'nodetype' : 'SUM', 'caption' : None}))

    
    # Setup calc node relation
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity_Group___COMPDAYS',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Activity___F0',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Sum_Assigned___F0',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Activity___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Sum_Planned___F0',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Request Limit',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'F0 limit',
								  'factor'            : 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Sum_Assigned___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Task_Group___F0',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Sum_Planned___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Driver___d-F0',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Sum_Planned___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Driver___d-F0-Prod',
								  'factor'            : None}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name' : 'Migrated',
								  'parent_setup_cat'  : 'C',
								  'parent_name'       : 'Sum_Planned___F0',
								  'child_setup_name'  : 'Migrated',
								  'child_setup_cat'   : 'C',
								  'child_name'        : 'Driver___d-F0-Prod-LH',
								  'factor'            : None}))

	# Update existing F0 relation from Task_Group___Compdays to newly created Task_Group___F0 (create new and delete old)
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name': 'Migrated',
																  'parent_setup_cat': 'C',
																  'parent_name': 'Task_Group___F0', # changed from Task_Group___Compdays
																  'child_setup_name': 'Migrated',
																  'child_setup_cat': 'C',
																  'child_name': 'F0',
																  'factor': None}))
	# delete old relation
    ops.append(fixrunner.createOp('est_calc_node_relation', 'D', {'parent_setup_name': 'Migrated',
																  'parent_setup_cat': 'C',
																  'parent_name': 'Task_Group___Compdays',
																  'child_setup_name': 'Migrated',
																  'child_setup_cat': 'C',
																  'child_name': 'F0',
																  'factor': None}))


    # Setup activity
    ops.append(fixrunner.createOp('est_activity', 'N', {'name' : 'F0',
							'cat' : 'C',
							'ag_name' : 'COMPDAYS',
							'ag_cat' : 'C',
							'displayorder' : 1,
							'display' : True,
							'calc' : True,
							'strategy' : 'MAX',
							'startdate' : 'SR',
							'si' : None})) 
    
    # Setup drivers
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'F0 limit',
                                                      'cat' : 'C',
                                                      'calcorder' : 1,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'C',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'C',
                                                      'calcnode_name' : 'F0 limit'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F0',
                                                      'cat' : 'C',
						      						  'activity_name' : 'F0',
						      						  'activity_cat'  : 'C',
                                                      'calcorder' : 262,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'C',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'C',
                                                      'calcnode_name' : 'Driver___d-F0'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F0-Prod',
                                                      'cat' : 'C',
												      'activity_name' : 'F0',
												      'activity_cat'  : 'C',
                                                      'calcorder' : 263,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'C',
						      						  'dependact_name' : 'Prod SH',
                                                      'dependact_cat' :  'C',
                                                      'dependstrat' : 'MAX',
						      						  'si' : '% av Prod',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'C',
                                                      'calcnode_name' : 'Driver___d-F0-Prod',
						      						  'depnode_setup_name' : 'Migrated',
                                                      'depnode_setup_cat' : 'C',
                                                      'depnode_name' : 'Activity___Prod SH'}))
    ops.append(fixrunner.createOp('est_driver', 'N', {'name' : 'd-F0-Prod-LH',
                                                      'cat' : 'C',
												      'activity_name' : 'F0',
												  	  'activity_cat'  : 'C',
                                                      'calcorder' : 261,
                                                      'calc' : True,
                                                      'dclass_classname' : 'DriverStdParamForm_',
                                                      'dclass_cat' : 'C',
						      						  'dependact_name' : 'Prod LH',
                                                      'dependact_cat' :  'C',
                                                      'dependstrat' : 'MAX',
						      						  'si' : '% av Prod',
                                                      'calcnode_setup_name' : 'Migrated',
                                                      'calcnode_setup_cat' : 'C',
                                                      'calcnode_name' : 'Driver___d-F0-Prod-LH',
						      						  'depnode_setup_name' : 'Migrated',
                                                      'depnode_setup_cat' : 'C',
                                                      'depnode_name' : 'Activity___Prod LH'}))

    # Setup bid period
    ops.append(fixrunner.createOp('bid_periods_type_set', 'N', {'bid_type' : 'D_F0'}))

    # Setup layout params for F0
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Activity___F0',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Activity___F0',
							   'caption' : 'F0',
							   'vieworder' : 0,
							   'viewlevel' : 'Activity',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity_Group___COMPDAYS'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F0',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Driver___d-F0',
							   'caption' : 'd-F0',
							   'vieworder' : 1,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F0'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F0-Prod',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Driver___d-F0-Prod',
							   'caption' : 'd-F0-Prod',
							   'vieworder' : 2,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F0'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Driver___d-F0-Prod-LH',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Driver___d-F0-Prod-LH',
							   'caption' : 'd-F0-Prod-LH',
							   'vieworder' : 0,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Planned___F0'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Assigned___F0',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Sum_Assigned___F0',
							   'caption' : 'Sum Assigned',
							   'vieworder' : 1,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F0'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Sum_Planned___F0',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Sum_Planned___F0',
							   'caption' : 'Sum Planned',
							   'vieworder' : 0,
							   'viewlevel' : 'Sum',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Activity___F0'}))
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : 'Task_Group___F0',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'Task_Group___F0',
							   'caption' : 'F0',
							   'vieworder' : 0,
							   'viewlevel' : 'Task Group',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : 'Sum_Assigned___F0'}))
     # Task___F0 C already existing from before. Need to update the parent_name on this one
    ops.append(fixrunner.createOp('est_layout_node', 'U', {'layout_calc_name' : 'Migrated',
                                                            'layout_calc_cat' : 'C',
          						   'layout_name' : 'Standard Layout',
         						   'name' : 'Task___F0',
         						   'calcnode_setup_name' : 'Migrated',
         						   'calcnode_setup_cat' : 'C',
         						   'calcnode_name' : 'F0',
         						   'caption' : 'F0',
         						   'vieworder' : 0,
         						   'viewlevel' : 'Task',
         						   'parent_layout_calc_name' : 'Migrated',
         						   'parent_layout_calc_cat' : 'C',
         						   'parent_layout_name' : 'Standard Layout',
         						   'parent_name' : 'Task_Group___F0'})) # updated from Task_Group___Compdays
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
							   'layout_calc_cat' : 'C',
	 						   'layout_name' : 'Standard Layout',
							   'name' : '_KPI_3_Request Limit_0_F0 limit_1',
							   'calcnode_setup_name' : 'Migrated',
							   'calcnode_setup_cat' : 'C',
							   'calcnode_name' : 'F0 limit',
							   'caption' : 'F0 limit',
							   'vieworder' : 1,
							   'viewlevel' : 'Driver',
							   'parent_layout_calc_name' : 'Migrated',
							   'parent_layout_calc_cat' : 'C',
							   'parent_layout_name' : 'Standard Layout',
							   'parent_name' : '_KPI_3_Request Limit_0'}))
    # Already existant from before
    # ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
    #     						   'layout_calc_cat' : 'F',
    #      						   'layout_name' : 'Standard Layout',
    #     						   'name' : 'Task_Group___F0',
    #     						   'calcnode_setup_name' : 'Migrated',
    #     						   'calcnode_setup_cat' : 'C',
    #     						   'calcnode_name' : 'Task_Group___F0',
    #     						   'caption' : 'F0',
    #     						   'vieworder' : 4,
    #     						   'viewlevel' : 'Task Group',
    #     						   'parent_layout_calc_name' : 'Migrated',
    #     						   'parent_layout_calc_cat' : 'F',
    #     						   'parent_layout_name' : 'Standard Layout',
    #     						   'parent_name' : 'Sum_Assigned___F Spec'}))
    # ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name' : 'Migrated',
    #     						   'layout_calc_cat' : 'F',
    #      						   'layout_name' : 'Standard Layout',
    #     						   'name' : 'Task___F0',
    #     						   'calcnode_setup_name' : 'Migrated',
    #     						   'calcnode_setup_cat' : 'F',
    #     						   'calcnode_name' : 'F0',
    #     						   'caption' : 'F0',
    #     						   'vieworder' : 0,
    #     						   'viewlevel' : 'Task',
    #     						   'parent_layout_calc_name' : 'Migrated',
    #     						   'parent_layout_calc_cat' : 'F',
    #     						   'parent_layout_name' : 'Standard Layout',
    #     						   'parent_name' : 'Task_Group___F0'}))


    ops.append(fixrunner.createOp('est_param_node', 'N', {'node_setup_name' : 'Migrated',
							  'node_setup_cat'  : 'C',
							  'node_name'       : 'Activity___F0',
							  'paramname'       : 'StrategyDate',
							  'paramvalue'      : 'SR'}))

    ops.append(fixrunner.createOp('est_task', 'U', {'code' : 'F0',
						    'cat'  : 'C',
						    'taskgroup_code' : 'F0', # changed from COMPDAYS
						    'taskgroup_cat'  : 'C',
						    'calcnode_setup_name' : 'Migrated',
						    'calcnode_setup_cat'  : 'C',
						    'calcnode_name'       : 'F0'}))

    ops.append(fixrunner.createOp('est_task_group', 'U', {'code' : 'F0',
														  'cat'  : 'C',
														  'activity_name' : 'F0',
														  'activity_cat'  : 'C'}))

    return ops


fixit.program = 'F0_bidding.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
