"""
 $Header$

 Hotel Report. For more information, see ../include/Hotel.py
"""
import report_sources.include.CpeStandbyDistribution
#reload(report_sources.include.CpeStandbyDistribution)

from report_sources.include.CpeStandbyDistribution import CpeStandbyDistribution as Report

class CpeStandbyDistribution(Report):
    
    def create(self):
        Report.create(self, 'pdf')
