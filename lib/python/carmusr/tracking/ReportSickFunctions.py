
# -*- coding: latin-1 -*-
# [acosta:06/317@10:33] Added coding. coding has to be on first or second row.
"""
Implementation of Report-Sick and Toggle-Report-Back functionality.
"""

import os
import time

import Cui
import Cfh
import Errlog
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import carmensystems.rave.api as r

import MenuCommandsExt
import carmstd.cfhExtensions as cfhExtensions
import Select
from utils.rave import RaveEvaluator
from utils.rave import RaveIterator
import carmusr.HelperFunctions as HF
import carmusr.tracking.Publish as Publish
from tm import TM
                                    
def reportSick(deadheadHome, sickCode):
    """
    Main report sick function.
    Allows a user to report crew sick for a user specified period.
    Fucntion finds deadhead flight home if deadheadHome is true and sick period
    starts away from homebase.
    """
    
    # Let user select a crew's sickness period
    selected_crew = RosterHaircrossSelection()
    if not selected_crew.isValidSelection():
        return 1

    # Deassign all activity within the selected period in order to make room
    #   for a deadhead.
    # Also to make sure the creation of sickness pacts won't fail later on.
    
    if not selected_crew.removeActivityInPeriod():
        return 1

    # Let user choose a deadhed to get home or to the next station after the
    # illness on the roster.
    # Adjust the selected period, so it starts after the deadhead.

    if deadheadHome:
        # (Don't care whether a dh was inserted or not)
        selected_crew.insertDeadheadHomeOrToConnection()
    
    # Insert pacts with proper IL-codes in the selected period
    selected_crew.createSickPeriods(sickCode)
    selected_crew.markInformed()
    
    return 0
    
def toggleReportBack():
    """
    Function to toggle report-back attribute on IL-day.
    Currently handled through separate activity codes:
        IL->ILR, IL4->IL4R, LA91->LA91R, ...
    """

    while True:
        try:
            crew_area, crew_id, time_utc = HF.roster_selection()
        except:
            return 1

        selected_crew = RaveEvaluator(crew_area, Cui.CrewMode, crew_id,
            is_object="studio_process.%%click_is_object%%(%s)" % time_utc,
            is_locked="studio_process.%%click_is_locked%%(%s)" % time_utc,
            is_illoa="studio_process.%%click_is_illness_or_loa%%(%s)" % time_utc,
            is_report_back="studio_process.%%click_is_report_back%%(%s)" % time_utc,
            can_report_back="studio_process.%%click_can_report_back%%(%s)" % time_utc,
            station="studio_process.%%click_station%%(%s)" % time_utc,
            start_hb="studio_process.%%click_day_start%%(%s)" % time_utc,
            end_hb="studio_process.%%click_day_end%%(%s)" % time_utc,
            code="studio_process.%%click_code%%(%s)" % time_utc,
            toggled_code="studio_process.%%click_toggled_report_back_code%%(%s)" % time_utc,
            )

        if not (selected_crew.is_object and selected_crew.is_illoa):
            if not cfhExtensions.confirm(
                "Please click on the preferred day of a crew illness object.\n\n"
                "Continue?"):
                return 1
        elif selected_crew.is_locked:
            if not cfhExtensions.confirm(
                "Report Back not possible.\n"
                "Cannot update a locked activity.\n\n"
                "Continue?"):
                return 1
        elif not (selected_crew.is_report_back or selected_crew.can_report_back):
            if not cfhExtensions.confirm(
                "Report Back not possible.\n"
                "The activity (%s) has no defined report-back code.\n\n"
                "Continue?" % selected_crew.code):
                return 1
        else:
            # Instead of toggling report-back on the clicked-on IL activity,
            #   we create a new one-day IL activity overlapping the old one.
            # This is because CuiCreatePact handles cutting of existing 
            #   activities correctly, so for a multi-day IL object
            #   only the clicked-on day will get the "R" flag. 
            
            cuiCreatePact(area=crew_area,
                          crew_id=crew_id,
                          station=selected_crew.station,
                          start=selected_crew.start_hb,
                          end=selected_crew.end_hb,
                          code=selected_crew.toggled_code,
                          cut_overlaps=True)
            return 0
    
def cuiCreatePact(area, crew_id, station, start, end, code, cut_overlaps):
    def create(cut):
        """
        If there were unforseen overlaps, we let the sys do
        the cutting instead. The reason for this two-step approach
        is performance; with sys cutting CuiCreatePact may take 1s,
        without it's about 1/100s... 
        """
        overlap_flag = bool(cut) * Cui.CUI_CREATE_PACT_REMOVE_OVERLAPPING_LEGS
        Cui.CuiCreatePact(Cui.gpc_info,
                          crew_id,
                          code,
                          "",
                          (start + RelTime(0,1)).getRep(),  # +00:01 to avoid overlaps where < or > are used.
                          end.getRep(),
                          station,
                          overlap_flag |
                          Cui.CUI_CREATE_PACT_DONT_CONFIRM |
                          Cui.CUI_CREATE_PACT_SILENT |
                          Cui.CUI_CREATE_PACT_NO_LEGALITY |
                          Cui.CUI_CREATE_PACT_TASKTAB)
    try:
        retried = ""
        t = time.time()
        if cut_overlaps:
            create(True)
        else:
            try:
                create(False)
            except:
                # Retry: If there were unforseen overlaps, we let the sys do
                # the cutting instead. The reason for this two-step approach
                # is performance; with sys cutting CuiCreatePact may take 1s,
                # without it's about 1/100s... 
                retried = "+True"
                create(True)

        Cui.CuiSyncModels(Cui.gpc_info)
        t = time.time() - t
    finally:
        print "+++ cuiCreatePact [%s@%s %s-%s] cut_overlaps=%s%s, %ss" \
              % (code, station, start, end, cut_overlaps, retried, t)
   
        
