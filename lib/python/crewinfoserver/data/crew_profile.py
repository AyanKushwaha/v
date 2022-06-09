#!/usr/bin/env python
# coding: utf-8
"""

 Builds Crew Profile data objects...

"""
# Python imports
from datetime import datetime
from pprint import pformat
import os

# External CARMUSR imports
import Cui
import carmensystems.rave.api as rave
from utils.selctx import SingleCrewFilter


# Crew Info Server imports
from crewinfoserver.common import util
import crewinfoserver.server.api_handler as api
import data_handler as dh


# CONSTANTS
CREW_CHUNK_SIZE = 500  # Number of crew updated at a time
DELAY = 1.0  # Delay between each http request with chunk in seconds


def push_crew(crew):
    """
    Pushes crew in chunks.
    :param crew: list of crew
    :return: [crew-count, elapsed-time]
    """
    return dh.make_http_push(crew, api.post_crew, CREW_CHUNK_SIZE, DELAY)


def push_all_crew():
    """
    Pushes all crew.
    :return:
    """
    push_specific_crew(None)


def push_specific_crew(crew_ids):
    """
    Builds and pushes specific crew.
    :param crew_ids: List of crew ID's for crew to be pushed
    :return: count: nr crew being pushed
    :return: elapsed: method execution time
    """
    start = datetime.now()

    crew_objects = build_crew(crew_ids)

    count, _ = push_crew(crew_objects)

    elapsed = datetime.now() - start
    print("Time elapsed pushing %s crew: %s" % (count, elapsed))
    return count, str(elapsed)


def push_visible_crew():
    """
    Called from RosterServer menu (crewinfoserver.menues.py)
    :return:
    """
    visible_crew = dh.get_visible_crew()
    count, elapsed = push_specific_crew(visible_crew)
    return count, elapsed


def prepare_crewprofile_messages(crew_ids):
    """
    Prepares the crewprofile messages to be put on the message queue

    :param crew_ids: the IDs of crew who are to be updated
    :return: count: nr of crews being part of all messages being created
    :return: messages: a list of all messages to be put on the queue
    """
    crew_objects = build_crew(crew_ids)
    count, messages = dh.structure_messages(crew_objects, "crewprofiles", CREW_CHUNK_SIZE)
    return count, messages


def build_crew(crew_ids=None):
    """
    Builds crew data for specified list of crew IDs.
    :param crew_ids: List of crew IDs. If None is passed, crew data for all
    crew will be built.
    :return: List of crew objects, each crew object is represented by a dict.
    """
    start = datetime.now()
    crew_ids = util.start_build("crew", crew_ids)

    crew_objects = list()
    if crew_ids is None:
        crew_objects = build_all_crew(crew_objects)
    else:
        for crew_id in crew_ids:
            crew_objects.append(build_single_crew(crew_id))

    util.end_build("crew", crew_ids, start)

    return crew_objects


def build_all_crew(crew_objects):
    """
    Builds a crew object for every crew listed in sp_crew context.
    :return: List of crew objects, each crew object is represented by a dict.
    """

    for roster_bag in rave.context('sp_crew').bag().chain_set(where="rosterserver.%has_employment%"):
        crew_objects.append(
            build_crew_object(roster_bag.rosterserver.crew_id(), roster_bag))

    return crew_objects


def build_single_crew(crew_id):
    """
    Builds crew objects for a specific crew ID.
    :param crew_id: String containing crew ID for one crew.
    :return: Crew object represented by a dict.
    """
    crew_object = dict()
    for crew_bag in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
        crew_object = build_crew_object(crew_id, crew_bag)
    return crew_object


def build_crew_object(crew_id, bag):

    """
    Builds and returns the crew object
    :param bag: CMS bag interface
    :param crew_id: ID of the crew being built
    :return: A dict containing specified crew information
    """ 
    
    documents = []
    for i in range(1, bag.rosterserver.count_rows() + 1):
        if str(bag.rosterserver.doc_type(i)) != 'N/A':
            document = dict()
            document['type'] = bag.rosterserver.doc_type(i)
            document['subtype'] = bag.rosterserver.doc_subtype(i)
            document['validfrom'] = bag.rosterserver.doc_validfrom(i)
            document['validto'] = bag.rosterserver.doc_validto(i)
            document['no'] = bag.rosterserver.doc_no(i)
            document['maindocno'] = bag.rosterserver.doc_maindoc(i)
            document['issuer'] = bag.rosterserver.doc_issuer(i)
            documents.append(document)
            
    return dict(
                empno=bag.rosterserver.empno(),
                last_update=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                crew_id=crew_id,
                seniority=bag.rosterserver.seniority(),
                name=util.encode_to_regular(bag.rosterserver.name()),
                gender=bag.rosterserver.gender(),
                main_rank=bag.rosterserver.main_rank(),
                title_rank=bag.rosterserver.title_rank(),
                group_type=bag.rosterserver.group_type(),
                sub_category=bag.rosterserver.sub_category(),
                company=bag.rosterserver.company(),
                region=bag.rosterserver.region(),
                homebase=bag.rosterserver.homebase(),
                station=bag.rosterserver.station(),
                civic_station=bag.rosterserver.civic_station(),
                ac_qual_group=bag.rosterserver.ac_qual_grp(),
                phone=bag.rosterserver.mobile_number(),
                email=util.encode_to_regular(bag.rosterserver.email_address()),
                line_check_crew=str(bag.rosterserver.is_line_check()),
                scc_qualified=str(bag.rosterserver.is_scc_qualified()),
                documents=documents
            )

def show_crew_profile_details(crew_id=None):
    """
    Builds and shows all crew-data for passed-in or first selected crew.
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
    crew = build_crew([crew_id])
    util.show_message(pformat(crew), "Crew data for crew %s" % crew_id)
