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
    parser.add_option('-c', '--last_create_time', dest='last_create_time', 
                      help="""Checks if the latest created file matching the pattern is created the last nof minutes stated by this option""")
    parser.add_option('-l', '--error_limit', dest='error_limit', 
                      help="""The minimum nof required files created within the specified time unless error""")
    parser.add_option('-w', '--warning_limit', dest='warning_limit', 
                      help="""The minimum nof required files created within the specified time unless warning""")


    options, args = parser.parse_args()

    # Check for required options
    for option in ('directory', 'file_pattern', 'last_create_time', 'error_limit', 'warning_limit'):
        if not getattr(options, option):
            print 'CRITICAL - %s not specified' % option.capitalize()
            sys.exit(common.CRITICAL)

    try:
    
        file_pattern = re.compile(options.file_pattern)
    
        oldest_valid_time = time.time() - 60*int(options.last_create_time)
        error_limit = int(options.error_limit)
        warning_limit = int(options.warning_limit)          

        dir_list=os.listdir(options.directory)
        
        nof_valid_files = 0
        
        for file in dir_list:
                        
            file_path = os.path.join(options.directory, file)
                        
            # Check if it is a file and the pattern matches
            if not os.path.isfile(file_path) or file_pattern.search(file) is None:
                continue

            if oldest_valid_time < os.path.getctime(file_path):
                nof_valid_files += 1
                
                    
        if nof_valid_files < error_limit:
            print "CRITICAL: Too few valid files. %d expected %d" % (nof_valid_files, error_limit)     
            sys.exit(common.CRITICAL)
        elif nof_valid_files < warning_limit:
            print "WARNING: Too few valid files. %d expected %d" % (nof_valid_files, warning_limit)
            sys.exit(common.WARNING)
        else:
            print "OK: Found %d valid file(s)" % (nof_valid_files)
            sys.exit(common.OK)

    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking file properties: %s' % e
        sys.exit(common.CRITICAL)
