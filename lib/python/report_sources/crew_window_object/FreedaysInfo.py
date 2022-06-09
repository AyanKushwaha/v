"""
 $Header$

 Freedays Info Report. For more information, see ../include/FreedaysInfo.py
"""

from report_sources.include.FreedaysInfo import FreedaysInfo as Report

class FreedaysInfo(Report):

    def create(self):
        Report.create(self, 'object', context='marked_in_window_left')
