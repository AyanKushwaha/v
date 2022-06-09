

"""
Report Server V2 interface to:

43.5.1.1 Vacation days performed (Danish Crew only).

(Monthly report)
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.api as api
import salary.run as run
from AbsTime import AbsTime
from RelTime import RelTime


@argfix
@add_reportprefix
def generate(*a, **k):
    # Per request we run this report per month. The per year version is left below as reference in case the requirements change back.
    return run.job(run.RunData(extsys="DK", runtype="VACATION_P"),
            release_run=True)

    # tt = api.Times()
    # # Ensure that when run in Jan, we get start of last year.
    # # Eg. when run in Jan2010 we want 01Jan2009 - 01Jan2010
    # year_start = AbsTime(tt.this_month_start) - RelTime(1)
    # year_start = year_start.year_floor()
    # return run.job(run.RunData(extsys="DK", runtype="VACATION_P",
    #     lastdate=tt.this_month_start, firstdate=year_start, noCheckPP=True), release_run=True)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
