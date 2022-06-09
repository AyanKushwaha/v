

"""
Handle checkin and checkout events.
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix, RSv2_report_delta
from cio.run import report_delta


@argfix
@add_reportprefix
@RSv2_report_delta()
def generate(*a, **k):
    return report_delta(*a, **k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
