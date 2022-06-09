
"""
Entry point for reportworker for CMS -> LMS qualifications
interface.
"""

from report_sources.report_server.rs_if import argfix
from salary.lms_qual_report import LMSQualReport

@argfix
def generate(*a, **d):
    crew_ids = d.get("crew_ids", None)
    if crew_ids is None:
        crew_ids = [crew_id for (crew_nr, crew_id) in d.iteritems() if 'crew' in crew_nr]

    print("Got %s crew: %s" % (len(crew_ids), crew_ids))
    lms = LMSQualReport()
    lms.generate([])
    #if type(crew_ids) is str:
    #    crew_ids = ast.literal_eval(crew_ids)
    #if crew_ids:
    #    roster_push.push_specific_rosters(crew_ids)

    return [], True
