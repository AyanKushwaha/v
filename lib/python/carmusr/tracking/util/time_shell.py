
import time
from AbsTime import AbsTime


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def abstime_now():
        year, month, day, hours, minutes = time.localtime()[0:5]
        return AbsTime(year, month, day, hours, minutes)


def abstime(abstime_str=None):
    return AbsTime(abstime_str) if abstime_str else abstime_now()


def isodate2absdate(d):
    """
    :param d: String of form 'yyyy-mm-dd'
    :return: String of form 'ddmonyyyy'
    """
    y,m,d = d.split("-")
    return "%s%s%s" % (d, MONTHS[int()], y)
