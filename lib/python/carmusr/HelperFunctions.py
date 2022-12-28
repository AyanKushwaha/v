
# [acosta:08/101@11:59] Merged and removed Utils.py into this module,
#    added generic roster selection code.

"""
Utility Functions / Classes for Studio.

Put functions that are useful for manipulation of Studio objects here.

This module is a merge from several other utility modules (Utils, ...).

Avoid putting generic string functions and other general things in this module,
there are other better places for such things.

Examples:
    time and date handling -> utils.time_util
    miscellaneous string functions, general parsing -> utils.divtools
    'Gui' updates -> utils.guiutil
"""

import Cui
import Csl
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions

from AbsTime import AbsTime
from Variable import Variable
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator


# globals ================================================================{{{1
csl = Csl.Csl()


# Context evaluation ====================================================={{{1

# ChainObject ------------------------------------------------------------{{{2
class ChainObject:
    """Base class"""
    def __init__(self, mode, id=None, area=None):
        self.mode = mode
        if mode == Cui.CrewMode:
            self.selected_object = 'levels.chain'
        elif mode == Cui.CrrMode:
            self.selected_object = 'levels.trip'
        elif mode == Cui.LegMode:
            self.selected_object = 'levels.leg'
        if area is None:
            self.area = Cui.CuiWhichArea
        else:
            self.area = area
        if id is None:
            # This assumes the object is generated from an object function
            self.CCL = CuiContextLocator(self.area, "object")
        else:
            self.CCL = CuiContextLocator(self.area, "object", mode, id)

    def eval(self, *eval_string):
        self.CCL.reinstate()
        # Old comment (2008): BZ 29425
        # Temporary solution since definitions like
        # level trip = levels.chain doesn't work 
        try:
            R.level(self.selected_object)
            level = self.selected_object
        except R.UsageError: 
            level = 'levels.chain'
        output = R.eval(R.selected(level), *eval_string)
        return output
        

# CrewObject -------------------------------------------------------------{{{2
class CrewObject(ChainObject):
    def __init__(self, crew_id=None, area=None):
        ChainObject.__init__(self, mode=Cui.CrewMode, id=crew_id, area=area)


# TripObject -------------------------------------------------------------{{{2
class TripObject(ChainObject):
    def __init__(self, trip_id=None, area=None):
        ChainObject.__init__(self, mode=Cui.CrrMode, id=trip_id, area=area)


# LegObject --------------------------------------------------------------{{{2
class LegObject(ChainObject):
    def __init__(self, leg_id=None, area=None):
        ChainObject.__init__(self, mode=Cui.LegMode, id=leg_id, area=area)


# Roster Selection ======================================================={{{1

# RosterSelectionError----------------------------------------------------{{{2
class RosterSelectionError(Exception):
    """ Illegal selection. """
    msg = ''

    def __init__(self, msg, title="Selection Error"):
        self.msg = msg
        self.title = title

    def __str__(self):
        return str(self.msg)


# RosterTimeSelection ----------------------------------------------------{{{2
class RosterTimeSelection:
    """ 
    Let user select start and end point, save key values as attributes.
    crew  -> crew id
    area  -> selected area
    st    -> start time of interval (in UTC)
    et    -> end time of interval (in UTC)
    """
    def __init__(self, validate_func=None):
        area, crew, t1 = roster_selection(validate_func=validate_func)
        self.area, self.crew, t2 = roster_selection(area=area, crew=crew,
                                                    validate_func=validate_func)
        self.st = min(t1, t2)
        self.et = max(t1, t2)

    def __str__(self):
        return "%s crew %s %s - %s" % (self.__class__.__name__, self.crew,
                self.st, self.et)

    def round_down(self, time, hb=False):
        """Round down time to nearest day. If 'hb' is True use home base date.
        Note: the time returned will still be in UTC."""
        if hb:
            return hb2utc(self.crew, utc2hb(self.crew, time).day_floor())
        else:
            return time.day_floor()

    def round_up(self, time, hb):
        """Round up time to nearest day. If 'hb' is True use home base date.
        Note: the time returned will still be in UTC."""
        if hb:
            return hb2utc(self.crew, utc2hb(self.crew, time).day_ceil())
        else:
            return time.day_ceil()


