"""
Test Editfact
"""


from carmtest.framework import *
from AbsTime import AbsTime

import utils.edifact as edifact

class TestTranslationDict(TestFixture):
    "Test translation dict"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001(self):
        x = edifact.TranslationDict('ACD', {66: 'X'})
        self.assertEqual(x[65], u'A')
        self.assertEqual(x[66], u'X')
        self.assertEqual(x[99], None)


class TestConversions(TestFixture):
    "Test conversions"    
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001_latin1_to_edifact(self):
        self.assertEqual(edifact.latin1_to_edifact('1234'), '1234')
        self.assertEqual(edifact.latin1_to_edifact(1234), '1234')
        self.assertEqual(edifact.latin1_to_edifact('\n' + chr(12)), '')


class TestSpecial(TestFixture):
    "Test Special"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_str(self):
        self.assertEqual(str(edifact.special), ":+.? '")

    def test_002_attr(self):
        self.assertEqual(edifact.special.level, 'UNOA')
        self.assertEqual(edifact.special.component, ':')
        self.assertEqual(edifact.special.data, '+')
        self.assertEqual(edifact.special.decimal, '.')
        self.assertEqual(edifact.special.release, '?')
        self.assertEqual(edifact.special.reserved, ' ')
        self.assertEqual(edifact.special.terminator, "'")

    def test_003_escape(self):
        self.assertEqual(edifact.special.escape('abc+def:??.b'), 'ABC?+DEF?:????.B')


class TestElist(TestFixture):
    "Test elist"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)             
     
    def test_001_init(self):
        x = edifact.Elist('a', 'b', 'c?:')
        self.assertEqual(str(x), 'abc?:')

    def test_002_compress(self):
        x = edifact.Elist()
        x.append('abcd')
        x.append('efgh')
        x.append('')
        self.assertEqual(x, ['abcd', 'efgh', ''])
        x.compress()
        self.assertEqual(x, ['abcd', 'efgh'])

    def test_003_size(self):
        x = edifact.Elist('12345', '12345')
        self.assertEqual(x, ['12345', '12345'])
        self.assertEqual(x.size(), 10)


class TestElistAttr(TestFixture):
    "Test elist attr"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_add(self):
        x = edifact.ElistAttr()
        x.append('abc')
        x.append('def')
        x('first', 'second', 'third', 'fourth')
        self.assertEqual(x.first, 'abc')
        self.assertEqual(x.second, 'def')
        x.fourth = 'jkl'
        self.assertEqual(x, ['abc', 'def', '', 'jkl'])
        del x.fourth
        self.assertEqual(x, ['abc', 'def'])


class TestSegment(TestFixture):
    "Test segment"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_basic(self):
        x = edifact.Segment('XXX')
        x('alpha', ('beta', ('beta_1', 'beta_2', 'beta_3', 'beta_4')))
        x.append('123')
        x.append('abc')
        self.assertEqual(x, ['123', 'abc'])
        self.assertEqual(str(x), "XXX+123+ABC'")
        x.beta.beta_2 = '4+3=7'
        self.assertEqual(str(x), "XXX+123+ABC:4?+3=7'")
        self.assertEqual(x.alpha, '123')
        self.assertEqual(x.beta, ['abc', '4+3=7'])
        self.assertEqual(x.beta.beta_1, 'abc')
        self.assertEqual(x.beta.beta_2, '4+3=7')
        x.beta.beta_4 = '9999'
        self.assertEqual(str(x), "XXX+123+ABC:4?+3=7::9999'")

    def test_002_size(self):
        x = edifact.Segment('XXX')
        x('alpha', ('beta', ('beta_1', 'beta_2', 'beta_3', 'beta_4')))
        x.beta = edifact.Composite('1234', '1414')
        self.assertEqual(str(x), "XXX++1234:1414'")
        self.assertEqual(x.size(), 15)
        x.beta.beta_4 = 'abc+123'
        self.assertEqual(str(x), "XXX++1234:1414::ABC?+123'")
        self.assertEqual(x.size(), 25)

    @REQUIRE("NotMigrated")
    def test_003_datatypes(self):
        x = edifact.Segment('XXX')
        x('alpha', ('beta', ('beta_1', 'beta_2', 'beta_3', 'beta_4')))
        x.beta.beta_1 = 1
        x.beta.beta_2 = None # What should be the correct thing to do here?
        self.assertEqual(str(x), "XXX++1'") #FAILS


