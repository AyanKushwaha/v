
# changelog {{{2
# [acosta:06/262@00:06] First version.
# [acosta:06/319@12:45] Uses named arguments.
# [acosta:07/094@16:06] Restructured, using Reply and ReplyError.
# }}}

"""
This is the CrewFlight report, described in interfaces 32.5.3, 32.5.7 and
32.6.3
"""

# imports ================================================================{{{1
import crewlists.elements as elements
import crewlists.status as status
import utils.exception

from AbsTime import AbsTime

from crewlists.replybody import Reply, ReplyError
from utils.paxfigures import PaxInfo, DelayInfo
from utils.rave import RaveIterator
from utils.selctx import FlightFilter


# classes ================================================================{{{1

# Activity ---------------------------------------------------------------{{{2
class Activity:
    """
    An object that holds the input data together with the rave values.
    That way the XML-formatting routines further down will have everything
    available.

    Has two fields:
        'inparams' - InputParameters object
        'iterator' - RaveIterator object
    """
    def __init__(self, inparams):
        self.inparams = inparams
        self.paxinfo = PaxInfo()
        self.delayinfo = DelayInfo(self.paxinfo.ec)

        # Filter for unique legs

        empty_station = set(('', 3 * ' ', None))
        if not inparams.arrStation in empty_station:
            inparams.uf.add('report_crewlists.%leg_ades%', '=', '"%s"' % inparams.arrStation)

        # NOTE: This first evalution is needed to get start and end times for
        # the airplane's previous three rotations
        mmIter = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where=inparams.uf.asTuple()),
            elements.MinMaxDateInfo()
        )
        try:
            val = mmIter.eval(inparams.uf.context())[0]
        except:
            raise ReplyError(inparams.requestName, status.FLIGHT_NOT_FOUND)

        # The iterations are:
        #   flight_set                  (to be able to get number of legs in flight)
        #       flight_leg_set          (for leg info)
        #           leg_set             (for crew info)
        #           ac_rotations_ref    (for previous a/c flights)
        #               chain_set       (context switch demands this /unconfirmed/)
        #                   flight_set  (to be able to get number of legs for multi-legged flights)
        #                       leg_set (for leg info)
        #

        flightSetIter = RaveIterator(
            RaveIterator.iter('iterators.flight_set', where=inparams.ff.asTuple())
        )

        uniqueLegIter = RaveIterator(
            RaveIterator.iter('iterators.flight_leg_set', where=inparams.uf.asTuple()),
            elements.FlightInfo()
        )

        legSetIter = RaveIterator(
            RaveIterator.iter('iterators.leg_set', 
                where='fundamental.%is_roster%',
                sort_by='report_crewlists.%sort_key%'),
            elements.CrewInfoForLeg(inparams.ff.flight.udor)
        )

        acRotTransform = RaveIterator(RaveIterator.iter('ac_rotations_ref'))
        acChainIter = RaveIterator(RaveIterator.iter('iterators.chain_set'))
        acFlightIter = RaveIterator(RaveIterator.iter('iterators.flight_set'))
        acLegIter = RaveIterator(
            RaveIterator.iter('iterators.leg_set',
                where='report_crewlists.%%leg_start_utc%% >= %s and report_crewlists.%%leg_start_utc%% < %s' % (val.min, val.max)),
            elements.FlightInfo()
        )

        # Connect the iterators
        flightSetIter.link(uniqueLegIter)
        uniqueLegIter.link(crew=legSetIter)
        legSetIter.link(acrot=acRotTransform)
        acRotTransform.link(acChainIter)
        acChainIter.link(acFlightIter)
        acFlightIter.link(acLegIter)

        try:
            # pass uniqueLegIter for flight that matches (should only be one
            # match for flightSetIter)
            self.iterator = flightSetIter.eval(inparams.ff.context())[0].chain()
        except:
            raise ReplyError(inparams.requestName, status.FLIGHT_NOT_FOUND, inparams=inparams)


# InputParameters --------------------------------------------------------{{{2
class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(
        requestName='CrewFlight',
        flightId=None,
        originDate=None, 
        depStation=None, 
        arrStation=None, 
        getTimesAsLocal=None,
        rsLookupError=None):
    """
    Returns an XML-formatted string with the report.
    """

    try:
        supportedRequests = ('CrewFlight')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.REQUEST_NOT_SUPPORTED, "requestName '%s' not supported. This report supports '%s' requests."  % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'Request date outside CMS historic period (%s).' % originDate)

        # flightId
        if flightId is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No flightId given.')

        # originDate
        if originDate is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No originDate given.')

        # depStation
        ip.depStation = depStation.upper()

        # arrStation
        ip.arrStation = arrStation.upper()

        try:
            ip.ff = FlightFilter.fromComponents(flightId, originDate)
            ip.uf = FlightFilter.fromComponents(flightId, originDate, depStation.upper())
        except ValueError: 
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, "Cannot parse flight ID '%s'." % flightId)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'originDate (%s) not usable.' % originDate)

        # getTimesAsLocal
        if not getTimesAsLocal in ("Y", "N"):
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'getTimesAsLocal must be one of ("Y", "N").')
        ip.getTimesAsLocal = (getTimesAsLocal == "Y")

        return elements.report(Activity(ip))

    except ReplyError, ere:
        # flight not found etc.
        return str(ere)

    except:
        # programming error, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-In Test, for basic test purposes """

    status.debug = True
    print report(
        requestName="CrewFlight",
        flightId="SK1463",
        originDate="20070507",
        depStation="",
        arrStation="",
        getTimesAsLocal="N"
    )


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    # This if for the first basic tests.

    import profile
    profile.run("bit()")


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
