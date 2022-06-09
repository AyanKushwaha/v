#

#
"""
Hotel Booking Report.
"""

from hotel_transport.HotelBookingRun import hotelBookingRun

"""Entry point for the report server
"""
def generate(param):
    bookingUpdate = False
    forecast = False
    performed = False
    if isinstance(param,list):
        l,d = param
    else:
        d = param
    if d.has_key('forecast'):
        forecast = d['forecast'] == 'True'
    if d.has_key('bookingUpdate'):
        bookingUpdate = d['bookingUpdate'] == 'True'
    if d.has_key('performed'):
        performed = d['performed'] == 'True'
        
    # Generate Booking or Forecast reports
    reports = hotelBookingRun(bookingUpdate=bookingUpdate,
                              forecast=forecast,
                              performed=performed)

    return (reports, True) # True means delta is used

