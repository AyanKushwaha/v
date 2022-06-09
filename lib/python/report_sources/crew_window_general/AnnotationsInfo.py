"""
 $Header$

 Annotations Info Report. For more information, see ../include/NotesInfo.py
"""

from report_sources.include.NotesInfo import NotesInfo as Report

class AnnotationsInfo(Report):

    def create(self):
        Report.create(self, Report.TYPE_ANNOTATIONS)
