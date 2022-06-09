"""
Transport Booking Data Handler
"""

from tm import TM

import carmensystems.rave.api as R
from modelserver import TableManager
import modelserver
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import Cui
import Crs
import sys
import os
import os.path
import Errlog
from utils.selctx import BasicContext
from utils.RaveData import DataClass
from utils.performance import clockme, log

NULL_FLIGHT_NR = "-00001"


def getExportDir():
    """
    Retrieves the directory where transport reports are written.
    """
    # Where to store export files
    exportDir = Crs.CrsGetModuleResource("transport", Crs.CrsSearchModuleDef, "ExportDirectory")
    # Create directory if it does not exist
    if not os.path.exists(exportDir):
        os.makedirs(exportDir)
    return exportDir

def getHotelRegion(hotelId):
    """
    convert country to region
    """
    country = None
    try:
        hotel = TM.hotel.search('(id=%s)' % hotelId)
        for h in hotel:
            if h:
                country = h.country
                break
    except modelserver.ReferenceError:
        pass
    if country == "SE":
        region="SKS"
    elif country == "NO":
        region="SKN"
    else:
        region="SKD"
    return region

def fromHotel(fromHotel):
    """
    auxiliar conversion function for searching in tables if a booking
    is made from hotel to airport or from airport to hotel
    """
    if fromHotel:
        return 'true'
    else:
        return 'false'
    

"""
Exception class used when no customer is found.
"""
class CustomerNotFoundException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
"""
Exception class used when no hotel is found.
"""
class HotelNotFoundException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()
"""
Exception class used when no transport is found.
"""
class TransportNotFoundException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()   

