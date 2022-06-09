#!/usr/bin/env python

from optparse import OptionParser
from time import strftime, time, localtime
import sys, os
from AbsTime import AbsTime
import util.common as common

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-u', '--dburl', dest='dburl',
                      help="""DB URL""")
    parser.add_option('-s', '--schema', dest='schema',
                      help="""DB schema""")
    parser.add_option('-e', '--error_limit', dest='error_limit', 
                      help="""The minimum number of bookings allowed before an error is returned""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit', 
                      help="""The minimum number of booking allowed before a warning is returned""")
    parser.add_option('-t', '--hours_back', dest='hours_back', type='int',
                      help="""The number of hours back to look""")

    options, args = parser.parse_args()
    
    for option in ('error_limit', 'warning_limit', 'hours_back', 'dburl', 'schema'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(common.CRITICAL)

    try:
        from_time = int(AbsTime(strftime('%Y%02m%02d %02H:%02M', localtime(time()-options.hours_back*3600))))*60        
            
        #Number of hotel bookings
        statement = "select count(*) from hotel_booking where revid > (select min(revid) from dave_revision where committs > %u)" % (from_time)
        nof_created_hbookings = int(common.SQL(statement, options.dburl, options.schema)[0][0])
    
        #Number of transport bookings
        statement = "select count(*) from transport_booking where revid > (select min(revid) from dave_revision where committs > %u)" % (from_time)
        nof_created_tbookings = int(common.SQL(statement, options.dburl, options.schema)[0][0])
    
        if nof_created_tbookings < int(options.error_limit) or nof_created_hbookings < int(options.error_limit):
            print "CRITICAL - Only %u hotel and %u tranport bookings" % (nof_created_hbookings, nof_created_tbookings)            
            sys.exit(common.CRITICAL)
        elif nof_created_tbookings < int(options.warning_limit) or nof_created_hbookings < int(options.warning_limit):
            print "WARNING - Only %u hotel and %u tranport bookings" % (nof_created_hbookings, nof_created_tbookings)            
            sys.exit(common.WARNING)
        else:
            print "OK - %u hotel and %u tranport bookings" % (nof_created_hbookings, nof_created_tbookings)
            sys.exit(common.OK)
            
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error when checking bookings: %s' % e
        sys.exit(common.CRITICAL)
