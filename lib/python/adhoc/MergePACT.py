
"""
This script will merge all PACT activities adjecent to eachother
into a single large PACT

Usage:
    MergePACT <schema> <dburl>

"""
__verision__ = "$Revision$"
__author__ = "Christoffer Sandberg, Jeppesen"

import os, sys, time
from tm import TM
import AbsTime
import RelTime
import AbsDate
from carmensystems.dave import dmf
import utils.spinner as spinner


class PactMerger:
    def __init__(self, schema, dburl):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._entityConn = None
        self._conn = None

    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        self._entityConn = dmf.EntityConnection()
        self._entityConn.open(self._dburl, self._schema)
        self._conn = dmf.Connection(self._dburl)
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        self._entityConn.close()
        self._conn.close()
        TM.disconnect()
        sys.stdout.write(" Done!\n")

    def run(self):
        self.connect()

        print "Loading tables"
        TM(["crew_activity"])
        TM.newState()

        print "Building crew cache"
        activityCount = 0
        crew_cache = {}
        for row in TM.crew_activity:
            try:
                activity = row.activity
                crew = row.crew.id
                if crew_cache.has_key(crew):
                    crew_cache[crew].append(row)
                else:
                    crew_cache[crew]=[row]
                activityCount += 1
            except:
                pass

        crewCount = len(crew_cache.keys())
        print "Amount of crew: %d" % (crewCount)
        print "Amount of activities: %d" % (activityCount)

        s = spinner.Spinner()
        p = spinner.ProgressBar(crewCount)
        x = 0

        print "Merging PACT's"
        for crewId in crew_cache.keys():
            if x % 10 == 0:
                p(x).write()
                s.write()
            x += 1
            pacts = crew_cache[crewId]

            pactList = [(pact.st, i, pact) for i, pact in enumerate(pacts)]
            pactList.sort()
            pactList = [pact for (_,_,pact) in pactList]

            delList = []
            lastPact =  None

            pactListLength = len(pactList)
            for i, pact in enumerate(pactList):
                if i == 0:
                    lastPact = pact
                    continue
                elif i == pactListLength:
                    break
                # Special condition, only merge midnight splitted activites UTC time
                if lastPact.activity == pact.activity and lastPact.et == pact.st and str(pact.st)[-5:] == '00:00':
                    lastPact.et = pact.et
                    delList.append(pact)
                else:
                    lastPact = pact
            for pact in delList:
                pact.remove()
        p(crewCount).write()

        sys.stdout.write("Saving to databse...\n")
        TM.save()
        sys.stdout.write("... Done\n")
        print "Done, exiting..."

def usage():
    print __doc__

def main(args):
    if len(args) != 3:
        usage()

    merger = PactMerger(sys.argv[1], sys.argv[2])
    merger.run()
    del merger

if __name__ == "__main__":
    main(sys.argv)

if len(sys.argv) > 1:
    main(sys.argv)
