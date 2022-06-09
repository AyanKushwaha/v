#

#
"""
Hotel Performed Report.
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as R
from tempfile import mkstemp
from AbsDate import AbsDate
from RelTime import RelTime
from utils.divtools import default as D
import carmstd.cfhExtensions
import hotel_transport.HotelBookingReportUtil as HU
import hotel_transport.HotelBookingData as H
from report_sources.include.SASReport import SASReport
from utils.selctx import BasicContext
from utils.divtools import fd_parser

def save(args):
    """
    Creates a hotel performed report.

    arg0 regioN
    arg1 hotel
    arg2 fromDate
    arg3 toDate
    """
    (fd, fileName) = mkstemp(suffix='.pdf',
                             prefix='HotelPerformed',
                             dir=H.getExportDir(),
                             text=True)

    region = 'REGION=%s' % args[0]
    hotel = 'HOTEL=%s' % args[1]
    fromDate = 'FROM_DATE=%s' % args[2]
    toDate = 'TO_DATE=%s' % args[3]
    args = ' '.join([region, hotel, fromDate, toDate])

    return generateReport('report_sources.hidden.HotelPerformedReport',
                          fileName,
                          PDF,
                          args)

"""
HotelPerformedReport is used to create a hotel performed report for a region,
hotel and for a given period.
"""
class HotelPerformedReport(SASReport):

    def create(self):
        """
        Creates a HotelPerformedReport.
        Uses HotelBookingData to retrieve some of the data needed
        for the report.
        """
        
        region = self.arg('REGION')
        hotelId = self.arg('HOTEL')
        fromDate = AbsDate(self.arg('FROM_DATE'))
        toDate = AbsDate(self.arg('TO_DATE'))
        fromStudio = (self.arg('FROMSTUDIO') == 'TRUE')
        
        studioRegion, = R.eval('planning_area.%filter_company_p%')
        isAllRegions = (studioRegion == 'ALL')
        
        headerItemsDict = HU.getHeaderItems(fromStudio, isAllRegions)
                
        SASReport.create(self, 'Hotel Reservation Performed', 
                         showPlanData=False, margins=padding(10,15,10,15),
                         headerItems=headerItemsDict)

        infoBox = HU.infoBox('Performed Info', fromDate, toDate)
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
        bookingBox = Column(Row(Text('Arrival',
                                     colspan=3,
                                     font=Font(weight=BOLD)),
                                Text('No. Of',
                                     colspan=2,
                                     font=Font(weight=BOLD)),
                                Text('Departure',
                                     colspan=4,
                                     font=Font(weight=BOLD))),
                            self.getTableHeader(('Company',
                                                 'Flight',
                                                 'Local Time',
                                                 'FD',
                                                 'CC',
                                                 'Date',
                                                 'Flight',
                                                 'Local Time',
                                                 ' ')))

        bc = BasicContext()
        context = bc.getGenericContext()

        if region == "ALL":
            region_txt="1 = 1"
        else:
            region_txt='report_hotel.%%region%% = "%s"' % region

        layovers, = R.eval(context, R.foreach(
            R.iter(
            'report_hotel.performed_layover_set',
            where=('report_hotel.%%adjusted_leg_end_hotel%% >= %s' % fromDate,
                   'round_down(report_hotel.%%adjusted_leg_end_hotel%%, 24:00) <= %s' % toDate,
                   'report_hotel.%has_layover_hotel_id%',
                   'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                   '%s' % region_txt,
                   'report_hotel.%%layover_hotel_id_override%% = "%s"' % hotelId,
                   'report_hotel.%assigned% > 0'),
            sort_by=('report_hotel.%leg_end_hotel%',
                     'report_hotel.%next_leg_start_hotel%')),
            'report_hotel.%formatted_arrival_day%',
            'report_hotel.%arrival_day%',
            'report_hotel.%arrival_time%',
            'report_hotel.%formatted_departure_day%',
            'report_hotel.%departure_time%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%dep_flight_nr%',
            'report_hotel.%assigned_fc%',
            'report_hotel.%assigned_cc%',
            'report_hotel.%region%',
            'report_hotel.%is_airport_hotel%',
            'report_hotel.%nights%'))

        # Prepare calendar dictionary and initiate with 0 rooms for each day.
        days = int((toDate - fromDate)/RelTime(24,0)) + 1
        ccCalendar = {}
        fcCalendar = {}
        for day in  range(days):
            ccCalendar['%s' % (fromDate + RelTime(day * 24, 0))] = 0
            fcCalendar['%s' % (fromDate + RelTime(day * 24, 0))] = 0

        color = True
        prevArrivalDay = None

        index = 1 #this is used for page breaks
        for (ix, formatArrivalDay, arrivalDay, arrivalTime, 
             formatDepartureDay, departureTime, arrFlightNr, 
             depFlightNr, assignedFC, assignedCC, 
             acRegion, isAirportHotel, nights) in layovers:
            
            color = not color

            if not prevArrivalDay or arrivalDay != prevArrivalDay:
                bookingBox.add(Row(Text(formatArrivalDay, font=Font(weight=BOLD))))
                color = True
            
            bookingBox.page()
            
            prevArrivalDay = arrivalDay

            if color:
                bgColor = 'dedede'
            else:                
                bgColor = 'ffffff'
            
            if depFlightNr == '?':
                departureTime = "?"
                nights = 1

            bookingBox.add(Row(Text('%s' % acRegion),
                               Text('%s' % arrFlightNr),
                               Text('%s' % arrivalTime),
                               Text('%s' % assignedFC),
                               Text('%s' % assignedCC),
                               Text('%s' % formatDepartureDay),
                               Text('%s' % depFlightNr),
                               Text('%s' % departureTime),
                               Text('%s' % ('', 'Airport')[isAirportHotel]),
                               background='#%s' % bgColor))
            bookingBox.page()

            # Add rooms needed to calendar dictionary
            date = AbsDate(arrivalDay)
            for i in range(nights):
                if date <= toDate:
                    dateKey = '%s' % date
                    ccCalendar[dateKey] = ccCalendar[dateKey] + assignedCC
                    fcCalendar[dateKey] = fcCalendar[dateKey] + assignedFC
                    date += RelTime(24, 0)
                else:
                    break

        if len(layovers) <= 0:
            bookingBox.add(Row(Text('No Reservations', colspan=5)))

        self.add(bookingBox)

        calendarHeader = Row(Text(''), font=Font(weight=BOLD))
        calendarCC = Row(Text('CC'))
        calendarFC = Row(Text('FD'))
        totalCC = 0
        totalFC = 0
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
