#!/usr/bin/env python
# coding: utf-8
"""

 Builds Hotel data objects...

"""
# Python imports
from datetime import datetime
from pprint import pformat, pprint
import os

# External CARMUSR imports
import Cui
import carmensystems.rave.api as rave
from utils.selctx import SingleCrewFilter
from tm import TM
from dig.DigJobQueue import DigJobQueue


# Hotel imports
import DataHandler as dh
import hotel_transport.common.util as util

# TMP
import Errlog

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
        hotel_objects.append(
            buildHotelObject(booking)
        )
    
    return hotel_objects


def buildHotelObject(booking):
    """
    Builds and returns the hotel object
    :param bag: CMS bag interface
    :param hotel_id: ID of the hotel being built
    :return: A dict containing specified hotel information
    """

    empno = rave.eval('rosterserver.%empno_by_id%(\"%s\")', str(booking['crew']))[1]
    db_hotel = next(TM.hotel.search('(id=%s)' % booking['hotelId']))
    for phe in hotel.referers('preferred_hotel_exc','hotel'):
        if phe.airport.id == airport and ce.crewrank.maincat == phe.maincat and ce.region == phe.region and phe.validfrom < now and phe.validto >= now:
                if phe.airport_hotel:
                    return "%s (airport hotel)" % hotel.id
                else:
                    break
    return "%s (city hotel)" % hotel.id
    
def showTestHotels():
    """
    Builds and shows all roster-data for passed-in or first selected crew.
    """
    import report_sources.report_server.rs_HotelBookingMq as test
    hotels = test.generate(dict())
    pprint(hotels)
    util.show_message(pformat(hotels), "Test hotels")
