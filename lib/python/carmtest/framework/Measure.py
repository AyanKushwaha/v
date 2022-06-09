'''
Various performance counters that are associated with each test.

All functions defined in this module that does not start with an
underscore (_) will be added as performance counters to each test.

Created on Feb 11, 2010

@author: rickard
'''

import os
import subprocess
import time


def REAL_TIME():
    "Real time"
    return time.time()

def CPU_TIME():
    "CPU time"
    return time.clock()

def RESIDENT_STORAGE_SIZE():
    "Resident storage size"
    return _getmem("rss")

def FREE_MEM():
    "Free physical memory"
    return _getfree(0)

def FREE_SWAP():
    "Free physical+swap memory"
    return _getfree(2)

def _getmem(s):
    try:
        p = subprocess.Popen("ps -p %d -o %s " % ( os.getpid(),s ), shell="False", stdout=subprocess.PIPE)
        return int(p.stdout.readlines()[1])/1024
    except:
        return 0
        
def _getfree(opt):
    try:
        # use the 'free' command to determine the available system memory
        # unit = MB
        x = subprocess.Popen("free -m", shell="False", stdout=subprocess.PIPE).stdout.readlines()
        mem = int(x[1].split()[3])
        withbuff = int(x[2].split()[3])
        if opt & 2:
            swap = int(x[3].split()[3])
            opt &= 1
        else:
            swap = 0
        if opt == 0:
            return withbuff + swap
        if opt == 1:
            return mem + swap
        return 0
    except:
        return 0