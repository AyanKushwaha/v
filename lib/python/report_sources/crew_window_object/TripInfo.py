#

#
"""
Trip Info Report
"""

from report_sources.include.TripInfo import TripInfo as Report

class TripInfo(Report):
 
    def create(self):
        Report.create(self, scope='crew_object', context='marked_in_window_left')
