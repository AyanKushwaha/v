#!/usr/bin/env python
# coding: utf-8
"""

 Builds check-in push objects if cio/run.py

"""
# Python imports
from datetime import datetime

# External CARMUSR imports
import carmensystems.rave.api as rave
from dig.DigJobQueue import DigJobQueue
from utils.selctx import SingleCrewFilter

# Crew Info Server imports
import crewinfoserver.server.api_handler as api
import crewinfoserver.common.util as util
import data_handler as dh


def push_checkin(empno):
    """

    :param activity_ids: comma separated string of all activity_id's in trip
    :param empno: employment number of crew
    :return:
    """
    checkin_object = build_checkin(empno)

    (res, status_code), elapsed = util.timed(lambda: api.post_check_in(checkin_object))
    print("done!  (status: %s) (res: %s) (elapsed: %s)" % (status_code, res, elapsed))

    return elapsed


def prepare_checkin_messages(empno):
    """

    :param empno: employment number of crew
    :return:
    """
    checkin_object = build_checkin(empno)
    count, messages = dh.structure_messages(checkin_object, "checkin")

    return count, messages


def build_checkin(empno):
    """
    Posts a check-in message to CIS

    :param empno: employment number of crew
    :return: returns the time elapsed for pushing crew to CIS
    """
    update_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    activity_id_list = build_activity_ids(empno)

    checkin_object = dict(
        activity_ids=activity_id_list,
        empno=empno,
        last_update=update_time
    )

    return checkin_object


def build_activity_ids(empno):
    """
    Builds a list of activities on which the crew should be checked in

    :param empno: employment number of crew
    :return: list of activities
    """ 
    activity_ids = []
    crew_id = rave.eval("rosterserver.%%extperkey_to_id_now%%(\"%s\")" % str(empno))[0]
    for ch in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
        for tr in ch.iterators.trip_set(where="rosterserver.%first_ci_trip%"):
            tmp_activities = []
	    for leg_bag in tr.iterators.leg_set():
                tmp_activities.append(leg_bag.keywords.activity_id())
	    activity_ids.append(tmp_activities)
    return activity_ids[0]


class CheckedInSubmitter(object):
    """
    Handle submissions to crewinfoserver DIG channel for checked in,
    used by cio/run.py
    """

    def __init__(self):
        self.__job_queue = None

    @property
    def job_queue(self):
        """Return DigJobQueue object"""
        if self.__job_queue is None:
            self.__job_queue = DigJobQueue(
                channel='crewinfoserver',
                submitter='check_in_dig_job',
                reportName='report_sources.report_server.rs_crewinfoserver',
                useTimeServer=False)
        return self.__job_queue

    def submit(self, empno):
        """
        Submit Job if a CheckInOut message has come in on the CQFREQ MQ-channel
        """
        submit_time, = rave.eval('fundamental.%now%')
        parameters = dict(
            push_type='checkin',
            crew_ids=empno
        )

        self.job_queue.submitJob(
            params=parameters,
            reloadModel='1',
            curtime=submit_time
        )

# "Singleton
run = CheckedInSubmitter()

# Used by cio/run.py
submit = run.submit


