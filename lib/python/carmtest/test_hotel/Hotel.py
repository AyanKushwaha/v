'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *

class hotel_001_HotelBooking(TestFixture):
    "Hotel bookings"
    
    @REQUIRE("Tracking")
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None
        self.report_files = []
        
    def setUp(self):
        # Make sure "Now" time is within the planning period
        print self.raveExpr("fundamental.%pp_end%")
        self._now = self.getNowTime()
        self.setNowTime(self.raveExpr("fundamental.%pp_end%")-RelTime(12,0))
        
    def test_001_createBookings(self):
        import hotel_transport.HotelBookingRun as r
        response = r.hotelBookingRun()
        
        for i in range(len(response)):
            self.report_files.append(response[i]['content-location'])

    @REQUIRE("NotMigrated")
    def test_002_createUpdates(self):
        import hotel_transport.HotelBookingRun as r
        from carmusr.tracking import Deassign
        import Cui
        
        bookingDate = AbsDate(self.getNowTime())
        crewId = None
        flt = None
        for booking in self.table("hotel_booking").search("(&(checkin=%s)(sent=true)(cancelled=false))" % (bookingDate)):
            crewId = str(booking.getRefI("crew"))
            flt = booking.arrival_flight
            if crewId == "N/A" or not "+SK" in flt: continue
            break
        
        if crewId == None or flt == None:
            self.dataError("Failed to find suitable booking")
        
        date,fltno = flt.split('+')
        tmp = fltno.split(' ')
        fltcarrier = tmp[0]
        fltno = tmp[1] 

        _, legs, startStation, endStation = zip(*(self.getLegs(('crew.%%id%%="%s" and leg.%%flight_carrier%%="%s" and leg.%%flight_nr%%=%s' % (crewId, fltcarrier, fltno)), area=Cui.CuiArea0, eval=('leg_identifier', 'leg.%start_station%', 'leg.%end_station%'))[0]))        
        self.markLegs(list(legs)[0], area=Cui.CuiArea0)
        response = Deassign.deassign(area=Cui.CuiArea0)
        assert response is None, "%s" % response

        response = r.hotelBookingRun(bookingUpdate=True)

        for i in range(len(response)):
            self.report_files.append(response[i]['content-location'])
        self.cleanUp()

        r1 = response[0]
        if (startStation[0] not in r1['destination'][0][1]['subject']) and (endStation[0] not in r1['destination'][0][1]['subject']):
            assert False, "Error when updating the booking reports"

        if len(response) > 1:
            r2 = response[1]
            if (startStation[0] not in r2['destination'][0][1]['subject']) and (endStation[0] not in r2['destination'][0][1]['subject']):
                assert False, "Error when updating the booking reports"

        assert "Error" not in response, "Found errors when generating reports"

    def cleanUp(self):
        import os
        # Restores "Now" time
        self.setNowTime(self._now)
        
        # Delete the test reports
        for i in range(len(self.report_files)):
            if os.path.exists(self.report_files[i]):
                os.remove(self.report_files[i])        