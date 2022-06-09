
# changelog {{{2
# [acosta:07/101@14:03] First version, modified flat file version.
# }}}

"""
This is the FutureActivites report, described in interface 32.15.1.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
import crewlists.elements as elements
import crewlists.status as status
import utils.exception

from AbsTime import AbsTime

from crewlists.replybody import Reply, ReplyError
from utils.extiter import ExtRaveIterator
from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter


# classes ================================================================{{{1

# Activity ---------------------------------------------------------------{{{2
class Activity:
    """
    An object that holds the input data together with the rave values.  That
    way the XML-formatting routines further down will have everything
    available.

    Has two fields:
        'inparams' - InputParameters object
        'iterator' - RaveIterator object
    """
    def __init__(self, inparams):
        self.inparams = inparams
        crewInfoIter = ExtRaveIterator(
            RaveIterator.iter('iterators.roster_set', where='report_crewlists.%%crew_id%% = "%s"' % (inparams.crewid)),
            elements.CrewInfo(inparams.startDate),
            modifier=elements.SimBriefDebriefExtender
        )
        where_expr = (
            'report_crewlists.%is_pre_act%',
            'report_crewlists.%%leg_end_lt%% >= %s' % (inparams.startDate),
        )
        activityInfoIter = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where=where_expr),
            elements.TaskInfo()
        )
        crewInfoIter.link(activityInfoIter)
        self.iterator = crewInfoIter.eval(SingleCrewFilter(inparams.crewid).context())


# InputParameters --------------------------------------------------------{{{2
class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(
        requestName='FutureActivities',
        empno=None,
        startDate=None):
    """ Returns an XML-formatted string with the report. """

    try:
        supportedRequests = ['FutureActivities']
        ip = InputParameters()

        # Misconfigured call from DIG
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.REQUEST_NOT_SUPPORTED, "requestName '%s' not supported. This report supports '%s' requests."  % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName
        
        if startDate is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No startDate given.')
        try:
            ip.startDate = AbsTime(startDate)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'startDate (%s) not usable.' % (startDate))
        
        if empno is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No empno given.')
        ip.empno = empno
        ip.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % empno)[0]
        if ip.crewid == None:
            # CR382: If crewid lookup fails, assume inparam is crewid and do 
            # lookup of empno instead
            ip.crewid = ip.empno
            ip.empno = rave.eval('sp_crew', 'crew_contract.%%extperkey_at_date_by_id%%("%s",%s)' % (ip.crewid,ip.startDate))[0]

        return elements.report(Activity(ip))

    except ReplyError, re:
        # crew not found, etc.
        return str(re)

    except:
        # programming error, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


# bit --------------------------------------------------------------------{{{2
def bit(s):
    """ Built-In Test, for basic test purposes. """

    status.debug = True
    print report(
        requestName="FutureActivities", 
        empno="15418", 
        startDate="20070201" 
    )


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    import sys
    bit(sys.argv[1:])


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
