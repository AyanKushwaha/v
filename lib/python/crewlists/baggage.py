
# {{{ Log
# [acosta:07/023@13:34] First version.
# [acosta:07/257@13:08] New version for ReportServer V2.
# }}}

"""
This report creates a Crew Baggage Reconciliation message.
The interface is described in:
    40.1 Crew Baggage Reconciliation

This report has a different XML root element than i.e. CrewList
"""

# NOTE: The format is described at the end of this file.

# imports ================================================================{{{1
import crewlists.status as status
import utils.edifact as edifact

from AbsTime import AbsTime
from tm import TM
from utils.fmt import CHR, INT
from utils.rave import RaveIterator
from utils.xmlutil import XMLElement
from crewlists.crewmessage import Message, MessageError
from utils.divtools import fd_parser
from utils.selctx import FlightFilter


# exports ================================================================{{{1
__all__ = ['reports']


# constants =============================================================={{{1
report_name = 'CrewBaggageReconciliation'
maxRecords = 9


# RaveIterator classes ==================================================={{{1

# CrewIterator -----------------------------------------------------------{{{2
class CrewIterator(RaveIterator):
    """ Crew info for a leg. """
    def __init__(self, fdes):
        # 'fdes' is an 'FlightDesignator' instance.
        fields = {
            'crewid': 'report_crewlists.%crew_id%',
            'titlerank': 'report_crewlists.%%crew_title_rank%%(%s)' % fdes.udor,
            'extperkey': 'report_crewlists.%crew_empno%',
            'sn': 'report_crewlists.%crew_sn%',
            'gn': 'report_crewlists.%crew_gn%',
            'first_in_duty': 'report_crewlists.%flight_is_first_in_duty%',
        }
        self.ff = FlightFilter(fdes)
        iterator = RaveIterator.iter('iterators.leg_set', where=self.ff.asTuple())
        RaveIterator.__init__(self, iterator, fields)

    def eval(self):
        return RaveIterator.eval(self, self.ff.context())


# LegIterator ------------------------------------------------------------{{{2
class LegIterator(RaveIterator):
    """ Flight info for a leg. """
    def __init__(self, fdes):
        fields = {
            'flightid': 'report_crewlists.%leg_flight_id%',
            'udor': 'report_crewlists.%leg_udor%',
            'ldor': 'report_crewlists.%leg_ldor%',
            'stnfr': 'report_crewlists.%leg_adep%',
            'stnto': 'report_crewlists.%leg_ades%',
            'passive': 'report_crewlists.%leg_is_deadhead%',
        }
        where_expr = (
            'report_crewlists.%%leg_is_flight%% and report_crewlists.%%leg_start_utc%% < %s + 24:00' % (fdes.udor),
            'report_crewlists.%%leg_start_utc%% > %s' % (fdes.udor),
        )
        iterator = RaveIterator.iter('iterators.leg_set', where=where_expr)
        RaveIterator.__init__(self, iterator, fields)


# TripIterator -----------------------------------------------------------{{{2
class TripIterator(RaveIterator):
    """ Trips for a crew """
    def __init__(self, fdes):
        where_expr = (
            'report_crewlists.%%trip_start_utc%% < %s + 24:00' % (fdes.udor),
            'report_crewlists.%%trip_end_utc%% > %s' % (fdes.udor),
        )
        iterator = RaveIterator.iter('iterators.trip_set', where=where_expr)
        RaveIterator.__init__(self, iterator)


# XML formatting classes ================================================={{{1

# baggageReconciliation -------------------------------------------------{{{2
class baggageReconciliation(XMLElement):
    """
    Add one 'CrewBaggageRecord' for the specific crew.
    """
    def __init__(self, fdes, crew):
        # 'fdes' is a 'FlightDesignator' object
        XMLElement.__init__(self)
        self['version'] = "1.8"
        self.append(XMLElement('crewBaggageInfo', CrewBaggageRecord(fdes, crew)))


# mainframe formatting classes ==========================================={{{1

# BaggageRecord ----------------------------------------------------------{{{2
class BaggageRecord:
    """ Base class """
    def __init__(self):
        """ reset counters """
        self.records = 0
        self.msg = ''

    def __len__(self):
        """ return number of legs """
        return self.records

    def __str__(self):
        """ return record """
        return str(self.msg)

    def emptyRecord(self, nr=1):
        """ Return an empty record or a string composed of 'nr' records. """
        empty = '   0000 ' + 21 * ' '
        # from 1 to 9 is allowed
        # note that -2 * 'x' returns '' as wanted.
        return min(maxRecords, nr) * empty


