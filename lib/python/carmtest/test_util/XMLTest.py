"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
import utils.xmlutil as xml


class TestKeyValueInit(TestFixture):
    "XML key value init"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_Init0Empty(self):
        x = xml.KeyValue()
        self.assert_(x.data == [])

    def test_002_Init1Arg(self):
        x = xml.KeyValue(('keyA', 'valueA'))
        self.assert_(x.data == [('keyA', 'valueA')])

    def test_003_Init2Args(self):
        x = xml.KeyValue(('keyA', 'valueA'), ('keyB', 'valueB'))
        self.assert_(x.data == [('keyA', 'valueA'), ('keyB', 'valueB')])

    def test_004_InitList(self):
        L = [('keyA', 'valueA'), ('keyB', 'valueB')]
        x = xml.KeyValue(L)
        self.assert_(x.data == [('keyA', 'valueA'), ('keyB', 'valueB')])

    def test_004_InitCall(self):
        L = [('keyA', 'valueA'), ('keyB', 'valueB')]
        x = xml.KeyValue(L)
        x(('keyC', 'valueC'), ('keyD', 'valueD'))
        self.assert_(x.data == [('keyA', 'valueA'), ('keyB', 'valueB'), ('keyC', 'valueC'), ('keyD', 'valueD')])

    def test_005_InitNamed(self):
        L = [('keyA', 'valueA'), ('keyB', 'valueB')]
        x = xml.KeyValue(L, keyX='valueX')
        self.assert_(x.data == [('keyA', 'valueA'), ('keyB', 'valueB'), ('keyX', 'valueX')])

    def test_006_InitMap(self):
        L = {'keyA': 'valueA', 'keyB': 'valueB'}
        x = xml.KeyValue(L)
        self.assert_(x.data == [('keyA', 'valueA'), ('keyB', 'valueB')] or x.data == [('keyB', 'valueB'), ('keyA', 'valueA')])


class TestKeyValueOps(TestFixture):
    "XML key value ops"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.x = xml.KeyValue(('keyA', 'valueA'), ('keyB', 'valueB'))

    def test_001_00Member1(self):
        self.assert_('keyA' in self.x)

    def test_002_00Member2(self):
        self.assert_('keyB' in self.x)

    def test_003_00NonMember(self):
        self.failIf('keyC' in self.x)

    def test_004_01GetItem(self):
        vb = self.x['keyB']
        self.assert_(vb == 'valueB')

    def _getMissing(self):
        return self.x['keyX']

    def test_005_01GetItemNotThere(self):
        self.assertRaises(KeyError, self._getMissing)

    def test_006_02ASetItem(self):
        self.x['keyC'] = 'valueC'
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyB', 'valueB'), ('keyC', 'valueC')])

    def test_007_02BSetItem(self):
        self.x['keyB'] = 'VALUEB'
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyB', 'VALUEB')])

    def test_008_03DelItem(self):
        self.x['keyC'] = 'valueC'
        del self.x['keyB']
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyC', 'valueC')])


class TestKeyValueIter(TestFixture):
    "Kay value iter"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def setUp(self):
        self.x = xml.KeyValue(('keyA', 'valueA'), ('keyB', 'valueB'), ('keyC', 'valueC'), ('keyD', 'valueD'))
    
    def test_001_Keys(self):
        self.assert_(self.x.keys() == ['keyA', 'keyB', 'keyC', 'keyD'])

    def test_002_Values(self):
        self.assert_(self.x.values() == ['valueA', 'valueB', 'valueC', 'valueD'])

    def test_003_Items(self):
        self.assert_(self.x.items() == [('keyA', 'valueA'), ('keyB', 'valueB'), ('keyC', 'valueC'), ('keyD', 'valueD')])

    def test_004_Iter(self):
        L = []
        for k in self.x:
            L.append(k)
        self.assert_(L == ['keyA', 'keyB', 'keyC', 'keyD'])

    def test_005_IterItems(self):
        L = []
        for k in self.x.iteritems():
            L.append(k)
        self.assert_(L == self.x.data)

    def test_006_Pop(self):
        j = self.x.pop('keyB')
        self.assert_(j == 'valueB')
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyC', 'valueC'), ('keyD', 'valueD')])
        k = self.x.pop('keyB', 'default')
        self.assert_(k == 'default')
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyC', 'valueC'), ('keyD', 'valueD')])
        k = self.x.pop('keyC', 'default')
        self.assert_(k == 'valueC')
        self.assert_(self.x.data == [('keyA', 'valueA'), ('keyD', 'valueD')])


