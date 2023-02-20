#

#
__version__ = "$Revision$"
"""
Export Scenarios
Module for doing:
Export plan from DB to file for APC or Matador runs
@date:26Aug2008
@author: Per Groenberg (pergr) (Added header...)
@org: Jeppesen Systems AB
"""

import Cui
import Gui
import Csl
import Variable
import Crs
import Errlog
import time
import os
import os.path
import shutil
import tempfile
from AbsTime import AbsTime
import AbsDate
import carmusr.ConfirmSave as cs
import utils.time_util as time_util
import carmusr.HelperFunctions as HF
import carmstd.cfhExtensions as cfhExtensions
import carmusr.application as application
import utils.CfhFormClasses as CFC
import carmusr.application as application

from tm import TM, TempTable

from modelserver import EntityError
from modelserver import DateColumn
from modelserver import StringColumn
from modelserver import RefColumn
from modelserver import BoolColumn
from modelserver import IntColumn
from modelserver import UUIDColumn
from modelserver import TimeColumn
from modelserver import RelTimeColumn

import modelserver
import carmensystems.rave.api as R
import StartTableEditor

#import carmensystems.common.ServiceConfig as ServiceConfig
import utils.ServiceConfig as ServiceConfig

# Uses to map ground duty attrs in matador
# Should match leg.%ground_task_mappings%
_GND_MAP_TMP_TABLE_NAME = "gnd_key_mappings"
_EXPORT_DATA_TMP_TABLE_NAME = "export_data"

_TMP_TABLES_SP = {_GND_MAP_TMP_TABLE_NAME:None}

_TMP_TABLES_LP = {_EXPORT_DATA_TMP_TABLE_NAME:None} # To prevent GC

class ParamsetNameDialog(CFC.BasicCfhForm):
    def __init__(self,
                 paramset_name,
                 title='Save Paramset As:'):
        CFC.BasicCfhForm.__init__(self,title)
        self.add_label(0, 1, 'form_text', "Please enter name,\ncancel will abort export.")
        self.add_filter_combo(2,1, "paramset", "Paramset Name:",
                              paramset_name,
                              [],
                              upper=False)
    @property
    def paramset(self):
        return self.paramset_field.valof()


def showPrompt(s):
    Csl.Csl().evalExpr('csl_prompt("%s")' % s)


def writeCREW_PLAN(crewplanname):
    """Creates a CREW_PLAN by exporting from TM"""
    fullpath = os.path.join(os.path.expandvars("$CARMDATA"),
                            "CREW_PLAN",
                            crewplanname)
    crewplan = open(fullpath, "w")

    ppStart, = R.eval("fundamental.%pp_start%")
    ppEnd, = R.eval("fundamental.%pp_end%")

    #validrecords = TM.crew_employment.search("(&(validfrom<=%s)(validto>%s))"%
    #                                         (str(ppStart), str(ppStart)))
    #

    # All non retired crew
    # crewinplan = TM.crew.search("(!(retirementdate<%s))"%str(ppStart))
    # All crew_employment overlapping
    crewempinplan = TM.crew_employment.search(
        "(&(validto>%s)(validfrom<%s)(!(crew.retirementdate<%s)))"%
        (str(ppStart), str(ppEnd), str(ppStart)))

    crewdict = {}

    for crewemp in crewempinplan:
        # Create some tuple
        try:
            rank = str(crewemp.titlerank.id)
            if rank[0] == "F":
                cat = "F"
            else:
                cat = "C"
            
            emptuple = (str(crewemp.crew.id), str(crewemp.crew.empno),
                        str(crewemp.crew.name),
                        str(crewemp.crew.forenames), str(crewemp.crew.logname),
                        cat, str(crewemp.titlerank.id), "", "",
                        "", "", "", str(crewemp.crew.sex),
                        crewemp.validfrom,
                        crewemp.validfrom,
                        crewemp.validfrom,
                        "1Jan1986 00:00",
                        "1Jan1986 00:00",
                        )
        except modelserver.ReferenceError:
            # crew_employment isn't filtered and contains more crew than the
            # crew table, therefor this exception is expected
            continue
                
        if crewdict.has_key(str(crewemp.crew.id)):
            # append
            print "Found one more row for crew ", str(crewemp.crew.id)
            crewl = crewdict[str(crewemp.crew.id)]
            crewl.append(emptuple)
        else:
            crewdict[str(crewemp.crew.id)] = [emptuple]

    
    crewplan.write("""
/*
This table is exported from CMS database
*/
18
SCrewId,
SEmpno,
SSurname,
SFirstName,
SSignature,
SMainCat,
SMainFunc,
SComplFunc,
SSndFunc,
STelno,
SSkill,
SPOBox,
SGender,
AMainFuncStart,
AComplFuncStart,
ASndFuncStart,
AExperienceDate1,
AExperienceDate2,
""")
    countmulti = 0
    count = 0
    for crewid, emplist in crewdict.items():
        # Iterating over all unique crew id
        number_employments = len(emplist)
        if number_employments > 1:
            Errlog.log("%s %s %s %s, %s" % ("WARNING Received",
                                            number_employments,
                                            "employment records for crewid",
                                            crewid,
                                            "only stores first."))
            countmulti = countmulti + 1
            emp = emplist[0]            
            crewrow1 = '"' + '", "'.join([str(c) for c in emp[0:13]]) + '", '
            crewrow2 = ', '.join([str(c) for c in emp[13:18]])
            crewplan.write(crewrow1 +  crewrow2 + ",\n")
        else:
            count = count + 1
            emp = emplist[0]           
            crewrow1 = '"' + '", "'.join([str(c) for c in emp[0:13]]) + '", '
            crewrow2 = ','.join([str(c) for c in emp[13:18]])
            crewplan.write(crewrow1 +  crewrow2 + ",\n")

    print "nr of multi crew emp records", countmulti
    print "nr of single crew emp records", count
    crewplan.close()
    return


