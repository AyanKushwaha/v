

"""
SASCMS-1639
Changes all entities in bid_leave_activity with status AUTOMATIC to MANUAL
Date argument restricts the latest vacation start to consider
"""

import adhoc.fixrunner as fixrunner
import AbsTime
import os
import time
__version__ = '$Revision$'



@fixrunner.run
def fixit(dc, date, *a, **k):
    
    MANUAL='MANUAL'
    endtime = int(AbsTime.AbsTime(date))
    logtime=time.strftime('%Y%m%d.%H%M.%S')
    file = open(os.getenv('CARMTMP', '.')+"/sascms-1639."+logtime, "w")
    ops = []
    app=[]
    for entry in fixrunner.dbsearch(dc, 'bid_leave_activity', ' AND '.join((
            "status = 'AUTOMATIC'",
            "act_st <= "+str(endtime),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        file.write("+".join((str(AbsTime.AbsTime(entry['act_st'])),
                             str(entry['act_crew']),
                             str(entry['act_activity'])))+'\n')
        entry['status'] = MANUAL
        ops.append(fixrunner.createOp('bid_leave_activity', 'U', entry))

    file.close()
    return ops


fixit.remark = 'SASCMS-1639 (%s)' % __version__


if __name__ == '__main__':
    import sys
    fixit(sys.argv[-1])
