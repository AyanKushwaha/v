
# [acosta:06/209@11:06] Added header

"""
This module handles interaction with database entities in the model.
"""

# imports ================================================================{{{1
import re
import cio.rv as rv
import utils.divtools as divtools

from Airport import Airport
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from tm import TM
from utils.paxfigures import FlightMessageInfo, FlightLegMessageInfo
from utils.exception import getCause

import logging
log = logging.getLogger('cio.db')


# classes ================================================================{{{1

# ciostatus --------------------------------------------------------------{{{2
class ciostatus:
    """Symbolic names for different check-in states (as saved in database)."""
    states = (UNDO, CI, CO, COI) = (0, 1, 2, 3)
    modes = (UNASSISTED, ASSISTED) = (0, 4)
    AUTOMATIC_CO = 8


# DBException ------------------------------------------------------------{{{2
class DBException(Exception):
    """ Signals failure (currently when crew is not rostered). """
    msg = ''
    def __init__(self, msg):
        Exception.__init__(self, self.msg)
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# Message types ----------------------------------------------------------{{{2
class MessageTypeDict(dict):
    """
    Create a dictionary with the different message types.
    The dictionary contains a list, to preserve order.
    If x is of type MessageTypeDict, then, x[type] will return:
        (1): type.si (if type is described in database).
        (2): default value for the type given (x[type]).
        (3): fallback value (x[default])
    """
    def __init__(self, seq, default=None):
        """ Init with a list/tuple of (key, value). """
        dict.__init__(self)
        self.default = default
        self.list = []
        for (k, v) in seq:
            self[k] = v
        assert default in self.list, "Default key must be represented in sequence."

    def __getitem__(self, key):
        """ Try to get value from database, then from self, then from default. """
        try:
            si = key.si
            if not si is None:
                return si
        except:
            pass
        try:
            return dict.__getitem__(self, str(key).upper)
        except KeyError:
            if key is None:
                return dict.__getitem__(self, self.default)
            else:
                return str(key).upper()

    def get(self, key, *a):
        """ As __getitem__, but with option to add own default. """
        try:
            si = key.si
            if not si is None:
                return si
        except:
            key = str(key)
        if not a:
            a = (self[self.default],)
        return dict.get(self, key, *a)

    def __setitem__(self, key, value):
        """ For completeness. """
        if not key in self.list:
            self.list.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        """ For completeness. """
        dict.__delitem__(self, key)
        self.list.remove(key)

    def __iter__(self):
        """ Return objects in list's order. """
        return iter(self.list)

    def index(self, key):
        """ For sorting purposes, return index from initialization. """
        if not key in self.list:
            return self.list.index(self.default)
        return self.list.index(key)


# message_types ----------------------------------------------------------{{{3
# Singleton
message_types = MessageTypeDict((
        ('SLOT', 'SLOT TIME'),
        ('RED', 'REDUCED CREW'),
        ('GEN', 'GENERAL INFO'),
        ('DEP', 'DEPORTEE'),
        ('VIP', 'VIP'),
        ('SICK', 'SICK TRANSPORT')
    ), default='GEN')


# classes for holding values ---------------------------------------------{{{2

# CrewDoc ----------------------------------------------------------------{{{3
class CrewDoc:
    """ Document information (passports, visas). """
    def __init__(self, row):
        self.type = row.doc.typ
        self.subtype = row.doc.subtype
        self.validfrom = row.validfrom
        self.validto = AbsDate(row.validto)
        self.docno = row.docno

    def __str__(self):
        if self.docno:
            num = " with number %s" % self.docno
        else:
            num = ""
        return "%s expires %s for %s%s." % (self.validto, self.type, self.subtype, num)


