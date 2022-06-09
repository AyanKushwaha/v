"""
 $Header$

 Bid Sim Conflict Info Report. For more information, see ../include/BidSimConflictInfo.py
"""

from report_sources.include.BidSimConflictInfo import BidSimConflictInfo as Report

class BidSimConflictInfo(Report):

    def create(self):
        Report.create(self, 'general')
