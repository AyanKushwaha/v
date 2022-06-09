"""
 $Header$

 Balance Distribution Report. For more information, see ../include/BalanceDistribution.py
"""

from report_sources.include.BalanceDistribution import BalanceDistribution as Report

class BalanceDistributionOutput(Report):
 
    def create(self):
        Report.create(self, output = 'csv')
