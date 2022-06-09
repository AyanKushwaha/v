
"""
This script will change departure and arrivals for all vacations to crews station

Usage:
    bin/startMirador.sh --script -s adhoc.FixVacArn [test]

"""
__verision__ = "$Revision$"
__author__ = "Max Franklin, Jeppesen"

import sys, os
from tm import TM

class BaseError(Exception):
    pass


class VacFixer(object):
    def __init__(self, schema, dburl, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save


    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        TM.disconnect()
        sys.stdout.write(" Done!\n")

    def getStation(self, list, date):
        for (start, end, station) in list:
            if date<=end and date>=start:
                return station
        raise BaseError("No station found at %s" %date)
    
    def run(self):
        self.connect()

        print "Loading tables"
        TM(["crew_activity"])
        TM(["crew_employment"])
        TM(["airport"])
        TM(["crew_base_set"])
        TM.newState()

        print "Doing work"
        empCount=0
        baseNotFound=0
        crewDict={}
        for row in TM.crew_employment:
            try:
                if not crewDict.has_key(row.crew.id):
                    crewDict[row.crew.id]=[]
                if row.station in ("STO","CPH","OSL","TRD","SVG"):
                    crewDict[row.crew.id].append((row.validfrom, row.validto, row.station))
                    empCount += 1
            except Exception, e:
                print "error with: ", row.crew.id, e
                pass
        
        activityCount = 0
        for row in TM.crew_activity:
            try:
                activity = row.activity
                if activity.id in ("VA", "VA1", "F7"):
                    station=self.getStation(crewDict[row.crew.id], row.st)
                    airport=TM.crew_base_set[station].airport
                    if ( airport.id != row.adep.id):
                        row.adep=airport
                        row.ades=airport
                        print "Vacation not at station: ", airport.id,row.adep.id, row._id
                        activityCount += 1
            except BaseError, e:
                baseNotFound+=1
            except Exception, e:
                print "error with: ",row.crew.id, e
                pass
                
        print "Read employments: " , empCount
        print "Corrected activities not matching station: " , activityCount
        print "Bases not found: ", baseNotFound
        if self._save:
            print "Saving..."
            TM.save()
        else:
            print "Not saving..."
        sys.stdout.write("... Done\n")
        print "Done, exiting..."

def usage():
    print __doc__

def main(args):
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    save=True
    try:
        if args[1]=="test":
            print "Test run without save."
            save=False
        
    except:
        pass
    fixer = VacFixer(schema, db_url, save)
    fixer.run()
    del fixer

main(sys.argv)
