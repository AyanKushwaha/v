#

#
"""
Transport Booking Run
reload(hotel_transport.TransportBookingData); reload(hotel_transport.TransportBookingRun).transportBookingRun()
"""

from tm import TM
from carmensystems.publisher.api import *
from hotel_transport.TransportBookingData import TransportBookingManager,getExportDir
import hotel_transport.HotelBookingReportUtil as HU
import data.TransportMqHandler as transportMqHandler
import carmensystems.rave.api as R
import time
import os
from tempfile import mkstemp
import Cfh
import Cui
import carmstd.cfhExtensions
from AbsDate import AbsDate
from AbsTime import AbsTime
from AbsTime import PREV_VALID_DAY
from utils.selctx import BasicContext
from utils.performance import clockme, log, profileme
from carmensystems.common.ServiceConfig import ServiceConfig
import Errlog
import json

"""
Form used to select parameters for a manual transport booking run.
"""
class TransportBookingRunForm(Cfh.Box):
    def __init__(self, title):
        Cfh.Box.__init__(self, title)

        bookingManager = TransportBookingManager()

        now, = R.eval('fundamental.%now%')
        dateNow = AbsDate(now)
        fromDate, = R.eval('fundamental.%pp_start%')
        toDate, = R.eval('fundamental.%pp_end% + 24:00')
        
        self.date = HU.CfhDateInRange(self, 'DATE', dateNow, fromDate, toDate)
        self.date.setMandatory(1)
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL')

        layout = """
FORM;A_FORM;%s
FIELD;DATE;Date
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
""" % title

        (fd, fileName) = mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(layout)
        f.close()
        self.load(fileName)
        os.unlink(fileName)
        self.show(True)

    def getDate(self):
        return self.date.valof()


@clockme
def createBookings():
    """
    Opens a form and creates transport bookings for selected date in form.
    """
    form = TransportBookingRunForm('Create Transport Reservations')
    if form.loop() == Cfh.CfhOk:
        date = AbsDate(form.getDate())
    else:
        return
    # Bookings are made for three days
    toDate = date + RelTime(24, 0)
    mgr = TransportBookingManager()
    bookings = mgr.createUpdateBookings(date,toDate)
    mgr.refresh()

    transportMqHandler.prepareTransportMessages(bookings)

    return

@clockme
def updateBookings():
    """
    Updates transport bookings for current date or for selected date in form
    if fromMenu is true.
    """

    form = TransportBookingRunForm('Update Transport Reservations')
    if form.loop() == Cfh.CfhOk:
        date = AbsDate(form.getDate())
    else:
        return

    # Updates are made for only one day
    toDate = date + RelTime(24, 0)
    mgr = TransportBookingManager()
    mgr.createUpdateBookings(date,toDate)
    mgr.refresh()    

@clockme
def deleteBookings():
    """
    Removes transport bookings for selected date in form.
    This function is only used for testing purposes
    """
    form = TransportBookingRunForm('Remove Transport Reservations')
    if form.loop() == Cfh.CfhOk:
        fromDate = AbsDate(form.getDate())
    else:
        return
    toDate = fromDate + RelTime('24:00')
    bookings = TM.transport_booking.search('(&(flight_day>=%s)(flight_day<%s))'\
                                       % (fromDate, toDate))
    for booking in bookings:
        booking.remove()
    

