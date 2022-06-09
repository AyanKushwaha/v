"""
Collection of small functions that don't fit elsewhere.

!!! WARNING !!!
! Do not introduce any functions or modules that are dependent on Studio (e.g.
! Cui).  Place these functions in carmusr.HelperFunctions instead!  We want to
! be able to use this module from many different places, including such places
! where we don't want to use Studio.
! Time-related functions should be in utils.time_util (which imports AbsTime)
"""

# Don't import anything else than standard Python modules here!
import os
import re
import tempfile


__all__ = ['fd_parser', 'simple_urlparser', 'is_base_activity', 'i2rm', 'rm2i', 'AtomicFile']


# classes ================================================================{{{1

# SimpleURLParser --------------------------------------------------------{{{2
class SimpleURLParser:
    """ See simple_urlparser. """
    def __init__(self, url):
        self.scheme = ''
        self.netloc = ''
        self.path = ''
        self.params = ''
        self.query = ''
        self.fragment = ''
        self.username = None
        self.password = None
        self.hostname = None
        self.port = None
        self.url = url
        self.parse()

    def toTuple(self):
        """ Return a tuple, that also has fields. """
        class SimpleURL(tuple):
            """ URL Container """
            pass
        u = SimpleURL((self.scheme, self.netloc, self.path, self.params, self.query, self.fragment))
        u.__dict__ = self.__dict__
        return u

    def __str__(self):
        """ for basic tests """
        return '\n'.join((
            '---',
            'url : (%s)' % (self.url,), 
            ' netloc   : (%s)' % (self.netloc,),
            '   username : %s' % (self.username,),
            '   password : %s' % (self.password,),
            '   hostname : %s' % (self.hostname,),
            '   port     : %s' % (self.port,),
            ' path     : %s' % (self.path,),
            ' params   : %s' % (self.params,),
            ' query    : %s' % (self.query,),
            ' fragment : %s' % (self.fragment,),
        ))

    def __repr__(self):
        """ for basic tests """
        return repr((
            self.scheme, 
            (self.username, self.password, self.hostname, self.port), 
            self.path, 
            self.params, 
            self.query, 
            self.fragment
        ))

    def parse(self):
        """ scheme://netloc/path;parameters?query#fragment """
        # everything could have been done with a giant regexp, but...
        # ... first split out scheme, netloc and path
        regexp = re.compile(r'^([^:]+:)?(//[^/]*)?(/[^;]*)?(;[^?]*)?(\?[^\#]*)?(\#.*)?$')
        m = regexp.match(self.url)
        if m:
            (scheme, netloc, path, params, query, fragment) = m.groups()
            if not scheme is None:
                self.scheme = scheme[:-1]
            if not netloc is None:
                self.netloc = netloc[2:]
            if not path is None:
                self.path = path[1:]
            if not params is None:
                self.params = params[1:]
            if not query is None:
                self.query = query[1:]
            if not fragment is None:
                self.fragment = fragment[1:]
        else:
            raise ValueError('Malformed url %s' % (self.url,))
        if self.netloc:
            # ... then split up the host/ip-address component
            regexp = re.compile(r'^(([^:]+)(:[^@]+)?@)?([^:]+)(:[0-9]+)?$')
            m = regexp.match(self.netloc)
            if m:
                (userpass, username, password, hostname, port) = m.groups()
                if not username is None:
                    self.username = username
                if not password is None:
                    self.password = password[1:]
                self.hostname = hostname
                if not port is None:
                    self.port = int(port[1:])
            else:
                raise ValueError('Malformed netloc %s' % (self.netloc,))


