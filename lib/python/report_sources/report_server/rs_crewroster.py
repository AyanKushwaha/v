

"""
32.0.2, 32.5.1, 32.6.1, and 32.20.1 CrewRosterService
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.crewroster import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
