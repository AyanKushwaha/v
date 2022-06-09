#

#
"""
Hotel Forecast Report.
"""

import carmensystems.rave.api as R
from AbsDate import AbsDate
from RelTime import RelTime
from carmensystems.publisher.api import *

import hotel_transport.HotelBookingReportUtil as HU
from report_sources.include.SASReport import SASReport
from utils.selctx import BasicContext

"""
HotelForecastReport is used to create a hotel forecast for a hotel
and a sas region for a given period.
"""


class HotelForecastReport(SASReport):
    def create(self):
        """
        Creates a HotelForecastReport.
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

        SASReport.create(self, 'Hotel Reservation Forecast', showPlanData=False, headerItems=headerItemsDict)

        infoBox = HU.infoBox('Forecast Info', fromDate, toDate)
        hotelBox = HU.hotelBox(hotelId)
        customerBox = HU.customerBox(region, hotelId)

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
                            self.getTableHeader(('Arrival',
                                                 'Incoming Flight',
                                                 'Departure',
                                                 'Next Flight',
                                                 'Rooms',
                                                 'Nights/Day Room')))

        bc = BasicContext()
        context = bc.getGenericContext()

        if region == "ALL":
            region_txt = "1 = 1"
        else:
            region_txt = 'report_hotel.%%region%% = "%s"' % region

        # Fetch assigned layovers
        layovers_assigned, = R.eval(context, R.foreach(
            R.iter(
                'report_hotel.forecast_layover_set',
                where=(
                    'report_hotel.%%adjusted_leg_end_hotel%% >= %s' % fromDate,
                    'round_down(report_hotel.%%adjusted_leg_end_hotel%%, 24:00) <= %s' % toDate,
                    'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                    '%s' % region_txt,
                    'report_hotel.%%layover_hotel_id_override%% = "%s"' % hotelId,
                    'fundamental.%is_roster%'
                ),
                sort_by=('report_hotel.%leg_end_hotel%', 'report_hotel.%next_leg_start_hotel%', 'report_hotel.%nights%')
            ),
            'report_hotel.%leg_end_hotel%',
            'report_hotel.%next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%dep_flight_nr%'))

        # Fetch open layovers
        layovers_open, = R.eval("sp_crrs", R.foreach(
            R.iter(
                'report_hotel.forecast_layover_set',
                where=(
                    'report_hotel.%%adjusted_leg_end_hotel%% >= %s' % fromDate,
                    'round_down(report_hotel.%%adjusted_leg_end_hotel%%, 24:00) <= %s' % toDate,
                    'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                    '%s' % region_txt,
                    'report_hotel.%%layover_hotel_id_override%% = "%s"' % hotelId,
                    'fundamental.%is_roster%'
                ),
                sort_by=('report_hotel.%leg_end_hotel%', 'report_hotel.%next_leg_start_hotel%', 'report_hotel.%nights%')
            ),
            'report_hotel.%leg_end_hotel%',
            'report_hotel.%next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%dep_flight_nr%'))

        # Add the two together
        layovers = {}
        for list in layovers_assigned, layovers_open:
            for (_, checkIn, checkOut, nights, arrFlightNr, depFlightNr) in list:
                key = (checkIn, checkOut, nights, arrFlightNr, depFlightNr)
                if key in layovers:
                    layovers[key] += 1
                else:
                    layovers[key] = 1

        # Prepare calendar dictionary and initiate with 0 rooms for each day.
        days, = R.eval('((%s - %s) / 24:00) + 1' % (toDate, fromDate))
        nightCalendar = {}
        for day in range(days):
            nightCalendar['%s' % (fromDate + RelTime(day * 24, 0))] = 0

        color = True

        for (checkIn, checkOut, nights, arrFlightNr, depFlightNr), assigned in sorted(layovers.items()):

            color = not color

            if color:
                bgColor = 'dedede'
            else:
                bgColor = 'ffffff'

            checkInStr = str(AbsTime(checkIn))
            checkOutStr = str(AbsTime(checkOut))

            bookingBox.page()
            if depFlightNr == "?":
                nights = 1
                nightsText = '?'
            elif nights == 0:
                nightsText = 'D'
            elif nights > 1:
                nightsText = 'C'
            else:
                nightsText = ''

            if depFlightNr == "?":
                checkOutStr = "?"

            bookingBox.add(Row(Text('%s' % checkInStr),
                               Text('%s' % arrFlightNr),
                               Text('%s' % checkOutStr),
                               Text('%s' % depFlightNr),
                               Text('%s' % assigned),
                               Text('%s' % nightsText),
                               background='#%s' % bgColor))

            # Add rooms needed to calendar dictionary
            date = AbsDate(checkIn)
            if nights == 0: nights += 1
            for i in range(nights):
                if date <= toDate:
                    dateKey = '%s' % date
                    nightCalendar[dateKey] = nightCalendar[dateKey] + assigned
                    date += RelTime(24, 0)
                else:
                    break

        if len(layovers) <= 0:
            bookingBox.add(Row(Text('No Reservations', colspan=5)))

        self.add(bookingBox)

        calendarHeader = Row(Text(''), font=Font(weight=BOLD))
        calendarNight = Row(Text('Rooms'))
        totalNight = 0
        for day in range(days):
            date = fromDate + RelTime(day * 24, 0)
            nightAmount = nightCalendar['%s' % date]
            totalNight += nightAmount
            calendarHeader.add(Text('%2s' % date.split()[2], align=RIGHT))
            calendarNight.add(Text('%s' % nightAmount, align=RIGHT))

        calendarHeader.add(Text('Total'))
        calendarNight.add(Text('%s' % totalNight, align=RIGHT))

        self.add(Row(' '))
        self.add(Isolate(Column(calendarHeader,
                                calendarNight,
                                border=border_all(1))))
