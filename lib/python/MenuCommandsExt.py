#

#
# This module is imported as to the __main__ module by StudioCustom.py at start up.
# It should not be imported by other modules. 
#
# The module is supposed to contain functions that are used as argument to "PythonExalExpr" 
# in the menu source files. 
#
# By Stefan Hammar, Carmen Systems AB, Sept 2004
#

import traceback
import time

import Cui
import Gui
import Crs
import Csl
import Localization
import Variable
import Errlog
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime

import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as R

import carmstd.area as area
import carmstd.parameters as parameters
import carmstd.plan as plan
import carmstd.rave as rave   
import carmstd.report as report
import carmstd.rpc as rpc

import filecmp
import os
import subprocess
import re
import tempfile
from Select import mark
from Select import select
from Select import selectParam
from Select import sortParam
from Select import selectCrew
from Select import selectParamCrew
from Select import subSelectCrew
from Select import selectAndSort
from Select import selectCrewQual
from Select import selectAllQual
from Select import selectTripQual
from Select import selectSimQual
from Select import selectSBYQual
from Select import subSelectCrewQual
from Select import selectTrip
from Select import subSelectTrip
from Select import selectTripEquipment
from Select import subSelectTripEquipment
from Select import selectTripUsingPlanningAreaBaseFilter
from Select import selectCrewUsingPlanningAreaBaseFilter
from Select import selectCrewOutsidePlanningAreaBaseFilter
from Select import selectTripsOutsidePlanningAreaBaseFilter
from Select import selectLegsUsingPlanningAreaBaseFilter
from Select import selectLegsOutsidePlanningAreaBaseFilter
from Select import sort
from Select import restore_sorting

import carmusr.HelperFunctions as HelperFunctions
import carmusr.application as application
import carmusr.ground_duty_handler as ground_duty_handler
import carmusr.SBHandler as SBHandler
import carmusr.tracking.FlightProperties as FlightProperties
import carmusr.pairing.export_pairing_form as export_pairing_form
import carmusr.Attributes as Attributes
import carmusr.rostering.Fairness as Fairness
import carmusr.sim_exception_handler as SIM
import carmusr.planning.DaysForProduction

from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from carmensystems.basics.CancelException import CancelException
from utils.rave import RaveEvaluator, RaveIterator, MiniEval
from utils.divtools import isYes, isNo, yesOrNo, yesOrNoInverse
from tm import TM
import utils.time_util as time_util
import utils.Names as Names

import carmensystems.mave.etab as etab
from carmstd import bag_handler

csl = Csl.Csl()

###########################
# Simple menu calls
###########################

def refresh_test_menu(*args, **kwargs):
    import carmtest.framework.TestFunctions as F
    return reload(F).refresh_test_menu(*args, **kwargs)

def test_menu_run_test(*args, **kwargs):
    import carmtest.framework.TestFunctions as F
    return reload(F).run_tests(*args, **kwargs)

def set_user_message(msg):
    Errlog.set_user_message(msg)

def showCrewCrrs(planning_area_filter=False, remove_other_windows=False, set_basefilter=False):
    """
    Displays crew in window 0 and trips in window 1
    with or without planning area selection
    """
    
    # Awkwardly check which windows exist using CuiGetScaleValues.
    #   Create windows (1) and (2) if they don't exist.
    #   If 'remove_other_windows' is True, remove (3) and (4) if they exist.
    
    for area in range(Cui.CuiAreaN):
        scale = Variable.Variable(-1)
        Cui.CuiGetScaleValues(Cui.gpc_info, area, scale, scale)
        if scale.value < 0 and area <= Cui.CuiArea1:
            Cui.CuiOpenArea(Cui.gpc_info) # Opens lowest numbered available area
        elif scale.value >= 0 and remove_other_windows and area >= Cui.CuiArea2:
            Cui.CuiRemoveArea(Cui.gpc_info, area)

    # Display rosters in (1), and trips in (2), possibly applying a filter.
    
    if planning_area_filter:
        try:
            if set_basefilter:
                selectCrewUsingPlanningAreaBaseFilter(area=Cui.CuiArea0)
            else:
                select({"planning_area.%crew_is_in_planning_area%":"T"}, Cui.CuiArea0, Cui.CrewMode)
        except:
            print "Failure when applying crew filter:"
            traceback.print_exc()
        try:
            if set_basefilter:
                selectTripUsingPlanningAreaBaseFilter(area=Cui.CuiArea1)
            else:
                select({"planning_area.%trip_is_in_planning_area%":"T"}, Cui.CuiArea1, Cui.CrrMode)
        except:
            print "Failure when applying trip filter:"
            traceback.print_exc()
    else:
        Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, Cui.CuiShowAll)
        Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1, Cui.CrrMode, Cui.CuiShowAll)
    restore_sorting(area=Cui.CuiArea0)
    restore_sorting(area=Cui.CuiArea1)  

def showOptInput():
    """
    Displays the crew optimizer input in window 0 and
    the trip optimizer input in window 1
    """
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, "crew_apc_tag")
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea1, Cui.CrrMode, "apc_crr_tag")

def showCrrsLegs():
    """
    Displays legs and trips in window
    """
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrrMode, Cui.CuiShowAll)
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1, Cui.LegMode, Cui.CuiShowAll)

    
def showIllegal():
    """
    Displays illegal crew in window 0 and illegal trips in window 1
    """
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, Cui.CuiShowIllegal)
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1, Cui.CrrMode, Cui.CuiShowIllegal)


def showReportPopup(report, area=Cui.CuiWhichArea, scope="object"):
    """
    Runs a PDL report and shows a popup as PDL.
    Will not consider whether to use publisher or pdl!
    """
    oldViewer = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "ReportViewer")
    try:
        Crs.CrsSetAppModuleResource("gpc", "preferences", "ReportViewer", "CRG", "Restored by python script")
        # Considers pdf/pdl settings...
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope, report, 0), 
    except Exception, e:
        Errlog.log("%s" % e)
        Errlog.log("Failed to run report %s" % report)
    if not oldViewer is None:
        Crs.CrsSetAppModuleResource("gpc", "preferences", "ReportViewer", oldViewer, "Restored by python script")

        
def sort_crew_scroll_home(key, arg):
    """
    Sorts crew window according to standard
        CuiSortArea(gpc_info, CuiWhichArea, key, arg)
    Then the area is scrolled to top.
    """
    Cui.CuiSortArea(Cui.gpc_info,
                    Cui.CuiWhichArea,
                    key,
                    arg)
    HelperFunctions.redrawAreaScrollHome(Cui.CuiWhichArea)
    return 0
    
    
###########################
# Generating etables
###########################


def report2etab(reportName, destination, verify=True, refresh=True, area=None, scope=None):
    """
    Runs a report and stores the result in an etable.
    The destination can be:
      SpLocal/<name>    - stored in open subplan etab directory
      LpLocal/<name>    - stored in open local plan etab directory
      [module].%rave%   - stored in $CARMDATA/ETABELS/val(rave_variable)
      <other>           - expands environment variables
    """
    if HelperFunctions.isDBPlan():
        cfhExtensions.show("Crew Values should not be generated in Database!")
        Errlog.log("Crew Values should not be generated in Database!")
        return
    outPath = expandEtabName(destination)
    if verify and os.path.exists(outPath):
        if not cfhExtensions.confirm("Do you want to replace:\n%s?" % outPath):
            return

    try:
        report.Report(reportName, area, scope).save(outPath)
    except Exception, e:
        Errlog.log("%s "% e)
        Errlog.set_user_message("Failed to run report %s" % reportName)
    if refresh:
        Cui.CuiCrcRefreshEtabs(os.path.dirname(outPath),
                               Cui.CUI_REFRESH_ETAB_FORCE)

def expandEtabName(destination):
    """
    If the destination looks like a rave variable (several "%")
    the table will be stored under: $CARMDATA/ETABLES/<rave value>

    If the destination contains a string starting with SpLocal or
    LpLocal it will be stored in the local plan or subplan.
    """
    if destination.count("%") > 1:
        try:
            d, = R.eval(R.expr(destination))
            if not (d.startswith("SpLocal") or d.startswith("LpLocal")):
                outPath=os.path.join("$CARMDATA", "ETABLES", d)
            else:
                outPath=d
        except Exception, e:
            Errlog.log("%s" % e)
            Errlog.set_user_message("Could not find rave variable:\n%s" % destination)
            return
    else:
        outPath=destination

    if outPath.startswith("SpLocal"):
        sp = plan.getCurrentSubPlan()
        outPath = outPath.replace("SpLocal", sp.getEtabPath())
    elif outPath.startswith("LpLocal"):
        lp = plan.getCurrentLocalPlan()
        outPath = outPath.replace("LpLocal", lp.getEtabPath())
    return os.path.expandvars(outPath)

