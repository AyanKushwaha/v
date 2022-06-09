#

#
"""
Transport Booking Report.
"""

import carmensystems.rave.api as R
import os
from tempfile import mkstemp
import Cfh
import Cui
from AbsDate import AbsDate
from RelTime import RelTime
from utils.divtools import default as D
from utils.divtools import fd_parser
import carmstd.cfhExtensions
from tm import TM
import hotel_transport.HotelBookingReportUtil as HU
import hotel_transport.TransportBookingData as T
from hotel_transport.TransportBookingRun import transportBookingRun
from report_sources.include.SASReport import SASReport
from carmensystems.publisher.api import *
import hotel_transport.SthlmTaxiMessages as SthlmTaxi
from datetime import datetime,date,time
import json
"""
TransportBookinUpdatedReport is used to update transport bookings for a transport
and a sas region for a given date.
"""
### PRT Formatting Functions
def ColumnSpacer(*a, **k):
    """An empty column of width 15"""
    k['width'] = 15
    return Column(*a, **k)

def TextStyle(*a, **k):
    """A text with left padding 15,
       italic style and colspan 5"""
    k['padding'] = padding(15,0,0,0)
    k['font'] = font(style=ITALIC)
    k['colspan'] = 5 
    return Text(*a, **k)

def RowSpacer(*a, **k):
    """An empty row of height 10"""
    k['height'] = 10
    return Row(*a, **k)

