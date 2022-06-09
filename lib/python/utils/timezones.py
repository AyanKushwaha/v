
# [acosta:07/249@17:36] Borrowed code from docs.python.org and added Europe.

"""
tzinfo implementations.
"""

# imports ================================================================{{{1
from datetime import tzinfo, timedelta, datetime
import time as _time


# constants =============================================================={{{1
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# classes ================================================================{{{1

# TimeHolder -------------------------------------------------------------{{{2
class TimeHolder(tuple):
    """ Stores (Hours, Minutes, Seconds) """
    def __str__(self):
        L = ["%+02d" % self[0]]
        if self[1] != 0 or self[2] !=0:
            L.append("%02d" % self[1])
        if self[2] != 0:
            L.append("%02.1f" % self[2])
        return ':'.join(L)


# TZ_UTC -----------------------------------------------------------------{{{2
class TZ_UTC(tzinfo):
    """ UTC """
    def utcoffset(self, dt):
        return ZERO

    def __repr__(self):
        return "Etc/UTC"

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"


# TZ_Fixed ---------------------------------------------------------------{{{2
class TZ_Fixed(tzinfo):
    """
    Fixed offset in minutes east from UTC, for building timezones with no DST.
    Note that TZ_Fixed(0, "Etc/UTC", "UTC") is equivalent of TZ_UTC()
    """
    def __init__(self, offset, reprname=None, name=None):
        tzinfo.__init__(self)
        self.offset = offset
        self.reprname = reprname
        self.name = name

    def __repr__(self):
        if self.reprname is None:
            n = self.name
        else:
            n = self.reprname
        if n is None:
            n = "UTC%s" % timedelta2str(self.offset)
        return n

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        if self.name is None:
            return "UTC%s" % timedelta2str(self.offset)
        else:
            return self.name

    def utcoffset(self, dt):
        return self.offset


# TZ_Local ---------------------------------------------------------------{{{2
class TZ_Local(tzinfo):
    """
    Captures the local system's view of timezones.
    """
    def __init__(self, *a, **k):
        tzinfo.__init__(self, *a, **k)
        self.stdoffset = timedelta(seconds=-_time.timezone)
        if _time.daylight:
            self.dstoffset = timedelta(seconds=-_time.altzone)
        else:
            self.dstoffset = self.stdoffset

    def dst(self, dt):
        if self._isdst(dt):
            return self.dstoffset - self.stdoffset
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.dstoffset
        else:
            return self.stdoffset

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0


# TZ_DST -----------------------------------------------------------------{{{2
class TZ_DST(tzinfo):
    """
    Timezone with daylight savings.
    This class *MUST* be subclassed
    """
    def __init__(self, offset, reprname=None, stdname=None, dstname=None):
        tzinfo.__init__(self)
        self.offset = offset
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        if self.reprname is None:
            return self.__class__.__name__
        else:
            return self.reprname

    def dst(self, dt):
        raise NotImplementedError('Method dst() is not implemented.')

    def tzname(self, dt):
        if self.dst(dt):
            name = self.dstname
        else:
            name = self.stdname
        if name is None:
            name = "UTC%s" % timedelta2str(self.utcoffset(dt))
        return name

    def utcoffset(self, dt):
        return self.offset + self.dst(dt)


# TZ_Europe --------------------------------------------------------------{{{2
class TZ_Europe(TZ_DST):
    """
    European time zones.
    """
    # The switches are at 1AM UTC on the last Sundays in March and October.
    DSTSTART = datetime(1, 3, 1, 1)
    DSTEND = datetime(1, 10, 1, 1)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            return ZERO
        assert dt.tzinfo is self
        dststart = self._last_sunday_in(self.DSTSTART.replace(year=dt.year))
        dstend = self._last_sunday_in(self.DSTEND.replace(year=dt.year))
        dt -= self.offset # Note that the shift is at 01:00:00Z
        if dststart <= dt.replace(tzinfo=None) < dstend:
            return HOUR
        else:
            return ZERO

    def _last_sunday_in(self, dt):
        next = dt.replace(month=(dt.month + 1))
        days_to_go = 6 - next.weekday()
        if days_to_go:
            next += timedelta(days_to_go)
        return next - timedelta(days=7)


# TZ_US ------------------------------------------------------------------{{{2
class TZ_US(tzinfo):
    """
    A complete implementation of current DST rules for major US time zones.
    """

    # In the US, DST starts at 2am (standard time) on the first Sunday in April.
    DSTSTART = datetime(1, 4, 1, 2)
    # and ends at 2am (DST time; 1am standard time) on the last Sunday of Oct.
    # which is the first Sunday on or after Oct 25.
    DSTEND = datetime(1, 10, 25, 1)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.  It
            # depends on how you want to treat them.  The default fromutc()
            # implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find first Sunday in April & the last in October.
        start = self._first_sunday_on_or_after(self.DSTSTART.replace(year=dt.year))
        end = self._first_sunday_on_or_after(self.DSTEND.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def _first_sunday_on_or_after(dt):
        days_to_go = 6 - dt.weekday()
        if days_to_go:
            dt += timedelta(days_to_go)
        return dt


# functions =============================================================={{{1

# timedelta2str ----------------------------------------------------------{{{2
def timedelta2str(td):
    """
    Convert timedelta to TimeHolder() which has a (better) string
    representation.
    """
    seconds = td.days * 86400 + td.seconds
    if seconds < 0:
        seconds = -seconds
        f = -1
    else:
        f = 1
    (hours, rest) = divmod(seconds, 3600)
    (minutes, rest) = divmod(rest, 60)
    seconds = rest / 60.0
    return TimeHolder((f * hours, minutes, seconds))


# some instances ========================================================={{{1

UTC = TZ_UTC()

Local = TZ_Local()

CET = TZ_Europe(timedelta(hours=1), stdname="CET", dstname="CEST")
WET = TZ_Europe(ZERO, stdname="WET", dstname="WEST")

Eastern  = TZ_US(timedelta(hours=-5), "Eastern",  "EST", "EDT")
Central  = TZ_US(timedelta(hours=-6), "Central",  "CST", "CDT")
Mountain = TZ_US(timedelta(hours=-7), "Mountain", "MST", "MDT")
Pacific  = TZ_US(timedelta(hours=-8), "Pacific",  "PST", "PDT")

Shanghai = TZ_Fixed(timedelta(hours=8), "Asia/Shanghai", "PRC")
Tokyo = TZ_Fixed(timedelta(hours=9), "Asia/Tokyo", "Japan")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
