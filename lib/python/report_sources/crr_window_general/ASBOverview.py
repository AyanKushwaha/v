"""
 $Header$
 
 Deadhead Report. For more information, see ../include/DeadheadInfo.py
 
"""

from report_sources.include.ASBOverview import ASBOverview as Report

class ASBOverview(Report):
    
    def create(self):
        Report.create(self, 'output')
