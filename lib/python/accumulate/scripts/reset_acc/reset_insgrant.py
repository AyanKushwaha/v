from tm import TM
import carmensystems.rave.api as R
from AbsTime import AbsTime
from datetime import datetime
from carmensystems.basics.uuid import uuid
import utils.Names
import Cui
import adhoc.fixrunner as fixrunner

crew_fetch = []
crew_list = []
agmtgrp = 'SKD_CC_AG'
branchid = 1
name = 'accumulators.blank_days_acc'
val1 = 15
tim1 = 18714240
def main():
    acc()
    fixit()

def acc():
    crew_fetch, = R.eval('sp_crew', R.foreach(R.iter('iterators.roster_set', where=('crew.%is_cabin% and crew.%agmt_group_id% = ' + "\""+ str(agmtgrp) + "\"")),'crew.%id%'))
    for crew_id in crew_fetch:
        print "Crew id is " , crew_id
        crew_list.append(crew_id)


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for crew in crew_list:
        ops.append(fixrunner.createOp('accumulator_int', 'N', {'branchid': int(branchid),
                                                            'name': str(name),
                                                            'acckey': str(crew[1]),
                                                            'tim': int(tim1),
                                                            'val': int(val1)}))
    return ops


__version__ = '2021-07-16'
fixit.program = 'reset_insgrant.py (%s)' % __version__

