

"""
CR 184 - Landings for A/C without ACARS.

Update crew landings for aircraft types that don't have the ACARS system (F50
and B737 Classic). This report is started by the scheduler once every day.
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.crewlanding import run

# This report updates the entity 'crew_landing'.

@argfix
@RSv2_report(use_delta=True)
def generate(*a, **k):
    # Will default to use previous UTC date.
    return run(from_date=k.get('from_date'), to_date=k.get('to_date'))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
