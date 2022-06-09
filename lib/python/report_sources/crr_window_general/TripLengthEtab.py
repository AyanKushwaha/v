"""
 $Header$

 Hotel Report. For more information, see ../include/Hotel.py
"""
import report_sources.include.TripLengthEtab
#reload(report_sources.include.TripLengthEtab)

from report_sources.include.TripLengthEtab import TripLengthEtab as Report

class TripLengthEtab(Report):
    
    def create(self):
        Report.create(self, 'output')
