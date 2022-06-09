#

#
"""
Hotel Booking Report.
"""

import carmensystems.rave.api as R
import os
from tempfile import mkstemp
import Cfh
import Cui
from AbsDate import AbsDate
from RelTime import RelTime
from utils.divtools import default as D
import carmstd.cfhExtensions
import utils.CfhFormClasses as F
import hotel_transport.HotelBookingReportUtil as HU
import hotel_transport.HotelBookingData as H
from report_sources.include.SASReport import SASReport
from carmensystems.publisher.api import *
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator

""" 
PRT formatting functions 
"""
def TextRight(*a, **k):
    """An text aligned to the right"""
    k['align'] = RIGHT
    return Text(*a, **k)

"""
HotelBookingReport is used to create a hotel bookings for a hotel
and a sas region for a given date.
"""
class HotelBookingReport(SASReport):

    def create(self):
        """
        Creates a HotelBookingReport.
        Uses HotelBookingData to retrieve data.
        Report uses either data from db or from plan depending on db param.
        report uses default context or all crew depending on context param 
        """
        bookingManager = H.HotelBookingManager()

        region = self.arg('REGION')
        hotelId = self.arg('HOTEL')
        date = AbsDate(self.arg('DATE'))
        db = self.arg('DB') == 'True'
        update = self.arg('UPDATE') == 'True'
        context = self.arg('CONTEXT')
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        
        studioRegion, = R.eval('planning_area.%filter_company_p%')
        isAllRegions = (studioRegion == 'ALL')
        
        if update:
            report_title="Hotel Update Daily"
        else:
            report_title="Hotel Reservation Daily"

        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions, isLandscape=True)
        SASReport.create(self, report_title, showPlanData=False,
                         orientation=LANDSCAPE, headerItems=headerItemsDict)

        items = SASReport.getTableHeader(self,[
            "Times in local time of the arrival/departure station (not UTC)"
                            ], vertical=True, widths=None, aligns=None)
        SASReport.getHeader(self).add(items)
        SASReport.getHeader(self).add(Text(""))
        SASReport.getHeader(self).set(border=border(bottom=0))

        # Create box with general booking report information.
        infoBox = Column(
            Row(Text('Reservation Info',
                     font=self.HEADERFONT,
                     background=self.HEADERBGCOLOUR,
                     align=CENTER,
                     colspan=2)),
            Row(Text('Check in dates:', font=Font(weight=BOLD)),
                Text('%s' % date)),
            Row(Text(''),
                Text('%s' % (date + RelTime(24, 0)))),
            Row(Text('Day period:', font=Font(weight=BOLD)),
                Text('from 02:00 to 01:59')))
        
        hotelBox = HU.hotelBox(hotelId)
        customerBox = HU.customerBox(region,hotelId)

        # Add boxes to report
        self.add(Isolate(Row(Isolate(hotelBox),
                             Text(''),
                             Isolate(customerBox),
                             Text(''),
                             Isolate(infoBox))))
        self.add(Row(' '))
        if update:
            bookingBox = self.getBookingHeader('New Reservations')
        else:
            bookingBox = self.getBookingHeader('Reservations')
            
        if db:
            # Create box with new hotel bookings.
            bookings = bookingManager.getDbBookings(
                date, hotelId, region, False)
        else:
            # Create box with hotel bookings in plan.
            bookings = bookingManager.getPlanBookings(
                date, hotelId, region, context)
        
        if len(bookings) > 0:
            ix = 0
            prevDate = None
            for booking in bookings:
                ix += 1
                bookingBox.page()
                curDate = AbsDate(AbsTime(booking.arrFlightTime) - RelTime('02:00'))
                if prevDate and curDate > prevDate:
                    bookingBox.add(Row(Text(' ')))
                prevDate = curDate
                bookingBox.add(getBookingRow(ix, booking))
        else:
            if update:
                noReservationStr = 'No New Reservations'
            else:
                noReservationStr = 'No Reservations'
            bookingBox.add(Row(Text(noReservationStr, colspan=5)))

        self.add(bookingBox)
        self.add(Row(' '))
        self.page()

        if update:
            # Create box with cancelled hotel bookings.
            cancelBox = self.getBookingHeader('Cancelled Reservations')
            cancelledBookings = bookingManager.getDbBookings(
                date, hotelId, region, True)
            ix = 0
            if len(cancelledBookings) > 0:
                for booking in cancelledBookings:
                    ix += 1
                    cancelBox.page()
                    cancelBox.add(getBookingRow(ix, booking))
            else:
                cancelBox.add(Row(Text('No Cancellations', colspan=5)))
            self.add(cancelBox)
            self.page()


    def getBookingHeader(self, header):
        """
        Creates a booking header column.
        """
        return Column(Row(Text(header, colspan=5, font=Font(weight=BOLD))),
                      self.getTableHeader((
                          'No',
                          'Emp No',
                          'Rank',
                          'Name',
                          'Company',
                          'Incoming Flight',
                          'Arrival',
                          'Next Flight',
                          'Departure',
                          'Rooms',
                          'Nights/Day Room')))

