"""
 $Header$

 Pattern Conflict Info Report. For more information, see ../include/PatternConflictInfo.py
"""

from report_sources.include.PatternConflictInfo import PatternConflictInfo as Report

class PatternConflictInfo(Report):

    def create(self):
        Report.create(self)
