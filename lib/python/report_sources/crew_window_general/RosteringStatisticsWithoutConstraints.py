"""
 $Header$
 
 Rostering Statistics Report. For more information, see ../include/RosteringStatistics.py
 
"""

from report_sources.include.RosteringStatistics import RosteringStatistics as Report

class RosteringStatisticsWithoutConstraints(Report):

    def create(self):
        Report.create(self, 'general', fd=False)
