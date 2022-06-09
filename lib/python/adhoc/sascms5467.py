import sys
from datetime import date
import subprocess
import os

if __name__ == '__main__':
    if len(sys.argv) == 1:
        
        print "Run with argument: "
        print "updateF3 - Conversion of F3 accounts. Applies to CC SKD."
        print "updateF0 - Conversion of F0 accounts. Applies to CC SKD."
        print "reset - Moves F0 balance to F3 account and then resets F0 balance to zero. Applies to CC SKD."
    else:
        if sys.argv[1] in ["updateF3", "updateF0", "reset"]:
            carmusr_path = os.environ['CARMUSR']
            environment = dict(os.environ)
            
            command = [carmusr_path + '/bin/studio.sh', '-t', '-d']
            environment["PERIOD_START"] = '01Jun2013'
            environment["PERIOD_END"] = '30Jun2013'
            environment["PLANNING_AREA"] = "SKD"
            if sys.argv[1] == 'updateF3':
                environment["START_SCRIPT"] = "'adhoc.F3Conversion'"
            elif sys.argv[1] == 'updateF0':
                environment["START_SCRIPT"] = "'adhoc.F0Conversion'"
            elif sys.argv[1] == 'reset':
                environment["START_SCRIPT"] = "'adhoc.F0Reset'"

            pobj = subprocess.Popen(command, env=environment)
            return_code = pobj.wait()

            print "####### CONVERSION SCRIPT ENDED #######"
        else:
            print "Invalid argument"
