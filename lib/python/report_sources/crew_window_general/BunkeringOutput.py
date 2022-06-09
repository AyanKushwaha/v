from report_sources.include.Bunkering import Bunkering as Report


class BunkeringOutput(Report):
    def create(self):
        Report.create(self, outputType='csv')
