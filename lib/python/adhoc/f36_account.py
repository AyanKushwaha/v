import sys
import subprocess
import os
import time
from AbsTime import AbsTime

def main():
    if len(sys.argv) == 1:
        print "Run with argument: "
        print "entitlement - Adds entitled F36 days for CC in upcoming year."
        print "              (Should be run on 01Oct)"
        print "correction  - Add corrections to entitled F36 days and reductions on roster."
        print "              (Should be run on 01Jan,01Apr, 01Jul and 01Oct)"
    else:
        if sys.argv[1] in ["entitlement","correction"]:
            (year,month,day,hours,minutes) = time.localtime()[0:5]
        
            carmusr_path = os.environ['CARMUSR']
            environment = dict(os.environ)
            
            command = [carmusr_path + '/bin/studio.sh', '-t', '-d']

            if sys.argv[1] == 'entitlement':
                pp_start = AbsTime(year,month,day,hours,minutes)
                pp_end = pp_start.adddays(1)
                
                environment["PERIOD_START"] = str(pp_start)[0:9]
                environment["PERIOD_END"] = str(pp_end)[0:9]
                environment["PLANNING_AREA"] = "ALL"
                environment["START_SCRIPT"] = "'adhoc.f36_entitlement'"
            elif sys.argv[1] == 'correction':
                pp_start = AbsTime(year,month,day,hours,minutes)
                pp_end = pp_start.addyears(1).year_floor()
                
                environment["PERIOD_START"] = str(pp_start)[0:9]
                environment["PERIOD_END"] = str(pp_end)[0:9]
                environment["PLANNING_AREA"] = "ALL"
                environment["START_SCRIPT"] = "'adhoc.f36_correction'"

            pobj = subprocess.Popen(command, env=environment)
            return_code = pobj.wait()

            print "####### CONVERSION SCRIPT ENDED #######"
        else:
            print "Invalid argument"


if __name__ == '__main__':
    main()

