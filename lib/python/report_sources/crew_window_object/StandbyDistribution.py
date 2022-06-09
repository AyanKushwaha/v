"""
 $Header$

 Standby Distribution Report. For more information, see ../include/StandbyDistribution.py
"""

from report_sources.include.StandbyDistribution import StandbyDistribution as Report

class StandbyDistribution(Report):

    def create(self):
        Report.create(self, 'object', context='marked_in_window_left')
