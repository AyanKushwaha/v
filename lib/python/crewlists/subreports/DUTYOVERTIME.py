"""
This is report 32.13 Duty Overtime Report.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML               
import crewlists.status as status
import utils.exception
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief
import salary.ec.ECOvertime as Overtime

from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime
from RelTime import RelTime
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator, Entry
from utils.selctx import SingleCrewFilter
from utils.divtools import default as D


# constants =============================================================={{{1
report_name = 'DUTYOVERTIME'
title = "Duty Overtime"

# Start of salary month parameter
startparam = 'salary.%salary_month_start_p%'

# End of salary month parameter
endparam = 'salary.%salary_month_end_p%'


# XMLElement classes ====================================================={{{1

# infoTable --------------------------------------------------------------{{{2
class infoTable(HTML.table):
    """
    Creates a table with crew information.
    """
    def __init__(self, i, c):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
            'Employee no',
            'Name',
            'Year',
            'Salary Month'
        )
        self['id'] = "basics"
        self.append(
            c.empno,
            c.logname,
            "%04d" % (i.year),
            "%02d" % (i.month)
        )


# otTable ----------------------------------------------------------------{{{2
class otTable(HTML.table):
    """
    Creates a table with overtime.
    """
    def __init__(self, i, r):
        """ <table>...</table> where activities are listed. """
        # i is input data
        # r is a RaveIterator
        HTML.table.__init__(self,
            'Date',
            'Duty',
            'Activity',
            'From',
            'To',
            'STD',
            'ATD',
            'STA',
            'ATA',
            'Duty time',
            'Block time',
            '',
            'Overtime',
            ''
        )
        self['id'] = "details"
        self.append("","","","","","","","","",
                    "","","Type","Duty time","Overtime")
        for d in r.chain():
            for a in d.chain():
                if a.std >= i.firstDate and a.std < i.lastDate:
                    self.append(
                        str(a.udor).split()[0],
                        a.duty,
                        a.fd,
                        a.adep,
                        a.ades,
                        "%02d:%02d" % a.std.split()[3:5],
                        ('', "%02d:%02d" % a.atd.split()[3:5])[bool(a.is_flight)],
                        "%02d:%02d" % a.sta.split()[3:5],
                        ('', "%02d:%02d" % a.ata.split()[3:5])[bool(a.is_flight)],
                        ("", formatTime(d.duty_time))[bool(a.is_last_in_duty)],
                        ("", formatTime(a.blockhrs))[a.blockhrs is not None],
                        a.ottype,
                        a.otduty,
                        a.ot,
                    )
        ot = formatTime(r.ot)
        bt = formatTime(r.bt)
        dt = formatTime(r.dt)
        mt = ""
        if r.mertid and int(r.mertid):
            mt = " +%s" % r.mertid
        self.append("","<b>TOTAL:</b>","","","","","","","",
                    "<b>%s</b>" % dt,"<b>%s</b>" % bt,"","","<b>%s%s</b>" % (ot,mt))


# allowTable -------------------------------------------------------------{{{2
class allowTable(HTML.table):
    """
    Creates a table with allowances.
    """
    def __init__(self, i, r):
        """ <table>...</table> where activities are listed. """
        # i is input data
        # r is a RaveIterator
        HTML.table.__init__(self,
            'Date',
            'Duty',
            'Activity',
            'From',
            'To',
            'STD',
            'ATD',
            'STA',
            'ATA',
            'MDC SH',
            'MDC LH',
            'SCC',
            'SCC NP',
            'Min RestH',
            'Min RestL'
        )
        self['id'] = "details"
        for d in r.chain():
            for a in d.chain():
                if a.std >= i.firstDate and a.std < i.lastDate:
                    self.append(
                        str(a.udor).split()[0],
                        a.duty,
                        a.fd,
                        a.adep,
                        a.ades,
                        "%02d:%02d" % a.std.split()[3:5],
                        ('', "%02d:%02d" % a.atd.split()[3:5])[bool(a.is_flight)],
                        "%02d:%02d" % a.sta.split()[3:5],
                        ('', "%02d:%02d" % a.ata.split()[3:5])[bool(a.is_flight)],
                        formatTime(a.mdcsh),
                        formatTime(a.mdclh),
                        formatTime(a.scc),
                        formatTime(a.sccnp),
                        ("&nbsp;&nbsp;1", "")[a.lrhigh is None or not a.lrhigh],
                        ("&nbsp;&nbsp;1", "")[a.lrlow is None or not a.lrlow],
                    )
        scc = formatTime(r.scc)
        sccnop = formatTime(r.sccnop)
        mdcsh = formatTime(r.mdcsh)
        mdclh = formatTime(r.mdclh)
        lrh = r.lrh
        lrl = r.lrl
        self.append("","<b>TOTAL:</b>","","","","","","","","<b>%s</b>" % mdcsh,"<b>%s</b>" % mdclh,"<b>%s</b>" % scc,"<b>%s</b>" % sccnop,"<b>%s</b>" % lrh,"<b>%s</b>" % lrl)


# Add simulator briefing and debriefing =================================={{{1

# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    class Briefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkin) > 0):
                raise briefdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.fd = 'B' + a.fd[1:]
            self.std = a.std - a.leg_checkin
            self.sta = a.std
            self.is_last = False
            self.use = False

    class Debriefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.leg_checkout) > 0):
                raise briefdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.fd = 'D' + a.fd[1:]
            self.std = a.sta
            self.sta = a.sta + a.leg_checkout
            self.is_last = False
            self.use = False


# RaveIterator help classes =============================================={{{1

class ExtOTEntry(extiter.ExtEntry):
    def __init__(self, modifier):
        extiter.ExtEntry.__init__(self, modifier)
        # Signal that the entry is the last entry in the chain
        self.is_last = False
        # Signal that Overtime value should be used
        self.use = False


class OTEntry(Entry):
    def __init__(self):
        Entry.__init__(self)
        # Signal that the entry is the last entry in the chain
        self.is_last = False
        # Signal that Overtime value should be used
        self.use = False


class OTRaveIterator(RaveIterator):
    def create_entry(self):
        return OTEntry()


# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo(OTRaveIterator):
    """ Evalutated on a chain. Used by RaveIterator. """
    def __init__(self, i):
        fields = {
            'id': 'report_crewlists.%crew_id%',
            'empno': 'report_crewlists.%crew_empno%',
            'logname': 'report_crewlists.%crew_logname%',
            'is_SKD': 'report_crewlists.%overtime_is_SKD%',
            'is_SKN': 'report_crewlists.%overtime_is_SKN%',
            'is_SKS': 'report_crewlists.%overtime_is_SKS%',
            'bt': 'report_crewlists.%%acc_block_time%%(%s, %s)' % (i.firstDate, i.lastDate),
            'dt': 'report_crewlists.%%acc_duty_time%%(%s, %s)' % (i.firstDate, i.lastDate),
            'ot': 'void_reltime',
            'mdcsh': 'void_reltime',
            'mdclh': 'void_reltime',
            'mdc': 'void_reltime',
            'scc': 'void_reltime',
            'lrh': 'void_int',
            'lrl': 'void_int',
        }        
        where_expr = (
            'report_crewlists.%%crew_empno%% = "%s"' % (i.extperkey),
        )
        iterator = OTRaveIterator.iter('iterators.roster_set', where=where_expr)
        OTRaveIterator.__init__(self, iterator, fields)


        
# DutyInfo----------------------------------------------------------------{{{2
class DutyInfo(extiter.ExtRaveIterator):
    def __init__(self):
        fields = {
            'duty_time': 'report_crewlists.%duty_time%',
        }
        where_expr = (
            'not duty.%has_no_duty_time_contribution%',
        )
        iterator = RaveIterator.iter('iterators.duty_set', where=where_expr)
        extiter.ExtRaveIterator.__init__(self, iterator, fields,
                modifier=SimBriefDebriefExtender, entry=ExtOTEntry)


# LegInfo ----------------------------------------------------------------{{{2
class LegInfo(OTRaveIterator):
    """ Evalutated on a leg. Used by RaveIterator. """
    def __init__(self):
        fields = {
            'udor': 'report_crewlists.%leg_udor%',
            'duty': 'report_crewlists.%duty_code%',
            'fd': 'report_crewlists.%activity_name%',
            'adep': 'report_crewlists.%leg_adep%',
            'ades': 'report_crewlists.%leg_ades%',
            'atd': 'report_crewlists.%leg_atd_utc%',
            'ata': 'report_crewlists.%leg_ata_utc%',
            'std': 'report_crewlists.%leg_std_utc%',
            'sta': 'report_crewlists.%leg_sta_utc%',
            'id': 'report_crewlists.%crew_id%',
            'actype': 'report_crewlists.%leg_ac_type%',
            'acreg': 'report_crewlists.%leg_ac_reg%',
            'active': 'report_crewlists.%crew_active_landing%',
            'blockhrs': 'report_crewlists.%leg_block_time%',
            'duty_time': 'report_crewlists.%duty_time%',
            'mdcsh': 'report_crewlists.%overtime_mdcsh%',
            'mdclh': 'report_crewlists.%overtime_mdclh%',
            'scc': 'report_crewlists.%overtime_scc%',
            'sccnp': 'report_crewlists.%overtime_sccnp%',
            'is_last_in_duty':'report_crewlists.%leg_is_last_in_duty%',
            'is_last_in_wop': 'report_crewlists.%leg_is_last_in_wop%',
            'lrhigh': 'report_crewlists.%overtime_lrhigh%',
            'lrlow': 'report_crewlists.%overtime_lrlow%',
            'nextLegStart':'report_common.%next_activity_start_UTC%',
            'endUTC': 'leg.%end_UTC%',
            'ottype': 'void_string',
            'ot': 'void_string',
            'otduty': 'void_string',
            'is_flight': 'report_crewlists.%leg_is_flight%',
            'is_simulator': 'report_crewlists.%leg_is_simulator%',
            'leg_checkin': 'report_crewlists.%leg_check_in%',
            'leg_checkout': 'report_crewlists.%leg_check_out%',
        }
        iterator = OTRaveIterator.iter('iterators.leg_set')
        OTRaveIterator.__init__(self, iterator, fields)


# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey, month, year) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.", payload=getReportReply(report_name, parameters))
        try:
            M = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            self.month = M.index(month.upper()) + 1
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Month not usable.", payload=getReportReply(report_name, parameters))
        try:
            self.year = int(year)
            self.firstDate = AbsTime("%04d%02d01" % (self.year, self.month))
            if self.month == 12:
                self.lastDate = AbsTime("%04d%02d01" % (self.year + 1, 1))
            else:
                self.lastDate = AbsTime("%04d%02d01" % (self.year, self.month + 1))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Year/Month not usable.", payload=getReportReply(report_name, parameters))
        # [acosta:09/016@12:56] Should we bother to recalculate now to be in local time???
        now, = rave.eval('sp_crew', 'fundamental.%now%')
        if self.firstDate >= now:
            raise ReplyError('GetReport', status.REQUEST_NOT_SUPPORTED, "%s cannot be used for future dates." % report_name)
        if self.lastDate > now:
            # [acosta:09/049@14:41] WP Int-FAT 203, allow requests that are for
            # current month, but limit to show until today's date.
            self.lastDate = now
        self.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % (self.extperkey))[0]
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, parameters))

    def __str__(self):
        """ for basic tests only """
        L = ["--- !InputData"]
        L.extend(["%s : %s" % (str(x), self.__dict__[x]) for x in self.__dict__])
        return "\n".join(L)


# run ===================================================================={{{1
def run(*a):
    """ Here is where the report gets generated. """
    try:
        i = InputData(a)

        ri = CrewInfo(i)
        di = DutyInfo()
        li = LegInfo()

        ri.link(di)
        di.link(li)
        
        # Set parameter to limit search for records within start -> end
        old_salary_month_start = rave.param(startparam).value()
        rave.param(startparam).setvalue(i.firstDate)
        old_salary_month_end = rave.param(endparam).value()
        rave.param(endparam).setvalue(i.lastDate)

        try:
            context = SingleCrewFilter(i.crewid).context()
            rosters = ri.eval(context)
        
            crewOtMembers = Overtime.OvertimeRosterManager(context=context, crewlist=[i.crewid])
            crewOtRosters = crewOtMembers.getOvertimeRosters()
        finally:
            # Restore parameters
            rave.param(startparam).setvalue(old_salary_month_start)
            rave.param(endparam).setvalue(old_salary_month_end)

        try:
            roster = rosters[0]
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, a))

        # See which values that should be considered (Overtime)
        for r in crewOtRosters:
            overtime = r.getOvertime()
            if not overtime:
                overtime = RelTime(0)
            roster.ot = overtime
            roster.lrh = r.getLossRestHigh()
            roster.lrl = r.getLossRestLow()
            roster.scc = r.getSCC()
            roster.sccnop = r.getSCCNOP()
            roster.mdcsh = r.getMDCShortHaul()
            roster.mdclh = r.getMDCLongHaul()
            roster.mertid = r.getCalendarMonthPartTimeExtra()
            otBalanced = D(r.getOtContributors(), [])
            otBalanced.sort()
        
        if overtime is None: roster.use = False
            
        for duty in roster.chain():
            for leg in duty.chain():
                leg.ot = ""
                leg.otduty = ""
                leg.ottype = ""
                if otBalanced and type(otBalanced) == type([]) and int(leg.nextLegStart) >= int(otBalanced[0][0]):
                    leg.ot = str(otBalanced[0][3])
                    leg.otduty = str(otBalanced[0][1])
                    if otBalanced[0][2] == Overtime.OT_PART_7x24_FWD:
                        leg.ottype = "Week"
                    elif otBalanced[0][2] == Overtime.OT_PART_7x24_BWD:
                        leg.ottype = "Week"
                    elif otBalanced[0][2] == Overtime.OT_PART_1x24_FWD:
                        leg.ottype = "Day"
                    elif otBalanced[0][2] == Overtime.OT_PART_1x24_BWD:
                        leg.ottype = "Day"
                    elif otBalanced[0][2] == Overtime.OT_PART_MONTH:
                        leg.ottype = "Month"
                    elif otBalanced[0][2] == Overtime.OT_PART_PARTTIME_MONTH:
                        leg.ottype = "Mertid"
                    elif otBalanced[0][2] == Overtime.OT_PART_CALENDARWEEK:
                        leg.ottype = "Week"
                    elif otBalanced[0][2] == Overtime.OT_PART_DUTYPASS:
                        leg.ottype = "Day"
                    elif otBalanced[0][2] == Overtime.OT_PART_LATE_CHECKOUT:
                        leg.ottype = "Late C/O"
                    else:
                        print "no, not handling at all"
                        otBalanced = RelTime(0)

                    if type(otBalanced) == type([]):
                        del otBalanced[0]
                
                        
        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(XMLElement('h2', 'BASICS'))
        html.append(infoTable(i, roster))
        html.append(XMLElement('h2', 'OVERTIME'))
        html.append(otTable(i, roster))
        html.append(XMLElement('h2', 'OTHER ALLOWANCES'))
        html.append(allowTable(i, roster))

        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))

def archive(crew, firstdate, lastdate):
    s = str(firstdate).split()[0]
    y = s[-4:]
    m = s[-7:-4]
    ret = {}
    lc = len(crew)
    for i,(id,extperkey) in enumerate(crew):
        print "DUTYOVERTIME Crew",id,extperkey," (",i,"of",lc,")"
        try:
            ret[extperkey] = run(3, extperkey, m, y)
        except:
            import traceback, sys
            traceback.print_exc()
            ret[extperkey] = "!!ERROR!!" + sys.exc_info()
    return ret
# format ================================================================={{{1
def formatTime(t):
    # this functions returns "" if time is 0:00 or void, 
    # or the time with a leading zero if not empty.
    if (t is None or int(t) == 0):
        return ""
    else:
        return "%02d:%02d" % t.split()
    

# main ==================================================================={{{1
# for basic tests
if __name__ == '__main__':
    print run(3, '19627', 'JAN', '2013')

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
