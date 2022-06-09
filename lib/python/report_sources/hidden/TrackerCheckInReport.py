#######################################################
#
# Tracker Check In Report
#
# -----------------------------------------------------
# This report shall show the check information accessible
# by the crew in the crew portal
# -----------------------------------------------------
# Created:    2007-03-09
# By:         Jeppesen, Yaser Mohamed
#
#######################################################

from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport

# This report requires "empNo" as input argument
class TrackerCheckInReport(SASReport):

    def create(self):
        SASReport.create(self, 'Check In Report', False, )

        # Should be printed as monospace in order for the alignment of stuff
        # to be correct.
        TEXTFORMAT = Font(face=MONOSPACE)

        # The entire report is an in-argument in the form of one long string.
        report = self.arg("Report")

        # Split the string on all the places where there should be a new line
        report = report.replace("_", " ")

        report = report.split("\n")

        # Add each line as a line in the pdf
        for line in report:
            # Add row for row...
            self.add(Row(Text("%s" %line), font=TEXTFORMAT))