def saveGeneralScenario(test_mode_params = None):
    timer = time_util.Timer("Exporting Optimizer Scenario")
    if not _assert_db():
        return False
    # Tables to export
    lptabs = [
        "ac_employer_set",
        "account_baseline",
        "account_entry",
        "account_set",
        "accumulator_int",
        "accumulator_int_run",
        "accumulator_rel",
        "accumulator_time",
        "ac_qual_map",
        "activity_category",
        "activity_group",
        "activity_group_period",
        "activity_set",
        "activity_set_period",
        "agreement_validity",
        "agmt_group_set",
        "aircraft_type",
        "airport",
        "airport_hotel",
        "annotation_set",
        "apt_requirements",
        "apt_restrictions",
        "apt_restrictions_course",
        "assignment_attr_set",
        "bases",
        "bought_days",
        "bought_days_svs",
        "cabin_recurrent",
        "cabin_training",
        "callout_list",
        "christmas_freedays",
        "ci_exception",
        "coterminals",
        "country",
        "country_req_docs",
        "course_content",
        "course_content_exc",
        "course_participant",
        "crew",
        "crew_address",
        "crew_annotations",
        "crew_attr_set",
        "crew_base_set",
        "crew_complement",
        "crew_contact",
        "crew_contract",
        "crew_contract_set",
        "crew_document",
        "crew_document_set",
        "crew_employment",
        "crew_extra_info",
        "crew_fairness_history",
        "crew_landing",
        "crew_leased",
        "crew_log_acc_mod",
        "crew_need_exception",
        "crew_need_jarops_period",
        "crew_need_service",
        "crew_not_fly_with",
        "crew_notification",
        "crew_passport",
        "crew_position_set",
        "crew_prod_day_change",
        "crew_prod_day_groups",
        "crew_prod_day_sg",
        "crew_qual_acqual",
        "crew_qualification",
        "crew_rank_set",
        "crew_recurrent_set",
        "crew_region_set",
        "crew_rehearsal_rec",
        "crew_rest",
        "crew_restr_acqual",
        "crew_restriction",
        "crew_seniority",
        "crew_training_log",
        "crew_training_need",
        "crew_user_filter",
        "crew_roster_request",
        "exchange_rate",
        "flight_leg",
        "flight_leg_attr",
        "meal_flight_owner",
        "freeday_requirement",
        "freeday_requirement_cc",
        "f36_total",
        "f36_targets",
        "half_freeday_carry_over",
        "hotel",
        "hotel_contract",
        "hotel_transport",
        "leave_actual_rotation",
        "leave_season", 
        "lh_apt_exceptions",
        "lifetime_block_hours",
        "lifus_airport",
        "meal_airport",
        "meal_airport",
        "meal_code",
        "meal_special_code_set",
        "meal_cons_correction",
        "meal_consumption_code",
        "meal_customer",
        "meal_load_correction",
        "meal_opt_out",
        "meal_flight_opt_out",
        "meal_order",
        "meal_order_line",
        "meal_special_order_line",
        "meal_prohibit_flight",
        "meal_supplier",
        "minimum_connect",
        "minimum_connect_pass",
        "new_hire_follow_up",
        "pattern_acts pattern_set",
        "lpc_opc_or_ots_composition",
        "per_diem_compensation",
        "pgt_need",
        "planning_group_set",
        "preferred_hotel",
        "preferred_hotel_exc",
        "property",
        "rave_string_paramset",
        "rest_on_board_cc",
        "rest_on_board_fc",
        "sb_activity_details",
        "sb_daily_lengths",
        "sb_daily_needs",
        "simulator_briefings",
        "simulator_composition",
        "simulator_set",
        "spec_weekends",
    ]

    sptabs = [
        "additional_rest",
        "crew_activity_attr",
        "crew_annotations",
        "crew_attr",
        "crew_flight_duty_attr",
        "crew_ground_duty_attr",
        "ground_task_attr",
        "roster_attr",
        "rule_exception",
        "special_schedules",
    ]
    
    sptabs += _TMP_TABLES_SP.keys() # Dummy export tables, use model to write them!
    lptabs += _TMP_TABLES_LP.keys()
    
    lptabs.sort()
    sptabs.sort()

    lptabs = " ".join(lptabs) #Shell array of string (space separated string)
    sptabs = " ".join(sptabs) #Shell array of string (space separated string)
    os.environ["LP_TABS"] = lptabs
    os.environ["SP_TABS"] = sptabs
    
    return saveScenario(sptabs, lptabs, timer, test_mode_params)


