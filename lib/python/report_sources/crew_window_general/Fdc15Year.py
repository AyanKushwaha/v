"""
 $Header$

 Yeardays FDC15 Report. For more information, see ../include/Fdc15Year.py
"""

from report_sources.include.Fdc15Year import Fdc15Year as Report

class Fdc15Year(Report):

    def create(self):
        Report.create(self, 'pdf')
