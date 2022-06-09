

"""
40.2 Crew Baggage Reconciliation.
"""

from report_sources.report_server.rs_if import argfix
from crewlists.baggage import reports

@argfix
def generate(*a, **k):
    reportlist_str = reports(*a, **k)
    reportlist = []
    for r_str in reportlist_str:
        reportlist.append(
            {
                'content': r_str,
                'content-type': 'text/plain',
                'destination': [('default', {})],
            }
        )
    
    return reportlist, True


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
