from report_sources.report_server.rs_if import argfix, RSv2_report
from crewlists.services_archiver import report


@argfix
@RSv2_report(use_delta=False)
def generate(*a, **k):
    return report(*a, **k)
