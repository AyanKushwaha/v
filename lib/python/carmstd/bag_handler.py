#
# Added to SAS CARMUSR from OTS CARMUSR with minimal changes
# in March 2012
#
# By Stefan Hammar
#
"""
Purpose:
    Classes to use to get top bags in reports and scripts.

Background:
    With select-and-operate it is a not-trivial task to create
    top bags in a correct way. There is also a risk that the
    select-and-operate standard will be changed in the future.
    Therefore top-bag definitions should be made in one place.

About the classes:
   All classes in the module provide two public attributes:
       warning - A text with information about the content
                 if there is something problematic.
       bag     - The bag. May be None. All code using the classes
                 must handle the None case.

   Traps: * You must always keep a reference to the BagHandler object
            as long as you use its bag.
          * You should not change plan data while you are using a
            bag from a BagHandler object.
          (The traps are consequences of CpmBuffer weaknesses and
           may be gone in future CARMSYS releases)

   Note:  * The implementation has been made so the behaviour is
            kept when Rave becomes able to handle empty bags.
          * The Roster BagHandlers only consider rosters. The others
            work for all kinds of chains.
          * CARMSYS version 16.8 or later is needed.

Limitation:
    This module can't be used in reports you generate in batch.
    The reason is that cui/cpm-buffers do not work well in batch.


Example of usage in a trip report:

----------------------------------------------------------
import carmensystems.publisher.api as prt

import report_sources.include.standardreport as std
from carmstd import bag_handler

class Report(prt.Report):

    def create(self):

        tbh = bag_handler.MarkedTripsMain()

        self.add(std.standard_header(self, "Trip Report", tbh.warning))
        self.add(std.standard_footer(self))

        if not tbh.bag:
            return

        for trip_bag in tbh.bag.iterators.trip_set();
            ...

-----------------------------------------------------------
"""

import Localization as L
import carmensystems.rave.api as rave
import carmensystems.studio.cpmbuffer as cpmb
import carmensystems.studio.cuibuffer as cuib
import Cui
from Variable import Variable
from __main__ import exception as StudioError #@UnresolvedImport


def get_ref_plan_number(rp_id):
    """
    @type rp_id: int
    @param rp_id: cpmb.REF_PLAN_1 or cpmb.REF_PLAN_2
    @return: 1 or 2
    @rtype: int
    @raise KeyError: if the rp_id is illegal.
    """
    return {cpmb.REF_PLAN_1 : 1,
            cpmb.REF_PLAN_2 : 2}[rp_id]


def _get_loc_tuple(s, *args):
    """
    Creates a tuple with one not translated and one translated string
    from a format string and arguments to the format string. Tuples in
    "args" are supposed to contain one not translated and one translated
    string.
    """
    return (s.format(*(tuple(a[0] if isinstance(a, types.TupleType) else a
                             for a in args))),
            L.bl_msgr(s).format(*(tuple(a[1] if isinstance(a, types.TupleType) else a
                                        for a in args))))


