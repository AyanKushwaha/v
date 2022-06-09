
# [acosta:08/235@11:21] Created.

"""
32.12 Office List

The report is divided into several PDF files:

Flight Deck                             |Cabin Crew
=================== ====================|=================== =======
office_F_CPH_M8     CPH, MD80           |office_A_CPH_AP     CPH, AP
office_F_CPH_A2     CPH, Airbus 320     |office_A_CPH_AS     CPH, AS
office_F_CPH_A3A4   CPH, Airbus 330-340 |office_A_CPH_AH     CPH, AH
                                        |
office_F_OSL_38     OSL, B737           |office_A_OSL_AP     OSL, AP
office_F_OSL_F5     OSL, F50            |office_A_OSL_AS     OSL, AS
office_F_OSL_A3A4   OSL, Airbus 330-340 |office_A_OSL_AH     OSL, AH
                                        |
office_F_SVG_38     SVG, B737           |office_A_SVG_AP     SVG, AP
office_F_SVG_F5     SVG, F50            |office_A_SVG_AS     SVG, AS
                                        |office_A_SVG_AH     SVG, AH
                                        |
office_F_TRD_38     TRD, B737           |office_A_TRD_AP     TRD, AP
office_F_TRD_F5     TRD, F50            |office_A_TRD_AS     TRD, AS
                                        |office_A_TRD_AH     TRD, AH
                                        |
office_F_STO_36     STO, B737           |office_A_STO_AP     STO, AP
office_F_STO_M8     STO, MD80           |office_A_STO_AS     STO, AS
office_F_STO_A3A4   STO, Airbus 330-340 |office_A_STO_AH     STO, AH
                                        |
office_F_other      Other pilots        |office_A_other      Other attendants
"""

# imports ================================================================{{{1
import os

import Crs
import carmensystems.rave.api as rave
import carmensystems.publisher.api as prt
import report_sources.include.RosterInfo as RosterInfo

from AbsTime import AbsTime
from report_sources.include.SASReport import SASReport
from utils.selctx import BasicContext
from utils.TimeServerUtils import TimeServerUtils

# acosta BEGIN PATCH
import logging
import traceback
logging.basicConfig(filename=os.path.join(os.environ['CARMTMP'], 'logfiles',
    'office_list.log'))
log = logging.getLogger('officelist')
# END PATCH


# module variables ======================================================={{{1
# Bag containing current context
_bag = None


# classes ================================================================{{{1

# Report -----------------------------------------------------------------{{{2
class Report(RosterInfo._FlightBasedReport):
    """Iterate over the global _bag context to get a report. The global _bag is
    set-up by the caller.
    Note that the list will contain rosters from the 1st till the last in next
    month (the list is supposed to run on the 16th every month)."""
    def create(self):
        try:
            self._create()
        except Exception, e:
            log.error(traceback.format_exc())
            raise

    def _create(self):
        """Iterate over crew members and create PDF report."""
        global _bag
        self.roster_height = RosterInfo._roster_height
        SASReport.create(self, title=self.get_title(), showPlanData=True,
                pageWidth=820, orientation=prt.LANDSCAPE, usePlanningPeriod=True)
        self.current_rosters_height = 0
        self.first_day = AbsTime(self.arg('ST'))
        self.end_day = AbsTime(self.arg('ET'))
        self.extra_days = 0
        self.add_column_header()
        for roster in _bag.iterators.roster_set(sort_by=(
                    'report_crewlists.%%crew_base%%(%s)' % self.first_day,
                    'report_crewlists.%crew_empno%',
                )):
            if roster.crew.crew_has_valid_employment_in_period(self.first_day, self.end_day):
                self.add_one_crew(roster)


# functions =============================================================={{{1

# get_next_month ---------------------------------------------------------{{{2
def get_next_month():
    """Return first day of next month and first day of next-next month."""
    def add_one(y, m):
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1
        return y, m
    y, m = TimeServerUtils().getTime().timetuple()[:2]
    y1, m1 = add_one(y, m)
    y2, m2 = add_one(y1, m1)
    return AbsTime(y1, m1, 1, 0, 0), AbsTime(y2, m2, 1, 0, 0)
    

# run --------------------------------------------------------------------{{{2
def run(st=None, et=None, runidx=None):
    """Return a list of filenames of Office Lists."""
    global _bag

    if st is None or et is None:
        first_day, end_day = get_next_month()
    if st is None:
        st = first_day
    if et is None:
        et = end_day

    # Get and create directory
    dir = Crs.CrsGetModuleResource("officelist", Crs.CrsSearchModuleDef, "ExportDirectory")
    if dir is None:
        dir = os.environ['CARMTMP']
    if not os.path.exists(dir):
        os.makedirs(dir, 0775)

    L = []
    bc = BasicContext()
    idx = 0
    if not runidx:
        runidx = range(1,10)
    for entry in rave.context(bc.getGenericContext()).bag().report_crewlists.office_list_iterator():
        idx += 1
        if not idx in runidx:
            print "Skipping office list #%d" % idx
            continue
        # Set the global _bag to current context.
        _bag = entry
        print "Generating office list #%d" % idx
        # Add filename of new report to list
        L.append(prt.generateReport('crewlists.office_list', 
            os.path.join(dir, "office_%s" % (
                entry.report_crewlists.office_list_code())), prt.PDF, 
                {'ST': str(st), 'ET': str(et)}))
    return L


# NOTE: Cannot run the report from main within Studio (__main__._bag)

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
