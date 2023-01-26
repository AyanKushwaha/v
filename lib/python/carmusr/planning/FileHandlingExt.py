############################################################

#
# Module containing callback functions that are called by
# Studio before/after opening/saving plans.
# This module contains definitions active in planning-mode
#
############################################################

import os
import traceback
import tempfile
import time

import Errlog
import Cui
import Gui
import Crs
import Cfh
import Variable
import tm
import carmusr.StartFilteredTableEditor as StartFilteredTableEditor
import AbsTime
from AbsTime import PREV_VALID_DAY
import AbsDate
import RelTime
import carmusr.DaveFilterTool as DaveFilterTool
import carmstd.cfhExtensions
import carmusr.AccountHandler
import carmusr.HelperFunctions as HF
import carmusr.application as application
import carmusr.CrewTableHandler as CTH
import utils.time_util as time_util
import utils.TimeServerUtils as TimeServerUtils
import utils.CfhFormClasses as CFC
import carmensystems.rave.api as R

import carmusr.ConfirmSave as cs
import carmusr.planning.PlanningAreas as pa
import carmusr.modcrew as modcrew
import carmusr.activity_set as a_set
import carmusr.training_attribute_handler

import __main__

import utils.PerformanceMonitor as pm

from carmusr.planning.ExportScenarios import export_string
# This variable is used for passing information between load filter
# and the post load function

MODULE = 'carmusr.planning.FileHandlingExt'
post_load_actions = {}


##################################################################
# Class and functions for dave filter dialog
#
###########################################################################

def _testForm(p='PRE'):
    try:
        if p=='PRE':
            form = LoadFilterDialogPrePlanning()
        else:
            form = LoadFilterDialogPlanning()
        values = form()
        for val in values:
            print type(val),str(val)
    except CFC.CancelFormError, err:
        print err



# Form base class
class LoadFilterDialog(CFC.BasicCfhForm):
    """
    Base class for filter form
    """
    rostering = application.PRODUCT_OPTIONS[application.ROSTERING]
    pairing = application.PRODUCT_OPTIONS[application.PAIRING]
    def __init__(self,title='Open plan:'):
        CFC.BasicCfhForm.__init__(self,title)
        self._delta_y = 13
        default_start, default_end = self.get_default_dates()
        self.add_date_combo(0,0,'period_start','Period Start:',default_start)
        self.add_date_combo(1,0,'period_end','Period End:',default_end)
        
        planning_areas = pa.planning_areas.keys()
        planning_areas.sort()
        self.add_filter_combo(3,0,'planning_area','Planning Area:',
                              'ALL',planning_areas)

    
    def get_default_dates(self):
        return ('1Jan1901','31Dec2035')
    
    def check_ok_action(self):
        # provoke check, some small issue with components own checking
        message = self.period_start_field.check(self.period_start_field.getValue()) or \
                  self.period_end_field.check(self.period_end_field.getValue())
        if message:
            return message
        try:
            assert self.period_start < self.period_end
        except:
            return "Period start must be smaller then period end"
        return ""    
    
    @property
    def period_start(self):
        return AbsTime.AbsTime(self.period_start_field.getValue())
    @property
    def period_end(self):
        #Entered as date in form, convert to non-inclusive abstime
        return AbsTime.AbsTime(self.period_end_field.getValue()).adddays(1)
    @property
    def planning_area(self):
        return self.planning_area_field.getValue()
    @property
    def is_rostering(self):
        raise NotImplementedError
    @property
    def product(self):
        return NotImplementedError  
    @property
    def param_set(self):
        return NotImplementedError 
    

