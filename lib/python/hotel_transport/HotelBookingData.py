#

#
"""
Hotel Booking Data Handler
"""

from tm import TM

import carmensystems.rave.api as R
from modelserver import TableManager
import modelserver
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

import data.HotelMqHandler as hotelMqHandler


def getExportDir():
    """
    Retrieves the directory where hotel reports are written.
    """
    # Where to store export files
    exportDir = Crs.CrsGetModuleResource("hotel", Crs.CrsSearchModuleDef, "ExportDirectory")
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

class HotelBookingManager:
    """
    Hotel Booking Manager Class
    """
    def __init__(self):
        bc = BasicContext()
        self.context = bc.getGenericContext()

    def refresh(self):
        """
        Reloads the table where hotel bookings are stored.
        """
        Cui.CuiReloadTable('hotel_booking')

    def createBooking(self, crewId, region, hotelId, checkIn, checkOut, nights, 
                      rooms, arrFlightNr, arrFlightTime, depFlightNr, depFlightTime):
        """
        Creates a new hotel booking line in the model.
        """
        selectErrMsg = "\n Region: %s, Hotel: %s, Date: %s" % (region, hotelId, checkIn)
        if not hotelId:
            Errlog.log('No hotel found')
            return
        if not region:
            print "WARNING: The following booking does not have a region:"
            print crewId, region, hotelId, arrFlightNr, depFlightNr, arrFlightTime, depFlightTime
            region = "SKD"
        try:
            # Get the first (next) match in the search result.
            customer = TM.hotel_customer.search(
                '(region=%s)' % (region)).next()
        except StopIteration:
            Errlog.log('No customer found in region %s.' % (region))
            return

        crew = TM.crew.getOrCreateRef((crewId,))  
        arrFlight = str(arrFlightTime) + "+" + arrFlightNr
        if depFlightNr == "?":
            depFlight = "?"
        else:
            depFlight = str(depFlightTime) + "+" + str(depFlightNr)
        hotel = TM.hotel.getOrCreateRef((hotelId,))
        booking = TM.hotel_booking.create((TM.createUUID(),))
        
        booking.crew = crew
        booking.checkin = checkIn
        booking.checkout = checkOut
        booking.nights = nights
        booking.rooms = rooms
        booking.arrival_flight = arrFlight
        booking.departure_flight = depFlight
        booking.hotel = hotel
        booking.customer = customer
        booking.sent = False
        booking.cancelled = False

        return

    @clockme
    def createUpdateBookings(self, fromDate):
        """
        Creates hotel bookings for crew and open trips for given date
        and next day. Also works as update.
        """
        
        # Bookings and updates are made for two days
        toDate = fromDate + RelTime(48, 0)
        
        layoverDuties, = R.eval(self.context, R.foreach(
            R.iter('iterators.leg_set',
                   where=('report_hotel.%%adjusted_next_leg_start_hotel%%  >= %s' % fromDate,
                          'report_hotel.%%adjusted_leg_end_hotel%% < %s' % toDate,
                          'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                          'not void(report_hotel.%layover_hotel_id_override%)')),
            'report_hotel.%crew_id%',
            'report_hotel.%layover_hotel_id_override%',
            'report_hotel.%adjusted_leg_end_hotel%',
            'report_hotel.%adjusted_next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%arr_flight_end%',
            'report_hotel.%dep_flight_nr%',
            'report_hotel.%dep_flight_start%'))
        Errlog.log("LAYOVER: " + str(layoverDuties))
        planBookings = []
        for (ix, crew, hotelId, checkIn, checkOut, nights,
             arrFlightNr, arrFlightTime, depFlightNr, depFlightTime) in layoverDuties:
            
            region = getHotelRegion(hotelId)
            # Use BookingEntity so that entity can be searched for in list
            if checkOut >= AbsTime('30DEC2099'):
                Errlog.log("ERROR: Undefined checkout in plan for crew %s at hotel %s arriving at %s: No booking created!" % (crew, hotelId, checkIn))
                continue

            planBookings.append(
                BookingEntity(crew,
                              region,
                              hotelId,
                              checkIn,
                              checkOut,
                              nights,
                              1,
                              arrFlightNr,
                              arrFlightTime,
                              depFlightNr,
                              depFlightTime))
        
        searchStr = '(&(!(crew=N/A))(checkout>=%s)(checkin<%s)(cancelled=false))'\
                  % (fromDate, toDate)
        dbBookings = TM.hotel_booking.search(searchStr)
        for booking in dbBookings:
            try:
                # Hotel id might not exist. Get only the id.
                hotelId = str(booking.getRefI('hotel'))
                # Airport table should not be used. Get the referring string.
                try:
                    arrFlightNr = self.getDescriptor(booking.arrival_flight)
                    arrFlightTime = self.getFlightTime(booking.arrival_flight)
                except Exception, e:
                    booking.cancelled = True
                    booking.sent = False
                    continue
                
                try:
                    depFlightNr = self.getDescriptor(booking.departure_flight)
                    depFlightTime = self.getFlightTime(booking.departure_flight)
                except Exception, e:
                    booking.cancelled = True
                    booking.sent = False
                    continue
                
                # Create BookingEntity to search list of bookings in plan
                # ValueError thrown if no match
                i = planBookings.index(
                    BookingEntity(booking.crew.id,
                                  booking.customer.region.id,
                                  hotelId,
                                  booking.checkin,
                                  booking.checkout,
                                  booking.nights,
                                  booking.rooms,
                                  arrFlightNr,
                                  arrFlightTime,
                                  depFlightNr,
                                  depFlightTime))
                # Remove match
                planBookings.pop(i)
            except ValueError:
                booking.cancelled = True
                booking.sent = False
            except modelserver.ReferenceError:
                Errlog.log("Bad reference in table hotel_booking:" + \
                           "%s crew or %s customer referenced doesn't exist in referred table" % (
                    booking.getRefI('crew'), booking.getRefI('customer')))
                
            
        for booking in planBookings:
            # Remaining bookings are new
            self.createBooking(booking.crew,
                               booking.region,
                               booking.hotelId,
                               booking.checkIn,
                               booking.checkOut,
                               booking.nights,
                               booking.rooms,
                               booking.arrFlightNr,
                               booking.arrFlightTime,
                               booking.depFlightNr,
                               booking.depFlightTime)
            
        # Create/update hotel bookings for open trips
        layoverOpenDuties, = R.eval('sp_crrs', R.foreach(
            R.iter('report_hotel.layover_set',
                   where=('report_hotel.%%adjusted_next_leg_start_hotel%% >= %s' % fromDate,
                          'report_hotel.%%adjusted_leg_end_hotel%% < %s' % toDate,
                          'report_common.%is_open_trip%',
                          'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                          'not void(report_hotel.%layover_hotel_id_override%)',
                          'report_hotel.%assigned% > 0')),
            'report_hotel.%layover_hotel_id_override%',
            'report_hotel.%leg_end_hotel%',
            'report_hotel.%next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%assigned%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%arr_flight_end%',
            'report_hotel.%dep_flight_nr%',
            'report_hotel.%dep_flight_start%'))

        planBookings = []
        for (_, hotelId, checkIn, checkOut, nights, assigned,
             arrFlightNr, arrFlightTime, depFlightNr, depFlightTime) in layoverOpenDuties:
            
            # Use BookingEntity so that entity can be searched for in list
            region = getHotelRegion(hotelId)
            planBookings.append(
                BookingEntity('N/A',
                              region,
                              hotelId,
                              checkIn,
                              checkOut,
                              nights,
                              assigned,
                              arrFlightNr,
                              arrFlightTime,
                              depFlightNr,
                              depFlightTime))

        searchStr = '(&(crew=N/A)(checkout>=%s)(checkin<%s)(cancelled=false))'\
                    % (fromDate, toDate)
        dbBookings = TM.hotel_booking.search(searchStr)

        for booking in dbBookings:
            try:
                # Hotel id might not exist. Get only the id.
                hotelId = str(booking.getRefI('hotel'))
                try:
                    arrFlightNr = self.getDescriptor(booking.arrival_flight)
                    arrFlightTime = self.getFlightTime(booking.arrival_flight)
                except Exception, e:
                    Errlog.log("Bad reference in table hotel_bookings:" + \
                               "%s arrival flight or ground referenced doesnt exist" % \
                               booking)
                try:
                    depFlightNr = self.getDescriptor(booking.departure_flight)
                    depFlightTime = self.getFlightTime(booking.departure_flight)
                except Exception, e:
                    Errlog.log("Bad reference in table hotel_bookings:" + \
                               "%s departure flight or ground referenced doesnt exist" % \
                               booking)
                
                # Create BookingEntity to search list of bookings in plan
                # ValueError thrown if no match
                i = planBookings.index(
                    BookingEntity('N/A',
                                  booking.customer.region.id,
                                  hotelId,
                                  booking.checkin,
                                  booking.checkout,
                                  booking.nights,
                                  booking.rooms,
                                  arrFlightNr,
                                  arrFlightTime,
                                  depFlightNr,
                                  depFlightTime))
                # Remove match
                planBookings.pop(i)
            except ValueError:
                booking.cancelled = True
                booking.sent = False
            except modelserver.ReferenceError:
                Errlog.log("Bad reference in table hotel_booking:" + \
                           "%s crew or %s customer referenced doesn't exist in referred table" % (
                    booking.getRefI('crew'), booking.getRefI('customer')))

        for booking in planBookings:
            # Remaining bookings are new
            self.createBooking(booking.crew,
                               booking.region,
                               booking.hotelId,
                               booking.checkIn,
                               booking.checkOut,
                               booking.nights,
                               booking.rooms,
                               booking.arrFlightNr,
                               booking.arrFlightTime,
                               booking.depFlightNr,
                               booking.depFlightTime)


        return planBookings
                
    def setBookingsAsSent(self, fromDate, hotelId, region, isUpdate=False):
        """
        Sets all bookings as sent for given date, hotel 
        and region, 48hours forward.
        """
        if region == "ALL":
            region = "*"
        toDate = fromDate + RelTime(48, 0)
        if isUpdate:
            hotelCheckStr = 'checkout'
        else:
            hotelCheckStr = 'checkin'
        bookings = TM.hotel_booking.search(
            '(&(%s>=%s)(checkin<%s)(hotel=%s)(customer=%s)(sent=false))'\
            % (hotelCheckStr, fromDate, toDate, hotelId, region))

        for booking in bookings:
            booking.sent = True

        return
    
    def setPreviousBookingsAsSent(self, fromDate, hotelId, region):
        """
        Sets all bookings made for previous days from given date,
        hotel and region as not sent
        """
        if region == "ALL":
            region = "*"
        bookings = TM.hotel_booking.search(
            '(&(checkout>=%s)(checkin<%s)(hotel=%s)(customer=%s)(sent=false))'\
            % (fromDate, fromDate, hotelId, region))
        for booking in bookings:
            booking.sent = True
            
        return
        

    def setTodayBookingsAsNotSent(self, fromDate, hotelId, region):
        """
        Sets all bookings as not sent for given date, hotel 
        and region, for today and 48hours forward.
        """
        if region == "ALL":
            region = "*"
        toDate = fromDate + RelTime(48, 0)
        bookings = TM.hotel_booking.search(
            '(&(checkin>=%s)(checkin<%s)(hotel=%s)(customer=%s)(sent=true))'\
            % (fromDate, toDate, hotelId, region))
        for booking in bookings:
            booking.sent = False

        return

    def getPlanBookings(self, fromDate, hotelId, region, context=None, isUpdate=False):
        """
        Gets hotel bookings from plan data for a date and two days forward
        and for a hotel and sas region.
        """
        if context is None:
            context = self.context

        # Bookings are made for two days
        toDate = fromDate + RelTime(48, 0)
        
        if isUpdate:
            hotelCheckStr = 'report_hotel.%adjusted_next_leg_start_hotel%'
        else:
            hotelCheckStr = 'report_hotel.%adjusted_leg_end_hotel%'
        
        if region == "ALL":
            region_txt="1 = 1"
        else:
            region_txt='report_hotel.%%region%% = "%s"' % region

        layoverDuties, = R.eval(context, R.foreach(
            R.iter('iterators.leg_set',
                   where=('%s >= %s' % (hotelCheckStr, fromDate),
                          'report_hotel.%%adjusted_leg_end_hotel%% < %s' % toDate,
                          'not void(report_hotel.%layover_hotel_id_override%)',
                          'fundamental.%is_roster%',
                          'not (leg.%is_standby_at_hotel% and leg.%is_first_in_duty%)',
                          'report_hotel.%%layover_hotel_id_override%% = "%s"' % hotelId,
                          '%s' % region_txt)),
            'report_hotel.%crew_id%',
            'report_hotel.%crew_employee_number%',
            'report_hotel.%crew_rank%',
            'report_hotel.%crew_firstname%',
            'report_hotel.%crew_surname%',
            'report_hotel.%ac_region%',
            'report_hotel.%leg_end_hotel%',
            'report_hotel.%next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%dep_flight_nr%',
            'report_hotel.%crew_pos%(report_hotel.%crew_rank%)'))
        
        result = []
        
        for (_, crewId, empNumber, rank, firstName, lastName, crew_region,
             checkIn, checkOut, nights, arrFlightNr, depFlightNr, pos) in layoverDuties:
            
            if not empNumber:
                empNumber = crewId

            result.append(HotelBooking(crewId,
                                       empNumber,
                                       rank,
                                       firstName,
                                       lastName,
                                       crew_region,
                                       arrFlightNr,
                                       checkIn,
                                       depFlightNr,
                                       checkOut,
                                       nights,
                                       1,
                                       pos))

        layoverDuties, = R.eval('sp_crrs', R.foreach(
            R.iter('report_hotel.layover_set',
                   where=('%s >= %s' % (hotelCheckStr, fromDate),
                          'report_hotel.%%adjusted_leg_end_hotel%% < %s' % toDate,
                          'not void(report_hotel.%layover_hotel_id_override%)',
                          'report_common.%is_open_trip%',
                          'report_hotel.%%layover_hotel_id_override%% = "%s"' % hotelId,
                          '%s' % region_txt,
                          'report_hotel.%assigned% > 0')),
            'report_hotel.%ac_region%',
            'report_hotel.%leg_end_hotel%',
            'report_hotel.%next_leg_start_hotel%',
            'report_hotel.%nights%',
            'report_hotel.%assigned%',
            'report_hotel.%arr_flight_nr%',
            'report_hotel.%dep_flight_nr%'))
        
        for (ix, ac_region, checkIn, checkOut, nights, 
             rooms, arrFlightNr, depFlightNr) in layoverDuties:
            
            result.append(HotelBooking(None,
                                       None,
                                       None,
                                       None,
                                       None,
                                       ac_region,
                                       arrFlightNr,
                                       checkIn,
                                       depFlightNr,
                                       checkOut,
                                       nights,
                                       rooms,
                                       0))
        result.sort()
        return result

    def isNotSentDbBookings(self, fromDate, hotel, region, bookingUpdate=False):
        """
        Checks if there are unsent bookings at a date for hotel and region.
        """
        if region == "ALL":
            region = "*"
        toDate = fromDate + RelTime(48, 0)
        if bookingUpdate:
            hotelCheckStr = 'checkout'
        else:
            hotelCheckStr = 'checkin'
        for booking in TM.hotel_booking.search(
            '(&(%s>=%s)(checkin<%s)(hotel=%s)(customer=%s)(sent=false))' % (
            hotelCheckStr, fromDate, toDate, hotel, region)):
            return True
        return False

    def isSentDbBookings(self, fromDate, toDate, hotel, region):
        """
        Checks if there are sent bookings for a period, a hotel and region.
        """
        if region == "ALL":
            region = "*"
        for _ in TM.hotel_booking.search(
            '(&(checkin>=%s)(checkin<=%s)(hotel=%s)(customer=%s)(sent=true))' % (
            fromDate, toDate, hotel, region)):
            return True
        return False
    
    def printDbBookings(self, fromDate, hotelId, region, prfx):
        if region == "ALL":
            region = "*"
        toDate = fromDate + RelTime(48, 0)
        searchStr = '(&(checkout>=%s)(checkin<%s)(hotel=%s)' % (fromDate, toDate, hotelId)
        searchStr += '(customer=%s)(sent=false))' % (region)
        bookings = TM.hotel_booking.search(searchStr)
        for b in bookings:
            print prfx, str(b)
    
    def getDbBookings(self, fromDate, hotelId, region, cancelled=False):
        """
        Gets hotel bookings in the database from date and two days forward for
        a hotel and sas region. Either cancelled or current bookings can be fetched.
        """
        toDate = fromDate + RelTime(48, 0)
        if cancelled:
            cancelled = 'true'
        else:
            cancelled = 'false'
        if region == "ALL":
            region = "*"
        searchStr = '(&(checkout>=%s)(checkin<%s)(hotel=%s)' % (fromDate, toDate, hotelId)
        searchStr += '(customer=%s)(cancelled=%s)(sent=false))' % (region, cancelled)
        bookings = TM.hotel_booking.search(searchStr)

        result = []
        for booking in bookings:
            try:
                crewId = booking.crew.id
            except modelserver.ReferenceError:
                crewId = None
            if crewId:
                empSearch = TM.crew_employment.search(
                    '(&(crew=%s)(validfrom<=%s)(validto>=%s))' % (
                    crewId, fromDate, fromDate))
                try:
                    employment = empSearch.next()
                    # Get the first (next) perkey in the search result.
                    empNumber = employment.extperkey
                    # Get the first (next) crew rank in the search result.
                    rank = employment.crewrank.id
                    crew_region = employment.region.id
                except StopIteration:
                    Errlog.log('Employment data not found for crewId %s.' % crewId)
                    empNumber = None
                    rank = None
                    crew_region = None
                firstName = booking.crew.forenames
                lastName = booking.crew.name
            else:
                crewId = None
                empNumber = None
                rank = None
                firstName = None
                lastName = None
                crew_region = None

            # Airport table should not be used. Get the referring string.
            try:   # Crew arriving on a flight
                arrFlightTime = self.getFlightTime(booking.arrival_flight)
                arrFlightNr = self.getDescriptor(booking.arrival_flight)
            except Exception, e:
                Errlog.log("Bad reference in table hotel_booking: arrival" + \
                           "flight or ground referenced doesn't exist. %s" % \
                           booking)
                continue
            try:
                depFlightTime = self.getFlightTime(booking.departure_flight)
                depFlightNr = self.getDescriptor(booking.departure_flight)
            except Exception, e:
                Errlog.log("Bad reference in table hotel_booking: departure" + \
                           "%s flight or ground referenced doesn't exist" % \
                           booking)
                continue

            pos = 0
            if rank:
                # Use position for sorting of rank
                pos, = R.eval('report_hotel.%%crew_pos%%("%s")' % rank)

            if not empNumber:
                empNumber = crewId

            result.append(HotelBooking(crewId,
                                       empNumber,
                                       rank,
                                       firstName,
                                       lastName,
                                       crew_region,
                                       arrFlightNr,
                                       arrFlightTime,
                                       depFlightNr,
                                       depFlightTime,
                                       booking.nights,
                                       booking.rooms,
                                       pos))
        result.sort()
        return result

    def getNewBookings(self, date, hotelId, region, context=None):
        """
        Gets new bookings by comparing bookings in plan and
        current bookings in database (not cancelled).
        """
        bookings = self.getDbBookings(date, hotelId, region)
        planBookings = self.getPlanBookings(date, hotelId, region, context, True)

        new = []
        for booking in planBookings:
            try:
                bookings.index(booking)
            except ValueError:
                new.append(booking)

        new.sort()
        return new

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

    def getHotels(self, airportId='*'):
        """
        Returns all hotels in the database
        or returns all hotels associated to airport 'airportId'
        """
        if airportId == '*':
            return TM.hotel.search('(id=*)')
        else:
            hotels=[]
            searchStr = '(airport.id=%s)' % airportId 
            airportsWithHotel = TM.airport_hotel.search(searchStr)
            for a in airportsWithHotel:
                hotels = self.getHotel(a, hotels)
            otherAirportsWithHotel = TM.preferred_hotel.search(searchStr)
            for oa in otherAirportsWithHotel:
                hotels = self.getHotel(oa, hotels)
            yetOtherAirportsWithHotel = TM.preferred_hotel_exc.search(searchStr)
            for yoa in yetOtherAirportsWithHotel:
                hotels = self.getHotel(yoa, hotels)
            return hotels
        
    def getHotel(self, a, hotels):
        """
        Return hotel 'h' appended list 'hotels' if it's
        not already included in such list 'hotels'
        """
        try:
            if a.hotel:
                hotel = TM.hotel.search('(id=%s)' % a.hotel.id)
                for h in hotel:
                    if not h in hotels:
                        hotels.append(h)
        except modelserver.ReferenceError:
            Errlog.log("Bad reference in table airport_hotel:" + \
                       "%s hotel referenced doesnt exist in table hotel" % a)
        
        return hotels
    
    def getAirports(self, hotelId='*'):
        """
        Returns all airports in the database with some hotel associated.
        """
        airports = []
        searchStr = '(hotel=%s)' % hotelId
        
        airportsWithHotel = TM.airport_hotel.search(searchStr)
        for a in airportsWithHotel:
            airports = self.getUniqueAirport(a, airports, "airport_hotel")
            
        otherAirportsWithHotel = TM.preferred_hotel.search('(hotel=%s)' % hotelId)
        for oa in otherAirportsWithHotel:
            airports = self.getUniqueAirport(oa, airports, "preferred_hotel")
            
        yetOtherAirportsWithHotel = TM.preferred_hotel_exc.search('(hotel=%s)' % hotelId)
        for yoa in yetOtherAirportsWithHotel:
            airports = self.getUniqueAirport(yoa, airports, "preferred_hotel_exc")
            
        return airports
    
    def getUniqueAirport(self, a, airports, tableName):
        """
        Return airport 'a' appended to list 'airports' if it's 
        not already included in such list 'airports'
        """
        try:
            airport = TM.airport.search('(id=%s)' % a.airport.id)
            airp = airport.next()
            if not (airp.id,airp.name) in airports:
                airports.append((airp.id,airp.name))
        except modelserver.ReferenceError:
            Errlog.log("Bad reference in table %s: " % tableName + \
                       "%s airport referenced doesnt exist in table airport" % a.getRefI('airport'))
        return airports

    def getRegions(self):
        """
        Returns all regions in the database.
        """
        return TM.hotel_customer.search('(region=*)')
    
    def getFlightTime(self, flight):
        """
        Gets the arrival/departure time of the flight/ground activity
        """
        return flight.split('+')[0]
    def getDescriptor(self, flight):
        """
        Gets the flight descriptor / ground activity id
        """
        return flight.split('+')[1]
"""
BookingEntity is used to store bookings in memory and be able to compare them.
"""
class BookingEntity(DataClass):

    def __init__(
        self, crew, region, hotelId, checkIn, checkOut, nights, rooms, 
        arrFlightNr, arrFlightTime, depFlightNr, depFlightTime):
        self.crew = crew
        self.region = region
        self.hotelId = hotelId
        self.checkIn = checkIn
        self.checkOut = checkOut
        self.nights = nights
        self.rooms = rooms
        self.arrFlightNr = arrFlightNr
        self.arrFlightTime = arrFlightTime
        self.depFlightNr = depFlightNr
        self.depFlightTime = depFlightTime
        return

    def __eq__(self, other):
        """
        Checks if two BookingEntities are equal.
        """
        if (self.crew == other.crew
            and self.hotelId == other.hotelId
            and self.arrFlightNr == other.arrFlightNr
            and AbsTime(self.arrFlightTime) == AbsTime(other.arrFlightTime)
            and self.depFlightNr == other.depFlightNr
            and AbsTime(self.depFlightTime) == AbsTime(other.depFlightTime)
            and self.rooms == other.rooms):
            return True
        return False

"""
HotelBooking is used for reports and compare bookings.
"""
class HotelBooking(DataClass):

    def __init__(self, crewId, empNumber, rank, firstName, lastName, region, arrFlightNr, 
                 arrFlightTime, depFlightNr, depFlightTime, nights, rooms, rankNo):
        self.crewId = crewId
        self.empNumber = empNumber
        self.rank = rank
        self.firstName = firstName
        self.lastName = lastName
        self.region = region
        self.arrFlightNr = arrFlightNr
        self.arrFlightTime = arrFlightTime
        self.depFlightNr = depFlightNr
        self.depFlightTime = depFlightTime
        self.nights = nights
        self.rooms = rooms
        self.rankNo = rankNo

        return

    def __eq__(self, other):
        """
        Checks if two hotel bookings is equal.
        """
        if (self.crewId == other.crewId
            and self.arrFlightNr == other.arrFlightNr
            and self.depFlightNr == other.depFlightNr
            and self.rooms == other.rooms):
            return True
        return False

    def __cmp__(self, other):
        """
        Compares two hotel bookings so that bookings may be sorted.
        """
        t1 = self.arrFlightTime
        t2 = other.arrFlightTime
        try:
            t1 = AbsTime(t1)
        except:
            pass
        try:
            t2 = AbsTime(t2)
        except:
            pass
        cmpArrFlightTime = cmp(t1, t2)
        if cmpArrFlightTime == 0:
            cmpArrFlightNr = cmp(self.arrFlightNr, other.arrFlightNr)
            if cmpArrFlightNr == 0:
                return cmp(self.rankNo, other.rankNo)
            return cmpArrFlightNr
        return cmpArrFlightTime
    


    