"""
A form used for selecting information needed to create a
transport performed report.
"""
class PerformedForm(Cfh.Box):
    def __init__(self, title):
        Cfh.Box.__init__(self, title)

        bookingManager = TransportBookingManager()

        drgn, = R.eval("planning_area.%filter_company_p%")
        if drgn.upper() == "ALL":
            reg_all="ALL;"
        else:
            reg_all=''

        regions = 'Flight Owner;' +reg_all +';'.join(
            ['%s:%s' % (r.region.id, r.region.name)
             for r in bookingManager.getRegions()])
        transportList = [(transport.id, transport.name, transport.city,
                          transport.country)
                         for transport in  bookingManager.getTransports()]
        transportList.sort()
        transports = 'Transport;' + ';'.join(
            ['%s:%s %s %s %s' % (transportId, transportId, name, city, country)
             for (transportId, name, city, country) in transportList])
        transports += ';default:Not Defined'

        airportList = [(airport[0], airport[1])
                       for airport in bookingManager.getAirports()]
        airportList.sort()
        airports = 'Airport;' + ';'.join(
            ['%s:%s %s' % (airportId, airportId, name)
             for (airportId, name) in airportList])
        airports += ';default:Not Defined'

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
        d1 = now.month_floor()
        d2 = now.month_ceil()
        fromDate, = R.eval('fundamental.%pp_start%')
        toDate, = R.eval('fundamental.%pp_end% + 24:00')
        self.date1 = HU.CfhDateInRange(self, 'DATE1', d1, fromDate, toDate)
        self.date1.setMandatory(1)
        self.date2 = HU.CfhDateInRange(self, 'DATE2', d2, fromDate, toDate)
        self.date2.setMandatory(1)
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL') 

        layout = """
FORM;A_FORM;%s
FIELD;REGION;Flight Owner
FIELD;AIRPORT;Airport
FIELD;TRANSPORT;Transport Co.
FIELD;DATE1;From Date
FIELD;DATE2;To Date
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
""" % title

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

    def getFromDate(self):
        return self.date1.valof()

    def getToDate(self):
        return self.date2.valof()
    
    def getHotels(self):
        airport = self.getAirport()
        transport = self.getTransport()
        hotels = []
        hotelsearch = TM.airport_hotel.search(
            '(&(airport=%s)(transport=%s)(hotel=*))' % (airport,transport))
        for hotel in hotelsearch:
            hotels.append(hotel.hotel.id)
        return hotels

def runForecastPerformedReport(title, rpt):
    """
    Creates a form where user may select information needed to create
    a transport performed report and creates a transport performed
    report if user clicks 'Ok'.
    """
    transportBookingForm = PerformedForm(title)
    if transportBookingForm.loop() == Cfh.CfhOk:
        region = 'REGION=%s' % transportBookingForm.getRegion()
        transport = 'TRANSPORT=%s' % transportBookingForm.getTransport()
        airport = 'AIRPORT=%s' % transportBookingForm.getAirport()
        fromDate = 'FROM_DATE=%s' % AbsDate(transportBookingForm.getFromDate())
        toDate = 'TO_DATE=%s' % AbsDate(transportBookingForm.getToDate())
        fromStudio = 'FROMSTUDIO=TRUE'
        
        hotels = transportBookingForm.getHotels()
        for h in hotels:
            hotel = 'HOTEL=%s' % h
            args = ' '.join([region, airport, hotel, transport, 
                             fromDate, toDate, fromStudio])
            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,
                                           Cui.CuiNoArea,
                                           'plan',
                                           rpt,
                                           0,
                                           args)
    return

def forecastReport():
    """
    Initiates a hotel forecast report.
    """
    runForecastPerformedReport('Transport Forecast', 'TransportForecastReport.py')
    return

def performedReport():
    """
    Initiates a transport performed report.
    """
    runForecastPerformedReport('Transport Performed', 'TransportPerformedReport.py')
    return

@clockme
def generateBookingReportFile(*args):
    """
    Creates a transport booking report.
    arg0 customerregion
    arg1 transport
    arg2 hotel
    arg3 airport
    arg4 date
    arg5 isUpdateBooking
    arg6 region
    arg7 file_format
    """
    isUpdate = args[5]
    file_format = args[7]

    if isUpdate:
        if file_format == "TXT":
            fileName = HU.createFileName('TransportUpdateTXT', args[6], args[2], args[4], True, False,"TXT")
        else:
            fileName = HU.createFileName('TransportUpdate', args[6], args[2], args[4], True, False,"PDF")
    else:
        if file_format == "TXT":
            fileName = HU.createFileName('TransportBookingReportTXT', args[6], args[2], args[4], False, False,"TXT")
        else:
            fileName = HU.createFileName('TransportBookingReport', args[6], args[2], args[4], False, False,"PDF")
    
    region = 'REGION=%s' % args[6]
    transport = 'TRANSPORT=%s' % args[1]
    hotel = 'HOTEL=%s' % args[2]
    db = 'DB=True'
    airport = 'AIRPORT=%s' % args[3]
    date = 'DATE=%s' % AbsDate(args[4])
    format_text ="FORMAT=STOCKHOLM_TAXI"
    format_pdf="FORMAT=PDF"
    args = ' '.join([region, transport, hotel, airport, date, db])
    
    if isUpdate:
        if file_format == "TXT":
            args=args+" "+format_text
            return generateReport('report_sources.hidden.TransportBookingUpdatedReport',
                                  fileName,
                                  TXT,
                                  args)
        else:
            args=args+" "+format_pdf
            return generateReport('report_sources.hidden.TransportBookingUpdatedReport',
                                  fileName,
                                  PDF,
                                  args)

    else:
        bc = BasicContext()
        args += ' CONTEXT=%s' % bc.getGenericContext()
        if file_format == "TXT":
            args=args+" "+format_text
            return generateReport('report_sources.hidden.TransportBookingReport',
                                  fileName,
                                  TXT,
                                  args)
        else:
            args=args+" "+format_pdf
            return generateReport('report_sources.hidden.TransportBookingReport',
                                  fileName,
                                  PDF,
                                  args)


