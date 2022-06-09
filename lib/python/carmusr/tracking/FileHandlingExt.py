############################################################

#
# Module containing functions that is to be run before or after opening and
# saving of plans in tracking mode.
#
############################################################
import Variable
import Errlog
import Cui
import Gui
import Cfh
import carmstd.cfhExtensions
import tempfile
from carmstd.carmexception import CarmException
import tm
import Crs
import carmusr.StartFilteredTableEditor as StartFilteredTableEditor
import traceback
import os
import sys
import carmusr.tracking.CrewNotificationFunctions as CrewNotification
import carmusr.AccountHandler
import carmusr.CrewTableHandler as CTH
import os
import carmusr.ConfirmSave as cs
import carmusr.tracking.Publish
import carmusr.tracking.CrewMeal
import AbsTime
import RelTime
import time
import carmusr.DaveFilterTool as DaveFilterTool
import carmensystems.rave.api as R
import carmusr.tracking.OpenPlan as OpenPlan
import carmusr.application as application
import carmensystems.studio.Tracking.OpenPlan
import Variable as V
import carmusr.activity_set as a_set
import __main__
import utils.PerformanceMonitor as pm
import passive.passive_bookings as passive_bookings
import crewinfoserver.data.crew_rosters as crew_rosters
import carmusr.training_attribute_handler
from utils.selctx import BasicContext
from utils.performance import clockme

from modelserver import *


MODULE = 'carmusr.tracking.FileHandlingExt'

SPP_NOT_INVOKED = "not invoked"
SPP_ABORTED = "aborted"
SPP_PERFORMED = "performed"

__savePlanPreProc = SPP_NOT_INVOKED
## filter-tool to setup filters
global filterTool

