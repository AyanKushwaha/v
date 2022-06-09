
# [acosta:08/057@12:51] Major rewrite connected to PublishV3.

"""
The functions are referenced in the menu_source files and some tracking
reports.

Sections:
1. Common classes and global variables
2. Private functions
3. User accessible functions

Note: some of the logic related to manual checkin has moved to Rave module.
"""

import os
import tempfile

import carmensystems.rave.api as R
import Cui
import Cfh
import Errlog
import Gui
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew
import carmusr.Attributes as Attributes

import carmstd.cfhExtensions as cfhExtensions
import cio.db
import cio.run
import cio.rv
import modcheckin

from AbsTime import AbsTime
from tm import TM
from cio.db import ciostatus
from utils.rave import MiniEval


__all__ = ['assistCheckInOutCrew', 'freezeUnfreezeBriefingTime', 'setCheckInOutTimes']

# 1. Common classes and global variables ================================={{{1

class Evaluator(dict):
    """Evaluate some values on current leg."""
    def __init__(self, fields):
        dict.__init__(self)
        self.area = Cui.CuiGetCurrentArea(Cui.gpc_info)
        me = MiniEval(fields)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.area, 'object')
        self.update(me.eval(R.selected(R.Level.atom())).__dict__)

    def __getattr__(self, key):
        return self.get(key, None)


# CIOValues --------------------------------------------------------------{{{2
class CIOValues(Evaluator):
    """Get some commonly used values."""
    def __init__(self, additional_fields={}):
        fields = {
            'crewid': 'crew.%id%',
            'now': 'fundamental.%now%',
            'logname': 'crew.%login_name%',
            'dp_brief_start_utc': 'leg.%duty_brief_start_utc%',
            'dp_debrief_end_utc': 'leg.%duty_debrief_end_utc%',
            'dp_checkin_activity': 'studio_process.%duty_checkin_activity%',
            'udor': 'leg.%udor%',
            'adep': 'leg.%start_station%',
            'flightid': 'leg.%flight_descriptor%',
            'dp_checkout_activity': 'studio_process.%duty_checkout_activity%',
            'dp_finished': 'duty.%is_finished%',
            'ci_comment': 'leg.%duty_ci_override_comment%',
            'co_comment': 'leg.%duty_co_override_comment%',
            'dp_start_leg_id': 'studio_process.%duty_briefing_leg%',
            'dp_end_leg_id': 'studio_process.%duty_debriefing_leg%',
            'briefing_leg_std': 'leg.%briefing_leg_std%',
            'has_frozen_start': 'leg.%has_frozen_duty_start%',
            'prev_debriefing_end': 'leg.%prev_debriefing_end%',
            'has_checkin': 'leg.%has_check_in%',
            }
        fields.update(additional_fields)
        Evaluator.__init__(self, fields)


# AssistCIOBox -----------------------------------------------------------{{{2
class AssistCIOBox(Cfh.Box):
    """Create Box with crew name and perkey, add four buttons (Check-in,
    Check-out, Undo and Cancel)."""

    # The cancel button will return -1
    return_values = (CANCEL, NO_ACTION, PRINT_REPORT) = (-1, 999, 1000)

    def __init__(self, crewid, name='ASSIST_CIO_BOX'):
        self._names = {}
        self.name = name
        Cfh.Box.__init__(self, name, 'Assisted Check-in/Check-out')
        self.setDim(Cfh.CfhDim(40, 3))

        r = cio.rv.EvalRoster(crewid)
        status = str(r.cio_status).split('.')[1]
        retval = self.NO_ACTION
        text = ''
        
        if status == 'ci':
            retval = ciostatus.CI|ciostatus.ASSISTED
            text = "Check-in"
        elif status == 'co':
            retval = ciostatus.CO|ciostatus.ASSISTED
            text = "Check-out"
        elif status == 'coi':
            retval = ciostatus.COI|ciostatus.ASSISTED
            text = "Check-out/Check-in"
        elif status == 'late4co':
            text = "Too late for check-out"
        elif status == 'early4ci':
            text = "Too early for check-in"
        elif status == 'alreadyci':
            text = "Already checked-in"
        elif status == 'alreadyco':
            text = "Already checked-out"

        # Text on the "action" button
        if retval == self.NO_ACTION:
            btext = 'N/A'
        else:
            btext = text

        self._crew = Cfh.Label(self, self._get_name(),
            Cfh.CfhArea(Cfh.CfhDim(30, 1), Cfh.CfhLoc(0, 0)), 
            "%s %s" % (r.extperkey, r.logname))
        self._crew.setStyle(Cfh.CfhSLabelHeader)
        self._text = Cfh.Label(self, self._get_name(),
            Cfh.CfhArea(Cfh.CfhDim(22, 1), Cfh.CfhLoc(1, 0)),
            text)
        self._cio = self.UserDefinedButton(self, self._get_name(),
                text=btext, retval=retval)
        self._report = self.UserDefinedButton(self, self._get_name(),
                text="Show Report", retval=self.PRINT_REPORT)
        self._undo = self.UserDefinedButton(self, self._get_name(), 
                text='Undo Check-In/-Out', retval=ciostatus.UNDO)
        self._cancel = self.UserDefinedButton(self, self._get_name(),
            text='Cancel', cancel=True)

        if retval == self.NO_ACTION:
            # Dim button.
            self._cio.setEnable(False)

        self.build()
        self.show(True)
        self.__result = self.loop() 
        if self.__result == self.CANCEL:
            # Cancel was pressed.
            raise AssistCIOBox.Cancelled()

    def __int__(self):
        """Return result code."""
        return self.__result

    def _get_name(self, key=None):
        """Generate a component name."""
        if key is None:
            key = self.name
        if key in self._names:
            self._names[key] += 1
        else:
            self._names[key] = 0
        return "%s-%d" % (key, self._names[key])

    # Cancelled ----------------------------------------------------------{{{3
    class Cancelled(Exception):
        def __str__(self):
            return "Operation aborted."

    # UserDefinedButton --------------------------------------------------{{{3
    class UserDefinedButton(Cfh.Function):
        """Button with return code."""
        def __init__(self, box, name, area=None, text=None, retval=-1, cancel=False):
            Cfh.Function.__init__(self, box, name, area)
            self.retval = retval
            self.cancel = cancel
            self.setText(text)

        def action(self):
            """Return if 'cancel' flag is set then "how" is 1, else "how" is 0
            (meaning that fields are validated etc.). A return code of -1 means
            that "Cancel" was pressed."""
            if self.cancel:
                self.finishForm(1, -1)
            else:
                self.finishForm(0, self.retval)


