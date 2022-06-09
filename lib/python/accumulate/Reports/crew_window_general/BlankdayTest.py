"""
 $Header$

 Blankday Distribution Report. For more information, see ../include/BlankdayDistribution.py
"""

from report_sources.include.BlankdayTest import BlankdayTest as Report

class BlankdayTest(Report):

    def create(self):
        Report.create(self, 'general')
