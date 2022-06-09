"""
 $Header$

 Sim Statistics Report. For more information, see ../include/SimStatistics.py
"""

from report_sources.include.SimStatistics import SimStatistics as Report

class SimStatistics(Report):
 
    def create(self):
        Report.create(self, 'general')
