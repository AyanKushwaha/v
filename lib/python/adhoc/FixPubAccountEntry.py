"""
This script will set all VA, F7 and VA1 account entries in table acount_entry to published.
Only entries that start between from and to will be changed.

Usage:
    bin/startMirador.sh --script -s adhoc.FixPubAccountEntry periodFrom periodTo [test]
    
    periodFrom and periodTo in Abstime-format: 01Jan1986 

"""
__verision__ = "$Revision$"
__author__ = "Erik Fjelkner, Jeppesen"

import sys, os
from tm import TM
from AbsTime import AbsTime

class AccountPubFixer(object):
    def __init__(self, schema, dburl, save=False, periodFrom=AbsTime("31Dec2036"), periodTo=AbsTime("31Dec2036")):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save
        self._periodFrom = periodFrom
        self._periodTo = periodTo
            
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
    
    def run(self):
        self.connect()

        print "Loading tables"
        TM(["account_entry"])
        TM.newState()

        print "Doing work"
        changedEntries = 0
        for row in TM.account_entry:
            try:
                entryTime = row.tim
                account = row.account.id
                published = row.published
                if entryTime >= self._periodFrom and \
                   entryTime <= self._periodTo and \
                   account in ("VA", "VA1", "F7") and \
                   not published:
                    row.published = True
                    changedEntries += 1
            
            except Exception, e:
                print "error with ",row.crew.id, "and entry time ",str(row.tim), "error : ",e
                pass  
        print "Changed entries: " , changedEntries
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

    periodFrom = args[1]
    fromDate=periodFrom[0:1]
    fromMonth=periodFrom[2:4]
    fromYear=periodFrom[5:8]
    
    periodTo =args[2]
    toDate=periodTo[0:1]
    toMonth=periodTo[2:4]
    toYear=periodTo[5:8]
    if not fromDate.isdigit() or not fromMonth.isalpha() or not fromYear.isdigit() \
       or not toDate.isdigit() or not toMonth.isalpha() or not toYear.isdigit():
        usage()
        sys.exit(2)
        
    try:
        periodFrom = AbsTime(periodFrom)
        periodTo = AbsTime(periodTo)
    except:
        usage()
        sys.exit(2)
        
    try: 
        if args[3]=="test":
            print "Test run without save."
            save=False
        
    except:
        pass

    fixer = AccountPubFixer(schema, db_url, save, periodFrom, periodTo)
    fixer.run()
    del fixer

main(sys.argv)
