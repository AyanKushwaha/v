

"""
46.3 Landings
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.crewlanding import report

# This report updates the entity 'crew_landing'.

@argfix
@RSv2_report(use_delta=True)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