class TransportBookingUpdatedReport(SASReport):

    def getBookingId(self,booking):
        BookingId = str(booking.pickUpTime)
        return BookingId

    def ARN_transport_update_report(self,region, transportId, airportId, hotelId, date, correctionTerm):
        hotel = HU.getHotel(hotelId)
        hotel_name, = hotel.name,
        hotel_postal_code= D(hotel.postalcode)
        hotel_city = D(hotel.city)

        bookingManager = T.TransportBookingManager()
        bookingsHotelAirport = bookingManager.getDbBookings(
            True, date, transportId, hotelId, airportId, region, False)
        bookingsAirportHotel = bookingManager.getDbBookings(
            False, date, transportId, hotelId, airportId, region, False)

        bookingsHA = separateBookings(True, date, bookingsHotelAirport)
        bookingsAH = separateBookings(False, date, bookingsAirportHotel)

        cancelledBookingsHotelAirport = bookingManager.getDbBookings(
            True, date, transportId, hotelId, airportId, region, True)
        cancelledBookingsAirportHotel = bookingManager.getDbBookings(
            False, date, transportId, hotelId, airportId, region, True)

        cancelledBookingsHA = separateBookings(True, date, cancelledBookingsHotelAirport)
        cancelledBookingsAH = separateBookings(False, date, cancelledBookingsAirportHotel)
        cancelation_list =[]
        result_list = []
        if len(cancelledBookingsHA[0]) > 0:
            for booking in cancelledBookingsHA[0]:
                cancelation_id=SthlmTaxi.makeUniqueOrderId(booking)
                cancelation_list.append(cancelation_id)

        if len(cancelledBookingsAH[0]) > 0:
            for booking in cancelledBookingsAH[0]:
                cancelation_id=SthlmTaxi.makeUniqueOrderId(booking)
                cancelation_list.append(cancelation_id)

        for cancelation in cancelation_list:
            m=SthlmTaxi.StockholmTaxiCancellationMessage()
            msg=m.createMsg(cancelation)
            result_list.append(msg)


        if len(bookingsHA[0])>0:
           for booking in bookingsHA[0]:
                m = SthlmTaxi.StockholmTaxiBookingMessage()
                reservation = m.createHoteltoAirportMessage(booking, hotel_postal_code,
                                                           hotel_city, bookingManager, correctionTerm)

                result_list.append(reservation)

        if len(bookingsAH[0]) > 0:
            for booking in bookingsAH[0]:
                m = SthlmTaxi.StockholmTaxiBookingMessage()
                reservation = m.createAirporttoHotelMessage(booking, hotel_postal_code,
                                                            hotel_city,  bookingManager, correctionTerm)
                result_list.append(reservation)

        temporary_report = json.dumps(result_list)

        SASReport.create(self, showPlanData=False, headers=False,showPageTotal=False)

        txt = Text(temporary_report)

        self.add(txt)


    def create(self):
        """
        Creates a TransportBookingUpdatedReport.
        Uses TransportBookingData to retrieve data.
        """
        region = self.arg('REGION')
        transportId = self.arg('TRANSPORT')
        airportId = self.arg('AIRPORT')
        hotelId = self.arg('HOTEL')
        date = AbsDate(self.arg('DATE'))
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        format = self.arg("FORMAT")


        studioRegion, = R.eval('planning_area.%filter_company_p%')
        isAllRegions = (studioRegion == 'ALL')
        StockholmTaxiValid, = R.eval('report_transport.%Stockholm_taxi_valid%')
        correctionTerm, = R.eval('report_transport.%pick_up_time_correction%')


        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions)


        bookingManager = T.TransportBookingManager()

        if airportId == "ARN" and not fromStudio and format=="STOCKHOLM_TAXI" and StockholmTaxiValid:
            # Taxi Sthlm has its own format
            self.ARN_transport_update_report(region, transportId, airportId, hotelId, date, correctionTerm)
        else:
            # Create box with general booking report information.
            SASReport.create(self, '3 Day Pick-Up List Update', showPlanData=False,
                             margins=padding(10, 15, 10, 15), headerItems=headerItemsDict)
            infoBox = Column(
                Row(Text('Reservation Info',
                         font=self.HEADERFONT,
                         background=self.HEADERBGCOLOUR,
                         align=CENTER,
                         colspan=2)),
                Row(Text('Pick Up dates:', font=Font(weight=BOLD)),
                    Text('%s' % formatDate(date))),
                Row(Text(''),
                    Text('%s' % formatDate(date + RelTime(24, 0)))),
                Row(Text(''),
                    Text('%s' % formatDate(date + RelTime(48, 0)))),
                Row(Text('Day period:', font=Font(weight=BOLD)),
                    Text('from 02:00 to 01:59')),
                Row(Text('Date in Local time', font=Font(weight=BOLD), colspan=2)))

            transportBox = HU.transportBox(transportId)
            customerBox = HU.customerBox(region,hotelId)
            hotelBox = HU.hotelBox(hotelId)

            # Add boxes to report
            self.add(Isolate(Row(Isolate(transportBox),
                                 Text(''),
                                 Isolate(hotelBox),
                                 Text(''),
                                 Isolate(customerBox),
                                 Text(''),
                                 Isolate(infoBox))))

            self.add(Row(' '))

            # Create box with new transport bookings.
            bookingsHotelAirport = bookingManager.getDbBookings(
                True, date, transportId, hotelId, airportId, region, False)
            bookingsAirportHotel = bookingManager.getDbBookings(
                False, date, transportId, hotelId, airportId, region, False)

            bookingsHA = separateBookings(True, date, bookingsHotelAirport)
            bookingsAH = separateBookings(False, date, bookingsAirportHotel)

            cancelledBookingsHotelAirport = bookingManager.getDbBookings(
                True, date, transportId, hotelId, airportId, region, True)
            cancelledBookingsAirportHotel = bookingManager.getDbBookings(
                False, date, transportId, hotelId, airportId, region, True)

            cancelledBookingsHA = separateBookings(True, date, cancelledBookingsHotelAirport)
            cancelledBookingsAH = separateBookings(False, date, cancelledBookingsAirportHotel)

            for day_index in xrange(3):

                ################################ From Hotel to Airport #############################
                if day_index == 0:
                    text = 'Pick-up List ORDER UPDATE - '
                else:
                    text = 'Pick-up List FORECAST UPDATE - '

                self.add(Isolate(
                    Column(Row(Text(text,
                                    font=Font(size=12,weight=BOLD)),
                               Text('%s' % formatDate(date),
                                    font=Font(size=12))))))

                self.add(RowSpacer())

                self.add(Isolate(
                    Row(Text('Updates From Hotel to Airport',
                             font=Font(size=11)))))

                self.add(RowSpacer())

                # Create box with cancelled transport bookings.
                if len(cancelledBookingsHA[day_index]) > 0:
                    title = 'Cancelled Reservations From Hotel To Airport'
                    cancelBoxHA = self.getBookingHeader(True, title, colour="#d30000")
                    ix = 0
                    for booking in cancelledBookingsHA[day_index]:
                        ix += 1
                        cancelBoxHA.add(getBookingRow(True, ix, booking, airportId))
                        cancelBoxHA.page()
                else:
                    cancelBoxHA = Column(Row(TextStyle('No Cancellations')))

                self.add(cancelBoxHA)
                self.add(RowSpacer())

                # Create box with new transport bookings.
                if len(bookingsHA[day_index]) > 0:
                    title = 'New Reservations From Hotel To Airport'
                    bookingBoxHA = self.getBookingHeader(True, title, colour="#0000d3")
                    ix = 0
                    for booking in bookingsHA[day_index]:
                        ix += 1
                        bookingBoxHA.add(getBookingRow(True, ix, booking, airportId))
                        bookingBoxHA.page()
                else:
                    bookingBoxHA = Column(TextStyle('No New Reservations'))

                self.add(bookingBoxHA)
                self.add(RowSpacer())



                ################################### from Airport to Hotel ############################
                self.add(Isolate(
                    Row(Text('Updates From Airport to Hotel',
                             font=Font(size=11)))))

                self.add(RowSpacer())

                # Create box with cancelled transport bookings.
                if len(cancelledBookingsAH[day_index]) > 0:
                    title = 'Cancelled Reservations From Airport To Hotel'
                    cancelBoxAH = self.getBookingHeader(False, title, colour="#d30000")
                    ix = 0
                    for booking in cancelledBookingsAH[day_index]:
                        ix += 1
                        cancelBoxAH.add(getBookingRow(False, ix, booking, airportId))
                        cancelBoxAH.page()
                else:
                    cancelBoxAH = Column(Row(TextStyle('No Cancellations')))

                self.add(cancelBoxAH)
                self.add(RowSpacer())

                # Create box with cancelled transport bookings.
                if len(bookingsAH[day_index]) > 0:
                    title = 'New Reservations From Airport to Hotel'
                    bookingBoxAH = self.getBookingHeader(False, title, colour="#0000d3")
                    ix = 0
                    for booking in bookingsAH[day_index]:
                        ix += 1
                        bookingBoxAH.add(getBookingRow(False, ix, booking, airportId))
                        bookingBoxAH.page()
                else:
                    bookingBoxAH = Column(TextStyle('No New Reservations'))
                self.add(bookingBoxAH)
                self.add(RowSpacer())

                #Take next day but not for the last day to avoid empty page
                if day_index < 2:
                    self.newpage()
                    date = date + RelTime(24, 0)


        
    def getBookingHeader(self, fromHotelToAirport, title, colour):
        """
        Creates a booking header column.
        """
        
        if fromHotelToAirport:
            textFlight = 'Outgoing flight'
            textType = 'Departure (local)'
            textPickUp = 'Pick-Up (at hotel)'
            textToFrom = 'to Airport'
        else:
            textFlight = 'Incoming flight'
            textType = 'Arrival (local)'
            textPickUp = 'Pick-Up (at airport)'
            textToFrom = 'from Airport'
            
        return Column(Row(ColumnSpacer(),
                          Column(Row(Text(title, colspan=5,
                                          font=Font(style=ITALIC),
                                          colour=colour)),
                                 self.getTableHeader(
                                     ('Res.No',
                                      'Company',
                                      textFlight,
                                      textType,
                                      textPickUp,
                                      'Deadhead Crew',
                                      'Total Crew',
                                      textToFrom),
                                     aligns=[CENTER,CENTER,CENTER,
                                             CENTER,CENTER,CENTER,
                                             CENTER,CENTER],
                                     widths=[5,5,10,15,15,5,5,20]),
                                width=300),
                          Column(width=350)))
        
