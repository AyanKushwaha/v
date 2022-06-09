import os

import carmensystems.rave.api as R
import modelserver
from tm import TM

from RelTime import RelTime
from AbsTime import AbsTime
from datetime import datetime
import Errlog

import hotel_transport.data.HotelMqHandler as handler
import hotel_transport.HotelBookingData as H

"""Entry point for the report server
"""
def generate(param):
    bookingUpdate = False
    if isinstance(param, list):
        _, d = param
    else:
        d = param

    # Enable the use of RosterServer menues set time
    if os.getenv("CARMSYSTEMNAME") in ["PROD_TEST", "CMSDEV"]:
        fromDate = AbsTime(str(R.eval("fundamental.%now%")[0]).replace('-', ''))
    else:
        fromDate = AbsTime(str(datetime.now().date()).replace('-',''))

    toDate = fromDate + RelTime(48, 0)

    searchStr = '(&(!(crew=N/A))(checkout>=%s)(checkin<%s)(cancelled=false))' % (fromDate, toDate)
    dbBookings = TM.hotel_booking.search(searchStr)

    bookings = []
    for booking in dbBookings:
        hotelId, booking = validateBooking(booking)
        if booking.cancelled == 0 and hotelId:
            bookings.append(
                    parseBooking(hotelId, booking)
                )
                
    # Generate booking messages for AIRSIDE
    _, res = handler.prepareHotelMessages(bookings)
    reports = []
    for request in res:
        reports.append({'content':("%s" % request),
                        'content-type':'application/json',
                        'destination':[('default', {})],
                        })
        print("%s Hotel - request_id: %s" % (datetime.now().strftime("%Y%m%d %H:%M:%S"), request['request_id']))
    
    return (reports, True) # True means delta is used


def parseBooking(hotelId, booking):
    if booking.cancelled == 0 and booking.sent == 1:
        return dict(
            crew = booking.crew.id,
            hotelId = hotelId,
            checkIn = booking.checkin,
            checkOut = booking.checkout,
            nights = booking.nights,
            arrFlightNr = getDescriptor(booking.arrival_flight),
            depFlightNr = getDescriptor(booking.departure_flight),
            )
        

def validateBooking(booking): 
    try:
        # Hotel id might not exist. Get only the id.
        hotelId = booking.hotel.id
    except:
        booking.cancelled = 1
        booking.sent = 0
        hotelId = None
        
    return hotelId, booking


def getDescriptor(flight):
    """
    Gets the flight descriptor / ground activity id
    """
    if '+' in flight:
        return flight.split('+')[1]
    else:
        return flight
