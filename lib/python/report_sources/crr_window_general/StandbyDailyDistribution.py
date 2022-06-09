"""
 $Header$

 Hotel Report. For more information, see ../include/Hotel.py
"""
import report_sources.include.StandbyDailyDistribution
#reload(report_sources.include.StandbyDailyDistribution)

from report_sources.include.StandbyDailyDistribution import StandbyDailyDistribution as Report

class StandbyDailyDistribution(Report):
    
    def create(self):
        Report.create(self, 'pdf')
