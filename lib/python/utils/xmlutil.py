
# {{{2 Log
# [acosta:06/261@23:20] First version.
# [acosta:07/010@14:35] Refactoring using better base classes. New approach to
#                       indentation problems
# [acosta:07/318@11:44] XMLElement is subclassing list instead of UserList, many
#                       (not so useful) methods removed. Added SOX printout and partial
#                       namespace support. Added better support for XSD restrictions.
# }}}

"""
Utilitites for XML output.
"""

# For usage examples, see bottom of this file.

# imports ================================================================{{{1
import base64
import re

from utils.collectionutil import KeyValue


# constants =============================================================={{{1
declaration = '<?xml version="%s" encoding="%s"?>\n'
indent = 2


# exports ================================================================{{{1
__all__ = ['XMLElement', 'XMLDocument', 'CDATA', 'COMMENT', 'xsd']


# classes ================================================================{{{1

# XMLAttributes ----------------------------------------------------------{{{2
class XMLAttributes(KeyValue):
    """
    This class is a special case of KeyValue, with a format suitable for XML
    attributes.
    """
    def escape(self, s):
        """Escape single and double quotes, since they will spoil the XML."""
        return str(s).replace("'", '&apos;').replace('"', '&quot;')

    def __str__(self):
        return ' '.join(['%s="%s"' % (k, self.escape(v)) for (k, v) in self.iteritems()])


# XMLDocument ------------------------------------------------------------{{{2
class XMLDocument(list):
    """
    For adding an XML header to a list of XMLElements()

    Example:
        x = XMLDocument(xmlElement1(), xmlElement2())

        z = x + XMLDocument([xmlElement1(), xmlElement2(), ...])
        z.encoding = 'iso-8859-1'
    """

    def __init__(self, *a, **k):
        list.__init__(self)
        self.version = k.get('version', "1.0")
        self.encoding = k.get('encoding', "UTF-8")
        self.delim = '\n'
        self(*a)

    def __call__(self, *a):
        for i in a:
            if isinstance(i, (tuple, list)) and not isinstance(i, (XMLDocument, XMLElement)):
                self.extend(i)
            else:
                self.append(i)
        return self

    def __str__(self):
        return declaration % (self.version, self.encoding) + self.delim.join([str(x) for x in self])


# XMLElement -------------------------------------------------------------{{{2
class XMLElement(list):
    """
    This class forms an XML element and can be sub-classed.

    For more examples and hints: see 'test_xml.py'.

    Fields:
       data         list of sub-elements or other content.
       attributes   XMLAttributes object.
       tag          the name of the XML start (and end) tag.
       markup       definition of markup delimiters, default value is:
                    ('<', '>', '</', '/>')
       indent       Indentation level (default 2).

    If no tag name is given, the class name will be used as the element tag
    name.
    """
    # See bottom of file for examples...

    markup = ('<', '>', '</', '/>')

    def __init__(self, tag=None, *a, **na):
        list.__init__(self)
        self.xmlns = None
        self._tag = tag
        self.attributes = XMLAttributes()
        self.indent = indent
        self.parentIndent = 0
        self(*a, **na)

    def _set_tag(self, value):
        self._tag = value

    def _get_tag(self):
        if self.xmlns is None:
            xmlns = ''
        else:
            xmlns = self.xmlns + ":"
        if self._tag is None:
            self._tag = self.__class__.__name__
        return xmlns + self._tag

    tag = property(_get_tag, _set_tag)

    def __call__(self, *a, **na):
        for items in a:
            if isinstance(items, dict):
                self.attributes(items)
            else:
                if isinstance(items, (tuple, list)) and not isinstance(items, XMLElement):
                    self.extend(items)
                else:
                    self.append(items)
        self.attributes(**na)
        return self

    def __contains__(self, key):
        if isinstance(key, int):
            return key in self
        else:
            return key in self.attributes

    def __delitem__(self, key):
        if isinstance(key, int):
            del self[key]
        else:
            del self.attributes[key]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self[key]
        else:
            return self.attributes[key]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self[key] = value
        else:
            self.attributes[key] = value

    def __str__(self):
        """ Here is where the formatting takes place. """
        a = []

        a.append(self.markup[0] + self.tag)

        if self.attributes:
            a.append(str(self.attributes))

        if not self:
            # return empty tag
            a.append(self.markup[3])
            return ' '.join(a)

        S = [' '.join(a) + self.markup[1]]
        prevWasATag = True
        myIndent = self.indent + self.parentIndent
        for obj in self:
            if isinstance(obj, XMLElement):
                obj.addIndent(myIndent)
                if prevWasATag:
                    S.append('\n')
                    S.append(myIndent * ' ')
                prevWasATag = True
            else:
                prevWasATag = False
            S.append(str(obj))
        if prevWasATag:
            S.append('\n')
            S.append(self.parentIndent * ' ')
        S.append(self.markup[2] + self.tag + self.markup[1])
        return ''.join(S)

    def addIndent(self, i):
        self.parentIndent = i

    def copy(self):
        newObj = XMLElement(self.tag, *self[:])
        #newObj.tag = self.tag
        #newObj.data = [self._copy(x) for x in self.data]
        newObj.attributes = self.attributes.copy()
        newObj.indent = self.indent
        newObj.parentIndent = self.parentIndent
        newObj.xmlns = self.xmlns
        return newObj

    #def _copy(self, obj):
    #    """ "Deep" copy. """ 
    #    if hasattr(obj, 'copy'):
    #        return obj.copy()
    #    else:
    #        return obj

    def asSOX(self):
        """Simple Outline XML (Experimental)."""
        def __indent(s):
            rows = s.split('\n')
            delim = '\n' + self.indent * ' '
            if rows[-1] == '':
                return delim.join(rows[:-1])
            else:
                return delim.join(rows)
        S = []
        if self.attributes:
            for k, v in self.attributes.iteritems():
                S.append("\n%s=%s" % (k, v))
        for item in self:
            if hasattr(item, "asSOX"):
                S.append(item.asSOX())
            else:
                S.append(str(item))
        return str(self.tag) + ' '.join(('>', __indent('\n'.join(S))))