class TransportBookingManager:
    """
    Transport Booking Manager Class
    """

    def __init__(self, context = None):
        if not context:
            bc = BasicContext()
            context = bc.getGenericContext()
        self.context = context

    def refresh(self):
        """
        Reloads the table where transport bookings are stored.
        """
        Cui.CuiReloadTable('transport_booking')

    def createBooking(self, isHotelToAirport, region, crewAmount, crewAmountDH, transportId, hotelId,
                      flightDay, pickUpTime, flightNr, flightStart, flightDepStn):
        """
        Creates a new transport booking line in the model.
        """
        airport = TM.airport.getOrCreateRef((flightDepStn,))
        # Note that the model server will always provide the
        # latest data from flight_leg, even when running in
        # published mode. In this case it does not matter
        # though. The lookup will still succeed because no
        # legs are being removed.

        is_ground_duty = flightNr.strip() == NULL_FLIGHT_NR
        
        flight = None

        if is_ground_duty:
            print "\n   ### is_ground_duty  flightNr:", flightNr, "\n"
            flightArrStn = flightDepStn  # a bit meaningless!?
        else:
            try:
                flight = TM.flight_leg[(flightStart, flightNr, airport)]
                flightArrStn = str(flight.getRefI('ades'))
            except modelserver.EntityNotFoundError:
                Errlog.log(
                    "%s %s %s flight doesnt exist in flight_leg table\n" % (
                    flightStart, flightNr, airport) + \
                    "Region: %s, Hotel: %s, Transport: %s, Date: %s" % (
                    region, hotelId, transportId, flightDay))

        if not hotelId:
            if isHotelToAirport:
                Errlog.log('No hotel found at station %s.' % flightDepStn)
            else:
                Errlog.log('No hotel found at station %s.' % flightArrStn)                 
            return

        if not transportId:
            if isHotelToAirport:
                Errlog.log('No transport found at station %s.' % flightDepStn)
            else:
                Errlog.log('No transport found at station %s.' % flightArrStn)
            return
 
        try:
            # Get the first (next) match in the search result.
            customer = TM.hotel_customer.search(
                '(region=%s)' % (region)).next()
        except StopIteration:
            Errlog.log(
                'No customer found in region %s.' % (region))
            return

        transport = TM.transport.getOrCreateRef((transportId,))
        hotel = TM.hotel.getOrCreateRef((hotelId,))
        booking = TM.transport_booking.create((TM.createUUID(),))

        booking.cancelled = False
        booking.num_crew = crewAmount
        booking.num_crew_dh = crewAmountDH
        booking.flight_day = flightDay
        booking.pick_up = pickUpTime
        booking.flight = flight
        booking.transport = transport
        booking.hotel = hotel
        booking.customer = customer
        booking.sent = False
        booking.from_hotel = isHotelToAirport
        
        return

    @clockme
    def createUpdateBookings(self, fromDate, toDate):
        """
        Creates transport bookings for crew going from Hotel to Airport
        and open trips for given date and next two days.
        In the first Rave iterator search, the value 'crew_needing_transport..'
        looks at both assigned trips and open trips.
        Works also as update.
        """

        layoverDutiesFromHotelQuery = R.foreach(
            R.iter('iterators.leg_set',
                   where=('report_transport.%%flight_time_from_hotel%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_hotel%% < %s' % toDate,
                          'report_transport.%need_transport_from_hotel%')),
            'report_transport.%crew_needing_transport_from_hotel%',
            'report_transport.%crew_needing_transport_from_hotel_dh%',
            'report_transport.%transport_id_from_hotel%',
            'report_transport.%hotel_id_from_hotel%',
            'report_transport.%flight_time_from_hotel%',
            'report_transport.%pick_up_time_from_hotel%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%')

        layoverDutiesFromAirportQuery = R.foreach(
            R.iter('iterators.leg_set',
                   where=('report_transport.%%flight_time_from_airport%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_airport%% < %s' % toDate,
                          'report_transport.%need_transport_from_airport%')),
            'report_transport.%crew_needing_transport_from_airport%',
            'report_transport.%crew_needing_transport_from_airport_dh%',
            'report_transport.%transport_id_from_airport%', 
            'report_transport.%hotel_id_from_airport%',
            'report_transport.%flight_time_from_airport%',
            'report_transport.%pick_up_time_from_airport%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%')
        
        layoverDutiesFromHotel, layoverDutiesFromAirport = R.eval('sp_crew', layoverDutiesFromHotelQuery, layoverDutiesFromAirportQuery)

        planBookings = []

        for (ix, crewAmount, crewAmountDH, transportId, hotelId, flightDay, pickUpTime,
             flightNr, flightStart, flightDepStn) in layoverDutiesFromHotel:

            region = getHotelRegion(hotelId)
            # Use BookingEntity so that entity can be searched for in list
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = BookingEntity(True,
                                           region,
                                           crewAmount,
                                           crewAmountDH,
                                           transportId,
                                           hotelId,
                                           flightDay,
                                           pickUpTime,
                                           flightNr,
                                           flightStart,
                                           flightDepStn)
                i = planBookings.index(tryBooking)
                pass
            except ValueError:
                planBookings.append(tryBooking)

        for (ix, crewAmount, crewAmountDH, transportId, hotelId, flightDay, pickUpTime, 
             flightNr, flightStart, flightDepStn) in layoverDutiesFromAirport:
            
            region = getHotelRegion(hotelId)
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = BookingEntity(False,
                                           region,
                                           crewAmount,
                                           crewAmountDH,
                                           transportId,
                                           hotelId,
                                           flightDay,
                                           pickUpTime,
                                           flightNr,
                                           flightStart,
                                           flightDepStn)
                i = planBookings.index(tryBooking)
                pass
            except ValueError:
                planBookings.append(tryBooking)
            
        searchStr = '(&(flight_day>=%s)(flight_day<%s)(cancelled=false))' % (
                fromDate, toDate)

        dbBookings = TM.transport_booking.search(searchStr)

        for booking in dbBookings:
            try:
                # Transport id might not exist. Get only the id.
                transportId = str(booking.getRefI('transport'))
                # same with hotel id.
                hotelId = str(booking.getRefI('hotel'))

                is_ground_duty = booking.flight == None
                if is_ground_duty:
                    print " ### is_ground_duty:", is_ground_duty
                # Airport table should not be used. Get the referring string.
                flightDepStn = "airport standby" if is_ground_duty else str(booking.flight.getRefI('adep'))
                # Create BookingEntity to search list of bookings in plan
                # ValueError thrown if no match
                i = planBookings.index(
                    BookingEntity(booking.from_hotel,
                                  booking.customer.region.id,
                                  booking.num_crew,
                                  booking.num_crew_dh,
                                  transportId,
                                  hotelId,
                                  booking.flight_day,
                                  booking.pick_up,
                                  NULL_FLIGHT_NR if is_ground_duty else booking.flight.fd,
                                  booking.flight_day if is_ground_duty else booking.flight.udor,
                                  flightDepStn))
                    # Remove match
                planBookings.pop(i)
            except ValueError:
                booking.cancelled = True
                booking.sent = False
            except modelserver.ReferenceError:
                Errlog.log("Bad reference in transport_booking table:" + \
                           "%s flight or %s customer reference doesn't exist in referred table" % (
                    booking.getRefI('flight'), booking.getRefI('customer')))

        for booking in planBookings:
            log("Creating booking2 for %s %s" % (booking.region, booking.transportId))
            # Remaining bookings are new
            self.createBooking(booking.isHotelToAirport,
                               booking.region,
                               booking.crewAmount,
                               booking.crewAmountDH,
                               booking.transportId,
                               booking.hotelId,
                               booking.flightDay,
                               booking.pickUpTime,
                               booking.flightNr,
                               booking.flightStart,
                               booking.flightDepStn)

        #Now we look through open trips wich don't have any crew assigned#
        openTripsFromHotel, = R.eval('sp_crrs', R.foreach(
            R.iter('report_transport.layover_set_from_hotel',
                   where=('report_transport.%%flight_time_from_hotel%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_hotel%% < %s' % toDate,
                          'report_common.%is_open_trip%',
                          'report_transport.%crew_needing_transport_from_hotel_roster% = 0',
                          'report_transport.%crew_needing_transport_from_hotel_open_trip% > 0')),
            'report_transport.%crew_needing_transport_from_hotel_open_trip%',
            'report_transport.%crew_needing_transport_from_hotel_open_trip_dh%',
            'report_transport.%transport_id_from_hotel%',
            'report_transport.%hotel_id_from_hotel%',
            'report_transport.%flight_time_from_hotel%',
            'report_transport.%pick_up_time_from_hotel%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%'))
        
        openTripsFromAirport, = R.eval('sp_crrs', R.foreach(
            R.iter('report_transport.layover_set_from_airport',
                   where=('report_transport.%%flight_time_from_airport%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_airport%% < %s' % toDate,
                          'report_common.%is_open_trip%',
                          'report_transport.%crew_needing_transport_from_airport_roster% = 0',
                          'report_transport.%crew_needing_transport_from_airport_open_trip% > 0')),
            'report_transport.%crew_needing_transport_from_airport_open_trip%',
            'report_transport.%crew_needing_transport_from_airport_open_trip_dh%',
            'report_transport.%transport_id_from_airport%',
            'report_transport.%hotel_id_from_airport%',
            'report_transport.%flight_time_from_airport%',
            'report_transport.%pick_up_time_from_airport%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%'))

        planBookings = []
        for (ix, crewAmount, crewAmountDH, transportId, hotelId, flightDay, pickUpTime,
             flightNr, flightStart, flightDepStn) in openTripsFromHotel:

            region = getHotelRegion(hotelId)
            # Use BookingEntity so that entity can be searched for in list
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = BookingEntity(True,
                                           region,
                                           crewAmount,
                                           crewAmountDH,
                                           transportId,
                                           hotelId,
                                           flightDay,
                                           pickUpTime,
                                           flightNr,
                                           flightStart,
                                           flightDepStn)
                i = planBookings.index(tryBooking)
                pass
            except ValueError:
                planBookings.append(tryBooking)

        for (ix, crewAmount, crewAmountDH, transportId, hotelId, flightDay, pickUpTime,
             flightNr, flightStart, flightDepStn) in openTripsFromAirport:

            region = getHotelRegion(hotelId)
            # Use BookingEntity so that entity can be searched for in list
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = BookingEntity(False,
                                           region,
                                           crewAmount,
                                           crewAmountDH,
                                           transportId,
                                           hotelId,
                                           flightDay,
                                           pickUpTime,
                                           flightNr,
                                           flightStart,
                                           flightDepStn)
                i = planBookings.index(tryBooking)
                pass
            except ValueError:
                planBookings.append(tryBooking)

        result = []
        for planBooking in planBookings:
            if planBooking.isHotelToAirport:
                from_hotel = 'true'
            else:
                from_hotel = 'false'
            searchStr = '(&(from_hotel=%s)(flight.udor=%s)(customer.region.id=%s)(transport.id=%s)' %(
                from_hotel, AbsDate(planBooking.flightStart),planBooking.region,planBooking.transportId)
            searchStr += '(flight_day=%s)(flight.adep=%s)(flight.fd=%s)(hotel.id=%s))' %(
                planBooking.flightDay,planBooking.flightDepStn,planBooking.flightNr,planBooking.hotelId)
            dbBookings = TM.transport_booking.search(searchStr)

            try:
                dbBooking = dbBookings.next()
            except StopIteration:
                result.append(planBooking)
                continue

            newPlanBooking = False
            while True:
                if planBooking.isConsideredEqual(dbBooking):
                    pass
                elif not dbBooking.cancelled:
                    dbBooking.cancelled = True
                    dbBooking.sent = False
                    newPlanBooking = True
                try:
                    dbBooking = dbBookings.next()
                except StopIteration:
                    break
                
            if newPlanBooking:
                result.append(planBooking)

        booked_transports = []
        for booking in result:
            log("Creating booking for %s %s" % (booking.region, booking.transportId))
            self.createBooking(booking.isHotelToAirport,
                               booking.region,
                               booking.crewAmount,
                               booking.crewAmountDH,
                               booking.transportId,
                               booking.hotelId,
                               booking.flightDay,
                               booking.pickUpTime,
                               booking.flightNr,
                               booking.flightStart,
                               booking.flightDepStn)
            booked_transports.append(booking)
        return booked_transports

    @clockme
    def getPlanBookings(self, fromDate, transportId, hotelId, airportId, region, context=None, toDate=None):
        """
        Gets transport bookings from plan data for a date and two days forward
        and for a transport and sas region.
        """
        if context is None:
            context = self.context
        
        # Bookings are made for three days
        if not toDate:
            toDate = fromDate + RelTime(72, 0)

        if region == "ALL":
            region_txt="1 = 1"
        else:
            region_txt='report_hotel.%%region%% = "%s"' % region

        layoverDutiesFromHotelQuery = R.foreach(
            R.iter('iterators.leg_set',
                   where=('report_transport.%%flight_time_from_hotel%% < %s' % toDate,
                          'report_transport.%%flight_time_from_hotel%% >= %s' % fromDate,
                          '%s' % region_txt,
                          'report_transport.%need_transport_from_hotel%',
                          'report_transport.%%transport_id_from_hotel%% = "%s"' % transportId,
                          'report_transport.%%hotel_id_from_hotel%% = "%s"' % hotelId,
                          'report_transport.%%airport_from_hotel%% = "%s"' % airportId)),
            'report_transport.%region%',
            'report_transport.%crew_needing_transport_from_hotel%',
            'report_transport.%crew_needing_transport_from_hotel_dh%',
            'report_transport.%airport_from_hotel%',
            'report_transport.%transport_id_from_hotel%',
            'report_transport.%hotel_id_from_hotel%',
            'report_transport.%flight_time_from_hotel%',
            'report_transport.%pick_up_time_from_hotel%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%')
        layoverDutiesFromAirportQuery = R.foreach(
            R.iter('iterators.leg_set',
                   where=('report_transport.%%flight_time_from_airport%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_airport%% < %s' % toDate,
                          '%s' % region_txt,
                          'report_transport.%need_transport_from_airport%',
                          'report_transport.%%transport_id_from_airport%% = "%s"' % transportId,
                          'report_transport.%%hotel_id_from_airport%% = "%s"' % hotelId,
                          'report_transport.%%airport_from_airport%% = "%s"' % airportId)),
            'report_transport.%region%',
            'report_transport.%crew_needing_transport_from_airport%',
            'report_transport.%crew_needing_transport_from_airport_dh%',
            'report_transport.%airport_from_airport%',
            'report_transport.%transport_id_from_airport%',
            'report_transport.%hotel_id_from_airport%',
            'report_transport.%flight_time_from_airport%',
            'report_transport.%pick_up_time_from_airport%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%')
        
        layoverDutiesFromHotel, layoverDutiesFromAirport =  R.eval(context, layoverDutiesFromHotelQuery, layoverDutiesFromAirportQuery)
        #layoverDutiesFromHotel, = R.eval(context, layoverDutiesFromHotelQuery)
        #layoverDutiesFromAirport, = R.eval(context, layoverDutiesFromAirportQuery)    

        result = []
        
        for (ix, region, crewAmount, crewAmountDH, airport, transportId, hotelId, flightTime,
             pickUpTime, flightNr, flightDepStn, flightArrStn) in layoverDutiesFromHotel:
            try:
                # Only create one BookingEntity for all crew in the same flight
                tryBooking = TransportBooking(True,
                                              region,
                                              hotelId,
                                              crewAmount,
                                              crewAmountDH,
                                              flightNr,
                                              flightTime,
                                              pickUpTime,
                                              flightDepStn,
                                              flightArrStn)
                i = result.index(tryBooking)
            except ValueError:
                result.append(tryBooking)
                    
        for (ix, region, crewAmount, crewAmountDH, airport, transportId, hotelId, flightTime,
             pickUpTime, flightNr, flightDepStn, flightArrStn) in layoverDutiesFromAirport:
            
            try:
                # Only create one BookingEntity for all crew in the same flight
                tryBooking = TransportBooking(False,
                                              region,
                                              hotelId,
                                              crewAmount,
                                              crewAmountDH,
                                              flightNr,
                                              flightTime,
                                              pickUpTime,
                                              flightDepStn,
                                              flightArrStn)
                i = result.index(tryBooking)
            except ValueError:
                result.append(tryBooking)
                
        #Now we look through open trips#
        openTripsFromHotelQuery = R.foreach(
            R.iter('report_transport.layover_set_from_hotel',
                   where=('report_transport.%%flight_time_from_hotel%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_hotel%% < %s' % toDate,
                          '%s' % region_txt,
                          'report_common.%is_open_trip%',
                          'report_transport.%crew_needing_transport_from_hotel_roster% = 0',
                          'report_transport.%crew_needing_transport_from_hotel_open_trip% > 0',
                          'report_transport.%%transport_id_from_hotel%% = "%s"' % transportId,
                          'report_transport.%%hotel_id_from_hotel%% = "%s"' % hotelId,
                          'report_transport.%%airport_from_hotel%% = "%s"' % airportId)),
            'report_transport.%region%',
            'report_transport.%crew_needing_transport_from_hotel_open_trip%',
            'report_transport.%crew_needing_transport_from_hotel_open_trip_dh%',
            'report_transport.%hotel_id_from_hotel%',
            'report_transport.%flight_time_from_hotel%',
            'report_transport.%pick_up_time_from_hotel%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%')
        
        openTripsFromAirportQuery = R.foreach(
            R.iter('report_transport.layover_set_from_airport',
                   where=('report_transport.%%flight_time_from_airport%% >= %s' % fromDate,
                          'report_transport.%%flight_time_from_airport%% < %s' % toDate,
                          '%s' % region_txt,
                          'report_common.%is_open_trip%',
                          'report_transport.%crew_needing_transport_from_airport_roster% = 0',
                          'report_transport.%crew_needing_transport_from_airport_open_trip% > 0',
                          'report_transport.%%transport_id_from_airport%% = "%s"' % transportId,
                          'report_transport.%%hotel_id_from_airport%% = "%s"' % hotelId,
                          'report_transport.%%airport_from_airport%% = "%s"' % airportId)),
            'report_transport.%region%',
            'report_transport.%crew_needing_transport_from_airport_open_trip%',
            'report_transport.%crew_needing_transport_from_airport_open_trip_dh%',
            'report_transport.%hotel_id_from_airport%',
            'report_transport.%flight_time_from_airport%',
            'report_transport.%pick_up_time_from_airport%',
            'report_transport.%flight_nr%',
            'report_transport.%flight_start%',
            'report_transport.%flight_dep_stn%',
            'report_transport.%flight_arr_stn%')

        openTripsFromHotel, openTripsFromAirport = R.eval('sp_crrs', openTripsFromHotelQuery, openTripsFromAirportQuery)
        planBookings = []

        for (ix, region, crewAmount, crewAmountDH, hotelId, flightTime, pickUpTime, flightNr,
             flightStart, flightDepStn, flightArrStn) in openTripsFromHotel:

            # Use BookingEntity so that entity can be searched for in list
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = TransportBooking(True,
                                              region,
                                              hotelId,
                                              crewAmount,
                                              crewAmountDH,
                                              flightNr,
                                              flightTime,
                                              pickUpTime,
                                              flightDepStn,
                                              flightArrStn)
                i = result.index(tryBooking)
                pass
            except ValueError:
                result.append(tryBooking)
                
        for (ix, region, crewAmount, crewAmountDH, hotelId, flightTime, pickUpTime, flightNr,
             flightStart, flightDepStn, flightArrStn) in openTripsFromAirport:

            # Use BookingEntity so that entity can be searched for in list
            try:
                # Only create one BookingEntity for all crew in the same flight
                # ValueError thrown if no match
                tryBooking = TransportBooking(False,
                                              region,
                                              hotelId,
                                              crewAmount,
                                              crewAmountDH,
                                              flightNr,
                                              flightTime,
                                              pickUpTime,
                                              flightDepStn,
                                              flightArrStn)
                i = result.index(tryBooking)
                pass
            except ValueError:
                result.append(tryBooking)
                
        result.sort()
        return result

    def isNotSentDbBookings(self, fromDate, toDate, transport, hotel, airport, region, includeCancelled):
        """
        Checks if there are unsent bookings at a date for transport, airport and region.
        """
        if region == "ALL":
            region = "*"
        searchStr = '(&(flight_day>=%s)(flight_day<%s)(transport=%s)(sent=false)' % (
            fromDate, toDate, transport)
        if not includeCancelled: searchStr += '(cancelled=false)'
        searchStr += '(|(flight.adep=%s)(flight.ades=%s))(hotel=%s)(customer=%s))' % (
            airport, airport, hotel, region)
            
        for booking in TM.transport_booking.search(searchStr):
            return True
        return False

    def isSentDbBookings(self, fromDate, toDate, transport, hotel, airport, region):
        """
        Checks if there are sent bookings at a period for transport, airport and region.
        """
        if region == "ALL":
            region = "*"
        searchStr = '(&(flight_day>=%s)(flight_day<=%s)(transport=%s)(sent=true)' % (
            fromDate, toDate, transport)
        searchStr += '(|(flight.adep=%s)(flight.ades=%s))(hotel=%s)(customer=%s))' % (
            airport, airport, hotel, region)
            
        for booking in TM.transport_booking.search(searchStr):
            return True
        return False

    def setBookingsAsSent(self, fromDate, toDate, transportId, hotelId, airportId, region):
        """
        Sets all bookings as sent for given date, transport, airport and region.
        """
        fromDate = AbsDate(fromDate)
        toDate = AbsDate(toDate)
        if region == "ALL":
            region = "*"

        searchStr = '(&(flight_day>=%s)(flight_day<=%s)(transport=%s)(hotel=%s)(sent=false)' % (
            fromDate, toDate, transportId, hotelId)
        searchStr += '(| (flight.adep=%s) (flight.ades=%s) (!(flight=*)) ) (customer=%s))' % (
            airportId, airportId, region)
            
        bookings = TM.transport_booking.search(searchStr)

        for booking in bookings:
            booking.sent = True

        return
    
    # Note: The function below is not (yet) used. It could be used to improve
    #       performance of the TransportBookingRun.
    @clockme
    def getUnsentBookingCategories(self, fromDate, toDate):
        s = set()
        searchStr = '(&(flight_day>=%s)(flight_day<%s)(sent=false)(cancelled=false))' % (fromDate, toDate)                
        bookings = TM.transport_booking.search(searchStr)
        for booking in bookings:
            if booking.from_hotel:
                b = (str(booking.getRefI('customer')), str(booking.getRefI('transport')), str(booking.getRefI('hotel')), str(booking.flight.getRefI('adep')))
            else:
                b = (str(booking.getRefI('customer')), str(booking.getRefI('transport')), str(booking.getRefI('hotel')), str(booking.flight.getRefI('ades')))
            if b[2] == 'default': continue # Don't generate booking reports for 'default' hotel
            s.add(b)
        return list(s)
                
    @clockme
    def setTodayBookingsAsNotSent(self, fromDate):
        """
        Sets all bookings as not sent for given date, hotel 
        and region, for today and 72hours forward.
        """
        toDate = fromDate + RelTime(72, 0)
        searchStr = '(&(flight_day>=%s)(flight_day<%s)(sent=true))' % (
            fromDate, toDate)
                                                                            
        bookings = TM.transport_booking.search(searchStr)
        
        for booking in bookings:
            booking.sent = False

        return

    @clockme
    def printDbBookings(self, fromDate, transportId, hotelId, airportId, region, prefix):
        fromDate = AbsTime(fromDate)
        toDate = fromDate + RelTime(72, 0)
        if region == "ALL":
            region = "*"
        searchStr = '(&(flight_day>=%s)(flight_day<%s)(transport=%s)(|(flight.adep=%s)(flight.ades=%s))' % (
                fromDate, toDate, transportId, airportId, airportId)
        searchStr += '(hotel=%s)(customer=%s)(sent=false))' % (
            hotelId, region)
        bookings = TM.transport_booking.search(searchStr)
        bookings = list(bookings)
        print prefix, "Length=",len(bookings)
        for booking in bookings:
            print prefix, str(booking)
    
    def getNewBookings(self, date, transportId, hotelId, airportId, region, context=None):
        """
        Gets new bookings by comparing bookings in plan and
        current bookings in database (not cancelled).
        """
        new = []
        bookingsFromHotel = self.getDbBookings(False, date, transportId, hotelId, airportId, region)
        bookingsToHotel = self.getDbBookings(True, date, transportId, hotelId, airportId, region)

        planBookings = self.getPlanBookings(date, transportId, hotelId, airportId, region, context)

        
        for booking in planBookings:
            try:
                bookingsFromHotel.index(booking)
                bookingsToHotel.index(booking)
            except ValueError:
                new.append(booking)

        new.sort()
        return new

    @clockme
    def getDbBookings(self, isHotelToAirport, fromDate, transportId,
                      hotelId, airportId, region, cancelled=False):
        """
        Gets transport bookings in the database from date and three days forward
        for a transport and sas region. Either cancelled or current bookings can
        be fetched.
        """
        fromDate = AbsTime(fromDate)
        toDate = fromDate + RelTime(72, 0)
        if cancelled:
            cancelled = 'true'
        else:
            cancelled = 'false'
        if region == "ALL":
            region = "*"
            
        if isHotelToAirport == None:
            searchStr = '(&(flight_day>=%s)(flight_day<%s)(transport=%s) (| (flight.adep=%s) (flight.ades=%s) (!(flight=*)) )' % (
                fromDate, toDate, transportId, airportId, airportId)
        elif isHotelToAirport:
            searchStr = '(&(flight_day>=%s)(flight_day<%s)(transport=%s) (| (flight.adep=%s) (!(flight=*)) ) (from_hotel=true)' % (
                fromDate, toDate, transportId, airportId)
        else:
            searchStr = '(&(flight_day>=%s)(flight_day<%s)(transport=%s)(| (flight.ades=%s) (!(flight=*)) ) (from_hotel=false)' % (
                fromDate, toDate, transportId, airportId)
        searchStr += '(hotel=%s)(customer=%s)(cancelled=%s)(sent=false))' % (
            hotelId, region, cancelled)
        
        bookings = TM.transport_booking.search(searchStr)
        bookings = list(bookings)          

        result = []
        for booking in bookings:
            is_ground_duty = booking.flight == None
            if is_ground_duty:
                print "   ### found ground duty!"
                flightArrStn = airportId
                flightDepStn = airportId
            else:
                try:
                    flightArrStn = str(booking.flight.getRefI('ades'))
                    flightDepStn = str(booking.flight.getRefI('adep'))
                except modelserver.ReferenceError:
                    Errlog.log("Bad reference in table transport_booking:" + \
                               "%s flight referenced doesn't exist in flight_leg table" % \
                               booking.getRefI('flight'))


            hotelId = str(booking.getRefI('hotel'))
            #region = str(booking.getRefI('customer'))
            #region = booking.flight.cpe
            region = str(booking.getRefI('customer')) if is_ground_duty else booking.flight.cpe
            isHotelToAirport = booking.from_hotel

            if isHotelToAirport:
                flight_stn = flightDepStn
                flight_time = booking.pick_up if is_ground_duty else booking.flight.sobt
            else:
                flight_stn = flightArrStn
                flight_time = booking.pick_up if is_ground_duty else booking.flight.sibt

            if is_ground_duty:
                # flight_time is already local time (booking.pick_up)
                flightTime = flight_time
            else:
                flightTime, = R.eval(
                    'station_localtime("%s", %s)' % (
                    flight_stn,
                    flight_time))

            result.append(TransportBooking(isHotelToAirport,
                                           region,
                                           hotelId,
                                           booking.num_crew,
                                           booking.num_crew_dh,
                                           "A000" if is_ground_duty else booking.flight.fd,
                                           flightTime,
                                           booking.pick_up,
                                           flightDepStn,
                                           flightArrStn))
        result.sort()
        return result

    def getTransportData(self, transportId):
        """
        Gets the transport data for the specified transportId
        """
        try:
            return TM.transport[(transportId,)]
        except modelserver.EntityNotFoundError:
            raise TransportNotFoundException(
                'No transport found with id %s.' % transportId)

    def getHotelData(self, hotelId):
        """
        Gets the hotel data for the specified hotelId
        """
        try:
            return TM.hotel[(hotelId,)]
        except modelserver.EntityNotFoundError:
            raise HotelNotFoundException(
                'No hotel found with id %s.' % hotelId) 

    def getCustomerData(self, region):
        """
        Gets the customer data for the specified region
        """
        try:
            # Get the first (next) match in the search result.
            return TM.hotel_customer.search(
                '(region=%s)' % (region)).next()
        except StopIteration:
            raise CustomerNotFoundException(
                'No customer found at in region %s.' % (region))

    def getTransports(self, airportId='*'):
        """
        Returns all transports in the database
        or returns all transports associated to airport 'airportId'
        """
        if airportId == '*':
            return TM.transport.search('(id=*)')
        else:
            transports=[]
            searchStr = '(airport.id=%s)' % airportId 
            airportsWithTransport = TM.airport_hotel.search(searchStr)
            for a in airportsWithTransport:
                try:
                    if a.transport:
                        transport = TM.transport.search('(id=%s)' % a.transport.id)
                        for t in transport:
                            if not t in transports:
                                transports.append(t)
                except modelserver.ReferenceError:
                    Errlog.log("Bad reference in table airport_hotel:" + \
                               "%s transport referenced doesnt exist in table transport" % \
                               a.getRefI('airport'))
        return transports

    def getAirports(self, transportId='*'):
        """
        Returns all airports in the database with some transport associated.
        or returns all airports associated to transport 'transportId'
        """
        searchStr = '(transport.id=%s)' % transportId
        airportsWithTransport = TM.airport_hotel.search(searchStr)
        airports = []
        for a in airportsWithTransport:
            try:
                airport = TM.airport.search('(id=%s)' % a.airport.id)
                airp = airport.next()
                if not (airp.id,airp.name) in airports:
                    airports.append((airp.id,airp.name))
            except modelserver.ReferenceError:
                Errlog.log("Bad reference in table airport_hotel: " + \
                           "%s airport referenced doesnt exist in table airport" % a.getRefI('airport'))

        return airports

    def getRegions(self):
        """
        Returns all regions in the database.
        """
        return TM.hotel_customer.search('(region.id=*)')