def confirmExport(test_mode_params=None, link=False):
    """Confirmation check"""
    if link:
        confirm_text = 'Export {} scenario to Link Carmdata?'.format(application.get_product_name())
    else:
        confirm_text = 'Export {} scenario to file?'.format(application.get_product_name())

    product = application.get_product_from_ruleset()
    if not product:
        if test_mode_params is None:
            Gui.GuiWarning("Unknown product in Export Scenario, export aborted!")
            return False
        else:
            return True
    elif test_mode_params is None and not cfhExtensions.confirm(confirm_text):
        Errlog.log("ExportScenarios.py:: User cancelled export")
        return False
    else:
        return True


def saveScenario(sptabs, lptabs, timer, test_mode_params = None, link = False):
    """Saves a scenario currently in memory to file"""
    expstr = export_string.get()
    if not expstr:
        Errlog.log("ExportScenarios:: finished. EXPORT_STRING empty.")
        if test_mode_params is None:
            Gui.GuiWarning("Internal error, EXPORT_STRING empty")
        return False

    # Check for open forms. Could be that the user forgot to save any data.
    # All java forms will be closed mercyless later on in this method and this
    # is a softer approach to rescue the absent-minded user.
    try:
        open_forms = StartTableEditor.getOpenForms()
        if test_mode_params is None and len(open_forms) > 0:
            cfhExtensions.show("You need to close all forms before exporting scenario.")
            return False
    except:
        pass

    if not link and not confirmExport(test_mode_params, link):
        return False

    product = application.get_product_from_ruleset()

    # The mercyless way of closing forms.
    # getOpenForms() does not detect Table Editor which will (most of the time)
    # cause Studio to crash after the export is done.
    StartTableEditor.closeAll()

    try:
        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
        ## Save modified plan to db (Link export will never save at this point)
        if not link:
            try:
                if test_mode_params is None:
                    saveResult = Cui.CuiAskAndSavePlans(Cui.gpc_info, 0)
                else:
                    saveResult = Cui.CuiSavePlans(Cui.gpc_info, Cui.CUI_SAVE_DONT_CONFIRM | Cui.CUI_SAVE_SKIP_LP | Cui.CUI_SAVE_SKIP_SP)
            except:
                pass

        ## Get values to use in scenario name

        # Timestamp for operation
        timestamp =  time.strftime("%Y%m%d_%H%M")

        # Crew category
        cat, = R.eval("planning_area.%planning_area_crew_category%")
        if cat == "F":
            cat = "FD"
        elif cat == "C":
            cat = "CC"

        # Crew planning group
        pg, = R.eval("planning_area.%crew_planning_group%")

        # Crew station
        sta, =  R.eval("planning_area.%planning_area_crew_station%")

        #Crew qualification
        qual, =  R.eval("planning_area.%planning_area_crew_qualification%")

        #User
        user = os.environ.get("USER")

        # Scenario name
        crew_plan_name = expstr + "_" + timestamp
        sp_name = "Export_"+ user + "_" + timestamp

        comment_string = '\n'.join((
            "Category: %s" % cat,
            "Planning group: %s" % pg,
            "Station: %s" % sta,
            "Qualification: %s" % qual,
            "Exported scenario on time: %s" % timestamp,
            "Exported by: %s" % user,
        ))
        
        timer.tick("Collecting planning variables")    
        # Set resources with tables to export

        # Load the tables to export into memory if not already loaded
        Errlog.log("ExportScenarios:: pre-loading the tables to export")
        all_tabs = lptabs + " " + sptabs
        # Remove head and/or tail spaces that appears if either sptabs or lptabs
        # is empty
        if all_tabs[-1] == " ":
            all_tabs = all_tabs[:-1]
        elif all_tabs[0] == " ":
             all_tabs = all_tabs[1:]
        print "All tables: " + str(all_tabs)+ ";"
        tab_list = all_tabs.split(" ")
        #Tmp table doesn't need loading
        TM([tab for tab in tab_list if not (tab in _TMP_TABLES_SP.keys() or tab in _TMP_TABLES_LP.keys())])

        # In matador we need to map ground tasks uuid to leg keys
        # in for example simulator attributes
        if not _create_ground_task_map_tmp_table():
            return False
        if not _create_export_data_tmp_table():
            return False
        timer.tick("Preloading tables to model")

        Errlog.log("ExportScenarios:: pre-loading finished.")

        #Save current parameters 
        if test_mode_params is None:
            paramset_name = _get_paramset_name()
            if paramset_name is None:
                return False
        else:
            user = os.environ.get("USER")
            paramset_name = os.path.join(user, "temp_parameters")
            
        Cui.CuiCrcSaveParameterSet(Cui.gpc_info, "", paramset_name)
        
        Errlog.log("ExportScenarios:: before setting resources")
        # These are stored in your personal preferences, but we always override
        # them here
        Crs.CrsSetModuleResource("Database", "ExportEtabSubPlan",
                                 "$(SP_TABS)", "Tables to SpLocal for Scenario")

        Crs.CrsSetModuleResource("Database", "ExportEtabLocalPlan",
                                 "$(LP_TABS)", "Tables to LpLocal for Scenario")

        # Set resources for CREWPLAN
        Crs.CrsSetModuleResource("Database","ExportEtabCrewPlan",
                                 crew_plan_name, "Name of CREW_PLAN for Scenario")
        Errlog.log("ExportScenarios:: after setting resources")
        
        # Write out the CREWPLAN
        writeCREW_PLAN(crew_plan_name)
        timer.tick("Saving crew plan")
        
        #Set database parameter to false
        Cui.CuiCrcSetParameterFromString("fundamental.is_database","False")

        # Find name of current rule set 
        ruleSetPath = Variable.Variable('')
        Cui.CuiCrcGetRulesetName(ruleSetPath)
        (head,ruleSet) = os.path.split(ruleSetPath.value)

        pp_start, = R.eval('fundamental.%pp_start%')
        version = "%04d-%02d" % pp_start.split()[:2]
        if link:  # Link uses full timestamp for lp
            lp = '_'.join((timestamp, user))
        else:
            lp = '_'.join((timestamp.split('_')[0], user))
        lp_name = os.path.join(expstr, version, lp)

        #Save plan
        cs.save_db_to_file = True #Set global variable in carmusr/ConfirmSave.py

        # Clearing areas for export to not display redundant warning messages
        Errlog.log("ExportScenarios:: Clearing all areas")
        Cui.CuiClearAllAreas(Cui.gpc_info)
        Errlog.log("ExportScenarios:: do SaveSubPlan...")
        saveResult = 0  # Initiate so we can use after the try, except block
        
        if test_mode_params is None:
            showPrompt("Save to file plan")
        
        try:
            if test_mode_params is None:
                ok_mode = '' if link else 0  # Link export presses OK automatically
                saveResult = Cui.CuiSavePlansAs( # Use this if exception is wanted
                    {'FORM':'SUB_PLAN_FORM',
                     'SUB_PLAN_HEADER_NAME': sp_name,
                     'LOCAL_PLAN_HEADER_NAME': lp_name,
                     'SUB_PLAN_HEADER_COMMENT': comment_string,
                     'SUB_PLAN_SAVE_ON_FILE': 'On',
                     'FORM':'SUB_PLAN_FORM',
                     'OK':ok_mode},
                    Cui.gpc_info)
            else:            
                # Generate names for 'local plan' and 'sub plan'
                if product == application.PAIRING:
                    product_name = "Autotests_Pairing"
                elif product == application.ROSTERING:
                    product_name = "Autotests_Rostering"
                else:
                    product_name = "Autotests_UnknownProduct"
                    
                user = os.environ.get("USER")
                timestamp =  time.strftime("%Y%m%d_%H%M")    
                lp = user + "_" + timestamp
                
                lp_name = os.path.join(expstr, product_name, lp)
                sp_name = "Export_" + timestamp

                test_mode_params["local_plan"] = lp_name
                test_mode_params["sub_plan"] = sp_name


                # Set assign value
                if "export_assign_value" in test_mode_params and test_mode_params['export_assign_value']:
                    exp_assign_value = test_mode_params['export_assign_value']
                else:
                    exp_assign_value = '0/0/0/0//0/0/0/0//0/0'


                # Set mask value
                if "export_mask_value" in test_mode_params and test_mode_params['export_mask_value']:
                    exp_mask_value = test_mode_params['export_mask_value']
                else:
                    exp_mask_value = '0/0/0/0//*/*/*/*//0/0'
                    
                
                # Set export start and end dates 
                exp_date_start,  = R.eval("fundamental.%plan_start%")
                exp_date_end,  = R.eval("fundamental.%plan_end%")
                
                if "export_max_days" in test_mode_params and exp_date_start.adddays(test_mode_params["export_max_days"]) < exp_date_end:
                    exp_date_start, = R.eval("fundamental.%pp_start%")
                    exp_date_end = exp_date_start.adddays(test_mode_params["export_max_days"])
                
                exp_date_start = AbsDate.AbsDate(exp_date_start).ddmonyyyy()
                exp_date_end = AbsDate.AbsDate(exp_date_end).ddmonyyyy()
                             
                
                # Save plans to file             
                saveResult = Cui.CuiSavePlansAs(
                    {
                    'FORM': 'SUB_PLAN_FORM',
                    'LOCAL_PLAN_HEADER_NAME': lp_name,
                    'SUB_PLAN_HEADER_NAME': sp_name,
                    'SUB_PLAN_HEADER_COMMENT': comment_string,
                    'SUB_PLAN_ASSIGN_VALUE': exp_assign_value,
                    'SUB_PLAN_MASK_VALUE': exp_mask_value,
                    'SUB_PLAN_CC_FILTER_LEG_ON': 'On',
                    'SUB_PLAN_CC_FILTER_AC_ON': 'Off',
                    'SUB_PLAN_CC_FILTER_CRR_ON': 'On',
                    'SUB_PLAN_SAVE_ON_FILE': 'On',
                    'SUB_PLAN_PPP_START': exp_date_start,
                    'SUB_PLAN_PPP_END': exp_date_end,
                    'SUB_PLAN_DEF_FILE': 'DefaultBaseDefinitions',
                    'SUB_PLAN_CONSTR_FILE': 'DefaultBaseConstraints',
                    'OK': ''},
                    Cui.gpc_info)                            

            if product == application.ROSTERING:
                # Copy fairness table
                _copy_fairness_table_to_new_plan()
                
            if test_mode_params is None:
                showPrompt("Saved to file plan") 
            # Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
        except Exception, err:
            cs.save_db_to_file = False
            # Reset global variable in carmusr/ConfirmSave.py
            Errlog.log("ExportScenarios:: aborted while calling CuiSavePlansAs: %s" %
                       err)
            showPrompt("Export aborted")
            
            #If save canceled, reload initial rule set
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, ruleSet)
            Cui.CuiCrcLoadParameterSet(Cui.gpc_info,paramset_name) 
            Errlog.log("ExportScenarios:: Reloaded initial rule set.")
            return False

        timer.tick("Sys save (incl. form)")
        # Reset global variable in carmusr/ConfirmSave.py
        cs.save_db_to_file = False
        timer.display()
    finally:
        showPrompt("Export finished") 
        
    # Prompt if some tables were not copied ok!    
    _check_tables_copied_ok(sptabs, lptabs)

    buf = Variable.Variable()

    Cui.CuiGetSubPlanPath(Cui.gpc_info, buf)
    sp_path = buf.value

    Cui.CuiGetLocalPlanPath(Cui.gpc_info,buf)
    lp_path = buf.value

    Errlog.log("ExportScenarios:: Lp_path: " + lp_path)
    Errlog.log("ExportScenarios:: Sp_path: " + sp_path)

    Errlog.log(
        "ExportScenarios:: Trying to open plan with Cui.CuiOpenSubPlan")
    open_result = Cui.CuiOpenSubPlan(Cui.gpc_info, lp_path, sp_path, 2)

    if open_result is None:
        Errlog.log("ExportScenarios:: Open result is None")
    else:
        Errlog.log("ExportScenarios:: Open result: " + open_result)
    message = "ExportScenarios:: Finished ok, you are now in file mode"

    Errlog.log(message)
    
    if test_mode_params is None and not link:
        cfhExtensions.show(message)

    timer.tick('Check result and open file-based plan')

    return True

