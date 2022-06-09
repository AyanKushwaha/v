
# changelog {{{2
# [acosta:06/209@11:07] Added header
# [acosta:06/328@14:24] Moved CHR and INT to utils.fmt
# }}}

"""
This module handles formatting of ACCI messages.
"""

# For details about the ACCI format see bottom of this file
# For samples see ../tests/cio/test_acci.py

# imports ================================================================{{{1
import crewlists.elements as elements
import crewlists.status as status
import utils.exception

from utils.fmt import CHR, INT
from AbsTime import AbsTime
from crewlists.replybody import Reply, ReplyError


# set up logging ========================================================={{{1
import logging
log = logging.getLogger('cio.acci')


# classes ================================================================{{{1

# ACCI -------------------------------------------------------------------{{{2
class ACCI(list):
    """
    This class takes care of the ACCI-print part of ACCI messages.
        z = cio.acci.ACCI()
        z.append("Line 1")
        z.append(fstr("Formatted line", ("FO1", 0, 0)))
        z.append(fstr("Another Formatted line", ("FO2", 0, 0)))
        z.appendf("Another Formatted line", ("FO2", 0, 0))
        z.append()
        z.append("Prev line was empty")
        z.header(mesno=30, eta=AbsTime("19650110"))
        message = str(z)
    """
    # Comment: if this line is to be removed in the future, change __iter__().
    last_line_text = "End of print."

    def __init__(self, records=(), header=None, end_of_print=True):
        list.__init__(self, records)
        class Dummy:
            requestName = 'CheckInOut'
        self.inparams = Dummy()
        if header is None:
            self.header = ACCIHead()
        else:
            self.header = header
        self.last_line = fstr(self.last_line_text, ("P02", 0, 0))
        self.end_of_print = end_of_print

    def __call__(self, *a, **k):
        self.header(*a, **k)

    @classmethod
    def fromACCIString(cls, acci):
        accistring = str(acci)
        header = ACCIHead.fromACCIString(accistring[:82])
        report = accistring[82:]

        records = []
        lines = []
        formats = {}

        slice = Slice(report)

        # Get number of text lines
        nrOfLines = int(slice(4))
        c = 0
        while c < nrOfLines:
            slen = int(slice(2))
            lines.append(slice(slen))
            c += 1

        # Get number of formatting blocks
        nrOfFLines = int(slice(3))
        c = 0
        while c < nrOfFLines:
            lineNo = int(slice(3))
            format = slice(3)
            startPosition = int(slice(3))
            endPosition = int(slice(3))
            filler = slice(11)
            if lineNo in formats:
                formats[lineNo].append((format, startPosition, endPosition))
            else:
                formats[lineNo] = [(format, startPosition, endPosition)]
            c += 1

        i = 1
        for line in lines:
            if i in formats:
                records.append(fstr(line, *formats[i]))
            else:
                records.append(line)
            i += 1
        return cls(header=header, records=records)

    def __iter__(self):
        # Append 'End of print.' to all messages.
        if self.end_of_print:
            return list.__iter__(self + [self.last_line])
        else:
            return list.__iter__(self)

    def __str__(self):
        """ Prints an ACCI formatted string. (Raw format) """
        # Keep formatting directions in this list
        F = []

        # (1) ACCI header
        S = [str(self.header)]

        # Will add end_of_print if applicable (via __iter__()).
        Z = [x for x in self]

        # (2) indicator of how many print-rows in the message
        S.append("%04d" % len(Z))

        # (3) each print-row with a number indicating the number of characters prepended.
        i = 1
        for l in Z:
            if hasattr(l, 'formats'):
                for f in l.formats:
                    F.append(f.lineformat(i))
            S.append("%02d%s" % (len(str(l)), l))
            i += 1

        # (4) number of formatting rules.
        S.append("%03d" % len(F))

        # (5) each formatting rule
        S.append(''.join(F))
        return ''.join(S)

    def decode(self):
        """ Return a 'decoded' ACCI message (in plain text format). """
        return '\n'.join([str(x) for x in self])

    def asXML(self):
        """ Return an XML-formatted version of the ACCI printout. """
        try:
            return elements.report(self)
        except ReplyError, re:
            log.error(self.header.mesno)
            return str(re)
        except Exception, e:
            log.error(utils.exception.getCause())
            return str(Reply(self.inparams.requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))

    def appendf(self, str, *tup):
        """ Convenience method, to make it easier for callers. """
        self.append(fstr(str, *tup))

    def dump(self):
        """ Some kind of home-brewed formatting. """
        ret = [
            str(self),
            "--- ACCI HEAD BEGIN ---",
            self.header.dump(),
            "--- ACCI HEAD END ---",
            "--- ACCI PRINT BEGIN ---",
        ]
        c = 1
        for l in self:
            if hasattr(l, 'formats'):
                for (f, s, e) in l.formats:
                    if e == 0:
                        e = len(l)
                    if s != 0:
                        s = s - 1
                    x = l[:s] + "[" + l[s:e] + "]" + l[e:]
                    ret.append("%05d %3s %s" % (c, f, x))
            else:
                ret.append("%05d %3s %s" % (c, '', l))
            c += 1
        ret.append("--- ACCI PRINT END ---")
        return '\n'.join(ret)

    def ok(self):
        """ Signal that everything went ok. """
        return int(self.header.mesno) == 0


