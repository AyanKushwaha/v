"""
 $Header$

 Crew Warning Info Report. For more information, see ../include/CrewWarningInfo.py
"""
import interbids.rostering.reports.RequestReciept as RequestReciept
reload(RequestReciept)

from interbids.rostering.reports.RequestReciept import RequestReciept as Report



class rs_RequestReciept(Report):

    def create(self, crew_id=""):
        if not crew_id:
            crew_id = self.arg('crew_id')
        Report.create(self, 'general', crew_id)
