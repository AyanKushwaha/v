import os

import Cui

from behave import use_step_matcher
from Variable import Variable

import util
import rave_util

use_step_matcher('re')


#
# Load plans
#
@given(u'I load the plan "(?P<plan_path>.*)"')
def open_subplan(context, plan_path):
    """
    Given I load the plan "Jeppesen/2012Apr/FC_737_WEEKLY/ex_optimization"
    """
    plan_path = util.verify_plan_path(plan_path)
    plan_dirs = plan_path.split('/')

    localplan_dir = os.path.join(plan_dirs[0],plan_dirs[1],plan_dirs[2])
    context.lp_dir = localplan_dir
    subplan_dir = len(plan_dirs) >3 and os.path.join(localplan_dir, plan_dirs[3]) or None
    context.sp_dir = subplan_dir
    solution_dir = len(plan_dirs) == 5 and plan_dirs[4] or None
    context.sol_dir = solution_dir

    #print('Local Plan: ', localplan_dir)
    #print('Subplan: ', subplan_dir)
    #print('Solution: ', solution_dir)

    if solution_dir:
        # Open a solution
        Cui.CuiLoadSolution(Cui.gpc_info, localplan_dir, subplan_dir, solution_dir)
    elif subplan_dir:
        # Open a subplan
        Cui.CuiOpenSubPlan(Cui.gpc_info, localplan_dir, subplan_dir, Cui.CUI_SILENT)
    else:
        # Open a local plan
        Cui.CuiOpenLocalPlan(Cui.gpc_info, localplan_dir, Cui.CUI_SILENT)


#
# work with windows
#
#TODO: Ad to example test case
@given(u'window %(window_ix)s is active' % util.matching_patterns)
def set_current_area(context, window_ix):
    """
    Given window 1 is active
    """
    _set_current_area(context, window_ix)

def _set_current_area(context, window_ix):
    window_area = util.verify_window_ix_to_area(window_ix)
    context.window_area = window_area
    Cui.CuiSetCurrentArea(Cui.gpc_info, window_area)

@when(u'I toggle the "(?P<leg_trip>leg|trip)" filter "(?P<on_off>on|off)"')
def toggle_object_filter(context, leg_trip, on_off):
    """
    When I toggle the "leg" filter "off"
    """
    toggle_value = on_off.encode().lower() == 'on' and 1 or 0
    if leg_trip.encode().lower() == 'leg':
        Cui.CuiSetSubPlanCrewFilterLeg(Cui.gpc_info, toggle_value)
    else:
        Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, toggle_value)

@when(u'I show "%(window_mode)s" in window %(window_ix)s' % util.matching_patterns)
def display_objects_in_win(context, window_mode, window_ix=None):
    """
    When I show "trips" in window 1
    """
    if window_ix:
        _set_current_area(context, window_ix)

    _, cui_mode = util.verify_window_mode(window_mode)
    Cui.CuiDisplayObjects(Cui.gpc_info, context.window_area, cui_mode, Cui.CuiShowAll)

#
# Filter in Gantt
#

@when(u'I filter "%(window_mode)s" where homebase is "%(stn)s" in window %(window_ix)s' % util.matching_patterns)
def filter_objects_homebase_in_win(context, window_mode, stn, window_ix=None):
    """
    When I filter "trips" where homebase is "GOT" in window 1
    """
    window_mode = util.verify_window_mode(window_mode)
    homebase = util.verify_stn(stn)
    if window_ix:
        window_ix = util.verify_int(window_ix)
        _set_current_area(context, window_ix)

    fn = "Behave_filter_objects_homebase"
    byp = [("FORM", fn),
           ("DEFAULT", ""),
           ("FC_CRR_HOMEBASE", "%s" % homebase)]
    if window_mode == 'legs':
        filter_mode = 'LegFilter'
    elif window_mode == 'duties':
        filter_mode = 'DutyFilter' # Could be RtdFilter ?
    else:
        filter_mode = 'CrrFilter'
    try:
        Cui.CuiFilterObjects(byp, Cui.gpc_info, context.window_area, filter_mode, fn)
    except Cui.CancelException:
        assert False, 'Could not filter objects, unknown error'

