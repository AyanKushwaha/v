"""
 $Header$

 Blankday Distribution Report. For more information, see ../include/BlankdayDistribution.py
"""

from report_sources.include.BlankdayDistribution import BlankdayDistribution as Report

class BlankdayDistribution(Report):

    def create(self):
        Report.create(self, 'object')
