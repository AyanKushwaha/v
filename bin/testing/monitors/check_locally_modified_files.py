#!/usr/bin/env python

from optparse import OptionParser
import sys, os, time
import util.common as common
import subprocess

valid_modified_files = ["etc/users/PROD.xml"]

if __name__ == "__main__":

    try:

        nof_invalid_files = 0

        p = subprocess.Popen(['hg', 'status', '-m'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        for line in p.stdout.readlines():
            if line.startswith("M ") and not line[2:-1] in valid_modified_files:
                nof_invalid_files += 1
 
        retval = p.wait()

        if nof_invalid_files > 0:
            print "WARNING: %u invalid modified files" % (nof_invalid_files)
            sys.exit(common.WARNING)
        else:
            print "OK: No locally modified files"
            sys.exit(common.OK)
            
    except SystemExit:
        raise
    except Exception, e:
        print 'CRITICAL - Error checking lcoally modified files: %s' % e
        sys.exit(common.CRITICAL)
