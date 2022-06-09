"""

 Report for Course and Office days distribution. For more information, see ../include/CourseOfficedayDistribution.py
"""

from report_sources.include.CourseOfficedayDistribution import CourseOfficedayDistribution as Report

class CourseOfficedayDistribution(Report):
 
    def create(self):
        Report.create(self, 'general')
