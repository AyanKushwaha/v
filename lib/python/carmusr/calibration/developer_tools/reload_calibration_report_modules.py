'''
This module is just for development. It reloads most modules defining the Calibration reports in the right order.
Execute it as a script to perform all the reloads.

Created on 4 Dec 2020

@author: steham
'''

import sys
from six.moves import reload_module


def doit():
    reload_module(__import__("carmusr.calibration.mappings", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.pie_chart", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.basics", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.config_per_product_si", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.config_per_product_rule_details", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.config_per_product", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.common", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.rave_code_explorer", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.calibration_rules", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.complement", fromlist=[None]))
    ret = __import__("carmusr.calibration.util.complement", fromlist=[None]).refresh_and_get_error_message_if_something_is_wrong()
    if ret:
        print(ret)
    reload_module(__import__("carmusr.calibration.util.compare_plan", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.rule_kpis_imp", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.report_util", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.util.report_rules", fromlist=[None]))

    reload_module(__import__("carmusr.calibration.command_si_rave_code_generation", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_violations_over_station", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_violations_over_time", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_violations_over_weekdays", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_rule_value_distribution", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_rule_details", fromlist=[None]))

    reload_module(__import__("carmusr.calibration.report_compare_plans", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_si", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_pattern_analysis", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_rule_kpis", fromlist=[None]))
    reload_module(__import__("carmusr.calibration.report_dashboard", fromlist=[None]))

    reload_module(__import__("carmusr.calibration.util.report_forms", fromlist=[None]))

    for module_name in list(sys.modules):
        if not sys.modules[module_name]:
            continue
        if "calibration" not in module_name:
            continue
        if "report_sources" not in module_name:
            continue
        try:
            reload_module(sys.modules[module_name])
        except ImportError:
            pass


if __name__ == "__main__":
    me = __import__("carmusr.calibration.developer_tools.reload_calibration_report_modules",
                    fromlist=[None])
    reload_module(me)
    me.doit()
