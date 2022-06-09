

"""
Report Server V2 interface to:

44.5 Bought days and compensation days (Danish Crew) (autorelease).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.autorelease(run.RunData(extsys="DK", runtype="COMPDAYS"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
