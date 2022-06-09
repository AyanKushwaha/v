"""
Swedish salary system.
Schedule calculation.
"""

from operator import attrgetter
import carmensystems.rave.api as R
from utils.rave import RaveIterator
from utils.RaveData import DataClass
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
from time import clock
from tm import TM
import salary.conf as conf
from utils.performance import clockme, log
from salary.Activity import SchedCCSEActivityManager
from salary.api import SalaryException
from salary.api import getDailyRecordsFor


(DUTIES,
 CREW_ID,
 FIRST_NAME,
 LAST_NAME,
 EMPNO,
 #IS_TEMPORARY,
 RANK,
 SCHEDULE_HOURS) = range(7)#8)
ROSTER_VALUES = ('report_common.%crew_id%',
                 'report_common.%crew_firstname%',
                 'report_common.%crew_surname%',
                 'report_common.%employee_number_salary%',
                 #'report_overtime.%is_temporary%',
                 'crew.%rank%',
                 )

DUTY_VALUES = ('report_overtime.%overtime_month_start%',
               'report_overtime.%overtime_month_end%')


class ScheduleCCSEManager:
    """
    A class that creates and holds ScheduleRosters.
    """

    def __init__(self, rundata, context, iterator='iterators.roster_set', crewlist=None):
        self.context = context
        self.rosterIterator = iterator
        self.crewlist = crewlist
        self.startDate = R.param(conf.startparam).value()
        self.endDate = R.param(conf.endparam).value()
        self.activityManager = SchedCCSEActivityManager(self.context, rundata, self.startDate, self.endDate)

    def getScheduleRosters(self):
        scheduleRosters = []

        if self.crewlist:
            try:
                import Cui
                Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, self.crewlist)
                Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiScriptBuffer)
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
                self.context = "default_context"
            except:
                # CuiSetCurrentArea may fail (e.g. in report workers).
                # No real problem, just a bit slower. It is filtered later on anyway.
                pass

        dt = self.startDate
        day_offset = 0
        hour_values = []
        while (dt < self.endDate):
            hour_values.append("report_overtime.%%crew_calculated_duty_hours%%(%s)" % dt)
            dt = dt.adddays(1)
        roster_values = list(ROSTER_VALUES) + hour_values

        duty_iterator_where = 'duty.%is_on_duty% or duty.%is_privately_traded%'
        duty_iterator = R.iter('iterators.duty_set', where=duty_iterator_where)
        duty_iteration = R.foreach(duty_iterator, *DUTY_VALUES)

        roster_iteration = R.foreach(self.rosterIterator, duty_iteration, *roster_values)

        rosters, = R.eval(self.context, roster_iteration)

        ### Or using bag-interface - and in this case with a simple roster-filter (where-clause)
        # for r in R.context(self.context).bag().iterators.roster_set('report_common.%crew_id% = "16159"'):
        #     roster = list(R.eval(r, *ROSTER_VALUES))
        #     duties = [(0,)+R.eval(d,*DUTY_VALUES) for d in r.iterators.duty_set(duty_iterator_where)]
        #     rx = self.createRoster(tuple([0]+[(duties)]+roster))

        for rosterItem in rosters:
            for r in rosterItem:
                if self.crewlist is None or str(r) in self.crewlist:
                    r = self.createRoster(rosterItem)
                    if r != None:
                        scheduleRosters.append(r)
                    break

        return scheduleRosters

    def createRoster(self, rosterItem):
        rosterItem = rosterItem[1:]

        scheduleHours = list(rosterItem[SCHEDULE_HOURS:])

        # Remove free days from schedule
        (activities, _) = self.activityManager.getActivitiesForCrew(rosterItem[CREW_ID])

        # If the crew has no activities registered at all we assume that this crew shall not be included in the schedule.
        includeThisCrew = True
        if (len(activities) == 0):
            (allActivities, _) = self.activityManager.getAllActivitiesForCrew(rosterItem[CREW_ID])
            if len(allActivities) == 0:
                print "WARNING! No activities for crew %s: skipping schedule. (rank %s)." % (
                rosterItem[CREW_ID], rosterItem[RANK])
                includeThisCrew = False

        scheduleRoster = None
        if includeThisCrew:
            for (code, extent, startTime, endTime) in activities:
                if startTime < self.startDate:
                    startTime = self.startDate
                if endTime > self.endDate:
                    endTime = self.endDate
                while startTime < endTime:
                    offset = int(startTime - self.startDate) / (60 * 24)
                    scheduleHours[offset] = RelTime(0)
                    startTime = startTime.adddays(1)

            scheduleRoster = ScheduleCCSERoster(rosterItem[DUTIES],
                                              rosterItem[CREW_ID],
                                              rosterItem[FIRST_NAME],
                                              rosterItem[LAST_NAME],
                                              rosterItem[EMPNO],
                                              scheduleHours)

        return scheduleRoster


class ScheduleCCSERoster(DataClass):
    """
    A Roster item with schedule values.
    """

    def __init__(self,
                 duties,
                 crewId,
                 firstName,
                 lastName,
                 empNo,
                 scheduleHours):
        self.crewId = crewId
        self.firstName = firstName
        self.lastName = lastName
        self.empNo = empNo

        self.scheduleHours = scheduleHours

    def getScheduledHours(self):
        return self.scheduleHours


class ScheduleRunDataHandler:
    def __init__(self, rd):
        self.rundata = rd
        self.scheduleRunData = self._getScheduleRun()

    def _getScheduleRun(self):
        schedule_run_query = "(&(runtype=SCHEDULE)(admcode=N)(extsys=%s)(firstdate=%s)(lastdate=%s))" % (
        self.rundata.extsys, self.rundata.firstdate, self.rundata.lastdate)
        runid = None
        for run_id_record in sorted(TM.salary_run_id.search(schedule_run_query),
                                    key=attrgetter('releasedate', 'starttime'), reverse=True):
            print "Using schedule time runid %s" % run_id_record.runid
            #            if run_id_record.releasedate == None: FIXME: Remove comments to only use released runs!
            #                continue
            runid = run_id_record.runid
            break

        if runid == None:
            raise SalaryException("No released schedule time run was found for period %s - %s." % (
            self.rundata.firstdate, self.rundata.lastdate))

        return getDailyRecordsFor(runid)

    def getScheduleRunData(self):
        return self.scheduleRunData

    def getLastScheduleDay(self, crewid):
        try:
            maxday = 0
            for (day, value) in self.scheduleRunData[crewid]['000']:  # SCHEDULE_HOURS => 000:
                if day > maxday:
                    maxday = day
            result = self.rundata.firstdate.adddays(maxday)

        except KeyError:
            print "No scheduled time for crewid %s found" % crewid
            result = self.rundata.lastdate.adddays(-1)  # FIXME: crewid not found in db
        return result
