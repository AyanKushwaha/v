"""
 $Header$

 Production Distribution Report. For more information, see ../include/ProductionDistribution.py
"""

from report_sources.include.ProductionDistribution import ProductionDistribution as Report

class ProductionDistributionOutput(Report):
 
    def create(self):
        Report.create(self, outputType = 'csv', allCrew=False)
