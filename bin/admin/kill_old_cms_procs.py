#!/usr/bin/python

import os
import sys
import subprocess
import time
import getopt

def main(argv):
    testrun = False

    try:
        opts, args = getopt.getopt(argv,"t",["testrun"])
    except getopt.GetoptError:
        print 'kill_old_cms_procs.py [-t/--testrun]'
        sys.exit(2)
    for opt,arg in opts:
        if opt in ("-t", "--testrun"):
            print 'Will perform a test run'
            testrun = True

    cct_studio = "studio"
    mirador = "mirador"
    java = "java"
    pdf="evince"
    pdl="pdl"

    apps = [cct_studio, mirador, java, pdf, pdl]

    month = time.strftime("%b", time.gmtime())
    months= [' Jan', ' Feb', ' Mar', ' Apr', ' May', ' Jun', ' Jul', ' Aug', ' Sep', ' Oct', ' Nov', ' Dec']
    months.remove(" " + month)
    #print months #for debug purpose

    procs = []
    print "Following processes will be killed: "
    for app in apps:
        for month in months:
            command=['ps', '-ef']
            ps_raw = subprocess.Popen(command, stdout=subprocess.PIPE)

            ps_result = filter(None, ps_raw.stdout.read().split("\n"))

            for row in ps_result:
                if app in row and month in row and 'grep' not in row and 'root' not in row and 'SessionServer' not in row:
                    print "User: "+ row.split()[0] + " running pid: " + row.split()[1] + " from: " + row.split()[4] + " cmd: " + row.split()[7]
                    procs.append(row.split()[1])

    if len(procs) > 0 :
        if testrun:
            for proc in procs:
                print "subprocess.Popen(['kill', '-9', %s]) "% proc # this line is for testing
        else:
            for proc in procs:
                subprocess.Popen(['kill', '-9', str(proc)])
    else:
        print "No old processes found on this host"


if __name__ == '__main__':
	main(sys.argv[1:])
