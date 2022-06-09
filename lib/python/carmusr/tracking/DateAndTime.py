
#
# Functions used by the commandline to handle date and time input.
# 
#

import time
import calendar
import carmensystems.rave.api as R
import Errlog
from carmstd.carmexception import CarmException
from AbsTime import AbsTime

def monthList():
    """
    The function returns a list of 3-letter abriviations of all months.
    The names are dependelt of the local settings. 
    """
    months = []
    for i in range(1,13):
        months.append(time.strftime("%b", time.strptime(str(i),"%m")))
    return map(lambda m: m.lower(), months)

def get_search_time(set_date="", set_time=""):
    """
    The function returns a time string of the form 'ddmmmYYYY HH:MM'.
    If no arguments are given, the now-time is returned.
    If 'set_date' is given as a day (without month) the next occurence of
    the day is returned (or now, if the current day is given).
    If 'set_date' is given with a day and month, the date is set to the closest
    occurence of the given date (6 months forward or 6 months backward).
    If 'set_date' is given with a day and month and year, the date is set to the one specified.
    If 'set_date' is given it MUST be inside the opened period.
    If the 'set_time' is given, the time is set to the given time.
    If only date is given, the time is set to 0:00.
    
    Accepted formats of date is either only a number or a number and an abbreviated month
    (the first three letters) without spaces between them, or a number, an abbreviated month and the
    last 2 digits of the year (from 00 to 99).
    Accepted formats of time is two integers separeted by a period. The minutes
    part is treated as the start of a clock time (if 4.5 is given, it is treated
    as 4:50). Leaving out an integer treats it as if it was zero (only '.' is
    treated as 00:00). 
    """
    format_str = "%d%b%Y %H:%M"
    year = ""
    try:
        now, = R.eval("fundamental.%now%")
        now = time.localtime(time.mktime(now.split() + (0,0,0,0)))
    except:
        # Notice: strptime is not locale-safe w.r.t %b
        now = time.localtime()
    new_time = list(now)
    if set_time:
        hour = int("0"+set_time[:set_time.find(".")])
        minute = int((set_time[set_time.find(".")+1:]+"00")[:2])
        divs = divmod(minute, 60)
        new_time[3:5] = [hour+divs[0], divs[1]]
    elif set_date:
        format_str = format_str.split()[0]
    if not set_date:
        return time.strftime(format_str, new_time)
    if set_date.isdigit():
        try: 
            day = time.strptime(set_date, "%d")[2]
        except:
            print "DATEANDTIME: Error in date format"
            raise DateFormatException
        new_time[2] = day
        if day < now[2]:
            if new_time[1] == 12:
                new_time[1] = 1
                new_time[0] += 1
            else:
                new_time[1] += 1
        if day == now[2]:
            format_str = "%d%b%Y %H:%M"
    else:
        try: 
            (month, day) = time.strptime(set_date, "%d%b")[1:3]
        except:
            try: 
                (year, month, day) = time.strptime(set_date, "%d%b%y")[0:3]
            except:
                try: 
                    (year, month, day) = time.strptime(set_date, "%d%b%Y")[0:3]
                except:
                    print "DATEANDTIME: Error in date format"
                    raise DateFormatException
        new_time[1] = month
        if year:
            new_time[0] = year
        else:
            month_diff = abs(new_time[1] - now[1])
            if month_diff > 6 and new_time < list(now):
                new_time[0] += 1
            elif month_diff >= 6 and new_time > list(now):
                new_time[0] -= 1
    new_time[2] = min(day, calendar.monthrange(new_time[0],new_time[1])[1])
    new_time = time.strftime(format_str, new_time)
    
    valid_time = AbsTime(new_time)
    valid_date, = R.eval("studio_process.%%inside_opened_period%%(%s)" % valid_time)
    if valid_date:
        Errlog.log("DATEANDTIME: The time created is " + new_time)
        return new_time
    else:
        print "DATEANDTIME: Date outside opened period:", valid_time
        raise DateRangeException

class DateFormatException(CarmException):
    """
    Exception rasied when an format error occures in this module.
    """
    def __init__(self, *args):
        CarmException.__init__(self, *args)

class DateRangeException(CarmException):
    """
    Exception rasied when an format error occures in this module.
    """
    def __init__(self, *args):
        CarmException.__init__(self, *args)
