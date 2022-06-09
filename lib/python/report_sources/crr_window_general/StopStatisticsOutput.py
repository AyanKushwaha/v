"""
 $Header$

 Stop Statistics Output Report. For more information, see ../include/StopStatistics.py
"""

import report_sources.include.StopStatistics
#reload(report_sources.include.StopStatistics)


from report_sources.include.StopStatistics import StopStatistics as Report

class StopStatisticsOutput(Report):
 
    def create(self):
        Report.create(self,"output")
