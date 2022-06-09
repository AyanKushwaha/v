
"""
This script will renumber the priority of the bids in bid_general table to remove the out of sequence priority.
Before some bids for a specific type could be  first bid prio 3, second bid prio 7 and third bid prio 15.
After this script the first bid will be prio 1, second bid prio2 and third bid prio 3.
 --- This renumbering will be only apply to current valid bids ---


Usage:
    bin/startMirador.sh --manpower --script -s adhoc.sascms-6202 [test]

"""
__verision__ = "$Revision$"
__author__ = "Jose Cortes, Jeppesen"

import sys, os
from tm import TM
from carmensystems.manpower.private.util import Connect
from carmensystems.manpower.private.util.tableManagerGlobalHandler import TableManagerGlobalRepository
from carmensystems.manpower.core.logger import Logger
from AbsTime import AbsTime
from carmensystems.manpower.util import time_util


class BidGeneralUpdatePrio(object):
    def __init__(self, schema, dburl, category, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save
        self._cat = category
           
    def run(self):
        
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        if self._cat == 'C':
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('25dec2013'), AbsTime('15mar2014'), '25dec2013')
        else:
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('25dec2013'), AbsTime('15mar2014'), '25dec2013')
            
        tmgh = TableManagerGlobalRepository.getInstance().getGlobalHandler(_tm)
        workset = tmgh.getWorkset()
        sys.stdout.write(" ...Connected!\n")

        listCrewBidtype = []
        for bid_general in tmgh.tm.table('bid_general'):
            crewBidtype = (bid_general.crew,bid_general.bidtype)
            if crewBidtype not in listCrewBidtype:
                listCrewBidtype.append(crewBidtype)
        
        for crew,bidtype in listCrewBidtype:
            valid_time = time_util.nowAbsTime()
            ldap = '(&(crew.id=%s)(bidtype=%s)(validfrom<=%s)(validto>=%s))' % (
                crew.id, bidtype.id, valid_time, valid_time)
            bidList = [eBid for eBid in tmgh.tm.table('bid_general').search(ldap)]
            bidList.sort(lambda x,y: cmp(x.prio, y.prio))
            i = 1
            for eBid in bidList:
                eBid.prio = i
                i += 1


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
    updaterObj = BidGeneralUpdatePrio(schema, db_url, 'C', save)
    updaterObj.run()
    del updaterObj
    
    #Execution for flight deck
    updaterObj2 = BidGeneralUpdatePrio(schema, db_url,'F', save)
    updaterObj2.run()
    del updaterObj2

main(sys.argv)

