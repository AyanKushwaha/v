

"""
Report Server V2 interface to:

43.2 AMBI list (Danish Crew only).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="DK", runtype="AMBI"), release_run=True)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