"""
BookingEntity is used to store bookings in memory and be able to compare them.
"""
class BookingEntity(DataClass):

    def __init__(
        self, isHotelToAirport, region, crewAmount, crewAmountDH, transportId,
        hotelId, flightDay, pickUpTime, flightNr, flightStart, flightDepStn): 
        
        self.isHotelToAirport = isHotelToAirport
        self.region = region
        self.crewAmount = crewAmount
        self.crewAmountDH = crewAmountDH
        self.transportId = transportId
        self.hotelId = hotelId
        self.flightDay = flightDay
        self.pickUpTime = pickUpTime
        self.flightNr = flightNr
        self.flightStart = flightStart
        self.flightDepStn = flightDepStn

        return

    def __eq__(self, other):
        """
        Checks if two BookingEntities are equal.
        """
        if (self.transportId == other.transportId
            and self.isHotelToAirport == other.isHotelToAirport
            and self.hotelId == other.hotelId
            and self.crewAmount == other.crewAmount
            and self.crewAmountDH == other.crewAmountDH
            and self.flightNr == other.flightNr
            and AbsDate(self.flightDay) == AbsDate(other.flightDay)
            and AbsDate(self.flightStart) == AbsDate(other.flightStart)
            and AbsTime(self.pickUpTime) == AbsTime(other.pickUpTime)
            and self.flightDepStn == other.flightDepStn):
            return True
        return False

    def isConsideredEqual(self, otherBooking):
        samePickupTime = True
        sameAmount = otherBooking.num_crew == self.crewAmount and otherBooking.num_crew_dh == self.crewAmountDH
        if self.flightDepStn == "ARN":
            samePickupTime = AbsTime(self.pickUpTime) == AbsTime(otherBooking.pick_up)
        return sameAmount and samePickupTime

