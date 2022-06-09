#!/bin/env python


"""
SKCMS-1909: Add FS1 activity.
Sprint: SAS77
New version since it needs to run in SAS77
"""

import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2019-01-02'
ops = []


def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # Add FS1 activity and define the period.
    ops.append(fixrunner.createOp('activity_set', 'N', {'id': 'FS1',
                                                        'grp': 'FRE',
                                                        'si': 'Prioritized (super) free single day',
                                                        'recurrent_typ': None}))
    

    ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': 'FS1',
                                                               'validfrom': val_date("01Jan1986"),
                                                               'validto': val_date("31Dec2035"),
                                                               'si': None}))
    # Add calc setup nodes.
    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated',
                                                               'setup_cat': 'C',
                                                               'name': 'FS1',
                                                               'nodetype': 'TASKDRIVER',
                                                               'caption': None}))

    ops.append(fixrunner.createOp('est_calc_setup_node', 'N', {'setup_name': 'Migrated',
                                                               'setup_cat': 'C',
                                                               'name': 'FS1 limit',
                                                               'nodetype': 'DRIVER',
                                                               'caption': None}))
    # Add calc node relations.
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name': 'Migrated',
                                                                  'parent_setup_cat': 'C',
                                                                  'parent_name': 'Task_Group___F',
                                                                  'child_setup_name': 'Migrated',
                                                                  'child_setup_cat': 'C',
                                                                  'child_name': 'FS1',
                                                                  'factor': 1}))
    ops.append(fixrunner.createOp('est_calc_node_relation', 'N', {'parent_setup_name': 'Migrated',
                                                                  'parent_setup_cat': 'C',
                                                                  'parent_name': 'Request Limit',
                                                                  'child_setup_name': 'Migrated',
                                                                  'child_setup_cat': 'C',
                                                                  'child_name': 'FS1 limit',
                                                                  'factor': 1}))

    # Add bid period type.
    ops.append(fixrunner.createOp('bid_periods_type_set', 'N', {'bid_type': 'E_FS1'}))

    # Add layout parameters for FS1.
    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name': 'Migrated',
                                                           'layout_calc_cat': 'C',
                                                           'layout_name': 'Standard Layout',
                                                           'name': 'Task___FS1',
                                                           'calcnode_setup_name': 'Migrated',
                                                           'calcnode_setup_cat': 'C',
                                                           'calcnode_name': 'FS1',
                                                           'caption': 'FS1',
                                                           'vieworder': 1,
                                                           'viewlevel': 'Task',
                                                           'parent_layout_calc_name': 'Migrated',
                                                           'parent_layout_calc_cat': 'C',
                                                           'parent_layout_name': 'Standard Layout',
                                                           'parent_name': 'Task_Group___F'}))

    ops.append(fixrunner.createOp('est_layout_node', 'N', {'layout_calc_name': 'Migrated',
                                                           'layout_calc_cat': 'C',
                                                           'layout_name': 'Standard Layout',
                                                           'name': '_KPI_3_Request Limit_0_FS1 limit_1',
                                                           'calcnode_setup_name': 'Migrated',
                                                           'calcnode_setup_cat': 'C',
                                                           'calcnode_name': 'FS1 limit',
                                                           'caption': 'FS1 limit',
                                                           'vieworder': 1,
                                                           'viewlevel': 'Driver',
                                                           'parent_layout_calc_name': 'Migrated',
                                                           'parent_layout_calc_cat': 'C',
                                                           'parent_layout_name': 'Standard Layout',
                                                           'parent_name': '_KPI_3_Request Limit_0'}))

    ops.append(fixrunner.createOp('est_task', 'N', {'code': 'FS1',
                                                    'cat': 'C',
                                                    'taskgroup_code': 'F Spec',
                                                    'taskgroup_cat': 'C',
                                                    'calcnode_setup_name': 'Migrated',
                                                    'calcnode_setup_cat': 'C',
                                                    'calcnode_name': 'FS1'}))

    ops.append(fixrunner.createOp('est_driver', 'N', {'name': 'FS1 limit',
                                                      'cat': 'C',
                                                      'calcorder': 1,
                                                      'calc': True,
                                                      'dclass_classname': 'DriverStdParamForm_',
                                                      'dclass_cat': 'C',
                                                      'calcnode_setup_name': 'Migrated',
                                                      'calcnode_setup_cat': 'C',
                                                      'calcnode_name': 'FS1 limit'}))
    return ops


fixit.program = 'FS1_activity.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
