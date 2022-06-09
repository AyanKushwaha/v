# ../../cio/acci.py
from carmtest.framework import *

#import tests.support as ts
#from tests.decorators import *

from AbsTime import AbsTime
from cio.acci import ACCI, ACCIHead, accidump, fstr, ftuple, decode, Slice


class TestSlice(TestFixture):
    """
    Test slice
    """
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None

    def test_01_slice(self):
        x = "ABCDEFGHIJKLMN"
        s = Slice(x)
        self.assertEqual(s(2), "AB")
        self.assertEqual(s(3), "CDE")
        self.assertEqual(s(5), "FGHIJ")
        self.assertEqual(s(-1), "")
        self.assertEqual(s(0), "")
        self.assertEqual(s(1), "J")
        self.assertEqual(s(6), "KLMN")


class Testfstr(TestFixture):
    """
    Test fstr
    """
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None

    def test_01_fstr(self):
        x = fstr("A test string")
        self.assertEqual(x, "A test string")

    def test_02_fstr(self):
        x = fstr("A test string", ("P01", 0, 0))
        self.assertEqual(x, "A test string")
        self.assert_(hasattr(x, 'formats'))
        self.assertEqual(x.formats, [("P01", 0, 0)])
        self.assertEqual(x.formats[0].lineformat(1), "001P01000000           ")

    def test_03_fstr(self):
        x = fstr()
        self.assertEqual(x, "")

    def test_04_fstr(self):
        x = fstr('test', ('P02', 0, 0), ('P04', 1, 4))
        self.assert_(hasattr(x, 'formats'))
        self.assertEqual([f.lineformat(1) for f in x.formats], ["001P02000000           ", "001P04001004           "])
        self.assertEqual(x.formats, [('P02', 0, 0), ('P04', 1, 4)])


class Testftuple(TestFixture):
    """
    Test ftuple
    """
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None

    def test_01_ftuple(self):
        x = ftuple(("P01", 0, 0))
        self.assertEqual(x, ("P01", 0, 0))
        self.assertEqual(str(x), "P01000000           ")

    def test_02_ftuple(self):
        x = ftuple(("H01", 3, 4))
        self.assertEqual(x.code, "H01")
        self.assertEqual(x.start, 3)
        self.assertEqual(x.end, 4)

    def test_03_ftuple(self):
        def f():
            x = ftuple(("A", 0))
        self.assertRaises(ValueError, f)


class TestACCIHead(TestFixture):
    """
    Test CCI Head
    """
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None

    def test_01_accihead(self):
        x = ACCIHead(mesno="20", cico=2, dutycd="X", activityid="BL", adep="ARN", udor=AbsTime("20070501"))
        self.assertEqual(str(x), "0200202X  BL      20070501ARN000000000000000000000000000000000000         NNNN0000")
        x(std=AbsTime("20070501 12:31"))
        self.assertEqual(str(x), "0200202X  BL      20070501ARN200705011231000000000000000000000000         NNNN0000")

    def test_02_accihead(self):
        x = ACCIHead(mesno="20", cico=2, dutycd="X", activityid="BL",
                adep="ARN", udor=AbsTime("20070501"))
        self.assertEqual(x.mesno, "20")
        self.assertEqual(x.cico, 2)
        self.assertEqual(x.dutycd, "X")
        self.assertEqual(x.activityid, "BL")
        self.assertEqual(x.adep, "ARN")
        self.assertEqual(x.udor.split(), (2007, 5, 1, 0, 0))
        self.assertEqual(x.sta, None)

    def test_03_accihead(self):
        x = ACCIHead(mesno="20", cico=2, dutycd="X", activityid="BL",
                adep="ARN", udor=AbsTime("20070501"))
        self.assertEqual(x.mesno, "20")
        self.assertEqual(x.cico, 2)
        self.assertEqual(x.dutycd, "X")
        self.assertEqual(x.activityid, "BL")
        self.assertEqual(x.adep, "ARN")
        self.assertEqual(x.udor.split(), (2007, 5, 1, 0, 0))
        x(sta=AbsTime("20070513 10:10"))
        self.assertEqual(x.sta.split(), (2007, 5 ,13, 10, 10))
        self.assertEqual(str(x), "0200202X  BL      20070501ARN000000000000200705131010000000000000         NNNN0000")


class ACCITest(TestFixture):
    """
    Test ACCI
    """
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None

    def test_01_acci(self):
        x = ACCI(["Test", '', fstr("Foeregaaende tom rad", ("XUL", 0, 3))])
        x.header(mesno=30, cico=2, eta=AbsTime("19650110"))
        self.assertEqual(str(x), "0300302           00000000   000000000000000000000000196501100000         NNNN0000000404Test0020Foeregaaende tom rad13End of print.002003XUL000003           004P02000000           ")
        self.assertEqual(x.decode(), "Test\n\nFoeregaaende tom rad\nEnd of print.")

    def test_02_acci(self):
        h = ACCIHead(mesno=30, cico=2, eta=AbsTime("19650110"))
        x = ACCI(["Test", '', fstr("Foeregaaende tom rad", ("XUL", 0, 3))], h)
        self.assertEqual(str(x), "0300302           00000000   000000000000000000000000196501100000         NNNN0000000404Test0020Foeregaaende tom rad13End of print.002003XUL000003           004P02000000           ")
        self.assertEqual(x.decode(), "Test\n\nFoeregaaende tom rad\nEnd of print.")
        self.assertEqual(x, ["Test", "", "Foeregaaende tom rad"])

    def test_03_acci(self):
        z = ACCI()
        z.append("Line 1")
        z.append(fstr("Formatted line", ("FO1", 0, 0)))
        z.append(fstr("Another Formatted line", ("FO2", 0, 0), ("H01", 3, 4)))
        z.append(fstr("A third formatted line", ("FO3", 3, 6)))
        z.append('')
        z.append("Prev line was empty")
        z(mesno=30, eta=AbsTime("19650110"))
        self.assertEqual(str(z), "030030            00000000   000000000000000000000000196501100000         NNNN0000000706Line 114Formatted line22Another Formatted line22A third formatted line0019Prev line was empty13End of print.005002FO1000000           003FO2000000           003H01003004           004FO3003006           007P02000000           ")
        self.assertEqual([x for x in z], ['Line 1', 'Formatted line', 'Another Formatted line', 'A third formatted line', '', 'Prev line was empty', 'End of print.'])
        accidump(z)
        print z.asXML()

    def test_04_acci(self):
        z = ACCI(end_of_print=False)
        z.append("Line 1")
        z.append(fstr("Formatted line", ("FO1", 0, 0)))
        z.append(fstr("Another Formatted line", ("FO2", 0, 0), ("H01", 3, 4)))
        z.append(fstr("A third formatted line", ("FO3", 3, 6)))
        z.append('')
        z.append("Prev line was empty")
        z(mesno=30, eta=AbsTime("19650110"))
        self.assertEqual(str(z), "030030            00000000   000000000000000000000000196501100000         NNNN0000000606Line 114Formatted line22Another Formatted line22A third formatted line0019Prev line was empty004002FO1000000           003FO2000000           003H01003004           004FO3003006           ")
        self.assertEqual([str(x) for x in z], ['Line 1', 'Formatted line', 'Another Formatted line', 'A third formatted line', '', 'Prev line was empty'])
        accidump(z)
        print z.asXML()
