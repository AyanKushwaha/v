"""
 $Header$

 Legality Info Report. For more information, see ../include/LegalityInfo.py
"""

from report_sources.include.LegalityInfo import LegalityInfo as Report

class LegalityInfoTrip(Report):

    def create(self):
        Report.create(self, scope='trip', headers=False, context='marked_in_window_main')