# NewBaggageRecord -------------------------------------------------------{{{2
class NewBaggageRecord(BaggageRecord):
    """ Use crew iterator to produce a baggage record. """
    def __init__(self, fdes, crew):
        BaggageRecord.__init__(self)
        L = []
        for trip in crew.chain('trip'):
            legs = trip.chain('leg')
            for leg in legs:
                if self.records >= maxRecords:
                    break
                L.append(self.record(leg))
                self.records += 1
            # Fill with empty records
            L.append(self.emptyRecord(maxRecords - self.records))
            # Only one trip allowed
            break
        self.msg = ''.join(L)

    def date2str(self, A):
        """ Convert from AbsTime to ddbbbyy. """
        # AbsTime is 'ddbbbyyyy HH:MM'
        a = str(A)
        return a[:5] + a[7:9]

    def record(self, L):
        """ Return a record for a given leg. """
        fd = fd_parser(L.flightid)
        flightid = "%-3.3s%1.1s%-04.4d" % (fd.carrier,fd.suffix,fd.number)
        return ''.join([
            CHR(8, flightid),
            CHR(7, self.date2str(L.udor)),
            CHR(7, self.date2str(L.ldor)),
            CHR(3, L.stnfr),
            CHR(3, L.stnto),
            ('A', 'P')[L.passive],
        ])


# OldBaggageRecord -------------------------------------------------------{{{2
class OldBaggageRecord(BaggageRecord):
    """ Search data base for last recorded message. """
    def __init__(self, fdes, crew):
        """ Find old record or create new empty one. """
        BaggageRecord.__init__(self)
        self.fdes = fdes
        extperkey = crew.extperkey
        try:
            self.rec = TM.sas_40_1_cbr[(extperkey,)]
            if self.rec.entrydate == fdes.udor:
                self.records = self.rec.records
                if self.rec.records is None:
                    self.records = 0
                self.msg = self.rec.msg
            else:
                self.msg = self.emptyRecord(maxRecords)
                self.records = 0
        except:
            self.rec = TM.sas_40_1_cbr.create((extperkey,))
            self.msg = self.emptyRecord(maxRecords)
            self.records = 0
            self.rec.msg = str(self)
            self.rec.records = len(self)

    def save(self, s, r):
        """ Save the string 's' """
        self.rec.entrydate = self.fdes.udor
        self.rec.msg = s
        self.rec.records = r


# CrewBaggageRecord ------------------------------------------------------{{{2
class CrewBaggageRecord(BaggageRecord):
    """ Format a "Crew Baggage Record" (for the mainframe). """

    def __init__(self, fdes, crew):
        # 'fdes' is a FlightDesignator object.
        # 'crew' is a an Entry object of CrewIterator type.
        # CR378 - Even stricter, now using Machine Readable Zone (MRZ) encoding.
        L = [
            CHR(9, "SK  %s" % (crew.extperkey)),
            "CREW",
            CHR(2, crew.titlerank),
            "/",
            CHR(20, "%s %s" % (edifact.latin1_to_edifact(crew.sn, 'MRZ'),
                edifact.latin1_to_edifact(crew.gn, 'MRZ')))
        ]

        n = NewBaggageRecord(fdes, crew)
        o = OldBaggageRecord(fdes, crew)

        # append "lengths" of new and old records
        L.append(INT(1, len(n)))
        L.append(INT(1, len(o)))

        # append new and old records
        L.append(str(n))
        L.append(str(o))

        # save the new record
        o.save(str(n), len(n))
        self.msg = ''.join(L)


# Help classes ==========================================================={{{1

# FlightDesignator -------------------------------------------------------{{{2
class FlightDesignator:
    """ Help class to store the keys of the flight designator. """
    def __init__(self, fd, udor, adep):
        # Note in this case udor will be an integer!
        self.fd = fd_parser(fd)
        self.udor = AbsTime(udor)
        self.adep = adep

    def __str__(self):
        """ For various messages.  """
        return "%s %04d%s/%s (%s)" % (self.fd.carrier, self.fd.number, self.fd.suffix, self.udor, self.adep)


# functions =============================================================={{{1

