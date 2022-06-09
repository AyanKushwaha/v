
# [acosta:09/212@13:19] 

"""
Generic "quick-n'-dirty" help "frame-work".'

To use this create a function, that at least takes one argument and returns a
list of Dave operations. See sample code at bottom of this file.

The Python module that contains the fix can then be run like this:

$ CARMUSR=/opt/Carmen/CARMUSR/PROD python my_fix.py [-d] [-n]
"""

__version__ = '$Revision$'
__all__ = ['createop', 'dbsearch', 'log', 'run']


# imports ================================================================{{{1
import logging
import os
import subprocess
import sys
import traceback
from optparse import OptionParser
from tempfile import mkstemp


# Shell script ==========================================================={{{1
# Set up basic Carmen environment
shell_script = """#!/bin/sh
. $CARMUSR/etc/carmenv.sh
$CARMSYS/bin/carmpython ${1+"$@"}
"""


# Run with carmpython ===================================================={{{1
try:
    from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer
except:
    # Probably not running with carmpython
    if sys.executable.startswith('/opt/Carmen'):
        raise Exception("Cannot even start with 'carmpython', check your installation!")
    try:
        os.environ['CARMUSR']
    except:
        raise Exception("Environment CARMUSR must be set.")
    # Create small shell script and re-run the lot, but now with 'carmpython'
    fd, fn = mkstemp(suffix='.sh', prefix='fixrunner_', dir='/tmp', text=True)
    try:
        f = os.fdopen(fd, 'w')
        f.write(shell_script)
        f.close()
        os.chmod(fn, 0700)
        p = subprocess.Popen(['/bin/sh', fn] + sys.argv)
        os.waitpid(p.pid, 0)
    finally:
        os.unlink(fn)
    sys.exit()


# Set up logging ========================================================={{{1
logging.basicConfig()
log = logging.getLogger('fixrunner')
log.setLevel(logging.INFO)


# classes ================================================================{{{1

# BasicParser ------------------------------------------------------------{{{2
class BasicParser(OptionParser):
    """Some basic command-line options."""
    def __init__(self, *a, **k):
        OptionParser.__init__(self, *a, **k)
        self.add_option("-n", "--nocommit",
            action="store_false",
            dest="commit",
            default=True,
            help="Do not commit any changes.")
        self.add_option("-d", "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="Show debug messages.")

# Exception for violating 'once' -----------------------------------------{{{2
class OnceException(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

# Runner -----------------------------------------------------------------{{{2
class Runner:

    """This class can be subclassed to handle more command-line options,
    etc."""
    def __init__(self, parser=BasicParser):
        self.commit = True
        self.debug = False
        self.parser = parser()
        self.remark = 'fixrunner.py'

    def run(self, func, *a, **k):
        """Decorator, func will get a DaveConnection as its first argument."""
        def wrapper(*a, **k):
            try:
                (opts, args) = self.parser.parse_args(sys.argv[1:])
                self.commit = opts.commit
                self.debug = opts.debug
                if self.debug:
                    log.setLevel(logging.DEBUG)
                k.update(opts.__dict__)
                return self.dc_runner(func, os.environ['DB_URL'], os.environ['DB_SCHEMA'], *(a + tuple(args)), **k)
            except SystemExit, se:
                pass
            except Exception, e:
                log.error("Exception: %s" % e)
                if self.debug:
                    print >>sys.stderr, traceback.format_exc()
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper

    def once(self, func, *a, **k):
        """Decorator, func will not run if it has run before on this schema."""
        def wrapper(*a, **k):
            program = get_program(func)
            dc = None
            try:
                dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
                l1conn = None
                try:
                    l1conn = dc.getL1Connection()
                    l1conn.rquery("SELECT * FROM dave_revision WHERE cliprogram = '%s'" % program, None)
                    if l1conn.readRow():
                        raise OnceException("The program '%s' has already run for this schema." % program)
                finally:
                    if l1conn is not None:
                        l1conn.endQuery()
            finally:
                if dc is not None:
                    dc.close()
            return func(*a, **k)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper

    def dc_runner(self, func, connstr, schemastr, *a, **k):
        """Run func, supply 'dc' object as first argument to func."""
        ops = []
        dc = None
        try:
            log.info("Connecting to %s" % connstr)
            dc = DaveConnector(connstr, schemastr)
            program = get_program(func)
            dc.getConnection().setProgram(program)
            log.debug("Setting 'cliprogram' to '%s'." % program)
            # Get "real values"
            log.info("Connection: %s, Schema %s" % dc.getConnectionInfo()[:2])
            ops = func(dc, *a, **k)
            if ops:
                log.info("*** Total %d ops" % len(ops))
                if self.debug:
                    for op in ops:
                        print op
                if self.commit:
                    if hasattr(func, 'remark'):
                        remark = func.remark
                    else:
                        remark = self.remark
                    log.debug("Setting reason (remark) to '%s'" % remark)
                    commitid = DaveStorer(dc, reason=remark).store(ops, returnCommitId=True) 
                    log.info("Saved with commitid = %d" % commitid)
                else:
                    log.warning("Not committing!")
        finally:
            if dc is not None:
                dc.close()
        return ops


# functions =============================================================={{{1

# backout ----------------------------------------------------------------{{{2
def backout(dc, revid):
    """Return list of operation needed to reverse all changes done in a commit
    with revid == 'revid'."""
    ops = []
    for upd in list(level_1_query(dc, ' '.join((
            'SELECT tablename',
            'FROM dave_updated_tables',
            'WHERE revid = %d' % revid)), ['tablename'])):
        table = upd['tablename']
        log.debug("Undoing changes to table '%s'." % table)
        for entry in dbsearch(dc, table, 'revid = %d' % revid,
                withDeleted=True):
            if entry['deleted'] == 'Y':
                del entry['deleted']
                ops.append(createop(table, 'W', entry))
            else:
                ops.append(createop(table, 'D', entry))
    return ops


# cid2revid --------------------------------------------------------------{{{2
def cid2revid(dc, cid):
    """Return 'revid' for a given 'commitid'."""
    for rec in level_1_query(dc, ' '.join((
            'SELECT revid',
            'FROM dave_revision',
            'WHERE commitid = %d' % cid)), ['revid']):
        return rec['revid']
    raise ValueError("Could not find any record in 'dave_revision' with commitid = '%s'." % cid)


# creatop ----------------------------------------------------------------{{{2
createop = createOp


# dbsearch ---------------------------------------------------------------{{{2
def dbsearch(dc, entity, expr=[], withDeleted=False):
    """Search entity and return list of objects."""
    if isinstance(expr, str):
        expr = [expr]
    return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))


