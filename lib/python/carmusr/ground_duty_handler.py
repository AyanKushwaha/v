# [acosta:08/227@16:36] Modified form, added training positions.

"""
@date:16Jul2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB

This module is used by Studio menues to create or update a ground duty (ground
task).

A CFH form is launched and the user can create or modify basic properties and
crew complement.
"""

# imports ================================================================{{{1
import Cfh
import Cui
import Gui
import weakref
import carmensystems.rave.api as R
import Errlog
import os

import carmusr.HelperFunctions as HF
import Select

from AbsTime import *
#from AbsDate import AbsDate
from RelTime import RelTime
#from Variable import Variable
from tm import TM
import modelserver
from utils.rave import MiniEval
import carmusr.application as application
import carmusr.modcrew as modcrew
import Attributes

global FORM_KEEP_VALUES
FORM_KEEP_VALUES = False

global GROUND_FORM_PROPERTIES
GROUND_FORM_PROPERTIES = None

# module variables ======================================================={{{1
__all__ = ['manage_ground_duty']
__version__ = "$Revision$"


# classes ================================================================{{{1

# CancelledFormError -----------------------------------------------------{{{2
class CancelledFormError(Exception):
    """User defined Exception which is raised when user presses 'Cancel'."""
    def __str__(self):
        return "Form was cancelled."


# GDCrewNum --------------------------------------------------------------{{{2
class GDCrewNum(Cfh.Number):
    """Number of crew in a position."""
    def __init__(self, *a, **k):
        Cfh.Number.__init__(self, *a, **k)
        self.setMandatory(True)

# GDCrewNumMock ----------------------------------------------------------{{{2
class GDCrewNumMock:
    """Number of crew in a position. Non graphical storage to fit in
       with GDCrewNum components
    """
    def __init__(self, value):
        self._value = value
    def assign(self, value):
        self._value = value
    def valof(self):
        return self._value
    def getValue(self):
        return self._value
        
# GDTimeBaseString -------------------------------------------------------{{{2
class GDTimeBaseString(Cfh.String):
    """Select time base 'UDOP' or 'LDOP'."""
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent
        self.setMandatory(True)
        self.setMenuOnly(True)
        self.setMenuString("Base;UDOP;LDOP")
        self.setTranslation(Cfh.CfhEntry.ToUpper)
        self.setStyle(Cfh.CfhSChoiceCombo)


# GDTaskCodeString -------------------------------------------------------{{{2
class GDTaskCodeString(Cfh.String):
    """Select task code. Allow user to select from codes in 'activity_set'."""
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent
        self.task_codes = {}
        for x in TM.activity_set:
            self.task_codes[x.id] = x.grp.id
        self.setTranslation(Cfh.CfhEntry.ToUpper)
        
    def check(self, value):
        """Return None if value is valid, else text string."""
        if not value in self.task_codes.keys():
            return "Unknown task code (%s)." % value
        elif self.task_codes[value] in ['OPC','AST','ASF','FFS','SIM']:
            #Collect the crew complement from rave table
            self.complementList = []
            for i in range(1,11):
                try:
                    special, = R.eval('crew_pos.%%sim_has_external_instructor%%("%s")' % value)
                    need, = R.eval('crew_pos.%%_sim_need_pos%s%%("%s", %s, %s)' % (i,self.task_codes[value], special, self.parent.save_date))
                    self.complementList.append(need)
                except:
                    self.complementList.append(0)
        else:
            self.complementList = [0,0,0,0,0,0,0,0,0,0]
    
    def compute(self):
        """Update the crew complement if the ground task group
           has any crew complement"""
        if self.getValue() and not self.parent.assigned:
            #self.parent.complement.assign(tuple(self.complementList))
            self.parent.complement.assign(tuple(self.complementList))   # BZ 31706


# GDTripNameString -------------------------------------------------------{{{2
class GDTripNameString(Cfh.String):
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent

# GDTripNameStringReadOnly -----------------------------------------------{{{2
class GDTripNameStringReadOnly(Cfh.String):
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent
        self.setEditable(False)
        self.setStyle(Cfh.CfhSLabelNormal)
        
# GDStationString --------------------------------------------------------{{{2
class GDStationString(Cfh.String):
    """Let user select from standard home bases. Other bases are also OK if
    they exist in 'airport'."""
    stations = ('ARN', 'CPH', 'OSL')
    def __init__(self, *a, **k):
        self.all_stations = [x.id for x in TM.airport] 
        Cfh.String.__init__(self, *a, **k)
        self.setMenuOnly(False)
        self.setMenuString("Stn;" + ';'.join(self.stations))
        self.setTranslation(Cfh.CfhEntry.ToUpper)

    def check(self, value):
        """Return None if valid else error message."""
        if not value in self.all_stations:
            return "Unknown station (%s)." % value

# GDBriefDefaultToggle ------------------------------------------------------{{{2
class GDBriefDefaultToggle(Cfh.Toggle):
    """Option to set briefing defaults."""

    def __init__(self, parent, *a, **k):
        Cfh.Toggle.__init__(self, parent, *a, **k)
        self.parent = parent

    def check(self, value):
        """If true, override briefing field."""
        r = Cfh.Toggle.check(self, value)
        if value == "False":
            self.parent.brief_time_entry.setEditable(0)
            self.parent.brief_time_entry.assign(self.parent.brief_default)
            self.parent.brief_time_over.assign('default')
        else:
            self.parent.brief_time_entry.setEditable(1)
            self.parent.brief_time_entry.assign(self.parent.brief_override)
            self.parent.brief_time_over.assign('override')
            
# GDDebriefDefaultToggle ------------------------------------------------------{{{2
class GDDebriefDefaultToggle(Cfh.Toggle):
    """Option to set debriefing defaults."""

    def __init__(self, parent, *a, **k):
        Cfh.Toggle.__init__(self, parent, *a, **k)
        self.parent = parent

    def check(self, value):
        """If true, disable override debriefing field."""
        r = Cfh.Toggle.check(self, value)
        if value == "False":
            self.parent.debrief_time_entry.setEditable(0)
            self.parent.debrief_time_entry.assign(self.parent.debrief_default)
            self.parent.debrief_time_over.assign('default')
        else:
            self.parent.debrief_time_entry.setEditable(1)
            self.parent.debrief_time_entry.assign(self.parent.debrief_override)
            self.parent.debrief_time_over.assign('override')
            
# Message ---------------------------------------------------------------{{{2
class Message(Cfh.String):
    """Box with outpu."""
    def __init__(self, parent, name, area):
        Cfh.String.__init__(self, parent, name, area, 8, '')
        self.parent = weakref.ref(parent)
        self.setEditable(False)
        self.setStyle(Cfh.CfhSLabelNormal)

                        
# GDCancelledToggle ------------------------------------------------------{{{2
class GDCancelledToggle(Cfh.Toggle):
    """Let user cancel activity."""

    def __init__(self, parent, *a, **k):
        Cfh.Toggle.__init__(self, parent, *a, **k)
        self.parent = parent


