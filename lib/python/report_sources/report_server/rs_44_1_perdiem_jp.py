

"""
Report Server V2 interface to:h

44.1 PerDiem (Japanese Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="JP", runtype="PERDIEM"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
