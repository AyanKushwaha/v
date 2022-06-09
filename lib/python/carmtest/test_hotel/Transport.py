'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *

class hotel_011_TransportBooking(TestFixture):
    "Transport bookings"
    
    @REQUIRE("Tracking")
    @REQUIRE("PlanLoaded")
    @REQUIRE("NotMigrated")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None
        
    
        
    def setUp(self):
        # Make sure "Now" time is within the planning period
        print self.raveExpr("fundamental.%pp_end%")
        self._now = self.getNowTime()
        self.setNowTime(self.raveExpr("fundamental.%pp_end%")-RelTime(12,0))