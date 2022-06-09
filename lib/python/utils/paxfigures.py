
# [acosta:07/339@16:39] Created.
# [acosta:08/301@10:56] Added flight_leg_message and flight_message.

"""
Use EntityConnection to get PAX information, to be able to exclude the huge PAX
tables to be loaded in Rave or in the model.

This module should have a different name, it handles not only PAX info, but
also flight delay info and messages targeted to the crew of a flight or a
flight leg.
"""

from utils.dave import EC
from utils.divtools import fd_parser


# These fields are used when a table is referring to flight_leg
default_fields = {
    'udor': 'leg_udor',
    'fd': 'leg_fd',
    'adep': 'leg_adep',
}


class EConn(object):
    """ Generic base class. """
    def __init__(self, ec=None, table=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        if ec is None:
            # Use table manager to get connection/schema
            from tm import TM
            self._my_ec = True
            self.ec = EC(TM.getConnStr(), TM.getSchemaStr())
        else:
            self._my_ec = False
            self.ec = ec
        assert table is not None
        self.table = table

    def __del__(self):
        self.close()

    def close(self):
        try:
            if self._my_ec:
                self.ec.close()
        except:
            # Maybe we should do something here...
            pass


class AuxInfo(EConn):
    """ Generic base class for flight info. """
    def __init__(self, ec=None, table=None, fields=default_fields):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        EConn.__init__(self, ec, table)
        self.fields = fields

    def __call__(self, udor=None, fd=None, adep=None):
        """Make object callable, at least one of the arguments has to be
        supplied."""
        s = []
        if not udor is None:
            s.append("%s = %d" % (self.fields['udor'], int(udor) / 1440))
        if not fd is None:
            f = fd_parser(fd)
            s.append("%s = '%s'" % (self.fields['fd'], f.flight_descriptor))
        if not adep is None:
            s.append("%s = '%s'" % (self.fields['adep'], adep))
        assert len(s) > 0, "Must give at least one of 'fd', 'udor' and 'adep'."
        return list(getattr(self.ec, self.table).search(' AND '.join(s)))


class PaxInfo(AuxInfo):
    """
    Return PAX figures using EntityConnection from flight_leg_pax table.

    Usage:
    With default connection (grabbed from TableManager).
        from utils.paxfigures import PaxInfo
        paxinfo = PaxInfo()
        for leg in roster:
            ...
            for p in paxinfo(leg.udor, leg.fd, leg.adep):
                print "\tsvc: %s - ppax %s, bpax %s, apax %s" % (p.svc, p.ppax, p.bpax, p.apax)

    If a separate connection is wanted (stand-alone script).
        from utils.dave import EC
        from utils.paxfigures import Paxinfo
        paxinfo = PaxInfo(EC(connstr, schema))
    """
    def __init__(self, ec=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        AuxInfo.__init__(self, ec, 'flight_leg_pax')


class DelayInfo(AuxInfo):
    """
    Return Delay times using EntityConnection from flight_leg_delay table.

    Usage:
    With default connection (grabbed from TableManager).
        from utils.paxfigures import DelayInfo
        delayinfo = DelayInfo()
        for leg in roster:
            ...
            for d in delayinfo(leg.udor, leg.fd, leg.adep):
                print "\tseq: %s - code %s, subcode %s, duration %s, reasontext %s" % (
                        d.seq, d.code, d.subcode, d.duration, d.reasontext)

    If a separate connection is wanted (stand-alone script).
        from utils.dave import EC
        from utils.paxfigures import DelayInfo
        delayinfo = DelayInfo(EC(connstr, schema))
    """
    def __init__(self, ec=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        AuxInfo.__init__(self, ec, 'flight_leg_delay')


class FlightLegMessageInfo(AuxInfo):
    """
    Return messages that are specific for a flight leg.
    These messages could be e.g. slot times, VIP info, sick transport info,
    etc.

    Usage:
    With default connection (grabbed from TableManager).
        from utils.paxfigures import FlightLegMessageInfo
        flminfo = FlightLegMessageInfo()
        for leg in roster:
            ...
            for d in flminfo(leg.udor, leg.fd, leg.adep):
                print "\t%s (%s): %s" % (d.msgtype, d.logtime, d.msgtext)

    If a separate connection is wanted (stand-alone script).
        from utils.dave import EC
        from utils.paxfigures import FlightLegMessageInfo
        flminfo = FlightLegMessageInfo(EC(connstr, schema))
    """
    def __init__(self, ec=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        AuxInfo.__init__(self, ec, 'flight_leg_message')


class FlightMessageInfo(AuxInfo):
    """
    Get messages targeted to a specific flight (could be more than one leg).
    See comments above for FlightLegMessageInfo.
    """
    def __init__(self, ec=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        # Note that flight_message does not refer to flight_leg, so the 
        # column names are slightly different.
        AuxInfo.__init__(self, ec, 'flight_message', {'udor': 'udor', 
            'fd': 'fd'})


class CIOStatus(EConn):
    """Use 'cio_status' table to check if a crew member is checked-in or not.
    This solution is not optimal, but since there is a delay between refresh
    in the report server, there is no other way to get recent info."""
    def __init__(self, ec=None):
        """Either supply utils.dave.EC object (using an existing connection),
        or, if no parameter supplied, create a new connection based on the
        connection parameters from TableManager."""
        EConn.__init__(self, ec, 'cio_status')

    def __call__(self, crewid):
        """Return True if the crew member is checked-in."""
        return list(getattr(self.ec, self.table).search("crew = '%s'" % crewid))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
