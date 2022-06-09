

"""
SKS-376

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
    environment["START_SCRIPT"] = "'adhoc.recalcBunkeringAcc'"
    environment["EXTERNAL_PUBLISH_STANDALONE"] = "YES"

    pobj = subprocess.Popen(command, env=environment)
    return_code = pobj.wait()

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    """Run through accumulations and try to recalculate data."""
    ops = []

    dates = [
        ("01Mar2020","31May2020")]

    for start, end in dates:
        print "RECALCULATING: [%s] to [%s]" % (start,end)
        startStudio(start,end)

    return ops


fixit.remark = 'SKS-376'


if __name__ == '__main__':
    fixit()