# Basic Data Types ======================================================={{{1

# Data type hierarchy ----------------------------------------------------{{{2
# anyType
#     (all complex types)
#     anySimpleType
#         NMTOKENS (*)
#         ENTITIES (*)
#         IDREFS (*)
#         anyAtomicType
#             duration
#             dateTime
#             time
#             date
#             gYear
#             gYearMonth
#             gMonth
#             gMonthDay
#             gDay
#             boolean
#             base64Binary
#             hexBinary
#             anyURL (*)
#             QName (*)
#             NOTATION (*)
#             string
#                 normalizedString
#                     token
#                         NMTOKEN (*)
#                         Name (*)
#                             NCName (*)
#                                 ENTITY (*)
#                                 IDREF (*)
#                                 ID (*)
#                         language (*)
#             float (*)
#             double (*)
#             pDecimal (*)
#             decimal
#                 integer
#                     nonPositiveInteger (*)
#                         negativeInteger (*)
#                     nonNegativeInteger (*)
#                         positiveInteger (*)
#                     unsignedLong (*)
#                         unsignedInt (*)
#                             unsignedShort (*)
#                                 unsignedByte (*)
#                     long (*)
#                         int (*)
#                             short (*)
#                                 byte (*)
#
# (*): Not implemented

# xsd --------------------------------------------------------------------{{{2
class _xsd(XMLElement):
    def __init__(self, *a, **k):
        XMLElement.__init__(self, self.__class__.__name__, *a, **k)
        self.xmlns = xsd.xmlns


