# coding: utf-8
##################################################
#
# Module containing helper functions
#
##################################################
from datetime import datetime, timedelta

from AbsTime import AbsTime
from RelTime import RelTime
import carmensystems.rave.api as rave


def show_message(message, title=""):
    """A basic modal dialog for presenting a (multiline) string in studio.
    :param message: String. A possibly multiline string to be shown as a mesage in a popup-window.
    :param title: String. An optional title for the window.
    :return:
    """
    import tempfile
    import carmstd.cfhExtensions as ext

    f_name = tempfile.mktemp()
    f = open(f_name, "w")
    f.write(message)
    f.close()
    ext.showFile(f.name, title)

def abs_time_to_str(abs_time, lex24=False):
    """
    Converts AbsTime to string with format YYYY-MM-DDTHH:MM:SS
    :param abs_time: AbsTime to be converted to string
    :type abs_time: 'AbsTime'
    :param lex24: If True '00:00' is represented as '23:59:59' on previous day.
    :type lex24: 'bool'
    :return: The datetime string representation.
    """

    if not isinstance(abs_time, AbsTime):
        return ""
    (y, mo, d, h, mi) = abs_time.split()
    if lex24 and h == 0 and mi == 0:
        lex24_result = abs_time - RelTime(0, 1)
        (y, mo, d) = lex24_result.split()[:3]
        h = 23
        mi = 59
        return "%04d-%02d-%02dT%02d:%02d:59" % (y, mo, d, h, mi)

    return "%4d-%02d-%02dT%02d:%02d:00" % abs_time.split()