# PrePlanning    
class LoadFilterDialogPrePlanning(LoadFilterDialog):
    """
    Filter form for PreStudio Application
    """
    def get_default_dates(self):
        now = TimeServerUtils.now_AbsTime().day_floor()
        self.now_time = now
        # Suggest a default start date
        defaultstart = AbsTime.AbsTime(now)
        publish_date = defaultstart.month_floor().adddays(15)
        if defaultstart >= publish_date:
            defaultstart = defaultstart.addmonths(1, PREV_VALID_DAY)
        else:
            defaultstart = defaultstart.adddays(1)
        defaultstart = defaultstart.month_ceil()
        # Suggest a default end date
        defaultend = AbsTime.AbsTime(defaultstart)
        defaultend = defaultend.addmonths(6,PREV_VALID_DAY).adddays(-1)

        return (defaultstart.ddmonyyyy(),defaultend.ddmonyyyy())
    
    def check_ok_action(self):
        if os.environ['CARMSYSTEMNAME'].endswith('MIRROR'):
            Gui.GuiWarning("This is a Production-Mirror\nDo not use unless you have written instruction to do so.")

        message = LoadFilterDialog.check_ok_action(self)
        if message:
            return message
        one_hour = RelTime.RelTime('24:00')
        historic_days = future_days  = 0 #init
        if self.period_start < self.now_time:
            # not too long historic data (3 months * 31 days = 93)
            historic_days = int((min(self.now_time,self.period_end)-self.period_start)/one_hour)
            if historic_days > 93:
                return "Max 3 months historic data"
            
        if self.period_end > self.now_time:
            # Not too much future data (12 months * 31 days ~= 370)
            future_days = int((self.period_end-max(self.now_time,self.period_start))/one_hour)
            if future_days > 370:
                return "Max 12 months future data"
        if future_days > 0 and  historic_days > 60: #Max one old month if opening future rosters
            return "Max 1 month historic data when opening future period"
    @property    
    def is_rostering(self):
        return True #Rostering in preplanning
    @property
    def product(self):
        return LoadFilterDialog.rostering  #Rostering in preplanning
    @property
    def param_set(self):
        return None  # No paramset option in pre
#Planning
class LoadFilterDialogPlanning(LoadFilterDialog):
    """
    Filter Form for Planning Area
    """
    def __init__(self, title='Open Plan'):
        
        LoadFilterDialog.__init__(self, title)
        
        #self.add_toggle_combo(5,0,'load_crew','Load Crew:',True)
        self.add_filter_combo(5,0,'product','Product:',
                              LoadFilterDialog.rostering.title(),
                              [LoadFilterDialog.rostering.title(),
                               LoadFilterDialog.pairing.title()], upper=False)
        dir = os.path.join(os.path.expandvars("${CARMUSR}"), "crc", "parameters",
                           os.path.expandvars("${USER}"))
        dirlist = []
        if os.path.exists(dir):
            dirlist = [e for e in os.listdir(dir) if e[0]<>"."]
        dirlist.append('NONE')
        self.add_filter_combo(6,0,'param_set','Apply parameters:','NONE',dirlist, upper=False)
    

    def get_default_dates(self):
        now = TimeServerUtils.now_AbsTime().day_floor()
        # Suggest a default start date
        defaultstart = AbsTime.AbsTime(now)
        defaultstart = defaultstart.adddays(-15)
        defaultstart = defaultstart.month_floor()
        defaultstart = defaultstart.addmonths(2,PREV_VALID_DAY)
        # Default end date is 1Jan1986 which will translate to period
        # of start + 1 month if end < start
        defaultend = AbsTime.AbsTime(defaultstart.addmonths(1,PREV_VALID_DAY)).adddays(-1)
        return (defaultstart.ddmonyyyy(),defaultend.ddmonyyyy())
        
    # Overload since used by planning
    @property
    def is_rostering(self):
        return self.product == LoadFilterDialog.rostering 
    @property
    def product(self):
        return self.product_field.valof().lower()
    @property
    def param_set(self):
        setting = self.param_set_field.valof()
        if setting == 'NONE':
            return None
        return setting


class PlanningDeamonFilterDialog(object):
    """
    Python Singleton class that is a Mimic of a LoadFilterDialog
    """
    __instance = None

    class Singleton:
        """  The actual class that will have only one instance """
        def __init__(self):
            self.period_start = None
            self.period_end = None
            self.planning_area = None
            self.is_rostering = True
            self.product = LoadFilterDialog.rostering
            self.param_set = None

    def __init__(self):
        if PlanningDeamonFilterDialog.__instance is None:
            PlanningDeamonFilterDialog.__instance = PlanningDeamonFilterDialog.Singleton()
        self.__dict__['_EventHandler_instance'] = PlanningDeamonFilterDialog.__instance

    def __call__(self):
        pass
    
    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


