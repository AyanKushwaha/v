

"""
16.1, 32.6.1, 32.11, 41.2, 46.1.1, 46.1.2, 46.2 CrewListService
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.crewlist import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
