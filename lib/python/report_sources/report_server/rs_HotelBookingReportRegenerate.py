
"""
Hotel Booking Report.
"""

from hotel_transport.HotelBookingRun import hotelBookingRun

global_hotelbooking_forecast_reports = []

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

    print "##############################"
    print reports
    print "##############################"
    return (reports, True) # True means delta is used

def generate_new_reports():


    if len(global_hotelbooking_forecast_reports) == 0:
        global global_hotelbooking_forecast_reports
        print "### Going to generte report and save it to global varible"
        global_hotelbooking_forecast_reports ,_delta = generate({'bookingUpdate': "False", 'performed': "False", 'forecast': "True"})
    dists = global_hotelbooking_forecast_reports
    print "### type dists) %s" % str(type(dists))
    print "### len distinations: %d" % len(dists)

    print "### Reports have been generted"



generate_new_reports()

