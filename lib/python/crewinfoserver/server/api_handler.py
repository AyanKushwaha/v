# coding: utf-8
"""

Handles all queries towards the Crew Info Server

"""

import servers
import endpoint_builder as epb


def post_crew(crew):
    """
    Spec at: <rosterserver>/cms/v1/api. UNKNOWN!!


    :param crew: A Python list of dicts - one dict per crew.
    :return: A Python map.
    """
    url = "/cis/v1/crewprofiles"
    return epb.http_json_request_response(servers.get_server(), url, epb.POST, dict(crewprofiles=crew))


def post_roster(rosters):
    """

    :param rosters: A Python list of dicts - one dict per crews roster.
    :return: A Python map.
    """

    url = "/cis/v1/crewrosters"
    return epb.http_json_request_response(servers.get_server(), url, epb.POST, dict(crewrosters=rosters))


def post_check_in(check_in):
    url = "/cis/v1/checkin"
    return epb.http_json_request_response(servers.get_server(), url, epb.POST, dict(checkin=check_in))
