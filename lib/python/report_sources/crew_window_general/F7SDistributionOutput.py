"""
 $Header$

 F7S Distribution Output Report. For more information, see ../include/F7SDistribution.py
"""

from report_sources.include.F7SDistribution import F7SDistribution as Report

class F7SDistributionOutput(Report):
 
    def create(self):
        Report.create(self, 'output')
