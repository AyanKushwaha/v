"""
 $Header$

 Compday Distribution Report. For more information, see ../include/CompdayDistribution.py
"""

from report_sources.include.CompdayDistribution import CompdayDistribution as Report

class CompdayDistribution(Report):
 
    def create(self):
        Report.create(self, 'object')
