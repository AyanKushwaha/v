

"""
Report Server V2 interface to:

Monthly allowances (Swedish Crew) (automatic release).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.autorelease(run.RunData(extsys="S3", runtype="ALLOWNCE_M"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
