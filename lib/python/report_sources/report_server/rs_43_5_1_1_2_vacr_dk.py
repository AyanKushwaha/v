

"""
Report Server V2 interface to:

43.5.1.1.2 Vacation days remaining (Danish Crew only).

(Monthly report)
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="DK", runtype="VACATION_R"),
            release_run=True)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