@clockme
def setDaveLoadFilters():
    print "SET DAVE LOAD FILTERS."
    FUNCTION = '::setDaveLoadFilter::'
    Errlog.log(MODULE+FUNCTION+" Entered")
    global open_plan_handler, filterTool
    pm.time_tic('Getting to setDaveLoadFilter')
    # Find out if we are using AlertMonitor or running external batch save
    SKIP_DIALOG = bool(os.environ.get('CARMUSINGAM')) or \
                  bool(os.environ.get('EXTERNAL_PUBLISH'))
        
    #Set up params in handler
    open_plan_handler.setupPlanPeriod(SKIP_DIALOG)
    open_plan_handler.setupDbPeriod(SKIP_DIALOG,
                                    getDbPeriodStart(open_plan_handler.PERIOD_START))
    if open_plan_handler.Canceled():
        Errlog.log(MODULE+":: User canceled form")
        return 1 # Cancel valued return
    # Lets not measure time spent in dialog
    pm.time_dialog_reset()
    
    ## Set global period variable so flamencobridge can read it
    __main__.PERIOD_START = V.Variable(open_plan_handler.PERIOD_START)
    __main__.PERIOD_END   = V.Variable(open_plan_handler.PERIOD_END)
    __main__.PLAN_CREW_ID   = V.Variable(open_plan_handler.CREW_ID)

    dbPeriodStart = open_plan_handler.DB_PERIOD_START
    dbPeriodEnd = open_plan_handler.DB_PERIOD_END
    crewId = open_plan_handler.CREW_ID
    threeyrsbefstart = open_plan_handler.DB_PERIOD_START - RelTime.RelTime(3*366*24*60)
    oneyrbefstart = open_plan_handler.DB_PERIOD_START - RelTime.RelTime(366*24*60)
    threemonthsbefstart = dbPeriodStart - RelTime.RelTime(3*30*1440)
    threemonthsafterend = dbPeriodEnd + RelTime.RelTime(3*30*1440)
    max_trip_length = 5
    max_number_of_days_with_optional_variant_deadheads_before_trip = 1
    trip_start = dbPeriodStart - RelTime.RelTime(max_trip_length*1440)
    trip_end = dbPeriodEnd + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_start = trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_end = trip_end + RelTime.RelTime(max_trip_length*1440)

    ## filter-tool to setup filters
    filterTool = DaveFilterTool.DaveFilterTool()
    ## Predefine parameter filters so we can use try-catch around each,
    ## list of 3-tuples (name, param, value)

    param_filters = []

    ## Very important to set the period filter!!
    param_filters += [("period", "start", str(dbPeriodStart)[0:9]),
                      ("period", "end", str(dbPeriodEnd)[0:9]),
                      ("period", "start_time", str(dbPeriodStart)),
                      ("period", "end_time", str(dbPeriodEnd)),
                      ("period", "threeyrsbefstart", str(threeyrsbefstart)),
                      ("period", "oneyrbefstart", str(oneyrbefstart)),
                      ("period", "threemonthsbefstart", str(threemonthsbefstart)),
                      ("period", "threemonthsafterend", str(threemonthsafterend)),
                      ("period", "trip_start", str(trip_start)),
                      ("period", "trip_end", str(trip_end)),
                      ("period", "leg_start", str(leg_start)),
                      ("period", "leg_end", str(leg_end))]
    
    
    # Geographical region split

    region_filter = open_plan_handler.get_area_filter_exp() # 3-tuple (region1,region2,acqual)
    param_filters += [("crew_user_filter_active", "start", str(dbPeriodStart)),
                      ("crew_user_filter_active", "end", str(dbPeriodEnd))]
    if region_filter[0] != "ALL":
        param_filters += [("crew_user_filter_cct", "start", str(dbPeriodStart)),
                          ("crew_user_filter_cct", "end", str(dbPeriodEnd)),
                          ("crew_user_filter_cct", "rank_planning_group_1", '_|'+region_filter[0]), #no rank
                          ("crew_user_filter_cct", "rank_planning_group_2", '_|'+region_filter[1]), #no rank
                          ("crew_user_filter_cct", "quals", '%%%s%%' % region_filter[2])]

    # Accumulator filters
    one_yr_bef_start = dbPeriodStart - RelTime.RelTime(366*24*60)
    two_yrs_bef_start = dbPeriodStart - RelTime.RelTime(2*366*24*60)
    seven_yrs_bef_start = dbPeriodStart - RelTime.RelTime(7*366*24*60)
    one_month_bef_start = dbPeriodStart.adddays(-30)
    param_filters += [("accperiod", "start", str(dbPeriodStart)),
                      ("accperiod", "end", str(dbPeriodEnd)),
                      ("accperiod", "oneyrbefstart", str(one_yr_bef_start)),
                      ("accperiod", "twoyrsbefstart", str(two_yrs_bef_start)),
                      ("accperiod", "sevenyrsbefstart", str(seven_yrs_bef_start)),
                      ("accperiod", "onemonthbefstart", str(one_month_bef_start)),
                      ("accperiod", "threemonthsbefstart", str(threemonthsbefstart))]

    # account_entry filters, only use if current baseline is before plan start
    filterTool.set_baseline_filter(open_plan_handler.DB_PERIOD_START,open_plan_handler.DB_PERIOD_END, studio=True)
    
    # Set the filters
    filterTool.set_param_filters(param_filters)
    if crewId:
        filterTool.set_param_filter("crew_filter", "crew", crewId)
    
    filterTool.set_filter('studio_filter')
    
    R.param("planning_area.%filter_company_p%").setvalue(open_plan_handler.get_plan_area())
    pm.time_tic("Setup of filter")

    return 0

@clockme
def openPlanPreProc():
    """
    Running functions before the CARMSYS function for
    opening a plan has been used.
    """

    if os.environ['CARMSYSTEMNAME'].endswith('MIRROR') and bool(os.environ.get('CARMUSINGAM')):
        Gui.GuiWarning("This is a Production-Mirror\nDo not use unless you have written instruction to do so.")

    global open_plan_handler
    FUNCTION = '::openPlanPreProc::'
    Errlog.log(MODULE+FUNCTION+" Entered")
    # Create filter form
    open_plan_handler = OpenPlan.OpenPlanParameterHandler()                               

    pm.time_reset('Open Plan Times')
    # Loading rule set and parameter changes.
    # The rule set is loaded prior to data load so
    # useRaveDefinedTrips works.
    Errlog.log(MODULE+":: Setting ruleset before open of plan")
    try:
        Cui.CuiCrcUnloadRuleset(Cui.gpc_info)
    except:
        pass # CARMSYS doesn't unload rave ruleset before trying to open plan
             # which caused unnecessary table reload on reopening
    ruleset = open_plan_handler.getProperty("Tracker/rule_set")
    Errlog.log(MODULE+":: Used ruleset:%s"%ruleset)
    Cui.CuiCrcLoadRuleset(Cui.gpc_info,
                          ruleset,
                          1)
    Cui.CuiCrcLoadParameterSet(Cui.gpc_info,
                               open_plan_handler.getProperty("Tracker/parameter_file"),
                               1)
    pm.time_tic("Loading parameters and rule set")
    if os.environ.get("CARMUSR_PERFORMANCE_TWEAK_TEST"):
        print "PERFORMANCE TRACE START"
        print '\n'.join('%-20s= %s' % x for x in sorted(os.environ.items()))

    return

