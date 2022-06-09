#!/bin/env python

# [acosta:07/227@12:04] First version

"""
This program can be used to check if there are any destinations or departures
that use an airport that is not in the airport database.

It creates a temporary table with one column containing the missing airport
ID.
"""

# imports ================================================================{{{1
import sys
import getopt
import StartTableEditor

from Airport import Airport
from modelserver import StringColumn, IntColumn
from tm import TM, TempTable


# classes ================================================================{{{1

# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    msg = ''
    def __init__(self, msg):
        self.msg = msg


# TmpNoAirport -----------------------------------------------------------{{{2
class TmpNoAirport(TempTable):
    _name = 'tmp_no_airport'
    _keys = [
        StringColumn("airport", "Airport missing from airports database"),
            ]


# AirportCache -----------------------------------------------------------{{{2
class AirportCache(dict):
    """ Small help class to avoid searching for airports that we already
    handled. """
    def __call__(self, key):
        if key in self:
            return self[key]
        value = Airport(key).isAirport()
        self[key] = value
        return value


# functions =============================================================={{{1

# check ------------------------------------------------------------------{{{2
def check(airport):
    """ Check if airport is defined. """
    return Airport
# main -------------------------------------------------------------------{{{2
def main(*argv):
    """
    usage:
        airport_check.py [-h|--help]

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

        missing = set()
        ac = AirportCache()

        # First construct a set with all possible airports.
        if len(args) == 0:
            for leg in TM.flight_leg:
                adep = str(leg.getRefI('adep'))
                if not ac(adep):
                    missing.add(adep)
                ades = str(leg.getRefI('ades'))
                if not ac(ades):
                    missing.add(ades)
        else:
            for airport in args:
                if not ac(airport):
                    missing.add(airport)
        print ac

        tt = TmpNoAirport()
        tt.removeAll()
        for a in sorted(missing):
            tt.create((a,))
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
