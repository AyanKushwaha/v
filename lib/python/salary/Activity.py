"""
Handle crew activities
"""

import carmensystems.rave.api as R
from tm import TM
from salary.api import getActivityArticleIdMap
from utils.rave import RaveIterator
import salary.conf as conf
from salary.api import SalaryException

class ActivityManager(object):
    """
    This class reads and handles crew activities
    """

    def __init__(self, prefix, context, rundata, startDate, endDate):
        # please note that startDate and endDate must be homebase dates
        self.prefix = prefix
        self.context = context
        self.rundata = rundata
        self.categories = ['CC', 'FC']
        articles = getActivityArticleIdMap("%s*" % prefix, rundata.extsys_for_db(), startDate)
        self.startDate = startDate
        self.endDate = endDate
        self.activityIds = self._makeArticleDict(articles)
        self.crewCategories = self._makeCrewCategoryDict()


    def _makeArticleDict(self, articles):
        articleDict = {}
        for category in self.categories:
            articleDict[category] = {}
        for article in articles:
            for category in self.categories:
                if article.intartid.endswith("_%s" % category):
                    intartid = article.intartid[len(self.prefix):-len(category)-1]
                    articleDict[category][intartid] = (article.extartid, article.extent)
                    break
            else:
                # intartid is common for all crew categories
                for category in self.categories:
                    intartid = article.intartid[len(self.prefix):]
                    articleDict[category][intartid] = (article.extartid, article.extent)

        return articleDict


    def _makeCrewCategoryDict(self):
        crewCatDict = {}

        old_salary_month_start = R.param(conf.startparam).value()
        old_salary_month_end = R.param(conf.endparam).value()
        R.param(conf.startparam).setvalue(self.rundata.firstdate)
        R.param(conf.endparam).setvalue(self.rundata.lastdate)
        try:
            iterator = CrewCategoryIterator(self.rundata)
            rosters = iterator.eval(conf.context)
        finally:
            R.param(conf.startparam).setvalue(old_salary_month_start)
            R.param(conf.endparam).setvalue(old_salary_month_end)

        for roster in rosters:
            if roster.is_pilot and roster.is_cabin:
                raise SalaryException("Crew with empno %s is both CC and FC")
            elif roster.is_pilot:
                crewCatDict[roster.crewid] = ("FC", roster.empno)
            elif roster.is_cabin:
                crewCatDict[roster.crewid] = ("CC", roster.empno)
            else:
                raise SalaryException("Crew with empno %s is neither CC and FC" % roster.empno)
        return crewCatDict


    def _getCrewCategory(self, crewId):
        try:
            (crewCat, _) = self.crewCategories[crewId]
        except KeyError:
            crewCat = 'CC'
            print "WARNING: Could not find crew category for crewid %s. Using %s." % (crewId, crewCat)
        return crewCat


    def _getEmpNo(self, crewId):
        try:
            (_, empNo) = self.crewCategories[crewId]
        except KeyError:
            empNo = crewId
            print "WARNING: Could not find empNo for crewid %s. Using %s." % (crewId, empNo)
        return empNo


    def getActivitiesForCrew(self, crewId):
        crewCat = self._getCrewCategory(crewId)
        empNo = self._getEmpNo(crewId)
        # self.endDate and self.startDate are homebase times. We have to get UTC times to use
        # them for searching activities in the crew_activity table
        period_start_utc = hb2utc(crewId, self.startDate)
        period_end_utc = hb2utc(crewId, self.endDate)

        activitySetFilter = "(|(activity=%s))" % ')(activity='.join(self.activityIds[crewCat].keys())
        crewActivityQuery = "(&(crew=%s)(st<%s)(et>%s)%s)" % (crewId, period_end_utc, period_start_utc, activitySetFilter)

        activities = []
        for activity in TM.crew_activity.search(crewActivityQuery):
            startTime = utc2hb(crewId, activity.st)
            endTime = utc2hb(crewId, activity.et)
            (extartid, extent) = self.activityIds[crewCat][activity.activity.id]
            activities.append((extartid, extent, startTime, endTime))

        return (activities, empNo)


    def getAllActivitiesForCrew(self, crewId):
        crewCat = self._getCrewCategory(crewId)
        empNo = self._getEmpNo(crewId)
        # self.endDate and self.startDate are homebase times. We have to get UTC times to use
        # them for searching activities in the crew_activity table
        period_start_utc = hb2utc(crewId, self.startDate)
        period_end_utc = hb2utc(crewId, self.endDate)
        crewActivityQuery = "(crew=%s)(st<%s)(et>%s)" % (crewId, period_end_utc, period_start_utc)

        activities = []
        for activity in TM.crew_activity.search(crewActivityQuery):
            startTime = utc2hb(crewId, activity.st)
            endTime = utc2hb(crewId, activity.et)
            activities.append((activity.activity.id, startTime, endTime))

        return (activities, empNo)

class BudgetedActivityManager(ActivityManager):

    def __init__(self, context, rundata, startDate, endDate):
        super(self.__class__, self).__init__("BUDG_ACT_", context, rundata, startDate, endDate)

class SchedActivityManager(ActivityManager):

    def __init__(self, context, rundata, startDate, endDate):
        super(self.__class__, self).__init__("F_ACT_", context, rundata, startDate, endDate)

class TcSchedActivityManager(ActivityManager):

    def __init__(self, context, rundata, startDate, endDate):
        super(self.__class__, self).__init__("F_ACT_", context, rundata, startDate, endDate)

class SchedCCSEActivityManager(ActivityManager):

    def __init__(self, context, rundata, startDate, endDate):
        super(self.__class__, self).__init__("F_ACT_", context, rundata, startDate, endDate)

class AbsenceActivityManager(ActivityManager):

    def __init__(self, context, rundata, startDate, endDate):
        super(self.__class__,self).__init__("ABS_ACT_", context, rundata, startDate, endDate)

class CrewCategoryIterator(RaveIterator):
    def __init__(self, rd):
        iterator = RaveIterator.iter('iterators.roster_set',
                                     where=('salary.%%salary_system%%(%s) = "%s"' % (rd.firstdate, rd.extsys_for_rave()),))
        fields = {
            'crewid'  : 'crew.%id%',
            'empno'   : 'crew.%employee_number%',
            'is_cabin': 'crew.%is_cabin%',
            'is_pilot': 'crew.%is_pilot%',
            }
        RaveIterator.__init__(self, iterator, fields)


# From HelperFunctions.py: got error about missing symbol when trying to import the module
def utc2hb(crewid, time):
    """Convert 'time' in UTC to homebase time for 'crewid'."""
    return R.eval('station_localtime(default(fundamental.%%base2station%%(crew_contract.%%base_at_date_by_id%%("%s", %s)), "CPH"), %s)' % (
        crewid, time, time))[0]

# From HelperFunctions.py: got error about missing symbol when trying to import the module
def hb2utc(crewid, time):
    """Convert 'time' in homebase time for 'crewid' to UTC."""
    return R.eval('station_utctime(default(fundamental.%%base2station%%(crew_contract.%%base_at_date_by_id%%("%s", %s)), "CPH"), %s)' % (
        crewid, time, time))[0]
