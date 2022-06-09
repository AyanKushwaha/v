

"""
Report Server V2 interface to:

Per Diem Tax (NO).
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    return run.job(run.RunData(extsys="NO", runtype="PERDIEMTAX", exportformat="CSV"))