class RosterHaircrossSelection(RaveEvaluator):
    def __init__(self):
        self.area = self.crew_id = self.start_hb = self.end_hb = self.any_lock = None
            
        try:
            sel = HF.RosterTimeSelection()
        except:
            return
        self.area = sel.area
        self.crew_id = sel.crew
        start_utc = sel.st
        end_utc = sel.et

        RaveEvaluator.__init__(self, self.area, Cui.CrewMode, self.crew_id)
        self.rEvalObj(any_lock='studio_process.%%crew_any_locked_in_period%%(%s,%s)' % (start_utc, end_utc),
                      home_stn='studio_process.%%crew_base_station_at_date%%(%s)' % (start_utc),
                      start_hb='studio_process.%%crew_startpoint_hb_adjusted_to_legs%%(%s)' % (start_utc),
                        end_hb='studio_process.%%crew_endpoint_hb_adjusted_to_legs%%(%s)' % (end_utc),
                      prev_leg='studio_process.%%crew_leg_before%%(%s)' % (start_utc),
                     start_stn='studio_process.%%crew_prev_arrival_station_before%%(%s)' % (start_utc),
                     start_inf='studio_process.%%report_sick_auto_inform_start%%(%s, %s)' % (start_utc, end_utc),
                       end_inf='studio_process.%%report_sick_auto_inform_end%%(%s, %s)' % (start_utc, end_utc),                     
            )
        if not self.home_stn:
            cfhExtensions.show("Unable to determine home base for crew.")
            return
        self.rEvalObj(duty_days='studio_process.%%crew_duty_day_types_in_hb_period%%(%s,%s)' % (self.start_hb,self.end_hb),
                 legs_to_remove='studio_process.%%crew_legs_to_remove_in_hb_period%%(%s,%s)' % (self.start_hb,self.end_hb),
                    legs_to_cut='studio_process.%%crew_legs_to_cut_in_hb_period%%(%s,%s)' % (self.start_hb,self.end_hb),
                      start_utc='station_utctime("%s",%s)' % (self.home_stn,self.start_hb),
                        end_utc='station_utctime("%s",%s)' % (self.home_stn,self.end_hb),
                dh_avail_end_hb='studio_process.%%crew_leg_after_start_hb%%(%s)' % (self.end_hb),
                        now_utc='fundamental.%now%',
            )
                      
    def __str__(self):
        if not self.isValidSelection():
            return "<%s NO SELECTION>" % self.__class__.__name__
        else:
            return RaveEvaluator.__str__(self)

    def isValidSelection(self):
        if self.any_lock:
            cfhExtensions.show("Attempt to perform operation on locked object.\n"
                               "To be able to perform this operation,\n"
                               "please unlock it first.")
            
        return not (self.area is None or
                    self.crew_id is None or
                    self.start_hb is None or
                    self.end_hb is None or
                    self.home_stn == "None" or
                    self.any_lock)
                    
    def createPact(self, start, end, code, cut_overlaps):
        cuiCreatePact(area=self.area,
                      crew_id=self.crew_id,
                      station=self.home_stn,
                      start=start,
                      end=end,
                      code=code,
                      cut_overlaps=cut_overlaps)
         
    def removeActivityInPeriod(self):
        """
        Remove activity in the period, in order to make space for inserting 
        a deadhead home anytime within the period.
        """
        try:
            if self.legs_to_remove or self.legs_to_cut:
                
                # Display the roster in CuiScriptBuffer.
                
                Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                           Cui.CuiScriptBuffer,
                                           Cui.CrewMode,
                                           Cui.CrewMode,
                                           [self.crew_id],
                                           0)

                # Remove all legs that are entirely within the period.
                
                if self.legs_to_remove:
                    marked = HF.getMarkedLegs(Cui.CuiScriptBuffer)
                    HF.unmarkAllLegs(Cui.CuiScriptBuffer)
                    HF.markLegs(Cui.CuiScriptBuffer, self.legs_to_remove)
                    Cui.CuiRemoveAssignments(
                        Cui.gpc_info, Cui.CuiScriptBuffer, self.crew_id,
                        Cui.CUI_MOVE_ASMT_SILENT)
                    HF.markLegs(Cui.CuiScriptBuffer, marked, self.legs_to_remove)

                # Adjust any pact that overlaps the illness end.
                # (Might be more than one if there are overlaps on the roster.)                    

                if self.legs_to_cut:
                    for legid in self.legs_to_cut.strip(',').split(','):
                        Cui.CuiSetSelectionObject(
                          Cui.gpc_info, Cui.CuiScriptBuffer, Cui.LegMode, legid)
                        sd, st = str(self.end_utc).replace(':', '').split(' ')
                        Cui.CuiUpdateTaskLeg(
                            {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
                            {'FORM':'TASK_LEG','START_DATE': sd},
                            {'FORM':'TASK_LEG','DEPARTURE_TIME': st},
                            {'FORM':'TASK_LEG','OK': ''},
                            Cui.gpc_info, Cui.CuiScriptBuffer, "object",
                            Cui.CUI_UPDATE_TASK_RECALC_TRIP |
                            Cui.CUI_UPDATE_TASK_SILENT |
                            Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK |
                            Cui.CUI_UPDATE_TASK_TASKTAB)
                    
                    # Adjust dh-assignable period according to the modified pact
                    self.dh_avail_end_hb = self.end_utc
                    
            return True
        except:
            cfhExtensions.show('Could not perform deassign operation.\n'
                               'Please deassign roster activities manually.')
            return False

    def insertDeadheadHomeOrToConnection(self):
        """
        Select leg before user-selected period.
        Let user choose a deadhead after the selected leg.
        """

        if not self.prev_leg \
        or self.start_stn == self.home_stn:
            return False

        Cui.CuiSetSelectionObject(Cui.gpc_info, self.area, Cui.LegMode, str(self.prev_leg))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.area, 'OBJECT')
        
        if MenuCommandsExt.getFilteredNextPrevDH(
               anyAirport=False,
               noStartBeforeUtc=max(self.start_utc, self.now_utc)) != 0:
            return False
        
        # Adjust user-selected period to start after the deadhead.
        # Adjust 'self.duty_days' so it still covers the adjusted period only.
        self.rEvalInit() # Must reset context & selection after the above operation
        old_start_date = AbsDate(self.start_hb)
        self.rEvalObj(start_hb='studio_process.%%crew_startpoint_hb_adjusted_to_added_dh%%(%s,%s)' \
                               % (self.start_hb,self.dh_avail_end_hb))
        new_start_date = AbsDate(self.start_hb)
        while old_start_date < new_start_date:
            self.duty_days = self.duty_days[1:]
            old_start_date += RelTime(24, 0)
        return True
    
