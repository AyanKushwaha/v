#######################################################

# report.py
# -----------------------------------------------------
# 
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
This module contains functionality for creating crg reports
in python.
"""
from application import application

if application=="Matador":
    import carmstd.matador.report as report
else:
    import carmstd.studio.report as report


class Report:
    """
    Ex:
    Report('CrewValues.output').saveAs('$CARMUSR/ETABLES/CrewValues.etab')
    """
    def __init__(self,filePath, area=None, scope=None):
        """
        filePath: Name of the report to generate (current directory is crg/hidden)
        """
        self.filePath=filePath
        self.area = area
        self.scope = scope

    def save(self,outPath,format="ascii"):
        """
        Generates and saves a report

        filePath: Filepath where to store it
        format: What format to use ['ascii','pdf']
        """
        print "report.Report('%s').save(%s,%s)" % (self.filePath, outPath, format)
        report.saveReport(self.filePath,outPath,format, self.area, self.scope)
