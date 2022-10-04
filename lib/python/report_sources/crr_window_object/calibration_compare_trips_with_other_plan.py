"""
Compare plans
"""


from __future__ import absolute_import

from carmusr.calibration import report_compare_plans as compare_plans


class Report(compare_plans.ReportComparePlans):
    pass


if __name__ == "__main__":
    from carmusr.calibration.mappings import report_generation as rg
    from carmusr.calibration.developer_tools import reload_calibration_report_modules

    reload_calibration_report_modules.doit()
    rg.display_prt_report(fm="HTML", area=0, scope="object")
