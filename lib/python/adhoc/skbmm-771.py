
"""
This script will set validto as 31Dec2035 23:00 in bid_general table 


Usage:
    bin/startMirador.sh --manpower --script -s adhoc.skbmm-771 [test]

"""
__verision__ = "$Revision$"
__author__ = "Jose Cortes, Jeppesen"

import sys, os
from tm import TM
from carmensystems.manpower.private.util import Connect
from carmensystems.manpower.private.util.tableManagerGlobalHandler import TableManagerGlobalRepository
from carmensystems.manpower.core.logger import Logger
from AbsTime import AbsTime


class BidGeneralUpdateToUFN(object):
    def __init__(self, schema, dburl, category, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save
        self._cat = category
           
    def run(self):
        
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        if self._cat == 'C':
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('15apr2013'), AbsTime('15sep2013'), '15apr2013')
        else:
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('15apr2013'), AbsTime('15sep2013'), '15apr2013')
            
        tmgh = TableManagerGlobalRepository.getInstance().getGlobalHandler(_tm)
        workset = tmgh.getWorkset()
        sys.stdout.write(" ...Connected!\n")

        for bid_general in tmgh.tm.table('bid_general'):
            bid_general.validto = AbsTime('31Dec2035 23:00')


        if self._save:
            print "Saving..."
            tmgh.save()
        else:
            print "Not saving..."
            
        sys.stdout.write("Closing down database connection ... Done!\n")
        

def usage():
    print __doc__


def main(args):
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]
    save = True
    try:
        if args[1] == "test":
            print "Test run without save."
            save = False
        
    except:
        pass
    
    #Execution for cabin crew
    updaterObj = BidGeneralUpdateToUFN(schema, db_url, 'C', save)
    updaterObj.run()
    del updaterObj
    
    #Execution for flight deck
    updaterObj2 = BidGeneralUpdateToUFN(schema, db_url,'F', save)
    updaterObj2.run()
    del updaterObj2

main(sys.argv)