def _check_tables_copied_ok(sptabs, lptabs):
    try:
        carmdata = os.environ['CARMDATA']
        localplan_path = Variable.Variable("")
        subplan_path = Variable.Variable("")
        Cui.CuiGetLocalPlanPath(Cui.gpc_info, localplan_path)
        Cui.CuiGetSubPlanPath(Cui.gpc_info, subplan_path)
        
        lp_table_path = os.path.join(carmdata,'LOCAL_PLAN',
                                     localplan_path.value,'etable','LpLocal')
        sp_table_path = os.path.join(carmdata,'LOCAL_PLAN',
                                     subplan_path.value,'etable','SpLocal')
        missing_etabs = []
        
        for lp_table in lptabs.split():
            absolute_file_path = os.path.join(lp_table_path,lp_table)
            if not os.path.exists(absolute_file_path):
                missing_etabs.append('LocalPlan Etable: %s'% lp_table)
                
        for sp_table in sptabs.split():
            absolute_file_path = os.path.join(sp_table_path,sp_table)
            if not os.path.exists(absolute_file_path):
                missing_etabs.append('SubPlan Etable:   %s'% sp_table)
        missing_etabs.sort()
        if missing_etabs:
            Errlog.log('ExportScenarios.py:: _check_tables_copied_ok:\n  Missing etab: %s'%\
                       '\n  Missing etab: '.join(missing_etabs))
            file = None
            tmpfile = None
            try:
                tmpfile = tempfile.mktemp()
                file = open(tmpfile,'w')
                message = 'Missing etables in new plan: \n\n'+'\n'.join(missing_etabs)
                file.write(message)
                file.close()
                cfhExtensions.showFile(tmpfile)
                os.unlink(tmpfile)
            finally:
                if file:
                    file.close()
                if tmpfile:
                    os.unlink(tmpfile)
        else:
            Errlog.log('ExportScenarios.py:: _check_tables_copied_ok: '+\
                       'all etabs copied to new plan! :)')
            
        return len(missing_etabs) == 0

    except Exception, err:
        print 'ExportScenarios.py:: _check_tables_copied_ok: Error %s'%err
        return False
        