###############
# Set Crr Names
###############    
def setCrrNames(start=None, area=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea), scope ='window'):
    """
    Sets the crr names on all trips in the selected scope
    """
    rc = rave.Context(scope,area)
    if not start:
        start = cfhExtensions.inputString('Start value:', 5, title = 'Set trip names')
    try:
        crr_num = int(start)
        for crrIdentifier in rc.getCrrIdentifiers("true",'trip.%start_UTC%'):
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrrMode,str(crrIdentifier))
            Cui.CuiSetCrrName(Cui.gpc_info, area, str(crr_num))
            crr_num = crr_num + 1
    except ValueError, e:
        Errlog.log("%s" % e)
        Errlog.set_user_message("Error: The trip name must be a number")
    except Exception, e:
        Errlog.log("%s" % e) 
        Errlog.set_user_message("Failed to set Trip names")

#####################################################################################
# DYNAMIC MENU ENTRIES
#####################################################################################
# These functions could be used to define the dynamic part of menus.
# The are used in the menu source files.  A simple Example:
#
# Menu Identifier {
#     "My dynamical menu" f.menu MyDynMenu
# }
# Menu MyDynMenu PythonEvalExpr("MenuCommandsExt.createMenuItems('MyDynMenu',\
#                                                                'csl_message(\"Hello %s\")',\
#                                                                ['Entry1','Entry2'],\
#                                                                'A title')")
# { /* The content is defined by the function call above */ } 
#

def createMenuItems(parent,callback_str,items,title=None,potency=0,opacity=0):
    """
    This function is supposed to be called from a menu source file to 
    define (temporary) items in a menu.
    Arguments:
    parent       : The name of the menu where the items should be added.
    callback_str : A string that defines the action for the menu entry.
                   The same syntax as for an action defined after f.exec in 
                   a menu source file.
                   All occurences of "%s" are replaced with string value of the
                   current item.
    items	 : A sequence of strings. Each string will become a menu entry.
    title        : An optional title for the menu entries.
    potency      : See Gui(3p)
    opacity      : See Gui(3p)
    """
    if title: 
        Gui.GuiAddMenuTitle(parent, "", title) 
        Gui.GuiAddMenuSeparator(parent, "")
    for item in items:
        Gui.GuiAddMenuButton(parent, "", item, "", "", "", 
                             callback_str.replace("%s",item), potency, opacity, item, 1, "")
    return 0


def createMenuItemsFromDir(parent,callback_str,dirp,filter=None,title=None,potency=0,opacity=0):
    """
    As "createMenuItems", but takes a directory and a filter as argument instead of a sequence.
    One menu entry is created for each file in the directory if the file is accepted by the filter. 
    dirp   : A path to a directory. 
    filter : A Python function that takes one argument (the full path to a file) and returns true or false.  
             Files in the directory that are directories are always ignored. 
    """
    l = [] 
    d = os.path.expandvars(dirp)
    for f in os.listdir(d):
        fn = d+"/"+f
        if os.path.isdir(fn): continue
        if filter and not filter(fn): continue
        l.append(f)

    createMenuItems(parent,callback_str,l,title,potency,opacity) 

###########################
# Example of dynamic menues
###########################

def loadRuleSetKeepParameters(path):
    """
    Loads the specified rule. Keet the current parameter setting.
    See then man page about CuiCrcLoadRuleset for details about
    the argument.
    """
    import __main__
    paramfile = tempfile.mktemp()
    buf = Variable.Variable("")
    try: Cui.CuiCrcGetParameterAsString("map_parameter_set_name",buf)
    except __main__.exception: pass
    Cui.CuiCrcSaveParameterSet(Cui.gpc_info,None,paramfile)
    Cui.CuiCrcLoadRuleset(Cui.gpc_info,path)
    Cui.CuiCrcLoadParameterSet(Cui.gpc_info,paramfile)
    try: Cui.CuiCrcSetParameterFromString("map_parameter_set_name",buf.value)
    except __main__.exception: pass
    os.unlink(paramfile)

def acceptableRuleSetName(path):
    return os.path.basename(path)[0] != "."

def createRuleSetMenu(menuName):
    createMenuItemsFromDir(menuName,
                           '''PythonEvalExpr("MenuCommandsExt.loadRuleSetKeepParameters('$CARMTMP/crc/rule_set/GPC/$ARCH/%s')")''',
                           '$CARMTMP/crc/rule_set/GPC/$ARCH',
                            acceptableRuleSetName,
                           Localization.MSGR('Rule Set'))


###########################
# FAIRNESS
###########################

def createFairnessTables():
    """
    Function for creating the fairness tables.
    Generates the Crew Factors initially and then uses 
    the generated values for creating the target values
    """
    report2etab('FairnessCrewFactors.output', 'fairness.%crew_factors_table%',  False)
    report2etab('FairnessTargetValues.output', 'fairness.%target_value_table%', False)
    Errlog.set_user_message("Fairness tables created")

###########################
# Property wrapper for leg
###########################
def getLegProperties():
    """
    Choose what Properties form to run.
    """
    if Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, "object", "personal_activity"):
        try:
            # Force form to be opend with LDOP
            Cui.CuiUpdateTaskLeg({'FORM':'TASK_LEG','FL_TIME_BASE': 'LDOP'},
                                 {'FORM':'TASK_LEG','OK': 'NO'},
                                 Cui.gpc_info,
                                 Cui.CuiWhichArea,
                                 "object",
                                 Cui.CUI_UPDATE_TASK_RECALC_TRIP + Cui.CUI_UPDATE_TASK_TASKTAB)
        except Exception, e:
            Errlog.log("Warning: MenuCommandsExt::getLegProperties::Swallowed exception from CuiUpdateTaskLeg")
            Errlog.log("Warning: MenuCommandsExt::getLegPropertiesTracking::'%s'" % e)
            return 1

    elif HelperFunctions.isDBPlan() and Cui.CuiCrcEvalBool(Cui.gpc_info,
            Cui.CuiWhichArea, "object", "ground_duty"):
        ground_duty_handler.manage_ground_duty("PROPERTIES_GND")
            
    else:
        #Updates legset! Note: Always returns None; Assume update has been performed
        try: 
            Cui.CuiLegSetProperties(Cui.gpc_info, Cui.CuiWhichArea, "object")
        except:
            print "Exception in getLegProperties, operation may have been canceled"
        return 0