# RosterDateSelection ----------------------------------------------------{{{2
class RosterDateSelection(RosterTimeSelection):
    """
    Select start and end points, 'st' and 'et' are adjusted to nearest date. If
    'hb' is true use homebase dates.
    Example:
        20                        21
        |x-----x     |            |      UTC
        |=========================|      Adjusted to UTC date.

      20                        21
      |  x-----x     |          |        HB
      |=========================|        Adjusted to HB date.

    User clicks 01:00 and on 05:00 the 20th (UTC time), crew has home base ARN
    (UTC+01:00 or UTC+02:00 in the summer).

    Return values are:
        (1 hb=False):  2008-06-20T00:00 - 2008-06-21T00:00
        (2 hb=True):   2008-06-19T22:00 - 2008-06-20T22:00

    NOTE: the values of 'st' and 'et' will always be in UTC time!
    """
    def __init__(self, hb=False, validate_func=None):
        RosterTimeSelection.__init__(self, validate_func=validate_func)
        self.st = self.round_down(self.st, hb)
        self.et = self.round_up(self.et, hb)


# RosterDaySelection -----------------------------------------------------{{{2
class RosterDaySelection(RosterTimeSelection):
    """
    Select specific day, ('st' = day start, 'et' = day end) with a single
    click.

    The optional parameter 'hb' will select day based on home base time.
    See comments above for RosterDateSelection().

    Note: the values of 'st' and 'et' will always be in UTC time!
    """
    def __init__(self, hb=False, validate_func=None):
        self.area, self.crew, t = roster_selection(validate_func=validate_func)
        self.st = self.round_down(t, hb)
        self.et = self.round_up(t, hb)


# functions =============================================================={{{1

# roster_selection -------------------------------------------------------{{{2
def roster_selection(area=None, crew=None, validate_func=None, interactive=True):
    """Let user click on roster to select crew member and time point."""
    while True:
        try:
            crew_variable = Variable("", 30)
            time_variable = Variable(0)
            Cui.CuiSelectTimeAndRow(Cui.gpc_info, Cui.CuiWhichArea,
                    Cui.CrewMode, time_variable, crew_variable, 30)
            clicked_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            clicked_crew = crew_variable.value
            clicked_time = AbsTime(time_variable.value)
            if (area is not None and area != clicked_area):
                if not cfhExtensions.confirm(
                    "Both selection points must be in the same roster window.\n"
                    "Continue?"):
                    raise RosterSelectionError("User cancelled operation (first area != second area).")
                continue
            if (crew is not None and crew != clicked_crew or not clicked_crew):
                if not cfhExtensions.confirm(
                    "Both selection points must be on the same roster.\n"
                    "Continue?"):
                    raise RosterSelectionError("User cancelled operation (first crew != second crew).")
                continue
            # Next call will raise exception if not in crew area
            Cui.CuiCheckAreaMode(Cui.gpc_info, clicked_area, Cui.CrewMode)
            # Perform user-supplied validation, if provided.
            if validate_func is not None:
                error = validate_func(clicked_area, clicked_crew, clicked_time)
                if error:
                    if not cfhExtensions.confirm("%s\nContinue?" % error):
                        raise RosterSelectionError("Validation failed.")
                    continue
            return clicked_area, clicked_crew, clicked_time
        except RosterSelectionError:
            raise
        except KeyboardInterrupt:
            raise RosterSelectionError("User cancelled operation (right click, or clicked outside).")
        except:
            if not interactive or not cfhExtensions.confirm(
                "Please click on a roster.\n"
                "Continue?"):
                raise RosterSelectionError("User cancelled operation (not a roster).")