@clockme
def openPlanPostProc():
    """
    Running functions after the CARMSYS function for
    opening a plan has been used.
    """
    pm.time_tic("CARMSYS Loading time")
    FUNCTION = '::openPlanPostProc::'
    Errlog.log(MODULE+FUNCTION+" Entered")
    tm.TM.showSelections()
    # We shall use tm.reset() with care. It is not supposed to recreate
    # a new TableManager instance. The operation shall just make sure that
    # we have a TM that will connect to the latest TableManager instance
    # when we start to use it
    
    global open_plan_handler
    #TM.showSelections()
    # To speed up the java forms, the JVM is prestarted
    try:
        singleJVM = open_plan_handler.getResource("config","SingleJVMLauncher")
        if singleJVM:
            StartFilteredTableEditor.launch(['-o'])
    except:
        Errlog.log(MODULE+"::openPlanPostProc:: Couldn't pre-start table editor:")
        traceback.print_exc()

    pm.time_tic("Starting JVM")

    # For studio to be able to detect changes, all tables edited via studio needs
    # to be loaded from the database. This also speeds up the usage of the interface.
    __preload_model_tables()
    pm.time_tic("Preloading tables to model")

    try:
        # Creating temporary (memory) table used for informed Rudob.
        import carmusr.tracking.informedtemptable
        carmusr.tracking.informedtemptable.init()
    except Exception, e:
        Errlog.log(MODULE+"::openPlanPostProc:: could not create temporary table.")
        traceback.print_exc()
        
    pm.time_tic("Create informed temptable")

    try:
        Errlog.log(MODULE+":: Preloading tables")
        rave_preload = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, "PLAN",
                                      "studio_process.%preload_rave%")
    except:
        Errlog.log(MODULE+"::openPlanPostProc:: Failed to preload accumulator tables.")
        traceback.print_exc()

    pm.time_tic("Preloading tables to rave")

    # Set the parameter filter_company_p to enable the filtering in the Trip window.
    R.param("planning_area.%filter_company_p%").setvalue(open_plan_handler.get_plan_area())

    # Set parameters for what has actually been loaded.
    preDBPeriod = getDbPeriodStart(open_plan_handler.PERIOD_START)
    R.param("fundamental.%extra_days_loaded_beginning%").setvalue(int(preDBPeriod))
    Errlog.log("%s%s loaded_data_period_start: %s" % (MODULE,FUNCTION, AbsTime.AbsTime(R.eval('fundamental.%loaded_data_period_start%')[0])))
    Errlog.log("%s%s loaded_data_period_end: %s" % (MODULE,FUNCTION, AbsTime.AbsTime(R.eval('fundamental.%loaded_data_period_end%')[0])))

    # Set parameters for what has actually been loaded.
    postDBPeriod = Crs.CrsGetAppModuleResource("gpc", Crs.CrsSearchAppDef, "config",
                                               Crs.CrsSearchModuleDef, "DataPeriodDbPost")
    R.param("fundamental.%extra_days_loaded_end%").setvalue(int(postDBPeriod))
    
    # Set parameter for rave awareness of which context it's operating in.
    rave_context_publish_type = BasicContext().publishType or "LATEST"
    Errlog.log(MODULE+"::openPlanPostProc:: Rave evaluation in %s revison" % rave_context_publish_type)
    R.param("fundamental.%rave_evaluation_publish_type%").setvalue(rave_context_publish_type)

    # Set subplan as not modified
    Cui.CuiSetSubPlanModified(Cui.gpc_info,0)

    a_set.run()

    pm.time_tic("Copying activity codes to temporary Etable")
    # Set the loaded state as start state for the "super undo" feature.
    # This should always be the last call in the open plan operation.
    #setStartUndoState()
    
    # Set studio header
    title = os.environ['SK_APP'] + '  ' + \
            str(open_plan_handler.PERIOD_START)[0:9] + ' - ' + str(open_plan_handler.PERIOD_END)[0:9] + '   ' + \
            os.environ['CARMROLE'] + '   ' + \
            os.environ['USER']
    Gui.GuiSetTitle(title)

    pm.time_log()
    
    # Set parameter application name
    Cui.CuiCrcSetParameterFromString("fundamental.active_application", os.environ['SK_APP'])

    tabs = str(tm.TM)
    tabs = [x.strip() for x in tabs[tabs.index('tables="')+8:tabs.index('">')].split(',')]
    print "Number of loaded model tables:",len(tabs)
    for tab in tabs:
        print "   %-30s: %d" % (tab, len(getattr(tm.TM, tab)))
    if os.environ.get("CARMUSR_PERFORMANCE_TWEAK_TEST"):
        sys.exit(0)