# ACCIHead ---------------------------------------------------------------{{{2
class ACCIHead:
    """ Header part of ACCI message. """
    headers = ( 'mesno', 'submesno', 'cico', 'dutycd', 'activityid', 'udor',
            'adep', 'std', 'sta', 'eta', 'perkey', 'look_for_ht', 'fli_info',
            'cli_info', 'rev_info', 'htl_info_after_line',)

    def __init__(self, mesno=None, submesno=None, cico=None, dutycd=None, activityid=None,
            udor=None, adep=None, std=None, sta=None, eta=None, perkey=None,
            look_for_ht=False, fli_info=False, cli_info=False, rev_info=False,
            htl_info_after_line=None):
        self.mesno = mesno
        if submesno is None:
            self.submesno = mesno
        self.cico = cico
        self.dutycd = dutycd
        self.activityid = activityid
        self.udor = udor
        self.adep = adep
        self.std = std
        self.sta = sta
        self.eta = eta
        self.perkey = perkey
        self.look_for_ht = look_for_ht
        self.fli_info = fli_info
        self.cli_info = cli_info
        self.rev_info = rev_info
        self.htl_info_after_line = htl_info_after_line

    def __call__(self, **map):
        for key, value in map.iteritems():
            if key == "mesno":
                self.submesno = value
            setattr(self, key, value)

    @classmethod
    def fromACCIString(cls, ah):
        """ Read ACCI String to recreate header. """
        def __ACCIStringToAbsTime(s):
            if s == 12 * '0':
                return None # AbsTime leaks memory, if faulty date...
            try:
                return AbsTime(int(s[:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]), int(s[10:12]))
            except:
                return None

        s = str(ah)
        return cls(
            mesno=s[:3],
            submesno=s[3:6],
            cico=s[6:7],
            dutycd=s[7:10],
            activityid=s[10:18],
            udor=__ACCIStringToAbsTime(s[18:26] + "0000"),
            adep=s[26:29],
            std=__ACCIStringToAbsTime(s[29:41]),
            sta=__ACCIStringToAbsTime(s[41:53]),
            eta=__ACCIStringToAbsTime(s[53:65]),
            perkey=s[65:74],
            look_for_ht=s[74:75],
            fli_info=s[75:76],
            cli_info=s[76:77],
            rev_info=s[77:78],
            htl_info_after_line=s[78:82])
    
    def fmt(self, h):
        """ To make printouts nicer looking. """
        return '-'.join(h.upper().split('_'))
       
    def dump(self):
        return '\n'.join(["%20s : %s" % (self.fmt(h), getattr(self, h)) for h in self.headers])

    def __str__(self):
        """ Takes care of the formatting of the heading part of an ACCI
        message. """
        def __AbsTimeToTuple(t):
            if t is None:
                return (0, 0, 0, 0, 0)
            else:
                return t.split()
        return ''.join((
            INT(3, self.mesno),
            INT(3, self.submesno),
            CHR(1, self.cico),
            CHR(3, self.dutycd),
            CHR(8, self.activityid),
            CHR(8, "%04d%02d%02d" % __AbsTimeToTuple(self.udor)[:3]),
            CHR(3, self.adep),
            CHR(12, "%04d%02d%02d%02d%02d" % __AbsTimeToTuple(self.std)[:5]),
            CHR(12, "%04d%02d%02d%02d%02d" % __AbsTimeToTuple(self.sta)[:5]),
            CHR(12, "%04d%02d%02d%02d%02d" % __AbsTimeToTuple(self.eta)[:5]),
            CHR(9, self.perkey),
            CHR(1, ('N', 'Y')[self.look_for_ht == True]),
            CHR(1, ('N', 'Y')[self.fli_info == True]),
            CHR(1, ('N', 'Y')[self.cli_info == True]),
            CHR(1, ('N', 'Y')[self.rev_info == True]),
            INT(4, self.htl_info_after_line),
        ))


# fstr -------------------------------------------------------------------{{{2
class fstr(str):
    """
    Keep text and formatting statements together.

    formats (public list): [ftuple, ...]
        ftuple: (code, start, end)
    """
    def __new__(cls, line='', *formats):
        return str.__new__(cls, line)

    def __init__(self, line='', *formats):
        str.__init__(self, line='')
        self.formats = [ftuple(f) for f in formats]


# ftuple -----------------------------------------------------------------{{{2
class ftuple(tuple):
    """Tuple with three values, 'code', 'start' and 'end'. The values are
    formatting statements. (See cio.run for examples).  'ftuple' will also have
    attributes 'code', 'start' and 'end."""
    def __new__(cls, f):
        """Has to use __new__ since tuples are immutable."""
        return tuple.__new__(cls, f)

    def __init__(self, f):
        """Set attributes, and do basic validity check."""
        if len(f) != 3:
            raise ValueError("usage: ftuple('code', start, end)")
        self.code, self.start, self.end = f

    def __str__(self):
        """Return string formatted for ACCI."""
        return "%3s%03d%03d" % self + 11 * ' '

    def lineformat(self, i):
        """To get complete formatting statement, the linenumber has to be there
        too, as caller use 'x.lineformat(lineno)'."""
        return "%03d" % i + str(self)


