

"""
41 PAH, Number of Crew to Load Sheet
"""

from report_sources.report_server.rs_if import RSv2_report, argfix
from crewlists.loadsheet import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
