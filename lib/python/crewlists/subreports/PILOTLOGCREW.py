
# changelog {{{2
# [acosta:07/078@14:06] First version
# [acosta:07/095@12:00] Refactoring...
# }}}

"""
This is report 32.3.2 Pilot Log Crew Activity.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML
import crewlists.status as status
import utils.exception

from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime
from AbsDate import AbsDate
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter


# constants =============================================================={{{1
report_name = 'PILOTLOGCREW'
title = "Pilot Log - Flight Activities"


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
            'Month'
        )
        self['id'] = "basics"
        self.append(
            c.empno,
            c.logname,
            "%04d" % (i.year),
            "%02d" % (i.month)
        )


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
            'Date',
            'Duty',
            'Activity',
            'From',
            'ATD',
            'ATA',
            'To',
            'CDR',
            'A/C Type',
            'A/C Reg',
            'Loggable Block Hours',
            'Block Hours',
            'Landings'
        )
        self['id'] = "details"
        for a in r:
            if a.acreg is None:
                acreg = ""
            else:
                acreg = a.acreg
            if a.active:
                landings = a.landings
            else:
                landings = 0
            self.append(
                AbsDate(a.atd).ddmonyyyy(),
                a.duty,
                a.fd,
                a.adep,
                "%02d:%02d" % a.atd.split()[3:5],
                "%02d:%02d" % a.ata.split()[3:5],
                a.ades,
                ('No', 'Yes')[a.pic == a.id],
                a.actype,
                acreg,
                HTML.span_right(a.loghrs),
                HTML.span_right(a.blockhrs),
                HTML.span_right(landings),
            )


# RaveIterator help classes =============================================={{{1

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """ Evalutated on a chain. Used by RaveIterator. """
    fields = {
        'id': 'report_crewlists.%crew_id%',
        'empno': 'report_crewlists.%crew_empno%',
        'logname': 'report_crewlists.%crew_logname%',
    }


# LegInfo ----------------------------------------------------------------{{{2
class LegInfo:
    """ Evalutated on a leg. Used by RaveIterator. """
    fields = {
        'udor': 'report_crewlists.%leg_udor%',
        'duty': 'report_crewlists.%duty_code%',
        'fd': 'report_crewlists.%leg_flight_name%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'atd': 'report_crewlists.%leg_atd_UTC%',
        'ata': 'report_crewlists.%leg_ata_UTC%',
        'pic': 'report_crewlists.%rc_pic%',
        'id': 'report_crewlists.%crew_id%',
        'actype': 'report_crewlists.%leg_ac_family%',
        'acreg': 'report_crewlists.%leg_ac_reg%',
        'active': 'report_crewlists.%crew_active_landing%',
        'blockhrs': 'report_crewlists.%leg_block_time%',
        'loghrs': 'report_crewlists.%leg_loggable_block_time%',
        'landings': 'report_crewlists.%crew_nr_landings%',
    }


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
            # yearMonth in format 'YYYYMM'
            self.year = int(year)
            #self.month = int(yearMonth[4:6])
            self.firstDate = AbsTime("%04d%02d01" % (self.year, self.month))
            if self.month == 12:
                self.lastDate = AbsTime("%04d%02d01" % (self.year + 1, 1))
            else:
                self.lastDate = AbsTime("%04d%02d01" % (self.year, self.month + 1))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Date not usable.", payload=getReportReply(report_name, parameters))
        # [acosta:09/016@13:29] We cannot show published data with "log" content.
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

        where_expr = (
            'report_crewlists.%%leg_atd_lt%% >= %s' % (i.firstDate),
            'report_crewlists.%%leg_atd_lt%% < %s' % (i.lastDate),
            'report_crewlists.%leg_is_active_flight% or report_crewlists.%leg_is_school_flight%',
        )

        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='crew.%%employee_number%% = "%s"' % (i.extperkey)), CrewInfo())
        li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=where_expr), LegInfo())
        ri.link(li)

        rosters = ri.eval(SingleCrewFilter(i.crewid).context())

        try:
            roster = rosters[0]
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, a))

        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(XMLElement('h2', 'BASICS'))
        html.append(infoTable(i, roster))
        html.append(XMLElement('h2', 'DETAILS'))
        html.append(resultTable(i, roster.chain()))

        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))

def archive(crew, firstdate, lastdate):
    """
    This function creates and archives file for crew and date. This
    is used later on in the crew portal to retrieve old data since the PUBLISH
    server only loads data from the previous month.
    """

    s = str(firstdate).split()[0]
    y = s[-4:]
    m = s[-7:-4]
    ret = {}
    lc = len(crew)
    for i,(id,extperkey) in enumerate(crew):
        print "PILOTLOGCREW Crew",id,extperkey," (",i,"of",lc,")"
        try:
            ret[extperkey] = run(3, extperkey, m, y)
        except:
            import traceback, sys
            traceback.print_exc()
            ret[extperkey] = "!!ERROR!!" + sys.exc_info()
    return ret

# main ==================================================================={{{1
# for basic tests
if __name__ == '__main__':
    print run(3, '27878', 'JUN', '2012')


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
