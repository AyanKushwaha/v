"""
Test Timezone
"""


from carmtest.framework import *

from datetime import date, time, timedelta, datetime
from utils import timezones


class TestTZ_Europe(TestFixture):
    "Timezone Europe"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    
    def setUp(self):
        self.UTC = timezones.UTC
        self.Amsterdam = timezones.CET
        self.London = timezones.WET
     
    def test_001(self):
        # Last day of DST:
        dt = datetime(2002, 10, 26, 12, 0, 0, tzinfo=self.Amsterdam)
        self.assertEqual(dt.ctime(), 'Sat Oct 26 12:00:00 2002')
        # The UTC offset is 2 hours
        self.assertEqual(dt.utcoffset().seconds, 7200)
        # Add one day, getting Sunday noon on the first day of standard time
        dt += timedelta(days=1)
        self.assertEqual(dt.ctime(), 'Sun Oct 27 12:00:00 2002')
        # The UTC offset is 1 hour
        self.assertEqual(dt.utcoffset().seconds, 3600)

    def test_002(self):
        # Last Wednesday before DST ends:
        dt = datetime(2002, 10, 23, 12, 0, 0, tzinfo=self.Amsterdam)
        self.assertEqual(dt.ctime(), 'Wed Oct 23 12:00:00 2002')
        # UTC offset is 2 hours
        self.assertEqual(dt.utcoffset().seconds, 7200)
        # And a week later:
        dt += timedelta(days=7)
        self.assertEqual(dt.utcoffset().seconds, 3600)

    def test_003(self):
        # One second before DST ends:
        dt = datetime(2002, 10, 27, 1, 59, 59, tzinfo=self.Amsterdam)
        self.assertEqual(dt.ctime() + ' ' + dt.tzname(), 'Sun Oct 27 01:59:59 2002 CEST')
        self.assertEqual(dt.astimezone(self.UTC).ctime() + ' UTC', 'Sat Oct 26 23:59:59 2002 UTC')
        # This is actually one whole hour before the DST ends, this is because
        # the first hour in DST is unrepresentable.

        # Check time in London
        dt1 = dt.astimezone(self.London)
        self.assertEqual(dt1.ctime() + ' ' + dt1.tzname(), 'Sun Oct 27 00:59:59 2002 WEST')

        # Now add one second, getting to 02:00
        dt += timedelta(seconds=1)
        self.assertEqual(dt.ctime() + ' ' + dt.tzname(), 'Sun Oct 27 02:00:00 2002 CET')
        self.assertEqual(dt.astimezone(self.UTC).ctime() + ' UTC', 'Sun Oct 27 01:00:00 2002 UTC')
        dt1 = dt.astimezone(self.London)
        self.assertEqual(dt1.ctime() + ' ' + dt1.tzname(), 'Sun Oct 27 01:00:00 2002 WET')

    def test_004(self):
        self.assertEqual(
            str(datetime(2002, 10, 26, 23, 0, 0, tzinfo=self.UTC).astimezone(self.Amsterdam)),
            '2002-10-27 01:00:00+02:00'
        )

    def test_005(self):
        self.assertEqual(
            str(datetime(2002, 10, 27, 0, 0, 0, tzinfo=self.UTC).astimezone(self.Amsterdam)),
            '2002-10-27 02:00:00+01:00'
        )

    def test_006(self):
        self.assertEqual(
            str(datetime(2002, 10, 27, 1, 0, 0, tzinfo=self.UTC).astimezone(self.Amsterdam)),
            '2002-10-27 02:00:00+01:00'
        )
