"""
 $Header$
 
 Trip Distribution

 Lists the number of trips of every length (days) in pp.
  
 Created:    December 2006
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants
CONTEXT = 'default_context'
TITLE = 'Trip Distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

# Trip Distribution
class TripDistribution(SASReport):
    def headerRow(self, dates):
        tmpRow = self.getCalendarRow(dates,leftHeader='Days',rightHeader='Sum')
        tmpCsvRow = self.getCalendarRow(dates,leftHeader='days',rightHeader='sum', csv=True)
        return tmpRow, tmpCsvRow

    def sumRow(self, data, dates):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        tmpCsvRow = "total"
        sum = 0
        for date in dates:
            tmp = data.get(date,0)
            sum += tmp
            tmpRow.add(Text(tmp,align=RIGHT))
            tmpCsvRow += ";" + str(tmp)
        tmpRow.add(Text(sum, border=border(left=0),align=RIGHT))
        tmpCsvRow += ";"+str(sum)
        return tmpRow,tmpCsvRow
    
    def create(self, reportType):
        self.modify_pp()
        outputReport = (reportType == "output")
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        # Get Planning Period start and end
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        
        # Create a dictionary to hold the values from the planning period
        fltData = {}
        sbyData = {}
        dataExists = False

        # build rave expression
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where=('trip.%pp_days% > 0','trip.%has_only_flight_duty%')),
            'trip.%is_standby%',
            #'trip.%has_only_flight_duty%',
            'trip.%start_day%',
            'report_common.%trip_days%',
            'trip.%homebase%',
            'crew_pos.%trip_assigned%',            
            )

        trips, = R.eval(CONTEXT, trip_expr)
        dataExists = (len(trips) > 0)

        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, is_standby, startdate, days, base, crew) in trips:
            for base in (base,"Total"):
                # Only do something if the current bag corresponds to a day
                # in the planning period and is a flight duty or standby
                if is_standby:
                    data = sbyData
                else:
                    data = fltData
                data[base] = data.get(base, {})
                data[base][days] = data[base].get(days, {})
                data[base]["Total"] = data[base].get("Total", {})
                try:
                    data[base][days][startdate] = data[base][days].get(startdate,0) + crew
                    for day in range(days):
                        date = startdate + RelTime(day*24,0)
                        data[base]["Total"][date] = data[base]["Total"].get(date,0) + crew
                except:
                    print "Error "+str(date) + " " + days + "-days trip"
            
        # build report
        csvRows = []
        pdfRows = []
        bases = []
        for base in self.SAS_BASES:
            bases.append(base)
        if (max(len(fltData),len(sbyData)) > 2):
            # Print total
            bases.append("Total")
            
        if dataExists:    
            for base in bases:
                basePage = Column()
                addBase = False
                for data in (fltData, sbyData):
                    if (base in data):
                        addBase = True
                        if (data == fltData):
                            blockHeader = "Flight-duties"
                        else:
                            blockHeader = "Standby-duties"
                        csvRows.append(base +", " + blockHeader)
                        basePage.add(Row(Text(base + ", " + blockHeader, font=self.HEADERFONT)))
                        hRow,hCsvRow = self.headerRow(dates)
                        csvRows.append(hCsvRow)
                        basePage.add(hRow)
                        totSum = 0
                        for rdays in range(7):
                            days = rdays+1
                            currentRow = Row()
                            csvRow = str(days)
                            currentRow.add(Text(days, font=Font(weight=BOLD), border=border(right=0)))
                            sum = 0
                            for date in dates:
                                try:
                                    tmp = data[base][days][date]
                                except:
                                    tmp = 0
                                currentRow.add(Text(tmp,align=RIGHT))
                                csvRow += ";"+str(tmp)
                                sum += tmp
                            totSum += sum
                            currentRow.add(Text(sum, font=Font(weight=BOLD), align=RIGHT, border=border(left=0)))
                            csvRow += ";" + str(sum)
                            csvRows.append(csvRow)
                            basePage.add(currentRow)
                            
                        sRow,sCsvRow = self.sumRow(data[base]["Total"],dates)
                        csvRows.append(sCsvRow)
                        basePage.add(sRow)
                        basePage.add(Row(Text("The Total row counts production days iso trip starts", font = Font(size=6))))
                        basePage.add(Text(" "))
                        basePage.add(Text(" "))
                if addBase:
                    pdfRows.append(Row(basePage))
                
        else:
            csvRows.append("No trips")
            pdfRows.append(Row("No trips"))
        if outputReport:
            self.set(font=Font(size=14))
            csvObject = OutputReport(TITLE, self, csvRows)
            self.add(csvObject.getInfo())
        else:
            for row in pdfRows:
                self.add(row)
                self.page()
        self.reset_pp()

# End of file