@when(u'I filter "%(window_mode)s" where rave "%(rave_name)s" is "%(rave_value)s" in window %(window_ix)s' % util.matching_patterns)
def filter_objects_rave_value_in_win(context, window_mode, rave_name, rave_value, window_ix=None):
    """
    When I filter "trips" where rave "leg.%connection_time%" is "0:46" in window 1
    """
    (window_mode, window_id) = util.verify_window_mode(window_mode)
    rave_name = util.verify_rave_name(rave_name)
    rave_value = util.verify_rave_value(rave_value)
    if window_ix:
        window_ix = util.verify_int(window_ix)
        _set_current_area(context, window_ix)

    fn = "Behave_filter_%s_rave" % window_mode
    byp = [("FORM", fn),
           ("DEFAULT", ""),
           ('CRC_VARIABLE_0', '%s' % rave_name),
           ('CRC_VALUE_0', '%s' % rave_value)]
    if window_mode == 'legs':
        filter_mode = 'LegFilter'
    elif window_mode == 'duties':
        filter_mode = 'DutyFilter' # Could be RtdFilter ?
    elif window_mode == 'trips':
        filter_mode = 'CrrFilter'
    else:
        assert False, 'Cannot handle window mode %s, use "legs" or "trips"' % window_mode
        
    try:
        Cui.CuiFilterObjects(byp, Cui.gpc_info, context.window_area, filter_mode, fn)
    except Cui.CancelException:
        assert False, 'Could not filter objects, review the rave expression %s / %s' % (rave_name, rave_value)
    

#
# Select in Gantt
#

@when(u'I select leg %(leg_ix)s' % util.matching_patterns)
def select_leg(context, leg_ix):
    """
    When I select leg 1
    """
    select_leg_trip_roster(leg_ix, 1, 0)

@when(u'I select trip %(trip_ix)s' % util.matching_patterns)
def select_trip(context, trip_ix):
    """
    When I select trip 1
    """
    trip_ix = util.verify_int(trip_ix)
    crr_id = str(rave_util.eval_rave('crr_identifier', 1, trip_ix, 0))

    Cui.CuiSetSelectionObject(Cui.gpc_info, 0, Cui.CrrMode, crr_id)
    Cui.CuiMarkCrrs(Cui.gpc_info, 0, "object")

def select_leg_trip_roster(leg_ix, trip_ix, roster_ix):
    leg_ix = util.verify_int(leg_ix)
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    
    leg_ids = []
    rave_name = 'leg_identifier'
    leg_id = str(rave_util.eval_rave(rave_name, leg_ix, trip_ix, roster_ix))
    leg_ids.append(leg_id)

    Cui.CuiMarkLegList(Cui.gpc_info, leg_ids)

@when(u'I select "%(window_mode)s" where rave "%(rave_name)s" is "%(rave_value)s"' % util.matching_patterns)
def select_objects_rave_value(context, window_mode, rave_name, rave_value):
    """
    When I select "trips" where rave "leg.%connection_time%" is "0:46"
    """
    _select_objects_rave_value_in_win(context, window_mode, rave_name, rave_value)

# TODO: add example test
@when(u'I select "%(window_mode)s" where rave "%(rave_name)s" is "%(rave_value)s" in window %(window_ix)s' % util.matching_patterns)
def select_objects_rave_value_in_win(context, window_mode, rave_name, rave_value, window_ix):
    """
    When I select "leg sets" where rave "leg.%start_utc%" is "6jul2003 10:00" in window 1
    """
    _select_objects_rave_value_in_win(context, window_mode, rave_name, rave_value, window_ix)


