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
class Hotel(SASReport):
    my_region = ""
    my_cat = ""
    def headerRow(self, dates):
        tmpRow = self.getCalendarRow(dates,leftHeader='Rooms for',rightHeader='Tot')
        tmpCsvRow = self.getCalendarRow(dates,leftHeader='Rooms for',rightHeader='tot', csv=True)
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

    def convertToDict(self, duties):
        # Create a dictionary to hold the values from the planning period
        stopData = {}
        planning_group, type, = R.eval('planning_area.%trip_planning_group%', 'planning_area.%_crew_category%')
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, long_stop, short_stop, day_stop, stop_day, \
             stop_station, num_crew, num_of_days) in duties:
            # Build up dictionary to sum the number of stops of different types for each day in period
            # A duty always has either a long, short or day stop. There may be a duty free break inside a duty.
                       
            if day_stop:
                key = "day"
            elif short_stop:
                key = "short"
            elif long_stop:
                key = "long"
            else:
                key = "last_in_trip"
                
                
            if stop_station not in stopData.keys() and not key == "last_in_trip":
                stopData[stop_station] = stopData.get(stop_station, {})
                stopData[stop_station][type] = stopData[stop_station].get(type, {})
                stopData[stop_station][type][planning_group] = stopData[stop_station][type].get(planning_group, {})
                
                stopData[stop_station][type][planning_group]["short"] =stopData[stop_station].get("short", {})
                stopData[stop_station][type][planning_group]["long"] = stopData[stop_station].get("long", {})
                stopData[stop_station][type][planning_group]["day"] = stopData[stop_station].get("day", {})

            if not key == "last_in_trip":
                if key == "day":
                    stopData[stop_station][type][planning_group][key][stop_day] = stopData[stop_station][type][planning_group][key].get(stop_day,0)+num_crew
                else:
                    for numday in xrange(0, num_of_days):
                        stopData[stop_station][type][planning_group][key][AbsTime(stop_day + RelTime(numday * 24, 0))] = stopData[stop_station][type][planning_group][key].get(AbsTime(stop_day + RelTime(numday * 24, 0)),0)+num_crew
        return stopData
    
    def convertToTrackingDict(self, duties):
        # Create a dictionary to hold the values from the planning period
        stopData = {}
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        for (ix, hotel, stop_day, stop_station, num_crew, num_of_days, type, region) in duties:
            # Build up dictionary to sum the number of stops of different types for each day in period
            # A duty always has either a long, short or day stop. There may be a duty free break inside a duty.
            #print ix, hotel, stop_day, stop_station, num_crew, num_of_days, type, region
            key = hotel
            if stop_station not in stopData.keys():
                stopData[stop_station] = stopData.get(stop_station, {})

            if type  not in stopData[stop_station].keys():
                stopData[stop_station][type] = stopData[stop_station].get(type, {})

            if region not in stopData[stop_station][type].keys():
                stopData[stop_station][type][region] = stopData[stop_station][type].get(region, {})

            if hotel not in stopData[stop_station][type][region].keys():
                stopData[stop_station][type][region][hotel] = stopData[stop_station][type][region].get(hotel, {})

            for numday in xrange(0, num_of_days):
                tmpTime = AbsTime(stop_day + RelTime(numday * 24, 0))
                if self.timeInReportInterval(tmpTime):
                    stopData[stop_station][type][region][hotel][tmpTime] = stopData[stop_station][type][region][key].get(tmpTime,0)+num_crew
                else:
                    continue
        return stopData

    def timeInReportInterval(self, tmpDate):
        return True
    
    def getDates(self):
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start.day_floor()
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        return dates
    
    def getData(self, context):
        # build rave expression
        source, = R.eval('crg_hotel.%report_source_string%')
        duty_expr = R.foreach(
            R.iter('iterators.duty_set', where=('trip.%pp_days% > 0','trip.%has_only_flight_duty%')),
            'report_common.%is_long_duty_stop%',
            'report_common.%is_short_duty_stop%',
            'report_common.%is_hotel_day_stop% ',
            'report_common.%hotel_stop_day%',
            'report_common.%duty_stop_station%',
            'report_common.%num_crew%',
            'report_common.%hotel_num_nights%')

        duties, = R.eval(context, duty_expr)
        dataExists = False
        dataExists = (len(duties) > 0)
        if dataExists:
            return self.convertToDict(duties), dataExists, source
        else:
            return {}, dataExists, source

    def getTrackingData(self, context):
        # build rave expression
        duty_expr = R.foreach(
            R.iter('report_hotel.performed_layover_set_new',
                   where=('report_hotel.%has_layover_hotel_id%', 'report_hotel.%assigned_tot% > 0'),
                   sort_by=('report_hotel.%leg_end_hotel%',
                     'report_hotel.%next_leg_start_hotel%')),
            'report_hotel.%hotel_name%',
            'report_hotel.%arrival_day%',
            'report_hotel.%arr_flight_arr_stn%',
            'report_hotel.%assigned%',
            'report_hotel.%nights%',
            'report_hotel.%crew_type%',
            'report_hotel.%region%')

        duties, = R.eval(context, duty_expr)
        dataExists = False
        dataExists = (len(duties) > 0)
        if dataExists:
            return self.convertToTrackingDict(duties), dataExists, "Performed"
        else:
            return {}, dataExists, "Performed"

    def presentData(self, stopData, outputReport, dataExists, dates, source, tracking):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)
        samba_path = os.getenv("SAMBA", "/samba-share")
        sp_name, name, periodName, version, period = R.eval('crg_info.%plan_name%','global_sp_name', 'global_lp_name', 'global_fp_version', 'crg_info.%period%')
        if tracking:
            name, = R.eval('planning_area.%filter_company_p%')
        if source == "Planned":
            periodName = version
        elif source == "DB_Planned":
            periodName = period
        #print samba_path,raw,sp_name
        if outputReport:
            self.presentRawData(stopData, dataExists, dates, samba_path, sp_name, name, source, periodName)
        else:
            self.presentNormalData(stopData, outputReport, dataExists, dates)
        # Get Planning Period start and end

    def presentNormalData(self, stopData, outputReport, dataExists, dates):
        sumData = {}
                    
        # build report
        csvRows = []
        pdfRows = []
        stations = stopData.keys()
        
        if dataExists:    
            for station in stations:
                basePage = Column()
                # Add station name as title to block
                csvRows.append(station)
                basePage.add(Row(Text(station, font=self.HEADERFONT)))
                #Add column header with all dates in planning period
                hRow,hCsvRow = self.headerRow(dates)
                csvRows.append(hCsvRow)
                basePage.add(hRow)
                for type in stopData[station].keys():
                    for region in stopData[station][type].keys():
                        totSum = 0
                        for stop in ["long","short","day"]:
                            currentRow = Row()
                            # Add stop type as block row heading
                            if stop == "long":
                                csvRow = "Night rooms >= 14h"
                                currentRow.add(Text("Night rooms >= 14h", font=Font(weight=BOLD), border=border(right=0)))
                            elif stop == "short":
                                csvRow = "Night rooms < 14h"
                                currentRow.add(Text("Night rooms < 14h", font=Font(weight=BOLD), border=border(right=0)))   
                            else:
                                csvRow = "Day rooms"
                                currentRow.add(Text("Day rooms", font=Font(weight=BOLD), border=border(right=0)))
                            sum = 0
                            for date in dates:
                                try:
                                    tmp = stopData[station][type][region][stop][date]
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
                basePage.add(Text(" "))
                basePage.add(Text(" "))
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

    def presentDateForStopTypeAndStation(self, stopData, station, type, region, stopType, date, csvRows, sp_name, source):
        try:
            ## dateData     = stopData[station][stop][date]
            dateData = stopData[station][type][region][stopType][date]
            csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;" %(sp_name, station, stopType, formatDate(date), str(dateData), region, type, source))
        except:
            dateData = 0
            print "No data for %s;%s;%s;%s;%s;%s;%s;" %(sp_name, station, stopType, formatDate(date), region, type, source)
        #csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;" %(sp_name, station, stopType, formatDate(date), str(dateData), region, type, source))

        
    def presentStopTypeForRegionTypeAndStation(self, stopData, station, type, region, stopType, csvRows, sp_name, source, dates):
        #typeData = stopData[station][type][region][stopType]
        #dates = typeData.keys()
        for date in dates:
            self.presentDateForStopTypeAndStation(stopData, station, type, region, stopType, date, csvRows, sp_name, source)

    def presentRegionForTypeAndStation(self, stopData, station, type, region, csvRows, sp_name, source, dates):
        typeData = stopData[station][type][region]
        stopTypes = typeData.keys()
        for stopType in stopTypes:
            self.presentStopTypeForRegionTypeAndStation(stopData, station, type, region, stopType, csvRows, sp_name, source, dates)

    def presentTypeForStation(self, stopData, station, type, csvRows, sp_name, source, dates):
        typeData = stopData[station][type]
        regions = typeData.keys()
        for region in regions:
            self.presentRegionForTypeAndStation(stopData, station, type, region, csvRows, sp_name, source, dates)

    def presentStation(self, stopData, station, csvRows, sp_name, source, dates):
        stationData = stopData[station]
        stopTypes = stationData.keys()
        for type in stopTypes:
            self.presentTypeForStation(stopData, station, type, csvRows, sp_name, source, dates)

    def presentRawData(self, stopData, dataExists, dates, samba_path, sp_name, name, source, periodString = ""):
        # build report
        csvRows = []
        stations = stopData.keys()
        samba_path = os.getenv('SAMBA', samba_path)
        if dataExists:    
            for station in stations:
                self.presentStation(stopData, station, csvRows, sp_name, source, dates)
        else:
            csvRows.append("No trips")
        mypath = "%s/%s/%s_%s/" %(samba_path, 'reports/HotellPrognos', source, periodString)
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        if source == "Planned":
            timeStamp = ""
        else:
            timeStamp = str(datetime.now().date())
        reportName = "Hotel_Info_%s_%s-%s_%s" %(name , formatDateStr(dates[0]),formatDateStr(dates[len(dates)-1]),timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        for row in csvRows:
            csvFile.write(row + "\n")
        csvFile.close()
        self.add("The output data is saved in %s" %myFile)
    
    def create(self, reportType='pdf', context = CONTEXT, tracking = False):
        outputReport = (reportType == "output")
        if tracking:
            duties,dataExists, source  = self.getTrackingData(context)
        else:
            duties,dataExists, source  = self.getData(context)
        self.presentData(duties, outputReport, dataExists, self.getDates(), source, tracking)

# End of file
