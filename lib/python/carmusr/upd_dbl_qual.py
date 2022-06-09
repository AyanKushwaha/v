###########################################################################

#
# This script will:
# 1. Find double qualified crew (crew.%is_double_qualified%)
# 2. Get the qualification code from the latest LC or LINE CHECK in CTL
# 3. Set REC+LC in crew_document to the "other" qualification.
#
# Janne Carlsson, Jeppesen 2008-09-18

import sys
import Cui
import AbsTime
import carmensystems.rave.api as R
import os
import traceback

#import application

### This functionality only works while on DB-plans
try:
    from tm import TM
    from modelserver import EntityError
except:
    # This handles when the script is called when modelserver isn't available
    pass

def getDblQualCrew():
    print "In getDblQualCrew()"
    crewIDs, = R.eval("sp_crew", 
                      R.foreach(R.iter("iterators.roster_set",
                                where = ('crew.%is_double_qualified%')),
                                'crew.%id%'))
    
    print len(crewIDs), "double qualified crew found"
    return crewIDs
    
def getLatestLC(crewList, to_date):
    print "In getLatestLC()", AbsTime.AbsTime(to_date)
    crewDict = {}
    
    tom_date = AbsTime.AbsTime(to_date)
    ctl_tbl = TM.table("crew_training_log")
    for ix, crewid in crewList:
        latest_date = AbsTime.AbsTime("01JAN1986")
        latest_code = ""
        for ctl_ent in ctl_tbl.search("(&(crew=%s)(|(typ=LC)(typ=LINE CHECK)))" % crewid):
            if ctl_ent.tim >= latest_date and ctl_ent.tim <= tom_date:
                latest_date = ctl_ent.tim
                latest_code = ctl_ent.code
        crewDict[crewid] = dict()
        crewDict[crewid]["code"] = latest_code
    
    return crewDict
    
def updateCrewDoc(crewDict, sharp):
    print "In updateCrewDoc()"
    qual_toggle = {"A3":"A4", "A4":"A3"}
    
    if sharp:
        print "Executing in update mode"
    else:
        print "Executing in test mode"
        
    crewdoc_tbl = TM.table("crew_document")
    for crewid in crewDict:
        
        for crewdoc_ent in crewdoc_tbl.search("(&(crew=%s)(doc=REC+LC))" % crewid):
            if ((crewDict[crewid]["code"] == crewdoc_ent.ac_qual) and
               (crewDict[crewid]["code"] <> "") and
               (["A3", "A4"].count(crewDict[crewid]["code"]) > 0)):
                print "============================================="
                print crewdoc_ent.crew.id, "DOC:", crewdoc_ent.ac_qual, "CTL:", crewDict[crewid]["code"]
                print "Change to:", qual_toggle[crewDict[crewid]["code"]]
                if sharp:
                    crewdoc_ent.ac_qual = qual_toggle[crewDict[crewid]["code"]]
    
    
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    
    
def run_it(to_date, sharp):
    list_one = getDblQualCrew()
    dict_one = getLatestLC(list_one, AbsTime.AbsTime(str(to_date)))
    updateCrewDoc(dict_one, sharp)
    

# Execution starts here
if __name__ == '__main__':
    print "Start executing"
    
    run_it("01Jan1986", False)
    
    



