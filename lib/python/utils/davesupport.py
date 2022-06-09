

"""
Some helpers to make it easier to use DAVE's revision functions and to look at
'forensic' data.
"""

import bisect
import logging
import os
import carmensystems.dig.framework.dave as dig_dave
import utils.dave as dave
import utils.dt as dt

from datetime import datetime, timedelta


# Set up logging ========================================================={{{1
logging.basicConfig()
log = logging.getLogger('utils.davesupport')
log.setLevel(logging.INFO)


# encoding ==============================================================={{{1
# Using datetime, which is better (committs)
encoding = dave.encodings.datetime


# Classes ================================================================{{{1

# DCRunner ---------------------------------------------------------------{{{2
class DCRunner:
    """Decorator to run queries. Opens a new dig connection, runs query, and
    closes connection."""
    def __init__(self, debug=False, commit=False):
        self.debug = debug
        self.commit = commit

    def __call__(self, func, *a, **k):
        """Decorator, func will get a DaveConnection as its first argument."""
        def wrapper(*a, **k):
            try:
                if self.debug:
                    log.setLevel(logging.DEBUG)
                return self.dc_runner(func, os.environ['DB_URL'], os.environ['DB_SCHEMA'], *a, **k)
            except SystemExit, se:
                pass
            except Exception, e:
                raise
                log.error("Exception: %s" % e)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper

    def dc_runner(self, func, connstr, schemastr, *a, **k):
        """Run func, supply 'dc' object as first argument to func."""
        dc = None
        ops = []
        try:
            dc = self.get_dave_connector(func, connstr, schemastr)
            ops = func(dc, *a, **k)
            self.store(ops)
        finally:
            if dc is not None:
                dc.close()
        return ops

    def get_dave_connector(self, func, connstr, schemastr):
        dc = dig_dave.DaveConnector(connstr, schemastr)
        if hasattr(func, 'program'):
            dc.getConnection().setProgram(func.program)
            log.debug("Setting 'cliprogram' to '%s'." % func.program)
        # Get "real values"
        log.debug("Connection: %s, Schema %s" % dc.getConnectionInfo()[:2])
        return dc

    def store(self, ops):
        if not ops:
            log.warning("No operations returned to store.")
            return
        log.info("*** Total %d ops" % len(ops))
        if ops:
            if self.debug:
                for op in ops:
                    print op
            if self.commit:
                commitid = dig_dave.DaveStorer(dc).store(ops, returnCommitId=True) 
                log.info("Saved with commitid = %d" % commitid)
            else:
                log.warning("Not committing!")


# DCRunnerReadOnly -------------------------------------------------------{{{2
class DCRunnerReadOnly(DCRunner):
    """Read-only version of DCRunner."""
    def store(self, ops):
        """Make 'store' a no-op."""
        pass


# Mangler ----------------------------------------------------------------{{{2
class Mangler:
    """Mangle field names of 'dave_revision' to allow other table to have
    column names like 'remark'."""
    def __init__(self, prefix):
        self.prefix = prefix

    def mangle(self, s):
        return self.prefix + s

    def demangle(self, s):
        return s[len(self.prefix):]


# mangle / demangle ------------------------------------------------------{{{2
_mangler = Mangler('dave_revision__')
mangle = _mangler.mangle
demangle = _mangler.demangle


# DaveRevision -----------------------------------------------------------{{{2
class DaveRevision(dict):
    """Definitions for dave_revision record."""

    # Protect columns in dave_revision making it possible to query
    # entity with a column named e.g. 'remark' or 'cliuser'
    fields = ('revid', 'commitid', 'cliprogram', 'clihost', 'cliuser',
            'committs', 'remark')
    translator = (
        (mangle('revid'), 'Int'),
        (mangle('commitid'), 'Int'),
        (mangle('cliprogram'), 'String'),
        (mangle('clihost'), 'String'),
        (mangle('cliuser'), 'String'),
        (mangle('committs'), 'TimeStamp'),
        (mangle('remark'), 'String'),
    )

    def __init__(self, record):
        dict.__init__(self)
        for f in self.fields:
            # remove the "dave_revision__" part
            self[f] = record[mangle(f)]

    def __getattr__(self, k):
        return self[k]

    def __str__(self):
        values = ['%s="%s"' % (n, self[n])  for n in self.fields]
        module = self.__class__.__module__
        name = self.__class__.__name__
        return '<%s.%s %s>' % (module, name, ' '.join(values))


