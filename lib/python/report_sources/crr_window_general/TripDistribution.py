"""
 $Header$

 Trip Distribution Report. For more information, see ../include/TripDistribution.py
"""

from report_sources.include.TripDistribution import TripDistribution as Report

class TripDistribution(Report):
 
    def create(self):
        Report.create(self, 'pdf')