############################################################################
# Property wrapper for leg, TRACKING:
# - Tracking specific dialog for flight legs
# - Handling of CALLOUT attribute when start time or leg code is modified
############################################################################
def getLegPropertiesTracking():
    """
    Choose what Properties form to run.
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    if Cui.CuiCrcEvalBool(Cui.gpc_info, area, "object", "ground_transport"):
        import carmensystems.studio.Tracking.CreateFlight as CreateFlight
        return CreateFlight.editTransport()

    elif Cui.CuiCrcEvalBool(Cui.gpc_info, area, "object", "personal_activity"):
        try:
            # Get CALLOUT attribute info (if it exists)
            org = RaveEvaluator(area, Cui.LegMode,
                                crewid = "crew.%id%",
                                legid = "leg_identifier",
                                st = "leg.%start_utc%",
                                activity = "leg.%code%")
            try:
                co_attr_values = Attributes.GetCrewActivityAttr(org.crewid, org.st, org.activity, "CALLOUT")
                # Get a list of legids on the roster before CuiUpdateTaskLeg is
                # called. Make sure the activity remains selected.
                Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, org.crewid)
                org_roster_legids = [l[1] for l in R.eval('default_context',
                    R.foreach(R.iter('iterators.leg_set',where=("personal_activity",)),'leg_identifier'))[0]]
                Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(org.legid))
            except Attributes.CrewAttrNotFoundError:
                co_attr_values = None
            # Let the user modify the activity using the standard dialog
            Cui.CuiUpdateTaskLeg(Cui.gpc_info, area, "object",
                                 Cui.CUI_UPDATE_TASK_RECALC_TRIP
                                 | Cui.CUI_UPDATE_TASK_TASKTAB)
                                 
            if co_attr_values is not None:
                # If start time or leg code was modified, then a new activity
                # was created instead of modifying the existing one.
                # In that case, move the CALLOUT attribute to the new activity.
                try:
                    # Make sure that the modified activity is selected, even if
                    # CuiUpdateTaskLeg has assigned a new legid. Get modified info
                    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
                    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, org.crewid)
                    mod_roster_legids = [l[1] for l in R.eval('default_context',
                        R.foreach(R.iter('iterators.leg_set',where=("personal_activity",)),'leg_identifier'))[0]]
                    mod_legid = (set(mod_roster_legids) & set([org.legid])  or 
                                 set(mod_roster_legids) - set(org_roster_legids)).pop()
                    mod = RaveEvaluator(area, Cui.LegMode, mod_legid,
                                        st = "leg.%start_utc%",
                                        activity = "leg.%code%",
                                        is_sby = "leg.%is_standby_with_rest%")
                    if mod.st != org.st or mod.activity != org.activity:
                        print "getLegPropertiesTracking: Modified st and/or code; move CALLOUT attribute"
                        # Original attribute not valid in latest roster revision
                        # (Keep value_int (=PUBLISHED), in case the activity change is do-not-publish.)
                        Attributes.SetCrewActivityAttr(org.crewid, org.st, org.activity, "CALLOUT", rel=None, refresh=False)
                        if mod.is_sby:
                            co_attr_values['si'] = "Created by %s at %s" % (Names.username(), AbsTime(*time.gmtime()[:5]))
                            Attributes.SetCrewActivityAttr(org.crewid, mod.st, mod.activity, "CALLOUT", **co_attr_values)
                        else:
                            print "getLegPropertiesTracking: Can't callout from '%s', attribute not created" % mod.activity
                except Exception, e:
                    Errlog.log("Warning: MenuCommandsExt::getLegPropertiesTracking::Swallowed failure to check for CALLOUT attribute change")
                    Errlog.log("Warning: MenuCommandsExt::getLegPropertiesTracking::'%s'" % e)
                    
        except Exception, e:
            Errlog.log("Warning: MenuCommandsExt::getLegPropertiesTracking::Swallowed exception from CuiUpdateTaskLeg")
            Errlog.log("Warning: MenuCommandsExt::getLegPropertiesTracking::'%s'" % e)
            return 1

    elif Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, "object", "ground_duty"):
        ground_duty_handler.manage_ground_duty("PROPERTIES_GND")
            
    else:
        # Updates legset (core table 'flight_leg')!
        # Note: Always returns None; Assume update has been performed
        FlightProperties.showFlightProperties()
        
    return 0

###################################################################
# Functions for displaying changed crew (locally or via a refresh)
###################################################################
def displayLocallyModifiedCrew():
    """
    Function for showing all crew that have been locally modified in the
    current model. 
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    mod_crew = Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info)
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, mod_crew)
    HelperFunctions.redrawAreaScrollHome(area)

def displayRefreshedModifiedCrew():
    """
    Function for showing all crew that have been modified after a refresh of
    the model from the database. 
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    mod_crew = Cui.CuiGetRefreshModifiedCrew(Cui.gpc_info)
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, mod_crew)
    HelperFunctions.redrawAreaScrollHome(area)

def displayPotentiallyConflictingCrew():
    """
    Function for displaying crew that have both been changed in the model
    and changed by a refresh.
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    local_crew = Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info)
    refreshed_crew = Cui.CuiGetRefreshModifiedCrew(Cui.gpc_info)
    conflict_crew = [crew for crew in local_crew if crew in refreshed_crew]
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, conflict_crew)
    HelperFunctions.redrawAreaScrollHome(area)

###############################################
# Wrapper for getNext/Previous functionality
###############################################

def getNextPrevious(searchType, prev=0, backToBase="No", allowIllegal="Yes", beforeNow="Yes"):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    if isYes(prev):
        prev = Cui.CUI_NP_PREV
    else:
        prev = 0

    if isYes(beforeNow):
        startTime = 0
    else:
        startTime = Cui.CuiCrcEvalAbstime(Cui.gpc_info, area, "object", "fundamental.%now%")
        
    Cui.CuiUpdateConnectionLock(Cui.gpc_info, area, 0)

    setNextPrevFilter(backToBase, allowIllegal)
    
    try:
        searchType = searchType.upper()
        if searchType == "DH":
            Cui.CuiGetNextPreviousDeadhead(Cui.gpc_info, prev, startTime)
        elif searchType == "LEG" :
            Cui.CuiGetNextPreviousLeg(Cui.gpc_info, prev, startTime)
        elif searchType == "DUTY" :
            Cui.CuiGetNextPreviousRtd(Cui.gpc_info, prev, startTime)
        elif searchType == "TRIP" :
            Cui.CuiGetNextPreviousCrr(Cui.gpc_info, prev, startTime)
        elif searchType == "OAG" :
            Cui.CuiGetNextPreviousOag(Cui.gpc_info, prev, startTime)
        elif searchType == "GT" :
            Cui.CuiGetNextPreviousGt(Cui.gpc_info, prev, startTime)
        elif searchType == "FROMROT" :
            Cui.CuiGetNextPreviousFromAcRot(Cui.gpc_info, prev, startTime)
    
    finally:
        print "Ended getNextPrev"

                                                # Default:
def getFilteredNextPrevDH(prev="No",              # get next dh   
                          anyAirport="Yes",       # all stations
                          allowIllegal="Yes",     # no illegalty check
                          noStartBeforeUtc=None,  # any dh departure time
                          quiet=False):
    """
    Selection of DH:s with extended filtering options.
    Assumes the default_context is a leg object.
    
    Either we allow any deadhead departure/arrival airports (default),
    or we limit the deadheads to those that connect the current leg with
    any SAS base station, next/prev location, or trip start/end station.
    """

    if isYes(prev):
        prev = Cui.CUI_NP_PREV
    else:
        prev = 0
        
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    thisLeg = RaveEvaluator(area, Cui.LegMode,
        base_stations = "studio_select.%dh_base_stations%",
        dep_stn       = "leg.%start_station%",
        arr_stn       = "leg.%end_station%",
        dep_utc       = "leg.%start_utc%",
        arr_utc       = "leg.%end_utc%",
        trip_dep_stn  = "trip.%start_station%",
        trip_arr_stn  = "trip.%end_station%",
        prev_arr_stn  = "studio_select.%dh_departure_station%",
        next_dep_stn  = "studio_select.%dh_arrival_station%",
        prev_arr_utc  = "studio_select.%dh_departure_utc%",
        next_dep_utc  = "studio_select.%dh_arrival_utc%",
        now_utc       = "fundamental.%now%",
        identifier    = "leg_identifier",
        )

    if str(noStartBeforeUtc).upper().startswith("NOW"):
        noStartBeforeUtc = thisLeg.now_utc
        
    assert noStartBeforeUtc is None or isinstance(noStartBeforeUtc, AbsTime), \
        "noStartBeforeUtc: expected an AbsTime or the string 'now'"
    
    # Deadhead search filters. "*" means no limitation.
    stations = "*"
    dep_stations = "*" # List of possible departure stations.
    arr_stations = "*" # List of possible arrival stations.
    dep_date =     "*" # Departure date on the form ">=01Jan2007".
    arr_date =     "*" # Arrival date on the form "<=01Jan2007".
    dep_datetime = "*" # Departure time on the form ">=01Jan2007 12:34".
    arr_datetime = "*" # Arrival time on the form "<=01Jan2007 12:34".
    # The reason for specifying both dates and datetimes is technical;
    #   possibly 'CuiGetNextPrevious' is more effective if the dates are given.
    
    # Either we allow any deadhead departure/arrival airports (default),
    # or we limit the deadheads to those that connect the current leg with
    # any SAS base station, next/prev location, or trip start/end station.
    
    if isNo(anyAirport):
        sas_stn_set = set(base.station for base in TM.bases)
        if prev: # backward selection
            if thisLeg.dep_stn == thisLeg.prev_arr_stn \
               and thisLeg.dep_stn in (thisLeg.base_stations or ""):
                cfhExtensions.show("Already at %s." % thisLeg.dep_stn)
                return 1
            leg_stn_set = set([thisLeg.prev_arr_stn, thisLeg.trip_arr_stn])
            dep_stations = ",".join((sas_stn_set | leg_stn_set) - set([None,""]))
        else: # forward selection
            if thisLeg.arr_stn == thisLeg.next_dep_stn \
               and thisLeg.arr_stn in (thisLeg.base_stations or ""):
                cfhExtensions.show("Already at %s." % thisLeg.arr_stn)
                return 1
            leg_stn_set = set([thisLeg.trip_dep_stn, thisLeg.next_dep_stn])
            arr_stations = ",".join((sas_stn_set | leg_stn_set) - set([None,""]))
    if prev:
        stations = dep_stations
    else:
        stations = arr_stations
    
    # Limit selectable deadheads to those that fit in time between
    # the current leg and the previous/next activity.
    # Possibly include the departure limitation imposed by 'noStartBeforeUtc'.  
    
    if prev: # backward selection
        if noStartBeforeUtc is not None:
            dep_limit = max(noStartBeforeUtc, thisLeg.prev_arr_utc)
        else:
            dep_limit = thisLeg.prev_arr_utc
        arr_limit = thisLeg.dep_utc    
    else: # forward selection
        if noStartBeforeUtc is not None:
            dep_limit = max(noStartBeforeUtc, thisLeg.arr_utc)
        else:
            dep_limit = thisLeg.arr_utc
        arr_limit = thisLeg.next_dep_utc
            
    dep_date = ">=%s" % AbsDate(dep_limit)
    dep_datetime = ">=%s" % dep_limit
    arr_date = "<=%s" % AbsDate(arr_limit)
    arr_datetime = "<=%s" % arr_limit
           
    # Let the user select deadheads from those available within
    # the station and departure/arrival time limitations.
    
    # Make sure the basic dh filter has reasonable values.
    setNextPrevFilter(allowIllegal=allowIllegal,
                      backToBase=yesOrNoInverse(anyAirport),
                      airportList=stations)
    
    # Show deadheads and get user selection.

    # [acosta:08/288@13:41] Comment in connection with BZ 31326 and return
    # values from CuiGetNextPrevious():
    # It *is possible to get a return value from CuiGetNextPrevious(), possible
    # values are ranging from -1 to 11. The values that can occur include -1
    # for 'failure', 0 for 'OK', 1 for 'cancelled' and 10 for 'no deadheads'.
    # Note also that CuiBypassWrapper() will raise KeyboardInterrupt
    # for 'cancelled' and 'no deadheads' unless the dict {'WRAPPER':
    # Cui.CUI_WRAPPER_NO_EXCEPTION} has been added to the parameters.
    try:
        Cui.CuiGetNextPrevious(
            {"FORM":"form_leg_filter", "DEFAULT":""}, # Resets form
            {"FORM":"form_leg_filter", "FL_FLIGHT_DEP_AIRP": dep_stations},
            {"FORM":"form_leg_filter", "FL_FLIGHT_ARR_AIRP": arr_stations},
            {"FORM":"form_leg_filter", "FL_LEG_DATE_DEP": dep_date},
            {"FORM":"form_leg_filter", "FL_LEG_DATE_ARR": arr_date},
            {"FORM":"form_leg_filter", "CRC_VARIABLE_0": "leg.%start_utc%"},
            {"FORM":"form_leg_filter", "CRC_VALUE_0": dep_datetime},
            {"FORM":"form_leg_filter", "CRC_VARIABLE_1": "leg.%end_utc%"},
            {"FORM":"form_leg_filter", "CRC_VALUE_1": arr_datetime},
            {"FORM":"form_leg_filter", "OK":""},
            Cui.gpc_info,
            area,
            Cui.CUI_NP_DEADHEAD,
            Cui.CUI_NP_FILTER | prev)
    except CancelException:
        Errlog.log("getFilteredNextPrevDH: Cancelled.")
        return 0
        
    # [acosta:08/294@10:42] This code can be removed, check for return value
    #     from CuiGetNextPrevious.
    # Check if the leg before or after has changed (i.e. if a dh was added).
    thisLeg_after = RaveEvaluator(area, Cui.LegMode, thisLeg.identifier,
        prev_arr_utc  = "studio_select.%dh_departure_utc%",
        next_dep_utc  = "studio_select.%dh_arrival_utc%",
        )
    if  thisLeg.prev_arr_utc == thisLeg_after.prev_arr_utc \
    and thisLeg.next_dep_utc == thisLeg_after.next_dep_utc:
        print "getFilteredNextPrevDH: No deadhead found/selected"
        return 1

    return 0


def setNextPrevFilter(backToBase="No", allowIllegal="Yes", airportList="*"):
    """
    Sets the standard parameters for Get Next/Get Previous.
    (Studio: Options>Command Parameters)
    """
    if yesOrNo(backToBase) and airportList and airportList != "*":
        backToBase = "No"
    Cui.CuiSetNextPreviousFilterValues(
        {"FORM": "form_next_prev_filter","SHOW_ILLEGAL": yesOrNo(allowIllegal)},
        {"FORM": "form_next_prev_filter","SHOW_AS_ACROT": "No"},
        {"FORM": "form_next_prev_filter","CARE_ABOUT_CREW_VALUE": "Yes"},
        {"FORM": "form_next_prev_filter","FNP_LEG_BACK2BASE": yesOrNo(backToBase)},
        {"FORM": "form_next_prev_filter","FNP_DH_BACK2BASE": yesOrNo(backToBase)},
        {"FORM": "form_next_prev_filter","FNP_LEG_BACK2FIRST_IN_CRR": "No"},
        {"FORM": "form_next_prev_filter","FNP_DH_BACK2FIRST_IN_CRR": "No"},
        {"FORM": "form_next_prev_filter","FNP_LEG_RET_FLIGHT": "No"},
        {"FORM": "form_next_prev_filter","FNP_DH_RET_FLIGHT": "No"},
        {"FORM": "form_next_prev_filter","FNP_LEG_AIRPORT": airportList},
        {"FORM": "form_next_prev_filter","FNP_DH_AIRPORT": airportList},
        Cui.gpc_info)

def exportPairingDataToManpower():
    export_pairing_form.show()
    #exporter.export()
    print "exportPairingDataToManpower"

############################################################################
# A function for terminating Studio
# Will be used in Studios started from the AlertMonitor if the Studio has
# been put in a state where it is no longer usable
# Improvement: if possible, the function should start a new caching of studio
############################################################################
def terminateStudio():
    if cfhExtensions.confirm("This will terminate Studio without saving any changes.\n" +
                             "It should only be used if Studio is broken and needs " +
                             "to be restarted."+
                             "\nDo you want to continue?"):
        import sys
        sys.exit()

# Extensions of Select, to select A/C Rotations =========================={{{1
def selectAcRot(selectionCriterias):
    select(selectionCriterias, dataMode=Cui.AcRotMode)


def subSelectAcRot(selectionCriterias):
    selectionCriterias['FILTER_METHOD'] = 'SUBSELECT'
    selectAcRot(selectionCriterias)


# Sorting and selecting, dynamic menues =================================={{{1
class DynamicSelectionCache(object):
    """Base class - keep an iteration of menu entries."""
    def __init__(self, data_mode=Cui.CrewMode):
        self.data_mode = data_mode
        self.cache = None

    def __call__(self):
        return self

    def __iter__(self):
        if self.cache is None:
            self.cache = ()
        return iter(self.cache)


class AcRotFamilyCache(DynamicSelectionCache):
    """Iteration of A/C families."""
    def __init__(self):
        DynamicSelectionCache.__init__(self, Cui.AcRotMode)

    def __iter__(self):
        if self.cache is None:
            acf = set()
            for r in TM.aircraft_type:
                try:
                    acf.add(r.maintype)
                except:
                    pass
            self.cache = tuple(sorted(acf))
        return iter(self.cache)
# Singleton
acrot_family_cache = AcRotFamilyCache()


class AcRotOwnerCache(DynamicSelectionCache):
    """Iteration of A/C owners."""
    def __init__(self):
        DynamicSelectionCache.__init__(self, Cui.AcRotMode)

    def __iter__(self):
        if self.cache is None:
            acr = set()
            for r in TM.aircraft:
                try:
                    acr.add(r.owner)
                except:
                    pass
            self.cache = tuple(sorted(acr))
        return iter(self.cache)
# Singleton
acrot_owner_cache = AcRotOwnerCache()


