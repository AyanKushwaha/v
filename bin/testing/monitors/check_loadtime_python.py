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
        
        #Total: 394.20 s (cpu: 119.40 s)        
        expression =  "Open\sPlan\sTimes:$\s*Total:\s(?P<total_time>[0-9\.]*)\ss\s\(cpu:\s(?P<cpu_time>[0-9\.]*)\s.*"

        dir_list=os.listdir(options.directory)
        
        total_load_time = 0.0
        nof_loads = 0
        longest_load_time = None
        warning_load_time = None
        
        for file in dir_list:
                        
            file_path = os.path.join(options.directory, file)
                        
            # Check if it is a file and the pattern matches
            if not os.path.isfile(file_path) or file_pattern.search(file) is None or \
                time.time() - os.path.getmtime(file_path) > 24*3600:
                continue
            
            nof_checked_files += 1
            searcher = Searcher(file_path, expression)
                    
            refresh_length = None
            refresh_time = None
            
            # We are checking all refresh time, if any is higher than the limit, report error
            for match in searcher:
                total_time = float(match['total_time'])
                cpu_time = float(match['cpu_time']) 

                total_load_time += total_time
                nof_loads += 1

                if longest_load_time is None or total_time > longest_load_time:
                    longest_load_time = total_time
                            
                if  total_time > error_limit:
                    print "CRITICAL: Plan load time is %s s (limit is %f s)" % (total_time, error_limit)
                    sys.exit(common.CRITICAL)
                    
                if  refresh_length > warning_limit:
                    warning_load_time = total_time
                    found_warning = True
        
        if nof_loads > 0:
            average_load_time = "%s s" % (round(total_load_time/nof_loads, 2))
        else:
            average_load_time = "N/A"
            longest_load_time = "N/A"
                    
        if found_warning:
            print "WARNING: Refresh time too long (%s s)" % (warning_load_time)     
            sys.exit(common.OK)
        else:
            print "OK: Checked %d files (longest load %s s, average load %s)" % (nof_checked_files, longest_load_time, average_load_time)
            sys.exit(common.OK)

    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking load times: %s' % e
        sys.exit(common.CRITICAL)
