"""
 $Header$

Sim Missing Info Report. For more information, see ../include/SimMissingInfo.py
"""

from report_sources.include.SimMissingInfo import SimMissingInfo as Report

class SimMissingInfo(Report):

    def create(self):
        Report.create(self, 'general')
