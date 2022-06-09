#!/bin/env python

# [acosta:06/345@11:08] Extended to accept input from stdin as well.

import sys, getopt, AbsTime, traceback


__all__ = ['main', 'split']

# UsageException ---------------------------------------------------------{{{2
class UsageException(RuntimeError):
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# main ==================================================================={{{1
def main(*argv, **kwds):
    """
    araSplit ($Revision$)

usage:
    araSplit.py [-m month] file

    or

    araSplit.py --help


arguments:

    -m month        Split file in month months per file, default 1 month per file.
    --month=month

    file            Filename, if file is '-' then input is taken
                    from stdin.

    """

    if len(argv) == 0:
        argv = sys.argv[1:]
    try:
        try:
            optlist, params = getopt.getopt(argv, 'm:',
                    [
                        "help",
                        "month=",
                    ]
            )
        except getopt.GetoptError, msg:
            raise UsageException(msg)
        k = {}
        for (opt, value) in optlist:
            if opt == '--help':
                print main.__doc__
                return 0
            elif opt in ('-m', '--month'):
                k['month'] = int(value)
            else:
                pass
        kwds.update(k)
        _split(*params, **kwds)
    except UsageException, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except Exception, err:
        traceback.print_exc()
        print >>sys.stderr, err
        return 22

## This small function works if the time format is of the format YYYY-MM-DD.
def parseTime(time_string):
    return (int(time_string[:4]),
            int(time_string[5:7]),
            int(time_string[8:10]),
            0, 0)

def parseTimeZulu(time_string):
    return (int(time_string[:4]),
            int(time_string[5:7]),
            int(time_string[8:10]),
            int(time_string[11:13]),
            int(time_string[14:16]))
            
def _split(filename, month=1):

    if len(filename) < 1:
        raise UsageException('ERROR: No file specified')

    try:
        if filename == '-':
            data = ''.join(sys.stdin.readlines())
        else:
            f = open(filename)
            for line in f:
                #print "Data read %s" % (line)
                if line.startswith("<araxml"):
                   #print "Data read %s" % (line)
                   words = line.split()
                   #print words
                   ara, vers, periodstart, periodend = words
                   ps = periodstart[14:24]
                   pe = periodend[12:22]
                   print "Periodstart %s, Periodend %s" % (ps, pe)
                   sd = parseTime(ps)
                   ed = parseTime(pe)
                   start = AbsTime.AbsTime(*sd)
                   end = AbsTime.AbsTime(*ed)
                   tstart = AbsTime.AbsTime(start)
                   tend = AbsTime.AbsTime(start)
                   tend = tend.addmonths(month,AbsTime.PREV_VALID_DAY)
                   tend = tend.adddays(-1)
                   f.close()

                   begining_of_time = AbsTime.AbsTime("1Jan1986 00:00")
                   # So that we don't cut of the start of some of the earlier activities
                   doSplit(filename, ara, vers, begining_of_time, tstart.adddays(-1))
                   
                   while tend < end:
                       #print 'doSplit(%s, %s, %s, %s)' % (ara, vers, tstart, tend)
                       doSplit(filename, ara, vers, tstart, tend)
                       tstart = tstart.addmonths(month,AbsTime.PREV_VALID_DAY)
                       tend = AbsTime.AbsTime(tstart)
                       tend = tend.addmonths(month, AbsTime.PREV_VALID_DAY)
                       tend = tend.adddays(-1)
                   #print 'doSplit(%s, %s, %s, %s)' % (ara, vers, tstart, end)
                   doSplit(filename, ara, vers, tstart, end)
                   break

        print "File is split"
        print "Splitting is done at 00:00 UTC time, run a crew_activity merger after import to database"
        print "If not done, activities will not start/end at 00:00 localtime when being split"
    except Exception, e:
        traceback.print_exc()

        print >>sys.stderr, str(e)
        sys.exit(2)


def split_respect_quotes( data, splitval=" "):
    """
    This function returns a list of arguments in data, but ignoring
    the splitval token when it is found within single quotes.
    
    For instances, it allows "cast 'magic missile' 'big ogre'" to
    be returned as three arguments.  cast, 'magic missile' and 'big ogre'
    """
    tmp = []
    buffer = ""
    quotes = 0
    for counter in range(0, len(data)):
        if data[counter] == '"':
            quotes = (quotes + 1) % 2
        elif quotes == 0 and data[counter] == splitval:
            tmp.append(buffer)
            buffer = ""
        else:
            buffer = buffer + data[counter]
    tmp.append(buffer)
    return tmp



