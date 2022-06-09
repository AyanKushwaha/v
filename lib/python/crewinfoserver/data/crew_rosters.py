#!/usr/bin/env python
# coding: utf-8
"""

 Builds Crew Roster data objects...

"""
# Python imports
from datetime import datetime
from pprint import pformat, pprint
from copy import copy

# External CARMUSR imports
import carmensystems.rave.api as rave
from utils.selctx import SingleCrewFilter, BasicContext
import utils.xmlutil as xml
import Cui
from dig.DigJobQueue import DigJobQueue
from RelTime import RelTime
import carmusr.modcrew as mods

# Crew Info Server imports
import crewinfoserver.common.util as util
import crewinfoserver.server.api_handler as api
import crewinfoserver.data.data_handler as dh


# CONSTANTS
ROSTER_CHUNK_SIZE = 50
DELAY = 5.0
DEFAULT_DURATION = "PT0H0M"


def push_rosters(roster):
    return dh.make_http_push(roster, api.post_roster, ROSTER_CHUNK_SIZE, DELAY)


def push_all_rosters():
    """
    Pushes all rosters.
    """
    push_specific_roster(None)


def push_specific_roster(crew_ids):
    """
    Builds and pushes the roster for specific crew
    :param crew_ids: List of crew whose roster are to be pushed
    :return:
    """
    start = datetime.now()

    roster_objects = build_rosters(crew_ids)
    count, _ = push_rosters(roster_objects)

    elapsed = datetime.now() - start
    print("Time elapsed pushing %s roster: %s" % (count, elapsed))

    return count, str(elapsed)


def push_visible_crews_roster():
    """
    Called from RosterServer menu (crewinfoserver.menues.py)
    """
    visible_crew = dh.get_visible_crew()
    push_specific_roster(visible_crew)


def prepare_crewroster_messages(crew_ids):
    """
    Prepares the crewroster messages to be put on the message queue

    :param crew_ids: the IDs of crew who are to be updated
    :return: count: nr of crews being part of all messages being created
    :return: messages: a list of all messages to be put on the queue

    """
    roster_objects = build_rosters(crew_ids)
    count, messages = dh.structure_messages(roster_objects, "crewrosters", ROSTER_CHUNK_SIZE)
    return count, messages


def build_rosters(crew_ids=None):
    """

    :param crew_ids:
    :return: list of crew rosters
    """
    start = datetime.now()
    crew_ids = util.start_build("rosters", crew_ids)

    roster_objects = list()
    for s, e in util.calculate_pushable_roster_months():
        trip_filter = 'rosterserver.%%trip_matches_month%%(%s, %s)' % (s, e)
        released_until = rave.eval("rosterserver.%%released_until%%(%s)" % s)[0][:19]
        if crew_ids is None:
            roster_objects.extend(build_all_rosters(trip_filter, released_until))
        else:
            for crew_id in crew_ids:
                roster_objects.append(build_single_crew_roster(crew_id, trip_filter, released_until))

    util.end_build("rosters", crew_ids, start)

    # Happens if crew doesn't have any employment
    if not roster_objects[0]:
        raise Exception("Failed to build rosters for crew %s" % str(crew_ids))

    return roster_objects


def build_all_rosters(trip_filter, released_until):
    """
    Builds a roster object for every crew in the 'sp_crew' context.
    :param trip_filter: used to filter trips based on planning period start/end
    :param released_until: 00:00 first of next month
    :return: List of roster objects, one roster object = the roster for one crew
    """
    roster_objects = list()

    update_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    for roster_bag in rave.context(BasicContext().getGenericContext()).bag().chain_set(where="rosterserver.%has_employment%"):
        activities, fdps = build_activities(roster_bag, trip_filter)
        roster_objects.append(dict(empno=roster_bag.rosterserver.empno(),
                                   last_update=update_time,
                                   crew_roster={
                                       'roster_released_until': released_until,
                                       'crew_activities': activities,
                                       'fdps': fdps
                                        },
                                ))
    
    return roster_objects