# CrewMessage ------------------------------------------------------------{{{3
class CrewMessage:
    """ Private/Office/Broadcast messages. """
    def __init__(self, msg):
        self.msg = msg 
        self.header = "(%s/%s)" % (self.msg.created, self.msg.created_by)
        rows = []
        for row in TM.notification_message.search('(idnr=%s)' % self.msg.idnr):
            rows.append((row.seq_no, row.free_text))
        rows.sort()
        self.message = ' '.join([txt for (seqno, txt) in rows])

    def fmtList(self, width=72):
        """ Return list of lines, each with a maximum width. """
        return fmt_list(self.message, width)

    def setDelivered(self, now):
        """ Mark message as delivered. """
        self.msg.delivered = now

    def __str__(self):
        """ For basic tests """
        return '\n'.join([self.header] + self.fmtList())


# FlightMessage ----------------------------------------------------------{{{3
class FlightMessage:
    """ Message for a specific flight. """
    format = "%s/%s     %s-%s    STD %s    STA %s    %s"

    def __init__(self, leg, msg):
        self.leg = leg
        try:
            self.msgtype = msg.msgtype.id
        except:
            self.msgtype = msg.msgtype
        self.msgtext = msg.msgtext
        self.logtime = msg.logtime
        self.type = message_types[self.msgtype]

    def __str__(self):
        return self.msgtext

    def fmtList(self, width=50):
        """Return list of one or more rows depending on content."""
        return fmt_list(self.fix_format(self.msgtext), width)

    def fix_format(self, string):
        """Slot times etc. comes in a very strange format with a lot of spaces.
        This code does it best to try to correct this."""
        # Convert two or more spaces to two spaces
        return '  '.join(re.split('\s[\s]+', string))

    def legHeader(self):
        """ Return a formatted string with info about the leg """
        return self.format % (
            self.leg.flight_name,
            str(self.leg.udor).split()[0],
            self.leg.adep,
            self.leg.ades,
            "%02d:%02d" % self.leg.std_lt.split()[3:5],
            "%02d:%02d" % self.leg.sta_lt.split()[3:5],
            self.leg.actype
        )

    def messageHeader(self):
        """
        Return message header (creation time and userid of message creator).
        """
        if self.logtime is None:
            return self.type
        else:
            return "%s (Entered %s)" % (self.type, self.logtime)


# Message ----------------------------------------------------------------{{{3
class Message:
    """ Manually created flight messages (reduced crew). """
    def __init__(self, msgtype=None, msgtext=None, logtime=None):
        self.msgtype = msgtype
        self.msgtext = msgtext
        self.logtime = logtime

    def __str__(self):
        return self.msgtext


# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo(list):
    """
    Search data model for messages (both private and office) for a crew.

    This principle is used:
     - If not delivered, the message will be shown.
     - All messages are shown until deadline is passed (regardless of
       isdelivered).

    usage example:
        x = db.CrewInfo(id, now)
        if x:
            for msg in x:
                print msg.header
                for row in msg:
                    print row
    """
    def __init__(self, id, now):
        list.__init__(self)
        self.now = now
        try:
            crew_ref = TM.crew[(id,)]
            rows = [(r.created, r) for r in crew_ref.referers('crew_notification', 'crew')
                    if r.typ.typ == 'Manual' and (r.deadline > now or r.delivered is None)]
            rows.sort()
            for (date, row) in rows:
                self.append(CrewMessage(row))
        except Exception, e:
            log.error(getCause())

    def setDelivered(self):
        for x in self:
            x.setDelivered(self.now)

    def __str__(self):
        """For Basic Tests only."""
        return '\n'.join([str(x) for x in self])


# ExpiryInfo -------------------------------------------------------------{{{2
class ExpiryInfo(list):
    """
    Searches crew_documents for documents that are about to expire.

    usage example:
        x = db.ExpiryInfo(id, now)
        if x:
            for l in x:
                print l
    """
    def __init__(self, id, now):
        list.__init__(self)
        self.id = id
        self.today = AbsTime(now).day_floor()
        self.excludeDocType = ['REC']
        self._search()
        self.sort(lambda a, b: cmp(a.validto, b.validto))

    def __str__(self):
        return '\n'.join(self)

    # private methods ----------------------------------------------------{{{3
