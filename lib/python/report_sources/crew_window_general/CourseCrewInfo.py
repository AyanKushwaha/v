"""
 $Header$

 Sim Dated Info Report. For more information, see ../include/SimDatedInfo.py
"""

from report_sources.include.CourseInfo import CourseCrewInfo as Report

class CourseCrewInfo(Report):
 
    def create(self):
        Report.create(self)

