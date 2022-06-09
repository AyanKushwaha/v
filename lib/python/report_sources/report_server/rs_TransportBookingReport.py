#

#
"""
Transport Booking Report.
"""

from hotel_transport.TransportBookingRun import transportBookingRun

"""
Entry point for the report server
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
    reports = transportBookingRun(bookingUpdate=bookingUpdate,
                                  forecast=forecast,
                                  performed=performed)

    return (reports, True) # True means delta is used

