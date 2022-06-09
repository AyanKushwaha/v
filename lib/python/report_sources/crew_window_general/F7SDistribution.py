"""
 $Header$

 F7S Distribution Report. For more information, see ../include/F7SDistribution.py
"""

from report_sources.include.F7SDistribution import F7SDistribution as Report

class F7SDistribution(Report):
 
    def create(self):
        Report.create(self, 'pdf')