class SelectMenu:
    """Keep connection between menu type and DynamicSelectionList instances."""
    def __init__(self, my_name, **iterators):
        """'my_name' is used by the "callback" in 'eval_select'. a is a list of
        tuples where first index is the name of the menu and the second is the
        associated class."""
        self.my_name = my_name
        self.iterators = iterators

    def __getitem__(self, k):
        """Get list associated with key 'k'. The list will be populated once it
        is instantiated, which also happens here on first call."""
        if not k in self.iterators:
            return DynamicSelectionCache()
        return self.iterators[k]

    def __call__(self, parent, key, title='', filter_method=None):
        """
        Entry point for menu files. A typical menu entry would be something like:
        Menu MainDat24AcSubSelectFamilyMenu PythonEvalExpr("MenuCommandsExt.select_menu('MainDat24AcSubSelectFamilyMenu', 'acrot_family', 'Subselect A/C Family', 'SUBSELECT')")
        {
           /* Dynamic menu */
        }
        """
        if title:
            # GuiAddMenuTitle(parentMenu,  icon,  title,  tooltip,  identifier, menuMode)
            Gui.GuiAddMenuTitle(parent, '', title, '', '', '')
            # GuiAddMenuSeparator(parentMenu, title, identifier)
            Gui.GuiAddMenuSeparator(parent, '', '')
        for value in self[key]:
            # GuiAddMenuButton(parentMenu,  icon,  title,  tooltip,   mnemonic,
            #     accelerator,  action,  potency,  opacity,  identifier, sensitive, menuMode)
            Gui.GuiAddMenuButton(parent, '', value, '', '', '',
                    self.eval_select(key, value, filter_method), Gui.POT_REDO,
                    Gui.OPA_OPAQUE, self.menu_id(parent, key, value, filter_method), True, '')

    def eval_select(self, key, value=None, filter_method=None):
        """Create a call for each menu item."""
        if filter_method is None:
            return """PythonEvalExpr("%s.%s.select('%s', '%s')")""" % (
                    self.__module__, self.my_name, key, value)
        else:
            return """PythonEvalExpr("%s.%s.select('%s', '%s', '%s')")""" % (
                    self.__module__, self.my_name, key, value, filter_method)

    def menu_id(self, *a):
        """Return id as 'parent_key' or 'parent_key_value'."""
        return '_'.join([x for x in a if x is not None])

    def select(self, key, value=None, filter_method=None):
        try:
            S = {type_map[key]: value}
            if not filter_method is None:
                S['FILTER_METHOD'] = filter_method
            select(S, dataMode=self[key].data_mode)
        except:
            raise
            return 1
        return 0


# select_menu ============================================================{{{1
# Singleton
# Note the arg 'select_menu' has to be the same as the variable name.
select_menu = SelectMenu(
    'select_menu', 
    acrot_family=acrot_family_cache,
    acrot_owner=acrot_owner_cache,
)


# type_map ==============================================================={{{1
type_map = {
    'acrot_type': 'leg.%ac_type%',
    'acrot_family': 'leg.%ac_family%',
    'acrot_owner': 'leg.%aircraft_owner%',
    'acrot_planning_group': 'leg.%ac_planning_group%',
    'acrot_tailid': 'leg.%sort_tail_id%',
    'acrot_flight': 'leg.%flight_id%',
    'trip_homebase': 'trip.%homebase%',
}


# sort_by_key ============================================================{{{1
def sort_by_key(type):
    if type in type_map:
        Cui.CuiSortArea(Cui.gpc_info, Cui.CuiWhichArea, Cui.CuiSortRuleValue, type_map[type])
        return 0
    return 1


# overlaps ==============================================================={{{1
def overlaps(key, *args):
    def _select_mark(expr):
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiWhichArea, 'WINDOW')
        select({'FILTER_MARK': 'LEG',
                'FILTER_METHOD': 'SUBSELECT',
                expr: 'true'})

    def _mark(expr):
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiWhichArea, 'WINDOW')
        mark({'FILTER_MARK': 'LEG',
              expr: 'true'})

    def _remove_marked():
        # 0 => OK, 1 => canceled, -1 => error
        rc = Cui.CuiRemoveMarkedLegsInWindow(Cui.gpc_info, 2)
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiWhichArea, 'WINDOW')

    if key == 'select':
        _select_mark('studio_overlap.leg_overlap') 

    elif key == 'remove':
        import carmusr.resolve_overlaps
        carmusr.resolve_overlaps.run()
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiWhichArea, 'WINDOW')

    elif key == 'report':
        import report_sources.hidden.OverlapReport
        report_sources.hidden.OverlapReport.run()


# select_similar ========================================================={{{1
def select_similar(key, *args):
    """Select rosters with "similar" legs."""
    # Analyze current leg.
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
            Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), 'OBJECT')
    leg = MiniEval({
        'code': 'leg.%code%',
        'training_code': 'leg.%training_code%',
        'start_utc': 'leg.%start_utc%',
        'start_station': 'leg.%start_station%',
        'end_station': 'leg.%end_station%',
        'uuid': 'leg.%uuid%',
        'is_flight_duty': 'leg.%is_flight_duty%',
        'is_pact': 'leg.%is_pact%',
        'is_simulator': 'leg.%is_simulator%',
        'group_code': 'task.%group_code%',
        'sim_ac_family': 'leg.%gd_leg_fam%',
        }).eval(R.selected(R.Level.atom()))

    expr = {'FILTER_MARK': 'LEG'}

    if leg.training_code is not None:
        # Training: select legs with same type of training.
        expr.update({
            'leg.training_code': leg.training_code,
        })
    elif leg.is_pact:
        # PACT: Select legs with same activity group.
        expr.update({
            'leg.is_pact': 'true', 
            'task.group_code': leg.group_code,
        })
    elif leg.is_flight_duty:
        # Flight: Select leg with same route.
        expr.update({
            'leg.is_flight_duty': 'true',
            'leg.start_station': leg.start_station,
            'leg.end_station': leg.end_station,
        })
    elif leg.is_simulator:
        # Simulator: Select simulator legs with same "A/C family".
        expr.update({
            'leg.is_simulator': 'true',
            'leg.gd_leg_fam': leg.sim_ac_family,
        })
    else:
        # Ground duty or others: Select leg of same type.
        expr.update({
            'leg.code': leg.code,
        })

    if key == 'future':
        expr['leg.start_utc'] = '> %s' % leg.start_utc

    area = Cui.CuiWhichArea
    if args and args[0] == 'trip':
        area = HelperFunctions.get_suitable_area(Cui.CrewMode)
        Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CuiShowAll)

    Cui.CuiUnmarkAllLegs(Cui.gpc_info, area, 'WINDOW')
    select(expr, windowArea=area)
    # Sort result so marked legs come first in time order.
    Cui.CuiSortArea(Cui.gpc_info, area, Cui.CuiSortRuleValue,
            'studio_select.first_marked_leg_start')

