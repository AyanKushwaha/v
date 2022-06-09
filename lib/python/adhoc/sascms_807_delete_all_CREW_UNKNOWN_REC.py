#!/bin/env python


"""
Deletes all records in CREW_UNKNOWN_REC
"""

import sys, getopt
from carmensystems.dig.framework import dave

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "hc:s:", ["help"])
    except getopt.GetoptError, e:
        print e
        return

    dbconn = None
    schema = None
    for opt, val in opts:
        if opt in ("-h","--help"):
            print __doc__
            return
        if opt == "-c":
            dbconn = val
        if opt == "-s":
            schema = val
    if not dbconn or not schema:
        print "Database connection and schema must be specified!"
        return

    connector = dave.DaveConnector(dbconn, schema)

    ops = []
    for rec in connector.runSearch(dave.DaveSearch('crew_unknown_rec',[])):
        ops.append(dave.createOp('crew_unknown_rec', 'D', rec))

    storer = connector.getStorer()
    storer.store(ops)


if __name__ == "__main__":
    main(sys.argv)
