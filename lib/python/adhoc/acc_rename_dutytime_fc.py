"""
Repair database after rename of accumulator
accumulators.duty_time_fc_skn_vg_acc
to
accumulators.duty_time_fc_skn_skd_vg_acc
"""

import fixrunner
from carmensystems.dig.framework.dave import DaveSearch


def dbsearch(dc, entity, expr=[], withDeleted=False):
    """Search entity and return list of DCRecord objects."""
    if isinstance(expr, str):
        expr = [expr]
    return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))

@fixrunner.run
def fixit(dc, *a, **k):
    done = False
    repl = []
    repct = 0
    table = 'accumulator_rel'
    exists = {}
    for modaccum in dbsearch(dc, table, "deleted = 'N' AND next_revid = 0 AND name='accumulators.duty_time_fc_skn_skd_vg_acc'"):
        exists[str((modaccum['acckey'], modaccum['tim']))] = 1
    for accum in dbsearch(dc, table, " ".join((
            "deleted = 'N'",
            "AND name = 'accumulators.duty_time_fc_skn_vg_acc'",
        ))):
        repct += 1;
        repl.append(fixrunner.createOp(table, 'D', accum))
        if exists.has_key(str((accum['acckey'], accum['tim']))):
            print "Dup rec, skipping", accum['acckey'], accum['tim']
        else:
            newaccum = accum.copy()
            newaccum['name'] = 'accumulators.duty_time_fc_skn_skd_vg_acc'
            repl.append(fixrunner.createOp(table, 'N', newaccum))

    print "Will replace %d" % repct
    return repl


fixit.program = 'acc_rename_dutytime_fc.py'

if __name__ == '__main__':
    fixit()

