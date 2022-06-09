'''
Calibration Dashboard for timetable Analysis
'''

import carmusr.calibration.report_dashboard
from carmusr.calibration.util import common


class Report(carmusr.calibration.report_dashboard.Report):
    default_variant_key = common.CalibAnalysisVariants.TimetableAnalysis.key


if __name__ == "__main__":
    from carmusr.calibration.mappings import report_generation as rg
    from carmusr.calibration.developer_tools import reload_calibration_report_modules

    reload_calibration_report_modules.doit()
    rg.display_prt_report(fm="HTML", area=0, scope="object")
