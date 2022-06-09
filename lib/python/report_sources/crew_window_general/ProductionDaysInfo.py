from report_sources.include.ProductionDaysInfo import  ProductionDaysInfo as Report

class ProductionDaysInfo(Report):
    
    def create(self):
        Report.create(self, outputType='general')
        
