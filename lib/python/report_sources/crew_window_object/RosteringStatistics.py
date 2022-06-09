"""
 $Header$
 
 Rostering Statistics Report. For more information, see ../include/RosteringStatistics.py
 
"""

from report_sources.include.RosteringStatistics import RosteringStatistics as Report

class RosteringStatistics(Report):

    def create(self):
        Report.create(self, 'object', context='marked_in_window_left')