# ComplementList ---------------------------------------------------------{{{2
class ComplementList(list):
    """Keep track of crew complement. There will be one entry per crew
    position the entry is of type 'Cfh.CfhNumber'.  The information labels
    are also kept in internal list to prevent garbage collection.
    Attribute access is extended, e.g. attribute 'FC' will return number in
    'FC' position."""

    f_pos = ['FC', 'FP', 'FR','FU'] 
    c_pos = ['AP', 'AS', 'AH','AU']
    #t_pos = ['TL', 'TR']
    t_pos = ['TL','TR']                    # BZ 31706, TR is inst on simulator
    pos = f_pos + c_pos + t_pos
    # Offset from left to the first position in each group
    offset = 10

    def __init__(self, box, start_row=0):
        list.__init__(self)
        self.box = box
        # Keep labels in list to prevent garbage collection!
        self.labels = []
        self.labels.append(Cfh.Label(self.box, "FD_LABEL",
                Cfh.Area(Cfh.Loc(start_row + 1, 0)), "Flight Deck"))
        self.labels.append(Cfh.Label(self.box, "CC_LABEL",
                Cfh.Area(Cfh.Loc(start_row + 3, 0)), "Cabin Crew"))
        self.labels.append(Cfh.Label(self.box, "TRAINING_LABEL",
                Cfh.Area(Cfh.Loc(start_row + 5, 0)), "Training"))
        for i in xrange(len(self.pos)):
            pos = self.pos[i]
            if pos in self.f_pos:
                x = self.f_pos.index(pos)
                row = start_row
            elif pos in self.c_pos:
                x = self.c_pos.index(pos)
                row = start_row + 2
            elif pos in self.t_pos:
                x = self.t_pos.index(pos)
                row = start_row + 4
            else:
                raise Exception("internal error")
            if pos not in ('FU','AU'): # Not needed by form, since they are free
                self.add_fields(x, pos, row)
            else:
                self.append(GDCrewNumMock(0)) # Just store value in non-graphic component
    def assign(self, values):
        """Assign values from the crew vector in the iterable 'values'."""
        for ix, value in enumerate(values):
            try:
                self[ix].assign(value)
            except:
                Errlog.log("ground_duty_handler:"
                    "Could not assign value '%s' in position '%d'." % (value, ix))

    def add_fields(self, ix, crew_pos, row):
        """Add one label and one input field to the parent form."""
        self.labels.append(Cfh.Label(self.box, "%s_LABEL" % crew_pos,
            Cfh.Area(Cfh.Dim(4, 1), Cfh.Loc(row, self.offset + (ix * 6))),
            crew_pos))
        self.append(GDCrewNum(self.box, crew_pos, 
            Cfh.Area(Cfh.Dim(4, 1), Cfh.Loc(row + 1, self.offset + (ix * 6))),
            0, False))

    def __getattr__(self, position):
        """Return value of 'Number' object for 'position'."""
        if not position in self.pos:
            raise AttributeError("No such position '%s'." % position)
        try:
            return self[self.pos.index(position)].valof()
        except:
            return 0

    def __int__(self):
        """Return sum of crew complement for all positions."""
        return sum([int(x.getValue()) for x in self])

    def __str__(self):
        """Return crew complement vector."""
        f = '/'.join([str(getattr(self, x)) for x in self.f_pos])
        c = '/'.join([str(getattr(self, x)) for x in self.c_pos])
        t = '/'.join([str(getattr(self, x)) for x in self.t_pos])
        return '//'.join((f, c, t))


# GDKeepValuesToggle -----------------------------------------------------{{{2
class GDKeepValuesToggle(Cfh.Toggle):
    """Let user keep previously entered values."""

    def __init__(self, parent, *a, **k):
        Cfh.Toggle.__init__(self, parent, *a, **k)
        self.parent = parent


# ValidateDone -----------------------------------------------------------{{{2
class ValidateDone(Cfh.Done):
    """The OK button. Perform a number of checks before submitting."""
    def __init__(self, parent, *args):
        Cfh.Done.__init__(self, parent, *args)
        self.parent = parent

    def action(self):
        def check_sanity():
            if not self.parent.taskcode_entry.getValue():
                return "Task code must not be empty."
            if not self.parent.station_entry.getValue():
                return "Station must not be empty."
            if not self.parent.cancelled_entry.getValue():
                return "Status must not be empty."
            try:
                sd = AbsTime(self.parent.start_date_entry.getValue())
            except:
                return "Start date has wrong format (10:00)."
            try:
                st = RelTime(self.parent.start_time_entry.getValue())
            except:
                return "Start time has wrong format (10:00)."
            try:
                ed = AbsTime(self.parent.end_date_entry.getValue())
            except:
                return "End date has wrong format (23Aug2008)."
            try:
                et = RelTime(self.parent.end_time_entry.getValue())
            except:
                return "End time has wrong format (23Aug2008)."
            
            # If updating start date for existing ground duty only
            # allow a change of date within the month given by old_st=trip_udor
            old_st=None
            try:
                old_st = self.parent.old_st
            except:
                pass
            if old_st and sd != old_st.day_floor():
                return "Start date must not be modified."
            
            if sd + st >= ed + et:
                self.parent.end_date_entry.setValue(str(ed + RelTime('24:00')))
            if hasattr(self.parent, 'complement') and int(self.parent.complement) <= 0:
                return "Total crew complement is zero."

            # Brief/debrief override times control for simulators in tracking..
            if self.parent.sim_track and self.parent.assigned:
                dbt = self.parent.brief_default_entry.getValue()
                ddt = self.parent.debrief_default_entry.getValue()
                self.parent.briefDebriefDictInfo['BRIEF'][2] = not dbt == 'True'
                self.parent.briefDebriefDictInfo['DEBRIEF'][2] = not ddt == 'True'

                br1 = RelTime(self.parent.brief_time_entry.getValue())
                br2 = RelTime(self.parent.brief_time_entry.valof())
                dbr1 = RelTime(self.parent.debrief_time_entry.getValue())
                dbr2 = RelTime(self.parent.debrief_time_entry.valof())
                self.parent.briefDebriefDictInfo['BRIEF'][0] = dbt == 'True'
                self.parent.briefDebriefDictInfo['DEBRIEF'][0] = ddt == 'True'
                    
                self.parent.briefDebriefDictInfo['BRIEF'][1] = br1
                if br1 > RelTime(8, 0):
                    self.parent.briefDebriefDictInfo['BRIEF'][0] = False
                    self.parent.briefDebriefDictInfo['BRIEF'][1] = self.parent.brief_default
                self.parent.briefDebriefDictInfo['DEBRIEF'][1] = RelTime(self.parent.debrief_time_entry.getValue())
                        
        m = check_sanity()
        if m is not None:
            self.parent.message(m, True)
        else:
            Cfh.Done.action(self)


