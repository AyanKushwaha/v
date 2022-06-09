

"""
SASCMS-2544 / SASCMS-2509

***********************************************************************************
*** NOTE the script SASCMS-2509 contained a bug. This is a corrected version of ***
*** the same script.                                                            ***
*** No accounts handled by Manpower are touched in this modified version.       ***
***********************************************************************************

Recreate entries that were removed by "accumulator" job that failed because of
"memory exhaustion".

The runs that need to be taken into consideration are:

    2010-08-26 faulty accumulation      (22401022)
    2010-09-10 faulty accumulation      (23337690)
    2010-09-10 restore job sascms-2487  (23377958)
    2010-09-15 faulty accumulation      (23674729)


Technique:
    * save all account_entries in mapping
    * iterate for each revid
    * check if correction already there: if True, then remove the correction
      and insert old value and update mapping
"""

import datetime
import adhoc.fixrunner as fixrunner
import utils.dt as dt
from optparse import OptionParser


__version__ = '$Revision$'


revids = 22401022, 23337690, 23674729
skip_accounts = ('F7', 'VA', 'VA1')


class stat:
    """Some counters for statistics."""
    added = 0
    removed = 0
    duplicates = 0


class MyParser(fixrunner.BasicParser):
    """Customized argument handling: add argument 'where'."""
    def __init__(self, *a, **k):
        fixrunner.BasicParser.__init__(self, *a, **k)
        self.add_option('-p', '--printstat',
                dest='printstat',
                action='store_true',
                default=False,
                help='Print full list of operations and some statistics.')
        self.add_option('-w', '--where',
                dest='where',
                default=[],
                help='Optional SQL where expression for testing.')


# Make fixrunner.run use the modified option parser.
fixrunner.set_parser(MyParser)


class ExistingRecord(dict):
    def __init__(self, *a, **k):
        dict.__init__(self, *a, **k)
        self.deleted = False


def makekey(rec):
    """Create key for identifying duplicate entries."""
    return (rec['crew'], rec['account'], rec['tim'], rec['reasoncode'])


def makewhere(cond, w):
    """Add optional 'where' clause to existing condition."""
    if isinstance(w, str):
        cond.append(w)
    else:
        cond.extend(w)
    return cond 


def fix_revid(dc, revid, mapping, handled, where):
    """Repair one revid."""
    ops = []
    w = ['revid = %d' % revid]
    for rec in fixrunner.dbsearch(dc, 'account_entry', makewhere(w, where),
            withDeleted=True):
        if rec['account'] in skip_accounts:
            continue
        key = makekey(rec)
        if key in handled:
            continue
        handled.append(key)
        removals = []
        if key in mapping:
            # similar entries exist
            for faulty in mapping[key]:
                if not faulty.deleted:
                    removals.append(faulty)
                    faulty.deleted = True
        if len(removals) == 1 and faulty['amount'] == rec['amount']:
            # Only one similar record - we are finished
            # one removal + one addition = do nothing
            stat.duplicates += 1
            continue
        # re-create old record
        del rec['deleted']
        ops.append(fixrunner.createop('account_entry', 'W', rec))
        stat.added += 1
        for faulty in removals:
            # remove duplicates
            ops.append(fixrunner.createop('account_entry', 'D', faulty))
            stat.removed += 1
    return ops


def print_ops(ops):
    """Print out operations, one per row, for testing purposes."""
    fmt = '%(crew)s %(account)-8.8s %(reasoncode)-12.12s %(xtim)-16.16s %(amount)8.8s %(rate)5.5s %(id)s %(revid)s'
    def mod_rec(r):
        x = dict(r)
        x['xtim'] = dt.m2dt(x['tim'])
        return x
    for op in ops:
        v = mod_rec(op.values or op.keys)
        print "%-8.8s - %s" % (op.name, fmt % v)


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    """Run through faulty accumulations and try to re-create data."""
    ops = []
    mapping = {}
    handled = []
    w = ["man = 'N'", "tim > %d" % dt.dt2m(datetime.datetime(2010, 1, 1))]
    for rec in fixrunner.dbsearch(dc, 'account_entry', makewhere(w, k['where'])):
        mapping.setdefault(makekey(rec), []).append(ExistingRecord(rec))
    for revid in revids:
        ops.extend(fix_revid(dc, revid, mapping, handled, k['where']))
    if 'where' in k and k['where']:
        print_ops(ops)
        return []
    if 'printstat' in k and k['printstat']:
        print_ops(ops)
        print "added:", stat.added
        print "duplicates:", stat.duplicates
        print "removed:", stat.removed
    return ops


fixit.remark = 'sascms-2544.py (%s): Restoring faulty removals from account_entry.' % __version__


if __name__ == '__main__':
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
