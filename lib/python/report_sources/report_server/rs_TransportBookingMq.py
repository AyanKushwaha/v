import os 

import carmensystems.rave.api as R
import modelserver
from tm import TM

from RelTime import RelTime
from AbsTime import AbsTime
from datetime import datetime
import Errlog

import hotel_transport.data.TransportMqHandler as handler
import hotel_transport.TransportBookingData as T
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

    mgr = T.TransportBookingManager()
    bookings = []

    searchStr = '(&(flight_day>=%s)(flight_day<%s)(cancelled=false))' % (fromDate, toDate)
    dbBookings = TM.transport_booking.search(searchStr)

    for booking in dbBookings:
        transportId, booking = validateBooking(booking)
        if booking.cancelled == 0 and booking.sent == 1:
            bookings.append(
                    parseBooking(transportId, booking)
                )
                
    # Generate booking messages for AIRSIDE
    _, res = handler.prepareTransportMessages(bookings)
    reports = []
    for request in res:
        print("RESULT: " + str(request))
        reports.append({'content':("%s" % request),
                        'content-type':'application/json',
                        'destination':[('default', {})],
                        })
        print("%s Transport - request_id: %s" % (datetime.now().strftime("%Y%m%d %H:%M:%S"), request['request_id']))

    
    return (reports, True)


def parseBooking(transportId, booking):
    is_ground_duty = booking.flight == None
    return dict(
                transportId = transportId,
                crewAmount = booking.num_crew,
                flightDay = booking.flight_day,
                pickUpTime = booking.pick_up,
                flightNr = "A000" if is_ground_duty else booking.flight.fd,
                isHotelToAirport = booking.from_hotel,
                )

def validateBooking(booking): 
    try:
        # Transport id might not exist. Get only the id.
        transportId = booking.transport.id
    except:
        booking.cancelled = 1
        booking.sent = 0
        transportId = None
        
    return transportId, booking
