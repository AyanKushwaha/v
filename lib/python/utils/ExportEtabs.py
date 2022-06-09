"""

This module will try and load all tables to the TM model, filter away bad things and export
them as etabs using CuiSave-command.

"""

import os
import os.path
import time

import Errlog
import Cui
import Variable
import Crs
import carmstd.cfhExtensions as cfhExtensions
import StartTableEditor
import carmusr.ConfirmSave as cs

from tm import TM

def create_export_string():
    pass

def kill_java_forms():
    """ Checks for open java forms """
    try:
        open_forms = StartTableEditor.getOpenForms()
        if len(open_forms) > 0:
            cfhExtensions.show("You need to close all forms before exporting scenario.")
            return
    except:
        pass
    StartTableEditor.closeAll()

EXCLUDED = ['track_alert', 'task_alert', 'recource_link', 'activity_link', 'task', 'job', 'flight_leg_pax', 'published_roster',
            'job_parameter','resource_link']

def tables_to_export():
    tables = []
    for table in TM._entity:
        name = table.entity
        if not name.startswith('_') and \
               not name.startswith('leave') and \
               not name.startswith('salary') and \
               not name.startswith('cga') and \
               not name.startswith('est') and \
               not name.startswith('tmp_') and \
               name not in EXCLUDED:
            tables.append(name)
        else:
            print "Export is ignoring the following table: %s" % (name)
    tables.sort()
    print "Tables to export:", tables
    return tables

def load_tables(tables):
    TM(tables)

def rename_to_etab(tables):
    """ renames each etab to end with .etab"""
    carmdata = os.environ['CARMDATA']
    localplan_path = Variable.Variable("")
    subplan_path = Variable.Variable("")
    Cui.CuiGetLocalPlanPath(Cui.gpc_info, localplan_path)
    Cui.CuiGetSubPlanPath(Cui.gpc_info, subplan_path)
    
    lp_table_path = os.path.join(carmdata,'LOCAL_PLAN',
                                 localplan_path.value,'etable','LpLocal')
    for lp_table in tables:
        absolute_file_path = os.path.join(lp_table_path,lp_table)
        if not os.path.exists(absolute_file_path):
            print "could not find the expected file %s at %s", (lp_table, absolute_file_path)
        else:
            os.rename(absolute_file_path, absolute_file_path+".etab")

def save_model_to_etabs():
    """
    Main method which will create a etable for each Model table
    """
    kill_java_forms()
    export_string = create_export_string()

    user = os.environ.get("USER")

    tables = tables_to_export()
    load_tables(tables)

    lptabs = " ".join(tables)
    sptabs = "crew"

    os.environ["LP_TABS"] = lptabs
    os.environ["SP_TABS"] = sptabs

    
    Crs.CrsSetModuleResource("Database", "ExportEtabSubPlan",
                             "$(SP_TABS)", "Tables to SpLocal for Scenario")

    Crs.CrsSetModuleResource("Database", "ExportEtabLocalPlan",
                             "$(LP_TABS)", "Tables to LpLocal for Scenario")

    Crs.CrsSetModuleResource("Database","ExportEtabCrewPlan",
                                 'apa', "Name of CREW_PLAN for Scenario")


    cs.save_db_to_file = True #Set global variable in carmusr/ConfirmSave.py

    timestamp =  time.strftime("%Y%m%d_%H%M")
    
    sp_name = user+'_'+timestamp
    lp_name = os.path.join("XXXExport", "Meep", user+'_'+timestamp)
    
    try:
        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

        saveResult = Cui.CuiSavePlansAs( # Use this if exception is wanted
            {'FORM':'SUB_PLAN_FORM',
             'SUB_PLAN_HEADER_NAME': sp_name,
             'LOCAL_PLAN_HEADER_NAME': lp_name,
             'SUB_PLAN_HEADER_COMMENT': "meep",
             'SUB_PLAN_SAVE_ON_FILE': 'On',
             'FORM':'SUB_PLAN_FORM',
             'OK':0},
            Cui.gpc_info)
    except Exception, err:
        cs.save_db_to_file = False
        # Reset global variable in carmusr/ConfirmSave.py
        Errlog.log("ExportScenarios:: aborted while calling CuiSavePlansAs: %s" %
                   err)
        return
    
    cs.save_db_to_file = False

    rename_to_etab(tables)
