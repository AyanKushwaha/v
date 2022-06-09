from carmtest.framework import *

# Make your changes here!

class Shouter:
    width = 78
    char = "*"
    def shout(self, s):
        print
        print self.width * self.char
        print s
        print self.width * self.char

class VacationList(TestFixture):
    """Vacation lists (SE,NO)"""
    
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self.firstdate, self.lastdate = self.rave().eval('fundamental.%pp_start%', 'fundamental.%pp_end%')

    def test_001_vacation_list_se(self):
        import salary.vacation_lists as salary_vacationlists
        s = Shouter()
        country = "SE"
        s.shout("Vaction list %s (%s-%s)" % (country, self.firstdate, self.lastdate))
        of = salary_vacationlists.vacation(country, self.firstdate, self.lastdate)
        s.shout("Output filename was '%s'" % str(of))

    def test_002_vacation_list_no(self):
        import salary.vacation_lists as salary_vacationlists
        s = Shouter()
        country = "NO"
        s.shout("Vacation list %s (%s-%s)" % (country, self.firstdate, self.lastdate))
        of = salary_vacationlists.vacation(country, self.firstdate, self.lastdate)
        s.shout("Output filename was '%s'" % str(of))

class TestVAYear(TestFixture):
    """
    Test Vacation year
    """
    facit = {
        (('C', 'BJS', 'SK'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'BJS', 'SK'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'BJS', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'BJS', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'CPH', 'SK'), 2008): (AbsTime(2008, 5, 1, 0, 0), AbsTime(2009, 5, 1, 0, 0)),
        (('C', 'CPH', 'SK'), 2009): (AbsTime(2009, 5, 1, 0, 0), AbsTime(2010, 5, 1, 0, 0)),
        (('C', 'CPH', 'SK'), 2010): (AbsTime(2010, 5, 1, 0, 0), AbsTime(2011, 5, 1, 0, 0)),
        (('C', 'CPH', 'SK'), 2011): (AbsTime(2011, 5, 1, 0, 0), AbsTime(2012, 5, 1, 0, 0)),
        (('C', 'NRT', 'SK'), 2008): (AbsTime(2008, 4, 1, 0, 0), AbsTime(2009, 4, 1, 0, 0)),
        (('C', 'NRT', 'SK'), 2009): (AbsTime(2009, 4, 1, 0, 0), AbsTime(2010, 4, 1, 0, 0)),
        (('C', 'NRT', 'SK'), 2010): (AbsTime(2010, 4, 1, 0, 0), AbsTime(2011, 4, 1, 0, 0)),
        (('C', 'NRT', 'SK'), 2011): (AbsTime(2011, 4, 1, 0, 0), AbsTime(2012, 4, 1, 0, 0)),
        (('C', 'OSL', 'BU'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'OSL', 'BU'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'OSL', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'OSL', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'OSL', 'SK'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'OSL', 'SK'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'OSL', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'OSL', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'STO', 'BU'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('C', 'STO', 'BU'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 6, 1, 0, 0)),
        (('C', 'STO', 'BU'), 2010): (AbsTime(2010, 6, 1, 0, 0), AbsTime(2011, 6, 1, 0, 0)),
        (('C', 'STO', 'BU'), 2011): (AbsTime(2011, 6, 1, 0, 0), AbsTime(2012, 6, 1, 0, 0)),
        (('C', 'STO', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('C', 'STO', 'SK'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 6, 1, 0, 0)),
        (('C', 'STO', 'SK'), 2010): (AbsTime(2010, 6, 1, 0, 0), AbsTime(2011, 6, 1, 0, 0)),
        (('C', 'STO', 'SK'), 2011): (AbsTime(2011, 6, 1, 0, 0), AbsTime(2012, 6, 1, 0, 0)),
        (('C', 'SVG', 'BU'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'SVG', 'BU'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'SVG', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'SVG', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'SVG', 'SK'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'SVG', 'SK'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'SVG', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'SVG', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'TRD', 'BU'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'TRD', 'BU'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'TRD', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'TRD', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('C', 'TRD', 'SK'), 2008): (AbsTime(2008, 1, 1, 0, 0), AbsTime(2009, 1, 1, 0, 0)),
        (('C', 'TRD', 'SK'), 2009): (AbsTime(2009, 1, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('C', 'TRD', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('C', 'TRD', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'CPH', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 5, 1, 0, 0)),
        (('F', 'CPH', 'SK'), 2009): (AbsTime(2009, 5, 1, 0, 0), AbsTime(2010, 5, 1, 0, 0)),
        (('F', 'CPH', 'SK'), 2010): (AbsTime(2010, 5, 1, 0, 0), AbsTime(2011, 5, 1, 0, 0)),
        (('F', 'CPH', 'SK'), 2011): (AbsTime(2011, 5, 1, 0, 0), AbsTime(2012, 5, 1, 0, 0)),
        (('F', 'OSL', 'BU'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'OSL', 'BU'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'OSL', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'OSL', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'OSL', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'OSL', 'SK'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'OSL', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'OSL', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'STO', 'BU'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'STO', 'BU'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 6, 1, 0, 0)),
        (('F', 'STO', 'BU'), 2010): (AbsTime(2010, 6, 1, 0, 0), AbsTime(2011, 6, 1, 0, 0)),
        (('F', 'STO', 'BU'), 2011): (AbsTime(2011, 6, 1, 0, 0), AbsTime(2012, 6, 1, 0, 0)),
        (('F', 'STO', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'STO', 'SK'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 6, 1, 0, 0)),
        (('F', 'STO', 'SK'), 2010): (AbsTime(2010, 6, 1, 0, 0), AbsTime(2011, 6, 1, 0, 0)),
        (('F', 'STO', 'SK'), 2011): (AbsTime(2011, 6, 1, 0, 0), AbsTime(2012, 6, 1, 0, 0)),
        (('F', 'SVG', 'BU'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'SVG', 'BU'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'SVG', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'SVG', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'SVG', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'SVG', 'SK'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'SVG', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'SVG', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'TRD', 'BU'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'TRD', 'BU'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'TRD', 'BU'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'TRD', 'BU'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
        (('F', 'TRD', 'SK'), 2008): (AbsTime(2008, 6, 1, 0, 0), AbsTime(2009, 6, 1, 0, 0)),
        (('F', 'TRD', 'SK'), 2009): (AbsTime(2009, 6, 1, 0, 0), AbsTime(2010, 1, 1, 0, 0)),
        (('F', 'TRD', 'SK'), 2010): (AbsTime(2010, 1, 1, 0, 0), AbsTime(2011, 1, 1, 0, 0)),
        (('F', 'TRD', 'SK'), 2011): (AbsTime(2011, 1, 1, 0, 0), AbsTime(2012, 1, 1, 0, 0)),
    }

    @REQUIRE("Mirador")
    def __init__(self):
        TestFixture.__init__(self)

    def testAll(self):
        import crewlists.subreports.VACATION as v
        # Quick'n'ugly
        L = {}
        for ce in self.table('crew_employment'):
            if ce.company.id == 'SC':
                continue
            key = (ce.crewrank.maincat.id, ce.base.id, ce.company.id)
            for y in (2008, 2009, 2010, 2011):
                if not (key, y) in L:
                    if ce.validfrom <= AbsTime(y, 1, 1, 0, 0) and ce.validto > AbsTime(y, 1, 1, 0, 0):
                        L[(key, y)] = ce.extperkey
        for z in sorted(L):
            i = v.InputData((3, L[z], 'VA', str(z[1])))
            self.assertEqual(self.facit[z], (i.va_start, i.va_end), "%s-%s %s" % (i.va_start, i.va_end, z))
