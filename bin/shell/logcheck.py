import re, sys
from AbsTime import AbsTime
from AbsDate import AbsDate
try:
    from db import _C, _getdaveconnector, _dbsearch, _dbsql, _createop, DaveStorer
except ImportError:
    print >>sys.stderr, "Error: logcheck depends on 'db' cmsshell module,"
    print >>sys.stderr, "       but it appears to be unavailable"
    sys.exit(1)

def erroneousdata(logfile, dblookup=True, removebrokentrips=False, interactive=True):
    """Remove errouneous data from the database
    --dblookup [default True]
    --removebrokentrips [default False] - Actually removes the trips from the database
    --interactive [default Treu] - Asks if we should remove trips even if there is multiple matchings"""
    lt = re.compile(r'Error! Pid:[0-9]+  (\w+ \w+  \d+ \d\d:\d\d:\d\d \d+)  User:.+')
    le = re.compile(r'.+')
    fdid = re.compile(r' +FlightId = Carrier: (\w+), Num: (\d+), Suffix: ([^,]+), Leg no: (\d+), tab_ix:.+')
    timestamp = "(unknown)"
    errCount = 0
    inerr = False
    trips = []
    trip = None
    leg = None
    rtyp = None
    if not dblookup and removebrokentrips:
        print >>sys.stderr, "Cannot remove broken trips with dblookup=False"
        sys.exit(1)
    for line in file(logfile):
        if inerr:
            if len(line) < 2:
                inerr = False
            elif line.startswith("      CRR:"):
                trip = {'legs':[]}
                trips.append(trip)
                rtyp = None
            elif line.startswith("            Leg:"):
                leg = {}
                if rtyp is not None: leg["type"] = rtyp
                trip["legs"].append(leg)
            elif trip is not None and line.startswith("        baseIx"):
                trip["base"] = line.split("(")[-1].strip()[:-1]
            elif trip is not None and line.startswith("          cc: "):
                trip["cc"] = ','.join(map(str.strip, line.split(":")[1].split(";"))).strip(",")
            elif trip is not None and line.startswith("        Base variant "):
                if not "basevariants" in trip:
                    trip["basevariants"] = []
                trip["basevariants"].append(line.split("(")[-1].strip()[:-1])
            elif trip is not None and line.startswith("            type: "):
                rtyp = line.split("(")[-1].split(",")[0].strip()
            elif leg is not None and line.startswith("              GDOR: "):
                leg["udor"] = AbsDate(int(line.split("(")[-1].strip()[:-1]))
                if not "firstday" in trip or trip["firstday"] > leg["udor"]:
                    trip["firstday"] = leg["udor"]
            elif leg is not None and line.startswith("                Airports: "):
                leg["adep"] = line.split(">")[0].split(":")[-1][:-1].strip()
                leg["ades"] = line.split(">")[-1].strip()
            elif leg is not None and line.startswith("                Airports: "):
                leg["adep"] = line.split(">")[0].split(":")[-1][:-1].strip()
                leg["ades"] = line.split(">")[-1].strip()
            elif leg is not None and line.startswith("                statcode: "):
                leg["statcode"] = line.split(":")[1].split()[0]
            elif leg is not None and line.startswith("              sobt: "):
                leg["sobt"] = AbsTime(int(line.split(": ")[-1].split("(")[-1].strip()[:-1]))
            elif leg is not None and line.startswith("              sibt: "):
                leg["sibt"] = AbsTime(int(line.split(": ")[-1].split("(")[-1].strip()[:-1]))
            elif leg is not None and line.startswith("              aobt: "):
                leg["aobt"] = AbsTime(line.split(": ")[-1].split("(")[0].strip())
            elif leg is not None and line.startswith("              aibt: "):
                leg["aibt"] = AbsTime(line.split(": ")[-1].split("(")[0].strip())
            elif leg is not None and fdid.match(line):
                m = fdid.match(line)
                leg["fd"] = "%s %0d" % (m.group(1), int(m.group(2)))
                leg["fdkey"] = "%s %06d%s" % (m.group(1), int(m.group(2)), m.group(3))
                leg["suffix"] = m.group(3)
                leg["legno"] = int(m.group(4))
            else:
                pass
        else:
            m = lt.match(line)
            if m:
                timestamp = m.group(1)
            elif "TripTable::postProcess(): Erroneous data:" in line:
                inerr = True
                errCount += 1
    #print json.dumps(trips,indent=2)
    def fdat(ref, date):
        days = int(date)/1440 - int(ref)/1440
        if days:
            return "%+d %s" % (days, date.time_of_day())
        else:
            return date.time_of_day()
    safetoremove = set()
    for trip in sorted(trips, key=lambda trip:trip.get("firstday",0)):
        print "%-4s (+)%-12s cc=%-28s" % (trip.get("base",""), ', '.join(trip.get("basevariants",[])), trip.get("cc"))
        dbtrips =None
        for leg in sorted(trip["legs"], key=lambda leg:leg.get("sobt",0)):
            udor = leg.get("udor",AbsTime(0))
            print "  %-6s %3s-%3s  %-10s %1s %2s  (%8s - %-8s) %s" % (leg.get("udor",""),leg.get("adep",""),leg.get("ades",""),leg.get("fdkey",""),leg.get("legno",""),
                leg.get("suffix",""),fdat(udor,leg.get("sobt","")),fdat(udor, leg.get("sibt","")),leg.get("statcode","")),
            if "aibt" in leg and int(leg["aibt"]) > 0 or "aobt" in leg and int(leg["aobt"]) > 0:
                print "act=(%8s - %-8s)" % (fdat(udor, leg.get("aobt")),fdat(udor, leg.get("aibt"))),
            print ""
            dblegtrips = set()
            if dblookup and leg.get("fdkey") and leg.get("udor"):
                for dbleg in _dbsearch("flight_leg", ["fd='%s'" % leg["fdkey"], "udor=%d" % (int(leg["udor"])/1440)]):
                    if dbleg["aobt"] and dbleg["aibt"]:
                        print "  > DB: rev=%8s %-10s   %27s act=(%8s - %-8s) " % (dbleg["revid"], dbleg["fd"], leg["statcode"], fdat(udor,AbsTime(int(dbleg["aobt"]))),fdat(udor,AbsTime(int(dbleg["aibt"])))),
                    else:
                        print "  > DB: rev=%8s %-10s   %27s act=N/A " % (dbleg["revid"], dbleg["fd"], leg["statcode"]),
                ct = 0
                for dbasmt in _dbsearch("trip_flight_duty", ["trip_udor>%d" % (int(udor)/1440-10), "trip_udor<%d" % (int(udor)/1440+10), "leg_fd='%s'" % leg["fdkey"], "leg_udor=%d" % (int(leg["udor"])/1440)]):
                    dblegtrips.add( (dbasmt["trip_udor"],dbasmt["trip_id"]) )
                    ct += 1
                print " (%d trips)" % ct
                if dbtrips is None: dbtrips = dblegtrips
                else: dbtrips = dbtrips.intersection(dblegtrips)
        if dblookup and len(dbtrips) > 0:
            print "%4d trips have all of these legs, now filtering on crew complement..." % len(dbtrips)
            ccs = []
            if trip.get("cc"):
                ccs = ["cc_%d=%s" % x for x in enumerate(trip["cc"].split(","))]
            dbmatchingtrips = _dbsearch("trip", [' or '.join("udor=%d and id='%s'" % _ for _ in dbtrips)] + ccs)
            for trip in dbmatchingtrips:
                print "> DB trip: rev=%8s  key=(udor=%d id='%s') udor=%s base=%s" % (trip["revid"], int(trip["udor"]), trip["id"], AbsDate(1440*int(trip["udor"])), trip["base"])
            if len(dbmatchingtrips) == 1:
                print "Only one matching trip found. This is likely the culprit!"
                safetoremove.add((dbmatchingtrips[0]["udor"],dbmatchingtrips[0]["id"]))
            elif len(dbmatchingtrips) == 0:
                print "No matching trip found. Already cleaned?"
            else:
                print "Multiple (%d) matching trips found. It is ambigous which one is the culprit" % len(dbmatchingtrips)
                if interactive:
                    for tudor, tid in dbtrips:
                        answer = raw_input( "Do you want to remove the following trip? (%s, %s) [Y/N]   " % (tudor, tid))
                        if answer.upper() == "Y" or answer.upper() == "YES":
                            safetoremove.add((dbmatchingtrips[0]["udor"],dbmatchingtrips[0]["id"]))
               
        print
    if removebrokentrips:
        if len(safetoremove) == 0:
            print "No trips were found for removal. See the above printout for details"
        else:
            print "%d broken trip(s) will now be removed" % len(safetoremove)
            actstorem = 0
            tripstorem = 0
            asmtstoup = 0
            ops = []
            for tab in ("trip_flight_duty", "trip_ground_duty", "trip_activity", "crew_trip"):
                for dbasmt in _dbsearch(tab, [' or '.join("trip_udor=%d and trip_id='%s'" % _ for _ in safetoremove)]):
                    ops.append(_createop(tab, "D", dbasmt))
                    actstorem += 1
            for tab in ("crew_flight_duty", "crew_ground_duty", "crew_activity"):
                for dbasmt in _dbsearch(tab, [' or '.join("trip_udor=%d and trip_id='%s'" % _ for _ in safetoremove)]):
                    dbasmt["trip_id"] = None
                    dbasmt["trip_udor"] = None
                    ops.append(_createop(tab, "U", dbasmt))
                    asmtstoup += 1
            for dbtrip in _dbsearch("trip", [' or '.join("udor=%d and id='%s'" % _ for _ in safetoremove)]):
                ops.append(_createop("trip", "D", dbtrip))
                tripstorem += 1
                
            if tripstorem != len(safetoremove):
                print "Warning: Internal consistency check failed: Found %d to remove, expected %d" % (tripstorem, len(safetoremove))
                
            print "%d operations will be performed" % len(ops)
            print "   %d trip assignments will be removed" % actstorem
            print "   %d crew assignments will be updated with null trip" % asmtstoup
            print "   %d trips will be deleted" % tripstorem
            print "Are you sure? This will BATCH EDIT LIVE DATA"
            try:
                raw_input("Press OK to continue, Ctrl+C to ABORT !")
            except KeyboardInterrupt:
                print ""
                return
            commitid = DaveStorer(_getdaveconnector(False), reason="logcheck.TripCleaner").store(ops, returnCommitId=True)
            print "Broken trips cleaned updated. New commitid = %s" % commitid
