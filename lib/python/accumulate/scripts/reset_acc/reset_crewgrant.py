import adhoc.fixrunner as fixrunner

crw = 26529
def main():
    fixit()

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for entry in fixrunner.dbsearch(dc, 'accumulator_int', ' AND '.join((
            "name = 'accumulators.blank_days_acc'",
            "acckey = %d" % int(crw),
            "deleted = 'N'",
            "next_revid = 0",
        ))):
        entry['val'] = 0
        ops.append(fixrunner.createOp('accumulator_int', 'U', entry))
    return ops


__version__ = '2021-07-16'
fixit.program = 'reset_crewgrant.py (%s)' % __version__

main()