class TestComposite(TestFixture):
    "Test composite"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        x = edifact.Composite('abc', 'def', '', 'ghi')
        self.assertEqual(str(x), 'ABC:DEF::GHI')
        self.assertEqual(x.size(), 12)
        self.assertEqual(x, ['abc', 'def', '', 'ghi'])
        del x[3]
        self.assertEqual(x, ['abc', 'def', ''])
        self.assertEqual(str(x), 'ABC:DEF:')
        x.compress()
        self.assertEqual(str(x), 'ABC:DEF')

    def test_002(self):
        x = edifact.Composite('abc', 'def', '', 'ghi')('item1', 'item2', 'item3', 'item4', 'item5')
        x.item5 = 'zz'
        self.assertEqual(str(x), 'ABC:DEF::GHI:ZZ')
        self.assertEqual(x.size(), 15)
        del x.item5
        del x.item4
        self.assertEqual(str(x), 'ABC:DEF')
        self.assertEqual(x.size(), 7)
        x.item4 = 1123
        self.assertEqual(str(x), 'ABC:DEF::1123')


class TestComplementarySegment(TestFixture):
    "Test complementary segment"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001(self):
        x = edifact.Elist()
        p = edifact.Segment('ABC')('reference')
        p.reference = 1234
        x.append(p)
        x.append(edifact.Segment('DEF', 'A+B'))
        y = edifact.ComplementarySegment('XYZ', p, x)
        x.append(y)
        self.assertEqual(str(y), "XYZ+3+1234'")
        self.assertEqual(str(x), "ABC+1234'DEF+A?+B'XYZ+3+1234'")
        self.assertEqual(p.size(), 9)
        self.assertEqual(len(y), 11)
        # Important tests
        self.assertEqual(x.size(), 29)
        p.reference = 'ABC:99'
        self.assertEqual(str(x), "ABC+ABC?:99'DEF+A?+B'XYZ+3+ABC?:99'")
        self.assertEqual(x.size(), 35)


class TestSegmentTag(TestFixture):
    "Test segment tag"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        st1 = edifact.SegmentTag('ABC')
        s1 = edifact.Segment(st1)
        e = edifact.Elist()
        e.append(s1)
        st2 = edifact.SegmentTag('ABC')
        s2 = edifact.Segment(st2)
        s2.append('ACOSTA')
        e.append(s2)
        self.assertEqual(str(e), "ABC+'ABC+ACOSTA'")
        st2.level_1 = 3
        self.assertEqual(str(e), "ABC+'ABC:3+ACOSTA'")
        st2.level_2 = 1
        self.assertEqual(str(e), "ABC+'ABC:3:1+ACOSTA'")
        st2.level_1 += 1
        self.assertEqual(str(e), "ABC+'ABC:4:1+ACOSTA'")


class TestElement(TestFixture):
    "Test element"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        e = edifact.Element('ABCD+1234')
        self.assertEqual(e, 'ABCD?+1234')

class TestInterchange(TestFixture):
    "Test interchange"

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        i = edifact.Interchange(edifact.EDIFACT)
        i.unb.reference = '9999'
        i.append(edifact.Segment('ABC', '1234'))
        self.assertEqual(str(i), "UNA:+.? 'UNB+++++9999'ABC+1234'UNZ+1+9999'")
        self.assertEqual(i.size(), 42)


class TestFunctionalGroup(TestFixture):
    "Test Functional group"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        i = edifact.FunctionalGroup(edifact.EDIFACT)
        i.ung.reference = '9999'
        i.append(edifact.Segment('ABC', '1234'))
        self.assertEqual(str(i), "UNG+++++9999'ABC+1234'UNE+1+9999'")
        self.assertEqual(i.size(), 33)


class TestMessage(TestFixture):
    "Test Message"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        i = edifact.Message(edifact.EDIFACT)
        i.unh.reference = '9999'
        i.append(edifact.Segment('ABC', '1234'))
        self.assertEqual(str(i), "UNH+9999'ABC+1234'UNT+3+9999'")
        self.assertEqual(i.size(), 29)
        i.append(edifact.Segment('ABC', '1234'))
        self.assertEqual(str(i), "UNH+9999'ABC+1234'ABC+1234'UNT+4+9999'")
        self.assertEqual(i.size(), 38)







