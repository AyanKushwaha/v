#!/usr/bin/env python
# coding: utf-8
"""

 Builds Transport data objects...

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

# Transport imports
import DataHandler as dh
import hotel_transport.common.util as util

# CONSTANTS
TRANSPORT_CHUNK_SIZE = 500  # Number of transport updated at a time
DELAY = 1.0  # Delay between each http request with chunk in seconds



def prepareTransportMessages(bookings):
    """
    Prepares the transport messages to be put on the message queue

    :param bookings: the IDs of bookings who are to be updated
    :return: count: nr of transports being part of all messages being created
    :return: messages: a list of all messages to be put on the queue
    """

    transport_objects = buildTransports(bookings)
    count, messages = dh.structure_messages(transport_objects, "transports", TRANSPORT_CHUNK_SIZE)

    return count, messages


def buildTransports(bookings):
    """
    Builds a transport object for every transport in booking.
    :return: List of transport objects, each transport object is represented by a dict.
    """

    transport_objects = list()
    for booking in bookings:
        transport_objects.append(
            buildTransportObject(booking)
        )

    return transport_objects


def buildTransportObject(booking):
    """
    Builds and returns the transport object
    :param transport_id: ID of the transport being built
    :return: A dict containing specified transport information
    """

    db_transport = next(TM.transport.search('(id=%s)' % booking['transportId']))
    booked_transport_info = next(TM.transport_booking.search('(transport=%s)' % booking['transportId']))

    if booking['isHotelToAirport'] == 0:
        booking['isHotelToAirport'] = False
    else:
        booking['isHotelToAirport'] = True

    return dict(
            transport_id = booking['transportId'],
            transport_name = db_transport.name,
            num_of_crew = booking['crewAmount'],
            flight_day = util.abs_time_to_str(booking['flightDay']),
            pick_up_time = util.abs_time_to_str(booking['pickUpTime']),
            hotel = str(booked_transport_info.getRefI('hotel')),
            flight_nr = booking['flightNr'],
            to_airport = booking['isHotelToAirport'],
            )

def showTestTransports():
    """
    Builds and shows all roster-data for passed-in or first selected crew.
    """
    import report_sources.report_server.rs_TransportBookingMq as test
    (transports, _) = test.generate(dict())
    pprint(transports)
    util.show_message(pformat(transports), "Test transports")