# Miscellaneous =========================================================={{{1

# isDBPlan ---------------------------------------------------------------{{{2
def isDBPlan():
    """
    This function checks that the currently
    loaded plan is a database-plan
    """
    isDbPlan = Variable(0)
    Cui.CuiSubPlanIsDBPlan(Cui.gpc_info, isDbPlan)
    return isDbPlan.value


# Area handling =========================================================={{{1

# get_specific_area ------------------------------------------------------{{{2
def get_specific_area(area):
    """
    Open specified area if it isn't already visible in Studio.
    'area' must refer to a displayable window (CuiArea0..CuiAreaN(.
    """
    assert Cui.CuiArea0 <= area < Cui.CuiAreaN, "Area must be displayable."
    removeareas = []
    try:
        for n in range(Cui.CuiAreaN):
            varea = Variable(-1)
            Cui.CuiGetArea(Cui.gpc_info, area, varea, 0)
            # If the specified area wasn't visible, a new window was opened.
            # The new window is always the lowest numbered non-visible one,
            # so it's not guaranteed to be the one that was specified.
            if varea.value == area:
                return area
            # A non-specified window was opened. Save its id and retry.
            removeareas.append(varea.value)
    finally:
        # Remove any non-specified window that was opened in the process.
        for rarea in removeareas:
            Cui.CuiRemoveArea(Cui.gpc_info, rarea)
    return area


# get_suitable_area ------------------------------------------------------{{{2
def get_suitable_area(mode=None):
    """
    Get a suitable studio window in the following priority order:
        1) If 'mode' is specified, try to find an existing window in that mode.
        2) Try to find an existing empty window.
           (Please note that only mode-less windows are considered empty.)
        3) Open a new window.
        4) If there are four visible, non-empty areas in the wrong mode,
           the last available (CuiAreaN-1) will be selected.
    The returned area id is guaranteed to be visible,
    but not to be empty and in the correct mode.
    """
    area = -1
    if mode is not None:
        area = Cui.CuiGetAreaInMode(Cui.gpc_info, mode)
    if area < 0:
        try:
            varea = Variable(-1)
            Cui.CuiGetArea(Cui.gpc_info, Cui.CuiNoArea, varea)
            area = varea.value
        except:
            area = Cui.CuiAreaN - 1
    return area
        

# redrawArea -------------------------------------------------------------{{{2
def redrawArea(area=Cui.CuiWhichArea):
    """Redraw given area."""
    csl.evalExpr("CuiRedrawArea(gpc_info,%s)" % area)


# redrawAreas ------------------------------------------------------------{{{2
def redrawAreas():
    """Redraw all areas."""
    csl.evalExpr("CuiRedrawAllAreas(gpc_info,CuiDumpAll)")


# redrawAreaScrollHome ---------------------------------------------------{{{2
def redrawAreaScrollHome(area=Cui.CuiWhichArea):
    """Redraw area, scroll to home.""" 
    csl.evalExpr("CuiRedrawArea(gpc_info,%s, CuiRedrawHome)" % area)


# redrawAllAreas ---------------------------------------------------------{{{2
def redrawAllAreas(mode=None):
    """Redraw all areas or, if a mode is given, all areas in that mode."""
    if mode is None:
    	redrawAreas()
    else:
        for area in range(Cui.CuiAreaN):
            try:
                if not mode is None:
                    Cui.CuiCheckAreaMode(Cui.gpc_info, area, mode)
                redrawArea(area)
            except:
                pass


# Position - Rank conversion ============================================={{{1

# pos2rank ---------------------------------------------------------------{{{2
def pos2rank(pos):
    mapping = {1:"FC", 2:"FP", 3:"FR", 4:"FU",
               5:"AP", 6:"AS", 7:"AH", 8:"AU",
               9:"TL", 10:"TR"}
    return mapping[pos]


# Marking / unmarking ===================================================={{{1
    