def build_single_crew_roster(crew_id, trip_filter, released_until):
    """
    Builds a JSON object for one crew for the period of one month, month specified by :param trip_search_string.

    :param crew_id: the ID of 1 crew
    :param trip_filter: used to filter trips based on planning period start/end
    :param released_until: 00:00 first of next month
    :return: a JSON structure roster object for one crew
    """
    roster_object = dict()
    update_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    for roster_bag in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
        activities, fdps = build_activities(roster_bag, trip_filter)
        roster_object = dict(empno=roster_bag.rosterserver.empno(),
                             last_update=update_time,
                             crew_roster={
                                'roster_released_until': released_until,
                                'crew_activities': activities,
                                'fdps': fdps
                                 },
                            )
    
    return roster_object


def build_activities(bag, trip_filter):
    """

    :param bag:  bag interface used for Rave communication
    :param trip_filter: used to filter trips based on planning period start/end
    :return: a list of activities
    """
    activities = []
    fdps = []

    for trip_bag in bag.iterators.leg_set(where=trip_filter):
        activity_id=trip_bag.rosterserver.activity_id()

        activity = dict(
            activity_id=activity_id,
            activity_type=trip_bag.rosterserver.activity_type()
        )

        if activity['activity_type'] == "F":
            ret = build_flight_activity(trip_bag)

            # Add meal activity if meal code is present for the flight.
            if not util.is_empty_meal_code(trip_bag.rosterserver.meal_code_excl_meal_break()):
                ret['crew_flight_activity']['pre_flight_meal'] = trip_bag.rosterserver.meal_code_excl_meal_break()

            activity.update(ret)
            activities.append(activity)

            # Add meal activity after flight leg if meal break code contains X or V.
            if (not util.is_empty_meal_code(trip_bag.rosterserver.meal_break_code()) and
                    ('X' in trip_bag.rosterserver.meal_break_code() or
                     'V' in trip_bag.rosterserver.meal_code())):
                ret['crew_flight_activity']['post_flight_meal'] = trip_bag.rosterserver.meal_break_code()
            
            date = trip_bag.rosterserver.leg_start()
            if trip_bag.rosterserver.prev_leg_is_prev_day(date):
                fdp = dict(
                    duty_start_date = trip_bag.rosterserver.duty_start_date(),
                    fdp = util.rel_time_to_str(trip_bag.rosterserver.fdp()),
                    max_fdp = util.rel_time_to_str(trip_bag.rosterserver.max_fdp()),
                    extended = util.bool_to_lower(trip_bag.rosterserver.is_extended())
                )
                fdps.append(fdp)

        else:
            ret = build_base_activities(trip_bag)

            # Multiple activities created for the trip, for example vacation spanning over multiple days.
            for idx, act in enumerate(ret):
                tmp_activity = copy(activity)
                tmp_activity['activity_id'] = activity_id + "+%d" % idx
                tmp_activity.update(act)
                activities.append(tmp_activity)
        


    return (activities, fdps)

