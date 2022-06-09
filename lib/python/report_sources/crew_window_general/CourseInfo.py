"""
 $Header$

 Sim Dated Info Report. For more information, see ../include/SimDatedInfo.py
"""

from report_sources.include.CourseInfo import CourseInfo as Report

class CourseInfo(Report):
 
    def create(self):
        Report.create(self)
