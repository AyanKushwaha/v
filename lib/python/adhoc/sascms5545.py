import sys
from datetime import date
import subprocess
import os

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Run with argument: "
        print "CCF7S - Add F7S to account for CC."
    else:
        if sys.argv[1] in ["CCF7S"]:
            carmusr_path = os.environ['CARMUSR']
            environment = dict(os.environ)

            command = [carmusr_path + '/bin/studio.sh', '-t', '-d']
            environment["PERIOD_START"] = '01Jan2013'
            environment["PERIOD_END"] = '01Mar2013'
            environment["PLANNING_AREA"] = "ALL"
            environment["START_SCRIPT"] = "'adhoc.sascms5545_script'"

            pobj = subprocess.Popen(command, env=environment)
            return_code = pobj.wait()

            print "####### SCRIPT ENDED #######"
        else:
            print "Invalid argument"
