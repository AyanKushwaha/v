"""
 $Header$

 Crew Warning Info Report. For more information, see ../include/CrewWarningInfo.py
"""

from report_sources.include.CrewWarningInfo import CrewWarningInfo as Report

class CrewWarningInfo(Report):

    def create(self):
        Report.create(self, 'general')
