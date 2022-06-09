"""
 $Header$

 Freedays FDC15 Report. For more information, see ../include/FreedaysFdc15.py
"""

from report_sources.include.Fdc15General import Fdc15General as Report

class Fdc15General(Report):

    def create(self):
        Report.create(self, 'pdf')
