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
    tim1 = 18669600
    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2021, 7, 1).strftime(format)
    tim2 = AbsTime(ae_tim[:15])
    print(tim2)
    for crew in crew_list:
        for entry in fixrunner.dbsearch(dc, 'accumulator_int', ' AND '.join((
                "name = 'accumulators.blank_days_acc'",
                "acckey = %s" % str(crew[1]),
                "deleted = 'N'",
                "to_char(tim) = %s" % str(tim1),
                "next_revid = 0",
            ))):
            entry['val'] = 0
            ops.append(fixrunner.createOp('accumulator_int', 'U', entry))
    return ops


__version__ = '2021-07-16b'
fixit.program = 'reaccumulate_updgrant.py (%s)' % __version__