# Slice ------------------------------------------------------------------{{{2
class Slice:
    """Get slice of a string, one bit at the time, keep rest."""
    def __init__(self, s):
        self.string = str(s)
        self.pos = 0

    def __call__(self, n):
        self.pos += n
        return self.string[self.pos - n:self.pos]


# functions =============================================================={{{1

# accidump ---------------------------------------------------------------{{{2
def accidump(x):
    """To test ACCI class.  Decodes ACCI-formatted string."""
    try:
        print x.dump()
    except Exception, e:
        log.error("The string '%s' does not conform to the ACCI specification.\n%s" % (x, e))
        raise


# decode -----------------------------------------------------------------{{{2
def decode(x):
    """Decode ACCI message, returns un-formatted ACCI message one row per
    record."""
    try:
        return ACCI.fromACCIString(x).decode()
    except Exception, e:
        log.error("The string '%s' does not conform to the ACCI specification.\n%s" % (x, e))
        raise


# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-in Self Test. """
    import tests.cio.test_acci
    tests.cio.test_acci.main()


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run BIT """
    bit()


# Specification of ACCI message =========================================={{{1

# ACCI - text message format for checkin/checkout events
#=============================================================================
# MESNO               INT(3)   Message number: Return code
#                              {       0 => 'success', 
#                                001-100 => 'info|warning', 
#                                100-899 => 'transaction error', 
#                                900-999 => 'system error' }
# SUBMESNO            INT(3)   Always equal to MESNO
# CICOINDIC           CHR(1)   Indicator:
#                              { '0' => 'No CI/CO performed',
#                                '1' => 'CI performed', 
#                                '2' => 'CO performed',
#                                '3' => 'CO/CI performed' }
# DUTYCD              CHR(3)   CO only: Duty Code on flight (which crew is checking out from)
# ACTIVITYID          CHR(8)   CO only: Flight number (of flight which crew is checking out from)
# ORIGSDT-UTC         INT(8)   CO only: Scheduled date of origin (-"-)
# STNFR               CHR(3)   CO only: Departure station (-"-)
# STDDAT              INT(8)   CO only: Scheduled date of departure (-"-)
# STD                 INT(4)   CO only: Scheduled time of departure (-"-)
# STADAT              INT(8)   CO only: Scheduled date of arrival (-"-)
# STA                 INT(4)   CO only: Scheduled time of arrival (-"-)
# ETADAT              INT(8)   CO only: Estimated date of arrival (-"-)
# ETA                 INT(4)   CO only: Estimated time of arrival (-"-)
# PERKEY              CHR(9)   CO only: Crew PERKEY
# LOOK-FOR-HT         CHR(1)   NOT USED: Look for hotel ('Y' if CO-MANDATORY, else 'N')
# FLI-INFO-INDIC      CHR(1)   CI only: (Special info exists) ? 'Y' : 'N'
# CLI-INFO-INDIC      CHR(1)   CI only: (Crew list exists) ? 'Y' : 'N'
# REV-INFO-INDIC      CHR(1)   CI only: (Revisions exist) ? 'Y' : 'N'
# HTL-INFO-AFTER-LINE INT(4)   Indicates where hotel info is placed in print
#-----------------------------------------------------------------------------
# NO-LINES-IN-PRINT   INT(4)   Number of print lines to be displayed and formatted
# ACCI-PRINT          CHAR(30000)
#=============================================================================
#
# ACCI-PRINT = (NO-LINES-IN-PRINT * ACCI-PRINT-LINE) + ACCI-FORMAT-LINES
#
# ACCI-PRINT-LINE
#=============================================================================
# Contains:
#  * General messages
#  * Office or private information
#  * Revisions to schedule
#  * Crew List
#  * Special information (flight info)
#  * XXX COQS info (removed)
#  * Delay information
#  * License expiration information
#=============================================================================
# LineIdx     INT(2)        Number of characters on this line 
# printLine   CHAR(lineIdx) CI/CO information formatted with ACCI-FORMAT-LINES
#=============================================================================
#
# ACCI-FORMAT-LINES = ACCI-FORMAT-LINES-HEADER + (FormatLineIdx * ACCI-FORMAT-LINE)
#
# ACCI-FORMAT-LINES-HEADER
#=============================================================================
# FormatLineIdx  INT(3)               Number of format line blocks
# LineFormat     ARRAY(FormatLineIdx) List of formatting directives
#=============================================================================
#
# ACCI-FORMAT-LINE
#=============================================================================
# lineNo         INT(3)        Line number
# format         CHR(3)        Formatting to be applied to line number lineNo
# startPosition  INT(3)        Start position of formatting
# endPosition    INT(3)        End position of formatting
# filler         CHR(11)       Empty space
#=============================================================================

# modeline ==============================================================={{{1
# vim: set fdm=marker:
