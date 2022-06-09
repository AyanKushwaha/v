"""
 $Header$
 
 Lists information about short and long stops to be used for hotel and transport bookings
  
 Created:    February 2013
 By:         Niklas Johansson, STOOJ SAS

"""

# imports
import carmensystems.rave.api as R
import carmusr.SBHandler as sbh
from carmensystems.publisher.api import *

from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import os
import os.path
from datetime import datetime


# constants
CONTEXT = 'default_context'
TITLE = 'Hotel Info'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8
REGION = ""
CAT = ""
def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)
# Hotel
class StandbyDailyDistribution(SASReport):

    def getCompl(self):
        return {'FC': 1, 'FP': 2, 'AP': 5, 'AH': 7}

    
    def presentData(self, data, outputReport):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)
        for cat in data.categories:
            self.presentDataForCategory(data, cat, outputReport)

    def presentDataForCategory(self, data, cat, outputReport):
        self.add(Row(Text(cat)))
        for dtc in data:
            dateColumn = Column()
            self.presentDTC(dtc, dateColumn)
            # Add station name as title to block
    

    def presentDTC(self, dtc, cat, col):
        col.add(Row(Text("%s" %str(dtc.date))))
        col.add(Row(Text("%i" %str(dtc.getTotalNeedFor(cat)))))
        for tc in dtc:
            self.presentTC(tc, cat, col)
            
    def presentTC(self, tc, cat, col):
        col.add(Row(Text("%s" %str(tc.time))))
        col.add(Row(Text("%i" %str(tc.getComplementFor(cat)))))
        
    def create(self, reportType):
        outputReport = (reportType == "output")
        data  = sbh.getData()
        self.presentData(data, outputReport)

# End of file
