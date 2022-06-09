#

#
"""
Trip Info Report
"""

from report_sources.include.TripInfo import TripInfo as Report

class TripInfo(Report):
 
    def create(self):
        Report.create(self, scope='trip_general', context='default_context')
