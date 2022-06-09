
# changelog {{{2
# [acosta:09/014@14:45] Warnings revamped.
# }}}

"""
This is report 32.13.3 Crew Slip
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML
import crewlists.status as status
import utils.exception
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief

from AbsTime import AbsTime
from RelTime import RelTime

from crewlists.replybody import Reply, ReplyError, getReportReply
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator, Entry
from utils.selctx import SingleCrewFilter


# constants =============================================================={{{1
report_name = 'CREWSLIP'
title = "Published Roster"

# functions =============================================================={{{1
def isEmptyMealCode(mealcode):
    if mealcode is None:
        return True
    if mealcode.strip(', ') == '':
        return True
    return False

def getNumberOfDays(st, et):
    """ Returns number of days for multi-day activitiy """
    diff = et.day_floor() - st.day_floor()
    days = diff.split()[0] / 24
    if days == 0:
        days = 1
    return days

# Formatting objects ====================================================={{{1

# basicTable -------------------------------------------------------------{{{2
class basicTable(HTML.table):
    """
    Creates a table with crew information.
    """
    def __init__(self, i, c):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
            'Name',
            'Employee #',
            'Seniority',
            'Cat',
            'Qual',
            'Group',
        )
        self['id'] = "basics"
        self.append(
            c.logname,
            c.empno,
            c.seniority,
            c.cat,
            c.qual.replace(' ',''),
            c.group,
        )


# rules ------------------------------------------------------------------{{{2
class rules(XMLElement):
    """
    Creates a list of broken rules and warnings.
    """
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    def __init__(self, ri, ri2, i):
        XMLElement.__init__(self)
        self.tag = 'div'
        self['id'] = 'rules'
        L = []
        failtexts = set()
        for failure in self.sort(ri.chain('rules')):
            if failure.failtext in failtexts:
                # WP Int-FAT 91 - only show each warning once.
                # This should not be problem, since the kinds of warnings
                # we show are of type license, visa, medical,...
                continue
            F = []
            (sy, sm, sd, ey, em, ed) = (False, False, False, False, False, False)
            if failure.startdate is not None:
                (sy, sm, sd) = failure.startdate.split()[:3]
            if failure.enddate is not None:
                (ey, em, ed) = failure.enddate.split()[:3]
            if sd:
                F.append("%02d" % (sd))
            if sm and sm != i.month and (em and em != sm):
                F.append(self.months[sm])
            if sy and sy != i.year and (ey and ey != sy):
                F.append("%04d" % (ey))
            if ed and (sd and sd != ed):
                F.append("-%02d" % (ed))
            if em and em != i.month:
                F.append(self.months[em])
            if ey and ey != i.year:
                F.append("%04d" % (ey))
            if len(F) > 0:
                F[0] = "[" + F[0]
                F.append("] ")
            F.append(failure.failtext)
            failtexts.add(failure.failtext)
            L.append(XMLElement('li', ''.join(F)))
        warntexts = set()
        for warngroup in ri.chain('pwarnings'):
            for warning in warngroup:
                warntexts.add((warngroup.group, warning.desc))
        for warngroup in ri.chain('warnings'):
            for warning in warngroup:
                warntexts.add((warngroup.group, warning.desc))
        for warngroup in ri2.chain('warnings'):
            for warning in warngroup:
                warntexts.add((warngroup.group, warning.desc))
        for g, d in sorted(warntexts):
            L.append(XMLElement('li', "%s: %s" % (g, d)))
        self.append(XMLElement('h3', 'Warnings'))
        if len(L) > 0:
            self.append(XMLElement('ul', L))

    def sort(self, iter):
        R = [(x.startdate, x.enddate, x) for x in iter]
        R.sort()
        return [x[2] for x in R]


# summary ----------------------------------------------------------------{{{2
class summary(XMLElement):
    def __init__(self, roster):
        XMLElement.__init__(self)
        self.tag = 'table'
        self['id'] = 'summary'

        bh = XMLElement('tr')
        bh.append(XMLElement('th', 'Block hours this month:'))
        bh.append(XMLElement('td', HTML.span_right(roster.blocktime)))
        self.append(bh)

        dh = XMLElement('tr')
        dh.append(XMLElement('th', 'Duty hours this month:'))
        dh.append(XMLElement('td', HTML.span_right(roster.dutytime)))
        self.append(dh)


# resultTable ------------------------------------------------------------{{{2
class resultTable(HTML.table):
    """
    Creates a table with flight activities for the chosen crew.
    """
    def __init__(self, i, r):
        """ <table>...</table> where activities are listed. """
        # i is input data
        # r is a RaveIterator
        HTML.table.__init__(self,
            'Day',
            'Date',
            'CI/CO',
            'Duty',
            'A/C',
            'Departure',
            'Arrival',
            HTML.span_right('Block h'),
            HTML.span_right('Stop'),
            'Meal s',
            HTML.span_right('Rest'),
            HTML.span_right('FDP'),
            HTML.span_right('Duty'),
        ) 
        self['id'] = "roster"
        self.last_date = (0, 0, 0)
        self.dayshift = False
        for a in r:
            # reset
            dutytime = fdp = rest = actype = blocktime = stop = meal = cio1 = cio2 = ""

            # Split muli-day activities
            numDays = getNumberOfDays(a.std, a.sta)
            multiday = (numDays > 1)
            for dayno in range(numDays):
                starttime = a.std + RelTime(dayno, 0, 0)
                endtime = a.sta - RelTime(numDays - dayno - 1, 0, 0)
                if endtime < i.firstDate or starttime > i.lastDate:
                    continue
                dutyname = a.name

                if a.last_in_duty:
                    if str(a.dutytime) != '0:00':
                        dutytime = a.dutytime
                    if str(a.fdp) !=  '0:00':
                        fdp = "%02d:%02d" % a.fdp.split()
                        fdp += a.extended
                    if not a.rest is None:
                        rest = a.rest + RelTime(numDays - dayno - 1, 0, 0)

                # We have to adjust the arrival time in case of ground duty ending 0:00 another day.
                sta = "%02d%02d" % endtime.split()[3:5]
                sta_abstime = endtime
                if a.is_flight_duty:
                    actype = a.actype
                    blocktime = a.blocktime
                    if a.stop is not None:
                        stop = a.stop
                    if a.meal is not None:
                        meal = ('', 'Yes')[a.meal]
                else:
                    if endtime.split()[3:5] == (0, 0):
                        # Ground duty will end 24:00 previous day instead of 0:00
                        sta = "2400"
                        sta_abstime = endtime - RelTime(0, 1)

                std = "%02d%02d" % starttime.split()[3:5]
                # Do not display station and time for off-duty activities
                depStr = ""
                desStr = ""
                if a.is_on_duty:
                    depStr = "%s %s" % (a.adep, std)
                    desStr = "%s %s" % (sta, a.ades)
                        
                # Add 'meal activity' if required
                if a.is_flight_duty and not isEmptyMealCode(a.meal_code) and a.meal_code not in ('X','V'):
                    (weekday, day) = self.weekday(a.std)
                    station = a.adep
                    self.append(
                        weekday,
                        day,
                        "",
                        a.meal_code,
                        "",
                        #"%s %s" % (station, '1200'),
                        #"%s %s" % ('1201', station),
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    )

                # Check if activity spans more than one day.
                if starttime.split()[:3] != sta_abstime.split()[:3]:
                    # date differs
                    if a.is_flight_duty:
                        if a.first_in_trip or a.last_in_trip:
                            if a.first_in_trip:
                                cio1 = "%02d%02d &laquo;" % a.checkin.split()[3:5]
                            if a.last_in_trip:
                                cio2 = "&raquo; %02d%02d" % a.checkout.split()[3:5]

                    (weekday, day) = self.weekday(starttime)
                    self.append(
                        weekday,
                        day,
                        cio1,
                        dutyname,
                        actype,
                        #"%s %02d%02d" % (a.adep, a.std.split()[3:5]),
                        depStr,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    )
                    (weekday, day) = self.weekday(sta_abstime)
                    self.append(
                        weekday,
                        day,
                        cio2,
                        "",
                        "",
                        "",
                        desStr,
                        HTML.span_right(blocktime),
                        HTML.span_right(stop),
                        meal,
                        HTML.span_right(rest),
                        HTML.span_right(fdp),
                        HTML.span_right(dutytime)
                    )

                else:
                    # Activity starts and ends on the same day.
                    if a.is_flight_duty:
                        if a.first_in_trip or a.last_in_trip:
                            if a.first_in_trip:
                                ci = "%02d%02d" % a.checkin.split()[3:5]
                            if a.last_in_trip:
                                co = "%02d%02d" % a.checkout.split()[3:5]
                            if a.first_in_trip and a.last_in_trip:
                                cio1 = ci + " " + co
                            elif a.first_in_trip:
                                cio1 = ci + " &laquo;"
                            else:
                                cio1 = "&raquo; " + co

                    (weekday, day) = self.weekday(starttime)
                    self.append(
                        weekday,
                        day,
                        cio1,
                        dutyname,
                        actype,
                        depStr,
                        desStr,
                        HTML.span_right(blocktime),
                        HTML.span_right(stop),
                        meal,
                        HTML.span_right(rest),
                        HTML.span_right(fdp),
                        HTML.span_right(dutytime)
                    )

                # Add 'meal activity' if required, X and V are after the flight.
                if a.is_flight_duty and not isEmptyMealCode(a.meal_code) and a.meal_code in ('X','V'):
                    (weekday, day) = self.weekday(a.sta)
                    station = a.adep
                    self.append(
                        weekday,
                        day,
                        "",
                        a.meal_code,
                        "",
                        #"%s %s" % (station, '1200'),
                        #"%s %s" % ('1201', station),
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    )


    def weekday(self, atime):
        result = ("", "")
        how = atime.time_of_week().split()[0]
        wd = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')[how // 24]
        d = atime.split()[:3]
        if d != self.last_date:
            self.dayshift = True
            result = (wd, "%02d" % (atime.split()[2]))
        else:
            self.dayshift = False
        self.last_date = d
        return result

    def append(self, *columns):
        # copied from rs.table, but odd/even switching removed, it is taken
        # care of above instead.
        row = HTML.tr(HTML.td, *columns)
        if self.dayshift:
            row['class'] = 'dayshift'
        self.tbody.append(row)


# RaveIterator help classes =============================================={{{1

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """ Evalutated on a chain. Used by RaveIterator. """
    def __init__(self, searchDate):
        self.fields = {
            'id': 'report_crewlists.%crew_id%',
            'empno': 'report_crewlists.%crew_empno%',
            'logname': 'report_crewlists.%%crew_logname_at_date%%(%s)' % (searchDate),
            'seniority': 'report_crewlists.%%crew_seniority%%(%s)' % (searchDate),
            'cat': 'report_crewlists.%%crew_title_rank%%(%s)' % (searchDate),
            'group': 'report_crewlists.%%crew_group_type%%(%s)' % (searchDate),
            'qual': 'report_crewlists.%%crew_ac_qlns%%(%s)' % (searchDate),
            'warn': 'report_crewlists.%warn_short%',
            'blocktime': 'report_crewlists.%%bt_in_month%%(%s)' % (searchDate),
            'dutytime': 'report_crewlists.%%dt_in_month%%(%s)' % (searchDate),
        }


# LegInfo ----------------------------------------------------------------{{{2
class LegInfo:
    """ Evalutated on a leg. Used by RaveIterator. """
    fields = {
        'actype': 'report_crewlists.%leg_ac_type%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'blocktime': 'report_crewlists.%leg_block_time_scheduled%',
        'checkin': 'report_crewlists.%duty_start_lt%',
        'checkout': 'report_crewlists.%duty_end_scheduled_lt%',
        'dutytime': 'report_crewlists.%duty_time%',
        'first_in_trip': 'report_crewlists.%leg_is_first_in_trip%',
        'last_in_trip': 'report_crewlists.%leg_is_last_in_trip%',
        'last_in_duty': 'report_crewlists.%leg_is_last_in_duty%',
        'is_flight_duty': 'report_crewlists.%leg_is_flight%',
        'meal': 'report_crewlists.%leg_is_meal_stop%',
        'meal_code': 'report_crewlists.%rm_meal_code%',
        'is_on_duty': 'report_crewlists.%leg_is_on_duty%',
        'name': 'report_crewlists.%pr_name%',
        "fdp": "report_crewlists.%fdp_time%",
        "extended": "report_crewlists.%extended_fdp_flag%",
        'rest': 'default(report_crewlists.%duty_rest_time%, report_crewlists.%trip_rest_time%)',
        'sta': 'report_crewlists.%leg_sta_lt%',
        'std': 'report_crewlists.%leg_std_lt%',
        'stop': 'report_crewlists.%stop_duration_scheduled%',
        # these three are for briefing/debriefing
        'is_simulator': 'report_crewlists.%leg_is_simulator%',
        'leg_checkin': 'report_crewlists.%leg_check_in%',
        'leg_checkout': 'report_crewlists.%leg_check_out%',
    }



# InputData =============================================================={{{1
class InputData:
    months = ('January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December')
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey, m, y) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.", payload=getReportReply(report_name, parameters))
        try:
            M = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            self.month = M.index(m.upper()) + 1
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Month not usable.", payload=getReportReply(report_name, parameters))
        try:
            self.year = int(y)
            self.firstDate = AbsTime(self.year, self.month, 1, 0, 0)
            if self.month == 12:
                self.lastDate = AbsTime(self.year + 1, 1, 1, 0, 0)
            else:
                self.lastDate = AbsTime(self.year, self.month + 1, 1, 0, 0)
            self.nextMonth = self.lastDate.addmonths(1)
            self.lastMonth = self.lastDate.addmonths(6)
            self.monthFull = self.months[self.month - 1]
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Date not usable.", payload=getReportReply(report_name, parameters))
        self.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % (self.extperkey))[0]
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, parameters))


# Add simulator briefing and debriefing =================================={{{1

# ExtEntry ---------------------------------------------------------------{{{2
class ExtEntry(extiter.ExtEntry):
    def chain(self, name=None):
        if name == 'legs':
            return extiter.ExtEntry.chain(self, name)
        return Entry.chain(self, name)


# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    class Briefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkin) > 0):
                raise briefdebrief.BriefDebriefException('Not a simulator')
            self.__dict__ = a.__dict__.copy()
            self.name = 'B' + a.name[1:]
            self.std = a.std - a.leg_checkin
            self.sta = a.std
            self.stop = None
            self.last_in_duty = False

    class Debriefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkout) > 0):
                raise briefdebrief.BriefDebriefException('Not a simulator')
            self.__dict__ = a.__dict__.copy()
            self.name = 'D' + a.name[1:]
            self.std = a.sta
            self.sta = a.sta + a.leg_checkout
            self.stop = None
            if a.last_in_duty:
                a.last_in_duty = False


# run ===================================================================={{{1
def run(*a):
    """ returns string containing the report """
    try:
        i = InputData(a)

        where_expr_leg = (
            'report_crewlists.%%leg_end_hb%% > %s' % (i.firstDate),
            'report_crewlists.%%leg_start_hb%% < %s' % (i.lastDate),
        )
        where_expr_rules = (
            rave.first(rave.Level.atom(), 'leg.%%start_hb%% < %s' % i.lastDate),
            rave.first(rave.Level.atom(), 'leg.%%end_hb%% > %s' % i.firstDate),
        )
        sort_expr_rules = rave.first(rave.Level.atom(), 'leg.%start_utc%')

        # First loop over roster set (1 item)
        ri = extiter.ExtRaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='report_crewlists.%%crew_empno%% = "%s"' % (i.extperkey)),
            CrewInfo(i.firstDate), modifier=SimBriefDebriefExtender, entry=ExtEntry)

        # Evaluate legs, rules and warnings
        li = RaveIterator(RaveIterator.iter('iterators.leg_set',
            where=where_expr_leg), LegInfo())
        rui = RaveIterator(
                RaveIterator.rulefailure(where=where_expr_rules,
                    group=rave.group("report_crewlists.crewslip"),
                    sort_by=sort_expr_rules))
        wi = RaveIterator(
                RaveIterator.times('report_crewlists.%t_warn_sections%',
                    where='report_crewlists.%warn_has_warn_in_section%'), 
                {
                    'group': 'report_crewlists.%warn_group%',
                })
        wgi = RaveIterator(
                RaveIterator.times('report_crewlists.%t_warn_prio%',
                    where='report_crewlists.%warn_has_prio%'),
                {
                    'desc': 'report_crewlists.%warn_desc%',
                })
        wi.link(wgi)
        pwi = RaveIterator(
                RaveIterator.times('report_crewlists.%document_expiry_group_count%'),
                {
                    'group': 'report_crewlists.%%document_expiry_group%%(%s)' % ('fundamental.%py_index%'),
                })
        pwgi = RaveIterator(
                RaveIterator.times('report_crewlists.%%document_expiry_count%%(%s, %s)' % (i.firstDate, 'fundamental.%py_index%'),
                    where='report_crewlists.%%has_document_expiry_warning%%(%s, %s)' % (i.firstDate, i.nextMonth)),
                {
                    'desc': 'report_crewlists.%%document_expiry_warning%%(%s, %s)' % (i.firstDate, i.nextMonth),
                })
        pwi.link(pwgi)
        ri.link(legs=li, rules=rui, warnings=wi, pwarnings=pwi)

        # Set parameter to limit search for warnings within start -> end
        start_param='crew_warnings.%user_warning_period_start%'
        end_param='crew_warnings.%user_warning_period_end%'
        old_wp_start = rave.param(start_param).value()
        rave.param(start_param).setvalue(i.firstDate)
        old_wp_end = rave.param(end_param).value()
        rave.param(end_param).setvalue(i.lastDate)
        
        # First evaluation, the lot, including warnings for the first period.
        the_context = SingleCrewFilter(i.crewid).context()
        rosters = ri.eval(the_context)

        # New evaluation with warnings for the second period (to be added to
        # previous evaluation).
        rave.param(start_param).setvalue(i.lastDate)
        rave.param(end_param).setvalue(i.lastMonth)
        ri2 = RaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='report_crewlists.%%crew_empno%% = "%s"' % (i.extperkey)),
            CrewInfo(i.firstDate))
        ri2.link(warnings=wi)
        rosters2 = ri2.eval(the_context)

        # Restore parameters to their original values
        rave.param(start_param).setvalue(old_wp_start)
        rave.param(end_param).setvalue(old_wp_end)

        try:
            roster = rosters[0]
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, a))

        # if this fails, then it is an unexpected error, which is handled below
        roster2 = rosters2[0]
        legs = roster.chain('legs')

        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', '%s: %s %s (local time)' % (title, i.monthFull, i.year)))
        html.append(XMLElement('h2', 'BASICS'))
        html.append(basicTable(i, roster))
        html.append(XMLElement('h2', 'OVERVIEW'))
        html.append(rules(roster, roster2, i))
        html.append(summary(roster))
        rosterHead = XMLElement('h2', 'ROSTER FOR %s %s' % (i.monthFull, i.year))
        rosterHead['class'] = 'floatstop'
        html.append(rosterHead)
        html.append(resultTable(i, legs))

        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))


# main ==================================================================={{{1
# for basic tests
def bit():
#    print run(3, '29228', 'NOV', 2020)
    print run(3, '11799', 'NOV', 2020)

if __name__ == '__main__':
    import profile
    profile.run("bit()")



# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