# SetCheckInOutForm ------------------------------------------------------{{{2
class SetCheckInOutForm(Cfh.Box):
    """Small box that gives user possibility to adjust check-in/check-out
    times and to add comments."""
    def __init__(self, rv):
        Cfh.Box.__init__(self, "SET_CHECKINOUT_FORM")

        layout = ["FORM;SET_CHECKINOUT_FORM;`Set times for %(logname)s (%(crewid)s)`", "COLUMN;30"]
        
        if not rv.dp_checkin_activity is None:
            layout.extend([
                "HEADER;`Check in`",
                "LABEL;`Time: %(dp_brief_start_utc)s.           Flight  %(dp_checkin_activity)s`",
                "FIELD;CIDATETIME;`New check-in time`",
                "FIELD;CICOMMENT;`Comment`",
            ])
            self.f_ci_datetime = Cfh.DateTime(self, "CIDATETIME",
                    int(rv.dp_brief_start_utc))
            self.f_ci_comment = Cfh.String(self, "CICOMMENT", 200, rv.ci_comment)
        if not rv.dp_checkout_activity is None:
            if rv.has_check_in:
                layout.append("SEPARATOR;")
            layout.extend([
                "HEADER;`Check out`",
                "LABEL;`Time: %(dp_debrief_end_utc)s.           Flight  %(dp_checkout_activity)s`",
                "FIELD;CODATETIME;`New check-out time`",
                "FIELD;COCOMMENT;`Comment`",
            ])
            self.f_co_datetime = Cfh.DateTime(self, "CODATETIME",
                    int(rv.dp_debrief_end_utc))
            self.f_co_comment = Cfh.String(self, "COCOMMENT", 200, rv.co_comment)
            if rv.has_frozen_start:
                # It is not possible to change the check-in time if it's frozen.
                self.f_ci_datetime.setEditable(False)
                self.f_ci_datetime.setStyle(Cfh.CfhSLabelNormal)
                self.f_ci_comment.setEditable(False)
                self.f_ci_comment.setStyle(Cfh.CfhSLabelNormal)
            if not rv.dp_finished:
                # It is not possible to change the check-out time until after
                # the duty
                self.f_co_datetime.setEditable(False)
                self.f_co_datetime.setStyle(Cfh.CfhSLabelNormal)
                self.f_co_comment.setEditable(False)
                self.f_co_comment.setStyle(Cfh.CfhSLabelNormal)

        self.f_ok = Cfh.Done(self, "OK")
        self.f_cancel = Cfh.Cancel(self, "CANCEL")

        # Use this template together with the rave values in rv.
        layout.extend([
            "BUTTON;OK;`Ok`;`_Ok`",
            "BUTTON;CANCEL;`Cancel`;`_Cancel`",
        ])

        fd, fn = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        f.write('\n'.join(layout) % rv)
        f.close()
        self.load(fn)
        os.unlink(fn)
        self.show(True)

    @property
    def ci_datetime(self):
        return AbsTime(self.f_ci_datetime.valof())

    @property
    def co_datetime(self):
        return AbsTime(self.f_co_datetime.valof())

    @property
    def ci_comment(self):
        return self.f_ci_comment.valof()

    @property
    def co_comment(self):
        return self.f_co_comment.valof()


