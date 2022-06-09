
# [acosta:07/250@10:57] Temporary solution imitating some of the interfaces in the Airport module.

"""
Temporary replacement for Carmen Airport module.

Note that Airport is not possible to import from scripts tarted by Mirador
See Bugzilla #14598.
"""

import utils.timezones as timezones
from datetime import datetime
from AbsTime import AbsTime

tzdict = {
    'TYO': timezones.Tokyo,
    'NRT': timezones.Tokyo,
    'PEK': timezones.Shanghai,
    'BJS': timezones.Shanghai,
    'SHA': timezones.Shanghai,
    'PVG': timezones.Shanghai,
}

default_tz = timezones.CET


# Airport ----------------------------------------------------------------{{{2
class Airport:
    """
    This class is a temporary replacement for the Airport module.
    See Bugzilla #14598.
    """
    def __init__(self, apcode):
        self.name = apcode
        self.tz = tzdict.get(apcode, default_tz)

    def getUTCTime(self, t):
        (_y, _m, _d, _H, _M) = t.split()[:5]
        dt = datetime(_y, _m, _d, _H, _M, 0, 0, self.tz)
        utc = dt.astimezone(timezones.UTC)
        return AbsTime(utc.year, utc.month, utc.day, utc.hour, utc.minute)

    def getLocalTime(self, t):
        (_y, _m, _d, _H, _M) = t.split()[:5]
        dt = datetime(_y, _m, _d, _H, _M, 0, 0, timezones.UTC)
        lt = dt.astimezone(self.tz)
        return AbsTime(lt.year, lt.month, lt.day, lt.hour, lt.minute)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