def _copy_fairness_table_to_new_plan():

    # Fairness table, get current path
    fairness_table = ""
    try:
        carmdata = os.environ['CARMDATA']
        fairness_table, = R.eval("fairness.%user_table_para%")
        fairness_table = os.path.join(carmdata,'ETABLES',fairness_table+'.etab')
        if not os.path.exists(fairness_table):
            raise Exception("Not found")
    except:
        Errlog.log('ExportScenarios.py:: '+\
                   'Could not find userdefined fairness config table,'+\
                   ' will copy default $CARMUSR/crc/etable/fairness_config.etab')
        try:
            fairness_table = "fairness_config"
            carmusr = os.environ['CARMUSR']
            fairness_table = os.path.join(carmusr,'crc','etable',fairness_table+'.etab')
            if not os.path.exists(fairness_table):
                raise Exception("Not found")
        except:
            Errlog.log('ExportScenarios.py:: '+\
                       'Could not find default fairness config table: '+\
                       '$CARMUSR/crc/etable/fairness_config.etab')
    if not os.path.exists(fairness_table):
        cfhExtensions.show("Unable to copy fairness_config table to new subplan,\n"+\
                           "could not find source table.\nFor more info, see log.")  
        return
    
    # Get new path and copy file
    try:
        carmdata = os.environ['CARMDATA']
        subplan_path = Variable.Variable("")
        Cui.CuiGetSubPlanPath(Cui.gpc_info, subplan_path)
        subplan_path = subplan_path.value
        new_path = os.path.join(carmdata,'LOCAL_PLAN',subplan_path,
                                "etable","SpLocal")
        shutil.copy(fairness_table,new_path)
        
        return
    except Exception, err:
        Errlog.log('ExportScenarios.py:: '+\
                   'Unable to copy fairness_config table to new subplan\n%s'%err)
        cfhExtensions.show("Unable to copy fairness_config table to new subplan")  
        return
    