# 2. Private functions ==================================================={{{1

# _refresh ---------------------------------------------------------------{{{2
def _refresh():
    """Refresh and redraw."""
    for table in ('crew_flight_duty_attr', 'crew_ground_duty_attr',
            'crew_activity_attr', 'ci_frozen', 'cio_status', 'cio_event'):
        Cui.CuiReloadTable(table, Cui.CUI_RELOAD_TABLE_SILENT)
    Gui.GuiCallListener(Gui.ActionListener)
    HF.redrawAllAreas(Cui.CrewMode)


# 3. Public functions. ==================================================={{{1

# assistCheckInOutCrew ---------------------------------------------------{{{2
def assistCheckInOutCrew():
    """Called from LeftDat24CrewComp_Tracking.menu.  Calls
    report_sources/hidden/CIOReport.py, where also all of the logic has
    moved."""
    c = CIOValues({
        'estimated_et': 'checkinout.%estimated_et%',
        'estimated_st': 'checkinout.%estimated_st%',
    })

    if c.estimated_st is None:
        cfhExtensions.show("There are no more duties left in the period to "
                "check in to or out from")
        return 1

    try:
        # Ask user for action
        action = int(AssistCIOBox(c.crewid))
        if action == ciostatus.UNDO:
            try:
                crew_ref = TM.crew[c.crewid,]
                rec = TM.cio_status[crew_ref,]
                rec.remove()
                _refresh()
                modcrew.add(c.crewid)
            except:
                print "cio_status remove failed"
        elif action == AssistCIOBox.PRINT_REPORT:
            # Create the HTML/PDF report
            
            cio.run.prt_report(c.crewid)
        else:
            cio.db.record_cio_event(c.crewid, c.now, st=c.estimated_st,
                    et=c.estimated_et, status=action, assisted=True)
            if action & ciostatus.CI:
                # Was a check-in
                cio.db.set_ci_frozen(c.crewid, c.estimated_st,
                        comment="Frozen at assisted check-in")
            _refresh()
            modcrew.add(c.crewid)

    except AssistCIOBox.Cancelled:
        # Canceled by user
        return 1

    return 0


# freezeUnfreezeBriefingTime ---------------------------------------------{{{2
def freezeUnfreezeBriefingTime():
    """
    Freeze duty start if not already frozen.
    Remove ALL possible frozen duty starts for duty if frozen.

    """

    Errlog.log("CHECKINOUT: Freeze/Unfreeze duty start.")

    # Get some rave values
    c = CIOValues()

    if c.dp_checkin_activity is None and c.dp_checkout_activity is None:
        cfhExtensions.show("This activity does not have check-in or check-out.",
                title="No check-in/check-out.")
        return 1

    # Get a reference to the crew entity.
    crew = TM.crew[(c.crewid,)]

    # If the duty start is already frozen, remove all freeze records.
    if c.has_frozen_start:
        Errlog.log("CHECKINOUT: Remove freeze between %s and %s for crew %s." %(c.prev_debriefing_end, c.briefing_leg_std, c.crewid))
        for frozen in crew.referers("ci_frozen", "crew"):
            if frozen.dutystart > c.prev_debriefing_end and frozen.dutystart <= c.briefing_leg_std:
                frozen.remove()

    # Else create a freeze record for the current duty start time.
    else:
        Errlog.log("CHECKINOUT: Set freeze at %s for crew %s." %(c.dp_brief_start_utc, c.crewid))
        try:
            new_frozen = TM.ci_frozen.create((crew, c.dp_brief_start_utc))
        except:
            new_frozen = TM.ci_frozen[(crew, c.dp_brief_start_utc)]
        new_frozen.si = c.ci_comment

    _refresh()

    Errlog.log("CHECKINOUT: Freeze/Unfreeze duty start... DONE")