class xsd:
    """XML Data Type conversion routines.  This class is just a container to
    make it easier to import conversion functions from other modules.
    Contains some XML formatting classes for XML schemas"""

    xmlns = 'xs'

    class schema(_xsd):
        def __init__(self, *a, **k):
            _xsd.__init__(self, *a, **k)
            self['xmlns:%s' % (xsd.xmlns,)] = 'http://www.w3.org/2001/XMLSchema'

    class all(_xsd): pass
    class annotation(_xsd): pass
    class any(_xsd): pass
    class anyAttribute(_xsd): pass
    class appInfo(_xsd): pass
    class attribute(_xsd): pass
    class attributeGroup(_xsd): pass
    class choice(_xsd): pass
    class complexContent(_xsd): pass
    class complexType(_xsd): pass
    class documentation(_xsd): pass
    class element(_xsd): pass
    class extension(_xsd): pass
    class field(_xsd): pass
    class group(_xsd): pass
    class import_(_xsd): pass
    class include(_xsd): pass
    class key(_xsd): pass
    class keyref(_xsd): pass
    class list(_xsd): pass
    class notation(_xsd): pass
    class redefine(_xsd): pass
    class selector(_xsd): pass
    class sequence(_xsd): pass
    class simpleContent(_xsd): pass
    class simpleType(_xsd): pass
    class union(_xsd): pass
    class unique(_xsd): pass

    class restriction(_xsd):
        """'restriction' has some goodies:
        xsd.simpleType(xsd.restriction(base='xs:string', length=1), name="char")
        <xs:simpleType name="char">
          <xs:restriction base="xs:string">
            <xs:length value="1" />
          </xs:restriction>
        </xs:simpleType>
        """
        def __init__(self, base=None, enumeration=(), fractionDigits=None, length=None, 
                maxExclusive=None, maxInclusive=None, maxLength=None, 
                minExclusive=None, minInclusive=None, minLength=None, 
                pattern=None, totalDigits=None, whiteSpace=None, 
                *a, **k):
            _xsd.__init__(self)
            if not base is None:
                self['base'] = base
            for e in enumeration:
                self.append(XMLElement('%s:enumeration' % xsd.xmlns, value=e))
            for facet in ('fractionDigits', 'length', 'maxExclusive',
                    'maxInclusive', 'maxLength', 'minExclusive',
                    'minInclusive', 'minLength', 'pattern', 'totalDigits', 'whiteSpace'):
                val = locals().get(facet, None)
                if not val is None:
                    self.append(XMLElement('%s:%s' % (xsd.xmlns, facet), value=val))

    # Conversion to XSD data types (not limited to XML Schema)
    @staticmethod
    def base64Binary(value):
        """ Convert Python string to base64. """
        return base64.encodestring(str(value))

    @staticmethod
    def boolean(value):
        """ String representation of Python Boolean value. """
        return ('false', 'true')[value == True]

    @staticmethod
    def char(value, preserve_space=False):
        """ NOTE! This is *NOT* a XML Schema data type. String of length 1. """
        # XSD schema and facet 'whiteSpace' -> 'preserve'
        v = (str(value) + char.default)[0]
        if preserve_space:
            return v
        else:
            return v.replace(' ', char.default)

    @staticmethod
    def date(t, utc=False, tz=None):
        """ AbsTime to ISO 8601 (date) """
        return "%04d-%02d-%02d" % t.split()[:3] + xsd._timezone(utc, tz)

    @staticmethod
    def dateTime(t, utc=False, tz=None, lex24=False):
        """ AbsTime to ISO 8601 (date + time).
            If 'lex24' is True '00:00' is represented as '23:59:59' on previous day.
        """
        from RelTime import RelTime
        from AbsTime import AbsTime
        (y, mo, d, h, mi) = t.split()
        if lex24 and h == 0 and mi == 0 and isinstance(t, AbsTime):
            t2 = t - RelTime(0,1)
            (y, mo, d) = t2.split()[:3]
            h = 23
            mi = 59
            return "%04d-%02d-%02dT%02d:%02d:59" % (y, mo, d, h, mi) + xsd._timezone(utc, tz)
        return "%04d-%02d-%02dT%02d:%02d:00" % (y, mo, d, h, mi) + xsd._timezone(utc, tz)

    @staticmethod
    def decimal(value):
        return str(float(value))

    @staticmethod
    def duration(t):
        """ RelTime to ISO 8601 (duration) """
        if (t.split()[0] < 0 or t.split()[1] < 0):
            return "-PT%dH%dM" % abs(t).split()[:2]
        else:
            return "PT%dH%dM" % t.split()[:2]

    float = staticmethod(decimal)

    @staticmethod
    def gDay(value, utc=False, tz=None):
        """ Convert AbsTime to day-of-month. """
        return "---%02d" % value.split()[2] + xsd._timezone(utc, tz)

    @staticmethod
    def gMonth(value, utc=False, tz=None):
        """ Convert AbsTime to month number. """
        return "--%02d" % value.split()[1] + xsd._timezone(utc, tz)

    @staticmethod
    def gMonthDay(value, utc=False, tz=None):
        """ Convert AbsTime to month number. """
        return "--%02d-%02d" % value.split()[1:3] + xsd._timezone(utc, tz)

    @staticmethod
    def gYear(value, utc=False, tz=None):
        """ Convert AbsTime to year. """
        return "%04d" % value.split()[0] + xsd._timezone(utc, tz)

    @staticmethod
    def gYearMonth(value, utc=False, tz=None):
        """ Convert AbsTime to year + month. """
        return "%04d-%02d" % value.split()[:2] + xsd._timezone(utc, tz)

    @staticmethod
    def hexBinary(value):
        """ Convert integer to hexadecimal. """
        return "%X" % (int(value),)

    @staticmethod
    def integer(value):
        """ Convert str/int to integer. """
        return "%d" % round(float(value))

    int = staticmethod(integer)

    @staticmethod
    def normalizedString(value):
        """ String with no '\t', '\r' and '\n' (for completeness). """
        ws = re.compile(r'[\t\r\n]')
        return escape(''.join(ws.split(value)))

    # XXX: string = staticmethod(str)
    @staticmethod
    def string(value):
        return escape(str(value))

    @staticmethod
    def time(t, utc=False, tz=None):
        """ AbsTime to ISO 8601 (time). tz is a RelTime object """
        return "%02d:%02d:00" % t.split()[3:5] + xsd._timezone(utc, tz) 

    @staticmethod
    def token(value):
        """ Convert string so that consecutive instances of ' ', '\t', '\n' and
        '\r' are converted to a single ' ' (for completeness). """
        ws = re.compile(r'\s+')
        return escape(' '.join(ws.split(value)).strip())

    # private ------------------------------------------------------------{{{3
    @staticmethod
    def _timezone(utc=False, tz=None):
        """ Return 'Z' if UTC else ISO representation of the RelTime 'tz'. """
        if utc:
            return "Z"
        elif tz is None:
            return ""
        elif int(tz) == 0:
            return "Z"
        else:
            return "%+02.2d:%02d" % tz.split()


