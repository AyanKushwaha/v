#

#
"""
Illegal Training Info Report
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
import report_sources.include.LegalityInfo as LegalityInfo

from AbsDate import AbsDate
from RelTime import RelTime
from AbsTime import AbsTime
import Dates
import time
import math
import BSIRAP

FAILHEADER = ('Failed rule',' ','Date',' ','Value',' ','Limit',' ','Diff')

class IllegalTrainingInfo(SASReport):
    
    def create(self):
        
        print "IllegalTrainingInfo_test"
        
        # Basic setup
        SASReport.create(self, 'Flights with illegal training', orientation=PORTRAIT, usePlanningPeriod=True)

        # Building rave expression and collecting data
        crew_expr = r.foreach(
            'iterators.roster_set',
            'report_common.%crew_string%',
            'report_common.%employee_number%',
            'report_common.%crew_homebase%',
            'report_ccr.%illegal_training_any_failure_pp%',
            r.foreach('iterators.leg_set',
                      'report_common.%leg_key_sort%',
                      'report_common.%leg_start_hb%',
                      'report_common.%leg_fd%',
                      'report_common.%leg_qual%',
                      'report_common.%leg_attribute%',
                      'report_ccr.%illegal_training_any_failure_leg%',
                      r.foreach(r.times('report_ccr.%illegal_training_number_rules%', where='report_ccr.%illegal_training_trigger_ix%'),
                                'fundamental.%py_index%',
                                'report_ccr.%illegal_training_remark_ix%',
                                'report_ccr.%illegal_training_value_ix%',
                                'report_ccr.%illegal_training_limit_ix%',
                                )
                      )
            )
            
            
        crewData, = r.eval('default_context',crew_expr)

        legData = dict()
        
        # Looping through rosters sets
        for (ix, crewString, empno, crewBase, anyFailurePP, legs) in crewData:
            if anyFailurePP:
                for (jx, legKey, legStart, legFd, legQual, legAttr, anyFailure, rules) in legs:
                    if anyFailure:
                        print "Leg:", legFd, legStart, legKey
                        for (kx, index, remark, value, limit) in rules:
                            print "In rules loop"
                            if legKey not in legData:
                                legData[legKey] = dict()
                                legData[legKey]["legValues"] = (legFd, legStart, legQual)
                                legData[legKey]["fails"] = list()
                            legData[legKey]["fails"].append((crewBase, empno, remark, value, limit, legAttr))

        if len(legData) == 0:
            self.add("No illegal training")
            return
        else:
            self.add(Text("Flights with illegal training", font=self.HEADERFONT))
            self.add(" ")
        
        legKeys = legData.keys()
        legKeys.sort()

        for legKey in legKeys:
            (legFd, legStart, legQual) = legData[legKey]["legValues"]
            #headerString = "Flight: %-8s AC-qual: %-8s %s" %legData[legKey]["legValues"]
            legBox = Column()
            legBox.add(self.getTableHeader(("Flight: "+legFd,"AC-Qual: "+legQual,"Departure: "+legStart)))
            innerHeader = Row()
            for item in ("Base", "Empno", "Remark", "Value", "Limit", "Attribute"):
                innerHeader.add(Text(item, font=Font(weight=BOLD)))
            legBox.add(innerHeader)
            for (crewBase, empno, remark, value, limit, legAttr) in legData[legKey]["fails"]:
                legBox.add(Row(crewBase, empno, remark, value, limit, legAttr))
            self.add(Row(legBox))
            self.add(" ")
            self.page0()
            

# End of file
