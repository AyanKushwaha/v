"""
Report generator for running data push jobs to Crew Info Server.
"""
# Python imports
from datetime import datetime
import ast
import os

# CARMUSR imports
from report_sources.report_server.rs_if import argfix
from crewinfoserver.data import crew_profile, crew_rosters, check_in

# CONSTANTS
CSYSENV = os.getenv("CARMSYSTEMNAME")


@argfix
def generate(*a, **k):
    push_type = k.get("push_type", None)
    if push_type is None:
        push_type = "crewprofiles"

    crew_ids = k.get("crew_ids", None)

    if crew_ids is None:
        crew_ids = [crew_id for (crew_nr, crew_id) in k.iteritems() if 'crew' in crew_nr]

    if crew_ids and type(crew_ids) is str:
        crew_ids = ast.literal_eval(crew_ids)

    # crew_ids is an int for check_in
    if type(crew_ids) != int and len(crew_ids) == 0:
        crew_ids = None

    res, reports = [], []
    count = 0
    if push_type == "crewprofiles":
        print("Starting crew profiles")
        if CSYSENV in ["PROD_TEST", "PROD"]:
            count, res = crew_profile.prepare_crewprofile_messages(crew_ids)
        else:
            crew_profile.push_specific_crew(crew_ids)
    elif push_type == "crewrosters":
        print("Starting crew rosters")
        if CSYSENV in ["PROD_TEST", "PROD"]:
            count, res = crew_rosters.prepare_crewroster_messages(crew_ids)
        else:
            crew_rosters.push_specific_roster(crew_ids)
    elif push_type == "checkin":
            print("Starting check_in")
            if CSYSENV in ["PROD_TEST", "PROD"]:
                count, res = check_in.prepare_checkin_messages(crew_ids)
            else:
                check_in.push_checkin(crew_ids)
    else:
        print("Unknown push type: %s", str(push_type))

    for request in res:
        reports.append({'content':("%s" % request),
                        'content-type':'application/json',
                        'destination':[('default', {})],
                        })
        print("%s CIS - request_id: %s" % (datetime.now().strftime("%Y%m%d %H:%M:%S"), request['request_id']))

    print("%s CIS - Push type: %s - chunk count %s" % (datetime.now().strftime("%Y%m%d %H:%M:%S"), push_type, str(count)))

    return reports, True