# GroundDutyPropertiesForm -----------------------------------------------{{{2
class GroundDutyPropertiesForm(Cfh.Box):
    """CFH form for creating or updating ground duty (ground task)
    properties."""

    def __init__(self, title="Ground Duty Properties", assigned=False, sim_track=False, old_st=None):
        """Don't show crew complement if 'assigned' is True."""
        # Main box for Form
        Cfh.Box.__init__(self, "GROUND_DUTY")

        self.assigned = assigned
        self.setText(title)
        self.sim_track = sim_track  # Indicates 'simulator' activity and 'tracking' application.
        self.old_st = old_st        # None or trip_udor for ground duty to be updated
        
        # Let start and end be based on 'now'.
        self.now = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, "None",
                "fundamental.%now%")

        self.timebase_label = Cfh.Label(self, "TIMEBASE_LABEL", 
                Cfh.Area(Cfh.Loc(0, 0)), "Time base:")
        self.timebase_entry = GDTimeBaseString(self, "TIMEBASE_VALUE",
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(0, 10)), 4, "LDOP")

        self.taskcode_label = Cfh.Label(self, "TASKCODE_LABEL",
                Cfh.Area(Cfh.Loc(1, 0)), "Task code:")
        self.taskcode_entry = GDTaskCodeString(self, "TASKCODE_VALUE",
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(1, 10)), 6, "")

        self.tripname_label = Cfh.Label(self, "NAME_LABEL",
                Cfh.Area(Cfh.Loc(2, 0)), "Name:")

        if not assigned:
            self.tripname_entry = GDTripNameString(self, "NAME_VALUE",
                    Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(2, 10)), 16, "")
        else:
            self.tripname_entry = GDTripNameStringReadOnly(self, "NAME_VALUE",
                    Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(2, 10)), 16, "")

        self.station_label = Cfh.Label(self, "STATION_LABEL",
                Cfh.Area(Cfh.Loc(3, 0)), "Station:")
        self.station_entry = GDStationString(self, "STATION_VALUE",
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(3, 10)), 4, "")

        self.cancelled_label = Cfh.Label(self, "CANCELLED_LABEL",
                Cfh.Area(Cfh.Loc(3, 22)), "Cancelled:")
        self.cancelled_entry = GDCancelledToggle(self, "CANCELLED_VALUE",
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(3, 30)), False)

        if not assigned:
            self.keep_values_label = Cfh.Label(self, "KEEP_VALUES_LABEL",
                Cfh.Area(Cfh.Loc(4, 22)), "Keep Values:")
            self.keep_values_entry = GDKeepValuesToggle(self, "KEEP_VALUES_VALUE",
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(4, 30)), False)
        

        self.start_label = Cfh.Label(self, "START_LABEL",
                Cfh.Area(Cfh.Loc(6, 0)), "Start")
        self.start_label.setStyle(Cfh.CfhSLabelHeader)
        self.start_date_label = Cfh.Label(self, "START_DATE_LABEL",
                Cfh.Area(Cfh.Loc(6, 5)), "Date:")
        self.start_date_entry = Cfh.Date(self, "START_DATE", 
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(6, 10)), self.now)
        self.start_date_entry.setMandatory(True)
        if old_st:
            self.start_date_entry.setEditable(False)
        last_line = 7
        self.start_time_label = Cfh.Label(self, "START_TIME_LABEL",
                Cfh.Area(Cfh.Loc(last_line, 5)), "Time:")
        self.start_time_entry = Cfh.Clock(self, "START_TIME",
                Cfh.Area(Cfh.Dim(5, 1), Cfh.Loc(last_line, 10)), RelTime(8, 0))

        self.end_label = Cfh.Label(self, "END_LABEL",
                Cfh.Area(Cfh.Loc(6, 22)), "End")
        self.end_label.setStyle(Cfh.CfhSLabelHeader)
        self.end_date_label = Cfh.Label(self, "END_DATE_LABEL",
                Cfh.Area(Cfh.Loc(6, 27)), "Date:")
        self.end_date_entry = Cfh.Date(self, "END_DATE", 
                Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(6, 32)), self.now)
        self.end_date_entry.setMandatory(True)
        self.end_time_label = Cfh.Label(self, "END_TIME_LABEL",
                Cfh.Area(Cfh.Loc(last_line, 27)), "Time:")
        self.end_time_entry = Cfh.Clock(self, "END_TIME", 
                Cfh.Area(Cfh.Dim(5, 1), Cfh.Loc(last_line, 32)), RelTime(16, 0))
        next_line = last_line + 2
            
        # Show default briefing/debreafing times for simulators in tracking.
        if self.sim_track and self.assigned:
            self.brief_default_label = Cfh.Label(self, "BRIEF_DEFAULT_LABEL",
                    Cfh.Area(Cfh.Loc(8, 0)), "Use brief override")
            self.brief_default_entry = GDBriefDefaultToggle(self, "BRIEF_DEFAULT_VALUE",
                    Cfh.Area(Cfh.Dim(0, 1), Cfh.Loc(8, 10)), False)
            self.debrief_default_label = Cfh.Label(self, "DEBRIEF_DEFAULT_LABEL",
                    Cfh.Area(Cfh.Loc(8, 22)), "Use debrief override")
            self.debrief_default_entry = GDDebriefDefaultToggle(self, "DEBRIEF_DEFAULT_VALUE",
                    Cfh.Area(Cfh.Dim(0, 1), Cfh.Loc(8, 33)), False)
            
            last_line = 9
            self.brief_time_label = Cfh.Label(self, "BRIEF_TIME_LABEL",
                    Cfh.Area(Cfh.Loc(last_line, 0)), "Briefing")
            self.brief_time_over = Message(self, "BRIEF_OVER",
                    Cfh.Area(Cfh.Loc(last_line, 5)))
            self.brief_time_entry = Cfh.Clock(self, "BRIEF_TIME",
                    Cfh.Area(Cfh.Dim(5, 1), Cfh.Loc(last_line, 10)))
            self.debrief_time_label = Cfh.Label(self, "DEBRIEF_TIME_LABEL",
                    Cfh.Area(Cfh.Loc(last_line, 22)), "Debriefing")
            self.debrief_time_over = Message(self, "DEBRIEF_OVER",
                    Cfh.Area(Cfh.Loc(last_line, 28)))
            self.debrief_time_entry = Cfh.Clock(self, "DEBRIEF_TIME",
                    Cfh.Area(Cfh.Dim(5, 1), Cfh.Loc(last_line, 33)), RelTime(2, 0))
            next_line = last_line + 2
                    
            self.briefDebriefDictInfo = {}
            self.briefDebriefDictInfo['BRIEF'] = [False, RelTime(0, 0), False]
            self.briefDebriefDictInfo['DEBRIEF'] = [False, RelTime(0, 0), False]
            
            self.brief_current = RelTime(0, 0)
            self.debrief_current = RelTime(0, 0)
            self.brief_override = RelTime(0, 0)
            self.debrief_override = RelTime(0, 0)
            self.brief_default = RelTime(0, 0)
            self.debrief_default = RelTime(0, 0)

        # Don't show complement or "keep values" toggle on assigned duties.
        if not self.assigned:
            self.complement = ComplementList(self, start_row=next_line)
            
        self.save_date = AbsTime(0)

        self.button_area = Cfh.Area(Cfh.Loc(-1,-1))
        self.done = ValidateDone(self, "OK", self.button_area, "Ok", "_Ok")
        self.cancel = Cfh.Cancel(self, "CANCEL", self.button_area, "Cancel", "_Cancel")
 
        # The normal Reset button doesn't seem to work properly with stored values
        # from a previous form.  A new class, DefaultButton is used when creating a
        # new ground duty
        if not assigned:
            self.reset = DefaultButton(self, "RESET", "Reset", "_Reset")
        else:
            self.reset = Cfh.Reset(self, "RESET", self.button_area, "Reset", "_Reset")


    def __call__(self):
        """Main entry point."""
        self.build()
        self.show(1)
        if self.loop():
            raise CancelledFormError()
        return 0

    def get_gnd_task_props(self):
        """Return properties about ground task"""
        return {'taskcode': self.taskcode,
                'tripname': self.tripname,
                'airport': self.station,
                'st': self.start_datetime_utc,
                'et': self.end_datetime_utc,
                'statcode': self.cancelled,
                'keep_values': self.keep_values,
                'start_date': self.start_date_s,
                'end_date': self.end_date_s,
                'start_time': self.start_time_s,
                'end_time': self.end_time_s
                }

    def set_form_fields(self, chain_object):
        """Update the entry fields with values from 'chain_object'."""
        leg = MiniEval({
            'task_uuid': 'ground_uuid',
            'task_udor': 'gdor',
            'start_lt': 'leg.%start_lt%',
            'end_lt': 'leg.%end_lt%',
            'station': 'leg.%start_station%',
            'code': 'task.%code%',
            'tripname': 'crr_name',
            'npos1': 'crew_pos.%leg_assigned_pos%(1)',
            'npos2': 'crew_pos.%leg_assigned_pos%(2)',
            'npos3': 'crew_pos.%leg_assigned_pos%(3)',
            'npos4': 'crew_pos.%leg_assigned_pos%(4)',
            'npos5': 'crew_pos.%leg_assigned_pos%(5)',
            'npos6': 'crew_pos.%leg_assigned_pos%(6)',
            'npos7': 'crew_pos.%leg_assigned_pos%(7)',
            'npos8': 'crew_pos.%leg_assigned_pos%(8)',
            'npos9': 'crew_pos.%leg_assigned_pos%(9)',
            'npos10': 'crew_pos.%leg_assigned_pos%(10)',
        }).eval(chain_object)

        # self.timebase_entry.assign("UDOP")
        self.timebase_entry.assign("LDOP")
        self.station_entry.assign(leg.station)
        self.taskcode_entry.assign(leg.code)
        self.tripname_entry.assign(leg.tripname)

        # Check if ground task has a valid statcode.
        # If not set it to active...
        ground_task = TM.ground_task[(leg.task_udor, leg.task_uuid)]
        try:
            statcode = ground_task.statcode.id
        except:
            ground_task.statcode = TM.activity_status_set["A"]
            statcode = "A"
            
        self.cancelled_entry.assign(statcode == "C")

        y, m, d, H, M = leg.start_lt.split()[:5]
        self.start_date_entry.assign(AbsTime(y, m, d, 0, 0))
        self.save_date = AbsTime(y, m, d, H, M)
        self.start_time_entry.assign(RelTime(H, M))

        y, m, d, H, M = leg.end_lt.split()[:5]
        self.end_date_entry.assign(AbsTime(y, m, d, 0, 0))
        self.end_time_entry.assign(RelTime(H, M))

        if not self.assigned:
            self.complement.assign((
                leg.npos1, leg.npos2, leg.npos3,leg.npos4,
                leg.npos5, leg.npos6, leg.npos7,leg.npos8,
                leg.npos9, leg.npos10))                 # BZ 31706,
                                                        # Pergr 31Oct2008. TR used as sim instr
                # npos4 and npos8 is FU and AU and they are free positions

                
        # Get simulator brief/debrief current, default and override times for tracking.
        if self.sim_track and self.assigned:
            self.getBriefDebriefInfo(chain_object)

    def getBriefDebriefInfo(self, chain_object):
        
        leg_brief = MiniEval({
            'brief': 'leg.%leg_sim_briefing_time_length%',
            'debrief': 'leg.%leg_sim_debriefing_time_length%',
            'brief_override': 'leg.%brief_assignment_override%',
            'debrief_override': 'leg.%debrief_assignment_override%',
            'brief_default': 'leg.%default_leg_sim_briefing_time_length%',
            'debrief_default': 'leg.%default_leg_sim_debriefing_time_length%',
        }).eval(chain_object)
        
        self.brief_time_over.assign('default')
        self.brief_time_entry.assign(leg_brief.brief)
        self.brief_override = leg_brief.brief_override
        self.brief_default_entry.assign(True)
        if leg_brief.brief_override is None:
            self.brief_override = RelTime(0, 0)
            self.brief_default_entry.assign(False)
        self.brief_current = leg_brief.brief
        self.brief_default = leg_brief.brief_default
        
        self.debrief_time_over.assign('default')
        self.debrief_time_entry.assign(leg_brief.debrief)
        self.debrief_override = leg_brief.debrief_override
        self.debrief_default_entry.assign(True)
        if leg_brief.debrief_override is None:
            self.debrief_override = RelTime(0, 0)
            self.debrief_default_entry.assign(False)
        self.debrief_current = leg_brief.debrief
        self.debrief_default = leg_brief.debrief_default

    def to_utc(self, time):
        """Return UTC time (if time is LDOP)."""
        if self.timebase == 'LDOP':
            return R.eval('station_utctime("%s", %s)' % (self.station, time))[0]
        return time

    # attribute access ---------------------------------------------------{{{3
    @property
    def timebase(self):
        return self.timebase_entry.valof()

    @property
    def taskcode(self):
        return self.taskcode_entry.valof()

    @property
    def tripname(self):
        return self.tripname_entry.valof()

    @property
    def station(self):
        return self.station_entry.valof()

    @property
    def cancelled(self):
        return self.cancelled_entry.valof()

    @property
    def keep_values(self):
        kval = None
        try:
            kval = self.keep_values_entry.valof()
        except:
            kval = False
        return kval

    @property
    def end_date_s(self):
        return str(AbsTime(self.end_date_entry.valof())).split()[0]

    @property
    def end_time_s(self):
        return "%02d%02d" % RelTime(self.end_time_entry.valof()).split()[:2]

    @property
    def start_date_s(self):
        return str(AbsTime(self.start_date_entry.valof())).split()[0]

    @property
    def start_time_s(self):
        return "%02d%02d" % RelTime(self.start_time_entry.valof()).split()[:2]

    @property
    def end_datetime(self):
        return AbsTime(self.end_date_entry.valof()) + RelTime(self.end_time_entry.valof())

    @property
    def start_datetime(self):
        return AbsTime(self.start_date_entry.valof()) + RelTime(self.start_time_entry.valof())

    @property
    def start_datetime_utc(self):
        return self.to_utc(self.start_datetime)

    @property
    def end_datetime_utc(self):
        return self.to_utc(self.end_datetime)

    @property
    def arrival_offset_days(self):
        timediff = int(self.end_datetime_utc - self.start_datetime_utc)
        if timediff >= 1440:
            return timediff / 1440
        return 0

    def defaultValues(self):
        self.taskcode_entry.assign('')
        self.tripname_entry.assign('')
        self.station_entry.assign('')
        self.start_date_entry.assign(self.now)
        self.end_date_entry.assign(self.now)
        self.start_time_entry.assign(RelTime(8, 0))
        self.end_time_entry.assign(RelTime(16, 0))
        self.keep_values_entry.assign('False')
        self.cancelled_entry.assign('False')

