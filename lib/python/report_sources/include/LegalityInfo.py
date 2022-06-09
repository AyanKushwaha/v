#

#
"""
Legality Info Report
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
import carmensystems.studio.rave.private.FailObjectParser as fop
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
from AbsTime import AbsTime
import Dates
import time
import math
import BSIRAP

FAILHEADER = ('Failed rule',' ','Date',' ','Value',' ','Limit',' ','Diff')

def failRow(failure, illegal_training=False, timezone=0):
    failRow = Row()
    descr = Column()
    remark = ""
    failtext = ""
    if failure.rule.remark():
        remark = failure.rule.remark()
        descr.add(Text(remark, font=Font(weight=BOLD)))
    if failure.failtext:
        failtext = failure.failtext
        descr.add(failure.failtext)
    if (illegal_training and
        failtext.lower().find("training") < 0 and
        remark.lower().find("training") < 0):
        return False
    failRow.add(descr)
    failRow.add(' ')
    start = "-"
    if not failure.failobject:
        if failure.startdate:
            start = failure.startdate + RelTime(0,timezone,0)
            startDate = AbsDate(start)
            startTime = start - AbsTime(startDate)
            if (startTime > RelTime(0,0)):
                start = Column(startDate, startTime)
            else:
                start = startDate
    else:
        (a,b,failobjectTime) = fop.parseFailobject(failure.failobject)
        start = AbsTime(failobjectTime) + RelTime(0,timezone,0)
        startDate = AbsDate(start)
        startTime = start - AbsTime(startDate)
        if (startTime > RelTime(0,0)):
            start = Column(startDate, startTime)
        else:
            start = startDate
    failRow.add(start)
    failRow.add(' ')
    actual = "-"
    if failure.actualvalue is not None:
        actual = failure.actualvalue
    limit = "-"
    if failure.limitvalue:
        limit = failure.limitvalue
    try:
        diff = actual - limit
    except:
        diff = "-"
    if (type(actual) == BSIRAP.AbsTime):
        actDate = AbsDate(actual)
        actTime = actual-AbsTime(actDate)
        if (actTime > RelTime(0,0)):
            actual = Column(actDate,actTime)
        else:
            actual = actDate
        limDate = AbsDate(limit)
        limTime = limit-AbsTime(limDate)
        if (limTime > RelTime(0,0)):
            limit = Column(limDate,limTime)
        else:
            limit = limDate
    failRow.add(actual)
    failRow.add(' ')
    failRow.add(limit)
    failRow.add(' ')
    failRow.add(diff)
    return failRow
    
class LegalityInfo(SASReport):
    
    def create(self, scope='crew_object', special=False, context='default_context', headers=True):
        if special:
            title = "Illegal Training Info"
            illegal_training = True
        else:
            title = "Legality Info"
            illegal_training = False
            
        # Basic setup
        SASReport.create(self, title, orientation=PORTRAIT, headers=headers, usePlanningPeriod=True)

        crewReport = (scope[0:4] == "crew")
        tripReport = not crewReport

        generalReport = (scope[5:] == "general")
        self.objectReport = not generalReport

        # Building rave expression and collecting data
        if crewReport:
            self.legalString = "Roster is legal"
            legality_expr = r.foreach(
                'iterators.roster_set',
                'report_common.%crew_string%',
                r.foreach(
                r.rulefailure(sort_by=r.first(r.Level.atom(), 'leg.%start_UTC%'))
                )
                )

            crewData, = r.eval(context, legality_expr)
            # Looping through rosters sets
            for (ix,crewString, failures) in crewData:
                headerBox = Text(crewString, font=Font(size=10, weight=BOLD))
                self.failBox(headerBox, failures, illegal_training)
        elif tripReport:
            self.legalString = "Trip is legal"
            leg_expr = r.foreach('iterators.leg_set',
                                 'leg.%flight_name%',
                                 'leg.%start_station%',
                                 'leg.%end_station%',
                                 )
            trip_expr = r.foreach('iterators.trip_set',
                                  'trip.%name%',
                                  'trip.%start_lt%',
                                  r.foreach('iterators.duty_set',leg_expr),
                                  r.foreach(r.rulefailure())
                                  )
            trips, = r.eval(context, trip_expr)
            for (ix,name,start_lt,dutys,failures) in trips:
                headerBox = Column(border=None)
                if name:
                    headerBox.add(Text(name, font=Font(size=10, weight=BOLD)))
                headerBox.add(Row(Text("Starts:", font=Font(weight=BOLD)),Text(start_lt)))
                dutyRow = ""
                dutySep = ""
                for (jx, legs) in dutys:
                    dutyRow += dutySep
                    for (kx,flightname,start_station, end_station) in legs:
                        dutyRow += start_station +"-"+flightname+"-"
                    dutyRow += end_station
                    dutySep = " | "
                headerBox.add(Row(Text("Trip: ", font=Font(weight=BOLD)),Text(dutyRow)))
                self.failBox(headerBox, failures)
                    
    def failBox(self, headerBox, failures, illegal_training=False):
        box = Column()
        box.add(Isolate(headerBox))
        noOfFailures = len(failures)
        actualFailures = 0
        if (noOfFailures > 0):
            box.add(self.getTableHeader(FAILHEADER))
            for failure, in failures:
                thisRow = failRow(failure, illegal_training)
                if not thisRow:
                    continue
                else:
                    actualFailures += 1
                    box.add(thisRow)
                    box.add(Row(Text(' ', font=Font(size=2)), height=3))
                    box.page0()
        else:
            box.add(Text(self.legalString, font=Font(weight=BOLD)))
        if (self.objectReport or actualFailures > 0):
            self.add(box)
            self.add(" ")
            self.page0()

# End of file