def create_pact(flags):
    """
    Create PACTs with better default values
    """
    
    default_params = {'FORM':'PACT',
                      'FL_TIME_BASE':'LDOP',
                      'OK':0}
    
    return Cui.CuiCreateManyAssignments({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                        default_params,
                                        Cui.gpc_info, Cui.CuiWhichArea, 0, 0, flags)

def create_one_pact(flags):
    """
    Create PACT with better default value
    """
         
    default_params = {'FORM':'PACT',
                      'FL_TIME_BASE':'LDOP',
                      'OK':0}
    
    return Cui.CuiCreateAssignment({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                   default_params,
                                   Cui.gpc_info, Cui.CuiWhichArea, flags)

def has_unchanged_colgen_parameters():
    """ 
    Check if colgen parameter files are changed
    """

    # Only check for rostering
    try:
        is_rostering = R.eval("base_product.is_rostering")[0]
    except:
        is_rostering = False
    if not is_rostering:
        return True, ""

    path1=os.path.join(os.path.expandvars("$CARMUSR"),"crc","parameters","rostering")
    path2=os.path.join(os.path.expandvars("$CARMDATA"),"RaveParameters","rostering")

    
    script2file = {"ColumnGeneration.py":"column_generation",
                   "ColumnGenerationShort.py":"column_generation_short"}
    
    try:
        script = R.eval("matador.script_file_name")[0]
        filename =  script2file[script]
    except:
        return True, ""

    f1 = os.path.join(path1, filename)
    f2 = os.path.join(path2, filename)
    try:
        test = filecmp.cmp(f1,f2)
    except:
        test = False

    return test, filename


# start_optimizer ========================================================{{{1
def start_optimizer(flags=Cui.CUI_START_OPTIMIZER_DEFAULT):
    """
    Start optimizer after some preliminary checks are done.

    flags is a combinations of:
    Cui.CUI_START_OPTIMIZER_DEFAULT
    Cui.CUI_START_OPTIMIZER_DONT_CONFIRM
    Cui.CUI_START_OPTIMIZER_SILENT
    Cui.CUI_START_OPTIMIZER_FORCE
    Cui.CUI_START_OPTIMIZER_SYNCHRONOUS
    Cui.CUI_START_OPTIMIZER_LOCAL

    1. Pick first area with CrewMode and first area with CrrMode
    2. Check for emptiness.
    3. Check for overlaps.

    Suggestion: Maybe all windows should be checked and report saying for instance:
       'Windows 3 and 4 contain overlaps, don't use them.'?
    """

    # Check if colgen parameters have changed
    unchanged, parameter_file = has_unchanged_colgen_parameters()
    if not unchanged:
        warning = "WARNING! Parameter file rostering/"\
            + parameter_file \
            + " has been modified compared to $CARMUSSR/crc/parameters/rostering/"\
            + parameter_file\

        Errlog.log('MenuCommandsExt::start_optimizer:%s' % warning)

        if not Gui.GuiYesNo("Changed parameters", "Warning!\nParameter file rostering/"
                            + parameter_file
                            + " has been modified.\n"
                            + "See logfile for details."
                            + "\nContinue?"):
            return -1

    if HelperFunctions.isDBPlan():
        warning = 'Can not start optimizer in database plan'
        Errlog.log('MenuCommandsExt::start_optimizer:%s' % warning)
        cfhExtensions.show(warning)
        return -1

    # Set %now% to a good value for optimizing. See crc/modules/fundamental for
    # further info
    Errlog.log("Setting fundamental.%now_debug% for optimizer")
    now, = R.eval('fundamental.%now%')
    R.param('keywords.%now_opt%').setvalue(now)

    def get_areas(only_trip_area=False):
        """
        Return tuple: (first window with CrewMode, first window with CrrMode).
        """
        c = t = None
        for area in xrange(Cui.CuiAreaN):
            area_mode = Cui.CuiGetAreaMode(Cui.gpc_info, area)
            if c is None and area_mode == Cui.CrewMode:
                c = area
            if t is None and area_mode == Cui.CrrMode:
                t = area
        if t is None:
            raise ValueError("No trip window is open.")
        if not Cui.CuiGetTrips(Cui.gpc_info, t, 'window'):
            raise ValueError("The trip window (%d) does not contain any trips." % (c + 1))

        if not only_trip_area:
            if c is None:
                raise ValueError("No roster window is open.")
            if not Cui.CuiGetCrew(Cui.gpc_info, c, 'window'):
                raise ValueError("The roster window (%d) does not contain any rosters." % (c + 1))

        return c, t

    # Get product to set default values
    default_product = application.get_product_from_ruleset()
    if default_product and default_product == application.ROSTERING:
        optimizer = 'Crew Rostering Optimizer'
        nr_slots = 1
    elif default_product and default_product == application.PAIRING:
        optimizer = 'APC'
        nr_slots = 4
        # Don't intercept when a Pairing ruleset is loaded
        dummy, trips = get_areas(True)
        return Cui.CuiStartOptimizer({'FORM': 'START_APC',
                                      'WHICH_OPTIMIZER': optimizer,
                                      'LEG_SRC': 'Window %d' % (trips + 1),
                                      'OK': 0},
                                     {'WRAPPER': Cui.CUI_WRAPPER_SUPPRESS_CANCEL,
                                      }, Cui.gpc_info, flags)
    else:
        warning = 'Can not start optimizer in ruleset for %s' % application.get_product_name()
        Errlog.log('MenuCommandsExt::start_optimizer:%s' % warning)
        cfhExtensions.show(warning)
        return -1

    try:
        rosters, trips = get_areas()
        if Cui.CuiCrcEvalBool(Cui.gpc_info, rosters, 'window', 'studio_overlap.%area_overlap%'):
            raise ValueError("The roster window (%d) contains overlapping assignments." % (rosters + 1))
        if Cui.CuiCrcEvalBool(Cui.gpc_info, trips, 'window', 'studio_overlap.%area_overlap%'):
            raise ValueError("The trip window (%d) contains overlapping trips." % (trips + 1))
    except ValueError, warning:
        cfhExtensions.show(str(warning) + "\n\nCannot start optimization job.",
                           title="Operation aborted")
        return 1
    except Exception, e:
        cfhExtensions.show(str(e))
        raise

    # Generate trip list etab to identify main base variants for KPIs
    # Only for Rostering
    if default_product and default_product == application.ROSTERING:
        etable_path = expandEtabName('kpi.%main_base_variant_etab%')

        session = etab.Session()
        e = etab.create(session, etable_path)
        e.appendColumn('trip_unique_string', str)

        bag_wrapper = bag_handler.WindowChains(area=trips)
        bag = bag_wrapper.bag
        for trip_bag in bag.iterators.trip_set():
            e.append([trip_bag.trip.trip_unique_string()])

        e.save()

    default_params = {'FORM': 'START_APC',
                      'WHICH_OPTIMIZER': optimizer,
                      'SLOTS': nr_slots,
                      'LEG_SRC': 'Window %d' % (trips + 1),
                      'CREW_SRC': 'Window %d' % (rosters + 1),
                      'OK': 0}
    if Cui.CUI_START_OPTIMIZER_LOCAL & flags:
        # Local job, no batch system
        pass
    else:
        default_params['BATCH_QUEUE'] = 'Default'

    # [acosta:08/107@14:48] Note: CuiStartOptimizer returns -1 if user pressed cancel...
    return Cui.CuiStartOptimizer(default_params,
                                 {'WRAPPER': Cui.CUI_WRAPPER_SUPPRESS_CANCEL}, Cui.gpc_info, flags)


def fetch_assignments():
    default_values_dict = {'FORM':'FETCH_ASSIGNMENTS',
                           'FETCH_BY':'Match Trips in current Sub-plan',
                           'OVERLAP_OPTION':'Deassign trips in current Sub-plan',
                           'CRC_VARIABLE_0': 'trip.%is_locked%',
                           'CRC_VALUE_0': 'F',
                           'CRC_VARIABLE_1': 'trip.%starts_in_pp%',
                           'CRC_VALUE_1': 'T',
                           'CRC_VARIABLE_2': 'hidden',
                           'CRC_VALUE_2': 'F',
                           'OK':0}
    result = Cui.CuiFetchAssignments({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                     default_values_dict, Cui.gpc_info)
    if result == 0:
        Errlog.log('MenuCommandsExt::fetch_assignments: Fetch returned successfully')

        #If assignments fetched succesfully, also fetch crew fairness targets
        #Uses functions in the Fairness module
        next_result = Fairness.fetch_crew_fairness_targets()
        if next_result == 0:
            Errlog.log('MenuCommandsExt::Fairness.fetch_crew_fairness_targets: Fetch returned successfully')
        elif next_result == -1:
            Errlog.log('MenuCommandsExt::Fairness.fetch_crew_fairness_targets: Fetch returned error.')

    elif result == 1:
        Errlog.log('MenuCommandsExt::fetch_assignments: User cancelled fetch')     
    elif result == -1:
        Errlog.log('MenuCommandsExt::fetch_assignments: Fetch returned error')



def fetch_trips():
    default_values_dict = {'FORM':'FETCH_CRRS_DATED',
                           'CRC_VARIABLE_0': 'planning_area.%trip_is_in_planning_area%',
                           'CRC_VALUE_0': 'T',
                           'CRC_VARIABLE_1': 'trip.%starts_in_pp%',
                           'CRC_VALUE_1': 'T',
                           'CRC_VARIABLE_2': 'trip.%is_ground_duty%',
                           'CRC_VALUE_2': 'F',
                           'CRC_VARIABLE_3': 'hidden',
                           'CRC_VALUE_3': 'F',
                           'OK':0}
    result = Cui.CuiFetchCRRs({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                              default_values_dict, Cui.gpc_info,0)
    if result == 0:
        Errlog.log('MenuCommandsExt::fetch_trips: Fetch returned successfully')
    elif result == 1:
        Errlog.log('MenuCommandsExt::fetch_trips: User cancelled fetch')
    elif result == -1:
        Errlog.log('MenuCommandsExt::fetch_trips: Fetch returned error')

# Extra Seat to Active
def convert_extra_seat_to_active():


    """
    Converts all passive legs marked as extra seat to active fligths
    """
    # Show all items in scriptbuffer
    # Mark the intresting legs and lopp through
    # them to convert to active
    saved = CuiContextLocator().fetchcurrent()


    area = Cui.CuiScriptBuffer
    CuiContextLocator(area, "WINDOW").reinstate()
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    crewList, = R.eval('default_context', R.foreach(
                    R.iter('iterators.roster_set',
                           where=('planning_area.%crew_is_in_planning_area%')),
                    'crew.%id%'))
    #print crewList
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CuiShowAll)
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    Cui.CuiSyncModels(Cui.gpc_info)
    mark_leg_bypass = {
        'FORM': 'form_mark_leg_filter',
        'FL_TIME_BASE': 'RDOP',
        'FILTER_MARK': 'LEG',
        'CRC_VARIABLE_0': 'leg.is_extra_seat',
        'CRC_VALUE_0': 'T',
        'CRC_VARIABLE_1': 'planning_area.crew_is_in_planning_area_at_leg_start_hb',
        'CRC_VALUE_1': 'T',
        'OK': ''}
    
    Cui.CuiMarkLegsWithFilter(mark_leg_bypass,
                              Cui.gpc_info, area, 0)
    
    marked_legs = [str(id) for id in Cui.CuiGetLegs(Cui.gpc_info,
                                                    area,
                                                    "MARKED")]
    for id in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, id)
        Cui.CuiExtraSeatFromTo(Cui.gpc_info,
                               Cui.CUI_EXTRA_SEAT_FROM_TO_SILENT |\
                               Cui.CUI_EXTRA_SEAT_FROM_TO_ALLOW_ILLEGAL)
        Cui.CuiChangeToFromPassive(Cui.gpc_info,area,"OBJECT",
                                   Cui.CUI_CHANGE_TO_FROM_SILENT |\
                                   Cui.CUI_CHANGE_TO_FROM_FORCE)
        if verbose:
            leg_obj = HelperFunctions.LegObject(id, area)
            (crew_empno,
             start_utc,
             current_func) = leg_obj.eval('crew.%extperkey%',
                                          'leg.%start_utc%',
                                          'default(crew_pos.%assigned_function%,crew_pos.%current_function%)')
            
            leg_str = 'Leg starting'+\
                      ' %s (UTC) for crew emp %s from extraseat to active %s'%\
                      (start_utc, crew_empno, current_func)
            Errlog.log('MenuCommandsExt::convert_extra_seat_to_active: Converted %s'%leg_str)
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    Cui.CuiSyncModels(Cui.gpc_info)
    saved.reinstate()
    return


def activate_apis_menu():
    """Activate context sensitive APIS menu."""
    import carmusr.paxlst.mmi as paxlst_mmi
    paxlst_mmi.activate_menus()

def current_crew():
    ret_set, = R.eval('default_context', R.foreach(
        R.iter('iterators.roster_set'),
        'crew.%id%'
        ))
    ret = {}
    for t in ret_set:
        ret[t[1]] = t[0]
    return ret
    

def reassign_fbr():
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    CuiContextLocator(area, "WINDOW").reinstate()
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")

    context_crew = current_crew()

    # Find legs to change (incl. what change)
    legs, = R.eval('default_context',
                   R.foreach(
                       R.iter("iterators.leg_set",
                              where = 'rules_studio_ccr.%trip_to_be_reassigned%',),
                       'leg_identifier',
                       'rules_studio_ccr.%pos_change%'
                       )
                   )
    ass_cnt=0
    # note: rave currently does not select AS for assignment change, so that target will be empty.
    # However, the python code is ready for any assignment change.
    leg_ids = {"FC":[],"FP":[],"FR":[],"AP":[],"AS":[],"AH":[]}
    for (ix, id, pos_change) in legs:
        newpos,newfunc,cmp_id = pos_change.split(',')
        # newpos: number of position to change to, used for sorting
        # newfunc: code of position to change to
        # cmp_id: crew id of roster to change with. Must be in current context
        if newpos is not None and cmp_id in context_crew:
            leg_ids[newfunc].append(id)
            ass_cnt += 1
            
    flags = 16|Cui.CUI_CHANGE_ASS_POS_SUPPRESS_DIALOGUE
    # 16 makes function work on segment rather than CRR
    # This overrules booking limitation, so that we can move to an
    # already occupied position
    for (cat,pos) in zip(("F","F","F","C","C","C"),("FC", "FP", "FR", "AP", "AS", "AH")):
        HelperFunctions.markLegs(area, leg_ids[pos])
        Cui.CuiChangeAssignedPosition({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                      Cui.gpc_info,
                                      cat,
                                      pos,
                                      flags)
        HelperFunctions.unmarkLegs(area, leg_ids[pos])

    print "reassigned to:"
    for k in leg_ids.keys():
        print k,len(leg_ids[k])
# dumpovertimecalc -------------------------------------------------------{{{1
def accumulate_publish():
    import carmusr.Accumulators as A
    A.accumulatePublished(Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea))

# run_report ============================================================={{{1
def run_report(name, *a):
    """Run various (Non-Core) reports."""
    if name == 'StandbySummaryReport':
        import report_sources.include.StandbySummaryReport
        report_sources.include.StandbySummaryReport.runReport(*a)
    elif name == 'List9':
        import report_sources.include.List9
        report_sources.include.List9.runReport(*a)
    elif name == 'List12':
        import report_sources.include.List12
        report_sources.include.List12.runReport(*a)
    elif name == 'ECList12':
        import report_sources.include.ECList12
        report_sources.include.ECList12.runReport(*a)
    elif name == 'PerDiemStatement':
        import report_sources.include.PerDiemStatementReport
        report_sources.include.PerDiemStatementReport.runReport(*a)
    elif name == 'ECPerDiemStatement':
        import report_sources.include.ECPerDiemStatementReport
        report_sources.include.ECPerDiemStatementReport.runReport(*a)
    elif name == 'PerDiemTax':
        import report_sources.include.PerDiemYearlyList
        report_sources.include.PerDiemYearlyList.runReport(*a)
    elif name == 'EmployeeCentral':
        from carmtest.TestIntegrationReports import DateIntervalForm
        import Cfh
        f = DateIntervalForm('Set month to run')
        if f.loop() == Cfh.CfhOk:
            args = ' '.join((
                'report_start_date=%s' % f.startDate,
                'report_end_date=%s' % f.endDate
            ))
        report_start_date = str(f.startDate).split()[0]
        report_end_date = str(f.endDate).split()[0]
        import salary.ec.ECSalaryReport as SEC
        ecrun = SEC.ECReport(report_start_date=report_start_date, report_end_date=report_end_date, release=False, test=True, studio=True)
        csv_files = ecrun.generate()
        try:
            for csv in csv_files:
                Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (os.path.basename(csv), csv))
        except Exception:
            cfhExtensions.show("Cannot show csv files", title="Error")
    #SKPROJ-457
    elif name == 'TimeEntry':
        from carmtest.TestIntegrationReports import DateIntervalForm
        import Cfh
        f = DateIntervalForm('Set month to run')
        if f.loop() == Cfh.CfhOk:
            args = ' '.join((
                'report_start_date=%s' % f.startDate,
                'report_end_date=%s' % f.endDate
            ))
        report_start_date = str(f.startDate).split()[0]
        report_end_date = str(f.endDate).split()[0]
        import salary.wfs.wfs_time_entry_report as TER
        te_run = TER.TimeEntryReport(report_start_date=report_start_date, report_end_date=report_end_date, release=False, test=False, studio=True)
        csv_files = te_run.generate([])
        try:
            for csv in csv_files:
                Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (os.path.basename(csv), csv))
        except Exception:
            cfhExtensions.show("Cannot show csv files", title="Error")
    elif name == 'OvertimeStatement':
        import report_sources.include.OvertimeStatement
        report_sources.include.OvertimeStatement.runReport(*a)
    elif name == 'JpOvertimeStatement':
        import report_sources.include.JpOvertimeStatement
        report_sources.include.JpOvertimeStatement.runReport(*a)
    elif name == 'ConvertibleCrew':
        import report_sources.hidden.ConvertibleCrew
        report_sources.hidden.ConvertibleCrew.runReport(*a)
    elif name == 'ResourcePoolIllnessReport':
        import report_sources.include.ResourcePoolIllnessReport
        report_sources.include.ResourcePoolIllnessReport.runReport(*a)
    elif name == 'AccountConflictReport':
        import report_sources.include.AccountConflictReport
        report_sources.include.AccountConflictReport.runReport(*a)
    elif name == 'SupervisionDetails':
        import report_sources.include.SupervisionDetails
        report_sources.include.SupervisionDetails.runReport(*a)
    elif name == 'ECSupervisionDetails':
        import report_sources.include.ECSupervisionDetails
        report_sources.include.ECSupervisionDetails.runReport(*a)
    elif name == 'ResourcePoolInfo':
        import report_sources.include.ResourcePoolInfo
        report_sources.include.ResourcePoolInfo.runReport(*a)