class DefaultButton(Cfh.Function):
    """
        Defines a reset button, resetting all values to the default ones.
    """

    def __init__(self, miniSelectObj, name, text, mnemonic):
        Cfh.Function.__init__(self, miniSelectObj, name, text, mnemonic)
        self.miniSelectObject = miniSelectObj
    def action(self):
        self.miniSelectObject.defaultValues()       

# functions =============================================================={{{1

# manage_ground_duty -----------------------------------------------------{{{2
def manage_ground_duty(mode=""):
    """Create ground duty. Called from object menues in Studio."""
    if mode.upper() == 'CREATE':
        create_ground_duty()
    elif mode.upper() == 'PROPERTIES_GND':
        update_ground_duty()
    else:
        Errlog.log("ground_duty_handler: manage_ground_duty::"
                "mode '%s' is not implemented" % mode)
        return 1
    return 0

# check_setattr ----------------------------------------------------------{{{2
def check_setattr(obj, name, value, colname=None):
    """
    If different from current value, set attribute 'name' to 'value' in 'obj'.
    Returns True if the attribute was updated.
    
    'colname': If 'name' is of a type where object comparison isn't
      properly implemented, 'colname' identifies a sub-item in the 'name'
      object that will be compared instead. For example:
          Airport("OSL") == Airport("OSL") returns False!
      However, the 'id' of an Airport object is a comparable string object,
      so specifying "id" as colname for an Airport comparison will work.
      For example:
          chg = check_setattr(task, "adep", airport, "id")
    """
    new_value = value
    old_value = getattr(obj, name, None)
    if colname:
        if new_value: new_value = getattr(new_value, colname)
        if old_value: old_value = getattr(old_value, colname)
    if new_value != old_value:
        setattr(obj, name, value)
        return True
    return False
    

