

"""
Report Server V2 interface to:

43.5.2 Vacation days year/account (Swedish Crew only).

(Yearly report)
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="SE", runtype="VACATION_Y", noCheckPP=True),
            release_run=True)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
