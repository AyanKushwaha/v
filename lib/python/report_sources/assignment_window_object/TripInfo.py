#

#
"""
Trip Info Report
"""

from report_sources.include.TripInfo import TripInfo as Report
import carmensystems.rave.api as R

class TripInfo(Report):
    def create(self):
        Report.create(self, scope='assignment_object', context='marked_in_window_main', showPlanData=False, showFailures=False)
