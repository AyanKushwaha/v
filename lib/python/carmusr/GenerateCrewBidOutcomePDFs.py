"""
This script generates CrewBidOutcome reports for PDF export.

One Summary report is generated plus one per crew member in the plan
who has a bid or lifestyle entered
"""


import os
import glob
import shutil
from datetime import datetime
from operator import itemgetter
from tempfile import NamedTemporaryFile

import Cui
import carmensystems.rave.api as r
from MenuCommandsExt import showCrewCrrs
from carmstd import area, bag_handler

# If additional output should be sent to stdout
DEBUG = False
# How many reports to save for each crew
MAX_INDIVIDUAL_REPORTS = 3
MAX_SUMMARY_REPORTS = 3

SUMMARY_REPORT_NAME = "group_statistics"

REPORT_PATH = 'crew_window_object/CrewBidOutcome.py'

# All reports will be delivered to Interbids
BASE_DIRECTORY = os.path.expandvars('$CARMDATA/crewportal/datasource/reports/interbids')

def dbg(text):
    """Send message to stdout if debug is active."""
    if DEBUG:
        print text

def notify(text):
    """Show message in studio, and stdout if debug is active"""
    area.promptPush(text)
    dbg(text)

def get_user_output_directory(crew_id):
    """Find out the location of the user's report directory."""
    # Path ex. <base_dir>/user/103/10300/CrewBidOutcome/
    return os.path.join(BASE_DIRECTORY, 'user', str(crew_id)[:3], crew_id, "CrewBidOutcome")

def generate_user_report(crew_id, plan_date):
    """Generate a report for a user."""
    output_directory = get_user_output_directory(crew_id)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_filename = "CrewBidOutcome_{0}_{1}.pdf".format(plan_date, crew_id)
    output_file_path = os.path.join(output_directory, output_filename)

    dbg("Generating individual report at: {0}".format(output_file_path))

    # Set Selection and generate pdf
    Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.CrewMode, crew_id)
    Cui.CuiCrgCreatePythonReport(Cui.gpc_info, Cui.CuiWhichArea, 'object', REPORT_PATH,
                                 output_file_path, 'pdf', 'script=Crew')

def generate_summary_report():
    """Generate a summary report in a temporary file and return the path"""

    output_path = NamedTemporaryFile(prefix='report_').name

    dbg("Generating summary report at: {0}".format(output_path))
    Cui.CuiCrgCreatePythonReport(Cui.gpc_info, Cui.CuiWhichArea, 'window', REPORT_PATH,
                                 output_path, 'pdf', 'script=Summary')
    return output_path

def remove_reports(output_directory, suffix, max_reports):
    """Remove old reports located at a specific directory."""
    report_paths = glob.glob("{0}/CrewBidOutcome_*_{1}.pdf".format(output_directory, suffix))

    reports = [{'path':file_path, 'datetime':datetime.strptime(os.path.basename(file_path),
                "CrewBidOutcome_%b%Y_{0}.pdf".format(suffix))} for file_path in report_paths]

    # We want the list sorted by date in reverse order i.e the oldest reports are last in the list
    reports.sort(key=itemgetter('datetime'), reverse=True)
    # Remove the oldest report until we're at or under the maximum allowed amount
    while len(reports) > max_reports:
        dbg("Removing: {0}".format(reports[-1]['path']))
        os.remove(reports.pop()['path'])

def remove_old_user_reports(crew_id):
    """Remove old reports for a specific user."""
    output_directory = get_user_output_directory(crew_id)
    # Quit early if no reports exist
    if not os.path.exists(output_directory):
        return
    remove_reports(output_directory, crew_id, MAX_INDIVIDUAL_REPORTS)
    remove_reports(output_directory, SUMMARY_REPORT_NAME, MAX_SUMMARY_REPORTS)

def generate_pdfs():
    """Generate individual and summary reports for all crew in the subplan."""
    dbg("Started")
    # Extract date information
    plan_date = r.eval('format_time(fundamental.%pp_start%, "%b%Y")')[0]

    # Show assignments and trips
    showCrewCrrs(planning_area_filter=True, remove_other_windows=False, set_basefilter=True)
    Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiArea0)

    # Iterate through all visible crew to get their ids
    bag_wrapper = bag_handler.WindowChains()
    crew_in_plan = []
    for roster_bag in bag_wrapper.bag.chain_set():
        crew_in_plan.append(roster_bag.crew.id())

    # Generate the summary pdf to temporary file
    notify('Generating Summary PDF')
    generated_summary_path = generate_summary_report()

    for index, crew_id in enumerate(crew_in_plan):
        notify('Generating, distributing and cleaning up reports for crew {0}/{1}'.format(index+1, len(crew_in_plan)))
        # Generate individual report
        generate_user_report(crew_id, plan_date)

        # Copy the summary report to this crew
        output_directory = get_user_output_directory(crew_id)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        output_filename = "CrewBidOutcome_{0}_{1}.pdf".format(plan_date, SUMMARY_REPORT_NAME)
        output_path = os.path.join(output_directory, output_filename)
        dbg("Copying summary report to: {0}".format(output_path))
        shutil.copyfile(generated_summary_path, output_path)

        # Clean up old reports
        remove_old_user_reports(crew_id)

    # Remove temp summary report
    os.remove(generated_summary_path)

    notify('CrewBidOutcome PDF generation completed')