"""
TransportBooking is used for reports and compare bookings.
"""
class TransportBooking(DataClass):

    def __init__(self, isHotelToAirport, region, hotelId, crewAmount, crewAmountDH,
                 flightNr, flightTime, pickUpTime, flightDepStn, flightArrStn):
        self.isHotelToAirport = isHotelToAirport
        self.region = region
        self.hotelId = hotelId
        self.crewAmount = crewAmount
        self.crewAmountDH = crewAmountDH
        self.flightNr = flightNr
        self.flightTime = flightTime
        self.pickUpTime = pickUpTime
        self.flightDepStn = flightDepStn
        self.flightArrStn = flightArrStn

        return

    def __eq__(self, other):
        """
        Checks if two transport bookings are equal.
        """
        if (self.flightNr == other.flightNr
            and self.isHotelToAirport == other.isHotelToAirport
            and self.crewAmount == other.crewAmount
            and self.crewAmountDH == other.crewAmountDH
            and self.flightTime == other.flightTime
            and self.pickUpTime == other.pickUpTime
            and self.flightDepStn == other.flightDepStn
            and self.flightArrStn == other.flightArrStn
            and self.hotelId == other.hotelId):
            return True
        return False

    def __cmp__(self, other):
        """
        Compares two transport bookings so that bookings
        may be sorted by arrival/departure time.
        """
        cmpflightTime = cmp(self.flightTime, other.flightTime)
        if cmpflightTime == 0:
            cmpflightNr = cmp(self.flightNr, other.flightNr)
            if cmpflightNr == 0:
                if self.isHotelToAirport:
                    return cmp(self.flightDepStn, other.flightDepStn)
                else:
                    return cmp(self.flightArrStn, other.flightArrStn)
            return cmpflightNr
        return cmpflightTime        