def _create_ground_task_map_tmp_table():
    class GroundTaskTmpTable(TempTable):
        """
        Temporary class exporting map so ground task attr and crew ground duty attr
        can be used in matador and fileplan studio
        """
        _name = _GND_MAP_TMP_TABLE_NAME
        _keys = [StringColumn('code', 'Code'),
                 TimeColumn('st', 'Start Time'),
                 TimeColumn('et', 'End Time'),
                 StringColumn('adep', 'Airport of departure'),
                 UUIDColumn('uuid', 'uuid'),
                 TimeColumn('udor', 'Udor')]
        _cols = []
        
        def __init__(self):
            TempTable.__init__(self)
            self.populate()

        def create_row(self, task):
            new_row = None
            try:
                code = task.activity.id
                st = task.st
                et = task.et
                adep = task.adep.id
                uuid = task.id
                udor = task.udor
                try:
                    new_row = self[(code,st,et,adep,uuid,udor)]
                except:
                    new_row = self.create((code,st,et,adep,uuid,udor))
            except (modelserver.ReferenceError,
                    modelserver.EntityNotFoundError), err:
                if new_row:
                    new_row.remove() # Leave no empty rows
                self.errors.add(str(err))
            
        def populate(self):
            self.removeAll() #Safe guard
            self.errors = set()
            for gta in TM.ground_task_attr:
                self.create_row(gta.task)
            for cgda in TM.crew_ground_duty_attr:
                self.create_row(cgda.cgd.task)
            for err in self.errors:
                Errlog.log('Export Scenarios::_create_ground_task_map_table %s'%err)
    # Create the tmp table
    try:
        _TMP_TABLES_SP[_GND_MAP_TMP_TABLE_NAME] = GroundTaskTmpTable()
        Errlog.log('ExportScenario::_create_ground_task_map_tmp_table: Mapping table create ok')
        return True
    except Exception, err:
        Errlog.log('ExportScenario::_create_ground_task_map_tmp_table: %s'%err)
        cfhExtensions.show("Unable to write ground task mappings needed in optimizer,\n"+\
                           "Export aborted!\n" +\
                           "For more info, see log.")
        return False


