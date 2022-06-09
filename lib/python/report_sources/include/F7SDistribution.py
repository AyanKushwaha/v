"""
 $Header$
 
 F7S Distribution

 Lists the number of F7S days for each day in pp,
 separated by category (and total sum).
  
 Created:    January 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from RelTime import RelTime

# constants
CONTEXT = 'default_context'
TITLE = 'F7S Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

# F7S Distribution
class F7SDistribution(SASReport):
    def headerRow(self, dates):
        tmpRow = self.getCalendarRow(dates,leftHeader='Category', cols=2)
        tmpCsvRow = self.getCalendarRow(dates,leftHeader='category', csv=True)
        return tmpRow, tmpCsvRow

    # If sum row is needed, check for example TripDistribution.py
    
    def create(self, reportType):
        self.modify_pp()
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        
        # Get Planning Period start and end
        pp_start,pp_end,pp_days,f7sQuota = R.eval('fundamental.%pp_start%','fundamental.%pp_end%','pp.%days%','report_common.%f7s_percentage_p%')
        
        # pp_days = int((pp_end-pp_start)/RelTime(24,0))

        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
            
        # Ranks in use
        ranksInUse = "FC","FP","FR","AH","AS","AP"
        quals = "SH","LH"
        subCats = "crew","assigned","remain"
        
        # Build rave expression and evaluate
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where=('trip.%code% = "F7S"','trip.%pp_days% > 0')),
            'trip.%start_day%',
            'trip.%end_day%',
            'crew.%is_long_haul_trip_start%',
            )
        day_expr = R.foreach(
            R.times(pp_days),
            'report_common.%date_ix%',
            'report_common.%crew_is_long_haul_ix%',
            'report_common.%crew_part_time_factor_ix%'
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'crew.%surname%',
            'crew.%firstname%',
            'crew.%employee_number%',
            'crew.%id%',
            'crew.%rank%',
            day_expr,
            trip_expr,
            )
        rosters, = R.eval(CONTEXT, roster_expr)
        
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        data = {}
        totalCrew = 0
        totalCrewFTE = 0
        for (ix,surname,firstname,empno,crewid,rank,dayData,trips) in rosters:
            totalCrew += 1
            totParttime = 0
            for (dateIndex,date,longHaulAtDate,parttimeAtDate) in dayData:
                totParttime += parttimeAtDate
                #dateIndex = int(str(dateIndex))
                #date = pp_start + RelTime((dateIndex-1)*24,0)
                if (longHaulAtDate):
                    category = rank+" LH"
                else:
                    category = rank+" SH"
                if (category in ["AS SH", "AH SH"]):
                    category = "AS/AH SH"
                if not (category in data):
                    data[category] = {}
                    for subCat in subCats:
                        data[category][subCat] = {}
                data[category]["crew"][date] = data[category]["crew"].get(date,0) + parttimeAtDate
            avParttime = totParttime/pp_days
            totalCrewFTE += avParttime
            for (ix,startDate,endDate,crewIsLongHaul) in trips:
                date = startDate
                while (date <= endDate):
                    data[category]["assigned"][date] = data[category]["assigned"].get(date,0) + 1
                    date += RelTime(24,0)

        # Build report
        csvRows = []
        pdfRows = []
        csvRows.append("Crew tot;"+str(totalCrew)+";fte;"+str(totalCrewFTE/100))
        pdfRows.append(Row("Crew tot/fte: "+str(totalCrew)+"/"+str(totalCrewFTE/100)+". All values are based on FTE"))
        hRow,hCsvRow = self.headerRow(dates)
        csvRows.append(hCsvRow)
        pdfRows.append(hRow)
        # this makes sure that we get the categories in the order WE want them
        catBorder = None
        asahprinted = False
        for rank in ranksInUse:
            for qual in quals:
                category = rank+" "+qual
                if (category in ["AS SH", "AH SH"]):
                    category = "AS/AH SH"
                    if (asahprinted):
                        continue
                    else:
                        asahprinted = True
                if (category in data):
                    categoryRow = Row(border=catBorder)
                    if not catBorder:
                        catBorder = border(top=0)
                    categoryRow.add(self.getTableHeader((category,), vertical=True))
                    categoryRow.add(self.getTableHeader(subCats, vertical=True))
                    dataColumn = Column(border=border(left=0))
                    crewRow = Row()
                    assignedRow = Row()
                    remainRow = Row()
                    crewRowCsv = category+", crew (fte)"
                    assignedRowCsv = category+", assigned"
                    remainRowCsv = category+", remain"
                    for date in dates:
                        crewRaw = data[category]["crew"].get(date,0)
                        crew = crewRaw/100
                        assigned = data[category]["assigned"].get(date,0)
                        toAssign = (f7sQuota * crewRaw)/10000
                        remain = toAssign - assigned
                        # Pdf rows
                        crewRow.add(Text(crew,align=RIGHT))
                        assignedRow.add(Text(assigned,align=RIGHT))
                        remainRow.add(Text(remain,align=RIGHT))
                        # Csv rows
                        crewRowCsv += ";"+str(crew)
                        assignedRowCsv += ";"+str(assigned)
                        remainRowCsv += ";"+str(remain)
                    dataColumn.add(crewRow)
                    dataColumn.add(assignedRow)
                    dataColumn.add(remainRow)
                    csvRows.append(crewRowCsv)
                    csvRows.append(assignedRowCsv)
                    csvRows.append(remainRowCsv)
                    
                    categoryRow.add(dataColumn)
                    pdfRows.append(categoryRow)
        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, csvRows)
            self.add(csvObject.getInfo())
        else:
            for row in pdfRows:
                self.add(row)

        self.reset_pp()

# End of file
