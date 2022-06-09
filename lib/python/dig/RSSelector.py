"""
Class to select right Historic reportserver, for historic requests

Example:
rs=RSSelector()
reportserver=rs.getRS(AbsTime date)

print rs shows all breakpoints, for selecting a certain reportserver.
>>> print rs
Breakpoints: ['16FEB2008 00:00', '01MAY2008 00:00', '16JUL2008 00:00', '01OCT2008 00:00', '16DEC2008 00:00', '01MAR2009 00:00', '16MAY2009 00:00', '01AUG2009 00:00', '16OCT2009 00:00', '01JAN2010 00:00']
 RSs: {1: 'rs_historic_27', 2: 'rs_historic_24', 3: 'rs_historic_21', 4: 'rs_historic_18', 5: 'rs_historic_15', 6: 'rs_historic_12', 7: 'rs_historic_9', 8: 'rs_historic_6', 9: 'rs_historic_3'}
>= 16FEB2008 00:00 => rs_historic_27
>= 01MAY2008 00:00 => rs_historic_24
>= 16JUL2008 00:00 => rs_historic_21
>= 01OCT2008 00:00 => rs_historic_18
>= 16DEC2008 00:00 => rs_historic_15
>= 01MAR2009 00:00 => rs_historic_12
>= 16MAY2009 00:00 => rs_historic_9
>= 01AUG2009 00:00 => rs_historic_6
>= 16OCT2009 00:00 => rs_historic_3

So calls to getRS(date) with date >= 16FEB2008 and date < 01MAY2008 returns rs_historic_27, and calls with 
date >= 01May2008 and date < 16JUL2008 returns rs_historic_24 and so on.

Throws KeyError if a date outside known boundaries is requested.
<  16FEB2008 00:00 => KeyError exception
>= 01JAN2010 00:00 => KeyError exception
"""
from AbsTime import AbsTime
import time
from bisect import bisect

class RSSelector:
    RSs = {}
    bp = [] 
    def __init__(self):
        self.breakpoints = [] 
        now = time.gmtime(time.time())
        myNow = AbsTime(*now[:5])
        prevMonthStart = AbsTime(myNow).month_floor()
        prevMonthStart = prevMonthStart.addmonths(-1) 
        r = range(23,1,-5)
        no=0
        no=no+1
        rsNo=27
        for x in r[:]:
               monthStart = prevMonthStart.addmonths(-x) # - x months
               monthStart1 = monthStart.adddays(+15) # + 15 days
               self.RSs[no] = 'rs_historic_' + str(rsNo)
               rsNo -= 3
               self.breakpoints.append(int(monthStart1))
               self.bp.append(str(monthStart1))
               monthStart = monthStart.addmonths(3) # + 3 months
               no=no+1
               self.RSs[no] = 'rs_historic_' +  str(rsNo)
               rsNo -= 3
               self.breakpoints.append(int(monthStart))
               self.bp.append(str(monthStart))
               no=no+1
        self.RSs.pop(no-1)
        #self.bp.pop()
    
    def __str__(self):
        def rsStr(date):
            try:
                return('>= %s => %s\n' % (date, self.getRS(AbsTime(date))))
            except KeyError:
                return('>= %s => KeyError\n' % (date))

        x = 'Breakpoints: %s\n RSs: %s\n' % (self.bp, self.RSs)
        x += rsStr(AbsTime(self.bp[0]).adddays(-1))
        for bp in self.bp:
            x += rsStr(bp)
        return x

    def getRS(self, date):
        return(self.RSs[bisect(self.breakpoints, int(date))])

