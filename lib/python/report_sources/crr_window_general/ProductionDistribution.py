"""
 $Header$

 Production Distribution Report. For more information, see ../include/ProductionDistribution.py
"""

from report_sources.include.ProductionDistribution import ProductionDistribution as Report

class ProductionDistribution(Report):
 
    def create(self):
        Report.create(self, outputType='standard', allCrew=True)

