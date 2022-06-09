"""
 $Header$

 Standby Line Distribution Report. For more information, see ../include/StandbyLineDistribution.py
"""

from report_sources.include.StandbyLineDistribution import StandbyLineDistribution as Report

class StandbyLineDistribution(Report):

    def create(self):
        Report.create(self, 'general')
