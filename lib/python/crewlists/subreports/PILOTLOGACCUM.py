
# changelog {{{2
# [acosta:07/140@19:57] First version
# }}}

"""
This is report 32.3.9 Pilot log accumulated info
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML
import crewlists.status as status
import utils.crewlog as crewlog
import utils.exception

from RelTime import RelTime

from crewlists.replybody import Reply, ReplyError, getReportReply
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter
from utils.TimeServerUtils import now


# constants =============================================================={{{1
report_name = 'PILOTLOGACCUM'
title = "Pilot Log - Crew Accumulated Info"


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
            'Pr Date',
        )
        self['id'] = "basics"
        self.append(
            c.empno,
            c.logname,
            "%04d-%02d-%02d" % (i.now_a.split()[:3])
        )


# resultTable ------------------------------------------------------------{{{2
class resultTable(HTML.table):
    """
    Creates a table with flight activities for the chosen crew.
    """

    titles = {
        'blockhrs': 'Block Hours',
        'logblkhrs': 'Loggable Block Hours',
        'simblkhrs': 'Simulator Block Hours',
        'landings': 'No of Landings',
    }

    def __init__(self, t, ac):
        """ <table>...</table> where activities are listed. """
        HTML.table.__init__(self, '', 
            'This Month',
            'Last Month',
            'Last 90 Days',
            'Last 6 Months',
            'Last 12 Months',
            'Lifetime')
        self['id'] = "details"
        for c in t.counters:
            if c in t and ac in t[c]:
                self.appendConv(
                    c,
                    self.titles[c],
                    t[c][ac].get(t.intervals[0], 0),
                    t[c][ac].get(t.intervals[1], 0),
                    t[c][ac].get(t.intervals[2], 0),
                    t[c][ac].get(t.intervals[3], 0),
                    t[c][ac].get(t.intervals[4], 0),
                    t[c][ac].get(t.intervals[5], 0),
                )
            else:
                # No landings/simulator, but blockhours
                self.appendConv(
                    c,
                    self.titles[c],
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                )

    def appendConv(self, c, *a):
        if c == "landings":
            R = [HTML.span_right(r) for r in a[1:]]
        else:
            # The other columns need to be converted
            R = [HTML.span_right(str(RelTime(r))) for r in a[1:]]
        self.append(a[0], *R)


# RaveIterator help classes =============================================={{{1

# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """ Evalutated on a chain. Used by RaveIterator. """
    fields = {
        'id': 'report_crewlists.%crew_id%',
        'empno': 'report_crewlists.%crew_empno%',
        'logname': 'report_crewlists.%crew_logname%',
    }



# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.", payload=getReportReply(report_name, parameters))

        self.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % (self.extperkey))[0]
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, parameters))

        self.now_a = now()


# Totals -----------------------------------------------------------------{{{2
class Totals(dict):
    """ Create structure with values for each type. """

    # Totals = {
    #      'blockhrs': {
    #                     'B737': {
    #                            'life': value,
    #                      }
    #       }
    # }
    counters = ['blockhrs', 'logblkhrs', 'simblkhrs', 'landings']

    def __init__(self, i, roster):
        dict.__init__(self)
        the_cstat = crewlog.stat_1_90_6_12_life(roster.id, hi=i.now_a)
        self.intervals = the_cstat.intervals
        # Reshuffle the data. The format from the crewlog functions is:
        # { 'blockhrs': { 'crewid': { 'B737': { interval: value, ...}}}}
        acf = set()
        for c in self.counters:
            try:
                self[c] = the_cstat[c][roster.id]
                acfams = [x for x in self[c]]
                self[c]['ALL'] = {}
                for acfam in acfams:
                    acf.add(acfam)
                    for i in self[c][acfam]:
                        # sum of all a/c families
                        self[c]['ALL'][i] = self[c]['ALL'].get(i, 0) + self[c][acfam][i]
            except KeyError:
                self[c] = {'ALL': {}}
        self.acFamilies = sorted(acf)


# run ===================================================================={{{1
def run(*a):
    """ Returns string containing the report """
    try:
        i = InputData(a)

        ri = RaveIterator(RaveIterator.iter('iterators.roster_set', 
            where='report_crewlists.%%crew_empno%% = "%s"' % (i.extperkey)), CrewInfo())

        rosters = ri.eval(SingleCrewFilter(i.crewid).context())

        try:
            roster = rosters[0]
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, a))


        totals = Totals(i, roster)

        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(XMLElement('h2', 'BASICS'))
        html.append(infoTable(i, roster))

        html.append(XMLElement('h2', 'ACTYPE ALL'))
        html.append(resultTable(totals, "ALL"))

        for ac in totals.acFamilies:
            html.append(XMLElement('h2', 'ACTYPE ' + ac))
            html.append(resultTable(totals, ac))

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
    print run(1, '41166')

if __name__ == '__main__':
    bit()
    #import profile
    #profile.run("bit()")


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
