"""
Swedish salary system.
Absence calculation.
"""

import carmensystems.rave.api as R
from utils.rave import RaveIterator
from utils.RaveData import DataClass
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
from time import clock
import carmensystems.rave.api as rave
from tm import TM
import salary.conf as conf
import salary.api as api
from salary.Schedule import ScheduleManager
from salary.Activity import AbsenceActivityManager
from utils.performance import clockme, log


# utc2hb -----------------------------------------------------------------{{{2
# From HelperFunctions: got error about missing symbol when trying to import the module
def utc2hb(crewid, time):
    """Convert 'time' in UTC to homebase time for 'crewid'."""
    return R.eval('station_localtime(default(fundamental.%%base2station%%(crew_contract.%%base_at_date_by_id%%("%s", %s)), "CPH"), %s)' % (
        crewid, time, time))[0]


(   DUTIES ,
    CREW_ID ,
    FIRST_NAME ,
    LAST_NAME ,
    EMPNO ,
    IS_TEMPORARY,
    RANK,
    TEMP_CREW_ILL_HOURS) = range(8)
ROSTER_VALUES = ('report_common.%crew_id%',
                 'report_common.%crew_firstname%',
                 'report_common.%crew_surname%',
                 'report_common.%employee_number_salary%',
                 'report_overtime.%is_temporary%',
                 'crew.%rank%',
                 )


DUTY_VALUES = ('report_overtime.%overtime_month_start%',
               'report_overtime.%overtime_month_end%')


class AbsenceManager:
    """
    A class that creates and holds AbsenceRosters.
    """

    def __init__(self, rundata, context, iterator='iterators.roster_set', crewlist=None):
        self.context = context
        self.rosterIterator = iterator
        self.crewlist = crewlist
        self.startDate = R.param(conf.startparam).value()
        self.endDate = R.param(conf.endparam).value()
        self.rundata = rundata
        self.activityManager = AbsenceActivityManager(self.context, self.rundata, self.startDate, self.endDate)

    def _getOverlap(self, (startTime1, endTime1), (startTime2, endTime2)):
        startTime = max(startTime1, startTime2)
        endTime = min(endTime1, endTime2)
        return (startTime, endTime)

    def _getTempCrewAbsence(self):
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
        while(dt < self.endDate):
            hour_values.append("report_overtime.%%temp_crew_ill_hours%%(%s)" % dt)
            dt = dt.adddays(1)
        roster_values = list(ROSTER_VALUES) + hour_values
 
        duty_iterator_where = 'duty.%is_on_duty% or duty.%is_privately_traded%'
        duty_iterator = R.iter('iterators.duty_set', where=duty_iterator_where)
        duty_iteration = R.foreach(duty_iterator, *DUTY_VALUES)
        roster_iteration = R.foreach(self.rosterIterator, duty_iteration, *roster_values)
        rosters, = R.eval(self.context, roster_iteration)

        crewAbsence = {} 
        for roster in rosters:
            roster = roster[1:]
            if roster[IS_TEMPORARY]:
                crewAbsence[roster[CREW_ID]] = roster[TEMP_CREW_ILL_HOURS:]
        return crewAbsence

    def getScheduleRosters(self):
        # part of the "interface"
        where_expr=('salary.%%salary_system%%(%s) = "%s"' % (self.rundata.firstdate, self.rundata.extsys_for_rave()),
                    'not salary.%crew_excluded%',
                    'not report_overtime.%is_temporary%',
                    'not crew.%%is_retired_at_date%%(%s)' % self.rundata.firstdate)
        salary_iterator = rave.iter('iterators.roster_set', where=where_expr)

        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(conf.startparam).value()
        rave.param(conf.startparam).setvalue(self.rundata.firstdate)
        old_salary_month_end = rave.param(conf.endparam).value()
        rave.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            rosters = ScheduleManager(self.rundata, conf.context, salary_iterator).getScheduleRosters()
        finally:
            rave.param(conf.startparam).setvalue(old_salary_month_start)
            rave.param(conf.endparam).setvalue(old_salary_month_end)
        if len(rosters) == 0:
            raise api.SalaryException("No matching rosters found.")
        return rosters


    def getAbsenceRosters(self):

        def append_unique(lst, value):
            if not (value in lst):
                lst.append(value)

        one_day = RelTime('24:00')
        # we will take only crewIDs from these
        scheduleRosters = self.getScheduleRosters()
        tempCrewAbsenceTimes = self._getTempCrewAbsence()

        absenceRosters = []

        crews = [sr.crewId for sr in scheduleRosters] + tempCrewAbsenceTimes.keys()

        for crewid in crews:
            if self.crewlist is None or crewid in self.crewlist:
                crew_daily = {}
                (activities, extperkey) = self.activityManager.getActivitiesForCrew(crewid)
                for (extartid, extent, startTime, endTime) in activities:
                    print '12455: AbsenceManager.getAbsenceRosters: crewid = %s, extartid = %s, extent = %s, startTime = %s, endTime = %s, self.startDate = %s, self.endDate = %s' % (str(crewid), str(extartid), str(extent), str(startTime), str(endTime), str(self.startDate), str(self.endDate))
                    if startTime < self.startDate:
                        startTime = self.startDate
                        print '12455: AbsenceManager.getAbsenceRosters: startTime changed to %s' % (str(startTime))
                    if endTime > self.endDate:
                        endTime = self.endDate
                        print '12455: AbsenceManager.getAbsenceRosters: endTime changed to %s' % (str(endTime))
                    # since endTime is not included into the activity time,
                    # we substract 0:01 to make endTime the last minute of
                    # the activity
                    endTime = endTime - RelTime('0:01')
                    print '12455: AbsenceManager.getAbsenceRosters: endTime decreased by 0:01 is now %s' % (str(endTime))
                    if not extartid in crew_daily:
                        crew_daily[extartid] = []

                    day_first = int((startTime - self.startDate) / one_day)
                    day_last = int((endTime - self.startDate) / one_day)
                    print '12455: AbsenceManager.getAbsenceRosters: day_first = %s, day_last = %s' % (str(day_first), str(day_last))

                    for day in range(day_first, day_last + 1):
                        append_unique(crew_daily[extartid], (day, 800))

                print '12455: AbsenceManager.getAbsenceRosters: crew_daily = %s' % (str(crew_daily))
                absenceRosters.append(AbsenceRoster(crewid, extperkey, crew_daily))

        return absenceRosters


class AbsenceRoster(DataClass):
    """
    A Roster item with absence values.
    """

    def __init__(self, crewId, empNo, absenceHours):
        self.crewId = crewId
        self.absenceHours = absenceHours
        self.empNo = empNo

    def getAbsenceHours(self):
        return self.absenceHours