class BagHandler(object):
    """
    Common base class providing default values
    for public attributes and private methods.
    """

    bag = None
    #warning = "Do not use a BagHandler class. Use an instance."
    warning_eng, warning = \
                           _get_loc_tuple(L.MSGX("Do not use a BagHandler class. Use an instance."))
    def __init__(self):
        "Creates the class attributes **bag**, **warning** and **warning_eng**."
        # Sets the warning attributes and returns -1 if something fundamental
        # and is wrong else 0 is returned.

        self.warning = self.warning_eng = ""

        try:
            rave.module("studio_sno")
        except rave.RaveError, err:
            self._set_warning(L.MSGX('Ruleset problems: "{0}"'),
                              _get_loc_tuple(str(err)))
            return

        buf = Variable("")
        Cui.CuiGetLocalPlanPath(Cui.gpc_info, buf)
        if not buf.value:
            self._set_warning(L.MSGX("No plan loaded"))

    def _set_warning(self, w, *a):
        """
        See "_get_loc_tuple".
        """
        self.warning_eng, self.warning = _get_loc_tuple(w, *a)

    def has_warning(self):
        return self.warning_eng != ""

    def _win_common(self, area, warn, sel):
        """
        Method for all classes using a window as source
        @type area: int
        @param area: area to use as source
        @type warn: string
        @param warn: Rave expression defining the warning text.
        @type sel: string
        @param sel: Boolean Rave expression defining the filtering.
        """

        if Cui.CuiAreaExists({"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION},
                             Cui.gpc_info, area):
            self.warning = "Window does not exist"
            return

        win_buf = cuib.CuiBuffer(area, cuib.WindowScope)
        if win_buf.isEmpty():
            self.warning = "Window is empty"
            return

        win_bag = rave.buffer2context(win_buf).bag()
        self.warning = rave.eval(win_bag, warn)[0]
        self._buf = cpmb.CpmBuffer(win_buf, sel)

        if not self._buf.isEmpty():
            self.bag = rave.buffer2context(self._buf).bag()


class CurrentObject(BagHandler):
    """
    The current (where the mouse is) object in Studio.
    Mainly for dynamic reports.
    """
    def __init__(self, level=None, sel=None, strict_level_check=True):
        """
        @type level: str or rave.level (default is Level.atom()).
        @param level: level of the object in the bag.
        @type sel: str
        @param sel: boolean rave expression string with correct level taking
                    leg_identifier as argument.
        @type strict_level_check: bool
        @param strict_level_check:  If True you get an error if the current object is
                                    a chain and the requested object is "smaller".
                                    If False you get the first object in the chain.
        """
        if BagHandler.__init__(self):
            return

        mod = Variable(0)
        id = Variable("")

        try:
            Cui.CuiGetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, mod, id)

        except Cui.CancelException:
            self.warning = "No current object"
            return

        except StudioError:
            self.warning = "Error in detecting current object"
            return

        if id.value == "-1":
            self.warning = "Current object is a Rudob"
            return

        if level is None:
            level = rave.Level.atom()

        if strict_level_check:
            if level.__class__ != rave.Level:
                level = rave.level(level)
            if mod.value != Cui.LegMode and level != rave.Level.chain():
                mn = {Cui.CrrMode : "Chain",
                      Cui.CrewMode: "Roster"}.get(mod.value, "Unknown")
                self.warning = "Current object (%s) is larger than '%s'" % (mn,
                                                                            level.name(),)
                return

        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiWhichArea, "object")

        leg_id = rave.selected(rave.Level.atom()).bag().leg_identifier()
        obuf = cuib.CuiBuffer(Cui.CuiWhichArea, cuib.ObjectScope)
        if not sel:
            sel = "leg_identifier = %d"
        self._buf = cpmb.CpmBuffer(obuf, sel % leg_id)
        self.bag = self.bag = rave.buffer2context(self._buf).bag()


class CurrentLeg(CurrentObject):
    pass


class CurrentDuty(CurrentObject):
    """
    The current duty in Studio.
    """
    def __init__(self):
        CurrentObject.__init__(self, "levels.duty",
                               "studio_sno.%%legid_in_duty%%(%s)", True)


class CurrentTrip(CurrentObject):
    """
    The current trip in Studio.
    """
    def __init__(self):
        CurrentObject.__init__(self, "levels.trip",
                               "studio_sno.%%legid_in_trip%%(%s)", True)


class CurrentChain(CurrentObject):
    """
    The current chain in Studio.
    """
    def __init__(self):
        CurrentObject.__init__(self, rave.Level.chain(),
                               "studio_sno.%%legid_in_chain%%(%s)", False)


class WindowChains(BagHandler):
    """
    All chains in the specified window.
    """

    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """
        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         '""',
                         "true")


class MarkedTripsMain(BagHandler):
    """
    Fully marked trips in the main window.
    """

    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """

        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         "studio_sno.%marked_trips_warning_txt%",
                         "studio_sno.%trip_is_marked%")


class MarkedRostersMain(BagHandler):
    """
    Selected rosters in the main window.
    It is enough that one leg is selected to consider the
    roster as selected.
    """
    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """

        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         "studio_sno.%marked_main_rosters_warning_txt%",
                         "studio_sno.%roster_is_marked_main%")


class MarkedRostersLeft(BagHandler):
    """
    Roster selected in the left part of the window
    """
    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """

        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         "studio_sno.%marked_left_rosters_warning_txt%",
                         "studio_sno.%roster_is_marked_left%")


