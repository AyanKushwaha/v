"""
 $Header$
 
 Hotel

 Lists information about short and long stops to be used for hotel and transport bookings
  
 Created:    September 2007
 By:         Anna Olsson, Jeppesen Systems AB

Changed by Niklas Johansson STOOJ Feb2013 Major change
"""

# imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import os
import os.path
from datetime import datetime
from tm import TM

# constants
CONTEXT = 'default_context'
TITLE = 'Trip Lengths'
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
class TripLengthEtab(SASReport):

    
    def getData(self, context):
        # build rave expression
        trip_expr = R.foreach(
            R.iter('studio_sb_handling.sb_trip_length_date_set',
                   where=('studio_sb_handling.%consider_trip_for_sb_calculation%'),
                   sort_by = ('trip.%start_base%', 'trip.%start_scheduled_day%', 'trip.%days%')
                   ),
            'trip.%start_base%',
            'trip.%start_scheduled_day%',
            'trip.%days%',
            R.foreach(R.times(12),
            'studio_sb_handling.%assigned_cat_name_ix%',
            'studio_sb_handling.%tot_no_assigned_for_pos_ix%'),
            )

        trips, = R.eval(context, trip_expr)
        dataExists = False
        dataExists = (len(trips) > 0)
        return trips, dataExists
        

    def presentData(self, data, outputReport, dataExists):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)
        etab_name, = R.eval('sb_handling.%sb_daily_length_table_p%')
        etab_path = "%s/%s/%s" %(os.environ['CARMDATA'], 'ETABLES', etab_name)
        
        self.presentRawData(data, dataExists, etab_path)

    def initEtabList(self):
        etabRows = []
        etabRows.append("5")
        etabRows.append("SBase,")
        etabRows.append("ASBdate,")
        etabRows.append("SCat,")
        etabRows.append("ILength,")
        etabRows.append("INoStarts,")
        return etabRows
        
    def presentRawData(self, data, dataExists, etab_path):
        # build report
        etabRows = self.initEtabList()
        if dataExists:    
            for (ix, base, date, days, _comp) in data:
                self.presentComp(base, date, days, _comp, etabRows)
        csvFile = open(str(etab_path), "w")
        for row in etabRows:
            csvFile.write(row + "\n")
        csvFile.close()
        self.add("The output data is saved in %s" %etab_path)
        
    def presentDateForCat(self, base, date, days, cat, no_assigned, csvRows):
        try:
            ## dateData     = stopData[station][stop][date]
            csvRows.append("\"%s\",%s,\"%s\",%s,%s," %(base, formatDateStr(date), cat, days, no_assigned))
        except:
            dateData = 0
            print "No data for %s;%s;%s;%s;%s;%s;" %(base, str(date), cat, days, no_assigned, str(csvRows))

        
    def presentComp(self, base, date, days, _comp, csvRows):
        #typeData = stopData[station][type][region][stopType]
        #dates = typeData.keys()
        for (ix, cat, no_assigned) in _comp:
            if (no_assigned > 0):
                self.presentDateForCat(base, date, days, cat, no_assigned, csvRows)
    
    def create(self, reportType, context = CONTEXT):
        ## activity_grp = TM.activity_group["SBH"]
##         activity = TM.activity_set.create(("RT"))
##         activity.grp = activity_grp
##         activity.si = "tailored SB"
##         start = AbsTime(1986,1,1, 0, 0)
##         end = AbsTime(2036,12,31, 0, 0)
##         ap = TM.activity_set_period.create((activity, start))
##         ap.validto = end
        outputReport = (reportType == "output")
        duties,dataExists = self.getData(context)
        self.presentData(duties, outputReport, dataExists)

# End of file
