

"""
Report Server V2 interface to:

44.6.2 Vacation lists OSL
"""

from salary.vacation_lists import vacation
from report_sources.report_server.rs_if import argfix, add_reportprefix, RSv2_report_file


@argfix
@add_reportprefix
def generate(*a, **k):
    return vacation('NO')


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
