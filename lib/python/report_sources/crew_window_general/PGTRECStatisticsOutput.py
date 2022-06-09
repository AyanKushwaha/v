"""
 $Header$

 F7S Distribution Output Report. For more information, see ../include/F7SDistribution.py
"""

from report_sources.include.PGTRECStatistics import PGTRECStatistics as Report

class PGTRECStatisticsOutput(Report):
 
    def create(self):
        Report.create(self, 'output')