@clockme
def generatePerformedReportFile(*args):
    """
    Creates a transport performed report.
    arg0 customerregion
    arg1 transport
    arg2 hotel
    arg3 airport
    arg4 fromDate
    arg5 toDate
    arg6 region
    """
    fileName = HU.createFileName(
        'TransportPerformed',args[6],args[2],args[4],False,False)

    region = 'REGION=%s' % args[6]
    transport = 'TRANSPORT=%s' % args[1]
    hotel = 'HOTEL=%s' % args[2]
    airport = 'AIRPORT=%s' % args[3]
    fromDate = 'FROM_DATE=%s' % args[4]
    toDate = 'TO_DATE=%s' % args[5]
    
    args = ' '.join([region, transport, hotel, airport, fromDate, toDate])
    
    return generateReport('report_sources.hidden.TransportPerformedReport',
                          fileName,
                          PDF,
                          args)    
@clockme
def generateForecastReportFile(*args):
    """
    Creates a transport performed report.
    arg0 customerregion
    arg1 transport
    arg2 hotel
    arg3 airport
    arg4 fromDate
    arg5 toDate
    arg6 region
    """
    fileName = HU.createFileName(
        'TransportForecast',args[6],args[2],args[4],False,False)

    region = 'REGION=%s' % args[6]
    transport = 'TRANSPORT=%s' % args[1]
    hotel = 'HOTEL=%s' % args[2]
    airport = 'AIRPORT=%s' % args[3]
    fromDate = 'FROM_DATE=%s' % args[4]
    toDate = 'TO_DATE=%s' % args[5]
    
    args = ' '.join([region, transport, hotel, airport, fromDate, toDate])
    
    return generateReport('report_sources.hidden.TransportForecastReport',
                          fileName,
                          PDF,
                          args)    

def makeReportDict(addr, ccAddr, sAddr, file, subject):
    attachment = os.path.split(file)[-1]
    emailSpec = {'mfrom': sAddr, 'to': addr, 'subject': subject, 'attachmentName': attachment}
    if not (addr == ccAddr):
        emailSpec['cc'] = ccAddr
    destList = [("mail", emailSpec)]
    reportDict = {'content-type': "application/pdf",
                  'content-location': file,
                  'destination': destList}
    return reportDict

def makeReportDictWebservice(address,report):
    destlist = [("webservice",{"address":address} )]
    reportDict = {'content':report,
                   'content-type': 'application/xml',
                   'destination' : destlist
                  }


    return reportDict

def isWebBased(airport):
     StockholmTaxiValid, = R.eval('report_transport.%Stockholm_taxi_valid%')
     return (airport == "ARN") and StockholmTaxiValid

