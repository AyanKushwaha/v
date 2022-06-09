#!/usr/bin/python
import random
import subprocess
import time
import os

def get_area():
    areas = ['ALL',
             'SKD',
             'SKN',
             'SKS',
             'SKI']
    random.shuffle(areas)
    return areas[0]

def get_dates():
    dates = [('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),
             ('1Jan2012', '31Jan2012'),

             ('1Dec2011', '31Jan2012'),
             ('1Dec2011', '31Jan2012'),
             ('1Dec2011', '31Jan2012'),


             ('1Nov2011', '28Feb2012'),
             ('1Oct2011', '30Dec2012'),
             ('1Dec2011', '31Mar2012')]
    random.shuffle(dates)
    return dates[0]


carmusr_path = os.environ['CARMUSR']
environment = dict(os.environ)
while(True):
    #print 'bin/runPlanningScripts.sh', get_plan(), 'NOP', get_date(), get_area()
    command = [carmusr_path + '/bin/studio.sh', '-t', '-d']
    start, end = get_dates()
    environment["PERIOD_START"] = start
    environment["PERIOD_END"] = end
    environment["PLANNING_AREA"] = get_area()
    environment["CARMUSR_PERFORMANCE_TWEAK_TEST"] = "1"

    print command
    subprocess.Popen(command, env=environment)
    time.sleep(15)