##################################################################        


# The set database filter callback. Defined in resource gpc.Database.loadfilter
def setDaveLoadFilters():
    """
    This function is called by studio whenever a database plan is opened. It asks
    the user for some input, sets load filters. It also sets a number of
    post-load actions that will be applied by the post-load function.
    """
    global load_filter_dialog, post_load_actions
    FUNCTION = "::setDaveLoadFilters:: "
    Errlog.log(MODULE +FUNCTION +"Entering setDaveLoadFilters")
    # Opening a dialog to the user
    
    prestudio = application.isPreplanning
    # This function is used both by pre and planning
    load_filter_dialog=None 
    if application.isPreplanning:
        load_filter_dialog = LoadFilterDialogPrePlanning()
        Errlog.log(MODULE +FUNCTION + "initializing pre dialog")
    elif application.isPlanning and application.isBatchDeamon:
        load_filter_dialog = PlanningDeamonFilterDialog()
        Errlog.log(MODULE +FUNCTION + "initializing deamon planning dialog")
    else:
        load_filter_dialog = LoadFilterDialogPlanning()
        Errlog.log(MODULE +FUNCTION + "initializing planning dialog")

    try:
        load_filter_dialog() # Show form
    except Exception, err:
        Errlog.log(MODULE +FUNCTION + str(err))
        return 1
    
    pm.time_dialog_reset()
    filterTool = DaveFilterTool.DaveFilterTool()

    # Setup  Filters:
    param_filters = []
    
    period_end = load_filter_dialog.period_end
    period_start = load_filter_dialog.period_start

    # Periods
    if prestudio:
        ext_period_start = period_start #No extended periods in pre
        ext_period_end = period_end - RelTime.RelTime(1)
    else:
        if load_filter_dialog.is_rostering:
            ext_period_start = period_start.addmonths(-1,PREV_VALID_DAY)
            ext_period_end = max(period_end.addmonths(1,AbsTime.PREV_VALID_DAY).month_floor(),
                                 period_end.adddays(10)) - RelTime.RelTime(1)
            
        else:
            ext_period_start = period_start.adddays(-5)
            ext_period_end = period_end.adddays(10) - RelTime.RelTime(1)

    # Set studio period
    __main__.PERIOD_START = Variable.Variable(ext_period_start)
    __main__.PERIOD_END   = Variable.Variable(ext_period_end)

    threeyrsbefstart = ext_period_start - RelTime.RelTime(3*366*24*60)
    oneyrbefstart = ext_period_start - RelTime.RelTime(366*24*60)
    threemonthsbefstart = ext_period_start - RelTime.RelTime(3*30*1440)
    threemonthsafterend = ext_period_end + RelTime.RelTime(3*30*1440)
    max_trip_length = 5
    max_number_of_days_with_optional_variant_deadheads_before_trip = 1
    trip_start = ext_period_start - RelTime.RelTime(max_trip_length*1440)
    trip_end = ext_period_end + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_start = trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_end = trip_end + RelTime.RelTime(max_trip_length*1440)

    # Set the period filter
    param_filters += [("period", "start", str(ext_period_start)[0:9]),
                      ("period", "end", str(ext_period_end)[0:9]),
                      ("period", "start_time", str(ext_period_start)),
                      ("period", "end_time", str(ext_period_end)),
                      ("period", "threeyrsbefstart", str(threeyrsbefstart)),
                      ("period", "oneyrbefstart", str(oneyrbefstart)),
                      ("period", "threemonthsbefstart", str(threemonthsbefstart)),
                      ("period", "threemonthsafterend", str(threemonthsafterend)),
                      ("period", "trip_start", str(trip_start)),
                      ("period", "trip_end", str(trip_end)),
                      ("period", "leg_start", str(leg_start)),
                      ("period", "leg_end", str(leg_end))]

    # Accumulators
    one_yr_bef_start = period_start - RelTime.RelTime(366*24*60)
    two_yrs_bef_start = period_start - RelTime.RelTime(2*366*24*60)
    seven_yrs_bef_start = period_start - RelTime.RelTime(7*366*24*60)
    
    one_month_bef_start = period_start.adddays(-30)
    
    param_filters += [("accperiod", "start", str(period_start)),
                      ("accperiod", "end", str(ext_period_end)),
                      ("accperiod","oneyrbefstart", str(one_yr_bef_start)),
                      ("accperiod","twoyrsbefstart", str(two_yrs_bef_start)),
                      ("accperiod","sevenyrsbefstart", str(seven_yrs_bef_start)),
                      ("accperiod", "onemonthbefstart", str(one_month_bef_start)),
                      ("accperiod", "threemonthsbefstart", str(threemonthsbefstart))]
             
    # Crew active
    #param_filters += [("crewactive", "start", str(ext_period_start)[0:9])]
    
    # Apply the planning area crew filters
    filter_dict = pa.planning_areas[load_filter_dialog.planning_area][0]

    for filter1, filter2, filter3 in pa.create_filters(filter_dict):

        if filter3 == "%start":
            filter3 = str(ext_period_start)
        if filter3 == "%end":
            filter3 = str(ext_period_end)
        param_filters += [(filter1, filter2, filter3)]


    # account_entry filters, only use if current baseline is before plan
    # start
    baseline = filterTool.set_baseline_filter(ext_period_start, ext_period_end, studio=True)
    # Set filters using filterTool
    filterTool.set_param_filters(param_filters)

    filterTool.set_filter('studio_filter')
    
    # End of filter setup
    # Reset the post load actions
    post_load_actions = {}
    if prestudio:
        _RULESET = "PreRostering"
    else:
        export_string.generate(load_filter_dialog.planning_area, load_filter_dialog.is_rostering)
        Errlog.log(MODULE + FUNCTION + "Generated export string: " + export_string.get())

        flightdeck = "FD" in load_filter_dialog.planning_area or \
                     load_filter_dialog.planning_area == 'ALL'
        
        # Set ruleset before load to use parallel load of accumulators
        if load_filter_dialog.is_rostering:
            _RULESET = ["Rostering_CC","Rostering_FC"][flightdeck]
        else:
            _RULESET= ["Pairing_CC","Pairing_FC"][flightdeck]
            
        if flightdeck:
            post_load_actions["ASSIGN"] = "1/1/1/0//0/0/0/0//1/1"
            post_load_actions["MASK"]   = "0/0/0/0//*/*/*/*//0/0"
        else:
            post_load_actions["ASSIGN"] = "0/0/0/0//1/1/1/0//1/0"
            post_load_actions["MASK"]   = "*/*/*/*//0/0/0/0//0/0"
        # Pairing specific details
        if not load_filter_dialog.is_rostering:
             # No assign vector in pairing
            post_load_actions["ASSIGN"] = "0/0/0/0//0/0/0/0//0/0"
           
            
        post_load_actions["PARAMETERS"] = load_filter_dialog.param_set
        
    # call set ruleset for pre and rostering
    if load_filter_dialog.is_rostering:
        __set_ruleset(_RULESET)
    post_load_actions["RULESET"] = _RULESET
    post_load_actions["PLANNINGAREA"] = pa.planning_areas[load_filter_dialog.planning_area][1]
    post_load_actions["PP"] = {'fundamental.%start_para%':str(period_start),
                               'fundamental.%end_para%':str(period_end)}

    Errlog.log(MODULE +FUNCTION+"leaving setDaveLoadFilters")
    pm.time_tic("Setting dave filters")

    return 0
