"""
 $Header$

 Resource Pool Info Report. For more information, see ../include/ResourcePoolInfo.py
"""

from report_sources.include.ResourcePoolInfo import ResourcePoolInfo as Report

class ResourcePoolInfo(Report):

    def create(self):
        Report.create(self)
