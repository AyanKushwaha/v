#

#
"""
Transport Performed Report.
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as R
from tempfile import mkstemp
from AbsDate import AbsDate
from RelTime import RelTime
from utils.divtools import default as D
import carmstd.cfhExtensions
import hotel_transport.HotelBookingReportUtil as HU
import hotel_transport.TransportBookingData as T
from report_sources.include.SASReport import SASReport
from tm import TM
from utils.selctx import BasicContext
from utils.divtools import fd_parser, fd_pre_parse_sanitize, fd_post_parse_prettify

def save(args):
    """
    Creates a transport performed report.
    arg0 region
    arg1 transport
    arg2 hotel
    arg3 airport
    arg4 fromDate
    arg5 toDate
    """
    (fd, fileName) = mkstemp(suffix='.pdf',
                             prefix='TransportPerformed',
                             dir=T.getExportDir(),
                             text=True)

    region = 'REGION=%s' % args[0]
    transport = 'TRANSPORT=%s' % args[1]
    airport = 'AIRPORT=%s' % args[2]
    hotel = 'HOTEL=%s' % args[3]
    fromDate = 'FROM_DATE=%s' % args[4]
    toDate = 'TO_DATE=%s' % args[5]
    args = ' '.join([region, transport, hotel, airport, fromDate, toDate])
    
    print "TransportPerformedReport.save args:", args

    return generateReport('report_sources.hidden.TransportPerformedReport',
                          fileName,
                          PDF,
                          args)

"""
TransportPerformedReport is used to create a transport performed report for a region,
transport and for a given period.
"""
class TransportPerformedReport(SASReport):

    def create(self):
        """
        Creates a TransportPerformedReport.
        Uses TransportBookingData to retrieve some of the data needed
        for the report.
        """
        region = self.arg('REGION')
        transportId = self.arg('TRANSPORT')
        airportId = self.arg('AIRPORT')
        hotelId = self.arg('HOTEL')
        fromDate = AbsDate(self.arg('FROM_DATE'))
        fromDateAbsTime = AbsTime(fromDate)
        toDate = AbsDate(self.arg('TO_DATE'))
        toDateAbsTime = AbsTime(toDate)
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        
        studioRegion, = R.eval('planning_area.%filter_company_p%')
        correctionTerm, = R.eval('report_transport.%pick_up_time_correction%')
        isAllRegions = (studioRegion == 'ALL')
        
        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions)
             
        SASReport.create(self, 'Transport Performed', False, 
                         margins=padding(10,15,10,15), headerItems=headerItemsDict)

        diffDays = int((toDate - fromDate)/RelTime(24,0)) + 1

        infoBox = HU.infoBox('Performed Info',
                             formatDate(fromDate),
                             formatDate(toDate))
        transportBox = HU.transportBox(transportId)
        hotelBox = HU.hotelBox(hotelId)
        customerBox = HU.customerBox(region,hotelId)

        # Add boxes to report
        self.add(Isolate(Row(Isolate(transportBox),
                             Text(''),
                             Isolate(hotelBox),
                             Text(''),
                             Isolate(customerBox),
                             Text(''),
                             Isolate(infoBox))))
        self.add(Row(' '))

        # now we get the bookings from the plan, and separate them into
        # 'from hotel to airport' (bookingsHA) and
        # 'from airport to hotel' (bookingsAH) transport types
        (bookings, ccCalendar, fcCalendar) = self.getBookings(
            fromDate, toDate, region, transportId, hotelId, airportId)
        (bookingsHA, bookingsAH) = self.separateBookings(bookings,fromDate,toDate)

        color = True
        prevFormatDayHA = None
        prevFormatDayAH = None
        
        if not len(bookings)>0:
            self.add(Row(Text("No performed bookings from %s to %s" % (
                fromDate, toDate),
                font=Font(weight=BOLD))))
            return
        
        for i in xrange(diffDays):
            bookingBox = Column(Row(Column(Row(
                self.getTableHeader(('Company',
                                     'Flight',
                                     'Local Time',
                                     'Pick Up',
                                     'No of Crew',
                                     'Airport'),
                                     aligns=[CENTER,CENTER,CENTER,
                                             CENTER,CENTER,CENTER],
                                     widths=[5,5,10,10,5,5])),
                                           width=300),
                                    Column(width=350)))
            
            bookings = bookingsHA[diffDays - i -1]

            if len(bookings) > 0:
                for booking in bookings:
                    color = not color
                    
                    bookingBox.page()
                    
                    bookingHA = booking[0]
                    formatDayHA = booking[1]

                    flightTime = str(bookingHA.flightTime)[10:]
                    pickUpTime = str(bookingHA.pickUpTime+correctionTerm)[10:]
                    
                    # Note that flightNr is the leg key. This is ok as long as we don't 
                    # present flight suffix. The suffix to use for presentation is origsuffix 
                    # which may differ from the key suffix e.g. when flights are diverted.

                    bookingHA.flightNr = fd_pre_parse_sanitize(bookingHA.flightNr)
                    fd = fd_parser(bookingHA.flightNr)
                    flightNr = fd_post_parse_prettify('%s %04d' % (fd.carrier, int(fd.number)))

                    if not prevFormatDayHA or formatDayHA != prevFormatDayHA:
                        bookingBox.add(Isolate(Row(
                            Text(formatDayHA, font=Font(weight=BOLD)),
                            Text("- From Hotel to Airport:", font=Font(style=ITALIC)),
                            Text("Departure Flights", font=Font(style=ITALIC)))))
                        color = True
                    prevFormatDayHA = formatDayHA
                
                    if color:
                        bgColor = 'dedede'
                    else:                
                        bgColor = 'ffffff'

                    bookingBox.add(Row(Column(Row(
                        Text('%s' % bookingHA.region, align=CENTER),
                        Text('%s' % flightNr, align=CENTER),
                        Text('%s' % flightTime, align=CENTER),
                        Text('%s' % pickUpTime, align=CENTER),
                        Text('%s' % bookingHA.crewAmount, align=CENTER),
                        Text('%s' % bookingHA.flightDepStn, align=CENTER),
                        background='#%s' % bgColor)),
                                       Column()))
                    
                    bookingBox.page()
                                   

            else:
                bookingBox.add(Row(Isolate(Column(Row(
                    Text("%s" % formatDay(fromDateAbsTime.adddays(i)),
                         font=Font(weight=BOLD)),
                    Text("- From Hotel to Airport:", font=Font(style=ITALIC)),
                    Text("Departure Flights", font=Font(style=ITALIC))),
                    Column()))))
                bookingBox.page()
                bookingBox.add(Row(Column(Row(
                    Text("  - No Reservations", colspan=6)),
                    background="#dedede"),
                    Column()))
                bookingBox.page()
                
            color = True
            bookings = bookingsAH[diffDays - i -1]

            if len(bookings) > 0:
                for booking in bookings:
                    color = not color

                    bookingAH = booking[0]
                    formatDayAH = booking[1]

                    if not prevFormatDayAH or formatDayAH != prevFormatDayAH:
                        bookingBox.add(Isolate(
                            Row(Text(formatDayAH, font=Font(weight=BOLD)),
                                Text("- From Airport to Hotel:", font=Font(style=ITALIC)),
                                Text("Arrival Flights", font=Font(style=ITALIC)))))
                        color = True
                    prevFormatDayAH = formatDayAH
                    
                    bookingBox.page()

                    flightTime = str(bookingAH.flightTime)[10:]
                    pickUpTime = str(bookingAH.pickUpTime+correctionTerm)[10:]
                    
                    # same as with bookingHA
                    bookingAH.flightNr = fd_pre_parse_sanitize(bookingAH.flightNr)
                    fd = fd_parser(bookingAH.flightNr)
                    flightNr = fd_post_parse_prettify('%s %04d' % (fd.carrier, int(fd.number)))
                    
                    if color:
                        bgColor = 'dedede'
                    else:                
                        bgColor = 'ffffff'

                    bookingBox.add(Row(Column(Row(
                        Text('%s' % bookingAH.region, align=CENTER),
                        Text('%s' % flightNr, align=CENTER),
                        Text('%s' % flightTime, align=CENTER),
                        Text('%s' % pickUpTime, align=CENTER),
                        Text('%s' % bookingAH.crewAmount, align=CENTER),
                        Text('%s' % bookingAH.flightArrStn, align=CENTER),
                        background='#%s' % bgColor)),
                        Column()))
                    
                    bookingBox.page()

            else:
                bookingBox.add(Row(Column(Isolate(Row(
                    Text("%s" % formatDay(fromDateAbsTime.adddays(i)),
                         font=Font(weight=BOLD)),
                    Text("- From Airport to Hotel:", font=Font(style=ITALIC)),
                    Text("Arrival Flights", font=Font(style=ITALIC)))),
                    Column())))
                bookingBox.page()
                bookingBox.add(Row(Column(Row(
                    Text("  - No Reservations", colspan=6)),
                    background="#dedede"),
                    Column()))
                bookingBox.page()
                
            self.add(bookingBox)
            
        calendarHeader = Row(Text(''), font=Font(weight=BOLD))
        calendarCC = Row(Text('CC'))
        calendarFC = Row(Text('FD'))
        totalCC = 0
        totalFC = 0
        days = int((toDate - fromDate)/RelTime(24,0)) + 1
        for day in range(days):
            date = fromDate + RelTime(day * 24, 0)
            ccAmount = ccCalendar['%s' % date]
            fcAmount = fcCalendar['%s' % date]
            totalCC += ccAmount
            totalFC += fcAmount
            calendarHeader.add(Text('%2s' % date.split()[2], align=RIGHT))
            calendarCC.add(Text('%s' % ccAmount, align=RIGHT))
            calendarFC.add(Text('%s' % fcAmount, align=RIGHT))
            
        calendarHeader.add(Text('Total'))
        calendarCC.add(Text('%s' % totalCC, align=RIGHT))
        calendarFC.add(Text('%s' % totalFC, align=RIGHT))
        
        self.add(Row(' '))
        self.add(Row(Text('Summary', font=Font(weight=BOLD))))
        self.add(Isolate(Column(calendarHeader,
                                calendarFC,
                                calendarCC,
                                border=border_all(1))))
        self.add(Row(' '))
        
    def getBookings(self, fromDate, toDate, region, transportId, hotelId, airportId):
        """
        This method gets transport bookings from the plan, and also a formatted
        version of the arrival and departure day for the report
        """
        # Prepare calendar dictionary and initiate with 0 rooms for each day.
        days = int((toDate - fromDate)/RelTime(24,0)) + 1
        ccCalendar = {}
        fcCalendar = {}
        for day in range(days):
            ccCalendar['%s' % (fromDate + RelTime(day * 24, 0))] = 0
            fcCalendar['%s' % (fromDate + RelTime(day * 24, 0))] = 0
            
        bc = BasicContext()
        context = bc.getGenericContext()

        if region == "ALL":
            region_txt="1 = 1"
        else:
            region_txt='report_hotel.%%region%% = "%s"' % region

        layoverDutiesFromHotel, = R.eval(context, R.foreach(
            R.iter(
                'iterators.leg_set',
                where=(
                    'report_transport.%%flight_time_from_hotel%% >= %s' % fromDate,
                    'round_down(report_transport.%%flight_time_from_hotel%%, 24:00) <= %s' \
                    % toDate,
                    '%s' % region_txt,
                    'report_transport.%need_transport_from_hotel%',
                    'report_transport.%%transport_id_from_hotel%% = "%s"' % transportId,
                    'report_transport.%%hotel_id_from_hotel%% = "%s"' % hotelId,
                    'report_transport.%%airport_from_hotel%% = "%s"' % airportId)),
            'report_transport.%ac_region%',
            'report_transport.%formatted_departure_day%',
            'report_transport.%departure_day%',
            'report_transport.%crew_needing_transport_from_hotel%',
            'report_transport.%crew_needing_transport_from_hotel_dh%',
            'report_transport.%assigned_cc%',
            'report_transport.%assigned_fc%',
            'report_transport.%airport_from_hotel%',
            'report_transport.%transport_id_from_hotel%',
            'report_transport.%hotel_id_from_hotel%',
            'report_transport.%flight_time_from_hotel%',
            'report_transport.%pick_up_time_from_hotel%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%'))

        flighTimeGreater='report_transport.%%flight_time_from_airport%% >= %s' % fromDate
        flightTimeLess ='round_down(report_transport.%%flight_time_from_airport%%, 24:00) <= %s' % toDate
        region = '%s' % region_txt
        needTransportFromAirport = 'report_transport.%need_transport_from_airport%'
        trasnportIdFromAirport ='report_transport.%%transport_id_from_airport%% = "%s"' % transportId
        hotelIdFromAirport = 'report_transport.%%hotel_id_from_airport%% = "%s"' % hotelId
        airportfromAirport= 'report_transport.%%airport_from_airport%% = "%s"' % airportId

        layoverDutiesFromAirport, = R.eval(context, R.foreach(
            R.iter(
                'iterators.leg_set',
                where=(flighTimeGreater, flightTimeLess, region, needTransportFromAirport,trasnportIdFromAirport, hotelIdFromAirport, airportfromAirport),
                sort_by= 'report_transport.%arrival_day%'),
            'report_transport.%ac_region%',
            'report_transport.%formatted_arrival_day%',
            'report_transport.%arrival_day%',
            'report_transport.%crew_needing_transport_from_airport%',
            'report_transport.%crew_needing_transport_from_airport_dh%',
            'report_transport.%assigned_cc%',
            'report_transport.%assigned_fc%',
            'report_transport.%airport_from_airport%',
            'report_transport.%transport_id_from_airport%',
            'report_transport.%hotel_id_from_airport%',
            'report_transport.%flight_time_from_airport%',
            'report_transport.%pick_up_time_from_airport%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%'))

        result = []
        for (ix, region, formattedArrivalDay, arrivalDay, crewAmount, crewAmountDH, assignedCC, 
             assignedFC, airport, transportId, hotelId, flightTime, pickUpTime, 
             flightNr, flightDepStn, flightArrStn) in layoverDutiesFromHotel:

            try:
                # Only create one BookingEntity for all crew in the same flight
                tryBooking = T.TransportBooking(True,
                                                region,
                                                hotelId,
                                                crewAmount,
                                                crewAmountDH,
                                                flightNr,
                                                flightTime,
                                                pickUpTime,
                                                flightDepStn,
                                                flightArrStn)
                i = result.index((tryBooking, formattedArrivalDay))
            except ValueError:
                result.append((tryBooking, formattedArrivalDay))
            # Add rooms needed to calendar dictionary
            date = AbsDate(arrivalDay)
            if date <= toDate:
                dateKey = '%s' % date
                ccCalendar[dateKey] = ccCalendar[dateKey] + assignedCC
                fcCalendar[dateKey] = fcCalendar[dateKey] + assignedFC
                date += RelTime(24, 0)


        for (ix, region, formattedDepartureDay, departureDay, crewAmount, crewAmountDH, assignedCC,
             assignedFC, airport, transportId, hotelId, flightTime, pickUpTime, flightNr, 
             flightDepStn, flightArrStn) in layoverDutiesFromAirport:

            try:
                # Only create one BookingEntity for all crew in the same flight
                tryBooking = T.TransportBooking(False,
                                                region,
                                                hotelId,
                                                crewAmount,
                                                crewAmountDH,
                                                flightNr,
                                                flightTime,
                                                pickUpTime,
                                                flightDepStn,
                                                flightArrStn)
                i = result.index((tryBooking, formattedDepartureDay))

            except ValueError:
                result.append((tryBooking, formattedDepartureDay))
            # Add rooms needed to calendar dictionary
            date = AbsDate(departureDay)
            if date < fromDate:
                continue
            if date <= toDate:
                dateKey = '%s' % date
                ccCalendar[dateKey] = ccCalendar[dateKey] + assignedCC
                fcCalendar[dateKey] = fcCalendar[dateKey] + assignedFC
                date += RelTime(24, 0)
            else:
                break
        result.sort()
        return (result, ccCalendar, fcCalendar)

    def separateBookings(self, bookings, fromDate, toDate):
        """
        Returns a two lists with three sublists with bookings for
        every different day. resultHA means 'from Hotel to Airport'
        and resultAH means 'from Airport to Hotel'
        """

        resultHA = []
        resultAH = []
        diffDays = int((toDate - fromDate)/RelTime(24,0)) + 1
        
        for i in xrange(diffDays+1):
            resultHA.append([])
            resultAH.append([])
    
        for booking in bookings:
            curDate = AbsDate(booking[0].flightTime)
            diffDays = int((toDate - curDate)/RelTime(24,0))
            if booking[0].isHotelToAirport:
                resultHA[diffDays].append(booking)
            else:
                resultAH[diffDays].append(booking)
        return (resultHA,resultAH)

    

def formatDate(date):
    day = str(date)[:2]
    month = str(date)[2:5].capitalize()
    year = str(date)[5:]
    return "%s %s %s" % (day,month,year)

def formatDay(date):
    return R.eval("format_time(%s, \"%%a %%02d%%b\")" % date)
    




def test1():
    import Cui
    rpt = 'TransportPerformedReport.py'
    args = 'REGION=ALL AIRPORT=BGO HOTEL=BGO4 FROM_DATE=01JUL2015 TO_DATE=31JUL2015 FROMSTUDIO=TRUE TRANSPORT=BGO4'
    print "  ## running report from __main__ ..."
    print "  ## rpt: '%s'" % rpt
    print "  ## args: '%s'" % args
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', rpt, 0, args)


if __name__ == "__main__":
    #test1()
    pass