# setCheckInOutTimes -----------------------------------------------------{{{2
def setCheckInOutTimes():
    """Opens a dialog where the user can set overloaded check-in/out times for
    the current duty. Must be run from context menu with selected duty."""

    Errlog.log("CHECKINOUT: In setCheckInOutTimes")

    currentArea = Cui.CuiGetCurrentArea(Cui.gpc_info)

    # Get some rave values
    c = CIOValues()

    if c.dp_checkin_activity is None and c.dp_checkout_activity is None:
        cfhExtensions.show("This activity does not have check-in or check-out.",
                title="No check-in/check-out.")
        return 1

    form = SetCheckInOutForm(c)
    if form.loop():
        Errlog.log("CHECKINOUT: setCheckInOutTimes Cancelled")
        return 1
        
    Cui.CuiSetCurrentArea(Cui.gpc_info, currentArea)
    if not c.dp_checkin_activity is None and (
            form.ci_datetime != c.dp_brief_start_utc
            or form.ci_comment != c.ci_comment):
        brief_time = c.briefing_leg_std - form.ci_datetime
        Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.LegMode, str(c.dp_start_leg_id))
        if form.ci_datetime == AbsTime(-1):
            Errlog.log("CHECKINOUT: setCheckInOutTimes, Removing manually set Check-in.")
            Attributes.RemoveAssignmentAttrCurrent("BRIEF", False)
        else:
            Errlog.log("CHECKINOUT: setCheckInOutTimes, Setting new Check-in to %s." % form.ci_datetime)
            Attributes.SetAssignmentAttrCurrent("BRIEF", False, rel=brief_time, str=form.ci_comment)

        modcrew.add(c.crewid)

    if not c.dp_checkout_activity is None and (
            form.co_datetime != c.dp_debrief_end_utc 
            or form.co_comment != c.co_comment):
        debrief_end_time = form.co_datetime
        Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.LegMode, str(c.dp_end_leg_id))
        if form.co_datetime == AbsTime(-1):
            Errlog.log("CHECKINOUT: setCheckInOutTimes, Removing manually set Check-out.")
            Attributes.RemoveAssignmentAttrCurrent("DEBRIEF", False)
        else:
            Errlog.log("CHECKINOUT: setCheckInOutTimes, Setting new Check-out to %s." % form.co_datetime)
            Attributes.SetAssignmentAttrCurrent("DEBRIEF", False, abs=debrief_end_time, str=form.co_comment)

        modcrew.add(c.crewid)

    _refresh()
    return 0

def freezeEstimatedBlockOff():
    """
    Freeze estimated block-off. Used mostly for maintaining
    correct per-diem compsenation when crew is delayed at home.
    """

    Errlog.log("CHECKINOUT: Freeze estimated block-off.")
    
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
    
        # Get some rave values
        c = CIOValues()
    
        if (c.dp_checkin_activity is None):
            continue
        
        if not c.has_checkin:
            continue

        # If the duty start is already frozen, remove all freeze records.
        if c.has_frozen_start:
            continue

        etd, = R.eval(R.selected("levels.leg"), 'leg.%activity_estimated_start_time_utc%')
        Errlog.log("CHECKINOUT: Freeze estimated block-off at %s for crew %s." % (etd, c.crewid))
    
        ci_new, = R.eval(R.selected("levels.leg"), 'leg.%activity_estimated_start_time_utc% - leg.%check_in_default%')
        
        if ci_new < AbsTime("01Jan1986 00:00"):
            continue
            
        brief_time = c.briefing_leg_std - ci_new 
        Attributes.SetAssignmentAttrCurrent("FROZEN_EST_BLKOFF", False, abs=etd)
    
        Errlog.log("CHECKINOUT: Old check-in is %s."% c.dp_brief_start_utc)
        Errlog.log("CHECKINOUT: Freeze estimated block-off, Setting new Check-in to %s." % ci_new)
        Attributes.SetAssignmentAttrCurrent("BRIEF", False, rel=brief_time, str="New check-in time after Freeze estimated block-off")
    
        modcrew.add(c.crewid)
        modcheckin.add(c.crewid, c.udor, c.flightid, c.adep, brief_time)

    _refresh()

    Errlog.log("CHECKINOUT: Freeze estimated block-off... DONE")

def unfreezeEstimatedBlockOff():
    """
    Remove frozen estimated block-off.
    """

    Errlog.log("CHECKINOUT: Un-freeze estimated block-off.")
  
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
        # Get some rave values
        c = CIOValues()
    
        if c.dp_checkin_activity is None:
            continue
    
        # Get a reference to the crew entity.
        etd, = R.eval(R.selected("levels.leg"), 'leg.%frozen_estimated_block_off_time%')
        if not etd:
            continue

    
        Errlog.log("CHECKINOUT: Unset estimated block-off freeze at %s for crew %s." % (etd, c.crewid))
        
        Attributes.RemoveAssignmentAttrCurrent("FROZEN_EST_BLKOFF", False)
    
    
        Errlog.log("CHECKINOUT: Un-freeze estimated block-off, Removing Check-in time set due to previously set Freeze estimated block-off.")
        Attributes.RemoveAssignmentAttrCurrent("BRIEF", False)
    
        modcrew.add(c.crewid)
    _refresh()

    Errlog.log("CHECKINOUT: Unset estimated block-off... DONE")
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
