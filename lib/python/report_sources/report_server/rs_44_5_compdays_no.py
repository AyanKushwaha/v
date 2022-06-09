

"""
Report Server V2 interface to:

44.5 Bought days and compensation days (Norwegian Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="NO", runtype="COMPDAYS"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