# MetaData ---------------------------------------------------------------{{{2
class MetaData:
    """Keep revid as keys."""
    def __init__(self):
        self.revids = {}
        self.commitids = {}

    def revisions(self, commitid=False):
        """Return list of revid's or if 'commitid' is True, return list of
        commitid's."""
        if commitid:
            return sorted(self.commitids)
        else:
            return sorted(self.revids)

    def get_commitid(self, t):
        """Return last commitid at time 't'."""
        try:
            return max([c for c in self.commitids if self.commitids[c].committs <= t])
        except ValueError:
            return 0

    def get_revdata(self, rev, commitid=False):
        if commitid:
            return self.commitids[rev]
        else:
            return self.revids[rev]

    def update(self, record):
        rid = record[mangle('revid')]
        cid = record[mangle('commitid')]
        dr = None
        if not rid in self.revids:
            dr = DaveRevision(record)
            self.revids[rid] = dr
        if not cid in self.commitids:
            if dr is None:
                dr = DaveRevision(record)
            self.commitids[cid] = dr


# QueryMaker -------------------------------------------------------------{{{2
class QueryMaker:
    """Create SQL query."""
    basic_query = ('SELECT a.*, b.*'
        ' FROM dave_revision a, %s b'
        ' WHERE a.revid = b.revid')

    def __call__(self, table, where_expr=None):
        """Create SQL select statement."""
        q = [self.basic_query % table]
        if where_expr is not None:
            q.append(' AND %s' % where_expr)
        q.append(' ORDER BY commitid')
        return ''.join(q)


# EntityTraverser --------------------------------------------------------{{{2
class EntityTraverser:
    """Walk through a result set (Level 1 connection). A number of different
    iterators makes it possible to recreate view at a certain time."""
    def __init__(self, dc, table, where_expr=None, qmaker=QueryMaker()):
        self.metadata, self.data = run_query(dc, table, qmaker(table, where_expr))

    def revisions(self, commitid=False):
        """Return list of revids. If 'commitid' is True, then instead return
        list of commmitid's."""
        return self.metadata.revisions(commitid)

    def get_revdata(self, rev, commitid=False):
        return self.metadata.get_revdata(rev, commitid)

    def get_commitid(self, t):
        return self.metadata.get_commitid(t)

    def __iter__(self):
        """Return unfiltered list of all records satisfying query."""
        for keys in sorted(self.data):
            for rec in self.data[keys]:
                yield rec

    def changes_to_prev(self, revid):
        """I'm not sure about this code... Possibly I got things wrong on this
        one, so beware. I don't understand the 'prev_revid' thing at all."""
        added = []
        changed = []
        deleted = []
        for keys in sorted(self.data):
            for rev in self.data[keys]:
                if rev.revid == revid:
                    if rev.deleted == 'Y':
                        deleted.append(rev)
                    elif rev.prev_revid == rev.next_revid and rev.prev_revid != 0:
                        pass
                    elif rev.prev_revid == 0 or rev.revid < rev.prev_revid:
                        added.append(rev)
                    else:
                        changed.append(rev)
        return added, changed, deleted

    def rev_iter(self, rev, commitid=False, with_deleted=False):
        """Return list of entries, as they would have been at an earlier point
        in time. If commitid is True, use commitid as filter, otherwise use
        'revid'."""
        if commitid:
            f = mangle('commitid')
        else:
            f = mangle('revid')
        for keys in sorted(self.data):
            ix = bisect.bisect([x[f] for x in self.data[keys]], rev)
            rec = self.data[keys][ix - 1]
            if rec[f] <= rev and (with_deleted or rec.deleted == 'N'):
                yield rec

    def time_iter(self, timepoint, with_deleted=False):
        """Iterate table, as it was at 'timepoint'. If timepoint is not a
        'datetime' object, then use AbsTime instead."""
        if isinstance(timepoint, datetime):
            t = timepoint
        else:
            t = dt.m2dt(timepoint)
        cid = self.get_commitid(t)
        return self.rev_iter(cid, commitid=True, with_deleted=with_deleted)

    def latest_iter(self, with_deleted=False):
        """Should yield same result as iteration over EntityConnection."""
        for keys in sorted(self.data):
            for rec in self.data[keys]:
                if rec['next_revid'] == 0 and (with_deleted or rec.deleted == 'N'):
                    yield rec


# functions =============================================================={{{1

