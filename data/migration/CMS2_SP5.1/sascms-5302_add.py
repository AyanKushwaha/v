

"""
SASCMS-5302_add

Recalculate accumulator.
"""

import datetime
import adhoc.fixrunner as fixrunner
import subprocess
import os

def startStudio(start,end):
    carmusr_path = os.environ['CARMUSR']
    environment = dict(os.environ)
    
    command = [carmusr_path + '/bin/studio.sh', '-t', '-d']
    environment["PERIOD_START"] = start
    environment["PERIOD_END"] = end
    environment["PLANNING_AREA"] = "ALL"
    environment["START_SCRIPT"] = "'adhoc.f36_correction'"
    environment["EXTERNAL_PUBLISH_STANDALONE"] = "YES"

    pobj = subprocess.Popen(command, env=environment)
    return_code = pobj.wait()

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    """Calc. F36 account"""
    ops = []
    
    startStudio('01Jan2013','01Jan2014')

    return ops


fixit.remark = 'SASCMS-5302_add'


if __name__ == '__main__':
    fixit()