# This (or similar) would have to be used to handle sickness on out-station!!!
# def hbTimeAsLocal(self, time_hb, station):
#     values = self.rEvalList(['station_localtime("%s",station_utctime("%s",%s)' \
#                              % (station, self.home_stn, time_hb)])
#     return values[0]

    def createSickPeriods(self, sick_code='IL'):
        """
        Creates sick day periods between start time and end time.
        Any activity during the period will be removed (existing pacts'
            start/end times are adjusted, if nescessary).
        """
        
        if self.start_hb >= self.end_hb:
            print "*** No time to be sick in", self.start_hb, "-", self.end_hb
            return
        
        from_day = 0
        last_day = len(self.duty_days) - 1

        start_date = AbsTime(self.start_hb).day_floor()
        end_date = AbsTime(self.end_hb).day_ceil()

        # Part-day illness: the code for sick_code "IL" is "IL7".
        # For "LA91", it's "LA92". In other cases it's the same as the sick_code.
        # UF: For now there is no specific part unfit code but it's still possible to be partly unfit.
        partial_sick_code = {"IL":"IL7", "LA91":"LA92", "UF":"UF"}.get(sick_code, sick_code)
        
        # Create partial sickness -start- day (if applicable)
        
        if self.start_hb > start_date:
            self.createPact(start=self.start_hb,
                            end=min(start_date + RelTime(24, 0), self.end_hb),
                            code=partial_sick_code,
                            cut_overlaps=False)
            from_day += 1
            
        # Create partial sickness -end- day (if applicable)
        
        if from_day <= last_day and self.end_hb < end_date:
            self.createPact(start=end_date - RelTime(24, 0),
                            end=self.end_hb,
                            code=partial_sick_code,
                            cut_overlaps=False)
            last_day -= 1
        
        # Create -full- day periods (multi-day if possible):
        #   "IL12"     for long-term illness
        #   "IL4"      for off-duty short-term
        #   sick_code  for on-duty short-term
        
        def IL_code(day_code):
            return {"L": "IL12", "D": sick_code}.get(day_code, "IL4")
        while from_day <= last_day:
            duty_code = IL_code(self.duty_days[from_day])
            to_day = from_day + 1
            while to_day <= last_day \
              and IL_code(self.duty_days[to_day]) == duty_code:
                to_day += 1
            self.createPact(start=start_date + RelTime(from_day*24, 0),
                            end=start_date + RelTime(to_day*24, 0),
                            code=duty_code,
                            cut_overlaps=False)
            from_day = to_day
            
    def markInformed(self):
        Publish.add_informed_period(self.crew_id, self.start_inf, self.end_inf)
