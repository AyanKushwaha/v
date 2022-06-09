"""
 $Header$
 
 Lists information about short and long stops to be used for hotel and transport bookings
  
 Created:    February 2013
 By:         Niklas Johansson, STOOJ SAS

"""

# imports
#import carmensystems.rave.api as R
import carmusr.ground_duty_handler as gdh
import carmusr.SBHandler as sbh
from carmensystems.publisher.api import *

from report_sources.include.SASReport import SASReport
#from report_sources.include.ReportUtils import OutputReport
#from AbsDate import AbsDate
#from AbsTime import AbsTime
#from RelTime import RelTime
#import os
#import os.path
#from datetime import datetime


# constants
CONTEXT = 'default_context'
#CONTEXT = 'sp_crrs'
TITLE = 'Standby daily distribution'
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
##        gtps = []
##         for dtc in data:
##             for sba in dtc.SBAssignments:
##                 if sba.isActive and not sba.exists:
##                     gtps.append(sba.gtp)
        for cat in data.categories:
            self.presentDataForCategory(data, cat, outputReport)
            self.page()
##        gdh.create_ground_duty_list_func(gtps)

    def presentDataForCategory(self, data, cat, outputReport):
        self.add(Row(Text(cat)))
        iter = 0
        for dtc in data:
            if (iter % 5 == 0):
                row = Row()
                self.add(row)
                self.page0()
            dateColumn = Column()
            self.presentDTC(dtc, cat, dateColumn)
            row.add(dateColumn)
            iter+=1
            # Add station name as title to block
    

    def presentDTC(self, dtc, cat, col):
        col.add(Row(Text("%s" %str(dtc.date))))
        col.add(Row(Text("mt:%s" %str(dtc.maxTime))))
        try:
            col.add(Row(Text("Need: %i" %dtc.getTotalNeedFor(cat))))
            col.add(Row(Text("Assi: %i" %dtc.getTotAssignedFor(cat))))
        except Exception as e:
            print "Error tn: cat:%s, date:%s dtc: %s" %(cat, str(dtc.date),  str(e))#str(dtc))
        try:
            col.add(Row(Text("Comp: %i" %dtc.getTotalCompFor(cat))))
            col.add(Row(Text("uc: %i lc: %i" %(dtc.upperReduction, dtc.lowerReduction))))
        except Exception as e:
            print "Error tc: cat:%s, date:%s dtc: %s" %(cat, str(dtc.date), str(e))#str(dtc))
        row = Row()
        legCol = Column()
        sbCol = Column()
        for tc in dtc:
            if (tc.getComplementFor(cat) > 0):
                self.presentTC(tc, cat, legCol)
        for sba in sorted(dtc.SBAssignments):
            if sba.isActiveForCat(cat):
                self.presentSBA(sba, cat, sbCol)
        row.add(legCol)
        row.add(sbCol)
        col.add(row)
            
    def presentTC(self, tc, cat, col):
        col.add(Row(Text("%s" %str(tc.time.time_of_day()))))
        col.add(Row(Text("%i u:%i l:%i" %(tc.getComplementFor(cat), tc.upperRestComplement, tc.lowerRestComplement))))

    def presentSBA(self, sba, cat, col):
        col.add(Row(Text("%s:%s-%s" %(sba.code, str(sba.startTime), str(sba.endTime)))))
        col.add(Row(Text("%s" %(sba.sb_info))))
        col.add(Row(Text("c:%i u:%i l:%i" %(sba.getComplementFor(cat), sba.upperRestComplement, sba.lowerRestComplement))))
     
    def create(self, reportType):
        outputReport = (reportType == "output")
        data,_,_  = sbh.getData(CONTEXT)
        self.presentData(data, outputReport)

# End of file