# anyType / complex / anySimpleType --------------------------------------{{{2
anyType = XMLElement
complex = XMLElement
anySimpleType = XMLElement


# anyAtomicType ----------------------------------------------------------{{{2
class anyAtomicType(XMLElement):
    """ Base class for simple XML element with conversions. """
    default = None

    def __init__(self, tag, value, default=None, use_default=True, *a, **k):
        XMLElement.__init__(self, tag)
        if default is None:
            default = self.default
        if value is None:
            if default is None or not use_default:
                raise TypeError("'%s' is None (void) and no default value was given." % (tag,))
            else:
                if str(default) != "":
                    self.append(default)
        else:
            try:
                s = getattr(xsd, self.__class__.__name__)(value, *a, **k)
            except Exception, t:
                raise TypeError("'%s' - value '%s' cannot be converted to '%s'. Reason: %s." % (tag, value, self.__class__.__name__, t))
            if str(s) != "":
                self.append(s)


# base64Binary -----------------------------------------------------------{{{2
class base64Binary(anyAtomicType):
    """ Convert Python string to base64. """
    default = ''


# boolean ----------------------------------------------------------------{{{2
class boolean(anyAtomicType):
    """ String representation of Python Boolean value. """
    default = 'false'


# char -------------------------------------------------------------------{{{2
class char(anyAtomicType):
    """ Special case (not a XML Schema datatype), for strings of length 1. """
    default = '_'


# date -------------------------------------------------------------------{{{2
class date(anyAtomicType):
    """ Convert AbsTime to ISO date. """
    default = '0001-01-01'


# dateTime ---------------------------------------------------------------{{{2
class dateTime(anyAtomicType):
    """ Convert AbsTime to ISO datetime. """
    default = '0001-01-01T00:00:00'


# decimal ----------------------------------------------------------------{{{2
class decimal(anyAtomicType):
    """ Convert number to decimal. """
    default = '.0'


# duration ---------------------------------------------------------------{{{2
class duration(anyAtomicType):
    """ Convert RelTime to ISO duration. """
    default = 'P0Y'


# float ------------------------------------------------------------------{{{2
# Not working (of course)
#float = decimal


# gDay -------------------------------------------------------------------{{{2
class gDay(anyAtomicType):
    """ Convert AbsTime to day-of-month. """
    default = '---01'


# gMonth -----------------------------------------------------------------{{{2
class gMonth(anyAtomicType):
    """ Convert AbsTime to month number. """
    default = '--01'


