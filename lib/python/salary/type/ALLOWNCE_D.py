"""
Daily reported allowances
"""


import logging
import salary.conf as conf
import salary.run as run
import carmensystems.rave.api as rave
import salary.type.OVERTIME as overtime
from salary.Overtime import OvertimeRoster
import salary.type.COMPDAYS as compdays
import salary.type.TEMP_CREW as tempcrew
from RelTime import RelTime
from salary.api import SalaryException, zap


log = logging.getLogger('salary.type.ALLOWNCE_D')


class AllowanceRoster(object):
    """
    Class fields structure:
    AllowanceRoster:
        crewid
        empno
        articles - dict:
            article: (offset, value)
    """

    def __init__(self, crewid, empno):
        self.crewid = crewid
        self.empno = empno
        self.articles = {}

    def add_data(self, article, offset, value):
        """
        Creates a new item in self.articles with a specified offset and writes data there,
        or finds an existing item in self.articles with a specified offset and adds
        a new value to an old one.
        """
        if not (article in self.articles.keys()):
            self.articles[article] = [(offset, value)]
        else:
            # add to existing values if any
            for i in xrange(len(self.articles[article])):
                if self.articles[article][i][0] == offset:
                    old_value = self.articles[article][i][1]
                    self.articles[article][i] = (offset, old_value + value)
                    break
            else:
                self.articles[article].append((offset, value))

    def get_value(self, article, offset):
        if article in self.articles.keys():
            for i in xrange(len(self.articles[article])):
                if self.articles[article][i][0] == offset:
                    return self.articles[article][i][1]
        return None

    def set_value(self, article, offset, value):
        if not (article in self.articles.keys()):
            self.articles[article] = [(offset, value)]
        else:
            # update existing values if any
            for i in xrange(len(self.articles[article])):
                if self.articles[article][i][0] == offset:
                    self.articles[article][i] = (offset, value)
                    break
            else:
                self.articles[article].append((offset, value))

    def remove_all_matching(self, article=None, offset=None):
        """
        Removes every item matching parameters. article=None means every article,
        offset=None means every offset.
        """
        if article != None:
            if offset != None:
                for item in self.articles[article]:
                    if item[0] == offset:
                        self.articles[article].remove(item)
            else:
                self.articles[article].remove(item)
        else:
            if offset != None:
                for article in self.articles.keys():
                    for item in self.articles[article]:
                        if item[0] == offset:
                            self.articles[article].remove(item)
            else:
                for article in self.articles.keys():
                    for item in self.articles[article]:
                        self.articles[article].remove(item)


