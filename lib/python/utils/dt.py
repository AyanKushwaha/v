

"""
Conversion functions for conversion between "Carmen times" and Python's common
datetime/timedelta objects.

Carmen products are using the epoch 1986-01-01T00:00:00.

examples:
    m2dt(12312411) -> datetime.datetime(2009, 5, 30, 6, 51)
    m2dt(AbsTime("20090530 06:51")) -> datetime.datetime(2009, 5, 30, 6, 51)
    dt2m(datetime.datetime(2009, 5, 30, 6, 51)) -> 12312411
    td2m(datetime.timedelta(days=1, seconds=93)) -> 1441
    RelTime(td2m(datetime.timedelta(days=1, seconds=93))) -> 24:01

Times will be stored as 'minutes since epoch' (an integer) in DAVE.
From Python we will get AbsTime objects from the Model and from the Rave API.

Dates will be stored as 'days since epoch' (an integer) in DAVE.
From Python we will get AbsTime objects from the Model and from the Rave API.
The difference in the model will be for input fields (in Wave).

'Seconds since epoch' are to my knowledge only used in one place: the column
'committs' in table 'dave_revision'.

NOTE 1:
AbsDate is not covered explicitly, however in all known cases you can use wrap
an AbsTime in an AbsDate or vice versa (hours and minutes will get truncated).

NOTE 2:
I have omitted conversions to/from AbsTime/AbsDate and RelTime objects. I don't
want to import these classes for several reasons.  The conversion is trivial: 
- AbsTime(dt2m(dt)) will return an AbsTime object from a datetime 'dt'.
- RelTime(td2m(td)) will return a RelTime object from a timedelta 'td'.
'm2dt' is already accepting 'AbsTime' objects and 'm2td' is accepting 'RelTime'
objects.
"""

import datetime
import re


EPOCH = datetime.datetime(1986, 1, 1, 0, 0)
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


# Conversion datetime -> integer ========================================={{{1
def dt2d(dt):
    """datetime -> 'days since epoch'"""
    # NOTE: seconds and microseconds will be truncated, no rounding!
    return td2d(dt - EPOCH)


def dt2m(dt):
    """datetime -> 'minutes since epoch'"""
    return td2m(dt - EPOCH)


def dt2s(dt):
    """datetime -> 'seconds since epoch'"""
    # NOTE: microseconds will be truncated!
    return td2s(dt - EPOCH)


# Conversion integer -> datetime ========================================={{{1
def d2dt(d):
    """'days since epoch' -> datetime"""
    return EPOCH + d2td(d)


def m2dt(m):
    """'minutes since epoch' -> datetime"""
    # Note: 'm' can be an AbsTime/AbsDate object.
    return EPOCH + m2td(m)


def s2dt(s):
    """'seconds since epoch' -> datetime"""
    return EPOCH + s2td(s)


# Conversion timedelta -> integer ========================================{{{1
def td2d(td):
    """timedelta -> 'number of days'"""
    # NOTE: microseconds and seconds will be truncated!
    return td.days


def td2m(td):
    """timedelta -> 'number of minutes'"""
    # NOTE: microseconds and seconds will be truncated!
    return 1440 * td.days + td.seconds / 60


def td2s(td):
    """timedelta -> 'number of seconds'"""
    # NOTE: microseconds will be truncated!
    return 86400 * td.days + td.seconds


# Conversion integer -> timedelta ========================================{{{1
def d2td(d):
    """'number of days' -> timedelta."""
    return datetime.timedelta(days=int(d))


def m2td(m):
    """'number of minutes' -> timedelta."""
    # Using int() so that 'm' can be a RelTime object.
    return datetime.timedelta(minutes=int(m))


def s2td(s):
    """'number of seconds' -> timedelta."""
    return datetime.timedelta(seconds=int(s))


# Conversion string -> datetime =========================================={{{1

