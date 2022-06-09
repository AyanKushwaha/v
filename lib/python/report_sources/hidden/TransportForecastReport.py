#

#
"""
Hotel Forecast Report.
"""

import carmensystems.rave.api as R
from carmensystems.publisher.api import *
import os
import Cui
from AbsDate import AbsDate
from RelTime import RelTime
import hotel_transport.HotelBookingReportUtil as HU
import hotel_transport.TransportBookingData as T
from report_sources.include.SASReport import SASReport
from utils.selctx import BasicContext

"""
TransportForecastReport is used to create a transport forecast for a transport
company and a sas region for a given period.
"""
class TransportForecastReport(SASReport):

    def create(self):
        """
        Creates a TransportForecastReport.
        Uses HotelBookingData to retrieve some of the data needed
        for the report.
        """
        
        region = self.arg('REGION')
        transportId = self.arg('TRANSPORT')
        hotelId = self.arg('HOTEL')
        airportId = self.arg('AIRPORT')
        fromDate = AbsDate(self.arg('FROM_DATE'))
        toDate = AbsDate(self.arg('TO_DATE'))
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        
        studioRegion, = R.eval('planning_area.%filter_company_p%')
        correctionTerm, = R.eval('report_transport.%pick_up_time_correction%')
        isAllRegions = (studioRegion == 'ALL')
        
        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions)
                
        SASReport.create(self, 'Transport Forecast', showPlanData=False, 
                         margins=padding(10,15,10,15), headerItems=headerItemsDict)

        infoBox = HU.infoBox('Forecast Info', fromDate, toDate)
        hotelBox = HU.hotelBox(hotelId)
        customerBox = HU.customerBox(region,hotelId)

        # Add boxes to report
        self.add(Isolate(Row(Isolate(hotelBox),
                             Text(''),
                             Isolate(customerBox),
                             Text(''),
                             Isolate(infoBox))))

        self.add(Row(' '))

        # Create box to list rooms needed in period.
        bookingBox = Column(Row(Text('Reservations',
                                     colspan=3,
                                     font=Font(weight=BOLD))),
                            self.getTableHeader(('Date',
                                                 'Outgoing Flight',
                                                 'Departure',
                                                 'To Airport',
                                                 'Incoming Flight',
                                                 'Arrival',
                                                 'From Airport',
                                                 'Pick-Up',
                                                 'Crew'), aligns=(LEFT, RIGHT, RIGHT, LEFT, RIGHT, RIGHT, LEFT, RIGHT, LEFT)))

        bc = BasicContext()
        context = bc.getGenericContext()

        td = reload(T).TransportBookingManager(context).getPlanBookings(fromDate, transportId, hotelId, airportId, region, context, toDate+RelTime(24,0))
        color = False
        fromHotelCalendar = {}
        toHotelCalendar = {}
        def cmp(a,b):
            at = AbsDate(a.flightTime)
            bt = AbsDate(b.flightTime)
            if at < bt:
                return -1
            elif at > bt:
                return 1
            elif a.isHotelToAirport and not b.isHotelToAirport:
                return -1
            elif not a.isHotelToAirport and b.isHotelToAirport:
                return 1
            return 0 
        td.sort(cmp=cmp)
        prevDate = str(fromDate)
        for booking in td:
            if booking.crewAmount <= 0: continue
            color = not color
            if color:
                bgColor = 'dedede'
            else:                
                bgColor = 'ffffff'
            flightDate = str(AbsDate(booking.flightTime))
            if prevDate != flightDate:
                bookingBox.add(Row(Text('')))
            prevDate = flightDate
            outFlt, departure, toAirport, inFlt, arrival, fromAirport = ('','','','','','')
            pickUp = booking.pickUpTime
            
            if booking.isHotelToAirport:
                outFlt = booking.flightNr
                departure = booking.flightTime.time_of_day()
                toAirport = booking.flightDepStn
                fromHotelCalendar[flightDate] = fromHotelCalendar.get(flightDate, 0) + booking.crewAmount
            else:
                inFlt = booking.flightNr
                arrival = booking.flightTime.time_of_day()
                fromAirport = booking.flightArrStn
                toHotelCalendar[flightDate] = toHotelCalendar.get(flightDate, 0) + booking.crewAmount
            
            bookingBox.page()
                
            bookingBox.add(Row(Text('%s' % flightDate),
                               Text('%s' % outFlt, align=RIGHT),
                               Text('%s' % departure, align=RIGHT),
                               Text('%s' % toAirport),
                               Text('%s' % inFlt, align=RIGHT),
                               Text('%s' % arrival, align=RIGHT),
                               Text('%s' % fromAirport),
                               Text('%s' % (booking.pickUpTime.time_of_day()+correctionTerm), align=RIGHT),
                               Text('%s' % booking.crewAmount),
                               background= '#%s' % bgColor))


        self.add(bookingBox)

        calendarHeader = Row(Text(''), font=Font(weight=BOLD))
        calendarRow1 = Row(Text('Hotel->Airport'))
        calendarRow2 = Row(Text('Airport->Hotel'))
        totalNight = 0
        date = fromDate
        while date <= toDate:
            calendarHeader.add(Text('%2s' % date.split()[2], align=RIGHT))
            calendarRow1.add(Text('%s' % fromHotelCalendar.get(str(date), "-"), align=RIGHT))
            calendarRow2.add(Text('%s' % toHotelCalendar.get(str(date), "-"), align=RIGHT))
            
            date += RelTime(24, 0)

        calendarHeader.add(Text('Total'))
        calendarRow1.add(Text('%s' % sum(fromHotelCalendar.values()), align=RIGHT))
        calendarRow2.add(Text('%s' % sum(toHotelCalendar.values()), align=RIGHT))

        self.add(Row(' '))
        self.add(Isolate(Column(calendarHeader,
                                calendarRow1, calendarRow2,
                                border=border_all(1))))
    

def testReport():
    s,e=R.eval("fundamental.%pp_start%", "fundamental.%pp_end%")
    print s,e
    args = "REGION=SKN AIRPORT=SVG HOTEL=SVG1 TRANSPORT=SVG1 FROM_DATE=%s TO_DATE=%s FROMSTUDIO=TRUE" % (AbsDate(s),AbsDate(e))
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,Cui.CuiNoArea,'plan',"TransportForecastReport.py",0,args)
