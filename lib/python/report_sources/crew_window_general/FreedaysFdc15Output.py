"""
 $Header$

 Freeday FDC15 Statistics Report. For more information, see ../include/FreedaysFdc15.py
"""

from report_sources.include.FreedaysFdc15 import FreedaysFdc15 as Report

class FreedaysFdc15Output(Report):

    def create(self):
        Report.create(self, 'output')
