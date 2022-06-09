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


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    For Python3: Change xrange -> range
    """
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]


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


def timed(f):
    """returns a tuplet consisting of result of running 'f' and time elapsed printable in form: hh:mm:ss.mmmmmm"""
    start_dt = datetime.now()
    res = f()
    elapsed = datetime.now() - start_dt
    return res, elapsed


def start_build(object_type, crew_ids):
    """
    Start of all build methods

    Puts crew_id into list if it's only one string.

    :param object_type: name of the data object being built (String)
    :param crew_ids: one crew_id as string or a list of crew_ids
    :return: a list of crew_id(s)
    """
    print("/build_%s" % object_type)

    if type(crew_ids) == str:
        crew_ids = list(crew_ids)

    return crew_ids


def end_build(object_type, crew_ids, start):
    """
    End of all build methods

    :param object_type: ame of the data object being built (String)
    :param crew_ids: list of crew IDs
    :param start: datetime when the build function started
    """
    elapsed = datetime.now() - start

    print("Time elapsed building %s %s: %s" %
          (("all" if crew_ids is None else len(crew_ids)), object_type, elapsed))


def calculate_pushable_roster_months():
    """
    Caclulates the union of month ranges open in studio and which months are push-able.
    The rule is that from if "now" is 1st to 15th, only this month may be pushed,
    while starting on the 16th, this and next month may be pushed.
    If only next mont is open, then only next month gets pushed.
    If only this month is open, then only this month gets pushed.
    If neither this or next month are not open, then nothing gets pushed.
    :return: A list of lists [[abstime-start, abstime-end]*]
    """
    start = rave.eval("fundamental.%pp_start%")[0]
    end = rave.eval("fundamental.%pp_end%")[0]
    now = rave.eval("fundamental.%now%")[0]
    print("start - end [ now ]: %s - %s [ %s ] " % (start, end, now))

    now_month_floor = now.month_floor()
    print("now_month_floor: %s" % now_month_floor)
    now_month_ceil = now.month_ceil()
    print("now_month_ceil: %s" % now_month_ceil)
    include_next_month = int(str(now)[:2]) > 12
    print("include_next_month: %s" % include_next_month)
    month_ceil = now_month_ceil.addmonths(1) if include_next_month else now_month_ceil
    print("month_ceil: %s" % month_ceil)

    '''
    if start < now_month_floor:
        start = now_month_floor
        print("start (adjusted): %s" % start)
    '''
    if end > month_ceil:
        end = month_ceil
        print("end (adjusted): %s" % end)

    next_start = start
    months = []
    while next_start < end:
        s = next_start
        e = s.addmonths(1)
        months.append([s, e])
        next_start = e

    return months


def bool_to_lower(val):
    """
    Casts bool to lowercase string
    If the value is None, it will be converted to False

    :param val: a boolean value (True/False)
    :return: "true", "false" or value (if not a boolean)
    """
    if val is None:
        val = False

    if type(val) is bool:
        return str(val).lower()
    else:
        return val


def convert_reltime_to_timedelta(reltime_val):
    if isinstance(reltime_val, RelTime):
        (hhh, mm) = reltime_val.split()
        return timedelta(hours=hhh, minutes=mm)
    else:
        return None


def convert_timedelta_to_iso_duration(timedelta):
    """
    Convert a timedelta into an ISO duration string. Class timedelta only hold days and seconds.

    An ISO duration looks like P2DT22H45M36S', 2 days, 22hours, 45 minutes, 36 seconds.
    Any field may be left out.
    """

    days = timedelta.days
    s = timedelta.seconds

    hours = minutes = seconds = 0
    hours = s / 3600
    minutes = (s - hours * 3600) / 60
    hours += days * 24

    h = '%dH' % hours
    m = '%0dM' % minutes
    return 'PT%s%s' % (h, m)


def format_time_string_as_iso_duration(string_duration):
    if isinstance(string_duration, str):
        input_as_timedelta = convert_reltime_to_timedelta(RelTime(string_duration))
        if input_as_timedelta is not None:
            return convert_timedelta_to_iso_duration(input_as_timedelta)
    else:
        return None


def get_number_of_days_str(start_time, end_time):
    """
    Returns number of days between two string dates.
    :param start_time: string representation of start time
    :type start_time: 'str'
    :param end_time: string representation of end time
    :type end_time: 'str'
    :return: number of days
    """

    # Convert input arguments to datetime objects
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
    end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ')

    # datetime - datetime results in a timedelta object
    day_difference = (end_time - start_time).days

    if day_difference == 0:
        day_difference = 1
    return day_difference


def get_number_of_days_abs_time(start_time, end_time):
    """
    Returns number of days between two AbsTime dates.
    :param start_time: string representation of start time
    :type start_time: 'AbsTime'
    :param end_time: string representation of end time
    :type end_time: 'AbsTime'
    :return: number of days
    """

    diff = end_time.day_floor() - start_time.day_floor()
    days = diff.split()[0] / 24
    if days == 0:
        days = 1
    return days


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

def rel_time_to_str(rel_time):
    """
    Converts RelTime to string with format HH:MM
    :param rel_time: RelTime to be converted to string
    :type rel_time: 'RelTime'
    :return: The datetime string representation.
    """

    if not isinstance(rel_time, RelTime):
        return ""
    
    return "%02d:%02d" % rel_time.split()

def is_empty_meal_code(mealcode):
    if mealcode is None:
        return True
    if str(mealcode) == "":
        return True
    if mealcode.strip(', ') == '':
        return True
    return False


def encode_to_regular(value):
    """
    Attempts to get the regular representation for a value.
    :return: The regular representation if it could be decoded and encoded.
    Otherwise empty string.
    """
    try:
        return value.decode('latin1').encode('utf-8')
    except AttributeError:
        return ""


def str2date(date_string):
    """
    Converts an Abstime formatted string to date
    For example: 19Sep2019 00:00 to 2019-09-19
    """
    datetime_obj = datetime.strptime(date_string, '%d%b%Y %H:%M')
    date_obj = datetime.strftime(datetime_obj, '%Y-%m-%d')
    return date_obj
