"""
 $Header$

 Group Statistics Report. For more information, see ../include/GroupStatistics.py
"""

from report_sources.include.GroupStatistics import GroupStatistics as Report

class GroupStatisticsOutput(Report):

    def create(self):
        Report.create(self, 'output')