@clockme
def transportBookingRun(bookingUpdate=False, performed=False, forecast=True):
    """
    Performs a Transport Booking Run.
    There are four types of runs:
    - Daily order run
      Executed once each night and creates orders for tomorrow and the following two days.
    - Update order run
      Executed once every hours updates the order from the daily run (for today and the following two days)
    - Performed run
      Creates a report for the actually bookings last month
    - Forcast run
      Creates a report for the next month
    """
    dateNow, = R.eval('fundamental.%now%')
    date = dateNow.day_floor()

    resultList = []

    mgr = TransportBookingManager()
    
    if performed:
        fromDate = AbsTime(int(date))
        fromDate = fromDate.month_floor()
        fromDate = fromDate.addmonths(-1)
        fromDate = AbsDate(fromDate)
        toDate = AbsTime(int(fromDate))
        toDate = toDate.addmonths(1, PREV_VALID_DAY)
        toDate = toDate.adddays(-1)
        toDate = AbsDate(toDate)

        for transport in TM.transport:
            for hotel in TM.hotel:
                hotelRegion = HU.getHotelRegion(hotel.country)
                customer = mgr.getCustomerData(hotelRegion)
                senderEmail = HU.getFirstEmail(customer.email)
                (hId, rId, tId) = (hotel.id, customer.region.id, transport.id)
                airports = TM.airport_hotel.search('(&(transport=%s)(hotel=%s))' % (tId, hId))
                for airport in airports:
                    aId = airport.airport.id
                    subject = 'Transport Performed - %s - %s' % ("ALL", hId)
                    if mgr.isSentDbBookings(fromDate, toDate, tId, hId, aId, rId):
                        try:
                            fileName = generatePerformedReportFile(rId, tId, hId, aId, fromDate, toDate, "ALL")
                            reportDict = makeReportDict(customer.email, customer.email, 
                                                            senderEmail, fileName, subject)
                            resultList.append(reportDict)
                        except Exception, msg:
                            Errlog.log("Error when generating %s\n %s" % (subject, msg))
                            continue
    elif forecast:
        fromDate = AbsTime(int(date)).month_floor()
        fromDate = fromDate.addmonths(1)
        toDate = fromDate.addmonths(1)
        fromDate = AbsDate(fromDate)
        toDate = AbsDate(toDate)

        for transport in TM.transport:
            for hotel in TM.hotel:
                hotelRegion = HU.getHotelRegion(hotel.country)
                customer = mgr.getCustomerData(hotelRegion)
                senderEmail = HU.getFirstEmail(customer.email)
                (hId, rId, tId) = (hotel.id, customer.region.id, transport.id)

                airports = TM.airport_hotel.search('(&(transport=%s)(hotel=%s))' % (tId, hId))
                for airport in airports:
                    aId = airport.airport.id
                    subject = 'Transport Forecast - %s - %s' % ("ALL", hId)
                    try:
                        fileName = generateForecastReportFile(rId, tId, hId, aId, fromDate, toDate, "ALL")
                        reportDict = makeReportDict(transport.email, customer.email, 
                                                        senderEmail, fileName, subject)
                        resultList.append(reportDict)
                    except Exception, msg:
                        Errlog.log("Error when generating %s\n %s" % (subject, msg))
                        continue
    else:
        if not bookingUpdate:
            # Bookings are run for tomorrow, since we need to book taxi for the early morning flights the day before.
            date = date.adddays(1)

        fromDate = AbsDate(date)
        
        # Bookings for three days, where the last two days are actually a short-term forecast.
        toDate = date + RelTime(72, 0)
        
        mgr.createUpdateBookings(fromDate, toDate)
        mgr.refresh()
        if not bookingUpdate:
            mgr.setTodayBookingsAsNotSent(fromDate)

        for hotel in TM.hotel:
            hotelRegion = HU.getHotelRegion(hotel.country)
            customer = mgr.getCustomerData(hotelRegion)
            senderEmail = HU.getFirstEmail(customer.email)

            for transport in TM.transport:
                (hId, rId, tId) = (hotel.id, customer.region.id, transport.id)
                if bookingUpdate:
                    transportEmail = transport.emailupd
                    subject = '3 Day Pick-up List Update - %s - %s' % ("ALL", hId)
                else:
                    transportEmail = transport.email
                    subject = '3 Day Pick-up List - %s - %s' % ("ALL", hId)

                airports = TM.airport_hotel.search('(&(transport=%s)(hotel=%s))' % (tId, hId))
                for airport in airports:
                    aId = airport.airport.id
                    # Do not create reports if there aren't any unsent bookings.
                    if mgr.isNotSentDbBookings(fromDate, toDate, tId, hId, aId, rId, bookingUpdate):
                        try:
                            # Besides delivering ARN report though mail, we have a special format for Sthlm taxi
                            # that shall be delivered as webservice
                            if isWebBased(aId):
                                fileName = generateBookingReportFile(rId, tId, hId, aId, date, bookingUpdate, "ALL","TXT")
                                f=open(fileName,'r')
                                messages=json.load(f)
                                f.close()
                                for message in messages:
                                    message = json.dumps(message)
                                    webaddress = getWebServiceAddress()
                                    reportDict=makeReportDictWebservice(webaddress,message)
                                    resultList.append(reportDict)
                            fileName = generateBookingReportFile(rId, tId, hId, aId, date, bookingUpdate, "ALL",
                                                                     "PDF")
                            reportDict = makeReportDict(transportEmail, customer.email,
                                                            senderEmail, fileName, subject)
                            resultList.append(reportDict)
                            mgr.setBookingsAsSent(fromDate, toDate, tId, hId, aId, rId)

                        except Exception, msg:
                            Errlog.log("Error when generating %s\n %s" % (subject, msg))
                            continue
    return resultList


def getWebServiceAddress():
    service_config = ServiceConfig()
    (_, taxi_url) = service_config.getProperty("dig_settings/webservice/taxi_sthlm_url")
    return taxi_url
