"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
from utils.airport_tz import Airport


from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime

import datetime
from utils import dt

class TestTimeDeltaConversion(TestFixture):
    "Time delta conversion"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)            
    
    def test_001_td2d(self):
        r = 13
        td = datetime.timedelta(days=13)
        t = dt.td2d(td) 
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_002_td2m(self):
        r = 3931
        td = datetime.timedelta(days=2, seconds=63060)
        t = dt.td2m(td) 
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_003_td2s(self):
        r = 89700
        td = datetime.timedelta(days=1, seconds=3300)
        t = dt.td2s(td)
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_004_d2td(self):
        r = datetime.timedelta(days=13)
        d = 13
        t = dt.d2td(d)
        self.assertTrue(isinstance(t, datetime.timedelta))
        self.assertEqual(t, r)

    def test_005_m2td(self):
        r = datetime.timedelta(days=2, seconds=63060)
        m = 3931
        t = dt.m2td(m)
        self.assertTrue(isinstance(t, datetime.timedelta))
        self.assertEqual(t, r)
    
    def test_006_s2td(self):
        r = datetime.timedelta(days=2, seconds=63060)
        s = 235860
        t = dt.s2td(s)
        self.assertTrue(isinstance(t, datetime.timedelta))
        self.assertEqual(t, r)

    def test_007_from_reltime(self):
        r = datetime.timedelta(days=1, seconds=3300)
        rt = RelTime(1495)
        t = dt.m2td(rt)
        self.assertTrue(isinstance(t, datetime.timedelta))
        self.assertEqual(t, r)

    def test_008_to_reltime(self):
        r = RelTime(1495)
        td = datetime.timedelta(days=1, seconds=3300)
        t = RelTime(dt.td2m(td))
        self.assertTrue(isinstance(t, RelTime))
        self.assertEqual(t, r)


class TestDateTimeConversion(TestFixture):
    "Date delta conversion"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)                
    
    def test_001_dt2d(self):
        r = 8550
        dtime = datetime.datetime(2009, 5, 30)
        t = dt.dt2d(dtime)
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_002_dt2m(self):
        r = 12312391
        dtime = datetime.datetime(2009, 5, 30, 6, 31)
        t = dt.dt2m(dtime)
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_003_dt2s(self):
        r = 738743464
        dtime = datetime.datetime(2009, 5, 30, 6, 31, 4)
        t = dt.dt2s(dtime)
        self.assertTrue(isinstance(t, int))
        self.assertEqual(t, r)

    def test_004_d2dt(self):
        r = datetime.datetime(2009, 5, 30)
        d = 8550
        t = dt.d2dt(d)
        self.assertTrue(isinstance(t, datetime.datetime))
        self.assertEqual(t, r)

    def test_005_m2dt(self):
        r = datetime.datetime(2009, 5, 30, 6, 31)
        m = 12312391
        t = dt.m2dt(m)
        self.assertTrue(isinstance(t, datetime.datetime))
        self.assertEqual(t, r)

    def test_006_s2dt(self):
        r = datetime.datetime(2009, 5, 30, 6, 31, 4)
        s = 738743464
        t = dt.s2dt(s)
        self.assertTrue(isinstance(t, datetime.datetime))
        self.assertEqual(t, r)

    def test_007_from_abstime(self):
        r = datetime.datetime(2009, 5, 30, 6, 31)
        a = AbsTime("20090530 06:31")
        t = dt.m2dt(a)
        self.assertTrue(isinstance(t, datetime.datetime))
        self.assertEqual(t, r)

    def test_008_to_abstime(self):
        r = AbsTime("20090530 06:31")
        dtime = datetime.datetime(2009, 5, 30, 6, 31)
        t = AbsTime(dt.dt2m(dtime))
        self.assertTrue(isinstance(t, AbsTime))
        self.assertEqual(t, r)

    def test_009_from_absdate(self):
        r = datetime.datetime(2009, 5, 30)
        a = AbsDate("20090530")
        t = dt.m2dt(a)
        self.assertTrue(isinstance(t, datetime.datetime))
        self.assertEqual(t, r)

    def test_010_to_absdate(self):
        r = AbsDate("20090530")
        dtime = datetime.datetime(2009, 5, 30)
        t = AbsDate(dt.dt2m(dtime))
        self.assertTrue(isinstance(t, AbsDate))
        self.assertEqual(t, r)

    def test_011_str2dt(self):
        self.assertEqual(dt.str2dt("2010-01-10 12:33:55"), datetime.datetime(2010, 1, 10, 12, 33, 55))
        self.assertEqual(dt.str2dt("20100110 12:33:55"), datetime.datetime(2010, 1, 10, 12, 33, 55))
        self.assertEqual(dt.str2dt("10Jan2010 12:33:55"), datetime.datetime(2010, 1, 10, 12, 33, 55))
        self.assertEqual(dt.str2dt("10Jan2010 12:33:55.132"), datetime.datetime(2010, 1, 10, 12, 33, 55, 132000))
        self.assertEqual(dt.str2dt("10Jan2010 12:33:55.0999"), datetime.datetime(2010, 1, 10, 12, 33, 55, 99900))
        self.assertEqual(dt.str2dt("10-12-11 12:33:55.9"), datetime.datetime(2010, 12, 11, 12, 33, 55, 900000))
        self.assertEqual(dt.str2dt("20100110 12:33:55.314156"), datetime.datetime(2010, 1, 10, 12, 33, 55, 314156))
        self.assertEqual(dt.str2dt("2010-01-10"), datetime.datetime(2010, 1, 10))
        self.assertEqual(dt.str2dt("20100110"), datetime.datetime(2010, 1, 10))
        self.assertEqual(dt.str2dt("10Jan2010"), datetime.datetime(2010, 1, 10))
        self.assertEqual(dt.str2dt("10Jan2010 12:33"), datetime.datetime(2010, 1, 10, 12, 33))

