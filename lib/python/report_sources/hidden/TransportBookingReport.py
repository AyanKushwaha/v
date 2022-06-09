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
from report_sources.include.SASReport import SASReport
from carmensystems.publisher.api import *
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import hotel_transport.SthlmTaxiMessages as SthlmTaxi
import json
from datetime import datetime,date,time


"""
TransportBookinReport is used to create transport bookings for a transport
and a sas region for a given date.
"""
class TransportBookingReport(SASReport):


    def ARN_transport_report(self,region, transportId, airportId, hotelId, date, context, db,correctionTerm):
        bookingManager = T.TransportBookingManager()
        transport = HU.getTransport(transportId)
        hotel = HU.getHotel(hotelId)
        hotel_name, = hotel.name,
        hotel_postal_code= D(hotel.postalcode)
        hotel_city = D(hotel.city)

        if db:
            bookings = bookingManager.getDbBookings(None, date, transportId, hotelId, airportId, region, False)
        else:
            bookings = bookingManager.getPlanBookings(date, transportId, hotelId,
                                                      airportId, region, context)

        (bookingsHAlist, bookingsAHlist) = separateBookings(date, bookings)
        bookingsHA = None
        if len(bookingsHAlist)>0:
            bookingsHA = bookingsHAlist[0]

        bookingsAH = None
        if len(bookingsAHlist) > 0:
            bookingsAH = bookingsAHlist[0]
        reservations =[]
        for booking in bookingsHA:
            if booking.crewAmount == 0:
                continue
            message_handler = SthlmTaxi.StockholmTaxiBookingMessage()
            reservation = message_handler.createHoteltoAirportMessage(booking, hotel_postal_code, hotel_city, bookingManager, correctionTerm)
            reservations.append(reservation)

        for booking in bookingsAH:
            if booking.crewAmount == 0:
                continue
            message_handler = SthlmTaxi.StockholmTaxiBookingMessage()
            reservation = message_handler.createAirporttoHotelMessage(booking, hotel_postal_code, hotel_city,bookingManager, correctionTerm)
            reservations.append(reservation)

        temporary_report = json.dumps(reservations)

        SASReport.create(self, showPlanData=False, headers=False,showPageTotal=False)

        txt =    Text(temporary_report)

        self.add(txt)

    def create(self):
        """
        Creates a TransportBookingReport.
        Uses TransportBookingData to retrieve data.
        """
        region = self.arg('REGION')
        transportId = self.arg('TRANSPORT')
        airportId = self.arg('AIRPORT')
        hotelId = self.arg('HOTEL')
        date = AbsDate(self.arg('DATE'))
        context = self.arg('CONTEXT')
        db = (self.arg('DB') == 'True')
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        format = self.arg("FORMAT")

        studioRegion, = R.eval('planning_area.%filter_company_p%')
        correctionTerm, = R.eval('report_transport.%pick_up_time_correction%')
        isAllRegions = (studioRegion == 'ALL')
        StockholmTaxiValid, = R.eval('report_transport.%Stockholm_taxi_valid%')

        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions)
                
        if airportId=="ARN" and not fromStudio and format=="STOCKHOLM_TAXI" and StockholmTaxiValid:
            # Taxi Sthlm has its own format
            self.ARN_transport_report(region, transportId,airportId,hotelId,date,context,db,correctionTerm)
        else:

            SASReport.create(self, '3 Day Pick-Up List', showPlanData=False,
                             margins=padding(10,15,10,15), headerItems=headerItemsDict)

            items = SASReport.getTableHeader(self,[
                "Times in local time of the arrival/departure station (not UTC)"
                                ], vertical=True, widths=None, aligns=None)
            SASReport.getHeader(self).add(items)
            SASReport.getHeader(self).add(Text(""))
            SASReport.getHeader(self).set(border=border(bottom=0))

            bookingManager = T.TransportBookingManager()

            # Create box with general booking report information.
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
                    Text('from 02:00 to 01:59')))

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

            # Create box with transport bookings in plan.
            if db:
                bookings = bookingManager.getDbBookings(None, date, transportId, hotelId, airportId, region, False)
            else:
                bookings = bookingManager.getPlanBookings(date, transportId, hotelId,
                                                      airportId, region, context)

            (bookingsHA,bookingsAH) = separateBookings(date,bookings)

    ################################ From Hotel to Airport #############################

            for i in xrange(3):

                #this variable is set for controlling page breaks, as PRT don't do it so well
                if i == 0: #if it's the first page
                    text = 'Pick-up List ORDER - '
                    self.add(Isolate(
                        Column(Row(Text(text,
                                        font=Font(size=12,weight=BOLD)),
                                   Text('%s' % formatDate(date),
                                        font=Font(size=12))))))
                else:
                    text = 'Pick-up List FORECAST - '
                    self.add(Isolate(
                        Column(Row(Text(text,
                                        font=Font(size=12,weight=BOLD,style=ITALIC)),
                                   Text('%s' % formatDate(date),
                                        font=Font(size=12,style=ITALIC))))))
                ix1 = 0 #index for bookings from Hotel to Airport
                ix2 = 0 #index for bookings from Airport to Hotel
                if len(bookingsHA[i]) > 0:
                    title = 'Reservations From Hotel To Airport - %s' % formatDate(date)
                    bookingBoxFromHotel = self.getBookingHeader(True, title)
                    for booking in bookingsHA[i]:
                        ix1 += 1
                        #this is done for adding a new header in case there are too many lines
                        if isPageBreak(ix1,ix2,i,position=1) and not newPage:
                            bookingBoxFromHotel.newpage()
                            bookingBoxFromHotel.add(getAdditionalHeader(True, title+' (cont.)'))
                        bookingBoxFromHotel.add(getBookingRow(True, ix1, booking, i, airportId, correctionTerm))
                        newPage = False
                        continue
                else:
                    bookingBoxFromHotel = Column(Row())
                    bookingBoxFromHotel.add(Row(Text('No Reservations From Hotel to Airport - %s' \
                                                     % formatDate(date), colspan=5,
                                                     font=Font(style=ITALIC))))
                self.add(bookingBoxFromHotel)
                self.add(Column(width=350))
                self.add(Row(' '))

    ################################### from Airport to Hotel ############################

                if len(bookingsAH[i]) > 0:
                    title = 'Reservations From Airport to Hotel - %s' % formatDate(date)
                    bookingBoxFromAirport = self.getBookingHeader(False, title)
                    for booking in bookingsAH[i]:
                        ix2 += 1
                        #this is done for adding a new header in case there are too many lines
                        if isPageBreak(ix1,ix2,i,position=2) and not newPage:
                            bookingBoxFromAirport.newpage()
                            bookingBoxFromAirport.add(getAdditionalHeader(False, title+' (cont.)'))
                        bookingBoxFromAirport.add(getBookingRow(False, ix2, booking, i, airportId, correctionTerm))
                        newPage = False
                        continue
                else:
                    bookingBoxFromAirport = Column(Row())
                    bookingBoxFromAirport.add(Row(Text('No Reservations From Airport To Hotel - %s' \
                                                       % formatDate(date), colspan=5,
                                                       font=Font(style=ITALIC))))

                self.add(bookingBoxFromAirport)
                self.add(Row(' '))

                if not i == 2:
                    self.newpage()
                    newPage = True
                    date = date + RelTime(24, 0)
        

    def getBookingHeader(self, fromHotelToAirport, title):
        """
        Creates a booking header column.
        """
        if fromHotelToAirport:
            textFlight = 'Outgoing flight'
            textType = 'Departure'
            textPickUp = 'Pick-Up (Hotel)'
            textToFrom = 'to Airport'
        else:
            textFlight = 'Incoming flight'
            textType = 'Arrival'
            textPickUp = 'Pick-Up (Airport)'
            textToFrom = 'from Airport'
            
        return Column(Row(Column(Row(Text(title, colspan=5,
                                          font=Font(style=ITALIC),
                                          colour='#000000')),
                                 self.getTableHeader(('Res.No',
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

def getAdditionalHeader(fromHotelToAirport, title):
    """
    this creates an additional header column in case
    there are too many lines in the report.
    This shouldn't be necessary for future versions of
    PRT (Python Report Toolkit)
    """
    if fromHotelToAirport:
        textFlight = 'Outgoing flight'
        textType = 'Departure'
        textPickUp = 'Pick-Up (at hotel)'
        textToFrom = 'to Airport'
    else:
        textFlight = 'Incoming flight'
        textType = 'Arrival'
        textPickUp = 'Pick-Up (at airport)'
        textToFrom = 'from Airport'

    return Row(Column(Row(Text(title, colspan=5,
                               font=Font(style=ITALIC),
                               colour='#000000')),
                      Row(Text('Res.No'),
                          Text('Company'),
                          textFlight,
                          textType,
                          textPickUp,
                          Text('Deadhead Crew'),
                          Text('Total Crew'),
                          textToFrom,
                          Text(background='#ffffff'),
                          font=Font(size=9, weight=BOLD),
                          background='#cdcdcd')))

def getBookingRow(fromHotelToAirport, ix, booking, forecastRow, airportId, correctionTerm):
    """
    Creates a booking row for a transport booking.
    """
    if ix % 2:
        bgColor = 'ffffff'
    else:
        bgColor = 'dedede'

    # sanitize flightNr (airport standby: "-00001") before fd_parser
    if booking.flightNr.strip() == "-00001":
        booking.flightNr = "A000"
        print "   flightNr sanitized: '%s'" %  booking.flightNr

    fd = fd_parser(booking.flightNr)

    flightTime = str(booking.flightTime)[10:]
    pickUpTime = str(booking.pickUpTime+correctionTerm)[10:]
        

    if forecastRow == 0:
        return Row(Text('%s' % ix, align=CENTER),
                   Text('%s' % booking.region, align=CENTER),
                   # clean up the output (airport standby: "A0 0000")
                   Text("airport standby" if fd.carrier == "A0" else
                        '%s %04d' % (fd.carrier, int(fd.number)),
                        align=CENTER),
                   Text('%s' % flightTime, align=CENTER),
                   Text('%s' % pickUpTime, align=CENTER),
                   Text('%s' % booking.crewAmountDH, align=CENTER),                   
                   Text('%s' % booking.crewAmount, align=CENTER),                   
                   Text('%s' % airportId, align=CENTER),
                   Text(background='#ffffff'),
                   background='#%s' % bgColor)
    else:
        return Row(Text('%s' % ix, align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % booking.region, align=CENTER, font=Font(style=ITALIC)),
                   # clean up the output (airport standby: "A0 0000")
                   Text("airport standby" if fd.carrier == "A0" else
                        '%s %04d' % (fd.carrier, int(fd.number)),
                        align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % flightTime, align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % pickUpTime, align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % booking.crewAmountDH, align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % booking.crewAmount, align=CENTER, font=Font(style=ITALIC)),
                   Text('%s' % airportId, align=CENTER, font=Font(style=ITALIC)),
                   Text(background='#ffffff'),
                   background='#%s' % bgColor)

def separateBookings(date, bookings):
    """
    Returns a list with three lists with bookings for three consecutive
    days. The first list is an order, and the other two are forecast
    """

    resultHA = [[],[],[]]
    resultAH = [[],[],[]]
    date1 = date
    date2 = date + RelTime(24,0)
    date3 = date + RelTime(48,0)
    
    for booking in bookings:
        curDate = AbsDate(booking.flightTime)
        if booking.isHotelToAirport == True:
            if curDate == date1:
                resultHA[0].append(booking)
            if curDate == date2:
                resultHA[1].append(booking)
            if curDate == date3:
                resultHA[2].append(booking)
        else:
            if curDate == date1:
                resultAH[0].append(booking)
            if curDate == date2:
                resultAH[1].append(booking)
            if curDate == date3:
                resultAH[2].append(booking)
    return [resultHA,resultAH]

def formatDate(date):
    day = str(date)[:2]
    month = str(date)[2:5].capitalize()
    year = str(date)[5:]
    return "%s %s %s" % (day,month,year)

def isPageBreak(ix1,ix2,isForecast, position):
    # this is done for adding a new header in case there are too many lines
    # index1 is for bookings from Hotel to Airport
    # index2 is for bookings from Airport to Hotel
    # isForecast is for 2nd and 3rd pages
    
    if isForecast == 0:
        if position == 1:
            return ((ix1 == 53) or
                    (ix1-53)%61 == 0)
        else: #position == 2
            return ((ix1+ix2 == 51) or
                    (ix1+ix2-51)%61 == 0)
    else:
        if position == 1:
            return ((ix1 == 61) or
                    (ix1-61)%61 == 0)
        else: #position == 2
            return ((ix1+ix2 == 56) or
                    (ix1+ix2-56)%61 == 0)
        
def runReport(context='sp_crew'):
    """
    Creates a form where user may select information needed to create
    a transport booking report and creates a transport booking report
    if user clicks 'Ok'.
    """

    transportBookingForm = TransportBookingForm()
    
    if context == 'default_context':
        area = Cui.CuiWhichArea
        scope = 'window'
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)            
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
    else:
        area = Cui.CuiNoArea
        scope = 'plan'
    contextlocator = CuiContextLocator(area, scope)
    
    if transportBookingForm.loop() == Cfh.CfhOk: 
        region = 'REGION=%s' % transportBookingForm.getRegion()
        transport = 'TRANSPORT=%s' % transportBookingForm.getTransport()
        airport = 'AIRPORT=%s' % transportBookingForm.getAirport()
        dateNow, = R.eval('fundamental.%now%')
        date = 'DATE=%s' % AbsDate(transportBookingForm.getDate())
        contxt = 'CONTEXT=%s' % context
        fromStudio = 'FROMSTUDIO=TRUE'
        rpt = 'TransportBookingReport.py'

        contextlocator.reinstate()

        hotels = transportBookingForm.getHotels()
        for h in hotels:
            hotel = 'HOTEL=%s' % h
            args = ' '.join([region, airport, hotel, transport, date, contxt, fromStudio])
            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,
                                           area,
                                           scope,
                                           rpt,
                                           0,
                                           args)

    else:
        return

"""
A form used for selecting information needed to create a transport booking report.
"""
class TransportBookingForm(Cfh.Box):
    def __init__(self):
        Cfh.Box.__init__(self, 'Transport Reservation Daily')

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
FORM;A_FORM;Transport Reservation Report
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
    
    def getDate(self):
        return self.date.valof()
    
    def getHotels(self):
        airport = self.getAirport()
        transport = self.getTransport()
        hotels = []
        hotelsearch = TM.airport_hotel.search(
            '(&(airport=%s)(transport=%s)(hotel=*))' % (airport,transport))
        for hotel in hotelsearch:
            print hotel
            hotels.append(hotel.hotel.id)
        return hotels
        
        
