"""
Rule Violations over Weekdays
"""


from __future__ import absolute_import

import carmusr.calibration.report_violations_over_weekdays as rr


class Report(rr.RuleViolationsOverWeekdays):
    pass


if __name__ == "__main__":
    from carmusr.calibration.mappings import report_generation as rg
    from carmusr.calibration.developer_tools import reload_calibration_report_modules

    reload_calibration_report_modules.doit()
    rg.display_prt_report(fm="HTML", area=0, scope="object")
