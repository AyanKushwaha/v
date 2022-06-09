###############################################################

# Converts between inclusive absdate and exclusive abstime and vice
# versa.
###############################################################


import AbsTime
import AbsDate
import RelTime

_ONE_MINUTE = RelTime.RelTime('00:01')
_24_HOURS = RelTime.RelTime('24:00')
def exclTimeToInclDate(time):
    """
    Takes and abstime in format '15Jan2008 00:00'
    and returns absdate '14Jan2008'
    if time isn't '00:00', the return date is same as abstime date
    """
    try:
        t = time-_ONE_MINUTE
        return AbsDate.AbsDate(t.day_floor())
    except:
        return None

def inclDateToExclTime(date):
    """
    Takes and absdate and returns the next dates abstime closest
    to the date, i.e. '14jan2008' gives '15Jan2008 00:00'
    """
    try:
        return AbsTime.AbsTime(date)+_24_HOURS
    except:
       return None 

def inclDateToInclTime(date):
    """
    Takes and absdate and returns the lastest abstime still on
    the date, i.e. '14jan2008' gives '14Jan2008 23:59'
    """
    try:
        return AbsTime.AbsTime(date)+_24_HOURS-_ONE_MINUTE
    except:
        return None

def inclDateToExclDate(date):
    """
    Takes and absdate and returns the next date absdate closest
    to the date, i.e. '14jan2008' gives '15Jan2008'
    """
    try:
        return AbsDate.AbsDate(AbsTime.AbsTime(date)+_24_HOURS)
    except:
        return None

def exclTimeToInclTime(time):
    """
    Converts excluse abstime to inclusive abstime
    i.e '15jan2008 00:00' to '14Jan2008 00:00'
    """
    try:
        return (time-_ONE_MINUTE).day_floor()
    except:
        return None

def inclTimeToExclTime(time):
    """
    Converts inclusive abstime to exclusive abstime
    i.e '14jan2008 23:59' to '15Jan2008 00:00'
    """
    try:
        return (time+_ONE_MINUTE).day_ceil()
    except:
        return None

def it2et(time):
    """
    Short syntax for inclTimeToExclTime
    """
    return inclTimeToExclTime(time)

def et2it(time):
    """
    Short syntax for exclTimeToInclTime
    """
    return exclTimeToInclTime(time)

def et2id(time):
    """
    Short syntax for inclTimeToExclDate
    """
    return exclTimeToInclDate(time)

def id2et(date):
    """
    Short syntax for exclDateToInclTime
    """
    return inclDateToExclTime(date)