##########################################################################

def openPlanPreProc():
    """
    Running functions before the CARMSYS function for
    opening a plan has been used.
    """

    if os.environ['CARMSYSTEMNAME'].endswith('MIRROR'):
        Gui.GuiWarning("This is a Production-Mirror\nDo not use unless you have written instruction to do so.")

    global post_load_actions
    Errlog.log(MODULE+'::OpenPlanPreProc: Entered')
    pm.time_reset('Open Plan Times')
    Cui.CuiCrcUnloadRuleset(Cui.gpc_info)
    post_load_actions = {}
    export_string.clear()
    pm.time_tic("openPlanPreProc")

    return 0

def openPlanPostProc():
    """
    Running functions after the CARMSYS function for
    opening a plan has been used.
    """
    global post_load_actions, single_jvm
    FUNCTION = "::openPlanPostProc:: "
    Errlog.log(MODULE + FUNCTION + ' Entered')
    pm.time_tic("CARMSYS open plan")
    if not HF.isDBPlan():
        a_set.run()
        pm.time_tic("Creating temporary Etable with activity codes")
        # Incase old paramsets are used
        _set_now_time()
        pm.time_log()
        return

    # To speed up the java forms, the JVM is prestarted, but only once
    try:
        print "Check if single_jvm exist"
        single_jvm == single_jvm
        print "it does exist"
    except:
        print "try to get resource and start"
        try:
            single_jvm = Crs.CrsGetModuleResource("config",
                                                  Crs.CrsSearchModuleDef,
                                                  "SingleJVMLauncher")
            if single_jvm:
                StartFilteredTableEditor.launch(['-o'])
        except:
            Errlog.log(FUNCTION + "Couldn't pre-start table editor:")
            traceback.print_exc()
    pm.time_tic("Starting JVM")
    # Improvement?: For studio to be able to detect changes, all tables edited via studio
    # needs to be loaded from the database. This also speeds up the usage of the
    # interface.
    model_tables = [
        "accumulator_int_run",
        "account_entry",
        "account_set",
        "additional_rest",
        "agmt_group_set",
        "annotation_set",
        "bases",
        "bought_days",
        "cabin_training",
        "cabin_recurrent",
        "course_type",
        "crew",
        "crew_activity_attr",
        "crew_address",
        "crew_annotations",
        "crew_attr",
        "crew_base_set",
        "crew_carrier_set",
        "crew_category_set",
        "crew_company_set",
        "crew_complement",
        "crew_contact",
        "crew_contract",
        "crew_contract_set",
        "crew_contract_valid",
        "crew_document",
        "crew_document_set",
        "crew_employment",
        "crew_fairness_history",
        "crew_flight_duty_attr",
        "crew_ground_duty_attr",
        "crew_log_acc_mod",
        "crew_not_fly_with",
        "crew_position_set",
        "crew_publish_info",
        "crew_qual_acqual",
        "crew_qualification",
        "crew_qualification_set",
        "crew_rank_set",
        "crew_region_set",
        "crew_rehearsal_rec",
        "crew_restr_acqual",
        "crew_restriction",
        "crew_restriction_set",
        "crew_sen_grp_set",
        "crew_seniority",
        "crew_training_log",
        "crew_training_need",
        "crew_training_t_set",
        "f36_targets",
        "flight_leg_attr",
        "ground_task_attr",
        "rule_exception",
        "special_schedules",
        "todo",
        "training_log_set",
    ]

    if application.ruleset_is_preplanning():
        model_tables += ["do_not_publish"]

    # These tables are not used by studio and are not required to be in the model
    # however RAVE will consume alot of database resources trying to load and
    # refresh this data, to keep up with the model. It is more efficient speed and
    # database load time wise to let the model handle these tables
    rave_tables = [
        "ac_employer_set",
        "ac_qual_map",
        "activity_group_period",
        "activity_set_period",
        "agmt_group_set",
        "agreement_validity",
        "apt_restrictions",
        "apt_restrictions_course",
        "apt_requirements",
        "cabin_recurrent",
        "cabin_training",
        "ci_exception",
        "coterminals",
        "country_req_docs", 
        "crew_complement",
        "crew_leased",
        "crew_need_exception",
        "crew_need_jarops_period",
        "crew_need_service",
        "crew_passport",
        "crew_recurrent_set",
        "crew_rest",
        "meal_flight_owner",
        "freeday_requirement",
        "hotel_contract",
        "hotel_transport",
        "lh_apt_exceptions",
        "meal_customer",
        "meal_airport",
        "minimum_connect",
        "minimum_connect_pass",
        "lpc_opc_or_ots_composition",
        "preferred_hotel_exc",
        "preferred_hotel",
        "simulator_briefings",
        "simulator_set",
        "spec_weekends",
        "pattern_acts",
        "lpc_opc_or_ots_composition",
        "pgt_need",
        "rave_string_paramset",
        "rest_on_board_cc",
        "rest_on_board_fc",
        "simulator_composition"
        ]

    needed_tables = model_tables[:]
    needed_tables.extend(rave_tables)
    
    try:
        # We shall use tm.reset() with care. It is not supposed to recreate
        # a new TableManager instance. The operation shall just make sure that
        # we have a TM that will connect to the latest TableManager instance
        # when we start to use it
        tm.reset()
        TM = tm.TM
        tables_to_load = [e.entity for e in TM._entity if (e.entity in
                                                           needed_tables)]
        error_tables = [t for t in needed_tables if t not in tables_to_load]
        if error_tables:
            Errlog.log(MODULE+FUNCTION+ "Table name errors: %s" % error_tables)
            
        TM(*tables_to_load)
        TM.showSelections()
        pass
    except:
        Errlog.log(MODULE+FUNCTION + "Failed to init tables. No DB plan loaded")
        traceback.print_exc()
    pm.time_tic("Preloading tables to model")

        
    # Set the post-load actions
    if post_load_actions:
        # Need to be first
        if post_load_actions.has_key("RULESET"):
            if post_load_actions["RULESET"].upper().startswith("PAIRING"):
                __set_ruleset(post_load_actions["RULESET"])
            
        # Load custom parameters here        
        if post_load_actions.has_key("PARAMETERS"):
            if post_load_actions["PARAMETERS"]:
                try:
                    Cui.CuiCrcLoadParameterSet(Cui.gpc_info,
                                               post_load_actions["PARAMETERS"])
                except:
                    Errlog.log(MODULE+FUNCTION + "Could not load personal parameters")
                    traceback.print_exc()
                    pass
        if post_load_actions.has_key("ASSIGN"):
            try:
                Cui.CuiSetSubPlanAssignValue(Cui.gpc_info,
                                             post_load_actions["ASSIGN"])
            except:
                Errlog.log(MODULE+FUNCTION + "Could not set assignment vector")
                traceback.print_exc()
        if post_load_actions.has_key("MASK"):
            try:
                bypass = {'FORM': 'SUB_PLAN_FORM',
                          'SUB_PLAN_MASK_VALUE' : str(post_load_actions["MASK"])}
                Cui.CuiSubPlanProperties(bypass, Cui.gpc_info)
            except:
                Errlog.log(MODULE+FUNCTION + "Could not set assignment mask")
                traceback.print_exc()                
        if post_load_actions.has_key("PLANNINGAREA"):
            for key in post_load_actions["PLANNINGAREA"].keys():
                val = post_load_actions["PLANNINGAREA"][key]
                print val, key
                Cui.CuiCrcSetParameterFromString(key, val)
        if post_load_actions.has_key("PP"):
            for key in post_load_actions["PP"].keys():
                Cui.CuiCrcSetParameterFromString(key,
                                                 post_load_actions["PP"][key])
    
    # Incase old paramsets are used
    _set_now_time()
    pm.time_tic("Setting post-load actions")
    
    # Pre-load large tables to rave. This moves processing time to the load phase
    # and speeds up the initial scrolling in studio. Only pre-load if using a
    # Rostering ruleset
    if post_load_actions["RULESET"][:9] == "Rostering":
        Errlog.log(MODULE+ FUNCTION + "Pre-loading accumulator tables.")
        try:
            rave_preload = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, "PLAN",
                                          "studio_process.%preload_rave%")
        except:
            Errlog.log(MODULE+FUNCTION + "Failed to preload accumulator tables.")
            traceback.print_exc()
    pm.time_tic("Preloading tables to rave")

    # Hook in protection here

    a_set.run()
    pm.time_tic("Creating temporary Etable with activity codes")

    modcrew.clear()
    # Set subplan as not modified
    Cui.CuiSetSubPlanModified(Cui.gpc_info,0)

    pm.time_log()
    
