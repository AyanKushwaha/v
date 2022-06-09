

"""
32.5.3, 32.5.7 and 32.6.3 CrewFlightService
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.crewflight import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
