

"""
Report Server V2 interface to:

Scheduled tempcrew (Swedish Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="S3", runtype="TCSCHEDULE"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