def getBookingRow(ix, booking):
    """
    Creates a booking row for a hotel booking.
    """
    if ix % 2:
        bgColor = 'ffffff'
    else:
        bgColor = 'dedede'

    if booking.depFlightNr == "?": nightsText = '?'
    elif booking.nights == 0: nightsText = 'D'
    elif booking.nights > 1: nightsText = 'C'
    else: nightsText = ''
    
    if booking.depFlightNr == "?": depFlightTimeText = "?"
    else: depFlightTimeText = booking.depFlightTime
    
    return Row(Text('%s' % ix),
               Text('%s' % D(booking.empNumber, 'N/A')),
               Text('%s' % D(booking.rank, 'N/A')),
               Text('%s, %s' % (D(booking.lastName, 'N/A'),
                                D(booking.firstName, 'N/A'))),
               Text('%s' % D(booking.region, 'N/A')),
               TextRight('%s' % booking.arrFlightNr),
               Text('%s' % booking.arrFlightTime),
               TextRight('%s' % booking.depFlightNr),
               Text('%s' % depFlightTimeText),
               Text('%s' % booking.rooms),
               Text('%s' % nightsText),
               background='#%s' % bgColor)
    

def runReport(fromDb, context='sp_crew'):
    """
    Creates a form where user may select information needed to create
    a hotel booking report and creates a hotel booking report
    if user clicks 'Ok'.
    """
    hotelBookingForm = HotelBookingForm(fromDb)
    
    if context == 'default_context':
        area = Cui.CuiWhichArea
        scope = 'window'
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)            
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
    else:
        area = Cui.CuiNoArea
        scope = 'plan'
    contextlocator = CuiContextLocator(area, scope)
    
    if hotelBookingForm.loop() == Cfh.CfhOk: 
        region = 'REGION=%s' % hotelBookingForm.getRegion()
        selectedHotel = hotelBookingForm.getHotel()
        if selectedHotel == 'DEFAULT':
            selectedHotel = 'default'
        hotel = 'HOTEL=%s' % selectedHotel
        dateArg = AbsDate(hotelBookingForm.getDate())
        date = 'DATE=%s' % dateArg
        db = 'DB=%s' % fromDb
        contxt = 'CONTEXT=%s' % context
        fromStudio = 'FROMSTUDIO=TRUE'
        args = ' '.join([region, hotel, date, db, contxt, fromStudio])
        rpt = 'HotelBookingReport.py'

        contextlocator.reinstate()
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,
                                       area,
                                       scope,
                                       rpt,
                                       0,
                                       args)

        # Set all bookings as sent for bookings included in report.
        # This is only done for report run from database.
        if fromDb:
            bookingManager = H.HotelBookingManager()
            bookingManager.setBookingsAsSent(
                dateArg,
                hotelBookingForm.getHotel(),
                hotelBookingForm.getRegion(),
                True)
    else:
        return

