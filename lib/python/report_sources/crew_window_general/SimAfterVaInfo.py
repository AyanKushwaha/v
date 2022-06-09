"""
 $Header$

Sim After Vacation Info Report. For more information, see ../include/SimAfterVaInfo.py
"""

from report_sources.include.SimAfterVaInfo import SimAfterVaInfo as Report

class SimAfterVaInfo(Report):

    def create(self):
        Report.create(self, 'general')
