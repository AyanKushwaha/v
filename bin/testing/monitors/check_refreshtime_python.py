#!/usr/bin/env python

from optparse import OptionParser
import sys
import time
import os
import re
from datetime import datetime, timedelta
from util.searcher import Searcher
import util.common as common 


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-d', '--dir', dest='directory',
                      help="""Directory to look in""")
    parser.add_option('-p', '--pattern', dest='file_pattern',
                      help="""The pattern for files in the directory that will be searched""")
    parser.add_option('-l', '--error_limit', dest='error_limit', 
                      help="""The maximum load time in seconds allowed before an error is returned""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit', 
                      help="""The maximum load time in seconds allowed before a warning is returned""")


    options, args = parser.parse_args()

    # Check for required options
    for option in ('directory', 'file_pattern','error_limit', 'warning_limit' ):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(common.CRITICAL)

    nof_checked_files = 0
    found_warning = False

    try:
        
        file_pattern = re.compile(options.file_pattern)
        error_limit = float(options.error_limit)
        warning_limit = float(options.warning_limit)
        
        #Thu, 19 Jan 2012 09:10:35 INFO #1326963819 refresh  took 12.696189 secs.
        expression =  "[a-zA-Z]{3},\s(?P<refresh_time>[0-9]+ [a-zA-Z]{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}).*?refresh\s\stook\s(?P<refresh_length>[0-9\.]*)\s.*"

        dir_list=os.listdir(options.directory)
        latest_refresh_time = None
        latest_refresh_length = None
        
        warning_refresh_time = None
        warning_refresh_length = None
        
        for file in dir_list:
                        
            file_path = os.path.join(options.directory, file)
                                    
            # Check if it is a file and the pattern matches
	    timediff = time.time() - os.path.getmtime(file_path)
            if not os.path.isfile(file_path) or file_pattern.search(file) is None or \
                timediff > 24*3600 or timediff < 0:
                continue

            nof_checked_files += 1
                        
            searcher = Searcher(file_path, expression)
                    
            refresh_length = None
            
            # We are checking all refresh time, if any is higher than the limit, report error
            for match in searcher:
                refresh_length = float(match['refresh_length'])
                refresh_time = datetime.strptime(match['refresh_time'], "%d %b %Y %H:%M:%S")

                if latest_refresh_time is None or  refresh_time > latest_refresh_time:
                    latest_refresh_time = refresh_time
                    latest_refresh_length = refresh_length
                                                            
                if  refresh_length > error_limit:
                    print "CRITICAL: Refresh time at %s is %s s (limit is %s s)" % (refresh_time, refresh_length, error_limit)
                    sys.exit(common.CRITICAL)
                                        
                if  refresh_length > warning_limit:
                    warning_refresh_time = refresh_time
                    warning_refresh_length = refresh_length
                    found_warning = True
 
                    
        # We are checking the latest time a refresh was made but only if we found a match
        if latest_refresh_time is not None:
            current_utc_time = datetime.utcnow()
            refresh_period = timedelta(minutes=10)        
        
            if current_utc_time - latest_refresh_time > refresh_period:
                print "CRITICAL: Latest refresh too old %s (now %s)" %(latest_refresh_time ,current_utc_time)
                sys.exit(common.CRITICAL)


        if found_warning:
            print "WARNING: Refresh time too long (refresh at %s to %s s)" % (warning_refresh_time, warning_refresh_length)     
            sys.exit(common.WARNING)
        else:
            print "OK: Checked %d files (latest refresh at %s took %s s)" % (nof_checked_files, latest_refresh_time or "N/A", latest_refresh_length or "N/A")     
            sys.exit(common.OK)


    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking load times: %s' % e
        sys.exit(common.CRITICAL)
