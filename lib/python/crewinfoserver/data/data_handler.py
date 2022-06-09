# coding: utf-8
# Python imports
import time
from datetime import datetime, timedelta
from uuid import uuid4

# CARMSYS imports
import Cui

# Crew Info Server imports
from crewinfoserver.common import util
import carmensystems.rave.api as rave


class CISPostException(Exception):
    pass


def get_visible_crew():
    """Returns list of all crew visible in "CuiArea0". """
    crew = []
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "WINDOW")
    for roster_bag in rave.context("current_context").bag().chain_set():
        crew.append(roster_bag.crew.id())
    return crew


def make_http_push(push_objects, post_function, chunk_size, delay):
    count = 0
    elapsed = timedelta()

    # List to keep track of status codes returned from CrewInfoServer.
    status_codes = list()
    # Counter for how many rosters successfully are updated in CrewInfoServer.
    success_count = 0

    for chunk in util.chunks(push_objects, chunk_size):
        size = len(chunk)
        try:
            # Set status_code to default value
            status_code = -1
            print("%s Sending chunk (%s) to server ..." % (datetime.now().strftime("%Y%m%d %H:%M:%S"), size))
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                (res, status_code), t = util.timed(lambda: post_function(chunk))
            print("done!  (status: %s) (res: %s) (elapsed: %s)" % (status_code, res, t))

            count += size
            elapsed += t
            if size == chunk_size:  # presumably more chunks to send, so sleep (per request from DXC)
                print("  sleeping %.1f sec ..." % delay)
                time.sleep(delay)
        except Exception as err:
            print("Unexpected error pushing data to CIS")
            break
        finally:
            status_codes.append(status_code)

            # Only increment the success counter if the push was successful.
            if status_code == 200:
                success_count += size

    # Raise exception if any of the chunks isn't successfully handled in CrewInfoServer.
    if any(sts_code != 200 for sts_code in status_codes):
        raise CISPostException(
            "%s failed to POST data to CrewInfoServer. %s/%s objects successfully sent." % (post_function.__name__,
                                                                                            success_count,
                                                                                              len(push_objects)))

    return count, elapsed


def structure_messages(built_objects, message_type, chunk_size=1):
    """
    Structures the messages to be put on the message queue

    :param built_objects: one dict or many dicts in a list built using the bag interface
    :param message_type: crewprofiles, crewrosters, checkin
    :param chunk_size: limiting value for how many objects should be sent at a time
    :return: count: total number of crew rosters (can be two for one crew if next month's roster is released)
    :return: messages: the message(s) to be put on the Message Queue
    """
    count = 0
    messages = []

    # crew_profile and crew_roster both contains several dicts in a list
    if isinstance(built_objects, list):
        for chunk in util.chunks(built_objects, chunk_size):
            size = len(chunk)
            messages.append(
                {"request_id":str(uuid4()),
                 message_type:chunk}
            )
            count += size

    # checkin is just a single dict
    elif isinstance(built_objects, dict):
        messages.append(
            {"request_id":str(uuid4()),
             message_type:built_objects}
        )
        count = 1

    return count, messages