def getBookingRow(fromHotelToAirport, ix, booking, airportId):
    """
    Creates a booking row for a transport booking.
    """
    if ix % 2:
        bgColor = 'ffffff'
    else:
        bgColor = 'dedede'

    #if booking.flightNr == "-00001":
    #    booking.flightNr = "A000"
    fd = fd_parser(booking.flightNr)

    flightTime = str(booking.flightTime)[10:]
    pickUpTime = str(booking.pickUpTime)[10:]

    return Row(ColumnSpacer(),
               Column(Row(
                   Text('%s' % ix, align=CENTER),
                   Text('%s' % booking.region, align=CENTER),
                   Text("airport standby" if fd.carrier == "A0" else '%s %04d' % (fd.carrier, int(fd.number)), align=CENTER),
                   Text('%s' % flightTime, align=CENTER),
                   Text('%s' % pickUpTime, align=CENTER),
                   Text('%s' % booking.crewAmountDH, align=CENTER),                   
                   Text('%s' % booking.crewAmount, align=CENTER),                   
                   Text('%s' % airportId, align=CENTER),
                   Text(background='#ffffff'),
                   background='#%s' % bgColor)))

def separateBookings(isHotelToAirport, date, bookings):
    """
    Returns a list with bookings for the date and the following two dates.
    """
    result = [[], [], []]
    
    today = date
    tomorrow = date + RelTime(24, 0)
    day_after_tomorrow = date + RelTime(48, 0)
    
    delta = R.eval("hotel.%hotel_time_of_day_change%")[0]
    for booking in bookings:
        # a day is considered from 02:00 to 01:59 of the next day
        curDate = AbsDate(booking.flightTime - delta)
        if booking.isHotelToAirport == isHotelToAirport:
            if curDate == today:
                result[0].append(booking)
            elif curDate == tomorrow:
                result[1].append(booking)
            elif curDate == day_after_tomorrow:
                result[2].append(booking)
                
    return result



def formatDate(date):
    """
    Formats a date to a more beautiful format.
    Ex: from '03MAY2007' to '03 May 2007'
    """
    day = str(date)[:2]
    month = str(date)[2:5].capitalize()
    year = str(date)[5:]
    return "%s %s %s" % (day,month,year)

