"""
 $Header$

 Trip Distribution Output Report. For more information, see ../include/TripDistribution.py
"""

from report_sources.include.TripDistribution import TripDistribution as Report

class TripDistributionOutput(Report):
 
    def create(self):
        Report.create(self, 'output')
