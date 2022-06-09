from AbsTime import AbsTime

def tosec(atime):
    "Converts an AbsTime string to seconds"
    print int(AbsTime(atime))*60

def toint(atime):
    "Converts and AbsTime string to minutes"
    print int(AbsTime(atime))
tomin = toint

def today(atime):
    "Converts an AbsTime string to days"
    print int(AbsTime(atime))/1440

def fromint(atime):
    "Converts a number of minutes to an AbsTime string"
    print str(AbsTime(int(atime)))
frommin = fromint

def fromsec(atime):
    "Converts a number of seconds to an AbsTime string"
    print str(AbsTime(int(atime)/60))

def fromday(atime):
    "Converts a number of days (UDOR, etc) to an AbsTime string"
    print str(AbsTime(int(atime)*1440))