class Zoom:
    """
    Replacement funcs for carmensystems.studio.gui.Zoom module.
    Typically used to override carmsys default menu in:
        menu_scripts/menus/customization/application/TOOL_BAR_Tracking.menu
    """
    @staticmethod
    def ZoomOut():
        """
        The standard function uses
            CuiChangeRuler(gpc_info, area, "local_plan_period", "pan", "0")
        That Cui function messes up the views, so that all data outside the pp
        will be hidden, even if data outside pp is loaded. This override should
        be used until carmensystems.studio.gui.Zoom.ZoomOut is fixed.
        
        See also: Jira SASCMS-2184
        """
        import carmensystems.studio.gui.private.Zoom
        st, et = R.eval('pp_start_time', 'pp_end_time')
        Errlog.log('MenuCommandsExt.Zoom.ZoomOut: (Overrides sys.) '
                   'Zoom to pp = [%s .. %s]' % (st,et))
        carmensystems.studio.gui.private.Zoom.ZoomTo(int(st), int(et))

def toggle_annotations():
    current_toggle, = R.eval('studio_config.%annotations_view_toggle%')

    if current_toggle == True:
        R.param('studio_config.annotations_view_toggle').setvalue(False)
    else:
        R.param('studio_config.annotations_view_toggle').setvalue(True)


def copy_roll_out():
    cui_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    is_sim_exception = Cui.CuiCrcEvalBool(Cui.gpc_info, cui_area, "object", "leg.%has_sim_exception%")
    
    if not is_sim_exception or not HelperFunctions.isDBPlan():
        try:
            Cui.CuiReplicateChains(Cui.gpc_info, 0)
        except:
            Errlog.log("copy_roll_out.py:: User cancelled operation")
            return 0

			
    if is_sim_exception and HelperFunctions.isDBPlan():
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, cui_area, 'WINDOW')
        Cui.CuiMarkCrrs(Cui.gpc_info, cui_area, 'OBJECT', Cui.CUI_MARK_SET)

        # Get values from the current trip
        orig_crr_id = Cui.CuiCrcEvalInt(Cui.gpc_info, cui_area, "object", "crr_identifier")
        trip = HelperFunctions.TripObject(str(orig_crr_id), cui_area)

        (brief, midbrief, debrief,
         fc, fp, fr, tl, tr,
         multisim) = trip.eval("studio_assign.%sim_brief%",
                       "studio_assign.%sim_midbrief%",
                       "studio_assign.%sim_debrief%",
                       "studio_assign.%sim_need_fc%",
                       "studio_assign.%sim_need_fp%",
                       "studio_assign.%sim_need_fr%",
                       "studio_assign.%sim_need_tl%",
                       "studio_assign.%sim_need_tr%",
                       "studio_assign.%sim_is_multi%")
  
        comp = (fc, fp, fr, tl, tr)
        briefings = (brief, midbrief, debrief)

        try:
            Cui.CuiReplicateChains(Cui.gpc_info, 0)
        except Exception:
            Cui.CuiUnmarkAllLegs(Cui.gpc_info, cui_area, 'WINDOW')
            Errlog.log("copy_roll_out.py:: User cancelled operation")
            return 0

        Cui.CuiSyncModels(Cui.gpc_info)
      
        trip_ids = Cui.CuiGetTrips(Cui.gpc_info, cui_area, "marked")
 
        for crr_id in trip_ids:
            trip = HelperFunctions.TripObject(str(crr_id), cui_area)

            (has_exception,
             legs) = trip.eval("studio_assign.%has_sim_exception%",
                       R.foreach(R.iter("iterators.leg_set",
                                        where="leg.%is_simulator%"),
                                 "leg.%udor%",
                                 "leg.%uuid%"))

            # Update the rolled out SIMs, except the original one
            if crr_id <> orig_crr_id:
                SIM._update_sim(legs, comp, briefings, multisim)

        Cui.CuiUnmarkAllLegs(Cui.gpc_info, cui_area, 'WINDOW')


#########################################################################
# Wrapper for refresh in Planning Studio.
# Needed to correctly refresh in fileplan mode.
#########################################################################

def refresh_planning():
    if HelperFunctions.isDBPlan():
        csl.evalExpr('PythonRunFile("Refresh.py")')
    else:
        try:
            Cui.CuiApuInit()
        except Exception, e:
            print "Exception: ", e

        try:
            Cui.CuiRefreshPlans(Cui.gpc_info, 0)
        except Exception, e:
            print "Exception: ", e

        try:
            Cui.CuiReloadTables(Cui.CUI_RELOAD_TABLES_NO_FORCE)
            Cui.gpc_reset_required_cc(Cui.gpc_info)
        except Exception, e:
            print "Exception: ", e

        try:
            Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
        except Exception, e:
            print "Exception: ", e



def build_udt_doc():
    """ Builds the functional reference 
    
    """    
    return subprocess.call(['python', os.path.expandvars('$CARMUSR/bin/shell/doc.py')])
    

FUNC_REF_HTML = os.path.expandvars("$CARMUSR/docs/functional_reference/html/index.html")
def display_func_ref():
    """ Displays the functional reference in HTML (Only the parts that been moved to UDT)
    
    """
    if build_udt_doc() == 0:
        Cui.CuiStartExternalBrowser(FUNC_REF_HTML, "ABS")
    else:
        cfhExtensions.show("Cannot build functional reference.", title="Error")

TROUBLE_SHOOTING_GUIDE_HTML = os.path.expandvars("$CARMUSR/docs/planning_tracking_trouble_shooting_guide/html/index.html")
def display_trouble_shooting_guide():
    """ Displays the trouble shooting guide
    
    """
    if build_udt_doc() == 0:
        Cui.CuiStartExternalBrowser(TROUBLE_SHOOTING_GUIDE_HTML, "ABS")
    else:
        cfhExtensions.show("Cannot build Trouble Shooting Guide.", title="Error")

PAIRING_HELP_HTML = os.path.expandvars("$CARMSYS/data/doc/UserHelpPairing/wwhelp.htm")
def display_pairing_guide():
    """ Displays the pairing guide
    
    """
    if build_udt_doc() == 0:
        Cui.CuiStartExternalBrowser(PAIRING_HELP_HTML, "ABS")
    else:
        cfhExtensions.show("Cannot build Pairing Help", title="Error")
        

#########################################################################
# Wrapper function for CuiCopyCrrActivity in Planning
# After copying/moving a PACT to a roster, the location of the PACT
# is set to the home airport of the destination roster
#########################################################################

def menu_copy_move_activity(cat=None, pos=None, cm=None):
    print "cm, cat, pos = %s %s %s" % (cm, cat, pos)
    # If the object is not a PACT, use CuiCopyCrrActivity in the usual fashion
    try:
        objPact = Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'report_common.%all_pact_no_grnd%')
    except:
        print "MenuCommandsExt.menu_copy_move_activity:: Could not retrieve Rave variables"
        return

    if not objPact:
        if cm == "copy":
            try:
                Cui.CuiCopyCrrActivity(Cui.gpc_info, cat, pos)
            except:
                print "MenuCommandsExt.menu_copy_move_activity:: CuiCopyCrrActivity cancelled"
                return
        else:
            try:
                Cui.CuiMoveCrrActivity(Cui.gpc_info, "", "")
            except:
                print "MenuCommandsExt.menu_copy_move_activity:: CuiMoveCrrActivity cancelled"
                return
    else:
        # If the object is a PACT this customized copy/move is used to make the location of the PACT
        # change according to the home airport of the crew(s)
        
        # Get variables from current object
        legId     = Cui.CuiCrcEvalInt(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg_identifier')
        legCode   = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%code%')
        groupCode = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%group_code%')
        
        start = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%start_utc%')
        start = AbsTime(start)
        
        legTime   = Cui.CuiCrcEvalReltime(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%time%')
        legTime   = RelTime(legTime)

        R.param("studio_config.%selected%").setvalue(legId)
        HelperFunctions.redrawAreas()

        if cm == "copy":
             while(True):
                try:
                    select_and_create_pact(legCode, groupCode, start, legTime)
                except HelperFunctions.RosterSelectionError:
                    break
        else:
            try:
                if select_and_create_pact(legCode, groupCode, start, legTime):
                    Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(legId))
                    Cui.CuiRemoveLeg(Cui.gpc_info)
            except HelperFunctions.RosterSelectionError:
                pass
        R.param("studio_config.%selected%").setvalue(-1)
        HelperFunctions.redrawAreas()        

def select_and_create_pact(code, groupCode, startutc, duration):
    ''' Creates a PACT on the roster and day the user selects '''
    
    area, crew, time = HelperFunctions.roster_selection(interactive=False)

    crew_object = HelperFunctions.CrewObject(crew, area)
    base,starthb = crew_object.eval('crew.%homeairport%',
                                    'crew.%%hb_time%%(%s)'% startutc)
    
    start = time.day_floor() + starthb.time_of_day()
    end = start + duration
    
    try:
        Cui.CuiCreatePact(Cui.gpc_info, crew, code, groupCode, start, end, base, 0)
        return True
    except:
        print "MenuCommandsExt.menu_copy_move_activity:: CuiCreatePact cancelled"
        return False

               
# __main__ ==============================================================={{{1
if __name__ == '__main__':
    pass    


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
