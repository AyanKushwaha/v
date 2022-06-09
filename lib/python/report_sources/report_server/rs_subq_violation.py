

"""
CR 476 - Sub Q Violation Report.

Updates 'rule_violation_log' with Sub Q rule violations once every day.
"""

from report_sources.report_server.rs_if import argfix, RSv2_report
from carmusr.tracking.RuleViolationReport import subq_violation_report

@argfix
@RSv2_report(use_delta=True)
def generate(*a, **k):
    return subq_violation_report(st=k.get('st'), en=k.get('en'), rerun=k.get('rerun'))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
