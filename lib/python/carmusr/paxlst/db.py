
# [acosta:07/332@12:35] Created.

"""
Handle updates of table paxlst_log which is needed to get a revisions and
reference IDs for the crew manifests/MCLs.
"""

import time

from carmensystems.dave import dmf
from AbsTime import AbsTime
from RelTime import RelTime

from tm import TM
from utils.divtools import fd_parser


table_name = 'paxlst_log'


class Ticket:
    def __init__(self):
        self.timestamp = AbsTime(*now())
        self.seqno = None

    def get_seqno(self):
        self.seqno = get_seqno()
        return self.seqno

    def save(self, count=None):
        if self.seqno is None:
            self.seqno = self.get_seqno()
        rec = getattr(TM, table_name).create((self.seqno,))
        rec.revision = self.revision
        rec.refid = self.refid
        rec.timestmp = self.timestamp
        rec.country = TM.country.getOrCreateRef((self.country,))
        rec.ismcl = self.mcl
        if self.mcl:
            rec.changetype = self.changetype
        else:
            ap_ref = TM.airport.getOrCreateRef(self.adep)
            # Note that the model server will always provide the
            # latest data from flight_leg, even when running in
            # published mode. In this case it does not matter
            # though. The lookup will still succeed because no
            # legs are being removed.
            rec.flight = TM.flight_leg[(self.udor, self.fd.flight_descriptor, ap_ref)]
        rec.cnt = count


class MCLTicket(Ticket):
    def __init__(self, country, changetype):
        Ticket.__init__(self)
        self.country = country
        self.mcl = True
        self.changetype = changetype
        self.revision = self.get_revision()
        (y, m, d) = self.timestamp.split()[:3]
        self.refid = 'SK%02dMCL%02d%02d%02d' % (self.revision, y % 100, m, d)

    def get_revision(self):
        (y, m, d) = self.timestamp.split()[:3]
        today = AbsTime(y, m, d, 0, 0)
        tomorrow = today + RelTime(24 * 60)
        max = 0
        for x in getattr(TM, table_name).search(
                '(&(timestmp>=%s)(timestmp<%s)(country=%s)(ismcl=true))' % (
                today, tomorrow, self.country)):
            if x.revision > max:
                max = x.revision
        return max + 1


class CLTicket(Ticket):
    def __init__(self, country, fd, udor, adep):
        Ticket.__init__(self)
        self.mcl = False
        self.country = country
        self.fd = fd_parser(fd)
        self.adep = adep
        self.udor = AbsTime(udor)
        self.revision = self.get_revision()
        self.refid = "%s%s%s %02d %s" % ( self.fd.carrier,
                self.fd.number, self.fd.suffix, self.udor.split()[2], adep)

    def get_revision(self):
        max = 0
        for x in TM.flight_leg[(self.udor, self.fd.flight_descriptor, TM.airport[(self.adep,)])].referers(table_name, 'flight'):
            if x.revision > max:
                max = x.revision
        return max + 1


def now():
    return time.localtime()[:5]


def get_seqno():
    return dmf.BorrowConnection(TM.conn()).getNextSeqValue("seq_paxlst")


def get_mcl_ticket(country, changetype):
    return MCLTicket(country, changetype)


def get_cl_ticket(country, fd, udor, adep):
    return CLTicket(country, fd, udor, adep)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