def savePlanPostProc():
    """
    Running functions after the CARMSYS function for
    saving a plan has been used.
    """
    
    FUNCTION = ":: savePlanPostProc:: "
    Errlog.log(MODULE+FUNCTION + ' Entered')
    pm.time_tic("Actual (sys) save")
    pm.time_log()
    if not HF.isDBPlan():
        # Currently we do nothing on fileplans
        Errlog.log(MODULE+FUNCTION + "Current plan is file plan, no post-process")
        return 0
    modcrew.clear()
    return 0

def savePlanPreProc():
    """
    Running functions before the CARMSYS function for
    saving a plan will be used.
    """
    FUNCTION = "FileHandlingExt:: savePlanPreProc:: "
    Errlog.log(MODULE+FUNCTION + ' Entered')
    if not HF.isDBPlan():
        # Currently we do nothing on fileplans
        Errlog.log(FUNCTION + "Current plan is file plan, no pre-process")
        pm.time_reset("Saving Plan Times")
        return 0

    # Confirm the Save ?
    if not cs.confirmSave():
        Errlog.log(MODULE+FUNCTION + "Save aborted")
        return 1 # -1 BZ 34939
    pm.time_reset("Saving Plan Times")
    # Also called by pre-studio
    if application.ruleset_is_rostering() or \
           application.ruleset_is_preplanning():
        return savePlanPreProcRostering()
    else:
        # No crew clean ups in pairing
        return 0
    