# get_program ------------------------------------------------------------{{{2
def get_program(f):
    """Return 'program' associated with the function 'f'."""
    if hasattr(f, 'program'):
        return f.program
    return os.path.basename(sys.argv[0])


# level_1_query ----------------------------------------------------------{{{2
def level_1_query(dc, query, columns):
    """Generator - return dictionary per iteration. 'columns' is a list of
    column names."""
    l1conn = dc.getL1Connection()
    l1conn.rquery(query, None)
    R = l1conn.readRow()
    while R:
        # Create dictionary, colname=value
        d = dict(zip(columns, R.valuesAsList()))
        # Remove 'branchid' (why ??, DIG does this, but is it necessary??)
        d.pop('branchid', None)
        yield d
        R = l1conn.readRow()
    l1conn.endQuery()


# runner -----------------------------------------------------------------{{{2
runner = Runner()


# run --------------------------------------------------------------------{{{2
run = runner.run


# once -------------------------------------------------------------------{{{2
once = runner.once


# get_parser -------------------------------------------------------------{{{2
def get_parser():
    return runner.parser


# set_parser -------------------------------------------------------------{{{2
def set_parser(parser):
    runner.parser = parser()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    print "connect=(%s), schema=(%s)" % (os.environ['DB_URL'], os.environ['DB_SCHEMA'])


# Sample code ============================================================{{{1
## import fixrunner
## 
## @fixrunner.run
## def fixit(dc, *a, **k):
##     ops = []
##     for entry in fixrunner.dbsearch(dc, 'account_entry', " ".join((
##             "source LIKE '%%salary%%'",
##             "AND deleted = 'N'",
##             "AND next_revid = 0", 
##         ))):
##         ops.append(fixrunner.createOp('account_entry', 'D', entry))
##     return ops
## 
## # if the attribute 'program' is set, then it will be recorded in DAVE_REVISION(cliprogram)
## fixit.program = 'install_fix_090730.py (2009-07-30)'
## 
## if __name__ == '__main__':
##     fixit()
# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