# gMonthDay --------------------------------------------------------------{{{2
class gMonthDay(anyAtomicType):
    """ Convert AbsTime to month + day. """
    default = '--01-01'


# gYear ------------------------------------------------------------------{{{2
class gYear(anyAtomicType):
    """ Convert AbsTime to year. """
    default = '0001'


# gYearMonth -------------------------------------------------------------{{{2
class gYearMonth(anyAtomicType):
    """ Convert AbsTime to year + month. """
    default = '0001-01'


# hexBinary --------------------------------------------------------------{{{2
class hexBinary(anyAtomicType):
    """ Convert integer to hexadecimal. """
    default = '0'


# integer ----------------------------------------------------------------{{{2
class integer(anyAtomicType):
    """ Convert str/int to integer. """
    default = '0'


# normalizedString -------------------------------------------------------{{{2
class normalizedString(anyAtomicType):
    """ String with no '\t', '\r' and '\n' (for completeness). """
    default = ''


# string -----------------------------------------------------------------{{{2
class string(anyAtomicType):
    """ Convert to string. """
    default = ''


# time -------------------------------------------------------------------{{{2
class time(anyAtomicType):
    """ Convert AbsTime to ISO time. """
    default = '00:00:00'


# token ------------------------------------------------------------------{{{2
class token(anyAtomicType):
    """ Convert string so that consecutive instances of ' ', '\t', '\n' and
    '\r' are converted to a single ' ' (for completeness). """
    default = ''


# functions =============================================================={{{1

# CDATA ------------------------------------------------------------------{{{2
def CDATA(s):
    """ Return the string 's' in a CDATA block. """
    return "<![CDATA[" + str(s) + "]]>"


# COMMENT ----------------------------------------------------------------{{{2
def COMMENT(s):
    """ Return the string 's' as an XML comment. """
    return "<!-- " + str(s) + " -->"


# escape -----------------------------------------------------------------{{{2
def escape(s):
    """ Escape special characters '&' and '<'. NOTE! This encoding is not smart,
    don't use it to encode passages where e.g. '<![CDATA[...]]>' could
    occur! """
    # [acosta:08/009@11:01] Improvement?: Are there better ways than this?
    if isinstance(s, str):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    else:
        return s

# Some usage examples ===================================================={{{1

# XMLDocument examples ---------------------------------------------------{{{2
# from utils.xmlutil import XMLDocument, XMLElement
#
#   x = XMLElement('tagX', ...)
#   y = XMLElement('tagY', ...)
#   z = XMLElement('tagZ', ...)
#
## Single element:
# print str(XMLDocument(x))
#
## Several elements as many arguments:
# print str(XMLDocument(x, y, z))
#
## Several elements as a list:
# print str(XMLDocument([x, y, z]))
#
## Some of the many possible operations:
# doc = XMLDocument()
# doc.append(x)
# doc.extend([y, z])
# 
# for i in doc:
#     ...
#
# anotherDoc = doc + y + z
#
## ..., etc. XMLDocument is able to do most things a list can do.

# XMLElement examples ----------------------------------------------------{{{2
#    from utils.xmlutil import XMLElement
#    from AbsTime import AbsTime
#
#    class myElement(XMLElement):
#        def __init__(self):
#           XMLElement.__init__(self)
#           self.append(myOtherElement())
#           self['date'] = AbsTime("20060918")
#           self['version'] = "1.2"
#
#    class  myOtherElement(XMLElement):
#        tag = 'otherElementRenamed'
#
## Initialization, some variants:
##   Note: lists and tuples are added to element content, mappings are added
##         to the attributes
#
#    print str(XMLElement('anotherElement', { 'version': "3.5", 'madeBy': "Acosta" }))
#    
#    me = myElement()
#    me['version'] = "1.0"
#
## Using keywords
#    print XMLElement('anotherElement', myOtherElement(), version="3.5", madeBy="Acosta")
#
## Note: with attributes like 'border.width', named arguments cannot be used,
##       do like this instead:
#    x = XMLElement('myElement', {'border.width': 500})
## Or like this:
#    x = XMLElement('myElement')
#    x['border.width'] = 500
#
## Another variant:
#    print XMLElement('outer')(XMLElement('inner')('contents of inner'))

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