def build_flight_activity(bag):
    """
    Builds a flight activity
    :param bag: bag interface used for Rave communication
    :return: a flight activity in JSON structure
    """
    stop_duration = xml.duration('stop_duration', bag.rosterserver.stop_duration_scheduled()).pop()

    flight_activity = dict()
    flight_activity['crew_flight_activity'] = dict(
        flight_id = (bag.rosterserver.flight_id()).rstrip(),
        duty_code = bag.rosterserver.duty_code(),
        origin_date = (bag.rosterserver.origin_date())[:10],
        check_in_time = bag.rosterserver.check_in_time(),
        check_out_time = bag.rosterserver.check_out_time(),
        checked_in = util.bool_to_lower(bag.rosterserver.checked_in()),
        dep_station = bag.rosterserver.dep_station(),
        arr_station = bag.rosterserver.arr_station(),
        std = bag.rosterserver.std_lt(),
        sta = bag.rosterserver.sta_lt(),
        aircraft = dict(
            ac_reg = bag.rosterserver.ac_reg(),
            ac_type = bag.rosterserver.ac_type()
        ),
        flight_leg_status = dict(
            etd = bag.rosterserver.etd_lt(),
            eta = bag.rosterserver.eta_lt(),
            atd = bag.rosterserver.atd_lt(),
            ata = bag.rosterserver.ata_lt()
        ),
        pilot_in_command = bag.rosterserver.pic(),
        flight_type = bag.rosterserver.type_of_flight(),
        flying_passive=util.bool_to_lower(bag.rosterserver.flying_passive()),
        crew_list_allowed=util.bool_to_lower(bag.rosterserver.crew_list_allowed()),
        stop_duration=stop_duration if (stop_duration is not "P0Y") else DEFAULT_DURATION,
        last_flown = bag.rosterserver.last_flown_date(),
        prev_activity = bag.rosterserver.prev_activity(),
        next_activity = bag.rosterserver.next_activity(),
        prev_duty = bag.rosterserver.prev_duty(),
        next_duty = bag.rosterserver.next_duty(),
        sort_key = bag.rosterserver.sort_key(),
        passport_nationality = bag.rosterserver.passport_nationality(),
        passport_no = bag.rosterserver.passport_no(),
        visa_no = bag.rosterserver.visa_no(),
        visa_expire_date = "" if not bag.rosterserver.visa_expire_date() else util.str2date(bag.rosterserver.visa_expire_date())
    )

    return flight_activity


def build_base_activities(bag):
    """
    Builds base activities.
    :param bag: bag interface used for Rave communication
    :return: a list of base activities in JSON structure
    """

    # If the activity covers more than one day, split it in to separate single day activities.
    activity_days = util.get_number_of_days_abs_time(bag.rosterserver.std_lt_abstime(),
                                                     bag.rosterserver.sta_lt_abstime())

    base_activities = list()
    start_day = bag.rosterserver.std_lt_abstime()
    show_times_and_stations = bag.rosterserver.task_code_not_in_base_act_set()

    for day_number in range(activity_days):
        # Special case for activities such as LA55, which has show_times_and_station as true.
        if activity_days > 1 and show_times_and_stations:
            sta = util.abs_time_to_str(start_day + RelTime(1, 0, 0), lex24=True)
        else:
            sta = bag.rosterserver.sta_lt() if show_times_and_stations else ''

        base_activity = dict()
        base_activity['crew_base_activity'] = dict(
            task_code=bag.rosterserver.leg_code(),
            duty_code = bag.rosterserver.duty_code(),
            std=util.abs_time_to_str(start_day),
            sta=sta
        )

        # Adds these values for certain ground activities, e.g. training but not on free days, vacations, etc.
        if show_times_and_stations:
            stop_duration = xml.duration('stop_duration', bag.rosterserver.stop_duration_scheduled()).pop()
            base_activity['crew_base_activity'].update(dict(
                dep_station=bag.rosterserver.dep_station(),
                arr_station=bag.rosterserver.arr_station(),
                stop_duration= stop_duration if (stop_duration is not "P0Y") else DEFAULT_DURATION,
                check_in_time = bag.rosterserver.check_in_time(),
                check_out_time = bag.rosterserver.check_out_time()
            ))

        # If activity is a simulator, surround the activity with briefing and debriefing activities.
        if bag.rosterserver.leg_is_simulator():
            base_activity['crew_base_activity'].update(dict(
                sim_position=bag.rosterserver.position_in_simulation()
            ))
            base_activities.append(build_briefing_activity(bag))
            base_activities.append(base_activity)
            # Only append debriefing if there is any checkout time in the activity.
            if int(bag.rosterserver.leg_check_out()) > 0:
                base_activities.append(build_briefing_activity(bag, briefing=False))
        else:
            base_activities.append(base_activity)

        # For activities longer than 1 day, increment start with 24hrs
        start_day = start_day + RelTime(1, 0, 0)

    return base_activities