class TestXMLAttributes(TestFixture):
    "XML Attributes"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.full = xml.XMLAttributes(('keyA', 'valueA'), ('keyB', 'valueB'), ('keyC', 'valueC'), ('keyD', 'valueD'))
        self.empty = xml.XMLAttributes()

    def test_001_Empty(self):
        self.assert_(str(self.empty) == '')

    def test_002_Full(self):
        self.assert_(str(self.full) == 'keyA="valueA" keyB="valueB" keyC="valueC" keyD="valueD"')

    def test_003_Escape(self):
        esc = xml.XMLAttributes(('keyA', 'something was "quoted" here.'), ('key0', "Something else was using 'apostrophes'."))
        self.assertEqual(str(esc), 'keyA="something was &quot;quoted&quot; here." key0="Something else was using &apos;apostrophes&apos;."')


class innerElement(xml.XMLElement):
    def __init__(self):
        xml.XMLElement.__init__(self)
        self(xml.XMLElement('someElement', ['a', 'b']))
        self.append(xml.XMLElement('emptyElement'))


class outerElement(xml.XMLElement):
    def __init__(self, value):
        xml.XMLElement.__init__(self)
        self['version'] = "1.0"
        self['anotherAttribute'] = 33
        self.append(xml.XMLElement('v', value))
        self.append(xml.XMLElement('stringValue', "A string\nvalue."))
        self.append(innerElement())


class TestXMLElement(TestFixture):
    "XML Element"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def setUp(self):
        self.o = outerElement('xyz')
        self.result = """<outerElement version="1.0" anotherAttribute="33">
  <v>xyz</v>
  <stringValue>A string
value.</stringValue>
  <innerElement>
    <someElement>ab</someElement>
    <emptyElement />
  </innerElement>
</outerElement>"""

    def test_001_SubClass(self):
        self.assertEqual(str(self.o), self.result)

    def test_002_MixedUsage(self):
        # Covers some use cases
        root = xml.XMLElement('anElement', version='1.0')
        other = xml.XMLElement('anotherElement')
        other.xmlns = 'xsd'
        other['xmlns:ns'] = 'http://www.acosta.se/'
        other.append(xml.string('gn', 'Fredrik'))
        other.append(xml.string('sn', 'Acosta'))
        root.append(other)
        self.assertEqual(str(root), """<anElement version="1.0">
  <xsd:anotherElement xmlns:ns="http://www.acosta.se/">
    <gn>Fredrik</gn>
    <sn>Acosta</sn>
  </xsd:anotherElement>
</anElement>""")


class TestVarious(TestFixture):
    "XML Element"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001_XMLDocument(self):
        doc = xml.XMLDocument(xml.XMLElement('empty'))
        self.assertEqual(str(doc), """<?xml version="1.0" encoding="UTF-8"?>
<empty />""")

    def test_002_COMMENT(self):
        self.assertEqual(xml.COMMENT("Howzit?"), """<!-- Howzit? -->""")

    def test_003_CDATA(self):
        self.assertEqual(xml.CDATA("Howzit?"), """<![CDATA[Howzit?]]>""")
    

