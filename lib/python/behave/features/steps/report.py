import os
import Cui

from behave import use_step_matcher

import util

use_step_matcher('re')

@when(u'I generate report "(?P<report_name>.*)"')
def generate_report(context, report_name):
    """
    When I generate report "crr_window_object/trip.py"
    """
    report_name = util.verify_file_name(report_name)
    area = context.window_area
    scope = 'window'
    flags = 0
    _args = 0
    format = 'HTML'
    if context.display:
        # Display the report in Studio browser

        # Note: Consider using OTS report module: report_generation.py
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, context.window_area,
                                           scope, report_name,
                                           flags, _args, format)

    new_root = os.path.expandvars('$CARMTMP/behave/reports')
    new_report_abspath =  os.path.join(new_root, report_name)

    Cui.CuiCrgCreatePythonReport(Cui.gpc_info, area, scope,
                                 report_name, new_report_abspath,
                                 format, _args)

    context.report_file = new_report_abspath



@then(u'the report shall contain a line with "(?P<match_1>.*)" and "(?P<match_2>.*)"')
def verify_report_line(context, match_1, match_2):
    """
    Then the report shall contain a line with "Cost" and "2720"
    """
    match_1 = match_1.encode()
    match_2 = match_2.encode()
    report_file = context.report_file

    with open(report_file, 'r') as report:
        for line in report:
            if line.find(match_1) > -1:
                if line.find(match_2) > -1:
                    return 
    assert False, 'Could not find any line with %s and %s in report:\n%s' % (match_1, match_2, report_file)


