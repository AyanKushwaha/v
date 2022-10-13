"""

 Mismatching A3/A4 LPC dates are listed. For more information, see ../include/SimMismatchingLPCDatesInfo.py
"""

from report_sources.include.SimMismatchingLPCDatesInfo import SimMismatchingLPCDatesInfo as Report

class SimMismatchingLPCDatesInfo(Report):

    def create(self):
        Report.create(self, 'general')
