#

#
"""
BCS Report
"""
import report_sources.include.BCS
#reload(report_sources.include.BCS)

from report_sources.include.BCS import BCS as Report

class BCS(Report):
 
    def create(self):
        Report.create(self, scope='trip_general', context='default_context')
