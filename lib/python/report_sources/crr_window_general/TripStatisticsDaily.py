"""
 $Header$

 Trip statistics daily Report. For more information, see ../include/TripStatisticsDaily.py
"""

from report_sources.include.TripStatisticsDaily import TripStatisticsDaily as Report

class TripStatisticsDaily(Report):
 
    def create(self):
        Report.create(self, 'standard')
