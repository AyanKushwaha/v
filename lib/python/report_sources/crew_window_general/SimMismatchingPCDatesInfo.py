"""

 Mismatching A3/A4 PC dates are listed. For more information, see ../include/SimMismatchingPCDatesInfo.py
"""

from report_sources.include.SimMismatchingPCDatesInfo import SimMismatchingPCDatesInfo as Report

class SimMismatchingPCDatesInfo(Report):

    def create(self):
        Report.create(self, 'general')
