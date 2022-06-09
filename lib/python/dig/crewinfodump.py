#!/bin/env python

"""
Dump all crew, assemble information from the following tables:
    crew
    crew_address
    crew_extra_info
    crew_contact
    crew_relatives

Parameters:
    -c <dbconn>             Database connect string
                            e.g. "oracle:myschema/myschema@host:port/sid"
    -s <schema>             Database schema name
"""

import sys, getopt, datetime, time
from carmensystems.dig.framework import dave
from carmensystems.dig.framework.dave import DaveConnector 
from carmensystems.dig.framework.carmentime import fromCarmenTime, fromCarmenDate
from AbsTime import AbsTime

def sortByDate(d1,d2):
    if d1['validfrom'] < d2['validfrom']:
        return 1
    elif d1['validfrom'] > d2['validfrom']:
        return -1
    return 0

def sortBySubtypeAndDate(d1,d2):
    if d1['subtype'] < d2['subtype']:
        return -1
    if d1['subtype'] > d2['subtype']:
        return 1
    if d1['validfrom'] < d2['validfrom']:
        return 1
    elif d1['validfrom'] > d2['validfrom']:
        return -1
    return 0

def sortByTypAndWhich(d1,d2):
    if d1['typ'] < d2['typ']:
        return -1
    if d1['typ'] > d2['typ']:
        return 1
    if d1['which'] < d2['which']:
        return -1
    if d1['which'] > d2['which']:
        return 1
    return 0

def checkOverlaps(name, recs):
    hasOverlap = False
    for idx in range(len(recs)):
        vfrom1 = recs[idx]['validfrom']
        vto1 = recs[idx]['validto']
        for idy in range(len(recs)):
            if idy != idx:
                vfrom2 = recs[idy]['validfrom']
                vto2 = recs[idy]['validto']
                if (vfrom2 <= vfrom1 and vto2 > vfrom1) or \
                        (vfrom2 >= vfrom1 and vfrom2 < vto1):      
                    hasOverlap = True
    if hasOverlap:
        print "  ERROR: Overlapping periods %s" % name


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "hc:s:", ["all","help"])
    except getopt.GetoptError, e:
        print e
        print __doc__
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

    connector = DaveConnector(dbconn, schema)

    search = dave.DaveSearch('crew', [])
    crew = connector.runSearch(search)
    for rec in crew:
        search = dave.DaveSearch('crew_address', [('crew','=',rec['id'])])
        crew_address = connector.runSearch(search)
        search = dave.DaveSearch('crew_contact', [('crew','=',rec['id'])])
        crew_contact = connector.runSearch(search)
        search = dave.DaveSearch('crew_extra_info', [('id','=',rec['id'])])
        crew_extra_info = connector.runSearch(search)
        search = dave.DaveSearch('crew_relatives', [('crew','=',rec['id'])])
        crew_relatives = connector.runSearch(search)
        crew_address.sort(sortByDate)
        crew_contact.sort(sortByTypAndWhich)
        crew_extra_info.sort(sortByDate)
        crew_relatives.sort(sortBySubtypeAndDate)
        print "EMPNO:%s ID:%s" % (rec['empno'], rec['id'])
        checkOverlaps('crew_address', crew_address)
        checkOverlaps('crew_extra_info', crew_extra_info)
        print "  %s %s %s" % (rec['forenames'], rec['name'], rec['logname'])
        for attr in crew_extra_info:
            print "  ATTR: %s - %s" % (fromCarmenDate(attr['validfrom']).strftime("%Y%m%d"), fromCarmenDate(attr['validto']).strftime("%Y%m%d"))
            print "    %s %s %s" % (attr['forenames'], attr['name'], attr['nationality'])
        for addr in crew_address:
            print "  %s - %s" % (fromCarmenTime(addr['validfrom']).strftime("%Y%m%d"), fromCarmenTime(addr['validto']).strftime("%Y%m%d"))
            print "    MAIN: %s %s %s" % (addr['street'],addr['postalcode'],addr['city'])
            print "    SECO: %s %s %s" % (addr['street1'],addr['postalcode1'],addr['city1'])
        for con in crew_contact:
            print "  CON: %s %s %s" % (con['typ'],con['which'],con['val'])
        for rel in crew_relatives:
            print "  REL%s: %s - %s" % (rel['subtype'],fromCarmenTime(rel['validfrom']).strftime("%Y%m%d"), fromCarmenTime(rel['validto']).strftime("%Y%m%d"))
            print "  REL%s:   %s %s %s %s" % (rel['subtype'],rel['co_name'],rel['street'],rel['postalcode'],rel['city'])

if __name__ == "__main__":
    main(sys.argv)