# TimeStringParser -------------------------------------------------------{{{2
class TimeStringParser(object):
    """Parse a time string into its year, month, etc. components."""

    time_component = r'((T|\s)(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2})?(\.(?P<microsecond>\d{1,6})?)?)?)?'

    def __init__(self, s):
        self.match = self.regexp.match(s)

    def __nonzero__(self):
        return self.match is not None

    def __str__(self):
        return "%s-%s-%s %s:%s:%s.%s" % (self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond)
 
    @property
    def year(self):
        i = int(self.match.group('year'))
        if i < 100:
            i += 2000
        return i
    
    @property
    def month(self):
        return int(self.match.group('month'))

    @property
    def day(self):
        return int(self.match.group('day'))

    @property
    def hour(self):
        if self.match.group('hour') is None:
            return 0
        else:
            return int(self.match.group('hour'))

    @property
    def minute(self):
        if self.match.group('minute') is None:
            return 0
        else:
            return int(self.match.group('minute'))

    @property
    def second(self):
        if self.match.group('second') is None:
            return 0
        else:
            return int(self.match.group('second'))

    @property
    def microsecond(self):
        if self.match.group('microsecond') is None:
            return 0
        else:
            decimal = self.match.group('microsecond')
            return int("%s%s" % (decimal, "000000"[:6 - len(decimal)]))


# TimeStringParser1 ------------------------------------------------------{{{2
class TimeStringParser1(TimeStringParser):
    """Handle the format YYYY-mm-dd HH:MM:SS.mmmmmm"""
    regexp = re.compile('^(?P<year>\d{2,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})%s$' % TimeStringParser.time_component)


# TimeStringParser2 ------------------------------------------------------{{{2
class TimeStringParser2(TimeStringParser):
    """Handle the format YYYYmmdd HH:MM:SS.mmmmmm"""
    regexp = re.compile('^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})%s$' % TimeStringParser.time_component)


# TimeStringParser3 ------------------------------------------------------{{{2
class TimeStringParser3(TimeStringParser):
    """Handle the format DDMMMYYYY."""
    regexp = re.compile('^(?P<day>\d{1,2})(?P<monthname>[A-Za-z]{3})(?P<year>\d{2,4})%s$' % TimeStringParser.time_component)

    @property
    def month(self):
        return MONTHS.index(self.match.group('monthname').upper()) + 1


# StringToDateTime -------------------------------------------------------{{{2
class StringToDateTime:
    """Convert input data (command line args) into datetime objects."""

    regexp = re.compile('^(today|tomorrow|yesterday)((\+|-)(\d+))?$')

    parsers = [
        TimeStringParser1,
        TimeStringParser2,
        TimeStringParser3,
    ]

    def __call__(self, s):
        # If None, the forget about it
        if s is None:
            return None

        # If string contains 'today', 'tomorrow' (+|-) offset
        s = s.lower()
        m = self.regexp.match(s)
        if m:
            return self.relative(m)

        # Try with the different time formats
        for parser in self.parsers:
            m = parser(s)
            if m:
                return self.dt(m)

        # Nothing worked, give up!
        raise ValueError("Cannot convert '%s' to a valid date." % s)

    def dt(self, m):
        """Return datetime object from a TimeStringParser object."""
        return datetime.datetime(year=m.year, month=m.month, day=m.day,
                hour=m.hour, minute=m.minute, second=m.second, microsecond=m.microsecond)

    def relative(self, m):
        """Add support for the words 'today', 'tomorrow' and 'yesterday'."""
        name, _, sign, days = m.groups()
        now = datetime.datetime.now()
        today = now.replace(now.year, now.month, now.day, 0, 0, 0, 0)
        if name == 'today':
            dt = today
        elif name == 'tomorrow':
            dt = today + datetime.timedelta(days=1)
        elif name == 'yesterday':
            dt = today - datetime.timedelta(days=1)
        else:
            raise ValueError("%s is not a valid date marker." % name)
        if sign == '-':
            days = -int(days)
        elif sign == '+':
            days = int(days)
        else:
            return dt
        return dt + datetime.timedelta(days=days)


# str2dt -----------------------------------------------------------------{{{2
str2dt = StringToDateTime()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    import tests.utils.test_dt
    tests.utils.test_dt.main()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
