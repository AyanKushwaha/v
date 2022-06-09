from report_sources.include.ProductionDaysInfo import  ProductionDaysInfo as Report

class ProductionDaysInfoOutput(Report):
    
    def create(self):
        Report.create(self, outputType='csv')
        
