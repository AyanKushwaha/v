import adhoc.fixrunner as fixrunner

crw = 26496 
tim1 = '18714240'
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
            "revid in (179531006)",
            "to_char(tim) =%s" % str(tim1), 
            "next_revid = 0",
        ))):
        entry['val'] = 0
        ops.append(fixrunner.createOp('accumulator_int', 'U', entry))
    return ops


__version__ = '2021-07-16c'
fixit.program = 'reset_revtimgrant.py (%s)' % __version__

main()