# update_ground_duty -----------------------------------------------------{{{2
def update_ground_duty():
    """Update ground duty based on values of the currently selected object.
    A form with current values is launched and the values are changed using
    Cui functions."""

    # Old comment: What happens when crew run properties on a trip is that they
    # get properties for one leg and then crew complement for the trip.
    # Also changing start date needs to recreate the leg and change udor.
    # Requires re-linking of trip_ground_duty and crew_ground_duty...
    #
    # JIRA SASCMS-4232: Pass on trip_udor for the ground duty to the
    # Ground duty properties form and only allow start date to be changed
    # to a date within the same month as trip_udor.

    # Synchronize the generic and classic models to make sure
    # that we work on the latest data.
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    leg_obj = HF.LegObject()

    # Get keyword information to find database records.
    # Get a list of all assigned crew, so we can set them to "locally modified".
    assigned, task_uuid, task_udor, user_id, is_simulator, equal_legs = \
        leg_obj.eval('not void(crr_crew_id)', 'ground_uuid', 'gdor',
                     'crr_crew_id', 'leg.%is_simulator%',
                     R.foreach('equal_legs',
                       R.foreach(R.iter('iterators.leg_set'), 'crew.%id%')))
    all_assigned_crew = [eql[1] for eql in equal_legs[0][1] if eql[1]]

    # Simulator brief/debrief override only for tracking.
    tracking_sim = is_simulator and (application.isTracking or application.isDayOfOps)

    trip_uuid, trip_udor = leg_obj.eval('trip_uuid', 'trip_udor')

    has_sim_exception, = leg_obj.eval('leg.%has_sim_exception%')
    
    # Don't let user change crew complement for assigned duties.
    if assigned:
        if trip_udor is None:
            trip_udor = task_udor
            old_st = trip_udor
        else:
            old_st = AbsTime(trip_udor*1440)
        
        form = GroundDutyPropertiesForm(assigned=True, sim_track=tracking_sim, old_st=old_st)
    else:
        # Test if trip is persistent or dynamically created.
        # If dynamic let's create it.
        trip = None
        if trip_udor is None:
            trip_udor = task_udor
        else:
            trip_udor = AbsTime(trip_udor*1440)
            try:
                trip = TM.trip[(trip_udor, trip_uuid)]
            except:
                pass

        if trip is None:
            # Create a new trip... (i.e. copy the trip)
            trip_uuid = TM.createUUID()
            trip = TM.trip.create((trip_udor, trip_uuid))

            # The trip_ground_duty record requires base as part of the key.
            # - is used as "no base".
            fake_base = TM.crew_base_set.getOrCreateRef('-')

            # Get a handle to the one and only ground task included in the
            # current dynamic trip.
            task = TM.ground_task[(task_udor,task_uuid)]

            # Connect the ground task to the trip.
            trip_ground_duty = TM.trip_ground_duty.create((trip,task,fake_base))
        
        form = GroundDutyPropertiesForm(sim_track=tracking_sim, old_st=trip_udor)
        
    # Get the current complement of the leg (before starting the form)
    lego = MiniEval({
            'npos1': 'crew_pos.%leg_assigned_pos%(1)',
            'npos2': 'crew_pos.%leg_assigned_pos%(2)',
            'npos3': 'crew_pos.%leg_assigned_pos%(3)',
            'npos4': 'crew_pos.%leg_assigned_pos%(4)',
            'npos5': 'crew_pos.%leg_assigned_pos%(5)',
            'npos6': 'crew_pos.%leg_assigned_pos%(6)',
            'npos7': 'crew_pos.%leg_assigned_pos%(7)',
            'npos8': 'crew_pos.%leg_assigned_pos%(8)',
            'npos9': 'crew_pos.%leg_assigned_pos%(9)',
            'npos10': 'crew_pos.%leg_assigned_pos%(10)',
        }).eval(HF.LegObject())
    current_comp = [lego.npos1, lego.npos2, lego.npos3, lego.npos4, lego.npos5, \
           lego.npos6, lego.npos7, lego.npos8, lego.npos9, lego.npos10]

    # Fill in the current values
    form.set_form_fields(HF.LegObject())

    try:
        form()
    except CancelledFormError:
        Errlog.log("ground_duty_handler:: user cancelled form")
        return 1
    except Exception:
        return -1

    # Get task properties from the form.
    ground_task_properties = form.get_gnd_task_props()
    st = ground_task_properties['st']
    et = ground_task_properties['et']
    tripname = ground_task_properties['tripname']

    # Perform type conversion.
    airport = TM.airport[ground_task_properties['airport']]
    activity = TM.activity_set[ground_task_properties['taskcode']]
    statcode = TM.activity_status_set[("A","C")[ground_task_properties['statcode']]]

    # Open and modify the ground_task activity.
    task = TM.ground_task[(task_udor, task_uuid)]
    task_is_modified = False
    task_is_modified |= check_setattr(task, 'st', st)
    task_is_modified |= check_setattr(task, 'et', et)
    task_is_modified |= check_setattr(task, 'adep', airport, "id")
    task_is_modified |= check_setattr(task, 'ades', airport, "id")
    task_is_modified |= check_setattr(task, 'activity', activity, "id")
    task_is_modified |= check_setattr(task, 'statcode', statcode, "id")

    # If opened from the trip view.
    # Update crew complement and base as well.
    # (Note: These "meta" attributes needn't be notified to crew.)
    if not assigned:

        # Read the complement from the form
        new_comp = []
        for value in form.complement:
            new_comp.append(int(value.valof()))

        # Try to set base according to chosen airport.
        # Default to CPH if non-base airport is chosen.
        if airport.id not in [base.airport.id for base in TM.crew_base_set]:
            trip_base = TM.crew_base_set['CPH']
        else:
            bases = TM.crew_base_set.search('(&(airport='+airport.id+'))')
            for base in bases:
                trip_base = base

        # Open and modify trip record.
        trip = TM.trip[(trip_udor, trip_uuid)]
        trip.base = trip_base
        trip.adhoc = tripname

        i = 0
        for value in form.complement:
            setattr(trip, "cc_"+str(i), int(value.valof()))
            i += 1

        while i < 12:
            setattr(trip, "cc_"+str(i), 0)
            i += 1

        # If the trip is a SIM and the booked value is other than need value,
        # update the need value in the ground_duty_attr table.  Only set the
        # SIM as an exception if the complement has been changed on the form
        task_codes = {}
        for x in TM.activity_set:
            task_codes[x.id] = x.grp.id
            
        taskname = ground_task_properties['taskcode']
        comp_changed = new_comp != current_comp

        if task_codes[taskname] in ['OPC','AST','ASF','FFS','SIM']:
            if has_sim_exception:
                set_sim_need(taskname, form.complement, task_udor, task.id)    
            if comp_changed:
                need_list = []
                for i in range(1,11):
                    try:
                        special, = R.eval('crew_pos.%%sim_has_external_instructor%%("%s")' % taskname)
                        need, = R.eval('crew_pos.%%_sim_need_pos%s%%("%s", %s, %s)' % (i,task_codes[taskname], special, task_udor))
                        need_list.append(need)
                    except:
                        need_list.append(0)
                form_list = []
                for value in form.complement:
                    form_list.append(int(value.valof()))
                if form_list != need_list:
                    set_sim_need(taskname, form.complement, task_udor, task.id)


    # Get override brief/debrief times for simulator in tracking for rosters.
    if tracking_sim and assigned:
        briefing_debriefing_handling(task, user_id, form.briefDebriefDictInfo, et)
        
    # Synchronize the generic and classic models.
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    
    # If any attribute was changed that might need to be notified to crew,
    # mark the crew as "locally modified" so notifications are updated at save.
    # Note: This only has effect in tracking, but since there is no noticable
    # performance impact, there is no distinction between different modes here.
    if task_is_modified:
        for crewid in all_assigned_crew:
            modcrew.add(crewid)

            
# Update crew_ground_duty_attr briefing values ---------------------------{{{2
def briefing_debriefing_handling(task, user_id, briefDebriefDictInfo, *args):
    """Update crew_ground_duty_attr briefing values."""

    # Dictionary with briefing/debriefing handling options
    # briefDebriefDictInfo = {}
    # briefDebriefDictInfo['BRIEF'] = [override ?, overrideValue, default ?]
    # briefDebriefDictInfo['DEBRIEF'] = [override ?, overrideValue, default ?]

    # Modify the crew_ground_duty_attr.
    for attrType in briefDebriefDictInfo.keys():
        (keyBrief, attr) = crew_ground_duty_attr_key(task, user_id, attrType)
        if briefDebriefDictInfo[attrType][0]:
            # Override briefing/debriefing times, create attributes record.
            try:
                taskAttrPntr = TM.crew_ground_duty_attr[(keyBrief, attr)]
            except:
                # Create a new simulator duty brief/debrief time override attribute record.
                taskAttrPntr = TM.crew_ground_duty_attr.create((keyBrief, attr))
            if attrType == "BRIEF":
                taskAttrPntr.value_rel = briefDebriefDictInfo[attrType][1]
            else:
                taskAttrPntr.value_abs = args[0] + briefDebriefDictInfo[attrType][1]
            taskAttrPntr.si = "Added by: ground_duty_handler::user: " + os.environ.get('USER')
            Errlog.log("ground_duty_handler::%s attributes ADDED."%attrType)
        elif briefDebriefDictInfo[attrType][2]:
            # Delete the attribute record for brief/debrief time override.
            try:
                taskAttrPntr = TM.crew_ground_duty_attr[(keyBrief, attr)]
                taskAttrPntr.remove()
                Errlog.log("ground_duty_handler::%s attributes REMOVED."%attrType)
            except modelserver.EntityNotFoundError:
                Errlog.log("ground_duty_handler::%s NO attributes found."%attrType)
                pass

    # Reload modified tables.    
    Cui.CuiReloadTable("crew_ground_duty_attr",Cui.CUI_RELOAD_TABLE_SILENT)
    modcrew.add(str(user_id))
        
    HF.redrawAllAreas(Cui.CrewMode)
    
