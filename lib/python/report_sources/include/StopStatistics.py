"""
 $Header$
 
 Stop Statistics

 Counts the number of short and long stops for each base and stop station.
  
 Created:    August 2007
 By:         Anna Olsson, Jeppesen Systems AB

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
TITLE = 'Stop Statistics'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8

# Block Off
#Report shows one table for each base in the context

class StopStatistics(SASReport):

    # The report contains one table for each base showing the number of short and long stops
    # between duties for all stations with duty stops in the context.If there are no stops
    # at a station for the given base 0 is shown in the coresponding cell.
    # In addition a table for the total number of short and long stops, regardless of trip homebase,
    # at a station should be shown last in the report. 
    
    # Define headers for the tables
  
    def getTableHeader(self):
        return Row(font=Font(size=6, weight=BOLD), border=None, background=self.HEADERBGCOLOUR)
    
    def getHeaderRow(self, stations, leftHeader=None, rightHeader=None, csv=False, cols=1):
        if csv:
            tmpRow = ""
            if leftHeader:
                tmpRow = leftHeader
            for station in stations:
                tmpRow += ";"+station
            if rightHeader:
                tmpRow += ";"+rightHeader
        else:
            tmpRow = self.getTableHeader()
            if leftHeader:
                tmpRow.add(Text(leftHeader, colspan=cols))
            for station in stations:
                tmpRow.add(Text(station,align=RIGHT))
            if rightHeader:
                tmpRow.add(Text(rightHeader,align=RIGHT))
        return tmpRow

    def sumRow(self, data, stations):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        tmpCsvRow = "total"
        sum = 0
        for station in stations:
            tmp = data.get(station,0)
            sum += tmp
            tmpRow.add(Text(tmp,align=RIGHT))
            tmpCsvRow += ";" + str(tmp)
        tmpRow.add(Text(sum, border=border(left=0),align=RIGHT))
        tmpCsvRow += ";"+str(sum)
        return tmpRow,tmpCsvRow


    def create(self, reportType = "pdf"):
        outputReport = (reportType == "output")
        
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        # Create a dictionary to hold the values from the planning period
        stopData = {}
        dataExists = False
        
        # build rave expressions
        duty_expr = R.foreach(
            R.iter('iterators.duty_set', where='report_common.%has_stop_station%'),
            'trip.%homebase%',
            'report_common.%stop_station%',
            'report_common.%is_short_stop%')

        duties, = R.eval(CONTEXT, duty_expr)
        dataExists = (len(duties) > 0)

        usedStations = {}
        stopData = {}
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix,base,station,short_stop) in duties:
            usedStations[station] = True
            data = stopData
            data[base] = data.get(base, {})
            data[base]["short"] = data[base].get("short", {})
            data[base]["long"] = data[base].get("long", {})
            data[base]["Total"] = data[base].get("Total", {})

            if short_stop:
                key = "short"
            else:
                key = "long"
            data[base][key][station] = data[base][key].get(station,0)+1
            data[base]["Total"][station] = data[base]["Total"].get(station,0)+1
            
            #Add data for Summation table
            data["Total"] = data.get("Total", {})
            data["Total"]["short"] = data["Total"].get("short", {})
            data["Total"]["long"] = data["Total"].get("long", {})
            data["Total"]["Total"] = data["Total"].get("Total", {})
            data["Total"][key][station] = data["Total"][key].get(station,0)+1
            data["Total"]["Total"][station] = data["Total"]["Total"].get(station,0)+1

                 
        usedStationsSorted = usedStations.keys()
        usedStationsSorted.sort()
        
        # Build report            
        csvRows = []
        pdfRows = []
        bases = []
        for base in self.SAS_BASES:
            bases.append(base)
        bases.append("Total")
                    
        
        if dataExists:
            for base in bases:
                basePage = Column()
                addBase = False
              
                if (base in stopData):  #Create a table for the base.
                    addBase = True
                    
                    #Add table header
                    csvRows.append(base)
                    basePage.add(Row(Text(base, font=self.HEADERFONT)))
                    hRow = self.getHeaderRow(usedStationsSorted,leftHeader="Stations", rightHeader="Sum", csv=False)
                    hCsvRow = self.getHeaderRow(usedStationsSorted,leftHeader="Stations", rightHeader="Sum", csv=True)
                    csvRows.append(hCsvRow)
                    basePage.add(hRow)
                    
                    #Add vertrical header and data
                    totSum = 0 #Contains number of total stops for a base
                    for stop in ["short","long"]:
                        #Add vertical header
                        currentRow = Row()
                        if stop == "short":
                            tmpHeading = "Short stop, < 14h"
                        else:
                            tmpHeading = "Long stop, >= 14h"
                        csvRow = str(tmpHeading)
                        currentRow.add(Text(tmpHeading, font=Font(weight=BOLD), border=border(right=0)))
                            
                        #Print number of short/long stops 
                        sum = 0 #Contains number of short or long stops for a single base
                        for station in usedStationsSorted:
                            try:
                                tmp = stopData[base][stop][station]
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
                        
                    
                    sRow,sCsvRow = self.sumRow(stopData[base]["Total"],usedStationsSorted)
                    csvRows.append(sCsvRow)
                    basePage.add(sRow)
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
                self.page0()
                        
            
                        
             
# End of file