"""
A form used for selecting information needed to create a hotel booking report.
"""
class HotelBookingForm(Cfh.Box):
    def __init__(self, fromDb=False, tptChoice=False, monthCombo=False,title=None):
        if not title:
            if tptChoice:
                title = "Hotel/Transport Forecast Preview"
            elif fromDb:
                title = 'Hotel Reservation Update'
            else:
                title = 'Hotel Reservation Daily'
        Cfh.Box.__init__(self, title)
        
        bookingManager = H.HotelBookingManager()

        drgn, = R.eval("planning_area.%filter_company_p%")
        if drgn.upper() == "ALL":
            reg_all="ALL;"
        else:
            reg_all=''
        regions = 'Flight Owner;' +reg_all +';'.join(['%s:%s' % (r.region.id, r.region.name)
                                        for r in bookingManager.getRegions()])
        airportList = [(airp[0], airp[1])
                       for airp in bookingManager.getAirports()]
        airportList.sort()
        airports = 'Airport;' + ';'.join(
            ['%s:%s %s' % (airpId, airpId, name) for (airpId, name) in airportList])
        airports += ';DEFAULT:Not Defined'
        hotelList = [(hotel.name, hotel.city, hotel.country, hotel.id)
                     for hotel in  bookingManager.getHotels()]
        hotelList.sort()
        hotels = 'Hotel;' + ';'.join(
            ['%s:%s %s %s' % (hotelId, name, city, country)
             for (name, city, country, hotelId) in hotelList])
        hotels += ';DEFAULT:Not Defined'
        if tptChoice:
            self.reptype = Cfh.String(self, 'REPTYPE', 10)
            self.reptype.setStyle(Cfh.CfhSChoiceRadioCol)
            self.reptype.setMenuString(";HOTEL:Hotel;TRANSPORT:Transport")
        else:
            self.reptype = None

        if drgn in [r.region.id for r in bookingManager.getRegions()]:
            self.region = Cfh.String(self, 'REGION', 10, drgn)
        else:
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
        if monthCombo:
            start, end = R.eval("fundamental.%pp_start%", "fundamental.%pp_end%")
            startm = str(start)[2:9].upper()
            l = []
            while start < end:
                l.append(str(start)[2:9].upper())
                start = start.addmonths(1)
            self.date = Cfh.String(self, 'DATE', 7, startm)
            self.date.setMenuString('Date;'+';'.join(l))
            self.date.setMenuOnly(1)
        else:
            now, = R.eval('fundamental.%now%')
            fromDate, = R.eval('fundamental.%pp_start%')
            toDate, = R.eval('fundamental.%pp_end% + 24:00')
            if now > toDate or now < fromDate:
                now = fromDate
            dateNow = AbsDate(now)
            self.date = HU.CfhDateInRange(self, 'DATE', dateNow, fromDate, toDate)
        self.date.setMandatory(1) 
        
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL')

        if tptChoice:
            rtyp = "FIELD;REPTYPE;Type\n"
        else:
            rtyp = ""
        layout = """
FORM;A_FORM;%s
%sFIELD;REGION;Flight Owner
FIELD;AIRPORT;Airport
FIELD;HOTEL;Hotel
FIELD;DATE;Date
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
        """ % (title, rtyp)

        (fd, fileName) = mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(layout)
        f.close()
        self.load(fileName)
        os.unlink(fileName)
        self.show(True)

    def getRegion(self):
        return self.region.valof()

    def getAirport(self):
        return self.airport.valof()

    def getHotel(self):
        v = self.hotel.valof()
        if v == "DEFAULT": return "default"
        return v
    
    def getDate(self):
        return self.date.valof()
        
    def getReportType(self):
        if self.reptype:
            return self.reptype.valof()
        return "HOTEL"


def runForecastPreview():
    frm = HotelBookingForm(tptChoice=True, monthCombo=True)
    if frm.loop() == Cfh.CfhOk:
        args = "REGION=%s AIRPORT=%s HOTEL=%s FROM_DATE=%s TO_DATE=%s FROMSTUDIO=TRUE" % (
            frm.getRegion(),
            frm.getAirport(),
            frm.getHotel(),
            AbsDate("01"+frm.getDate()),
            AbsDate(AbsTime("01"+frm.getDate()).addmonths(1) - RelTime(24,0))
            )
        if frm.getReportType() == "TRANSPORT":
            rpt = "TransportForecastReport.py"
            args += " TRANSPORT=%s" % frm.getHotel()
        else:
            rpt = "HotelForecastReport.py"
        
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,Cui.CuiNoArea,'plan',rpt,0,args)



def runPerformedPreview():
    frm = HotelBookingForm(tptChoice=True, monthCombo=True, title="Hotel/Transport Performed Preview")
    if frm.loop() == Cfh.CfhOk:
        args = "REGION=%s AIRPORT=%s HOTEL=%s FROM_DATE=%s TO_DATE=%s FROMSTUDIO=TRUE" % (
            frm.getRegion(),
            frm.getAirport(),
            frm.getHotel(),
            AbsDate("01"+frm.getDate()),
            AbsDate(AbsTime("01"+frm.getDate()).addmonths(1) - RelTime(24,0))
            )
        if frm.getReportType() == "TRANSPORT":
            rpt = "TransportPerformedReport.py"
            args += " TRANSPORT=%s" % frm.getHotel()
        else:
            rpt = "HotelPerformedReport.py"
        
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,Cui.CuiNoArea,'plan',rpt,0,args)





