#!/bin/env python

# [acosta:06/349@15:30] first version

"""
This program can be used to check if there are any referential errors in the
database.  It creates a temporary table with three columns:
    (1)  The entity (table)
    (2)  The value of the broken reference
    (3)  Number of occurrences, number of times this value has been
         referenced.
"""

# imports ================================================================{{{1
import sys
import getopt
import StartTableEditor

from modelserver import StringColumn, IntColumn
from tm import TM, TempTable


# globals ================================================================{{{1
refs = {}
missing = {}


# classes ================================================================{{{1

# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    msg = ''
    def __init__(self, msg):
        self.msg = msg


# TmpBrokenRefs ----------------------------------------------------------{{{2
class TmpBrokenRefs(TempTable):
    _name = 'tmp_broken_refs'
    _keys = [
        StringColumn("entity", "Entity with missing values"),
        StringColumn("value", "Value that is missing in this entity")
            ]
    _cols = [
        IntColumn("count", "Number of occurrences")
            ]

    def _add(self, entity, missing):
        try:
            rec = self.find((entity, missing))
        except:
            rec = self.create((entity, missing))
        rec.count += 1

    def _create(self, entity, missing, count):
        rec = self.create((entity, missing))
        rec.count = count


# functions =============================================================={{{1
def addrec(rec):
    global refs
    r = rec.referer
    x = {rec.field: rec.entity.entity}
    if refs.has_key(r):
        refs[r].update(x)
    else:
        refs[r] = x


# main -------------------------------------------------------------------{{{2
def main(*argv):
    """
    usage:
        broken_refs.py [-h|--help]

    arguments:
        -h           This help text.
        --help

    """
    if len(argv) == 0:
        argv = sys.argv[1:]
    try:
        try:
            (opts, args) = getopt.getopt(argv, "h", ["help"])
        except getopt.GetoptError, msg:
            raise UsageException(msg)

        # more code, unchanged
        for (opt, value) in opts:
            if opt in ('-h', '--help'):
                print main.__doc__
                return 0
            else:
                pass


        # First construct a tree with all referred tables
        if len(args) == 0:
            for rec in TM._referer:
                addrec(rec)
        else:
            for table in args:
                for rec in TM._referer.search('(referer=%s)' % (table)):
                    addrec(rec)

        # Then walk through the tree
        for referrer in refs.keys():
            TM(referrer)

            # For each table loop through all records
            for entry in TM.table(referrer):

                # For each field that contains reference...
                for field in refs[referrer].keys():
                    rtable = refs[referrer][field]
                    ivalue = str(entry.getRefI(field))
                    try:
                        # ... try to get attribute 
                        x = getattr(entry, field)
                    except:
                        if missing.has_key(rtable):
                            m = missing[rtable]
                            if m.has_key(ivalue):
                                m[ivalue] += 1
                            else:
                                m[ivalue] = 1
                        else:
                            missing[rtable] = {ivalue: 1}
        tt = TmpBrokenRefs()
        tt.removeAll()
        for t in sorted(missing.keys()):
            for k in sorted(missing[t].keys()):
                tt._create(t, k, missing[t][k])
        StartTableEditor.StartTableEditor(['-t', tt.table_name()])

    except UsageException, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


# main ==================================================================={{{1
if __name__ == '__main__':
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
