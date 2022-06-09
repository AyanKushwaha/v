

"""
Report Server V2 interface to:

44.3 Overtime Temporary Crew allowance (Danish Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    t = run.Times()
    return run.job(run.RunData(
        extsys="DK", runtype="TEMP_CREW", firstdate=t.month_start, lastdate=t.month_end))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