def savePlanPreProcRostering():

    FUNCTION = ":: savePlanPreProcRostering:: "
    Errlog.log(MODULE+FUNCTION + ' Entered')

    try:
        Cui.CuiMakeAssignmentsPersonal(Cui.gpc_info, 0)
    except:
        Errlog.log(MODULE+FUNCTION + "Function for making non personal assignments personal failed")
        traceback.print_exc()
    pm.time_tic("Function for making non personal assignments personal went successful")

    # 1) update training log here
    try:
        CTH.update_ctl_changed_crew()
    except:
        Errlog.log(MODULE+FUNCTION + "Error at crew_training_log update")
        traceback.print_exc()
    pm.time_tic("Updating training log")

    # 2) update crew leave accounts here
    try:
        carmusr.AccountHandler.updateChangedCrew()
    except:
        Errlog.log(MODULE+FUNCTION + "Error at AccountHandler update")
        traceback.print_exc()
    pm.time_tic("Updating crew accounts")

    # 3) cleaning attribute tables
    try:
        result = CTH.clean_attributes_tables()
        Errlog.log(MODULE+ FUNCTION + result)
    except:
        Errlog.log(MODULE+FUNCTION + "Error at attributes tables cleaning")
        traceback.print_exc()
    pm.time_tic("Cleaning attributes tables")
    
    # 4) update special training companion
    try:
        carmusr.training_attribute_handler.update_special_training_companions()
    except:
        Errlog.log(MODULE+FUNCTION + "Error at special training companions update")
        traceback.print_exc()
    pm.time_tic("Updating special training companions")        

    return 0