# run_query --------------------------------------------------------------{{{2
def run_query(dc, table, query):
    """Return tuple (metadata, data) from query on table."""
    metadata = MetaData()
    data = {}
    ec = dc.getConnection()
    espec = ec.getEntitySpec(table)
    keymaker = dave.KeyMaker(espec, encoding=encoding)
    translator = list(DaveRevision.translator)
    for ix in xrange(espec.getColumnCount()):
        col = espec.getColumnByNum(ix)
        translator.append((col.getName(), dave.api_types[col.getApiType()]))

    # put in prev_revid, next_revid after revid and deleted
    insertion_point = len(DaveRevision.translator) + 2
    translator[insertion_point:insertion_point] = [
        ('prev_revid', 'Int'),
        ('next_revid', 'Int'),
    ]

    l1 = dave.L1(dc.getL1Connection(), translator, encoding=encoding)
    for record in l1.search(query):
        metadata.update(record)
        keys = tuple(keymaker.map2key(record).valuesAsList())
        if keys in data:
            data[keys].append(record)
        else:
            data[keys] = [record]
    return metadata, data


# show_published_roster --------------------------------------------------{{{2
def show_published_roster(dc, crew, pubtype, interval=None):
    """Show how published_roster has been changed for a crew member."""
    query = [
        "crew = '%s'" % crew,
        "pubtype = '%s'" % pubtype,
    ]
    if interval is not None:
        query.extend([
            'pubend >= %d' % int(interval.first),
            'pubstart <= %d' % int(interval.last),
        ])
    return EntityTraverser(dc, 'published_roster', ' and '.join(query))


# creatop ----------------------------------------------------------------{{{2
createop = dig_dave.createOp


# dbsearch ---------------------------------------------------------------{{{2
def dbsearch(dc, entity, expr=[], withDeleted=False):
    """Search entity and return list of objects."""
    if isinstance(expr, str):
        expr = [expr]
    return list(dc.runSearch(dig_dave.DaveSearch(entity, expr, withDeleted)))


# run --------------------------------------------------------------------{{{2
def run(commit=False, debug=False, readonly=False):
    """Return suitable decorator."""
    def decorator(func):
        if readonly:
            f = DCRunnerReadOnly(debug=debug, commit=commit)
        else:
            f = DCRunner(debug=debug, commit=commit)
        return f(func)
    return decorator


# bit --------------------------------------------------------------------{{{2
@run(debug=True, readonly=True)
def bit(dc, table, where_expr, *a, **k):
    """Built-in-test. Just a test to show how the stuff works."""
    et = EntityTraverser(dc, table, where_expr)
    print 
    print "commitid", et.get_commitid(datetime(2009, 6, 24)) # NB! AbsTime if using that encoding!
    for x in et:
        print x.revid, x.activity, x.st, x.et, x.deleted, x.prev_revid, x.next_revid
    for rev in et.revisions():
        print "---"
        print "revision : %(committs)s by %(cliuser)s (%(remark)s)" % et.get_revdata(rev)
        chg_fmt = "   - %(revid)08d %(activity)-5.5s %(st)s %(et)s"
        a, c, d = et.changes_to_prev(rev)
        if a:
            print " - added:"
            for aa in a:
                print chg_fmt % aa
        if c:
            print " - changed:"
            for cc in c:
                print chg_fmt % cc
        if d:
            print " - deleted:"
            for dd in d:
                print chg_fmt % dd
        for rec in et.rev_iter(rev):
            print "%(revid)08d %(activity)-5.5s %(st)s %(et)s" % rec 
    print 
    et = show_published_roster(dc, '34353', 'PUBLISHED')
    print "revisions", et.revisions()
    for rev in et.revisions():
        print "rev", et.get_revdata(rev)
        for x in et.rev_iter(rev):
            revdata = et.get_revdata(x.revid)
            print x.pubstart, x.pubend, revdata.cliuser, revdata.remark
    print ">> (at 2009-08-01)"
    for x in et.time_iter(datetime(2009, 8, 1)):
        print x.pubcid, x.pubstart, x.pubend, x[mangle('committs')], 'next_revid', x.next_revid

    print ">> (latest)"
    for x in et.latest_iter():
        print x.pubcid, x.pubstart, x.pubend, x[mangle('committs')], 'next_revid', x.next_revid


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    from AbsTime import AbsTime
    print "connect=(%s), schema=(%s)" % (os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    bit('crew_activity', "crew = '34353' and st > %s" % int(AbsTime(2009, 6, 1, 0, 0)))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