# fd_parser =============================================================={{{1
class fd_parser(tuple):
    """
    fd is a flight designator in "free" format.

    Return a tuple -> (carrier, number, suffix)
    The tuple also has the following fields:

        x.carrier
        x.number
        x.suffix
        x.flight_name
        x.flight_id
        x.flight_descriptor

    Example:
        f = fd_parser("SK   434")
        f -> ("SK", 434, "")
        f.carrier -> "SK"
        f.number -> 434
        f.suffix -> ""
        f.flight_name -> "434"
        f.flight_id -> "SK 0434 "
        f.flight_descriptor -> "SK 000434 "
    """

    # NOTE: not possible with two digits first!
    #flight_re = re.compile(r'^\s*(([A-Z0-9][A-Z0-9][A-Z]?)\s*(\d{3,})\s*([A-Z]?)\s*$')
    flight_re = re.compile(r'^\s*(([A-Z][A-Z0-9][A-Z]?|[A-Z0-9][A-Z]{1,2})[ ]*)?(\d+)([A-Z]?)\s*$')
    own_carrier = "SK"

    def __new__(cls, f):
        """
        IATA allows a number of different notations:
           "SK 0424 ", "SK424", "SK  424 "

        flight_leg always uses 6 digits:
           "SK 000424 "

        The parser also allows e.g. 943 which is interpreted as SK943
        """
        m = cls.flight_re.match(f.upper())
        if m:
            (_ ,carrier, number, suffix) = m.groups()
            if carrier is None:
                carrier = cls.own_carrier
            number = int(number)
        else:
            raise ValueError('Malformed flightdesignator "%s".' % (f,))
        return tuple.__new__(cls, (carrier, number, suffix))

    def __init__(self, f):
        self.fd = f
        self.carrier, self.number, self.suffix = self 

    def __str__(self):
        return self.flight_id

    @property
    def flight_descriptor(self):
        """
        Reformat for use with UDM tables.
            Carrier: three positions, 
            Number: six positions, 
            Suffix: one position.
        CCC999999S
        """
        return "%-3.3s%-06.6d%1.1s" % (self.carrier, self.number, self.suffix)

    @property
    def flight_id(self):
        """
        Reformat for use within SAS.
            Carrier: three positions, 
            Number: four positions, 
            Suffix: one position.
        CCC9999S
        """
        return "%-3.3s%-04.4d%1.1s" % (self.carrier, self.number, self.suffix)

    @property
    def flight_name(self):
        """
        Reformat for use within SAS (unofficial use).
            Carrier: own carrier omitted,
            Number: four positions, 
            Suffix: one position.
        (CCC)999(9)(S)
        """
        if self.carrier == self.__class__.own_carrier:
            carrier = ""
        else:
            carrier = self.carrier
        return "%s%-03.3d%s" % (carrier, self.number, self.suffix)


# is_base_activity ======================================================={{{1
def is_base_activity(a):
    """ 
    Test if argument is a base activity. One or two letters followed by up to
    two digits and maybe a one letter suffix.
    """
    flight_re = re.compile(r'^([A-Z0-9]{2}[A-Z\s]?)?\d{3,6}[A-Z\s]?$')
    return not flight_re.match(a)


# simple_urlparser ======================================================={{{1
def simple_urlparser(url):
    """
    Simple variant of URL parser.
    Tries to simulate urlparser.urlparser in Python 2.5

    NOTE: Can be removed when upgrading to Python 2.5
    """
    return SimpleURLParser(url).toTuple()


# default ================================================================{{{1
def default(arg1, arg2=''):
    """Replace 'None' variables with a default value."""
    if arg1 is None:
        return arg2
    else:
        return arg1


# base2station -----------------------------------------------------------{{{1
def base2station(base):
    """
    Convert base to an airport (station). This function makes some assumptions
    and is far from complete, but it should do the job.
    The bases 'CPH', 'OSL', 'SVG', 'TRD' have airports with same codes.
    """
    return {
        'STO': 'ARN', # Stockholm -> Stockholm-Arlanda
        'TYO': 'NRT', # Tokyo -> Narita International
        'BJS': 'PEK', # Beijing -> Beijing Capital
        'SHA': 'PVG', # Shanghai -> Shanghai Pudong International
    }.get(base, base)


# Yes / No conversions ==================================================={{{1
#------------------------------------------------------------------------------
# Functions to evaluate different variants of specifying Yes or No from
# Studio menu entries. Possible values include e.g. True/None/"Yes"/"FALSE"/0.
#------------------------------------------------------------------------------

# isYes ------------------------------------------------------------------{{{2
def isYes(variationsOfYesOrNo):
    return str(variationsOfYesOrNo).upper() not in (
            "NONE", "NO", "N", "F", "FALSE", "0")


# isNo -------------------------------------------------------------------{{{2
def isNo(variationsOfYesOrNo):
    return not isYes(variationsOfYesOrNo)


# yesOrNo ----------------------------------------------------------------{{{2
def yesOrNo(variationsOfYesOrNo):
    return ("No","Yes")[isYes(variationsOfYesOrNo)]


