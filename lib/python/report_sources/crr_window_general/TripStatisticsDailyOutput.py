"""
 $Header$

 Trip statistics daily report. For more information, see ../include/TripStatisticsDaily.py
"""

from report_sources.include.TripStatisticsDaily import TripStatisticsDaily as Report

class TripStatisticsDailyOutput(Report):
 
    def create(self):
        Report.create(self, 'csv')
