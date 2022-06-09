"""
Help functions for date/time.
"""

from RelTime import RelTime
from AbsDate import AbsDate
from AbsTime import AbsTime
import Dates
from carmensystems.rave import api as rave


def abstime2gui_weekday_short_name(date):
    """
    :param date: date to evaluate weekday for
    :type date: AbsTime or AbsDate
    :returns: Weekday for the date (Localized short name)
    :rtype: String
    """
    return rave.eval('fundamental.%%abstime2gui_weekday_short_name%%(%s)' % date)[0]


def day_num2gui_weekday_short_name(day_num):
    """
    :param day_num: 1 for monday, 7 for sunday
    :type day_num: int
    :returns: Weekday for the date (Localized short name)
    :rtype: String
    """
    return rave.eval('fundamental.%%day_num2gui_weekday_short_name%%(%s)' % day_num)[0]


def day_range(first_day, end_day):
    """
    Generator of 24h intervals.

    :param first_day: First date+time to be returned from the generator
    :type first_day: AbsTime
    :param end_day: The last value from the generator is equal or less then 24:00 before this date+time.
    :type end_day: AbsTime
    """

    day = first_day
    while day <= end_day:
        yield day
        day = day.adddays(1)


def day_set_splitter(days):
    """
    A generator that splits a collection of days into printable sub sets;
    a more flexible alternative to the build-in rave iterators
    'actual_leg_period' and 'actual_chain_period'.

    :param days: A collection of days (AbsTime or AbsDate).
    :returns: An iterator returning (FROM_DATE, TO_DATE, FREQ), where
              FROM_DATE & TO_DATE are AbsTime with time part set to 00:00 and
              FREQ is a list with 7 booleans, one per week day.
    """

    one_day = RelTime(1440)
    days = frozenset(AbsTime(AbsDate(day)) for day in days)
    start_date = end_date = None
    freq = [False] * 7

    for date in day_range(min(days), max(days)):

        op_on_day = date in days

        if not start_date and not op_on_day:
            continue

        if not start_date:
            start_date = date

        wday = int(date.time_of_week() / one_day)

        if (date - start_date) / one_day < 7:  # Recoding frequency
            freq[wday] = op_on_day
        else:  # Checking recorded frequency
            if freq[wday] != op_on_day:

                yield start_date, end_date, freq

                start_date = end_date = None
                freq = [False] * 7
                if op_on_day:
                    start_date = date
                    freq[wday] = op_on_day

        if op_on_day:
            end_date = date

    yield start_date, end_date, freq


def freq2str(freq, day_with_no_traffic_symbol="."):
    """
    Converts a boolean frequency list to a string.
    """
    return "".join(str(n + 1) if v else day_with_no_traffic_symbol
                   for n, v
                   in enumerate(freq))


def abstime2gui_date_string(a):
    """
    Converts AbsDate or AbsTime to GUI date string.
    """
    return Dates.FDatExtendedInt2Date(a.getRep())


def abstime2gui_datetime_string(a):
    """
    Converts AbsTime to localized GUI date+time string.
    """
    return Dates.FDatExtendedInt2DateTime(a.getRep())


def abstime2gui_day_plus_month(date):
    """
    Converts AbsTime or AbsDate to localized "day + month" GUI string.
    """
    return rave.eval('fundamental.%%abstime2gui_day_plus_month%%(%s)' % date)[0]


def abstime2gui_month_plus_year(a):
    """
    Converts AbsTime or AbsDate to localized "month + year" GUI string.
    """
    return rave.eval('fundamental.%%abstime2gui_month_plus_year%%(%s)' % a)[0]

# End of file
