#
# Module for initializing the Studio menu states.
#

#
# Notes:
# - Must be named $CARMUSR/lib/python/CustomMenuStates.py,
#     in order to override $CARMSYS/lib/python/CustomMenuStates.py
# - For isActive() methods, return value:
#     0 -> not active
#     1 -> active
#

import os
import traceback

import Cui
import MenuState
import Errlog
import carmusr.application as application

###########################
# Setup CARMSYS Menu States
###########################

try:
    # This one is only available on tracking CARMSYS, only then
    if application.isTracking or application.isDayOfOps:
        import carmensystems.studio.Tracking.TrackingMenuStates
        carmensystems.studio.Tracking.TrackingMenuStates.standardInit()
    else:
        import TopMenuStates
        TopMenuStates.standardInit()
except:
    Errlog.log("CustomMenuStates Failed to initialize")
    traceback.print_exc()

###########################
# Setup CARMUSR Menu States
###########################

class PopupMenuState(MenuState.MenuState):
    isTracker = application.isTracking or application.isDayOfOps
    ravevar = None
    
    def __init__(self,name,ravevar):
        self.ravevar = ravevar
        MenuState.MenuState.__init__(self,[name],MenuState.POPUP_EVENT)
    
    def alwaysActive(self):
        # return (not self.manager.rulesetLoaded) | (not self.manager.useContextSensitiveMenus)
        return 0
    
    def objectSelected(self):
        try:
            Cui.CuiCrcEvalInt(Cui.gpc_info, Cui.CuiWhichArea, "OBJECT", "leg_identifier")
            return 1
        except:
            return 0
            
    #def isTrip(self):
    #    return not (self.manager.personalActivity | self.manager.protectedActivity)
    
    def isActive(self):
        if self.alwaysActive(): return 1
        if not self.objectSelected(): return 0
        #if not self.isTrip(): return 0
        try:
            active = Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, "OBJECT",self.ravevar)
            #print "CustomMenuStates::%s::isActive (%s)=%s" % (self.__class__.__name__, self.ravevar, active)
            return active
        except:
            #print "CustomMenuStates::%s::isActive (%s) FAILED" % (self.__class__.__name__, self.ravevar) 
            return 0

class PopupMenuStateEnv(MenuState.MenuState):
    """
    PopupMenuState which looks if environmental variable is defined
    NOTE: Menu item is active unless variable defined
    
    """
    variable = None
    def __init__(self,name,variable):
        self.variable = variable
        MenuState.MenuState.__init__(self,[name],MenuState.POPUP_EVENT)
    def isActive(self):
        if not application.isTracking: 
            if not application.isDayOfOps:
                return 0

        return not bool(os.environ.get(self.variable))

class PopupMenuStateProduct(MenuState.MenuState):
    """
    PopupMenuState checks current ruleset for product
    
    """
    def __init__(self,name,products):
        self._products = products
        MenuState.MenuState.__init__(self,[name],MenuState.POPUP_EVENT)
    def isActive(self):

        current_product = application.get_product_from_ruleset()
        if current_product:
            return  current_product.upper() in \
                   [product.upper() for product in self._products]
        else:
            return 0

class AnyCrewIsMarked(MenuState.MenuState):
    """Tell if any crew member is marked, used by batch annotations."""
    def __init__(self):
        """Register POPUP event at init."""
        MenuState.MenuState.__init__(self, ['AnyCrewIsMarked'],
                MenuState.POPUP_EVENT)

    def isActive(self):
        """POPUP event: Active if any crew member is marked."""
        try:
            return Cui.CuiAnyMarkedCrew(Cui.gpc_info, Cui.CuiWhichArea)
        except:
            return 0

class CanSwapActivities(MenuState.MenuState):
    """If activities are selected from two rosters."""
    def __init__(self):
        """Register POPUP event at init."""
        MenuState.MenuState.__init__(self, ['CanSwapActivities'],
                MenuState.POPUP_EVENT)

    def isActive(self):
        try:
            import carmusr.tracking.DragDrop as DD
            return DD.can_swap_activities()
        except:
            traceback.print_exc()
            return 0