##    def _found_checkin(self, low):
##        """
##        Returns true if a checkin was found within the interval (low, now)
##        """
##        checkins = TM.cio_event.search("(&(crew=%s)(ciotime<=%s)(ciotime>=%s))" % (self.id, self.today, low))
##        # [acosta:06/221@11:23] Can't use len(checkins), can't use checkins[0]
##        for c in checkins:
##            return True
##        return False

    def _search(self):
        """
        Searches for documents that are about to expire.
        Search scope are all documents that expire within the next 32 days.
        Filter out warnings where a more recent document already exists.
        """

        for row in TM.crew[(self.id,)].referers('crew_document', 'crew'):
            if row.doc.typ in self.excludeDocType:
                continue
            if (row.validto is not None and row.validto >= self.today 
                    and row.validto <= (self.today + RelTime(768, 0))):
                t0 = AbsTime(row.validto)
                for row2 in TM.crew[(self.id,)].referers('crew_document', 'crew'):
                    if (row2.doc.typ == row.doc.typ and row2.validto > t0):
                        t0 = AbsTime(row2.validto)
                t1 = t0 - RelTime(768, 0)
                if self.today >= t1:
                    try:
                        self.append(CrewDoc(row))
                    except:
                        pass


# SpecialInfo ------------------------------------------------------------{{{2
class SpecialInfo(list):
    """
    Searches data model for special info, i.e. messages that are targeted to
    PIC or C/A 1 for a specific flight.

    usage example:
        si = db.SpecialInfo(id, r)
        if si:
            ostd = AbsTime(0)
            otype = None
            for i in si:
                if i.leg.std != ostd:
                    print i.legHeader()
                    otype = None
                if i.type != otype:
                    print i.messageHeader()
                print str(i)
                ostd = i.leg.std_lt
                otype = i.type
                ...
    """
    _reduced_cc_format = "Number of CC is %s of %s."

    def __init__(self, id, now):
        list.__init__(self)
        self.id = id
        flminfo = FlightLegMessageInfo()
        fminfo = FlightMessageInfo()
        # [acosta:09/231@11:23] Updated to show all messages until next mandatory C/O.
        for leg in rv.EvalNextDutypass(self.id):
            # Only Pilots and C/A 1 will receive message
            if leg.rank.startswith('F') or str(self.id) == str(leg.ca1):
                for msg in flminfo(leg.udor, leg.fd, leg.adep):
                    self.append(FlightMessage(leg, msg))
                for msg in fminfo(leg.udor, leg.fd):
                    self.append(FlightMessage(leg, msg))
                # SASCMS-2411 - If need has been reduced and less people
                # assigned than needed we send the message.
                if leg.number_of_cc < leg.jar_need_cc:
                    self.append(FlightMessage(leg,
                                              Message(msgtype="RED",
                                                      msgtext=self._reduced_cc_format % (leg.number_of_cc, leg.jar_need_cc),
                                                      logtime=now)))
                elif leg.reduced_need and (leg.number_of_cc < leg.booked):
                    self.append(FlightMessage(leg,
                                              Message(msgtype="RED",
                                                      msgtext=self._reduced_cc_format % (leg.number_of_cc, leg.booked),
                                                      logtime=now)))
        flminfo.close()
        fminfo.close()
        self.sort(self._sort_function)

    def __str__(self):
        """One line per row. Used for basic tests only."""
        return '\n'.join(self.fmtList())

    def fmtList(self, width=50):
        """Return list of print rows, if a print row is too long, it's splitted
        into several rows. This code is duplicated in run.py and only used here
        for basic tests."""
        S = []
        if self:
            ostd_lt = AbsTime(0)
            for i in self:
                if i.leg.std_lt != ostd_lt:
                    S.append(i.legHeader())
                S.append(i.messageHeader())
                S.extend(i.fmtList(width))
                ostd_lt = i.leg.std_lt
        return S

    # private methods ----------------------------------------------------{{{3
    def _sort_function(self, a, b):
        """
        key 1 is the departure time,
        key 2 is the internal order of the special info messages (from self._order)
        """
        time_a = a.leg.std_lt
        time_b = b.leg.std_lt
        if time_a == time_b:
            key_a = message_types.index(a.type)
            key_b = message_types.index(b.type)
            return cmp(key_a, key_b)
        else:
            return cmp(time_a, time_b)


