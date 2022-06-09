"""
Report Server interface for WFS work schedule report.
"""

from report_sources.report_server.rs_if import argfix
from salary.wfs.wfs_work_schedule import WorkSchedule

@argfix
def generate(*a, **d):
    crew_ids = d.get("crew_ids", None)
    if crew_ids is None:
        crew_ids = [crew_id for (crew_nr, crew_id) in d.iteritems() if 'crew' in crew_nr]
    
    ws = WorkSchedule() # Default to release=True 

    if len(crew_ids) == 0:
        # Generate work schedule report for all crew
        ws.generate([])
    else:
        ws.generate(crew_ids)

    return []