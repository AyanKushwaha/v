
"""
This script will set the award_key in bid_leave_vacation table for all bids that were fulfilled with 
the old automatic assigner logic (automatic assigner previous to jira sascms-4010).


Usage:
    bin/startMirador.sh --manpower --script -s adhoc.sascms-4945 [test]

"""
__verision__ = "$Revision$"
__author__ = "Jose Cortes, Jeppesen"

import sys, os
from tm import TM
from carmensystems.manpower.leave.interfaces.i_vacation_bid import IVacationBid
from carmensystems.manpower.leave.interfaces.i_bid_leave_matcher_strategy import IBidLeaveMatcherStrategy
from carmensystems.manpower.leave.interfaces.i_leave_object_container import ILeaveObjectContainer
from carmensystems.manpower.leave.activity.leave_object_manager import LeaveObjectManager
from carmensystems.manpower.core.customer_object_manager import CustomerObjectManager
from carmensystems.manpower.leave.customer_object_register_internal import CustomerObjectRegisterInternal
from carmusr.manpower.leave.common.leave_parameter_set_manager import LeaveParameterSetManager
from carmusr.manpower.leave.bid.bidtypes.rotation_bid import RotationBid


from carmensystems.manpower.leave.crew.leave_crew_manager import LeaveCrewManager
from carmensystems.manpower.leave.bid.leave_bid_manager import LeaveBidManager
from carmensystems.manpower.private.util import Connect
from carmensystems.manpower.private.util.tableManagerGlobalHandler import TableManagerGlobalRepository
from carmensystems.manpower.core.logger import Logger
from AbsTime import AbsTime
import json
logging = Logger("sascms4945", "bid", "sascms4945")

class BidAwardKeyUpdate(IBidLeaveMatcherStrategy):
    
    def __init__(self, workset):
        self._workset = workset
        paramManager = LeaveParameterSetManager(self._workset)
        self.paramSet = paramManager.create()
    
    def match(self, bid):
        if isinstance(bid, IVacationBid) or isinstance(bid, RotationBid):
            logging.debug("Trying to match bid %s to vacations", bid)
            for alt in bid.getRequestKeys():
                logging.debug("Checking alt %s ", alt)
                bidAlt = bid.getRequest(alt)
                logging.debug("Checking bidAlt %s", bidAlt)
                logging.debug("Matching dates bidAlt.leave start %s, bidAlt.leave end %s, bidAlt start %s, bidAlt end %s",
                              bidAlt.getLeaveObject().getLocalStart(),
                              bidAlt.getLeaveObject().getLocalEnd(),
                              bid.getAlternativeStartDate(alt),
                              bid.getAlternativeEndDate(alt))
                
                logging.debug("Matching with legal moves: %s", self.paramSet.getLegalMoves(bidAlt.getLeaveObject().getCrew().getEntity(), \
                                                                                           bidAlt.getLeaveObject().getLocalStart(), \
                                                                                           bidAlt.getLeaveObject().getLocalEnd()))
                
                
                if self._isBidAssigned(bidAlt):
                    logging.debug("bidAlt is assigned,hasVacation %s",self._hasVacationBetween(bidAlt.getLeaveObject(),\
                                            bidAlt.getLeaveObject().getLocalStart(),\
                                               bidAlt.getLeaveObject().getLocalEnd()))
 
                     
                    if not self._hasVacationBetween(bidAlt.getLeaveObject(),\
                                               bid.getAlternativeStartDate(alt),\
                                               bid.getAlternativeEndDate(alt)):
                    # check if matched bid should be deattached 
                        logging.debug("bidAlt is reseted")
                        #bid.resetRequest(alt)
                        pass

                else:
                    #bid is not assigned
                    if not self._hasVacationBetween(bidAlt.getLeaveObject(),bidAlt.getLeaveObject().getLocalStart(),bidAlt.getLeaveObject().getLocalEnd()):
                        logging.debug("reset Request")
                        #bid.resetRequest(alt)
                        pass
                        
                    else:
                    #check if there are activities on roster that makes bid fulfilled                            
                        leaveContainer = None
                        for leave in LeaveObjectManager.getInstance(self._workset).getLeaveForCrew(bid.getCrew()):
                            if leave.getLeaveObject().isAssigned():
                                logging.debug("Matching dates bidAlt.leave start %s, bidAlt.leave end %s, leave start %s, leave end %s",
                                              bidAlt.getLeaveObject().getLocalStart(),
                                              bidAlt.getLeaveObject().getLocalEnd(),
                                              leave.getLeaveObject().getLocalStart(),
                                              leave.getLeaveObject().getLocalEnd())
                                if self._doesOverlapLeave(bidAlt.getLeaveObject(), leave.getLeaveObject()):
                                    logging.debug("add to container %s on bid %s on alt %s", leave, bid, alt)
                                    if leaveContainer is None:
                                        leaveContainer = CustomerObjectManager.getInstance().getApi(CustomerObjectRegisterInternal).createInstance(ILeaveObjectContainer, leave.getLeaveObject())
                                    else:
                                        leaveContainer.addLeaveObject(leave.getLeaveObject())
                        logging.debug("set Request")
                        if leaveContainer is None:
                            #bid.resetRequest(alt)
                            pass
                        else:
                            award_key = json.dumps([[x.getType().id, x.getLocalStart().yyyymmdd(), x.getLocalEnd().yyyymmdd()]
                                                        for x in leaveContainer.subPartsGenerator()])
                            if bid.getAlternativeEntity(alt).award_key != award_key:
                                bid.getAlternativeEntity(alt).award_key = award_key
                                
                            bid.setRequest(alt,leaveContainer)
