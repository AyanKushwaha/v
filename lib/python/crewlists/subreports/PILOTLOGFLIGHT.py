
# changelog {{{2
# [acosta:07/078@14:06] First version
# }}}

"""
This is report 32.3.3 Pilot Log Flight.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
import crewlists.html as HTML
import crewlists.status as status
import utils.exception

from AbsDate import AbsDate
from crewlists.replybody import Reply, ReplyError, getReportReply
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator
from utils.selctx import FlightFilter


# constants =============================================================={{{1
report_name = 'PILOTLOGFLIGHT'
title = "Pilot Log - Flight"


# XMLElement classes ====================================================={{{1

# infoTable --------------------------------------------------------------{{{2
class infoTable(HTML.table):
    """
    Creates a table with input data.
    """
    def __init__(self, i):
        """ <table>...</table> for crew information.  """
        HTML.table.__init__(self,
            'Activity',
            'Date'
        )
        self['id'] = "table1"
        self.append(
            i.ff.flight.fd.flight_id,
            str(i.ff.flight.udor).split()[0]
        )


# legTable ---------------------------------------------------------------{{{2
class legTable(HTML.table):
    """
    Creates a small table with info about the leg.
    """
    def __init__(self, i, leg):
        """ <table>...</table> where activities are listed. """
        # i is input data
        # leg is a RaveIterator result
        HTML.table.__init__(self,
            'Activity',
            'Date',
            'From',
            'ATD',
            'ATA',
            'To',
            'A/C Type',
            'A/C Reg'
        )
        self['id'] = "basics"
        if leg.acreg is None:
            acreg = ""
        else:
            acreg = leg.acreg
        self.append(
            leg.fd,
            AbsDate(leg.atd).ddmonyyyy(),
            leg.adep,
            "%02d:%02d" % leg.atd.split()[3:5],
            "%02d:%02d" % leg.ata.split()[3:5],
            leg.ades,
            leg.actype,
            acreg
        )


# crewTable --------------------------------------------------------------{{{2
class crewTable(HTML.table):
    """
    Creates a table with info about each crew on the flight.
    """
    def __init__(self, i, c):
        """ <table>...</table> where crew is listed. """
        # i is input data
        # c is a RaveIterator (a crew)
        HTML.table.__init__(self,
            'Emp. No',
            'Duty',
            'Name',
            'CDR',
            'Loggable Block Hours',
            'Block Hours',
            'Landed'
        )
        self['id'] = "details"
        for crew in c:
            if crew.active is None:
                active = False
            else:
                active = crew.active
            self.append(
                crew.empno,
                crew.duty,
                crew.logname,
                ('No', 'Yes')[crew.pic == crew.id],
                HTML.span_right(crew.loghrs),
                HTML.span_right(crew.blockhrs),
                ('', 'Yes')[active]
            )


# RaveIterator help classes =============================================={{{1

# FlightInfo -------------------------------------------------------------{{{2
class FlightInfo:
    """ Evalutated on a leg. Used by RaveIterator. """
    fields = {
        'flight_name': 'report_crewlists.%leg_flight_name%',
    }


# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo:
    """ Evalutated on a leg. Used by RaveIterator. """
    fields = {
        'id': 'report_crewlists.%crew_id%',
        'empno': 'report_crewlists.%crew_empno%',
        'logname': 'report_crewlists.%crew_logname_at_date%(report_crewlists.%leg_start_utc%)',
        'duty': 'report_crewlists.%duty_code%',
        'pic': 'report_crewlists.%rc_pic%',
        'active': 'report_crewlists.%crew_active_landing%',
        'blockhrs': 'report_crewlists.%leg_block_time%',
        'loghrs': 'report_crewlists.%leg_loggable_block_time%',
    }


# LegInfo ----------------------------------------------------------------{{{2
class LegInfo:
    """ Evalutated on a leg. Used by RaveIterator. """
    fields = {
        'udor': 'report_crewlists.%leg_udor%',
        'fd': 'report_crewlists.%leg_flight_id%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'atd': 'report_crewlists.%leg_atd_UTC%',
        'ata': 'report_crewlists.%leg_ata_UTC%',
        'actype': 'report_crewlists.%leg_ac_type%',
        'acreg': 'report_crewlists.%leg_ac_reg%',
    }


# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        # date in format 'YYYYMMDD'
        self.parameters = parameters
        try:
            (noParameters, extperkey, flight, date) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments", payload=getReportReply(report_name, parameters))

        try:
            self.ff = FlightFilter.fromComponents(flight, date)
        except ValueError: 
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Cannot parse flight ID '%s'." % (flight), payload=getReportReply(report_name, parameters))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "The date '%s' is in unusable format." % (date), payload=getReportReply(report_name, parameters))

        now, = rave.eval('sp_crew', 'fundamental.%now%')
        if self.ff.flight.udor >= now:
            raise ReplyError('GetReport', status.REQUEST_NOT_SUPPORTED, "%s cannot be used for flights in the future." % report_name)

# run ===================================================================={{{1
def run(*a):
    """ Here is where the report gets generated.  """
    try:
        i = InputData(a)
        filter = i.ff

        # To get the flight
        fi = RaveIterator(RaveIterator.iter('iterators.flight_set', where=filter.asTuple()), FlightInfo())

        # To get legs in the flight
        ui = RaveIterator(RaveIterator.iter('iterators.flight_leg_set'), LegInfo())

        # To get crew
        li = RaveIterator(
            RaveIterator.iter('iterators.leg_set',
                where='fundamental.%is_roster% and report_crewlists.%crew_is_pilot%',
                sort_by='report_crewlists.%sort_key%'),
            CrewInfo()
        )

        fi.link(ui)
        ui.link(li)
        flights = fi.eval(filter.context())

        try:
            flight = flights[0]
        except:
            raise ReplyError('GetReport', status.FLIGHT_NOT_FOUND, payload=getReportReply(report_name, a))

        html = HTML.html(title="%s (%s)" % (title, i.ff.flight.fd.flight_id), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(infoTable(i))
        legNo = 1
        for leg in flight.chain():
            html.append(XMLElement('h2', 'LEG %d' % legNo))
            html.append(legTable(i, leg))
            html.append(crewTable(i, leg.chain()))
            legNo = legNo + 1

        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))

def archive(activities):
    """
    This function creates and archives file for an activity id and date. This
    is used later on in the crew portal to retrieve old data since the PUBLISH
    server only loads data from the previous month.
    """

    ret = {}
    lc = len(activities)
    for i,(id,udor) in enumerate(activities):
        print "PILOTLOGFLIGHT activity ",id,udor," (",i,"of",lc,")"
        try:
            key = "%s" % (id)
            key = key.replace(" ", "")

            ret[key] = run(3, '', id, udor)

        except:
            import traceback, sys
            traceback.print_exc()
            ret[id] = "!!ERROR!!" + sys.exc_info()
    return ret

# main ==================================================================={{{1
# for basic tests
if __name__ == '__main__':
    print run(3, "10240", 'SK 1417 ', '20070501')


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