@clockme
def __preload_model_tables():
    tm.reset()    
    TM = tm.TM
    model_tables = [
        "accumulator_int_run",
        "account_entry",
        "agmt_group_set",
        "alert_time_exception",
        "bases",
        "bought_days",
        "ci_frozen",
        "cio_event",
        "cio_status",
        "country",
        "country_req_docs",
        "course_type",
        "crew_address",
        "crew_activity_attr",
        "crew_annotations",
        "crew_attr",
        "crew_base_break",
        "crew_contact",
        "crew_contract",
        "crew_contract_valid",
        "crew_document",
        "crew_employment",
        "crew_ext_publication",
        "crew_flight_duty_attr",
        "crew_ground_duty_attr",
        "crew_log_acc_mod",
        "crew_need_exception",
        "crew_not_fly_with",
        "crew_notification",
        "crew_publish_info",
        "crew_qual_acqual",
        "crew_qualification",
        "crew_rehearsal_rec",
        "crew_rest",
        "crew_restr_acqual",
        "crew_restriction",
        "crew_seniority",
        "crew_training_log",
        "crew_training_need",
        "crew_training_t_set",
        "do_not_publish",
        "job_parameter",
        "roster_attr",
        "flight_leg_attr",
        "ground_task_attr",
        "handover_message",
        "hotel_booking",
        "informed",
        "mcl",
        "meal_special_code_set",
        "notification_message",
        "passive_booking",
        "published_standbys",
        "rule_exception",
        "sas_40_1_cbr",
        "spec_local_trans",
        "special_schedules",
        "transport_booking"
    ]

    # These tables are not used by studio and are not required to be in the model
    # however RAVE will consume alot of database resources trying to load and
    # refresh this data, to keep up with the model. It is more efficient speed and
    # database load time wise to let the model handle these tables
    rave_tables = [
        "ac_employer_set",
        "ac_qual_map",
        "account_baseline",
        "activity_group_period",
        "activity_set",
        "activity_set_period",
        "additional_rest",
        "agreement_validity",
        "airport_hulk",
        "aircraft_type",
        "apt_restrictions",
        "apt_restrictions_course",
        "apt_requirements",
        "cabin_recurrent",
        "cabin_training",
        "ci_exception",
        "course_block",
        "course_content",
        "course_content_exc",
        "course_participant",
        "coterminals",
        "crew_contract_set",
        "crew_complement",
        "crew_extra_info",
        "crew_landing",
        "crew_leased",
        "crew_need_jarops",
        "crew_need_jarops_period",
        "crew_need_service",
        "crew_passport",
        "crew_position_set",
        "crew_prod_day_change",
        "crew_prod_day_sg",
        "crew_recurrent_set",
        "crew_roster_request",
        "crew_user_filter",
        "meal_airport",
        "meal_flight_owner",
        "flyover",
        "freeday_requirement",
        "freeday_requirement_cc",
        "gnd_key_mappings",
        "hotel_contract",
        "hotel_transport",
        "leave_account",
        "lifetime_block_hours",
        "lh_apt_exceptions",
        "meal_opt_out",
        "meal_flight_opt_out",
        "meal_customer",
        "meal_airport",
        "meal_cons_correction",
        "meal_prohibit_flight",
        "meal_supplier",
        "minimum_connect",
        "minimum_connect_pass",
        "new_hire_follow_up",
        "pc_opc_composition",
        "per_diem_compensation",
        "per_diem_tax",
        "preferred_hotel_exc",
        "preferred_hotel",
        "privately_traded_days",
        "property",
        "sb_activity_details",
        "simulator_briefings",
        "simulator_set",
        "spec_weekends",
        "pattern_acts",
        "pc_opc_composition",
        "pgt_need",
        "privately_traded_days_date",
        "rave_string_paramset",
        "rest_on_board_cc",
        "rest_on_board_fc",
        "salary_article",
        "simulator_briefings",
        "simulator_composition",
        "simulator_set",
        "tmp_inform_table",
        ]
    needed_tables = model_tables[:]
    needed_tables.extend(rave_tables)

    try:
        tables_to_load = [e.entity for e in TM._entity if (e.entity in
                                                           needed_tables)]

        # Table name check:
        error_tables = [t for t in needed_tables if t not in tables_to_load]
        if error_tables:
            Errlog.log(MODULE+"::Table name errors: %s" % error_tables)
            
        
        global filterTool
        try:
            if filterTool:
                filterTool.check_tables_for_filter_use(tables_to_load)
        except NameError:
            print MODULE+"::openPlanPostProc::Unable to find filterTool"
            pass
        
        TM(*tables_to_load)
       
        
    except:
        Errlog.log(MODULE+"::openPlanPostProc:: failed to init tables.")
        traceback.print_exc()


