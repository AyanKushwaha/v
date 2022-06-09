#!/usr/bin/python
# Calculations for determining if crew will get an subq fdp extension needs to check
# check-in time of FC. This is not available when doing roster publish for CC.
# This script will run after FD and CC has been published to check if we need to remove
# fdp extension flags which were incorrectly set at roster publish.

from datetime import date
import subprocess
import os

carmusr_path = os.environ['CARMUSR']
environment = dict(os.environ)

today = date.today()
year = today.year
month = today.month

start_period = date(year,month+1,01).strftime('%d%b%Y')

if month+2<13:
        end_period = date(year,month+2,01).strftime('%d%b%Y')
else:
        end_period = date(year+1,month-10,01).strftime('%d%b%Y')


print "Checking FDP extension flags for period: ", start_period, " - ", end_period

command = [carmusr_path + '/bin/studio.sh', '-t', '-d']
environment["PERIOD_START"] = start_period
environment["PERIOD_END"] = end_period
environment["PLANNING_AREA"] = "ALL"
environment["START_SCRIPT"] = "'adhoc.remove_incorrect_fdp_extension_flags'"

pobj = subprocess.Popen(command, env=environment)
return_code = pobj.wait()