def __set_ruleset(ruleset):
    FUNCTION = '__set_ruleset::'
    try:
        Cui.CuiCrcLoadRuleset(Cui.gpc_info,
                              ruleset, 1)
        Errlog.log(MODULE+FUNCTION + "Loaded rule set %s ok"
                   %ruleset)
        
        # Set parameters for what data has actually been loaded.
        preDBPeriod = Crs.CrsGetAppModuleResource("gpc", Crs.CrsSearchAppDef,
                                                  "config", Crs.CrsSearchModuleDef,
                                                  "DataPeriodDbPre")
        R.param("fundamental.%extra_days_loaded_beginning%").setvalue(int(preDBPeriod))
        
        # Set parameters for what data has actually been loaded.
        postDBPeriod = Crs.CrsGetAppModuleResource("gpc", Crs.CrsSearchAppDef,
                                                   "config", Crs.CrsSearchModuleDef,
                                                   "DataPeriodDbPost")
        R.param("fundamental.%extra_days_loaded_end%").setvalue(int(postDBPeriod))
    except:
        Errlog.log(MODULE+FUNCTION + "Could not load ruleset %s"%ruleset)

    
def _set_now_time():
    try:
        R.param('fundamental.%use_now_debug%').setvalue(False)
        R.param('fundamental.%now_debug%').setvalue(AbsTime.AbsTime('1Jan1986'))
        Errlog.log(MODULE+"::_set_now_time: Set use_now_debug=False")
    except Exception, err:
        pass