# getMarkedLegs ----------------------------------------------------------{{{2
def getMarkedLegs(area):
    """
    Get a list of marked legs in the specified area.
    """
    return Cui.CuiGetLegs(Cui.gpc_info, area, 'marked')
    
    
# markLegs ---------------------------------------------------------------{{{2
def markLegs(area, leg_ids, ignore_leg_ids=""):
    """
    Set rave keyword 'marked' to true for the specified legs.
    Note: the current selected object will be changed in the specified area.
    """
    markToggleLegs(
        area, leg_ids, flags=Cui.CUI_MARK_SET, ignore_leg_ids=ignore_leg_ids)


# unmarkLegs -------------------------------------------------------------{{{2
def unmarkLegs(area, leg_ids, ignore_leg_ids=""):
    """
    Set rave keyword 'marked' to false for the specified legs.
    Note: the current selected object will be changed in the specified area.
    """
    markToggleLegs(
        area, leg_ids, flags=Cui.CUI_MARK_CLEAR, ignore_leg_ids=ignore_leg_ids)


# unmarkAllLegs ----------------------------------------------------------{{{2
def unmarkAllLegs(area):
    """
    Unmark all legs in the specified area.
    """
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, area, 'WINDOW')
    

# markToggleLegs ---------------------------------------------------------{{{2
def markToggleLegs(area, leg_ids, flags=Cui.CUI_MARK_DEFAULT, ignore_leg_ids=""):
    """
    Set, clear or toggle rave keyword 'marked' for the specified legs.
    Note: the current selected object will be changed in the specified area.
    """
    if leg_ids:
        leg_ids = str(leg_ids).replace(" ","").replace("'","").strip("[()],").split(',')
        ignore_leg_ids = str(ignore_leg_ids).replace(" ","").replace("'","").strip("[()],").split(',')
        for id in leg_ids:
            if id not in ignore_leg_ids:
                try:
                    Cui.CuiSetSelectionObject(Cui.gpc_info,area,Cui.LegMode,id)
                except:
                    print ("HelperFunctions::markToggleLegs: info: "
                           "non-existing leg '%s' - ignored" % id)
                else:
                    Cui.CuiMarkLegs(Cui.gpc_info, area, "object", flags)


# Homebase time conversion ==============================================={{{1

# utc2hb -----------------------------------------------------------------{{{2
def utc2hb(crewid, time):
    """Convert 'time' in UTC to homebase time for 'crewid'."""
    return R.eval('station_localtime(default(fundamental.%%base2station%%(crew_contract.%%base_at_date_by_id%%("%s", %s)), "CPH"), %s)' % (
        crewid, time, time))[0]


# hb2utc -----------------------------------------------------------------{{{2
def hb2utc(crewid, time):
    """Convert 'time' in homebase time for 'crewid' to UTC."""
    return R.eval('station_utctime(default(fundamental.%%base2station%%(crew_contract.%%base_at_date_by_id%%("%s", %s)), "CPH"), %s)' % (
        crewid, time, time))[0]


# Local time conversion =================================================={{{1

# utc2lt -----------------------------------------------------------------{{{2
def utc2lt(airport, time):
    """Convert 'time' in UTC to localtime for 'airport'."""
    return R.eval('station_localtime("%s", %s)' % (airport, str(time)))[0]


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    """Basic tests."""
    print RosterDateSelection() 
    print RosterDateSelection(hb=True) 


# Testing ==============================================================={{{1