def _create_export_data_tmp_table():
    class ExportDataTmpTable(TempTable):
        """
        Temporary class exporting data so some static times can be accessed in file mode
        """
        _name = _EXPORT_DATA_TMP_TABLE_NAME
        _keys = [StringColumn('key', 'Key'),]

        _cols = [TimeColumn('timevalue', 'Time value'),]
        
        def __init__(self):
            TempTable.__init__(self)
            self.populate()
            
        def populate(self):
            self.removeAll() #Safe guard
            errors = set()
            now, = R.eval('fundamental.%now%')
            nowrow = self.create(("nowtime",))
            nowrow.timevalue = now

    # Create the tmp table
    try:
        _TMP_TABLES_LP[_EXPORT_DATA_TMP_TABLE_NAME] = ExportDataTmpTable()
        Errlog.log('ExportScenario::_create_export_data_tmp_table: Export data table created ok')
        return True
    except Exception, err:
        Errlog.log('ExportScenario::_create_export_data_tmp_table:%s'%err)
        cfhExtensions.show("Unable to write export data needed in file plan,\n"+\
                           "Export aborted!\n" +\
                           "For more info, see log.")
        return False


def _get_paramset_name():
    paramset_name = Variable.Variable("")
    try:
        Cui.CuiCrcGetParameterSetName(paramset_name)
        dialog = ParamsetNameDialog(paramset_name.value)
        dialog()
        paramset_name = dialog.paramset
    except CFC.CancelFormError:
        Errlog.log('ExportScenarios::saveScenario:User cancelled form')
        return None
    except Exception, err:
        paramset_name = "temp_parameters"
    return paramset_name


