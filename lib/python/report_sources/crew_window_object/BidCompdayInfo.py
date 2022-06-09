"""
 $Header$

 Bid Compday Info Report. For more information, see ../include/BidCompdayInfo.py
"""

from report_sources.include.BidCompdayInfo import BidCompdayInfo as Report

class BidCompdayInfo(Report):
    
    def create(self):
        Report.create(self, 'object')
        
