

"""
Report Server V2 interface to:

44.3 Overtime and Allowances (Swedish Crew).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    t = run.Times()
    return run.job(run.RunData(extsys="SE", runtype="OVERTIME", monthsBack=int(k.get('monthsBack',1))))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