# yesOrNoInverse ---------------------------------------------------------{{{2
def yesOrNoInverse(variationsOfYesOrNo):
    return ("Yes","No")[isYes(variationsOfYesOrNo)]
   


# fmt_list ==============================================================={{{1
def fmt_list(s, width=72):
    """Convert a (long) string to a list of lines, where no line is longer
    than width."""
    R = []
    while len(s) > width:
        bp = s.rfind(' ', 0, width)
        if bp == -1:
            # No space found, split word (could be done in a nicer fashion,
            # but how often do you find words that are that long???
            R.append(s[:width-1] + '-')
            s = s[width-1:]
        else:
            R.append(s[:bp])
            s = s[bp+1:]
    R.append(s)
    return R


# roman numerals ========================================================={{{1
_rm = (
    ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400), ('C', 100), ('XC', 90),
    ('L', 50), ('XL', 40), ('X', 10), ('IX', 9), ('V', 5), ('IV', 4), ('I', 1),
)


def i2rm(i):
    """Convert integer to roman numerals."""
    L = []
    for r, num in _rm:
        while i >= num:
            L.append(r)
            i -= num
    return ''.join(L)


def rm2i(r):
    """Convert roman numeral to integer."""
    num = 0
    drm = dict(_rm)
    R = r.upper()
    x = 0
    while x < len(R):
        try:
            # XC, IX etc, try using a couple
            num += drm.get(R[x:x+2])
            x += 1
        except:
            num += drm.get(R[x])
        x += 1
    return num


# AtomicFile ============================================================={{{1
class AtomicFile(file):
    """A subclass of file that will only appear in the file system when closed.

    The class can be useful when you have a process that scans a spool
    directory for files, and starts to read new files upon appearance.

    What could happen is that reading process starts to read the file before
    the writing process has finished its job, resulting in only parts of the
    file being read.
    
    To protect from this use 'AtomicFile' which make the file appear in the
    spool directory as an atomic operation, the functionality is based on the
    'os.rename()' operation which is atomic.

    There is one caveat, the mandatory argument 'dir' must:
      (1) exist and be on the SAME filesystem as 'filename'
      (2) the directory should NOT be the same directory as 'filename', or
          the whole point of this class is lost, a reading process could by
          mistake read the temporary file...

    Usage example ('/var/spool' and '/var/tmp' are on the same file system):
    > af = AtomicFile('/var/spool/spoolfile.dat', '/var/tmp')
    > print >>af, "Hello World!"
    > af.close()
    """
    def __init__(self, filename, dir, mode='w+b', suffix='', prefix='tmp'):
        """Make this file object an instance of 'file' with a temporary
        filename, 'dir' has to be a directory on the same filesystem, but not
        the same directory as 'filename'."""
        self.filename = filename
        if os.path.samefile(os.path.dirname(os.path.abspath(filename)), dir):
            raise ValueError("the directory of 'filename' must not be the same as 'dir'")
        self.__tmp_fn = tempfile.mktemp(suffix=suffix, prefix=prefix, dir=dir)
        file.__init__(self, self.__tmp_fn, mode)

    def close(self):
        """Close temporary file and rename the temporary file to 'filename'."""
        file.close(self)
        os.rename(self.__tmp_fn, self.filename)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof



def fd_pre_parse_sanitize(flight_nr):
    "prevents fd_parser from crashing for certain flight-numbers"
    lookup = {
        "-00001"   : "A000",
        "TAX-00001": "TAX0000",
        "LIM-00001": "LIM0000",
        "BUS-00001": "BUS0000",
        "BOA-00001": "BOA0000",
    }
    if flight_nr.strip() in lookup.keys():
        print "   flight nr pre-parse: '%s'" % flight_nr
        _flight_nr = lookup.get(flight_nr.strip())
        print "   flight nr sanitized: '%s'" % _flight_nr
        return _flight_nr
    return flight_nr



def fd_post_parse_prettify(flight_nr):
    """makes stange-looking flight-numbers more understandable"""
    lookup = {
        "A0 0000" : "airport standby",
        "TAX 0000": "taxi transport",
        "LIM 0000": "limo transport",
        "BUS 0000": "bus transport",
        "BOA 0000": "boat transport",
    }
    if flight_nr in lookup.keys():
        print "   flight nr post-parse: '%s'" % flight_nr
        _flight_nr = lookup.get(flight_nr)
        print "   flight nr prettyfied: '%s'" % _flight_nr
        return _flight_nr
    return flight_nr