class DailyAllowanceRun(run.GenericRun):
    def __init__(self, rundata, articles):
        super(DailyAllowanceRun, self).__init__(rundata, articles)
        self.accumulated_rosters = []

    def run(self):
        runid = super(DailyAllowanceRun, self).run()
        return runid

    def _accumulate(self, crewid, empno, article, offset, value):
        # find an existing roster or create a new one
        for roster in self.accumulated_rosters:
            if roster.crewid == crewid:
                break
        else:
            roster = AllowanceRoster(crewid, empno)
            self.accumulated_rosters.append(roster)
        # a roster we work with is now in a "roster" variable
        roster.add_data(article, offset, value)

    def _move_OT_CO_LATE_FC(self):
        # day offset:   -1  0  1  2  3  4  5  6  7  8  9  10
        # value:        [ ][ ][1][ ][2][2][ ][ ][1][ ][ ][1]
        # will give us: [ ][ ][0][1][0][0][2][ ][0][1][ ][0]
        for roster in self.accumulated_rosters:
            if 'OT_CO_LATE_FC' in roster.articles.keys():
                last_passed_empty_offset = None
                do_update = False
                # from number of days in period - 1 down to -1
                for offset in xrange(int((self.rundata.lastdate - self.rundata.firstdate) / RelTime(24, 0)) - 1, -2, -1):
                    value = roster.get_value('OT_CO_LATE_FC', offset)
                    if not value:
                        last_passed_empty_offset = offset
                        do_update = True
                    else:
                        roster.set_value('OT_CO_LATE_FC', offset, 0)
                        if do_update:
                            roster.set_value('OT_CO_LATE_FC', last_passed_empty_offset, value)
                            do_update = False

    def _remove_offset_minus_one(self):
        for roster in self.accumulated_rosters:
            roster.remove_all_matching(article=None, offset=-1)

    def rosters(self):
        old_firstdate = self.rundata.firstdate
        old_lastdate = self.rundata.lastdate
        # launch a pair of runs for every day in period
        # except for the -1 day - only overtime will be run for it
        for offset in xrange(-1, int((self.rundata.lastdate - self.rundata.firstdate) / RelTime(24, 0))):
            # set rundata borders to one day
            self.rundata.firstdate = old_firstdate + RelTime(24 * offset, 0)
            self.rundata.lastdate = self.rundata.firstdate + RelTime(24, 0)

            # run an overtime run
            log.debug('running an Overtime subrun for %s' % (str(self.rundata.firstdate)))
            s3_overtime_run = overtime.S3(self.rundata)
            try:
                s3_overtime_run.run(create_report=False)
            except SalaryException as e:
                # no rosters is not an error here
                if str(e)[:len("No rosters qualified for ")] == "No rosters qualified for ":
                    pass
                else:
                    raise
            else:
                # add information to accumulated rosters
                for roster in s3_overtime_run.accumulated_rosters:
                    self._accumulate(roster.crewId, roster.empNo, 'OTPT', offset, self.OTPT(roster))
                    self._accumulate(roster.crewId, roster.empNo, 'OT_CO_LATE_FC', offset, self.OT_CO_LATE_FC(roster))
                    self._accumulate(roster.crewId, roster.empNo, 'SNGL_SLIP_LONGHAUL', offset, self.SNGL_SLIP_LONGHAUL(roster))
                    self._accumulate(roster.crewId, roster.empNo, 'DUTYP', offset, self.DUTYP(roster))
                    # self._accumulate(roster.crewId, roster.empNo, 'TEMPCREW', offset, self.TEMPCREW(roster))
            # delete the overtime run - we do not need it anymore
            if s3_overtime_run.rundata.runid != None:
                zap(s3_overtime_run.rundata.runid)
            # The offset -1 day will be used in OT_CO_LATE_FC calculation later. Only an overtime
            # run will be run for that day.
            if offset == -1:
                continue
            
            # run a compdays run
            log.debug('running a Compdays subrun for %s' % (str(self.rundata.firstdate)))
            s3_compdays_run = compdays.S3(self.rundata)
            try:
                s3_compdays_run.run()
            except SalaryException as e:
                # no rosters is not an error here
                if str(e)[:len("No rosters qualified for ")] == "No rosters qualified for ":
                    pass
                else:
                    raise
            else:
                # compdays run gives us an iterator instead of a list of rosters
                for roster in s3_compdays_run.accumulated_rosters:
                    self._accumulate(roster.crewid, roster.empno, 'BOUGHT', offset, -self.BOUGHT(roster))
                    self._accumulate(roster.crewid, roster.empno, 'BOUGHT_BL', offset, -self.BOUGHT_BL(roster))
                    self._accumulate(roster.crewid, roster.empno, 'BOUGHT_FORCED', offset, -self.BOUGHT_FORCED(roster))
                    self._accumulate(roster.crewid, roster.empno, 'BOUGHT_8', offset, -self.BOUGHT_8(roster))
                    self._accumulate(roster.crewid, roster.empno, 'F0_F3', offset, self.F0_F3(roster))
                    self._accumulate(roster.crewid, roster.empno, 'F31_F33', offset, self.F31_F33(roster))
                    self._accumulate(roster.crewid, roster.empno, 'F7S', offset, self.F7S(roster))
                    self._accumulate(roster.crewid, roster.empno, 'SOLD', offset, self.SOLD(roster))
            # delete the compdays run - we do not need it anymore
            if s3_compdays_run.rundata.runid != None:
                zap(s3_compdays_run.rundata.runid)

        self.rundata.firstdate = old_firstdate
        self.rundata.lastdate = old_lastdate

        # now run a TEMP_CREW run for the entire period and take tempCrewHoursDaily from it
        log.debug('running at Tempcrew subrun for %s - %s' % (str(self.rundata.firstdate), str(self.rundata.lastdate)))
        s3_tempcrew_run = tempcrew.S3(self.rundata)
        try:
            s3_tempcrew_run.run()
        except SalaryException as e:
            # no rosters is not an error here
            if str(e)[:len("No rosters qualified for ")] == "No rosters qualified for ":
                pass
            else:
                raise
        else:
            for roster in s3_tempcrew_run.accumulated_rosters:
                for offset in xrange(int((self.rundata.lastdate - self.rundata.firstdate) / RelTime(24, 0))):
                    self._accumulate(roster.crewId, roster.empNo, 'TEMPCREW', offset, self.TEMPCREW(roster, offset))
        # delete the tempcrew run - we do not need it anymore
        if s3_tempcrew_run.rundata.runid != None:
            zap(s3_tempcrew_run.rundata.runid)

        # OT_CO_LATE_FC values should be moved from production days to following F-days. So here we move them.
        self._move_OT_CO_LATE_FC()

        # remove "offset -1" items - they should not be exported
        self._remove_offset_minus_one()

        return self.accumulated_rosters

    def save_run(self, rosters):
        for roster in rosters:
            for article in self.articles:
                if article in roster.articles.keys():
                    total = 0
                    for (offset, value) in roster.articles[article]:
                        if value:
                            self.save_extra(roster, article, value, offset)
                            total += value
                    self.save(roster, article, total)

    def save(self, rec, article, value):
        extartid = self.articleCodes[article]
        articleType = self.get_article_type(article)
        if articleType != None:
            extartid = extartid + ':' + articleType
        self.data.append(rec.crewid, rec.empno, extartid, value)

    def save_extra(self, rec, article, value, offset):
        extartid = self.articleCodes[article]
        self.extradata.append(rec.crewid, extartid + "%02d" % offset, value)

    def _OTPT(self, rec):
        return self.hours100(rec.getCalendarMonthPartTimeExtra())

    def OTPT(self, rec):
        if rec.isFlightCrew:
            return self._OTPT(rec)
        else:
            if rec.getMertidParttimeCc() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCc())
            elif rec.getMertidParttimeCcLong() > RelTime(0):
                return self.hours100(rec.getMertidParttimeCcLong())
            else:
                return 0

    def OT_CO_LATE_FC(self, rec):
        """This overtime is applied to all FD except CJ incl. SK.  Ref Jira SKCMS-691"""
        # result is being multiplied by 2 as we need a number of half-hours here
        return rec.get_OT_FD_hours100_netto() * 2

    def SNGL_SLIP_LONGHAUL(self, rec):
        if rec.isFlightCrew:
            return self.times100(rec.getSnglSlipLonghaul())
        else:
            return 0

    def DUTYP(self, rec):
        """ Duty pass SH, Duty pass LH, CO after free weekend"""
        if rec.isCC4EXNG:
            return 0
        return self.hours100((rec.getDutyPass() or RelTime(0)) + 
            (rec.getLateCheckout() or RelTime(0)))

    def BOUGHT(self, rec):
        return rec.bought

    def BOUGHT_BL(self, rec):
        return rec.bought_bl

    def BOUGHT_FORCED(self, rec):
        return rec.bought_forced

    def BOUGHT_8(self, rec):
        return rec.bought_8

    def F0_F3(self, rec):
        return rec.f0_f3

    def F31_F33(self, rec):
        return rec.f31_f33

    def F7S(self, rec):
        return rec.f7s

    def TEMPCREW(self, rec, offset):
        return self.hours100(rec.getTempCrewHoursDaily()[offset])

    def SOLD(self, rec):
        return rec.sold


class S3(DailyAllowanceRun):
    def __init__(self, rundata):
        articles = ['OTPT', 'OT_CO_LATE_FC', 'BOUGHT_FORCED', 'BOUGHT', 'BOUGHT_8', 'SNGL_SLIP_LONGHAUL', 'F0_F3', 'TEMPCREW', 'DUTYP', 'BOUGHT_BL', 'F7S', 'F31_F33', 'SOLD']
        DailyAllowanceRun.__init__(self, rundata, articles)

    def __str__(self):
        return "Daily reported allowances for Swedish crew"
