"""
 $Header$

PGT Missing Info Report. For more information, see ../include/PGTMissingInfo.py
"""

from report_sources.include.PGTMissingInfo import PGTMissingInfo as Report

class PGTMissingInfo(Report):

    def create(self):
        Report.create(self, 'general')
