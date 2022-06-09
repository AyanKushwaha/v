"""
 $Header$

 Special Schedule Info Report. For more information, see ../include/NotesInfo.py
"""

from report_sources.include.NotesInfo import NotesInfo as Report

class SpecialScheduleInfo(Report):

    def create(self):
        Report.create(self, Report.TYPE_SPEC_SCHED)
