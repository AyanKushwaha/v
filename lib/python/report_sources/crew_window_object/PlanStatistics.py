"""
 $Header$

 Plan Statistics Report. For more information, see ../include/PlanStatistics.py
"""

from report_sources.include.PlanStatistics import PlanStatistics as Report

class PlanStatistics(Report):

    def create(self):
        Report.create(self, context='marked_in_window_left')