# fix_ctl ----------------------------------------------------------------{{{2
def fix_ctl():
    """Fix crew_training_log, modify types and codes for sim activities."""
    from tm import TM
    from utils.dave import EC, RW, Record, txninfo

    def update_db(op, map_, key):
        (crew, tim, typ, code) = key
        rec = Record({}, ec.crew_training_log.translator)
        rec.crew = crew
        rec.tim = tim
        rec.typ = typ
        rec.code = code
        rec.attr = map_[key]
        #print "%(crew)s %(typ)-30s %(code)-10s %(tim)d %(attr)-10.10s" % rec, op
        op(rec)
    
    # Find all rows in fixed ctl that might be wrong, LPC, OPC, SIM ASSIST
    ec = EC(TM.getConnStr(), TM.getSchemaStr())
    rw = RW(ec)

    removed = {}
    inserted = {}
    updated = {}

    ecSearch = "tim > %s AND typ IN ('LPC', 'OPC', 'OTS', 'SIM ASSIST')" % int(AbsTime(2007, 1, 1, 0, 0))

    for row in ec.crew_training_log.search(ecSearch):
        ctl_migr_data, = R.eval(
            R.foreach(R.times(3),
                'training_log.%%ctl_migr_typ_ix%%("%s", %s)' % (row.crew, row.tim),
                'training_log.%%ctl_migr_code_ix%%("%s", %s)' % (row.crew, row.tim),
                'training_log.%%ctl_migr_attr_ix%%("%s", %s)' % (row.crew, row.tim)
                ))

        D = {}
        for (ix, typ, code, attr) in ctl_migr_data:
            if typ is None:
                break
            if attr == '':
                attr = None
            D[typ] = (code, attr)
            if typ == 'LPC':
                # If typ == 'LPC' we will use that and skip the rest.
                break

        if 'LPC' in D:
            # First choice
            typ = 'LPC'
        elif 'OPC' in D:
            # Second choice
            typ = 'OPC'
        elif 'OTS' in D:
            # Second choice
            typ = 'OTS'
        else:
            for typ in D:
                # Take any other type
                break
            else:
                # 'D' was empty
                continue
        code, attr = D[typ]
        if (typ, code) != (row.typ, row.code):
            # type or code was changed
            inserted[(row.crew, row.tim, typ, code)] = attr
            removed[(row.crew, row.tim, row.typ, row.code)] = row.attr
        elif attr != row.attr:
            # attribute was changed (unlikely)
            updated[(row.crew, row.tim, typ, code)] = attr

    for key in removed:
        update_db(rw.crew_training_log.dbdelete, removed, key)

    for key in inserted:
        update_db(rw.crew_training_log.dbwrite, inserted, key)

    for key in updated:
        update_db(rw.crew_training_log.dbupdate, updated, key)

    revid = rw.apply()
    print "saved with commitid", txninfo(ec, revid).commitid
    ec.close()


# fix_opc ----------------------------------------------------------------{{{2
def fix_opc():
    from tm import TM
    data, = R.eval("sp_crew",
                   R.foreach("iterators.roster_set",
                             "crew.%id%",
                             "training.%missing_opc_doc%",
                             "training.%new_opc_date%"))
    print data
    for (ix, crewid, opc_doc, opc_date) in data:
        if opc_doc:
            crew = TM.crew[(crewid,)]
            doc = TM.crew_document_set[("REC",opc_doc)]
            document = TM.crew_document[(crew, doc, AbsTime("1Jan1986"))]
            print ix, " Crew %s will have %s moved from %s to %s" %(crewid, opc_doc, document.validto, opc_date)
            document.validto = opc_date
            
    Cui.CuiReloadTable('crew_document', 1)   

# fix_opc ----------------------------------------------------------------{{{2
def fix_ots():
    from tm import TM
    data, = R.eval("sp_crew",
                   R.foreach("iterators.roster_set",
                             "crew.%id%",
                             "training.%missing_ots_doc%",
                             "training.%new_ots_date%"))
    print data
    for (ix, crewid, ots_doc, ots_date) in data:
        if ots_doc:
            crew = TM.crew[(crewid,)]
            doc = TM.crew_document_set[("REC",ots_doc)]
            document = TM.crew_document[(crew, doc, AbsTime("1Jan1986"))]
            print ix, " Crew %s will have %s moved from %s to %s" %(crewid, ots_doc, document.validto, ots_date)
            document.validto = ots_date
            
    Cui.CuiReloadTable('crew_document', 1)   

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
