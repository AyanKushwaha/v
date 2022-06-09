

"""
32.14 DutyCalculation.
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.dutycalculation import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
