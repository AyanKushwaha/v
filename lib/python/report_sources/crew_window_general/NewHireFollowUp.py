"""
 $Header$

 New Hire Follow Up Report. For more information, see ../include/NewHireFollowUp.py
"""

from report_sources.include.NewHireFollowUp import NewHireFollowUp as Report

class NewHireFollowUp(Report):
 
    def create(self):
        Report.create(self)
