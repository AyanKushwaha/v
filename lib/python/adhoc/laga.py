

"""
Re-create some ground tasks that were inadvertently removed by aradiff.

Rewritten to use fixrunner.
"""

import fixrunner
from AbsTime import AbsTime


class MoreOptions(fixrunner.BasicParser):
    def __init__(self, *a, **k):
        fixrunner.BasicParser.__init__(self, *a, **k)
        self.set_usage("%prog [options] revid")

    def parse_args(self, *a, **k):
        opts, args = fixrunner.BasicParser.parse_args(self, *a, **k)
        if not len(args) == 1:
            self.error('needs a revision (revid)')
        return opts, args


fixrunner.set_parser(MoreOptions)


@fixrunner.run
def fixit(dc, revid, **k):
    ops = []
    for gtrec in fixrunner.dbsearch(dc, 'ground_task', "revid = %s AND deleted = 'Y'" % revid, withDeleted=True):
        for cgdrec in fixrunner.dbsearch(dc, 'crew_ground_duty', "task_udor = %d AND task_id = '%s'" % (gtrec['udor'], gtrec['id'])):
            for internal in ('deleted',):
                try:
                    del gtrec[internal]
                except:
                    pass
            gtrec['si'] = 'laga.py'
            ops.append(createOp('ground_task', 'W', gtrec))
            if fixrunner.debug:
                print '-> %s %s' % (gtrec.get('activity'), AbsTime(gtrec.get('udor', 0) * 1440))
            break
    return ops

    
fixit.program = 'laga.py (2009-08-05)'


if __name__ == '__main__':
    fixit()
