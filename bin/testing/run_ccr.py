#!/usr/bin/python
import random
import subprocess
import time
import os

def get_area():
    areas = ['ALL_FD',
             'ALL_CC',
             'FD_SKN',
             'CC_SKN',
             'CC_SKS',
             'CC_AL',
             'CC_SKD',
             'CC_ASIA',
             'FD_SKI',
             'FD_SKD_A2',
             'FD_SKD_CJ',
             'FD_SKD_M8',
             'FD_SKS_M8',
             'FD_SKS_B737',
             'FD_SKN_B737',
             'FD_SKN_F5']
    random.shuffle(areas)
    return areas[0]

def get_date():
    dates = ['1Nov2011',
             '1Dec2011',
             '1Jan2012',
             '1Feb2012',
             '1Mar2012']
    random.shuffle(dates)
    return dates[0]
    
def get_plan():
    return 'Database/Production/cms_production/cms_production'
#    return 'TestPlans/Tracking/sk_cms2_dev/sk_cms2_dev'


carmusr_path = os.environ['CARMUSR']

while(True):
    #print 'bin/runPlanningScripts.sh', get_plan(), 'NOP', get_date(), get_area()
    command = [carmusr_path + '/bin/runPlanningScripts.sh', get_plan(), 'NOP', get_date(), get_area()]
    print command
    subprocess.Popen(command)
    time.sleep(8)