#    
    def _isBidAssigned(self,bidContainer):
        for part in bidContainer.subPartsGenerator():
            if not part.isAssigned():
                return False
        return True

    def _doesOverlapLeave(self, bidLeaveObject, leaveObject):
        leaveStart = leaveObject.getLocalStart()
        leaveEnd = leaveObject.getLocalEnd()
        bidLeaveStart = bidLeaveObject.getLocalStart()
        bidLeaveEnd = bidLeaveObject.getLocalEnd()
        
        crew = leaveObject.getCrew()
        legalMoves = self.paramSet.getLegalMoves(crew.getEntity(), leaveStart, leaveEnd)
        
        #Check if leave overlap bidLeave
        for move in legalMoves:
            if (leaveStart + move) < bidLeaveEnd and (leaveEnd + move) > bidLeaveStart:
                return True
        return False
        
    def _hasVacationBetween(self, leaveObject, starttime, endtime):
        crew = leaveObject.getCrew()
        legalMoves = self.paramSet.getLegalMoves(crew.getEntity(), starttime, endtime)
        for move in legalMoves:
            if self.paramSet.hasVacationBetween(crew,starttime + move, endtime + move):
                return True
        return False
  



class AwardKeyUpdate(object):
    def __init__(self, schema, dburl, category, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save
        self._cat = category
           
    def run(self):
        
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        if self._cat == 'C':
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('1jan2012'), AbsTime('6jan2013'), '30aug2012')
        else:
            (_tm, _tmid) = Connect.ConnectFilterAndLoad(self._cat, AbsTime('1jan2012'), AbsTime('31may2013'), '30aug2012')
            
        tmgh = TableManagerGlobalRepository.getInstance().getGlobalHandler(_tm)
        workset = tmgh.getWorkset()
        sys.stdout.write(" ...Connected!\n")
        

        bidAwardKeyUpdateStrategy = BidAwardKeyUpdate(workset)
        leaveCrewManager = LeaveCrewManager.getInstance(workset)
        leaveBidManager = LeaveBidManager.getInstance(workset)

        for crew_entry in tmgh.tm.table('crew'):
            crew = leaveCrewManager.getCrew(crew_entry.id)
            for bid in leaveBidManager.getBidsForCrew(crew): 
                bidAwardKeyUpdateStrategy.match(bid)


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
    updaterObj = AwardKeyUpdate(schema, db_url, 'C', save)
    updaterObj.run()
    del updaterObj
    
    #Execution for flight deck
    updaterObj2 = AwardKeyUpdate(schema, db_url,'F', save)
    updaterObj2.run()
    del updaterObj2

main(sys.argv)