# reports ----------------------------------------------------------------{{{2
def reports(**k):
    """
    Return a list of text messages.
    One message for each crew that has this flight as his/her
    first flight of a duty.
    """
    try:
        fdes = FlightDesignator(**k)

        ci = CrewIterator(fdes)
        ti = TripIterator(fdes)
        li = LegIterator(fdes)
        ci.link(trip=ti)
        ti.link(leg=li)
        crewlist = ci.eval()
        if len(crewlist) < 1:
            raise MessageError(report_name, status.CREW_NOT_FOUND, "No crew found for flight %s." % (fdes))
        reportlist = []
        for crew in crewlist:
            if crew.first_in_duty:
                reportlist.append(str(Message(report_name, baggageReconciliation(fdes, crew))))
        if len(reportlist) < 1:
            raise MessageError(report_name, status.CREW_NOT_FOUND, "No crew has flight %s as first flight in duty" % (fdes))
        return reportlist

    except Exception, e:
        # Don't send fault messages
        print str(e)
        return []


# main ==================================================================={{{1
if __name__ == '__main__':
    res = report(fd="SK 000277 ", udor="20070511", adep="OSL")
    print res


# Description of the output format ======================================={{{1
# General ----------------------------------------------------------------{{{2
#
# This report is generated a number of minutes before the departure of a given
# flight.
#
# The report consists of one or more lines formatted for a mainframe system
# which are wrapped in an XML envelope.
#
# The format of the envelope is:
#
# <?xml version="1.0" encoding="UTF-8"?>
# <crewMessage version="1.00">
#     <messageName>CrewBaggageReconciliation</messageName>
#     <messageBody>
#         <baggageReconciliation version="1.00">
#             <crewBaggageInfo> ... </crewBaggageInfo>
#         </baggageReconciliation>
#     </messageBody>
# </crewMessage>
#
# The element 'messageName' always contains 'CrewBaggageReconciliation'.
#
# A message is created for each crew where the given leg is the
# first leg in the crewmember's duty.
#
# The 'crewBaggageInfo' element contains information about the crew and all legs
# in the trip containing the given leg.
#
# The CrewBaggageInfo Record ---------------------------------------------{{{2
# The text string has this format:
#
# message ::= header newrecord oldrecord
# newrecord ::= newleg newleg newleg newleg newleg newleg newleg newleg newleg
# oldrecord ::= oldleg oldleg oldleg oldleg oldleg oldleg oldleg oldleg oldleg

# header -------------------------------------------------------------{{{3
# ExternalPerkey        CHR(9)            e.g. "SK  12345"
# Crew-Text             CHR(4)            always "CREW"
# Catnam                CHR(2)            crew category (title rank), e.g. "FC"
# Crew-Slash            CHR(1)            always "/"
# Name                  CHR(20)           crew name (logname)
# Nbr-Flight-Cur-Sch    NUM(1)            Number of flights in current sling.
# Nbr-Flight-Old-Sch    NUM(1)            Number of flights in old sling.
#                                         > 0 if message contains change of
#                                         schedule

# newleg -------------------------------------------------------------{{{3
# Cur-Activid-carrier   CHR(3)            Flight carrier, e.g. "SK"
# Cur-Activid-flightnum NUM(4)            Flight number, e.g. "0123"
# Cur-Activid-suffix    CHR(1)            Flight suffix, e.g. " "
# Cur-Origsdt-UTC       CHR(7)            UDOR in format DDMMMYY,
#                                         e.g. 01OCT06
# Cur-Origsdt-ALT       CHR(7)            UDOR in local time.
# Cur-Stnfr             CHR(3)            ADEP
# Cur-Stnto             CHR(3)            ADES
# Cur-Status-P          CHR(1)            'A' if active, 'P' if passive

# oldleg -------------------------------------------------------------{{{3
# These fields are empty if no change in schedule has occurred.
#
# Old-Activid-carrier   CHR(3)            Flight carrier, e.g. "SK"
# Old-Activid-flightnum NUM(4)            Flight number, e.g. "0123"
# Old-Activid-suffix    CHR(1)            Flight suffix, e.g. " "
# Old-Origsdt-UTC       CHR(7)            UDOR in format DD-MMM-YY,
#                                         e.g. 01OCT06
# Old-Origsdt-ALT       CHR(7)            UDOR in local time.
# Old-Stnfr             CHR(3)            ADEP
# Old-Stnto             CHR(3)            ADES
# Old-Status-P          CHR(1)            'A' if active, 'P' if passive


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
