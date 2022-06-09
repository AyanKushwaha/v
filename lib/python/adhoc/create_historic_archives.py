#!/usr/bin/python
import random
import subprocess
import time
import os

carmusr_path = os.environ['CARMUSR']
environment = dict(os.environ)

periods = [("1Oct2011", "31Oct2011"),
           ("1Nov2011", "30Nov2011"),
           ("1Dec2011", "31Dec2011"),
           ("1Jan2012", "31Jan2012"),
           ("1Feb2012", "29Feb2012"),
           ("1Mar2012", "31Mar2012"),
           ("1Apr2012", "30Apr2012"),
           ("1May2012", "31May2012"),
           ("1Jun2012", "30Jun2012"),
           ("1Jul2012", "31Jul2012"),
           ("1Aug2012", "31Aug2012"),
           ("1Sep2012", "30Sep2012"),
           ("1Oct2012", "31Oct2012")]

for (start, end) in periods:
        
    command = [carmusr_path + '/bin/studio.sh', '-t',  '-d']
    environment["PERIOD_START"] = start
    environment["PERIOD_END"] = end
    environment["PLANNING_AREA"] = "ALL"
    environment["START_SCRIPT"] = "'adhoc.archive_crewlists'"

    print "Updating period %s to %s" % (start, end)
    
    pobj = subprocess.Popen(command, env=environment)
    return_code = pobj.wait()
    
    
    
    
