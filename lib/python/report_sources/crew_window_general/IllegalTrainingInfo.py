"""
 $Header$

 Illegal Training Info Report. For more information, see ../include/LegalityInfo.py
"""

#from report_sources.include.LegalityInfo import LegalityInfo as Report
from report_sources.include.IllegalTrainingInfo import IllegalTrainingInfo as Report

class IllegalTrainingInfo(Report):
    
    def create(self):
        print "In report_sources/crew_window_general/IllegalTrainingInfo.py"
        #Report.create(self, scope='trip_general', special='training')
        Report.create(self)
        
