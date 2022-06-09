"""
 $Header$

 Group Statistics Report. For more information, see ../include/GroupStatistics.py
"""

from report_sources.include.GroupStatistics import GroupStatistics as Report

class GroupStatistics(Report):

    def create(self):
        Report.create(self, 'pdf', context='marked_in_window_left')