def _select_objects_rave_value_in_win(context, window_mode, rave_name, rave_value, window_ix=None):
    (window_mode, window_id) = util.verify_window_mode(window_mode)
    rave_name = util.verify_rave_name(rave_name)
    rave_value = util.verify_rave_value(rave_value)
    if window_ix:
        window_ix = util.verify_int(window_ix)
        _set_current_area(context, window_ix)

    fn = "Behave_select_%s_rave" % window_mode
    byp = [("FORM", fn),
           ("DEFAULT", ""),
           ('CRC_VARIABLE_0', '%s' % rave_name),
           ('CRC_VALUE_0', '%s' % rave_value)]

    if window_mode == 'leg sets':
        byp.append(("FILTER_MARK", "LEG"))
    elif window_mode == 'legs':
        byp.append(("FILTER_MARK", "LEG"))
    elif window_mode == 'duties':
        byp.append(("FILTER_MARK", "Duty"))
    else:
        byp.append(("FILTER_MARK", "Trip"))

    try:
        print(byp)
        print('apa bepa')
        Cui.CuiMarkWithFilter(byp, Cui.gpc_info, context.window_area, 0,fn,0)
    except Cui.CancelException:
        assert False, 'Could not select objects, review the rave expression %s / %s' % (rave_name, rave_value)
    


@then(u'there shall be 1 row')
def verify_displayed_row(context):
    """
    Then there shall be 1 row
    """
    _verify_displayed_rows(context, 1)

@then(u'there shall be %(total)s rows' % util.matching_patterns)
def verify_displayed_rows(context, total):
    """
    Then there shall be 8 rows
    """
    _verify_displayed_rows(context, total)

def _verify_displayed_rows(context, total):
    total = util.verify_int(total)
    try:
        area = context.window_area
    except:
        area = Cui.CuiArea0  # Assume window 1

    buf = Variable("", 1024)
    Cui.CuiGetAreaModeString(Cui.gpc_info, area, buf)
    buf_s = str(buf).lower()
    rows = Cui.CuiGetNumberOfChains(Cui.gpc_info, area)

    assert rows == total, 'Found %i(%i) %s' % (rows, total, buf_s)

@then(u'there shall be 1 selected "%(window_mode)s"' % util.matching_patterns)
def verify_selected_object(context, window_mode):
    """
    Then there shall be 1 selected "trip"
    """
    _verify_selected_objects(context, window_mode, 1)

@then(u'there shall be %(total)s selected "%(window_mode)s"' % util.matching_patterns)
def verify_selected_objects(context, total, window_mode):
    """
    Then there shall be 2 selected "leg sets"
    """
    _verify_selected_objects(context, window_mode, total)

def _verify_selected_objects(context, window_mode, total):
    window_mode, window_id = util.verify_window_mode(window_mode)
    total = util.verify_int(total)
    if window_mode in ('leg', 'legs', 'leg set', 'leg sets'):
        selected = rave_util.num_selected_legs()
    elif window_mode in ('trip', 'trips'):
        selected = rave_util.num_selected_trips()
    else:
        assert False, 'Cannot select from %s window, use legs or trips' % window_mode
    assert selected == total, 'Found %i(%i) selcted %s' % (selected, total, window_mode)


#
# Core menu functions
#

@when(u'I Split after')
def split_crrs(context):
    """
    When I Split after
    """
    Cui.CuiSplitChainObjects(Cui.gpc_info, Cui.CuiWhichArea, "Marked", 0, 0)
    
@when(u'I Change to/from Deadhead')
def change_to_from_deadhead(context):
    """
    When I Change to/from Deadhead 
    """
    Cui.CuiChangeToFromPassiveDnD(Cui.gpc_info, Cui.CuiWhichArea, "MARKED",
                                  Cui.CUI_CHANGE_TO_FROM_SILENT |
                                  Cui.CUI_CHANGE_TO_FROM_FORCE)

@when(u'I Slice Completely')
def slice_completely(context):
    """
    When I Slice Completely
    """
    Cui.CuiSliceMax(Cui.gpc_info, "CRR", "Marked")
