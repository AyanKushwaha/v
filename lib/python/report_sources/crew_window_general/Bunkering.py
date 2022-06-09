from report_sources.include.Bunkering import Bunkering as Report


class Bunkering(Report):
    def create(self):
        Report.create(self, outputType='general')
