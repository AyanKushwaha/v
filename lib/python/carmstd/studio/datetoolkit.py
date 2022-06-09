from carmensystems.basics.abstime import AbsTime
from carmensystems.basics.reltime import RelTime
        
def add_half_day(date):
    return date + RelTime('12:00')

def add_hour(date):
    return date + RelTime('1:00')

def minus_minute(date):
    return date - RelTime('0:01')

def get_weekday(date):
    """
    How to handle language ??
    """
    index =int(date.time_of_week()/RelTime("24:00"))
    return ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")[index]


def day_range(first_day, end_day):
    """
    generator of days to loop from first_day to end_day
    should be in Abstime module ??
    @param first_day: AbsTime. First day of the loop
    @param end_day: AbsTime. Last day of the loop
    """
    day = first_day
    while day <= end_day:
        yield day
        day=day.adddays(1)