@clockme
def savePlanPreProc():
    """
    Running functions before the CARMSYS function for
    saving a plan will be used.
    """
    global __savePlanPreProc
    FUNCTION = "::savePlanPreProc::"
    Errlog.log(MODULE+FUNCTION+" Entered")
    
    # 1) Confirm the Save
    if not cs.confirmSave():
        Errlog.log(MODULE+"::savePlanPreProc:: Save aborted")
        __savePreProcPerformed = SPP_ABORTED
        return 1

    __savePlanPreProc = SPP_PERFORMED
    ## Reset timer! Dont remove it, otherwise save-time statistics will be very wrong!
    pm.time_reset('Save Plan Times')
    
    try:
        Cui.CuiMakeAssignmentsPersonal(Cui.gpc_info, 0)
        pm.time_tic("Function for making non personal assignments personal")
    except Exception, e:
        Errlog.log(MODULE+FUNCTION + "Function for making non personal assignments personal failed")

    # 2) Prepare job for passive bookings.
    #    NOTE: the job must be submitted AFTER save, the job must not run
    #    before the actual commit.
    try:
        passive_bookings.prepare()
        pm.time_tic("Prepare passive bookings")
    except Exception, e:
        Errlog.log(MODULE + FUNCTION + "failed to prepare passive bookings update job " + str(e))


    try:
        crew_rosters.prepare()
        pm.time_tic("Prepare crew rosters to CrewInfoServer")
    except Exception, e:
        Errlog.log(MODULE + FUNCTION + "failed to prepare crew rosters to CrewInfoServer update job " + str(e))


    # 3) update training log here
    try:
        CTH.update_ctl_changed_crew()
    except Exception, e:
        Errlog.log(MODULE+FUNCTION+" Error at \
        crew_training_log update" + str(e))
    pm.time_tic("Training log run")
    # 4) update crew leave accounts here
    try:
        carmusr.AccountHandler.updateChangedCrew()
    except:
        Errlog.log(MODULE+FUNCTION+" error at AccountHandler update")
    pm.time_tic("Accounthandler run")
    # 5) Prepare for Automatic Assignment Notifications.
    try:
        dnp_period_dict = {}
        carmusr.tracking.Publish.publishPreSave(dnp_period_dict)
    except:
        traceback.print_exc()
        Errlog.log(MODULE+FUNCTION+" Error in Publish pre-processing")
    pm.time_tic("Publish pre-processing")
    # 6) cleaning attribute tables
    try:
        result = CTH.clean_attributes_tables(dnp_period_dict=dnp_period_dict)
        Errlog.log(MODULE+FUNCTION+ result)
    except:
        Errlog.log(MODULE+FUNCTION+" Error at attributes tables cleaning")
        traceback.print_exc()
    pm.time_tic("Cleaning attributes tables")
    # 7) update special training companions
    try:
        carmusr.training_attribute_handler.update_special_training_companions()
    except:
        Errlog.log(MODULE+FUNCTION + "Error at special training companions update")
        traceback.print_exc()
    pm.time_tic("Updating special training companions")    
    # 8) Update crew meal information
    try:
        carmusr.tracking.CrewMeal.update_meals()
    except:
        traceback.print_exc()
        Errlog.log(MODULE+FUNCTION+" Error in Update crew meals")
    pm.time_tic("Update crew meals")
    #clearUndoState()

