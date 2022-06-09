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
    for crew in crew_list:
        for entry in fixrunner.dbsearch(dc, 'accumulator_int', ' AND '.join((
                "name = 'accumulators.blank_days_acc'",
                "acckey = %s" % str(crew[1]),
                "deleted = 'N'",
                "to_char(tim) in ('18758880','18714240')",
                "next_revid = 0",
            ))):
            ops.append(fixrunner.createOp('accumulator_int', 'D', entry))
    return ops


__version__ = '2021-07-16c'
fixit.program = 'reset_delgrant.py (%s)' % __version__

