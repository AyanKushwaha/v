"""
 $Header$

 Hotel Report. For more information, see ../include/Hotel.py
"""
import report_sources.include.Hotel
#reload(report_sources.include.Hotel)
from report_sources.include.Hotel import Hotel as Report

class HotelOutput(Report):
 
    def create(self):
        Report.create(self, 'output')