@clockme
def savePlanPostProc():
    """
    Running functions after the CARMSYS function for
    saving a plan has been used.
    """
    global __savePlanPreProc
    FUNCTION = '::savePlanPostProc::'
    Errlog.log(MODULE+FUNCTION+" Entered")
    try:
        if __savePlanPreProc != SPP_PERFORMED:
            m = MODULE+FUNCTION+"invoked, " \
                "but savePlanPreProc was %s. ABORT." % __savePlanPreProc
            print "!!!!!", m, "!!!!!"
            Errlog.log(m)
            return -1

        pm.time_tic("Actual (sys) save")
            
        Errlog.log(MODULE+FUNCTION+" Performing post-save operations")

        carmusr.tracking.Publish.publishPostSave()
        pm.time_tic("Publish post-processing")
        try:
            passive_bookings.submit()
            pm.time_tic("Submit passive bookings update job")
        except Exception, e:
            Gui.GuiWarning(MODULE + FUNCTION + "failed to submit passive bookings update job " + str(e))
            Errlog.log(MODULE + FUNCTION + "failed to submit passive bookings update job " + str(e))


        try:
            crew_rosters.submit()
            pm.time_tic("Submit roster update to CrewInfoServer job")
        except Exception, e:
            Gui.GuiWarning(MODULE + FUNCTION + "failed to submit roster update to CrewInfoServer job " + str(e))
            Errlog.log(MODULE + FUNCTION + "failed to submit roster update to CrewInfoServer job " + str(e))

        pm.time_log()
    finally:
        __savePlanPreProc = SPP_NOT_INVOKED

    #setStartUndoState()

@clockme
def getDbPeriodStart(startTime):
    """
    DataDbPeriodPreFunc calls this function to calculate the DbPeriodStart
    This function takes an integer time as argument and return the number of days
    before the planningperiod start that should be loaded. Default the SYS function
    returns the value of the resource DataDbPeriodPre.
    """
    
    
    FUNCTION = "::getDbPeriodStart::"
    Errlog.log(MODULE+FUNCTION+" Entered")
    CARMUSINGAM = bool(os.environ.get('CARMUSINGAM'))
    dbPrePeriod = int(Crs.CrsGetModuleResource("config",Crs.CrsSearchAppDef,"DataPeriodDbPre"))
    try:
        if CARMUSINGAM and int(startTime) > -1:
            dayOfMonth = int(AbsTime.AbsTime(startTime).ddmonyyyy(True)[0:2])
            if dayOfMonth > dbPrePeriod:
                return dayOfMonth
    except:
        pass
    return dbPrePeriod


def setStartUndoState():
    """
    Set the start state to be used for superUndo.

    """

    Cui.CuiScenarioHandlerCtrl(Cui.CUI_SCENARIO_CREATE)

def clearUndoState():
    """
    Update the state for super undo to current state.

    """

    Cui.CuiScenarioHandlerCtrl(Cui.CUI_SCENARIO_APPLY)

def undoAndRefresh():
    """
    Undo all changes to the start state and refresh from the database.

    """

    Cui.CuiScenarioHandlerCtrl(Cui.CUI_SCENARIO_UNDO)
    Cui.CuiClearAllAreas(Cui.gpc_info)
    carmensystems.studio.Tracking.OpenPlan.refreshGui()
