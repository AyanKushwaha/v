#

#
"""
Arrival Airports Output Report
"""

from report_sources.include.ArrivalAirportsOutput import ArrivalAirportsOutput as Report

class ArrivalAirportsOutput(Report):
 
    def create(self):
        Report.create(self)
