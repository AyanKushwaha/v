
# changelog {{{2
# [acosta:06/229@10:30] First version.
# [acosta:07/089@08:52] Moved actual report code into this script.
# [acosta:07/129@14:17] Renamed and moved.
# }}}

"""
Create list of number of crew on a given flight.

The output format is specified in:

41. PAH, Number of Crew (to Load Sheet), integration.

The report is time triggered.

The information is sent to the PAH system three times before departure:

1. 180 min before STD,
2.  60 min before STD, and,
3.  22 min before STD.

"""

# For specification of the output format, see below.

# imports ================================================================{{{1
import re

import carmensystems.rave.api as rave

import crewlists.status as status
from crewlists.crewmessage import Message, MessageError
from utils.xmlutil import XMLElement
from utils.selctx import FlightFilter
import time
import datetime


# constants =============================================================={{{1
report_name = 'crewToLoadsheet'

# each leg info will be ended by an empty serviceclass message (see below).
EMPTY_SC = '0 00 00 00 00 00'
#            12345
EMPTY_LEG = '     0000'
EMPTY_LEG_EMPTY_SC = EMPTY_LEG + EMPTY_SC
TRCODE = 'AHCRU1  '


# XML formatting classes ================================================={{{1

# crewToLoadsheet --------------------------------------------------------{{{2
class crewToLoadsheet(XMLElement):
    """
    This element contains a number of 'crewLoadsheetMsg' elements.
    Each of these contain a row in the old PAH format.
    """
    def __init__(self, flight, date, adep):
        XMLElement.__init__(self)
        self['version'] = status.schema_version

        ff = FlightFilter.fromComponents(flight, date, adep, includeSuffix=True, onlyOperatedBySAS=True)
        legs_expr = rave.foreach(
                rave.iter('iterators.flight_leg_set',
                    where=ff.asTuple()),
            'report_crewlists.%leg_flight_id%',
            'report_crewlists.%leg_udor%',
            'report_crewlists.%leg_adep%',
            'report_crewlists.%leg_ades%',
            'report_crewlists.%num_fc%',
            'report_crewlists.%num_cc_incl_ferryflight%',
        )
        legs, = rave.eval(ff.context(), legs_expr)

        if len(legs) < 1:
            print "%s %s" % (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                  MessageError(report_name, status.CREW_NOT_FOUND, "No crew found on flight %s." % (ff.flight,)))
            return

        leg_info = []
        for (ix, fd, udor, stnfr, stnto, nfc, ncc) in legs:
            leg_info.append("%-5s%02d%02d%s" % (stnto, ncc, nfc, EMPTY_SC))
            leg_info.append(''.join([EMPTY_LEG_EMPTY_SC for zz in xrange(14)]))
            message = ''.join(
                [
                    "%s" % (fd),
                    "%04d%02d%02d" % udor.split()[:3],
                    "%-5s" % stnfr,
                    "%02d" % 1, # num legs
                    ''.join(leg_info),
                ])
            self.append(XMLElement('crewLoadsheetMsg', message))


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(flightId=None, originDate=None, adep=None):
    """
    Returns the whole report as a long string with embedded newlines.
    Flight is carrier(3) + flighno(4) + suffix(1), 8 characters. Ex: 'SK 0193 '
    UDOR is in format YYYYMMDD.
    """
    try:
        a1 = crewToLoadsheet(flightId, originDate, adep)
        a = str(a1)
        b = 'crewLoadsheetMsg'
        if b in a:
               return str(Message(report_name, a1))
        else:
               return
    except:
        # Don't send faulty messages
        raise


# bit --------------------------------------------------------------------{{{2
def bit(*c):
    """
    Built-In Test. Run the report. Print the raw output and "cooked" output.
    """
    r = report(*c)
    print "*** BEGIN REPORT ***"
    print r
    print "*** END REPORT ***"

    s = None
    from xml.dom.minidom import parseString
    dom = parseString(r)
    for cm in dom.getElementsByTagName('crewMessage'):
        for mb in cm.getElementsByTagName('messageBody'):
            print "mb", mb
            for ctl in mb.getElementsByTagName('crewToLoadsheet'):
                print "ctl", ctl
                for clm in ctl.getElementsByTagName('crewLoadsheetMsg'):
                    s = clm.childNodes[0].data
                    print s
                    break
                break
            break
        break
    if s is None:
        raise Exception("Could not parse XML (fault in test program, not necessarily in report).")
    print "*** BEGIN DATA ***"
    print s
    print "*** END DATA ***"

    print "*** START DUMP ***"
    for line in s.split('\n'):
        rest = line[8:]
        print "--- record ---"
        print "Flight          :", rest[:8]
        rest = rest[8:]
        print "UDOR            :", rest[:8]
        rest = rest[8:]
        print "ADEP            :", rest[:5]
        rest = rest[5:]
        (nol, rest) = (rest[:2], rest[2:])
        print "Nr of legs      :", nol
        try:
            for x in xrange(int(nol)):
                (stnto, rest) = (rest[:5], rest[5:])
                (cc, rest) = (int(rest[:2]), rest[2:])
                (fc, rest) = (int(rest[:2]), rest[2:])
                (svcinfo, rest) = (rest[:16], rest[16:])
                print "Arrival station :", stnto
                print "    CC          :", cc
                print "    FC          :", fc
                print "    SVC         :", svcinfo
        except:
            pass
    print "*** END DUMP ***"


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """
    import sys
    bit(sys.argv[1:])


# format specification ==================================================={{{1
# General:
# header{1} leginfo{15} serviceclassinfo{5}
#
# header:
# FLTNOX        CHR(8)     Flight carrier + Flight number + Flight code
#                          Ex: 'SK 0903 '
# FLTDT         INT(8)     Flight date origin UTC, YYYYMMDD (UDOR)
# STNCDON       CHR(5)     Departure statiaon (IATA, ADEP)
# NBRSTNCDOFF   INT(2)     Number of arrival stations, 01-15 (legs)
#
# leginfo, the message always contains 15 occurrences:
# STNCDOFF      CHR(5)     Arrival station (IATA)
# CACREWTTLA    INT(2)     Total number of active cabin crew.
# COCREWTTLA    INT(2)     Total number of active flight deck crew.
# NBRDHCCLASS   INT(1)     Number of service classes with deadheaded crew,
#                          0-5. *NOT USED*
#
# serviceclassinfo the message always contains 5 (empty) occurrences:
# SERVCL        CHR(1)     Service class. *NOT USED*
# NBRDHC        INT(2)     Number of deadheaded crew. *NOT USED*
#
# NB, since these are empty, each leg info is always ended by:
# NBRDHCCLASS + 5 * (SERVCL + NBRDHC) i.e. '0 00 00 00 00 00'


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
