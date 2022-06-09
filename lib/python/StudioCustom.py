#
# Customized initialization for Studio
# Imported from the standard Studio startup file.
#

print "StudioCustom:: starting to load customized modules..."

import traceback

# Patching AbsTime
import AbsTime
import AbsTime_patch

import os
import sys

def IMPORT_SK(module):
    """
    Wrapper in order to make the system continue importing
    modules if for some reason it fails when starting up.

    You cannot do an try - except.
    """
    try:
        importStatement = 'import %s' % module
        exec importStatement in globals()
    except:
        print importStatement + ' FAILED!'
        try:    traceback.print_exc()
        except: pass

def IMPORT_SK_UNPROTECTED(module):
    """
    'Unsafe' import wrapper. It is prefereable to use
    this one over the safe version, since using that
    will 'hide' a broken python environment'
    """
    importStatement = 'import %s' % module
    exec importStatement in globals()

def UNWRAP_CUI_FUNCTION(func):
    """
    Remove CuiBypassWrapper from Cui functions that should not have had them.
    Used as workaround for CARMSYS bugs.
    """
    try:
        import Cui, _Cui
        if not hasattr(Cui, func) or not hasattr(_Cui, func):
            print "UNWRAP_CUI_FUNCTION Warning: Cui function",func,"not found"
            return
        f = getattr(Cui, func)
        of = getattr(_Cui, func)
        setattr(Cui, func, of)
    except:
        import traceback
        traceback.print_exc()
        print "UNWRAP_CUI_FUNCTION Warning: Unable to unwrap Cui function",func

###############################
# Standard user modules
IMPORT_SK_UNPROTECTED('utils.AreaSort')
IMPORT_SK_UNPROTECTED('MenuCommandsExt')
IMPORT_SK_UNPROTECTED('ImportCommandsExt')
IMPORT_SK_UNPROTECTED('Localization')
IMPORT_SK_UNPROTECTED('Cui')
IMPORT_SK_UNPROTECTED('carmusr.Assign')
IMPORT_SK_UNPROTECTED('carmusr.SelectCrew as SelectCrew')
IMPORT_SK_UNPROTECTED('carmusr.SelectCrewForm as SelectCrewForm')
IMPORT_SK_UNPROTECTED('utils.DisplayReport')
IMPORT_SK_UNPROTECTED("carmusr.StartStudio")

###############################
# Common CMS functionality CARMSYS
# needed for Product Cas and Cct
# to behave the same

IMPORT_SK_UNPROTECTED('StartTableEditor')
IMPORT_SK_UNPROTECTED('carmensystems.mirador.tablemanager') # Needed for Java-XML forms in planning
IMPORT_SK_UNPROTECTED('carmensystems.studio.services.Command') # Needed for Java-XML forms in planning

##############################
# Common CMS functionality CARMUSR

IMPORT_SK_UNPROTECTED('carmusr.modcrew')
IMPORT_SK_UNPROTECTED('carmusr.AddonMenus')
IMPORT_SK_UNPROTECTED('carmusr.tracking.Standby as Standby')
IMPORT_SK_UNPROTECTED('carmusr.tracking.Annotations as Annotations')
IMPORT_SK_UNPROTECTED('carmusr.MiniSelect as MiniSelect')
IMPORT_SK_UNPROTECTED('carmusr.rule_exceptions')
IMPORT_SK_UNPROTECTED('carmusr.crewinfo.CrewInfo as CrewInfo')
IMPORT_SK_UNPROTECTED('carmusr.CrewBlockHours as CrewBlockHours')

IMPORT_SK_UNPROTECTED('carmusr.FileHandlingExt')
IMPORT_SK_UNPROTECTED('carmusr.Accumulators as Accumulators')
IMPORT_SK_UNPROTECTED('carmusr.accumulators_manual as accumulators_manual')
IMPORT_SK_UNPROTECTED('carmusr.AccountHandler')
IMPORT_SK_UNPROTECTED('carmusr.AccountView')
IMPORT_SK_UNPROTECTED('carmusr.CrewTableHandler')
IMPORT_SK_UNPROTECTED('carmusr.CrewTraining')
IMPORT_SK_UNPROTECTED('carmusr.AttributesForm')
#IMPORT_SK_UNPROTECTED('carmusr.FlightAttributes')
IMPORT_SK_UNPROTECTED('carmusr.Attributes')
IMPORT_SK_UNPROTECTED('carmusr.training_attribute_handler')
IMPORT_SK_UNPROTECTED('carmusr.HelperFunctions')
IMPORT_SK_UNPROTECTED('carmusr.CrewAuditTrail as CrewAuditTrail')
IMPORT_SK_UNPROTECTED('carmusr.ActivityManipulation')
IMPORT_SK_UNPROTECTED('carmusr.ConfirmSave')
IMPORT_SK_UNPROTECTED('carmusr.trip_area_handler')
IMPORT_SK_UNPROTECTED('carmusr.sim_exception_handler')
IMPORT_SK_UNPROTECTED('carmusr.SKLegAuditTrail')
IMPORT_SK_UNPROTECTED('carmusr.CrewRest as CrewRest')
IMPORT_SK_UNPROTECTED('utils.mnu')
IMPORT_SK_UNPROTECTED('utils.mnu as mnu')

###############################
# Modules for tracking (CCT)
IMPORT_SK_UNPROTECTED('os')
if os.path.expandvars("$PRODUCT").lower() == "cct":
  IMPORT_SK_UNPROTECTED('carmusr.tracking.CommandlineCommands')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.DragDrop as DragDrop')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.CheckInOut as CheckInOut')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.ReportSickFunctions as ReportSickFunctions')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.FindAssignableCrew as FindAssignableCrew')
  #IMPORT_SK_UNPROTECTED('carmusr.tracking.CallOutListFunctions as CallOutListFunctions')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.CrewNotificationFunctions as CrewNotificationFunctions')
 # IMPORT_SK_UNPROTECTED('carmusr.tracking.SaveSASPlan as SaveSASPlan')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.WarningPopUpControl as WarningPopUpControl')
  IMPORT_SK_UNPROTECTED('carmusr.paxlst.mmi')
  IMPORT_SK_UNPROTECTED('salary.mmi')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.HotelBookingReport')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.TransportBookingReport')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.TransportBookingUpdatedReport')
  IMPORT_SK_UNPROTECTED('hotel_transport.HotelBookingRun')
  IMPORT_SK_UNPROTECTED('hotel_transport.TransportBookingRun')
  IMPORT_SK_UNPROTECTED('passive.passive_bookings')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.ConflictReport')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.BuyDays')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.BaseBreak as BaseBreak')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.LegServiceNeed as LegServiceNeed')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.DutyPointsReport')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.FlightCrewList')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.OrderedMeals')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.Transport as Transport')
  IMPORT_SK_UNPROTECTED('carmusr.AccumulatorsTable as AccumulatorsTable')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.CfhExtension as CfhExtension')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.FlightProperties as FlightProperties')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.Publish as Publish')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.Rescheduling as Rescheduling')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.ReschedulingUpdate as ReschedulingUpdate')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.SetInstructorTag as SetInstructorTag')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.AlertTimeOverride as AlertTimeOverride')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.f3_overtime_replacement as f3_overtime_replacement')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.fxx_boughtday_replacement as fxx_boughtday_replacement')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.DeadHead')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.ChangePosition')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.Deassign')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.handover_report')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.GetTransport')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.TripTools')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.PlanningGroupSelect')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.NopCrewData')
  IMPORT_SK_UNPROTECTED('carmusr.ground_duty_handler')
  IMPORT_SK_UNPROTECTED('carmusr.SBHandler')
  IMPORT_SK_UNPROTECTED('carmusr.Cimber')
  IMPORT_SK_UNPROTECTED('carmusr.tracking.duty_break_handler as duty_break_handler')
  IMPORT_SK_UNPROTECTED('salary.PerDiemExport')
  IMPORT_SK_UNPROTECTED('carmusr.planning.SelectCrewTrainingForm') 


  IMPORT_SK_UNPROTECTED('crewinfoserver.menues')

  # Temporary SYS development by dle
  IMPORT_SK_UNPROTECTED('carmusr.Assign as Assign')

  # Temporary Integration Test imports
  IMPORT_SK_UNPROTECTED('carmtest.TestIntegrationReports as TestIntegrationReports')

  # Register our GUI Extension class
  import carmensystems.studio.gui.StudioGui
  import TrackingGuiExt
  myGuiExtension = TrackingGuiExt.TrackingGuiExt()
  carmensystems.studio.gui.StudioGui.registerStudioGui(myGuiExtension)

###############################
# Modules for pre-planning
if os.path.expandvars("$SK_APP").lower() == "preplanning":
  IMPORT_SK_UNPROTECTED('carmusr.preplanning.Publish')
  IMPORT_SK_UNPROTECTED('carmusr.preplanning.actions')
  IMPORT_SK_UNPROTECTED('carmensystems.studio.gui.private.StudioTimeInit') # To get now keyword
  IMPORT_SK_UNPROTECTED('carmusr.planning.SelectCrewTrainingForm')
# Needed for Performance Tests, shell variable set by runperftest.sh
if bool(os.environ.get('CARM_PERF_TEST',False)):
  IMPORT_SK_UNPROTECTED('carmtest.SaveTests')
  IMPORT_SK_UNPROTECTED('carmtest.RefreshTests')
  IMPORT_SK_UNPROTECTED('carmtest.Tests')


###############################
# Modules for planning (CCP/CCR)
if os.path.expandvars("$SK_APP").lower() == "planning":
  IMPORT_SK_UNPROTECTED('carmensystems.studio.gui.private.StudioTimeInit')
  IMPORT_SK_UNPROTECTED('carmusr.planning.SelectCrewTrainingForm')
  IMPORT_SK_UNPROTECTED('carmusr.BuildAcRotations as BuildAcRotations')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.Fairness as Fairness')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.Bids as Bids')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.create_F36_targets as create_F36_targets')
  IMPORT_SK_UNPROTECTED('carmusr.AssignActivities')
  IMPORT_SK_UNPROTECTED('carmusr.planning.ExportScenarios')
  IMPORT_SK_UNPROTECTED('carmusr.planning.ExportScenariosSVS')
  IMPORT_SK_UNPROTECTED('carmusr.pairing.CopyTrips322')
  IMPORT_SK_UNPROTECTED('carmusr.pairing.NopToOag')
  IMPORT_SK_UNPROTECTED('carmusr.pairing.retiming')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.Publish')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.PrepareForJCTImport')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.UpdatePublishAccumulators')
  IMPORT_SK_UNPROTECTED('carmusr.planning.MultiLegToTrip')
  IMPORT_SK_UNPROTECTED('carmusr.planning.SplitNightStops')
  IMPORT_SK_UNPROTECTED('carmusr.TripAuditTrail')
  IMPORT_SK_UNPROTECTED('adhoc.ScriptRunner')
  IMPORT_SK_UNPROTECTED('adhoc.ScriptRunner')
  IMPORT_SK_UNPROTECTED('carmstd.report_generation')
  IMPORT_SK_UNPROTECTED('report_sources.hidden.DutyPointsReport')
  IMPORT_SK_UNPROTECTED('carmusr.SBHandler')
  IMPORT_SK_UNPROTECTED('carmusr.FindBidTrips as FindBidTrips')
  IMPORT_SK_UNPROTECTED('carmusr.rostering.create_cabin_training_table')
  IMPORT_SK_UNPROTECTED('carmusr.GenerateCrewBidOutcomePDFs')
  IMPORT_SK_UNPROTECTED('carmusr.calibration.gui')  # @UnusedImport
  IMPORT_SK_UNPROTECTED('carmusr.rostering.export_duty_day_base_constraints')
  IMPORT_SK('carmusr.dynamic_menus')  # @UnusedImport
  IMPORT_SK('carmstd.select')  # @UnusedImport
  IMPORT_SK_UNPROTECTED('carmusr.FetchSVS')

print "StudioCustom:: loading finished."

print os.environ

# eof
