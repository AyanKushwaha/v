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
                      help="""The minimum numbers of alerts allowed before an error is returned""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit', 
                      help="""The minimum numbers of alerts allowed before a warning is returned""")
    parser.add_option('-t', '--hours_back', dest='hours_back', type='int',
                      help="""The number of hours back to look""")    

    options, args = parser.parse_args()
    
    for option in ('error_limit', 'warning_limit', 'hours_back', 'dburl', 'schema'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(common.CRITICAL)

    try:
        from_time = int(AbsTime(strftime('%Y%02m%02d %02H:%02M', localtime(time()-options.hours_back*3600))))*60        
            
        #Number of created or update alerts
        statement = "select count(*) from track_alert where deleted != 'Y' and revid > (select min(revid) from dave_revision where committs > %u)" % (from_time)
        nof_alerts = int(common.SQL(statement, options.dburl, options.schema)[0][0])
        
        if nof_alerts < int(options.error_limit):
            print "CRITICAL - Only %u alerts were generated" % (nof_alerts)            
            sys.exit(common.CRITICAL)
        elif nof_alerts < int(options.warning_limit):
            print "WARNING - Only %u alerts were generated" % (nof_alerts)            
            sys.exit(common.WARNING)
        else:
            print "OK - %u alerts were generated" % (nof_alerts)
            sys.exit(common.OK)
            
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking alert generator: %s' % e
        sys.exit(common.CRITICAL)
