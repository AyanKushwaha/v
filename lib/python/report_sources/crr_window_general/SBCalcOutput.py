"""
 $Header$

 Trip statistics daily Report. For more information, see ../include/SBCalcOutput.py
"""

from report_sources.include.SBCalcOutput import SBCalcOutput as Report

class SBCalcOutput(Report):
 
    def create(self):
        Report.create(self, 'standard', True)
