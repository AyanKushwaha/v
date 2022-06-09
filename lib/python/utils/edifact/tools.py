
# [acosta:07/327@16:52] Created.

"""Some conversion functions used by EDIFACT implementations."""
from tm import TM


def edi_date(dt):
    """Convert AbsTime to yymmdd"""
    (y, m, d) = dt.split()[:3]
    return "%02d%02d%02d" % (y % 100, m, d)


def edi_time(dt):
    """Convert AbsTime to HHMM"""
    return "%02d%02d" % dt.split()[3:5]


def edi_datetime(dt):
    """Convert AbsTime to yymmddHHMM"""
    (y, m, d, H, M) = dt.split()[:5]
    return "%02d%02d%02d%02d%02d" % (y % 100, m, d, H, M)


class ISO3166_1:
    """Conversion between ISO 3166-1 character code formats.
    E.g. SE <-> SWE, DK <-> DNK."""

    @staticmethod
    def alpha2to3(code):
        """Convert two character country code to three character code."""
        if code is None or code == '':
            return ''
        try:
            rec = TM.country[(code,)]
            if rec.long_id is None:
                raise ValueError("Could not convert '%s', alpha-3 id missing in 'country'." % (code,))
            return rec.long_id
        except Exception, e:
            raise ValueError("Could not convert '%s'. %s" % (code, e))

    @staticmethod
    def alpha3to2(code):
        """Convert three character country code to two character code."""
        if code is None or code == '':
            return ''
        short_id = None
        for rec in TM.country.search('(long_id=%s)' % (code,)):
            short_id = rec.id
        if short_id is None:
            raise ValueError("Could not convert '%s', alpha-2 id missing in 'country'." % (code,))
        return short_id


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
