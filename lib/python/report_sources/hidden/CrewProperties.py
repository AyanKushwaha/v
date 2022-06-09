"""
 $Header$

 Crew Properties Report. For more information, see ../include/CrewProperties.py
"""

from report_sources.include.CrewProperties import CrewProperties as Report

class CrewProperties(Report):

    def create(self):
        Report.create(self, headers=False, context='marked_in_window_left')
