

"""
Report Server V2 interface to:

44.2 Inst. Allowance (Swedish Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="SE", runtype="SUPERVIS"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