# functions =============================================================={{{1

# fmt_list ---------------------------------------------------------------{{{2
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


# get_cio_event_list -----------------------------------------------------{{{2
def get_cio_event_list(crewid, ivalstart, ivalend, maxentries):
    """ Get list of ci/co events. """
    filter = "(&(crew.id=%s)(ciotime>=%s)(ciotime<=%s))" % (crewid, ivalstart, ivalend)
    L = [(int(E.ciotime), E) for E in TM.cio_event.search(filter)]
    L.sort()
    return [E for (time, E) in L]
 

# record_cio_event -------------------------------------------------------{{{2
def record_cio_event(crewid, ciotime, st=None, et=None, status=None,
        assisted=False):
    """
    Record an event to 'cio_event' and change status in 'cio_status'.
        ciotime  : Actual check-in / check-out time.
        et       : Estimated end time of duty (if CI), not necessary.
        status   : {status.CI, status.CO, status.COI}
        assisted : True if the check-in/check-out was assisted.
    """
    crewid_ref = TM.crew[(crewid,)]
    try:
        eventRecord = TM.cio_event.create((crewid_ref, ciotime))
        eventRecord.assisted = assisted
        eventRecord.statuscode = status
    except:
        # Identical key, ignore second attempt
        pass

    if status is not None:
        # All events are recorded, but not all lead to a status change.
        try:
            statusRecord = TM.cio_status[crewid_ref,]
        except:
            statusRecord = TM.cio_status.create((crewid_ref,))
        statusRecord.ciotime = ciotime
        statusRecord.status = status
        statusRecord.assisted = assisted
        if status & ciostatus.CI:
            statusRecord.st = st
            statusRecord.et = et
            statusRecord.completed = False
        elif status & ciostatus.CO:
            if statusRecord.st is None:
                # was removed earlier, try to recreate using ciotime
                statusRecord.st = _get_earlier_ci(crewid_ref, ciotime)
            statusRecord.et = ciotime
            statusRecord.completed = True


# set_ci_frozen ----------------------------------------------------------{{{2
def set_ci_frozen(crewid, st, comment=None):
    """
    Update 'cio_frozen' with new start time.
    """
    crewid_ref = TM.crew.getOrCreateRef((crewid,))
    key = (crewid_ref, st)
    try:
        record = TM.ci_frozen[key]
    except:
        record = TM.ci_frozen.create(key)
    if not comment is None:
        record.si = comment


# _get_earlier_ci --------------------------------------------------------{{{2
def _get_earlier_ci(crew_ref, ciotime):
    L = [x.ciotime for x in crew_ref.referers('cio_event', 'crew') 
            if x.statuscode & ciostatus.CI]
    L.sort(reverse=True)
    for rec in L:
        return rec
    return None


# bit --------------------------------------------------------------------{{{2
def bit(x):
    """
    Built-In Test
    Runs _bit for each argument
    -or-
    if no arguments, for all crewid's and finally one impossible crewid.
    """
    #r = rv.EvalRoster('27936')
    #print CrewInfo('27936', r.now)
    #print SpecialInfo(x, r.now)
    #print ExpiryInfo(x, r.now)
    pass


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """
    import sys
    bit(sys.argv[1:])


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# EOF
