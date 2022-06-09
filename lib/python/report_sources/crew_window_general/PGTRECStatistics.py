"""
 $Header$

 F7S Distribution Output Report. For more information, see ../include/F7SDistribution.py
"""

from report_sources.include.PGTRECStatistics import PGTRECStatistics as Report

class PGTRECStatistics(Report):
 
    def create(self):
        Report.create(self, 'pdf')