def doSplit(fn, ara, vers, start, end):
    f = open(fn)
    print "Split: %s - %s" % (start, end)
    newFn = fn + "_" + start.yyyymmdd()[:8] + "_" + end.yyyymmdd()[:8]
    of = open(newFn, "w")
    syear,smonth,sday,sh,sm = start.split();
    eyear,emonth,eday,eh,em = end.split();
    for line in f:
        if line.startswith("<araxml"):
            of.write('%s %s period_start="%s-%02d-%02d" period_end="%s-%02d-%02d"><crew_list>\n' % (ara, vers, syear, smonth, sday, eyear, emonth, eday))
        elif line.startswith("<flight_leg_list"):
            of.write('<flight_leg_list period_start="%s-%02d-%02d" period_end="%s-%02d-%02d">\n' % (syear, smonth, sday, eyear, emonth, eday))
        elif line.startswith("<rotation_list"):
            of.write('<rotation_list period_start="%s-%02d-%02d" period_end="%s-%02d-%02d">\n' % (syear, smonth, sday, eyear, emonth, eday))
        elif line.startswith("<aircraft_assignments"):
            of.write('<aircraft_assignments period_start="%s-%02d-%02d" period_end="%s-%02d-%02d">\n' % (syear, smonth, sday, eyear, emonth, eday))
#        elif line.startswith("<ground_task_list"):
#            of.write('<ground_task_list period_start="%s-%02d-%02d" period_end="%s-%02d-%02d">\n' % (syear, smonth, sday, eyear, emonth, eday))
        elif line.strip().startswith("<rotation node_id"):
            words = split_respect_quotes(line)#line.split()
            udor = words[2][5:16]
#            print "\t\twords[2]: %s, words[2][5:16]: %s" % (words[2],words[2][5:16] )
#            print "start: %s udor: %s end: %s" % (start, udor, end)
            sd = parseTime(udor)
            sudor = AbsTime.AbsTime(*sd)
            if start <= sudor and end >= sudor:
                of.write(line)
        elif line.strip().startswith("<aircraft_flight_duty"):
            words = split_respect_quotes(line)#line.split()
            udor = words[3][14:24]
#            print "start: %s udor: %s end: %s" % (start, udor, end)
            sd = parseTime(udor)
            sudor = AbsTime.AbsTime(*sd)
            if start <= sudor and end >= sudor:
                of.write(line)                
        elif line.strip().startswith("<flight_leg node_id"):
            words = line.split()
            udor = words[2][6:16]
            #print "start: %s udor: %s end: %s" % (start, udor, end)
            sd = parseTime(udor)
            sudor = AbsTime.AbsTime(*sd)
            if start <= sudor and end >= sudor:
                of.write(line)
#<crew_flight_duty  crew_node_id="C+10033"  leg_node_id="F+2007-06-03+SK+000945++ARN" pos="AS" />
        elif line.strip().startswith("<crew_flight_duty "):
            words = line.split()
            date = words[2][15:25]
            #print "start: %s udor: %s end: %s" % (start, udor, end)
            sd = parseTime(date)
            sdate = AbsTime.AbsTime(*sd)
            if start <= sdate and end >= sdate:
                of.write(line)
#<crew_activity node_id="A+C+10033+F7S+2007-06-21T22:00Z+ARN" crew_node_id="C+10033" activity="F7S" st="2007-06-21T22:00Z" et="2007-06-23T22:00Z" adep="ARN" ades="ARN" />
        elif line.strip().startswith("<crew_activity "):
            words = line.split()
            date = words[4][4:-2]
            enddate = words[5][4:-2]
            sd = parseTimeZulu(date)
            ed = parseTimeZulu(enddate)
            sdate = AbsTime.AbsTime(*sd)
            edate = AbsTime.AbsTime(*ed)
            utcend = AbsTime.AbsTime(end)
            utcend = utcend.adddays(1)
            utcstart = AbsTime.AbsTime(start)
            utcstart = utcstart.adddays(-1)
            # To avoid overlapping crew activities
            # Change start for activities starting outside but ending in split period 
            if start < edate and edate <= utcend and sdate < start:
                myline = words[0] + ' ' + words[1] + ' ' + words[2] + ' ' + words[3] + ' '
                myline += ' st="%s-%02d-%02d%s ' % (start.split()[:3] + ('T00:00Z"',)) + words[5] + ' ' + words[6] + ' ' + words[7] + ' />\n'
                of.write(myline)
            # Change endtime to fit in current split period
            elif start <= sdate and sdate < utcend and edate > utcend:
                myline = words[0] + ' ' + words[1] + ' ' + words[2] + ' ' + words[3] + ' ' + words[4]
                myline += ' et="%s-%02d-%02d%s ' % (utcend.split()[:3] + ('T00:00Z"',)) + words[6] + ' ' + words[7] + ' />\n' 
                of.write(myline)
            # Change start and endtime if we extend over start and end for split period
            elif start > sdate and sdate < utcend and edate > utcend:
                myline = words[0] + ' ' + words[1] + ' ' + words[2] + ' ' + words[3] + ' '
                myline += ' st="%s-%02d-%02d%s ' % (start.split()[:3] + ('T00:00Z"',))
                myline += ' et="%s-%02d-%02d%s ' % (utcend.split()[:3] + ('T00:00Z"',)) + ' ' + words[6] + ' ' + words[7] + ' />\n'
                of.write(myline)
            # Change nothing if activity is completly in the split period
            elif start <= sdate and edate <= utcend and sdate < utcend:
                of.write(line)
        else:
            of.write(line)

    f.close()
    of.close()

if __name__ == "__main__":
    sys.exit(main())


