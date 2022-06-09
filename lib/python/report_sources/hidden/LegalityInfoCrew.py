"""
 $Header$

 Legality Info Report. For more information, see ../include/LegalityInfo.py
"""

from report_sources.include.LegalityInfo import LegalityInfo as Report

class LegalityInfoCrew(Report):
    
    def create(self):
        Report.create(self, scope='crew', context='marked_in_window_left', headers=False)
        
