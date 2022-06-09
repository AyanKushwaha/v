"""
Report Server interface for WFS time entry report.
"""

from report_sources.report_server.rs_if import argfix
from salary.wfs.wfs_time_entry import TimeEntry 

@argfix
def generate(*a, **d):
    crew_ids = d.get("crew_ids", None)
    if crew_ids is None:
        crew_ids = [crew_id for (crew_nr, crew_id) in d.iteritems() if 'crew' in crew_nr]
    
    te = TimeEntry() 
    
    if len(crew_ids) == 0:
        # Generate time entry report for all crew
        te.generate([])
    else:
        te.generate(crew_ids)

    return []
