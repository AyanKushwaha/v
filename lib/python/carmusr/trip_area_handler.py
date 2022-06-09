#####

##
#####
__version__ = "$Revision$"

"""
File for editing the area attribute on trip
@date: 26May2008
@author: Per Groenberg
@org: Jeppesen systems AB
"""
import Cui
import Gui
import Variable
import Cfh
import AbsDate
import AbsTime
import RelTime
import tempfile
import os
import carmusr.HelperFunctions as HF
import utils.CfhFormClasses as CFC
import tm
import Errlog
from modelserver import EntityNotFoundError
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions


MIX_WARN = 'MIX'


class TripAreaForm(CFC.BasicCfhForm):
    """ Edit the area attribute of selected trip
    """
    def __init__(self, start_planning_group, *args):
        CFC.BasicCfhForm.__init__(self, *args)
        self._delta_y = 8
        planning_groups = ["SKD", "SKI", "SKJ", "SKK", "SKN", "SKS", "SVS", "NONE"]
        self.add_label(0, 1, 'header', 'Please select area', style=Cfh.CfhSLabelNormal)
        self.add_filter_combo(2, 1, "planning_group", "Planning Group", start_planning_group or "NONE", planning_groups)

    @property
    def planning_group(self):
        return self.planning_group_field.valof()


def _update_for_trip(crr_id, new_trip_area, cui_area):
    """
    updates area for single trip
    """
    try:
        # For lookup in model, get tablekey from keywords
        trip = HF.TripObject(str(crr_id), cui_area)
        trip_uuid, =  trip.eval("trip.%uuid%")
        trip_startdate, = trip.eval("trip.%udor%")  # UDOR is absdate int
        if not trip_uuid or not trip_startdate:
            Errlog.log("trip_area_handler.py:: Trip's keyword uuid or udor is VOID, " +
                       "unable to continue action")
            return
        trip_startdate = AbsTime.AbsTime(1440 * trip_startdate)  # UDOR is absdate int
        trip_key = (trip_startdate, trip_uuid)
        try:
            trip_entity = tm.TM.trip[(trip_startdate, trip_uuid)]  # get trip from trip table
        except EntityNotFoundError, err:  # Create if not found, only an issue in tracking
            trip = _create_new_trip(trip, crr_id)
            trip_uuid, =  trip.eval("trip.%uuid%")
            trip_entity = tm.TM.trip[(trip_startdate, trip_uuid)]  # Get new database entity
        if new_trip_area.upper() == 'NONE':  # Reset area
            trip_entity.area = None
        else:
            trip_maincat = _warn_mixed_maincats(trip)
            if (trip_maincat != MIX_WARN):
                # Area e.g. in format F+SKN
                trip_entity.area = tm.TM.area_set[(trip_maincat + new_trip_area,)]
            else:
                return

    except Exception, err:
        Errlog.log("trip_area_handler.py:: Exception: %s" % err)


def _create_new_trip(old_trip, old_crr_id):
    #Get crew positions
    pos_vector = [old_trip.eval("crew_pos.%%trip_assigned_pos%%(%d)" % (ix + 1))[0] for ix in xrange(12)]
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                               Cui.CrrMode, Cui.CrrMode, [str(old_crr_id)])
    Cui.CuiMarkCrrs(Cui.gpc_info, Cui.CuiScriptBuffer, "object", Cui.CUI_MARK_SET)
    new_trip_id = Variable.Variable(0)
    Cui.CuiCreateTrip(Cui.gpc_info, Cui.CuiScriptBuffer,
                      "window", pos_vector, new_trip_id, 0)  # Create new
    Cui.CuiRemoveMarkedCrrs(Cui.gpc_info, Cui.CuiScriptBuffer, 3, 0)  # remove old
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    trip = HF.TripObject(str(new_trip_id.value), Cui.CuiScriptBuffer)  # Fetch new trip
    return trip


def _warn_mixed_maincats(trip):
    trip_has_fc, = trip.eval('planning_area.%fc_trip%')  # F or C
    trip_has_cc, = trip.eval('planning_area.%cc_trip%')  # F or C
    if trip_has_fc and trip_has_cc:
        cfhExtensions.show("In setting trip area:\nCould not set area attribute" +
                           " for trip with mixed\nmain categories!")
        return MIX_WARN
    elif trip_has_fc:
        return 'F'
    elif trip_has_cc:
        return 'C'
    else:
        # The trip has no positions in either flight deck or cabin
        cfhExtensions.show("In setting trip area:\nCould not set area attribute" +
                           " for trips without main category")
        return MIX_WARN


def set_area(mode, planning_group=None, cui_area=None):
    """
    Mode is WINDOW, MARKED or TRIP
    """
    Errlog.log("trip_area_handler.py:: Update trip area")
    if not HF.isDBPlan():
        Errlog.log("trip_area_handler.py:: Only in database plan")
        cfhExtensions.show("Only in database plan")
        return
    # Sync if any open-time trips are recently created
    Cui.CuiSyncModels(Cui.gpc_info)

    # Get current area
    if cui_area is None:
        cui_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # Get current trip(s)
    crr_ids = []
    if mode.upper() == 'TRIP':
        crr_id = Cui.CuiCrcEvalInt(Cui.gpc_info, cui_area, "object", "crr_identifier")
        trip = HF.TripObject(str(crr_id), cui_area)
        if _warn_mixed_maincats(trip) == MIX_WARN:
            return
        current_planning_group, = trip.eval("trip.%area_planning_group%")
        if planning_group is None:
            form = TripAreaForm(current_planning_group, "Trip area")
            try:
                form()
                planning_group = form.planning_group
            except CFC.CancelFormError, ef:
                Errlog.log("trip_area_handler.py:: User canceled operation")
                return -1
        crr_ids.append((crr_id, planning_group))

    elif mode.upper() in ('MARKED', 'WINDOW'):
        if planning_group is None:
            try:
                current_cat = R.param('planning_area.planning_area_trip_category_p').value()
                any_cat, = R.eval('planning_area.ANY_CAT')
                if current_cat == any_cat:
                    message = 'Not possible to set trip areas' + \
                              ' when planning area category is set to ANY'
                    Errlog.log('trip_area_handler.py::set_area: %s' % message)
                    Gui.GuiMessage(message)
                    return 1
                select = R.param('planning_area.planning_area_trip_planning_group_p').value()
                any_planning_group, =  R.eval('planning_area.ANY_PG')
                if select == any_planning_group:
                    select = 'NONE'
                else:
                    select, = R.eval('planning_area.%%enum_crew_planning_group_string%%(%s)' % select) or 'NONE'
            except:
                # tracking hasn't CAT nor PLANNING_GROUP enums in ruleset
                select = 'NONE'
            form = TripAreaForm(select, "Trip area")
            try:
                form()
                planning_group = form.planning_group
            except CFC.CancelFormError, ef:
                Errlog.log("trip_area_handler.py:: User canceled operation")
                return -1
        trip_ids = Cui.CuiGetTrips(Cui.gpc_info, cui_area, mode)
        for trip in trip_ids:
            crr_ids.append((trip, planning_group))
    else:
        Errlog.log("trip_area_handler.py:: Not implemented mode %s" % mode)
        return

    # Do the actual update
    for (crr_id, new_trip_area) in crr_ids:
        _update_for_trip(crr_id, new_trip_area, cui_area)

    Cui.CuiReloadTable('trip')
    Cui.CuiReloadTable('trip_flight_duty')
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    HF.redrawArea(cui_area)
    Cui.CuiSortArea(Cui.gpc_info, cui_area, Cui.CuiSortDefault)
