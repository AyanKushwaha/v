# Custom extension to the studio module

import Cui
from utils.rave import RaveIterator
import carmensystems.rave.api as rave
import carmensystems.studio.cpmbuffer as cpmb
import carmensystems.studio.cuibuffer as cuib

from behave import use_step_matcher

import util

use_step_matcher('re')


@when(u'I reschedule personal activity %(leg_ix)s of crew member %(roster_ix)s to start at %(date)s %(time)s and end at %(date2)s %(time2)s' % util.matching_patterns)
def reschedule_personal_activity(context, leg_ix, roster_ix, date, time, date2, time2):
    """
    When I reschedule personal activity 1 of crew member 1 to start at 25Feb2019 11:20 and end at 25Feb2019 21:20
    """
    assert context.ctf.roster_was_published(), \
        ('Can not reschedule items when working with unpublished data. '
        'Use the step "Given the roster is published" to emulate the publish process.')

    time = time.replace(":","")
    time2 = time2.replace(":","")
    roster_ix = util.verify_int(roster_ix)
    leg_ix = util.verify_int(leg_ix)
    type = 'leg.%is_pact%'

    identify_activity(context, type, leg_ix, roster_ix)
    # Silently call and populate the Personal Activity Properties dialog
    Cui.CuiUpdateTaskLeg(
        # Ensure that we update using utc
        {'FORM':'TASK_LEG','FL_TIME_BASE': 'UDOP'},
        {'FORM':'TASK_LEG','START_DATE': date},
        {'FORM':'TASK_LEG','END_DATE': date2},
        {'FORM':'TASK_LEG','DEPARTURE_TIME': time},
        {'FORM':'TASK_LEG','ARRIVAL_TIME': time2},
        Cui.gpc_info,
        context.window_area,
        "object",
        # Suppress any actual studio gui, ensure the operation is not blocked by rules
        Cui.CUI_UPDATE_TASK_RECALC_TRIP |\
        Cui.CUI_UPDATE_TASK_SILENT |\
        Cui.CUI_UPDATE_TASK_NO_LEGALITY_CHECK |\
        Cui.CUI_UPDATE_TASK_TASKTAB
    )


@when(u'I reschedule leg %(leg_ix)s of crew member %(roster_ix)s flight %(flight_id)s to depart from %(dep_apt)s %(date)s %(time)s and arrive at %(arr_apt)s %(date2)s %(time2)s' % util.matching_patterns)
def reschedule_leg(context, leg_ix, roster_ix, flight_id, dep_apt, date, time, arr_apt, date2, time2):
    """
    When I reschedule leg 1 of crew member 1 flight 101 from ARN to CPH of SKD to start at 08MAR2020 07:00 and
    end at 08MAR2020 08:10
    """
    assert context.ctf.roster_was_published(), \
        ('Can not reschedule items when working with unpublished data. '
        'Use the step "Given the roster is published" to emulate the publish process.')

    roster_ix = util.verify_int(roster_ix)
    leg_ix = util.verify_int(leg_ix)
    flight_id = util.verify_int(flight_id)
    dep_apt, arr_apt = util.verify_stn(dep_apt), util.verify_stn(arr_apt)
    date, date2 = util.verify_date(date), util.verify_date(date2)
    time, time2 = util.verify_time(time), util.verify_time(time2)
    eobt = date + ' ' + time
    eibt = date2 + ' ' + time2

    type = 'leg.%is_on_duty%'
    identify_activity(context, type, leg_ix, roster_ix)

    Cui.CuiLegSetProperties(
        {'FORM': 'DUMMY_FLIGHT', 'FL_TIME_BASE': 'UDOP'},
        {'FORM': 'DUMMY_FLIGHT', 'FLIGHT_ID': 'SK'+str(flight_id)},
        {'FORM': 'DUMMY_FLIGHT', 'DEPARTURE_AIRPORT': dep_apt},
        {'FORM': 'DUMMY_FLIGHT', 'ARRIVAL_AIRPORT': arr_apt},
        {'FORM': 'DUMMY_FLIGHT', 'eobt': eobt},
        {'FORM': 'DUMMY_FLIGHT', 'eibt': eibt},
        Cui.gpc_info,
        context.window_area,
        "object"
    )


def identify_activity(context, type, leg_ix, roster_ix):
    # Grab a context of the current window in area 0
    # This could be improved, currently requires the pact to be loaded in area 0
    cui_buf = cuib.CuiBuffer(0, cuib.WindowScope)
    cpm_buf = cpmb.CpmBuffer(cui_buf, 'true')
    window_context = rave.buffer2context(cpm_buf)

    # Create an iterator to filter activities for the specified crew
    crew_id = context.ctf.make_crew_id(roster_ix)
    result = RaveIterator(
        rave.iter('iterators.leg_set',
            where = ('crew.%%id%% = "%s"' % crew_id, type)),
        {'leg_id': 'leg_identifier'}
    ).eval(window_context)

    # If the activity was not found, notify the tester
    assert leg_ix <= len(result), \
        'Could not find activity %s for crew member %s.' % (leg_ix, roster_ix) \
        + 'Check if your index is out of bounds, and that the activity is loaded in window 1'

    # Get the identifier for the activity we're rescheduling
    leg_id = result[leg_ix - 1].leg_id

    # Select the activity in studio
    Cui.CuiSetSelectionObject(Cui.gpc_info, context.window_area, Cui.LegMode, str(leg_id))