def build_briefing_activity(bag, briefing=True):
    """
    Creates a briefing or debriefing activity surrounding a simulator activity.
    :param bag:
    :param briefing: True if the activity should be briefing activity, otherwise a debriefing activity is created.
    :return:
    """

    if briefing:
        ba_prefix ='B'  # briefing activity
        stop_duration = DEFAULT_DURATION
        task_code = ba_prefix + bag.rosterserver.leg_code()[1:]
        std = util.abs_time_to_str(bag.rosterserver.std_lt_abstime() - bag.rosterserver.leg_check_in())
        sta = bag.rosterserver.std_lt()
    else:
        ba_prefix='D'  # de-briefing activity
        if int(RelTime(bag.rosterserver.stop_duration_scheduled())) > 0:
            stop_duration = xml.duration('stop_duration', RelTime(bag.rosterserver.stop_duration_scheduled()) - bag.rosterserver.leg_check_out()).pop()
        else:
            stop_duration = DEFAULT_DURATION
        task_code = ba_prefix + bag.rosterserver.leg_code()[1:]
        std = bag.rosterserver.sta_lt()
        sta = util.abs_time_to_str(bag.rosterserver.sta_lt_abstime() + bag.rosterserver.leg_check_out())

    briefing_activity = dict(
        activity_id = ba_prefix + bag.keywords.activity_id()[1:],
        activity_type='B',
        crew_base_activity=dict(
            task_code=task_code,
            std=std,
            sta=sta,
            dep_station=bag.rosterserver.dep_station(),
            arr_station=bag.rosterserver.arr_station(),
            stop_duration=stop_duration
        )
    )

    return briefing_activity


def show_crew_rosters_data(crew_id=None):
    """
    Builds and shows all roster-data for passed-in or first selected crew.
    """
    if crew_id is None:
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), 'OBJECT')
        try:
            crew_id = rave.eval(rave.selected(rave.Level.atom()), 'rosterserver.%crew_id%')[0]
        except ValueError:
            print("Error: No context!")
    if not crew_id:
        import carmstd.cfhExtensions as ext
        ext.show("No crew selected.\n(Mark a roster by clicking on the crew info in left column).",
                 title="No crew selected")
        return -1
    crew = build_rosters([crew_id])
    pprint(crew)
    util.show_message(pformat(crew), "Roster data for crew %s" % crew_id)


class CrewRosterSubmitter(object):
    """
    Handle submissions to crewinfoserver DIG channel for crew roster,
    used by FileHandlingExt.
    """

    # Wait 'delay' minutes before the job is run
    delay = 0

    def __init__(self):
        self.modified_crew = []
        self.submitter = 'studio_save_crewroster_push_job'
        self.__job_queue = None

    @property
    def job_queue(self):
        """Return DigJobQueue object."""
        if self.__job_queue is None:
            self.__job_queue = DigJobQueue(
                channel='crewinfoserver',
                submitter=self.submitter,
                reportName='report_sources.report_server.rs_crewinfoserver',
                useTimeServer=False)
        return self.__job_queue

    def setSubmitter(self, submitter):
        self.submitter = submitter

    def prepare(self):
        """Check modified crew."""                
        self.modified_crew = mods.get()

    def submit(self):
        """Submit Job if any crew was modified."""
        try:
            if self.modified_crew:

                submit_time, = rave.eval('fundamental.%now%')
                crew_parameters = {'push_type': 'crewrosters'}
                for crew_nr, crew_id in enumerate(self.modified_crew):
                    crew_parameters['crew%s' % crew_nr] = crew_id

                # Add delay
                submit_time += RelTime(self.delay)

                self.job_queue.submitJob(params=crew_parameters,
                                         reloadModel='1',
                                         curtime=submit_time)
        finally:
            # Just in case, to avoid two submit() without prepare() between
            self.modified_crew = []
            self.submitter = 'studio_save_crewroster_push_job'

# "Singleton"
run = CrewRosterSubmitter()

# Used by FileHandlingExt
prepare = run.prepare
submit = run.submit