class MarkedDutiesMain(BagHandler):
    """
    Marked duties.
    """
    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """

        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         "studio_sno.%marked_duties_warning_txt%",
                         "studio_sno.%duty_is_marked%")


class MarkedLegsMain(BagHandler):
    """
    Marked legs. Needed if you are not sure any leg is selected.
    """
    def __init__(self, area=cuib.CuiWhichArea):
        """
        @type area: int
        @param area: area to use a source
        """

        if BagHandler.__init__(self):
            return

        self._win_common(area,
                         "studio_sno.%marked_legs_warning_txt%",
                         "studio_sno.%leg_is_marked%")


class MarkedRosterMainRefPlan(MarkedRostersMain):
    """
    All rosters in the reference plan selected in
    the main window.
    """
    def __init__(self, area=cuib.CuiWhichArea, ref_plan=cpmb.REF_PLAN_1):
        """
        @type area: int
        @param area: area to use a source
        @type ref_plan: int
        @param ref_plan: cpmb.REF_PLAN_1 or cpmb.REF_PLAN_2
        """

        MarkedRostersMain.__init__(self, area)
        if not self.bag:
            return

        rpn = get_ref_plan_number(ref_plan)

        buf_ref = cpmb.CpmBuffer(ref_plan)
        if buf_ref.isEmpty():
            self.warning = "Reference plan %s is not loaded" % rpn
            self.bag = None
            return

        buf_ref_crew = cpmb.CpmBuffer(buf_ref, "not void(crr_crew_id)")

        id_expr = " or ".join(['crr_crew_id = "%s"' % chain_bag.crr_crew_id()
                               for chain_bag
                               in self.bag.chain_set()])

        self._buf = cpmb.CpmBuffer(buf_ref_crew, id_expr)
        self.bag = rave.buffer2context(self._buf).bag()


class PlanTrips(BagHandler):
    """
    All trips in the sub plan. (Not trips which are part of Roster).
    """
    ALWAYS_INCLUDE_ZERO_CREW = 1
    NEVER_INCLUDE_ZERO_CREW = 2
    INCLUDE_ZERO_CREW_DEPENDING_ON_FILTER = 3

    def __init__(self, include_base_variants=False, include_hidden=True, include_zero_crew=1):
        """
        @type include_base_variants: bool
        @param include_base_variants: Include base variants of the trips.
        @type include_hidden: bool
        @param include_hidden: Include hidden trips.
        @type include_zero_crew: int
        @param include_zero_crew: 1 - Always
                                  2 - Never
                                  3 - Consider Trip filter in sub plan.
        """
        if BagHandler.__init__(self):
            return

        sp_buf = cpmb.CpmBuffer(cpmb.SUB_PLAN)
        if sp_buf.isEmpty():
            self.warning = "There is no sub plan loaded or it is empty"
            return

        self._buf = cpmb.CpmBuffer(sp_buf, "is_crr")
        if self._buf.isEmpty():
            self.warning = "There are no trips in the loaded sub plan"
            return

        if not include_base_variants:
            self._buf = cpmb.CpmBuffer(self._buf, "crr_is_main_variant")

        if not include_hidden:
            self._buf = cpmb.CpmBuffer(self._buf, "not hidden")
            if self._buf.isEmpty():
                self.warning = "All trips in the loaded sub plan are hidden"
                return

        if include_zero_crew == 3:
            buf = Variable(0)
            Cui.CuiGetSubPlanCrewFilterCrr(Cui.gpc_info, buf)
            if buf.value:
                include_zero_crew = 2

        if include_zero_crew == 2:
            self._buf = cpmb.CpmBuffer(self._buf, "studio_sno.%crew_on_trip_slice_not_zero%")
            if self._buf.isEmpty():
                self.warning = "All trips have been filtered away."
                return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanRosters(BagHandler):
    """
    All Rosters in the sub plan.
    """
    def __init__(self):

        if BagHandler.__init__(self):
            return

        sp_buf = cpmb.CpmBuffer(cpmb.SUB_PLAN)
        if sp_buf.isEmpty():
            self.warning = "There is no sub plan loaded or it is empty"
            return

        self._buf = cpmb.CpmBuffer(sp_buf, "not void(crr_crew_id)")
        if self._buf.isEmpty():
            self.warning = "There are no rosters in the loaded sub plan"
            return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanCrewChains(BagHandler):
    """
    All Rosters, Trips and Duty-chains in the sub plan.
    (Variants of base-variant-trips excluded.)
    """
    def __init__(self):

        if BagHandler.__init__(self):
            return

        sp_buf = cpmb.CpmBuffer(cpmb.SUB_PLAN)
        if sp_buf.isEmpty():
            self.warning = "There is no sub plan loaded or it is empty"
            return

        rave_exp = "not is_free_leg and default(crr_is_main_variant, true)"
        self._buf = cpmb.CpmBuffer(sp_buf, rave_exp)

        if self._buf.isEmpty():
            self.warning = "There are no crew chains in the loaded sub plan"
            return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanFreeLegs(BagHandler):
    """
    All legs in the sub-plan you can see in the Leg window
    (if the crew filter is switched off)
    Identical with the rave context sp_free_legs.
    """

    def __init__(self):
        if BagHandler.__init__(self):
            return

        sp_buf = cpmb.CpmBuffer(cpmb.SUB_PLAN)
        if sp_buf.isEmpty():
            self.warning = "There is no sub plan loaded or it is empty"
            return

        self._buf = cpmb.CpmBuffer(sp_buf, "is_free_leg")

        if self._buf.isEmpty():
            self.warning = "There are no free legs in the loaded sub plan"
            return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanRotations(BagHandler):
    """
    All rotations in the local plan.
    """
    def __init__(self):

        if BagHandler.__init__(self):
            return

        self._buf = cpmb.CpmBuffer(cpmb.LOCAL_PLAN_CARC)
        if self._buf.isEmpty():
            self.warning = "There are are no rotations in the local plan"
            return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanLegSets(BagHandler):
    """
    All leg sets in the local plan.
    """
    def __init__(self):

        if BagHandler.__init__(self):
            return

        self._buf = cpmb.CpmBuffer(cpmb.LOCAL_PLAN_CFC)
        if self._buf.isEmpty():
            self.warning = "The local plan is empty"
            return

        self.bag = rave.buffer2context(self._buf).bag()


class PlanRostersRefPlan(BagHandler):
    """
    All rosters in the reference plan.
    """
    def __init__(self, ref_plan=cpmb.REF_PLAN_1):
        """
        @type ref_plan: int
        @param ref_plan: cpmb.REF_PLAN_1 or cpmb.REF_PLAN_2
        """
        if BagHandler.__init__(self):
            return

        ref_plan_number = get_ref_plan_number(ref_plan)

        ref_buf = cpmb.CpmBuffer(ref_plan)
        if ref_buf.isEmpty():
            self.warning = "Reference plan %s is not loaded" % ref_plan_number
            return

        self._buf = cpmb.CpmBuffer(ref_buf, "not void(crr_crew_id)")
        if self._buf.isEmpty():
            self.warning = "There are no rosters in reference plan %s" % ref_plan_number
            return

        self.bag = rave.buffer2context(self._buf).bag()


if __name__ == "__main__":

    "Self testing"

    for case in (CurrentLeg, CurrentDuty, CurrentTrip, CurrentChain,
                 MarkedTripsMain, MarkedRostersMain, MarkedRosterMainRefPlan,
                 MarkedRostersLeft, MarkedDutiesMain, MarkedLegsMain,
                 WindowChains,
                 (WindowChains, (cuib.CuiArea0,)),
                 (WindowChains, (cuib.CuiArea3,)),
                 PlanRosters, PlanTrips, (PlanTrips, (True,)), (PlanTrips, (False, False, 1)),
                 PlanCrewChains, PlanFreeLegs, PlanRotations, PlanLegSets,
                 PlanRostersRefPlan):

        try:
            tbhclass = case[0]
            args = case[1]
        except TypeError:
            tbhclass = case
            args = ()

        tbh = tbhclass(*args)

        print "%-30s %6s %6s %6s %6s '%s'" % ("%s%s" % (tbh.__class__.__name__, args),
                                              tbh.bag and tbh.bag.gpc_iterators.num_chains_in_bag(),
                                              tbh.bag and tbh.bag.gpc_iterators.num_trips_in_bag(),
                                              tbh.bag and tbh.bag.gpc_iterators.num_duties_in_bag(),
                                              tbh.bag and tbh.bag.gpc_iterators.num_legs_in_bag(),
                                              tbh.warning)