class TestConversions(TestFixture):
    "XML conversions"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001_base64Binary(self):
        self.assertEqual(str(xml.base64Binary('base64', 0)), "<base64>MA==\n</base64>")
        self.assertEqual(str(xml.base64Binary('base64', 'Fredrik')), "<base64>RnJlZHJpaw==\n</base64>")
        self.assertEqual(str(xml.base64Binary('base64', '')), "<base64 />")

    def test_002_boolean(self):
        self.assertEqual(str(xml.boolean('bool', False)), '<bool>false</bool>')
        self.assertEqual(str(xml.boolean('bool', True)), '<bool>true</bool>')
        self.assertEqual(str(xml.boolean('bool', '')), '<bool>false</bool>')
        self.assertEqual(str(xml.boolean('bool', None, default='true')), '<bool>true</bool>')
        def raises():
            return xml.boolean('bool', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_003_date(self):
        from AbsTime import AbsTime
        from RelTime import RelTime
        self.assertEqual(str(xml.date('date', AbsTime("20070913"))), '<date>2007-09-13</date>')
        self.assertEqual(str(xml.date('date', AbsTime("20070913"), utc=True)), '<date>2007-09-13Z</date>')
        self.assertEqual(str(xml.date('date', AbsTime("20070913"), tz=RelTime("01:00"))), '<date>2007-09-13+01:00</date>')
        self.assertEqual(str(xml.date('date', None)), '<date>0001-01-01</date>')
        self.assertEqual(str(xml.date('date', None, default='1965-01-10')), '<date>1965-01-10</date>')
        def raises():
            return xml.date('date', None, use_default=False)
        self.assertRaises(TypeError, raises)
        def raises2():
            return xml.date('date', 12)
        self.assertRaises(Exception, raises2)

    def test_004_dateTime(self):
        from AbsTime import AbsTime
        from RelTime import RelTime
        self.assertEqual(str(xml.dateTime('dateTime', AbsTime("20070913 12:10"))), '<dateTime>2007-09-13T12:10:00</dateTime>')
        self.assertEqual(str(xml.dateTime('dateTime', AbsTime("20070913 12:10"), utc=True)), '<dateTime>2007-09-13T12:10:00Z</dateTime>')
        self.assertEqual(str(xml.dateTime('dateTime', AbsTime("20070913 12:10"), tz=RelTime("01:00"))), '<dateTime>2007-09-13T12:10:00+01:00</dateTime>')
        def raises():
            return xml.dateTime('dateTime', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_005_decimal(self):
        self.assertEqual(str(xml.decimal('decimal', "0")), '<decimal>0.0</decimal>')
        self.assertEqual(str(xml.decimal('decimal', 12)), '<decimal>12.0</decimal>')
        self.assertEqual(str(xml.decimal('decimal', False)), '<decimal>0.0</decimal>')
        self.assertEqual(str(xml.decimal('decimal', 1.3)), '<decimal>1.3</decimal>')
        self.assertEqual(str(xml.decimal('decimal', None)), '<decimal>.0</decimal>')
        self.assertEqual(str(xml.decimal('decimal', None)), '<decimal>.0</decimal>')
        def raises():
            return xml.decimal('decimal', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_006_duration(self):
        from RelTime import RelTime
        self.assertEqual(str(xml.duration('duration', RelTime("0:00"))), '<duration>PT0H0M</duration>')
        self.assertEqual(str(xml.duration('duration', RelTime("14:12"))), '<duration>PT14H12M</duration>')
        self.assertEqual(str(xml.duration('duration', None)), '<duration>P0Y</duration>')
        def raises():
            return xml.duration('duration', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_007_integer(self):
        self.assertEqual(str(xml.integer('integer', "0" )), '<integer>0</integer>')
        self.assertEqual(str(xml.integer('integer', 12)), '<integer>12</integer>')
        self.assertEqual(str(xml.integer('integer', False)), '<integer>0</integer>')
        self.assertEqual(str(xml.integer('integer', 1.9)), '<integer>2</integer>')
        self.assertEqual(str(xml.integer('integer', None)), '<integer>0</integer>')
        def raises():
            return xml.integer('integer', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_008_string(self):
        self.assertEqual(str(xml.string('string', "0" )), '<string>0</string>')
        self.assertEqual(str(xml.string('string', "" )), '<string />')
        self.assertEqual(str(xml.string('string', 12)), '<string>12</string>')
        self.assertEqual(str(xml.string('string', 'F & C')), '<string>F &amp; C</string>')
        self.assertEqual(str(xml.string('string', 'F <> X')), '<string>F &lt;&gt; X</string>')
        self.assertEqual(str(xml.string('string', False)), '<string>False</string>')
        self.assertEqual(str(xml.string('string', None)), '<string />')
        def raises():
            return xml.string('string', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_009_char(self):
        self.assertEqual(str(xml.char('char', "0" )), '<char>0</char>')
        self.assertEqual(str(xml.char('char', 12)), '<char>1</char>')
        self.assertEqual(str(xml.char('char', False)), '<char>F</char>')
        self.assertEqual(str(xml.char('char', 1.3)), '<char>1</char>')
        self.assertEqual(str(xml.char('char', ' ')), '<char>_</char>')
        self.assertEqual(str(xml.char('char', ' ', preserve_space=True)), '<char> </char>')
        self.assertEqual(str(xml.char('char', None)), '<char>_</char>')
        def raises():
            return xml.char('char', None, use_default=False)
        self.assertRaises(TypeError, raises)

    def test_010_time(self):
        from AbsTime import AbsTime
        from RelTime import RelTime
        self.assertEqual(str(xml.time('time', AbsTime("20070913 12:10"))), '<time>12:10:00</time>')
        self.assertEqual(str(xml.time('time', AbsTime("20070913 12:10"), utc=True)), '<time>12:10:00Z</time>')
        self.assertEqual(str(xml.time('time', AbsTime("20070913 12:10"), tz=RelTime("01:00"))), '<time>12:10:00+01:00</time>')
        def raises():
            return xml.time('time', None, use_default=False)
        self.assertRaises(TypeError, raises)


class TestXSD(TestFixture):
    "XSD Test"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001_01char(self):
        r = xml.xsd.simpleType(xml.xsd.restriction(base="xs:string", length=1), name="char")
        self.assertEqual(str(r), """<xs:simpleType name="char">
  <xs:restriction base="xs:string">
    <xs:length value="1" />
  </xs:restriction>
</xs:simpleType>""")

    def test_002_01restriction(self):
        r = xml.xsd.simpleType(xml.xsd.restriction(base="xs:string",
            enumeration=("Audi", "Golf", "BMW")), name="carType")
        self.assertEqual(str(r), """<xs:simpleType name="carType">
  <xs:restriction base="xs:string">
    <xs:enumeration value="Audi" />
    <xs:enumeration value="Golf" />
    <xs:enumeration value="BMW" />
  </xs:restriction>
</xs:simpleType>""")

    def test_003_02(self):
        # These are tested implicitely in TestConversions
        from AbsTime import AbsTime
        self.assertEqual(xml.xsd.dateTime(AbsTime("20070913 12:10")), "2007-09-13T12:10:00")

