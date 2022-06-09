"""
 $Header$

 Compday Distribution Report. For more information, see ../include/CompdayDistribution.py
"""

from report_sources.include.SimAssignmentDistribution import SimAssignmentDistribution as Report

class SimAssignmentDistribution(Report):
 
    def create(self):
        Report.create(self, 'general')
