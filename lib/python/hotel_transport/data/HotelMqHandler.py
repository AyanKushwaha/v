#!/usr/bin/env python
# coding: utf-8
"""

 Builds Hotel data objects...

"""
# Python imports
from pprint import pformat, pprint

# External CARMUSR imports

import carmensystems.rave.api as rave
from tm import TM
from dig.DigJobQueue import DigJobQueue


# Hotel imports
import DataHandler as dh
import hotel_transport.common.util as util


# CONSTANTS
HOTEL_CHUNK_SIZE = 500  # Number of hotel updated at a time
DELAY = 1.0  # Delay between each http request with chunk in seconds


def prepareHotelMessages(bookings):
    """
    Prepares the hotel messages to be put on the message queue

    :param bookings: the IDs of hotel who are to be updated
    :return: count: nr of hotels being part of all messages being created
    :return: messages: a list of all messages to be put on the queue
    """

    hotel_objects = buildHotels(bookings)
    count, messages = dh.structure_messages(hotel_objects, "hotels", HOTEL_CHUNK_SIZE)

    return count, messages


def buildHotels(bookings):
    """
    Builds a hotel object for every hotel in booking.
    :return: List of hotel objects, each hotel object is represented by a dict.
    """

    hotel_objects = list()
    for booking in bookings:
        hotel_objects.append(buildHotelObject(booking))

    return hotel_objects


def buildHotelObject(booking):
    """
    Builds and returns the hotel object
    :param bag: CMS bag interface
    :param hotel_id: ID of the hotel being built
    :return: A dict containing specified hotel information
    """

    empno = rave.eval('rosterserver.%empno_by_id%("%s")', str(booking["crew"]))[1]
    db_hotel = next(TM.hotel.search("(id=%s)" % booking["hotelId"]))
    timeNow = rave.eval("fundamental.%now%")[0]
    if any(
        TM.preferred_hotel_exc.search(
            "(&(hotel=%s)(validfrom<=%s)(validto>=%s)(airport_hotel=true))"
            % (booking["hotelId"], timeNow, timeNow)
        )
    ):
        hotel_type = "AIRPORT"
    else:
        hotel_type = "CITY"

    return dict(
        empno=empno,
        hotel_id=booking["hotelId"],
        name=db_hotel.name,
        address=db_hotel.street,
        hotel_type=hotel_type,
        date_arrival=util.abs_time_to_str(booking["checkIn"]),
        date_depature=util.abs_time_to_str(booking["checkOut"]),
        nights=booking["nights"],
        arr_flight_nr=booking["arrFlightNr"],
        dep_flight_nr=booking["depFlightNr"],
    )


def showTestHotels():
    """
    Builds and shows all roster-data for passed-in or first selected crew.
    """
    import report_sources.report_server.rs_HotelBookingMq as test

    hotels = test.generate(dict())
    pprint(hotels)
    util.show_message(pformat(hotels), "Test hotels")