class OpenWaveForms(MenuState.MenuState):
    """Tell if there are open wave forms"""
    
    def __init__(self):
        """Register POPUP event at init."""
        MenuState.MenuState.__init__(self, ['OpenWaveForms'],
                MenuState.ACTION_EVENT)

    def isActive(self):
        import utils.wave
        import StartTableEditor
        
        dbplan = MenuState.theStateManager.menuStateDict['IsDatabaseSubPlan']
        
        if utils.wave.STANDALONE or not dbplan:
            return 0
        else:
            crewInfo = '$CARMUSR/data/form/crew_info.xml'
            crewAccounts = '$CARMUSR/data/form/leave_accounts.xml'
            crewTraining = '$CARMUSR/data/form/crew_training.xml'
            crewBlock = '$CARMUSR/data/form/crew_block_hours.xml'

            if str(StartTableEditor.getFormState(crewInfo)).lower() not in ('none', 'error'):
                return 1
            elif str(StartTableEditor.getFormState(crewAccounts)).lower() not in ('none', 'error'):
                return 1       
            elif str(StartTableEditor.getFormState(crewTraining)).lower() not in ('none', 'error'):
                return 1
            elif str(StartTableEditor.getFormState(crewBlock)).lower() not in ('none', 'error'):
                return 1
            else:
                return 0



try:

    # Register CARMUSR menu states
    if application.isTracking or application.isDayOfOps:            
        PopupMenuState("AnyBaseBreak" ,"base_break.%any_break%")
        PopupMenuState("CanChangeDutyBreak", "not leg.%is_last_in_trip%")
        PopupMenuState("CanBaseBreakBefore", "base_break.%can_break_before%")
        PopupMenuState("CanBaseBreakAfter", "base_break.%can_break_after%")
        PopupMenuState("IsBaseBreakBefore", "base_break.%is_break_before%")
        PopupMenuState("IsBaseBreakAfter", "base_break.%is_break_after%")
        PopupMenuState("IsNotManualDutyBreak" ,"not attributes.%leg_has_duty_break_attribute%")
        PopupMenuState("IsNotManualDutyMerge" ,"not attributes.%leg_has_duty_merge_attribute%")
        PopupMenuState("HasManualDutyAttr" ,"attributes.%leg_has_duty_break_attribute% or attributes.%leg_has_duty_merge_attribute%")
        PopupMenuState("AnyNeedToChange", "crg_crew_pos.%any_need_to_change%")
        PopupMenuState("HasServiceNeedAS",
                       "crg_crew_pos.%has_service_need_and_proper_composition_as%")
        PopupMenuState("HasServiceNeedAH",
                       "crg_crew_pos.%has_service_need_and_proper_composition_ah%")
        PopupMenuState("HasNeedExceptAS",
                       "crg_crew_pos.%has_need_exception_and_proper_composition_as%")
        PopupMenuState("HasNeedExceptAH",
                       "crg_crew_pos.%has_need_exception_and_proper_composition_ah%")
        PopupMenuState("IsCabin", "crew.%is_cabin%")
        PopupMenuState("IsPilot", "crew.%is_pilot%")
       

        PopupMenuState("IsGroundDutyLeg", "leg.%is_ground_duty_leg%")
        PopupMenuState("AllMarkedUnlocked", "not studio_process.%roster_any_marked_locked%")
        PopupMenuState("IsOnDuty", "leg.%is_on_duty%")
        PopupMenuState("IsOffDuty", "not leg.%is_on_duty%")
        PopupMenuState("CanSetLocalTransport", "hotel.%can_set_local_transport%")
        PopupMenuState("NotWholeDay","not leg.%is_whole_day_activity%")
        PopupMenuStateEnv("NotUsingAM", "CARMUSINGAM")
        PopupMenuState("IsInfStandby","standby.%can_restore_standby%")

        PopupMenuState("IsFxxApplicable", "salary_overtime.%is_fxx_replace_applicable%")

        PopupMenuState("IsOperating", "not not_operating")
        PopupMenuState("IsAPIS", "leg.%is_apis%")
        PopupMenuState("NeedHotel", "report_hotel.%need_hotel%")
        PopupMenuState("IsEstimatedBlockOffFrozen", "leg.%has_frozen_estimated_block_off%")
        PopupMenuState("HasCheckIn", "leg.%has_check_in%")
        CanSwapActivities()
    # Enabled for all products (Tracking, Planning, PrePlanning, ...)
    PopupMenuState("Deadhead","leg.%is_deadhead%")
    PopupMenuState("IsFlightDuty", "leg.%is_flight_duty%")
    PopupMenuState("IsLongHaul", "leg.%is_long_haul%")
    PopupMenuState("IsPact", "leg.%is_pact%")
    PopupMenuState("IsCimber", "crew.%has_agmt_group_qa%")
    PopupMenuStateProduct("IsPairing",["CCP"])
    AnyCrewIsMarked()
    OpenWaveForms()

    # Start menu state handling
    MenuState.start()
except:
    Errlog.log("CustomMenuStates::Could not start CustomMenuStates handling")
    traceback.print_exc()
    