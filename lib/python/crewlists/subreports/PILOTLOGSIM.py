
# changelog {{{2
# [acosta:07/079@11:19] First version
# [acosta:07/095@12:20] Refactoring.
# }}}

"""
This is report 32.3.7 Pilot Log Simulator Activity.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML
import crewlists.status as status
import utils.exception
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief

from AbsTime import AbsTime

from crewlists.replybody import Reply, ReplyError, getReportReply
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter


# constants =============================================================={{{1
report_name = 'PILOTLOGSIM'
title = "Pilot Log - Simulator Activities"


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
            'Activity',
            'Duty',
            'Start Time',
            'End Time',
            'Simulator Block Hours',
            'A/C Qual.'
        )
        self['id'] = "details"
        for a in r:
            if isinstance(a, (SimBriefDebriefExtender.Briefing, SimBriefDebriefExtender.Debriefing)):
                blocktime = ""
            else:
                blocktime = "%02d:%02d" % (a.et - a.st).split()
            self.append(
                str(a.st).split()[0],
                a.taskcode,
                a.duty,
                "%02d:%02d" % a.st.split()[3:5],
                "%02d:%02d" % a.et.split()[3:5],
                blocktime,
                a.acqual,
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
        'taskcode': 'report_crewlists.%task_code%',
        'duty': 'report_crewlists.%duty_code%',
        'acqual': 'report_crewlists.%crew_ac_qlns%(report_crewlists.%leg_start_lt%)',
        'st': 'report_crewlists.%leg_start_utc%',
        'et': 'report_crewlists.%leg_end_utc%',
        'leg_checkin': 'report_crewlists.%leg_check_in%',
        'leg_checkout': 'report_crewlists.%leg_check_out%',
    }


# Add simulator briefing and debriefing =================================={{{1

# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    class Briefing:
        def __init__(self, a):
            if not int(a.leg_checkin) > 0:
                raise briefdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.taskcode = 'B' + a.taskcode[1:]
            self.st = a.st - a.leg_checkin
            self.et = a.st

    class Debriefing:
        def __init__(self, a):
            if not int(a.leg_checkout) > 0:
                raise briefdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.taskcode = 'D' + a.taskcode[1:]
            self.st = a.et
            self.st = a.et + a.leg_checkout


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
            # date in format 'YYYYMM'
            self.year = int(year)
            #self.month = int(yearMonth[4:6])
            self.firstDate = AbsTime("%04d%02d01" % (self.year, self.month))
            if self.month == 12:
                self.lastDate = AbsTime("%04d%02d01" % (self.year + 1, 1))
            else:
                self.lastDate = AbsTime("%04d%02d01" % (self.year, self.month + 1))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Date not usable.", payload=getReportReply(report_name, parameters))
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


# run ===================================================================={{{1
def run(*a):
    """ Returns string containing the report """
    try:
        i = InputData(a)

        where_expr = (
            'leg.%%start_lt%% >= %s' % (i.firstDate),
            'leg.%%start_lt%% < %s' % (i.lastDate),
            'leg.%is_simulator%' 
        )

        ri = extiter.ExtRaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='report_crewlists.%%crew_empno%% = "%s"' % (i.extperkey)), CrewInfo(),
            modifier=SimBriefDebriefExtender)
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
        print "PILOTLOGSIM Crew",id,extperkey," (",i,"of",lc,")"
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
    print run(3, '10240', 'JUN', '2012')


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
