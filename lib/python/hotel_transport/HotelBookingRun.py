#

#
"""
Hotel Booking Run
"""

from tm import TM
from carmensystems.publisher.api import *
from hotel_transport.HotelBookingData import HotelBookingManager,getExportDir
import hotel_transport.HotelBookingReportUtil as HU

import carmensystems.rave.api as R
import time
import os
from tempfile import mkstemp
import Cfh
import Cui
import carmstd.cfhExtensions
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from AbsTime import PREV_VALID_DAY
from utils.selctx import BasicContext
from utils.performance import clockme, log
import Errlog


"""
Form used to select parameters for a manual hotel booking run.
"""
class HotelBookingRunForm(Cfh.Box):
    def __init__(self, title):
        Cfh.Box.__init__(self, title)

        bookingManager = HotelBookingManager()
        
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
    Opens a form and creates hotel bookings for selected date in form.
    """
    form = HotelBookingRunForm('Create Hotel Reservations')
    if form.loop() == Cfh.CfhOk:
        date = AbsDate(form.getDate())
    else:
        return
    mgr = HotelBookingManager()
    mgr.createUpdateBookings(date)
    for hotel in TM.hotel:
        hotelRegion = HU.getHotelRegion(hotel.country)
        customer = mgr.getCustomerData(hotelRegion)
        mgr.setTodayBookingsAsNotSent(date, hotel.id, customer.region.id)
        mgr.setPreviousBookingsAsSent(date, hotel.id, customer.region.id)

    mgr.refresh()

    return

@clockme
def updateBookings(fromMenu=False):
    """
    Updates hotel bookings for current date or for selected date in form
    if fromMenu is true.
    """
    if fromMenu:
        form = HotelBookingRunForm('Update Hotel Reservations')
        if form.loop() == Cfh.CfhOk:
            date = AbsDate(form.getDate())
        else:
            return
    else:
        date, = R.eval('fundamental.%now%')
        date = AbsDate(date)
    mgr = HotelBookingManager()
    mgr.createUpdateBookings(date)
    mgr.refresh()
    return

@clockme
def deleteBookings():
    """
    Removes hotel bookings for selected date in form.
    This function is only used for testing purposes
    """
    form = HotelBookingRunForm('Remove Hotel Reservations')
    if form.loop() == Cfh.CfhOk:
        fromDate = AbsDate(form.getDate())
    else:
        return
    toDate = fromDate + RelTime('24:00')
    bookings = TM.hotel_booking.search('(&(checkin>=%s)(checkin<%s))'\
                                       % (fromDate, toDate))
    for booking in bookings:
        booking.remove()
    Cui.CuiReloadTable('hotel_booking')
    return

"""
A form used for selecting information needed to create a hotel
forecast/performed report.
"""
class ForecastPerformedForm(Cfh.Box):
    def __init__(self, title):
        Cfh.Box.__init__(self, title)

        bookingManager = HotelBookingManager()

        drgn, = R.eval("planning_area.%filter_company_p%")
        if drgn.upper() == "ALL":
            reg_all="ALL;"
        else:
            reg_all=''

        regions = 'Flight Owner;' +reg_all +';'.join(['%s:%s' % (r.region.id, r.region.name) for r in bookingManager.getRegions()])

        airportList = [(airp[0], airp[1])
                       for airp in bookingManager.getAirports() if airp[0] and airp[0] != 'DEFAULT']
        airportList.sort()
        airports = 'Airport;DEFAULT:(All);' + ';'.join(
            ['%s:%s: %s' % (airpId, airpId, name) for (airpId, name) in airportList])
        hotelList = [(hotel.id, hotel.city, hotel.country, hotel.name) for hotel in  bookingManager.getHotels() if hotel.id not in ['DEFAULT', 'NONE']]
        hotelList.sort()
        hotels = 'Hotel;DEFAULT:(Missing);NONE:(None);' + ';'.join(
            ['%s:%s: %s %s %s' % (hotelId, hotelId, name, city, country) for (hotelId, name, city, country) in hotelList])
        

        self.region = Cfh.String(self, 'REGION', 10)
        self.region.setMenuString(regions)
        self.region.setMenuOnly(1)
        self.region.setMandatory(1)
        self.region.setTranslation(Cfh.String.ToUpper)
        self.hotel = HU.CfhHotelString(self, 'HOTEL', 10, '')
        self.hotel.setMenuString(hotels)
        self.hotel.setMenuOnly(1)
        self.hotel.setMandatory(1)
        self.hotel.setTranslation(Cfh.String.ToUpper)
        self.airport = HU.CfhAirportHotelString(self, 'AIRPORT', 10, self.hotel)
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
FIELD;HOTEL;Hotel
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

    def getHotel(self):
        return self.hotel.valof()

    def getFromDate(self):
        return self.date1.valof()

    def getToDate(self):
        return self.date2.valof()

@clockme
def runForecastPerformedReport(title, rpt):
    """
    Creates a form where user may select information needed to create
    a hotel forecast/performed report and creates a hotel forecast/performed
    report if user clicks 'Ok'.
    """
    hotelBookingForm = ForecastPerformedForm(title)
    if hotelBookingForm.loop() == Cfh.CfhOk:
        region = 'REGION=%s' % hotelBookingForm.getRegion()
        selectedHotel = hotelBookingForm.getHotel()
        if selectedHotel == 'DEFAULT':
            selectedHotel = 'default'
        hotel = 'HOTEL=%s' % selectedHotel
        fromDate = 'FROM_DATE=%s' % AbsDate(hotelBookingForm.getFromDate())
        toDate = 'TO_DATE=%s' % AbsDate(hotelBookingForm.getToDate())
        fromStudio = 'FROMSTUDIO=TRUE'
        args = ' '.join([region, hotel, fromDate, toDate, fromStudio])

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
    runForecastPerformedReport('Hotel Reservation Forecast', 'HotelForecastReport.py')
    return

def performedReport():
    """
    Initiates a hotel performed report.
    """
    runForecastPerformedReport('Hotel Reservation Performed', 'HotelPerformedReport.py')
    return

@clockme
def generateBookingReportFile(*args):
    """
    Creates a hotel booking report.
    arg0 customerregion
    arg1 hotel
    arg2 date
    arg4 region
    """

    isUpdate = args[3]
    if isUpdate: 
        fileName = HU.createFileName('HotelUpdate', args[4], args[1], args[2], True)
    else: 
        fileName = HU.createFileName('HotelBookingReport', args[4], args[1], args[2])
    
    region = 'REGION=%s' % args[4]
    hotel = 'HOTEL=%s' % args[1]
    date = 'DATE=%s' % args[2]
    if not isUpdate:
        update = "UPDATE=False"
    else:
        update = "UPDATE=True"
    db = 'DB=True'
    bc = BasicContext()
    context = 'CONTEXT=%s' % bc.getGenericContext()
    
    args = ' '.join([region, hotel, date, db, update, context])
    
    return generateReport('report_sources.hidden.HotelBookingReport',
                          fileName,
                          PDF,
                          args)

@clockme
def generateForecastReportFile(*args):
    """
    Creates a hotel forecast report.
    arg0 customer region
    arg1 hotel
    arg2 fromDate
    arg3 toDate
    arg4 region
    """
    
    fileName = HU.createFileName('HotelForecast',args[4], args[1], args[2])

    region = 'REGION=%s' % args[4]
    hotel = 'HOTEL=%s' % args[1]
    fromDate = 'FROM_DATE=%s' % args[2]
    toDate = 'TO_DATE=%s' % args[3]
    
    args = ' '.join([region, hotel, fromDate, toDate])
    
    return generateReport('report_sources.hidden.HotelForecastReport',
                          fileName,
                          PDF,
                          args)

@clockme
def generatePerformedReportFile(*args):
    """
    Creates a hotel performed report.
    arg0 customer region
    arg1 hotel
    arg2 fromDate
    arg3 toDate
    arg4 region
    """
    
    fileName = HU.createFileName('HotelPerformed', args[4], args[1], args[2])
    
    region = 'REGION=%s' % args[4]
    hotel = 'HOTEL=%s' % args[1]
    fromDate = 'FROM_DATE=%s' % args[2]
    toDate = 'TO_DATE=%s' % args[3]
    
    args = ' '.join([region, hotel, fromDate, toDate])
    
    return generateReport('report_sources.hidden.HotelPerformedReport',
                          fileName,
                          PDF,
                          args)

@clockme
def makeReportDict(addr, ccAddr, sAddr, file, subject):
    attachment = os.path.split(file)[-1]
    emailSpec = {'mfrom': sAddr, 'to': addr, 
                 'subject': subject, 'attachmentName': attachment}
    if not (addr == ccAddr):
        emailSpec['cc'] = ccAddr
    destList = [("mail", emailSpec)]
    reportDict = {'content-type': "application/pdf",
                  'content-location': file,
                  'destination': destList}
    return reportDict

@clockme
def hotelBookingRun(bookingUpdate=False, forecast=False, performed=False):
    """
    Performs a Hotel Booking Run or Hotel Forecast Run.
    If bookingUpdate is true the booking run is performed for today
    otherwise for tomorrow.
    bookingUpdate does not apply to forecast run.
    """
    date, = R.eval('fundamental.%now%')
    resultList = []
    mgr = HotelBookingManager()
    
    if forecast:
        fromDate = AbsTime(int(date))
        fromDate = fromDate.month_floor()
        fromDate = fromDate.addmonths(1)
        fromDate = AbsDate(fromDate)
        toDate = AbsTime(int(fromDate))
        toDate = toDate.addmonths(1, PREV_VALID_DAY)
        toDate = toDate.adddays(-1)
        toDate = AbsDate(toDate)

        hotels = [(hc.hotel.id, hc.hotel.email, hc.hotel.country) for hc in TM.hotel_contract.search('(&(validto>%s)(validfrom<=%s))' % (fromDate, toDate))]
        customer = mgr.getCustomerData("SKD")
        hotels += [("default", customer.email, "DK")] # Missing bookings
        #hotels += [("none", customer.email, "DK")] # Manual/non-required bookings
        for hotelId, hotelEmail, hotelCountry in hotels:
            hotelRegion = HU.getHotelRegion(hotelCountry)
            customer = mgr.getCustomerData(hotelRegion)
            senderEmail = HU.getFirstEmail(customer.email)
            regionId = customer.region.id
            subject = 'Hotel Reservation Forecast - %s - %s' % ("ALL", hotelId)
            try:
                fileName = generateForecastReportFile(regionId, hotelId, fromDate, toDate, "ALL")
                reportDict = makeReportDict(hotelEmail, customer.email, 
                                            senderEmail, fileName, subject)
                resultList.append(reportDict)
            except Exception, msg:
                Errlog.log("Error when generating %s\n %s" % (subject, msg))
                continue

    elif performed:
        fromDate = AbsTime(int(date))
        fromDate = fromDate.month_floor()
        fromDate = fromDate.addmonths(-1)
        fromDate = AbsDate(fromDate)
        toDate = AbsTime(int(fromDate))
        toDate = toDate.addmonths(1, PREV_VALID_DAY)
        toDate = toDate.adddays(-1)
        toDate = AbsDate(toDate)

        hotels = [(hotel.id, hotel.email, hotel.country) for hotel in TM.hotel]
        customer = mgr.getCustomerData("SKD")
        hotels += [("default", customer.email, "DK")] # Missing bookings
        for hotelId, hotelEmail, hotelCountry in hotels:
            hotelRegion = HU.getHotelRegion(hotelCountry)
            customer = mgr.getCustomerData(hotelRegion)
            senderEmail = HU.getFirstEmail(customer.email)
            regionId = customer.region.id
            if mgr.isSentDbBookings(fromDate, toDate, hotelId, regionId):
                try:
                    subject = 'Hotel Reservation Performed - %s - %s' % ("ALL", hotelId)
                    fileName = generatePerformedReportFile(regionId, hotelId, fromDate, toDate, "ALL")
                    reportDict = makeReportDict(customer.email, customer.email, 
                                                senderEmail, fileName, subject)
                    resultList.append(reportDict)
                except Exception, msg:
                    Errlog.log("Error when generating %s\n %s" % (subject, msg))
                    continue

    else:
        date = date.day_floor()
        date = AbsDate(date)
        
        mgr.createUpdateBookings(date)
        mgr.refresh()
        hotels = [(hotel.id, hotel.email, hotel.country) for hotel in TM.hotel]
        customer = mgr.getCustomerData("SKD")
        hotels += [("default", customer.email, "DK")] # Missing bookings
        for hotelId, hotelEmail, hotelCountry in hotels:
            hotelRegion = HU.getHotelRegion(hotelCountry)
            customer = mgr.getCustomerData(hotelRegion)
            senderEmail = HU.getFirstEmail(customer.email)
            # if it's not an update, bookings are marked as no sent in the db
            # for the next day because it was marked as sent in the last 48 hrs
            # and previous bookings from today are marked as sent because they 
            # were already created and sent days before (not new)
            regionId = customer.region.id
            if not bookingUpdate:
                subject = 'Hotel Reservation Daily - %s - %s' % ("ALL", hotelId)
                mgr.setTodayBookingsAsNotSent(date, hotelId, regionId)
                mgr.setPreviousBookingsAsSent(date, hotelId, regionId)
            else:
                subject = 'Hotel Update Daily - %s - %s' % ("ALL", hotelId)

            # Do not create reports if there aren't any unsent bookings.

            if mgr.isNotSentDbBookings(date, hotelId, regionId, bookingUpdate):
                try:
                    fileName = generateBookingReportFile(regionId, hotelId, date, bookingUpdate, "ALL")
                    reportDict = makeReportDict(hotelEmail, customer.email,
                                                    senderEmail, fileName, subject)
                    resultList.append(reportDict) 
                    # this marks the bookings as sent 48 hours forward
                    mgr.setBookingsAsSent(date, hotelId, regionId, bookingUpdate)
                except Exception, msg:
                    Errlog.log("Error when generating %s\n %s" % (subject, msg))
                    continue

    return resultList
