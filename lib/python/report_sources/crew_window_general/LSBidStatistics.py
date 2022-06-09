"""
 $Header$

 Lifestyles & Bids Statistics Report. For more information, see ../include/LSBidStatistics.py

"""

from report_sources.include.LSBidStatistics import LSBidStatistics as Report


class LSBidStatistics(Report):

    def create(self):
        Report.create(self, 'general')