def runReport():
    """
    Creates a form where user may select information needed to create
    a transport booking report and creates a transport booking report
    if user clicks 'Ok'.
    """

    transportBookingForm = TransportBookingForm()
    if transportBookingForm.loop() == Cfh.CfhOk: 
        region = 'REGION=%s' % transportBookingForm.getRegion()
        transport = 'TRANSPORT=%s' % transportBookingForm.getTransport()
        airport = 'AIRPORT=%s' % transportBookingForm.getAirport()
        dateArg = AbsDate(transportBookingForm.getDate())
        date = 'DATE=%s' % dateArg
        fromStudio = 'FROMSTUDIO=TRUE'
        rpt = 'TransportBookingUpdatedReport.py'
        
        hotels = transportBookingForm.getHotels()
        for hotel in hotels:
            hotelArg = 'HOTEL=%s' % hotel
            args = ' '.join([region, airport, hotelArg, transport, date, fromStudio])
            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,
                                           Cui.CuiNoArea,
                                           'plan',
                                           rpt,
                                           0,
                                           args)
            
            # Set all bookings as sent for bookings included in report.
            bookingManager = T.TransportBookingManager()
            bookingManager.setBookingsAsSent(
                dateArg,
                dateArg+RelTime(72,0),
                transportBookingForm.getTransport(),
                hotel,
                transportBookingForm.getAirport(),
                transportBookingForm.getRegion())
    else:
        return

"""
A form used for selecting information needed to create a transport booking report.
"""
class TransportBookingForm(Cfh.Box):
    def __init__(self):
        Cfh.Box.__init__(self, 'Transport Reservation (New)')

        bookingManager = T.TransportBookingManager()

        drgn, = R.eval("planning_area.%filter_company_p%")
        if drgn.upper() == "ALL":
            reg_all="ALL;"
        else:
            reg_all=''
        regions = 'Flight Owner;' +reg_all +';'.join(
            ['%s:%s' % (r.region.id, r.region.name) for r in bookingManager.getRegions()])
        airportList = [(airp[0], airp[1])
                       for airp in bookingManager.getAirports()]
        airportList.sort()
        airports = 'Airport;' + ';'.join(
            ['%s:%s %s' % (airpId, airpId, name) for (airpId, name) in airportList])
        airports += ';default:Not Defined'
        transportList = [(transport.name, transport.city, transport.country, transport.id)
                         for transport in  bookingManager.getTransports()]
        transportList.sort()
        transports = 'Transport;' + ';'.join(
            ['%s:%s %s %s' % (transportId, name, city, country)
             for (name, city, country, transportId) in transportList])
        transports += ';default:Not Defined'

        self.region = Cfh.String(self, 'REGION', 10)
        self.region.setMenuString(regions)
        self.region.setMenuOnly(1)
        self.region.setMandatory(1)
        self.region.setTranslation(Cfh.String.ToUpper)
        self.transport = HU.CfhTransportString(
            self, 'TRANSPORT', 10, '')
        self.transport.setMenuString(transports)
        self.transport.setMenuOnly(1)
        self.transport.setMandatory(1)
        self.transport.setTranslation(Cfh.String.ToUpper)
        
        self.airport = HU.CfhAirportTransportString(
            self, 'AIRPORT', 10, self.transport)
        self.airport.setMenuString(airports)
        self.airport.setMenuOnly(1)
        self.airport.setMandatory(1)
        self.airport.setTranslation(Cfh.String.ToUpper)
        now, = R.eval('fundamental.%now%')
        dateNow = AbsDate(now)
        fromDate, = R.eval('fundamental.%pp_start%')
        toDate, = R.eval('fundamental.%pp_end% + 24:00')
        self.date = HU.CfhDateInRange(self, 'DATE', dateNow, fromDate, toDate)
        self.date.setMandatory(1) 
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL')

        layout = """
FORM;A_FORM;Transport Reservation (Update)
FIELD;REGION;Flight Owner
FIELD;AIRPORT;Airport
FIELD;TRANSPORT;Transport Co.
FIELD;DATE;Date
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
        """
        (fd, fileName) = mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(layout)
        f.close()
        self.load(fileName)
        os.unlink(fileName)
        self.show(True)

    def getRegion(self):
        return self.region.valof()

    def getTransport(self):
        return self.transport.valof()

    def getAirport(self):
        return self.airport.valof()
    
    def getHotels(self):
        airport = self.getAirport()
        transport = self.getTransport()
        hotels = []
        hotelsearch = TM.airport_hotel.search(
            '(&(airport=%s)(transport=%s))' % (airport,transport))
        for hotel in hotelsearch:
            hotels.append(hotel.hotel.id)
        return hotels
    
    def getDate(self):
        return self.date.valof()