def _assert_db():
    # Check if in database plan 
    try:
        assert HF.isDBPlan()
    except AssertionError:
        Errlog.log("ExpeortScenarios.py:: Only available in database plan")
        return False
    return True


def dumpEtabsLocalPlan():
    # Each table requied for pairing planning when working with SSIM should
    # be added to this list
    ccp_tables = [
                  'ac_employer_set',
                  'ac_qual_map',
                  'activity_category',
                  'activity_group',
                  'activity_group_period',
                  'activity_set',
                  'activity_set_period',
                  'agreement_validity',
                  'agmt_group_set',
                  'aircraft_type',
                  'airport',
                  'airport_hotel',
                  'bases',
                  'ci_exception',
                  'coterminals',
                  'crew_complement',
                  'crew_need_exception',
                  "crew_need_jarops_period",
                  'crew_need_service',
                  'crew_position_set',
                  'crew_region_set',
                  'exchange_rate',
                  'hotel',
                  'hotel_contract',
                  'hotel_transport',
                  'lifetime_block_hours',
                  'lh_apt_exceptions',
                  'meal_airport',
                  'meal_code',
                  'meal_special_code_set',
                  'meal_cons_correction',
                  'meal_consumption_code',
                  'meal_customer',
                  'meal_flight_owner',
                  'meal_load_correction',
                  'meal_order',
                  'meal_prohibit_flight',
                  'meal_supplier',
                  'minimum_connect',
                  'minimum_connect_pass',
                  'per_diem_compensation',
                  'per_diem_tax',
                  'planning_group_set',
                  'preferred_hotel',
                  'preferred_hotel_exc',
                  'property',
                  'rave_string_paramset',
                  'rest_on_board_cc',
                  'rest_on_board_fc',
                  'sb_activity_details',
                  'sb_daily_lengths',
                  'sb_daily_needs',
                  'spec_weekends',
                  'crew_base_set']
    
    # Each table requiering a filter will have to be added to this list
    # as a tuple with the table name as first value and the filter options
    # as the second (e.g. '<field dname="column_name">&gt; 1234</field>'). 
    ccp_tab_filters = []
    
    lpPath = Variable.Variable("")
    Cui.CuiGetLocalPlanEtabLocalPath(Cui.gpc_info, lpPath)
    lpPath = lpPath.value
    lp_tabs = os.listdir(lpPath)
    message = "You have already exported etables to this local plan.\n" + \
              "Do you want to export the tables again?"
    if lp_tabs and not cfhExtensions.confirm(message):
        return
    
    f = tempfile.NamedTemporaryFile(mode="w+t")
    f.writelines(['<?xml version="1.0" ?>\n<etabdump version="0.7" defmode="ignore">'])
    f.writelines(['<map entity="%s" extension="false"/>' %tab for tab in ccp_tables])
    f.writelines(['<filter entity="%s">%s</filter>' % filter for filter in ccp_tab_filters])
    f.writelines(['</etabdump>'])
    f.flush()

    c = ServiceConfig.ServiceConfig()
    dbUser = c.getPropertyValue("db/user")
    dbUrl = c.getPropertyValue("db/url")

    os.system("$CARMSYS/bin/carmrunner etabdump -c %s -s %s -f %s %s" %(dbUrl, dbUser,
                                                                        f.name, lpPath))


class EXPORT_STRING:
    value = None

    def set(self, s):
        self.value = s

    def get(self):
        return self.value

    def clear(self):
        self.value = None

    def generate(self, area, is_rostering):
        app = ('Pairing', 'Rostering')[bool(is_rostering)]
        self.set("%s_%s" % (app, area.replace(" ","_")))


# singleton
export_string = EXPORT_STRING()


# EOF