# Get crew_ground_duty_attr key ------------------------------------------{{{2
def crew_ground_duty_attr_key(task, crew, attr):
    """Get crew_ground_duty_attr key."""
    t_assig_attr = TM.table("assignment_attr_set")
    k_attr = t_assig_attr.getOrCreateRef((attr,))
    t_crew = TM.table("crew")
    crew = t_crew.getOrCreateRef((crew,))
    return (TM.crew_ground_duty[(task, crew)], k_attr)

# Get ground_task_attr key -----------------------------------------------{{{2
def ground_task_attr_key(attr):
    """Get ground_task_attr key."""
    t_assig_attr = TM.table("leg_attr_set")
    k_attr = t_assig_attr.getOrCreateRef((attr,))
    return  k_attr

# create_ground_duty -----------------------------------------------------{{{2
def create_ground_duty():
    """Create a ground duty."""
    form = GroundDutyPropertiesForm(title="Create Ground Duty")

    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # If the toggle, "Keep values" is checked, use the previous form's values
    if FORM_KEEP_VALUES:
        form.taskcode_entry.assign(GROUND_FORM_PROPERTIES['taskcode'])
        form.tripname_entry.assign(GROUND_FORM_PROPERTIES['tripname'])
        form.station_entry.assign(GROUND_FORM_PROPERTIES['airport'])
        form.start_date_entry.assign(GROUND_FORM_PROPERTIES['start_date'])
        form.end_date_entry.assign(GROUND_FORM_PROPERTIES['end_date'])
        form.start_time_entry.assign(GROUND_FORM_PROPERTIES['start_time'])
        form.end_time_entry.assign(GROUND_FORM_PROPERTIES['end_time'])
        form.keep_values_entry.assign(GROUND_FORM_PROPERTIES['keep_values'])
        form.cancelled_entry.assign(GROUND_FORM_PROPERTIES['statcode'])
        form.complement.assign(GROUND_FORM_PROPERTIES['complement'])
    try:
        form()
    except CancelledFormError:
        Errlog.log("ground_duty_handler:: user cancelled form")
        return 1
    except Exception:
        return -1

    global FORM_KEEP_VALUES
    global GROUND_FORM_PROPERTIES

    try:
        FORM_KEEP_VALUES = form.keep_values
        GROUND_FORM_PROPERTIES = form.get_gnd_task_props()
        clist = []
        for value in form.complement:
            clist.append(int(value.valof()))
        GROUND_FORM_PROPERTIES['complement'] = clist
    except:
        FORM_KEEP_VALUES = False
        GROUND_FORM_PROPERTIES = None

    # Get task properties from the form.
    ground_task_properties = form.get_gnd_task_props()

    st = ground_task_properties['st']
    et = ground_task_properties['et']
    tripname = ground_task_properties['tripname']

    # Decide how many objects to create.
    a_day = RelTime('24:00')
    start_date = st.day_floor()
    start_time = st.time_of_day()
    length = et - st
    # Whole day actvity check
    if int(length) % int(a_day) == 0:
        no_days = int((length)/a_day)
    else:
        no_days = int((length)/a_day + 1)
    time = length - a_day * (no_days - 1)

    # Perform type conversion.
    airport = TM.airport[ground_task_properties['airport']]
    activity = TM.activity_set[ground_task_properties['taskcode']]
    statcode = TM.activity_status_set[["A","C"][ground_task_properties['statcode']]]

    # Try to set base according to chosen airport.
    # Default to CPH if non-base airport is chosen.
    if airport.id not in [base.airport.id for base in TM.crew_base_set]:
        trip_base = TM.crew_base_set['CPH']
    else:
        bases = TM.crew_base_set.search('(&(airport='+airport.id+'))')
        for base in bases:
            trip_base = base

    # Remember created trips for selection at end.
    trip_list = []

    created_tasks = 0
    reused_tasks = 0
    for day_no in range(0,no_days):
        task_udor = start_date + a_day * day_no
        task_st = task_udor + start_time
        task_et = task_st + time
        task_adep = airport
        task_ades = airport
        task_activity = activity
        task_statcode = statcode

        try:
            task_key = (str(task_udor), str(task_st), str(task_et), str(task_adep.id), str(task_activity.id))
        except:
            # Invalid input
            Gui.GuiWarning("Invalid input")
            return

        # Try and find existing task, matching udor, st, et, adep, and activity
        for task in TM.ground_task.search("(&(udor=%s)(st=%s)(et=%s)(adep=%s)(activity=%s))" %task_key):
            reused_tasks += 1
            task.statcode = task_statcode
            break
        else:
            created_tasks += 1
            # Create the ground task activity.
            task_uuid = TM.createUUID()
            task = TM.ground_task.create((task_udor, task_uuid))
            task.st = task_st
            task.et = task_et
            task.adep = task_adep
            task.ades = task_ades
            task.activity = task_activity
            task.statcode = task_statcode
        
        # Create the trip.
        i = 0
        fc = False
        cc = False
        tfc = False

        for value in form.complement:
            if i < 4:
                if int(value.valof()) > 0:
                    fc = True
            elif i < 8:
                if int(value.valof()) > 0:
                    cc = True
            elif i < 10:
                if int(value.valof()) > 0:
                    tfc = True
            i += 1

        #Create the rows in trip table
        trip_udor = task_udor
        if fc:
            trip_uuid_fc = TM.createUUID()
            trip_list.append(trip_uuid_fc)
            trip_fc = TM.trip.create((trip_udor, trip_uuid_fc))
            trip_fc.base = trip_base
            trip_fc.adhoc = tripname
        if cc:
            trip_uuid_cc = TM.createUUID()
            trip_list.append(trip_uuid_cc)
            trip_cc = TM.trip.create((trip_udor, trip_uuid_cc))
            trip_cc.base = trip_base
            trip_cc.adhoc = tripname
        if tfc:
            trip_uuid_tfc = TM.createUUID()
            trip_list.append(trip_uuid_tfc)
            trip_tfc = TM.trip.create((trip_udor, trip_uuid_tfc))
            trip_tfc.base = trip_base
            trip_tfc.adhoc = tripname

        # Attributes cc_0 - cc_11 on the trip contains the crew complement.
        i = 0
        for value in form.complement:
            if i < 4:
                if fc:
                    # Attributes cc_0 - cc_3 on the trip contains the crew complement.
                    setattr(trip_fc, "cc_"+str(i), int(value.valof()))
                if cc: #Alway zero for pos 0-3
                    setattr(trip_cc, "cc_"+str(i), 0)
                if tfc:
                    setattr(trip_tfc, "cc_"+str(i), 0)
            elif i < 8:
                # Attributes cc_4 - cc_7 on the trip contains the crew complement.
                if fc: #Alway zero for pos 0-3
                    setattr(trip_fc, "cc_"+str(i), 0)
                if cc:
                    setattr(trip_cc, "cc_"+str(i), int(value.valof()))
                if tfc: #Alway zero for pos 8-9
                    setattr(trip_tfc, "cc_"+str(i), 0)
            elif i < 10:
                if fc: #Alway zero for pos 0-3
                    setattr(trip_fc, "cc_"+str(i), 0)
                if cc: #Alway zero for pos 4-7
                    setattr(trip_cc, "cc_"+str(i), 0)
                if tfc:
                    # Attributes cc_8 - cc_9 on the trip contains the crew complement.
                    setattr(trip_tfc, "cc_"+str(i), int(value.valof()))
            i += 1
           
        while i < 12:
            if fc:
                setattr(trip_fc, "cc_"+str(i), 0)
            if cc:
                setattr(trip_cc, "cc_"+str(i), 0)
            if tfc:
                setattr(trip_tfc, "cc_"+str(i), 0)
            i += 1
       
        # The trip_ground_duty record requires base as part of the key.
        # - is used as "no base".
        fake_base = TM.crew_base_set.getOrCreateRef('-')

        # Connect the trip and the ground_task.
        if fc:
            #trip_ground_duty = 
            TM.trip_ground_duty.create((trip_fc, task, fake_base))
        if cc:
            #trip_ground_duty1 = 
            TM.trip_ground_duty.create((trip_cc, task, fake_base))
        if tfc:
            #trip_ground_duty2 = 
            TM.trip_ground_duty.create((trip_tfc, task, fake_base))


        # If the trip is a SIM and the booked value is other than need value,
        # update the need value in the ground_duty_attr table
        task_codes = {}
        for x in TM.activity_set:
            task_codes[x.id] = x.grp.id
            
        taskname = ground_task_properties['taskcode']

        if task_codes[taskname] in ['OPC','AST','ASF','FFS','SIM']:
            need_list = []
            for i in range(1,11):
                try:
                    special, = R.eval('crew_pos.%%sim_has_external_instructor%%("%s")' % taskname)
                    need, = R.eval('crew_pos.%%_sim_need_pos%s%%("%s", %s, %s)' % (i,task_codes[taskname], special, task_udor))
                    need_list.append(need)
                except:
                    need_list.append(0)
            form_list = []
            for value in form.complement:
                form_list.append(int(value.valof()))
            if form_list != need_list:
                act = TM.activity_group[(task_codes[taskname])]
                multisim = TM.simulator_set[(act, length)].multisim
                set_sim_need(taskname, form.complement, task_udor, task.id, multisim)

    # Synchronize the generic and classic models.
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    # Put newly created trip on top.
    # Select form needs all uppercase to work.
    # '/' character is a range function in the selectform.
    # Changing it to a '?' gives a slight risk of displaying the multiple trips.
  
    # Studio/Rave freaks out if to long list (> 1024 characters!!)
    tmp_list = []
    for trip_uuid in trip_list:
        if (len(tmp_list) + 1) * (24 +1) > 1024: # uuid is 24 chars + ','-char
            Select.select({'FILTER_METHOD': 'ADD',
                           'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                          area, Cui.CrrMode)
            tmp_list = []
        tmp_list.append(trip_uuid)
    if tmp_list:
        # finish of with the last ones!
        Select.select({'FILTER_METHOD': 'ADD',
                       'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                      area, Cui.CrrMode)
    Errlog.log("ground_duty_handler: Created %s new tasks, reused %s old tasks" %(created_tasks, reused_tasks))
    
def create_sb_ground_duty():
    print "start"
    ground_task_properties = {}
    ground_task_properties['st'] = AbsTime(2013, 3, 15, 4, 0)
    ground_task_properties['et'] = AbsTime(2013, 3, 15, 14, 0)
    ground_task_properties['tripname'] = ''
    ground_task_properties['airport'] = 'CPH'
    ground_task_properties['taskcode'] = "R"
    ground_task_properties['statcode'] = False
    ## complement = ComplementList(self)
##     complement.assign((
##                 1, 2, 3, 4,
##                 5, 6, 7, 8,
##                 9, 10))
##     print "test"
    ground_task_properties['complement'] = [ 1, 2, 3, 4,
                   5, 6, 7, 8,
                   9, 10]
    create_ground_duty_func(ground_task_properties)
#/*Added by Niklas Johansson for test purposes*/
def create_ground_duty_list_func(ground_task_properties_list):
    trip_list = []
    for gtp in ground_task_properties_list:
        trip_list.extend(create_ground_duty_func(gtp, False))
    try:
        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    except:
        print "Error"
    tmp_list = []
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    for trip_uuid in trip_list:
        if (len(tmp_list) + 1) * (24 +1) > 1024: # uuid is 24 chars + ','-char
            Select.select({'FILTER_METHOD': 'ADD',
                           'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                            area, Cui.CrrMode)
            tmp_list = []
        tmp_list.append(trip_uuid)
    if tmp_list:
        # finish of with the last ones!
        Select.select({'FILTER_METHOD': 'ADD',
                       'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                      area, Cui.CrrMode)
 
def create_ground_duty_func(ground_task_properties, select = True):
    """Create a SB ground duties."""
    #form = GroundDutyPropertiesForm(title="Create Ground Duty")
    complement = ground_task_properties['complement']

    # If the toggle, "Keep values" is checked, use the previous form's values
    ## if FORM_KEEP_VALUES:
##         form.taskcode_entry.assign(GROUND_FORM_PROPERTIES['taskcode'])
##         form.tripname_entry.assign(GROUND_FORM_PROPERTIES['tripname'])
##         form.station_entry.assign(GROUND_FORM_PROPERTIES['airport'])
##         form.start_date_entry.assign(GROUND_FORM_PROPERTIES['start_date'])
##         form.end_date_entry.assign(GROUND_FORM_PROPERTIES['end_date'])
##         form.start_time_entry.assign(GROUND_FORM_PROPERTIES['start_time'])
##         form.end_time_entry.assign(GROUND_FORM_PROPERTIES['end_time'])
##         form.keep_values_entry.assign(GROUND_FORM_PROPERTIES['keep_values'])
##         form.cancelled_entry.assign(GROUND_FORM_PROPERTIES['statcode'])
##         form.complement.assign(GROUND_FORM_PROPERTIES['complement'])
##     try:
##         form()
##     except CancelledFormError, cf:
##         Errlog.log("ground_duty_handler:: user cancelled form")
##         return 1
##     except Exception, e:
##         return -1

##     global FORM_KEEP_VALUES
##     global GROUND_FORM_PROPERTIES

##     try:
##         FORM_KEEP_VALUES = form.keep_values
##         GROUND_FORM_PROPERTIES = form.get_gnd_task_props()
##         clist = []
##         for value in form.complement:
##             clist.append(int(value.valof()))
##         GROUND_FORM_PROPERTIES['complement'] = clist
##     except:
##         FORM_KEEP_VALUES = False
##         GROUND_FORM_PROPERTIES = None

    # Get task properties from the form.
##    ground_task_properties = form.get_gnd_task_props()

    st = ground_task_properties['st']
    et = ground_task_properties['et']
    tripname = ground_task_properties['tripname']
    # Decide how many objects to create.
    a_day = RelTime('24:00')
    start_date = st.day_floor()
    start_time = st.time_of_day()
    length = et - st
    # Whole day actvity check
    if int(length) % int(a_day) == 0:
        no_days = int((length)/a_day)
    else:
        no_days = int((length)/a_day + 1)
    time = length - a_day * (no_days - 1)
    attr = None
    if 'attr' in ground_task_properties:
        attr = ground_task_properties['attr']
    # Perform type conversion.
    airport = TM.airport[ground_task_properties['airport']]
    activity = TM.activity_set[ground_task_properties['taskcode']]
    statcode = TM.activity_status_set[["A","C"][ground_task_properties['statcode']]]

    # Try to set base according to chosen airport.
    # Default to CPH if non-base airport is chosen.
    if airport.id not in [base.airport.id for base in TM.crew_base_set]:
        trip_base = TM.crew_base_set['CPH']
    else:
        bases = TM.crew_base_set.search('(&(airport='+airport.id+'))')
        for base in bases:
            trip_base = base

    # Remember created trips for selection at end.
    trip_list = []
    created_tasks = 0
    reused_tasks = 0
    for day_no in range(0,no_days):
        task_udor = start_date + a_day * day_no
        task_st = task_udor + start_time
        task_et = task_st + time
        task_adep = airport
        task_ades = airport
        task_activity = activity
        task_statcode = statcode

        try:
            task_key = (str(task_udor), str(task_st), str(task_et), str(task_adep.id), str(task_activity.id))
        except:
            # Invalid input
            Gui.GuiWarning("Invalid input")
            return

        # Try and find existing task, matching udor, st, et, adep, and activity
        for task in TM.ground_task.search("(&(udor=%s)(st=%s)(et=%s)(adep=%s)(activity=%s))" %task_key):
            reused_tasks += 1
            task.statcode = task_statcode
            break
        else:
            created_tasks += 1
            # Create the ground task activity.
            task_uuid = TM.createUUID()
            task = TM.ground_task.create((task_udor, task_uuid))
            task.st = task_st
            task.et = task_et
            task.adep = task_adep
            task.ades = task_ades
            task.activity = task_activity
            task.statcode = task_statcode
            #niklas
            try:
                if attr:
                    qual_attr = 'QualType'
                    attr_vals = {'str': attr}
                    Attributes.SetGroundTaskAttr(task_udor, task.id, qual_attr, refresh=False, **attr_vals)
                    Attributes._refresh("ground_task_attr")
            except:
                Gui.GuiWarning("Invalid input")
        create_trip(task_udor, trip_base, tripname, complement, task, trip_list)
#    try:
#        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
#    except:
#        print "Error" + str(task)

    # Put newly created trip on top.
    # Select form needs all uppercase to work.
    # '/' character is a range function in the selectform.
    # Changing it to a '?' gives a slight risk of displaying the multiple trips.
  
    # Studio/Rave freaks out if to long list (> 1024 characters!!)
    if select:
        tmp_list = []
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        for trip_uuid in trip_list:
            if (len(tmp_list) + 1) * (24 +1) > 1024: # uuid is 24 chars + ','-char
                Select.select({'FILTER_METHOD': 'ADD',
                               'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                              area, Cui.CrrMode)
                tmp_list = []
            tmp_list.append(trip_uuid)
        if tmp_list:
            # finish of with the last ones!
            Select.select({'FILTER_METHOD': 'ADD',
                           'trip_uuid': ','.join(tmp_list).upper().replace('/','?')},
                      area, Cui.CrrMode)
    Errlog.log("ground_duty_handler: Created %s new tasks, reused %s old tasks" %(created_tasks, reused_tasks))
    return trip_list

def create_trip(task_udor, trip_base, tripname, complement, task, trip_list):
            # Create the trip.
        i = 0
        fc = False
        cc = False
        tfc = False

        for value in complement:
            if i < 4:
                if int(value) > 0:
                    fc = True
            elif i < 8:
                if int(value) > 0:
                    cc = True
            elif i < 10:
                if int(value) > 0:
                    tfc = True
            i += 1
        #Create the rows in trip table
        trip_udor = task_udor
        if fc:
            trip_uuid_fc = TM.createUUID()
            trip_list.append(trip_uuid_fc)
            trip_fc = TM.trip.create((trip_udor, trip_uuid_fc))
            trip_fc.base = trip_base
            trip_fc.adhoc = tripname
        if cc:
            trip_uuid_cc = TM.createUUID()
            trip_list.append(trip_uuid_cc)
            trip_cc = TM.trip.create((trip_udor, trip_uuid_cc))
            trip_cc.base = trip_base
            trip_cc.adhoc = tripname
        if tfc:
            trip_uuid_tfc = TM.createUUID()
            trip_list.append(trip_uuid_tfc)
            trip_tfc = TM.trip.create((trip_udor, trip_uuid_tfc))
            trip_tfc.base = trip_base
            trip_tfc.adhoc = tripname

        # Attributes cc_0 - cc_11 on the trip contains the crew complement.
        i = 0
        for value in complement:
            if i < 4:
                if fc:
                    # Attributes cc_0 - cc_3 on the trip contains the crew complement.
                    setattr(trip_fc, "cc_"+str(i), int(value))
                if cc: #Alway zero for pos 0-3
                    setattr(trip_cc, "cc_"+str(i), 0)
                if tfc:
                    setattr(trip_tfc, "cc_"+str(i), 0)
            elif i < 8:
                # Attributes cc_4 - cc_7 on the trip contains the crew complement.
                if fc: #Alway zero for pos 0-3
                    setattr(trip_fc, "cc_"+str(i), 0)
                if cc:
                    setattr(trip_cc, "cc_"+str(i), int(value))
                if tfc: #Alway zero for pos 8-9
                    setattr(trip_tfc, "cc_"+str(i), 0)
            elif i < 10:
                if fc: #Alway zero for pos 0-3
                    setattr(trip_fc, "cc_"+str(i), 0)
                if cc: #Alway zero for pos 4-7
                    setattr(trip_cc, "cc_"+str(i), 0)
                if tfc:
                    # Attributes cc_8 - cc_9 on the trip contains the crew complement.
                    setattr(trip_tfc, "cc_"+str(i), int(value))
            i += 1
           
        while i < 12:
            if fc:
                setattr(trip_fc, "cc_"+str(i), 0)
            if cc:
                setattr(trip_cc, "cc_"+str(i), 0)
            if tfc:
                setattr(trip_tfc, "cc_"+str(i), 0)
            i += 1
        # The trip_ground_duty record requires base as part of the key.
        # - is used as "no base".
        fake_base = TM.crew_base_set.getOrCreateRef('-')
        if fc:
            TM.trip_ground_duty.create((trip_fc, task, fake_base))
        if cc:
            TM.trip_ground_duty.create((trip_cc, task, fake_base))
        if tfc:
            TM.trip_ground_duty.create((trip_tfc, task, fake_base))
        # Connect the trip and the ground_task.
#        if fc:
#            trip_ground_duty = TM.trip_ground_duty.create((trip_fc, task, fake_base))
#        if cc:
#            trip_ground_duty1 = TM.trip_ground_duty.create((trip_cc, task, fake_base))
#        if tfc:
#            trip_ground_duty2 = TM.trip_ground_duty.create((trip_tfc, task, fake_base))

        # If the trip is a SIM and the booked value is other than need value,
        # update the need value in the ground_duty_attr table
        ## task_codes = {}
##         for x in TM.activity_set:
##             task_codes[x.id] = x.grp.id
            
##         taskname = ground_task_properties['taskcode']

##         if task_codes[taskname] in ['OPC','AST','ASF','FFS','SIM']:
##             need_list = []
##             for i in range(1,11):
##                 try:
##                     special, = R.eval('crew_pos.%%sim_has_external_instructor%%("%s")' % taskname)
##                     need, = R.eval('crew_pos.%%_sim_need_pos%s%%("%s", %s, %s)' % (i,task_codes[taskname], special, task_udor))
##                     need_list.append(need)
##                 except:
##                     need_list.append(0)
##             form_list = []
##             for value in form.complement:
##                 form_list.append(int(value.valof()))
##             if form_list != need_list:
##                 set_sim_need(taskname, form.complement, task_udor, task.id)
    # Synchronize the generic and classic models.

# Set the need value to match the crew complement - SIMs only        
def set_sim_need(taskname, complement, task_udor, task_id, multisim=False):

    # Create a tuple from the form's crew complement
    _sim_comp = []
    i = 0
    for value in complement:
        if i < 3:
            _sim_comp.append(int(value.valof()))
        if i > 7:
            _sim_comp.append(int(value.valof()))
        i += 1
    sim_comp = tuple(_sim_comp)	
		
    # Check if the task code is a SIM
    sim_exc_attr = "SIM EXC"
    comp_int = 0
    fact = 4
    for pos in sim_comp:
        comp_int += pos * (20**fact)
        fact -= 1
    fact = 2

    attr_vals = {"int":comp_int}
    if multisim:
        attr_vals['str'] = 'multisim'

    # Update the need value in the ground_task_attr table
    Attributes.SetGroundTaskAttr(task_udor, task_id, sim_exc_attr, refresh=False, **attr_vals)
    Attributes._refresh("ground_task_attr")
			
def change_ground_task_status(statcode="A"):
    """
    Change statcode of all marked ground_tasks.

    """

    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    statcode = TM.activity_status_set[(statcode,)]
    
    # Get the window the script is run from.
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    Select.select({'FILTER_METHOD': 'REPLACE',
                   'marked': 'TRUE'},
                  Cui.CuiScriptBuffer, Cui.CrrMode)

    # Build RAVE expression 
    leg_expr = R.foreach(
        R.iter('iterators.leg_set', where = ('marked',
                                             'leg.%is_nop%',
                                             'leg.%is_ground_duty%')),
        'ground_uuid',
        'gdor',
        )

    # Evaluate RAVE expression
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
    legs, = R.eval('default_context', leg_expr)
    # print 'leg',legs
    for (ixLeg, ground_uuid, gdor) in legs:
        if not ground_uuid:
            continue
        task = TM.ground_task[(gdor, ground_uuid)]
        task.statcode = statcode

    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

# __main__ ==============================================================={{{1
if __name__ == '__main__':
    create_ground_duty()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
