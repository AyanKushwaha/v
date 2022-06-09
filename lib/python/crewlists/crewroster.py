
# changelog {{{2
# [acosta:06/262@00:06] First version.
# [acosta:06/314@17:12] Updated to use extperkey.
# [acosta:06/319@14:22] Uses named parameters.
# [acosta:07/094@16:03] Restructured, using Reply and ReplyError.
# [acosta:08/029@15:17] PAX info now from database instead of Rave.
# }}}

"""
This is the CrewRosterService report,
described in interfaces 32.0.2, 32.5.1, 32.6.1, and, 32.20.1.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
import crewlists.elements as elements
import crewlists.status as status
import utils.exception

from AbsTime import AbsTime
from tempfile import mkstemp

from crewlists.replybody import Reply, ReplyError
from utils.extiter import ExtRaveIterator
from utils.paxfigures import PaxInfo
from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter
from os import environ


carmsystem_name = environ.get('CARMSYSTEMNAME')
userId = None

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

        # The iteration is
        #    roster_set (to pick out crewmember)
        #        flight_sd_lt_set (to be able to get nr. of leg in multilegged flight)
        #            leg_set (for evalutating leg)

        crewInfoIter = RaveIterator(
            RaveIterator.iter('iterators.roster_set', where='report_crewlists.%%crew_id%% = "%s"' % inparams.crewid),
            elements.CrewInfo('fundamental.%now%')
        )


        flightSetIter = ExtRaveIterator(RaveIterator.iter('iterators.flight_sd_lt_set'),
                modifier=elements.SimBriefDebriefExtender)

        lfilter = ['true']
        if inparams.getSling:
            lfilter.append('report_crewlists.%in_current_or_next_sling%')
        else:
            if not inparams.startDate is None:
                lfilter.append('report_crewlists.%%leg_end_lt%% > %s' % inparams.startDate)
            if not inparams.endDate is None:
                lfilter.append('report_crewlists.%%leg_start_lt%% < %s' % inparams.endDate)

        innerLegSetIter = RaveIterator(
                RaveIterator.iter('iterators.leg_set', where=' and '.join(lfilter)), 
                elements.FlightInfo())

        # Connect the iterators
        crewInfoIter.link(flightSetIter)
        flightSetIter.link(innerLegSetIter)
        
        self.iterator = crewInfoIter.eval(SingleCrewFilter(inparams.crewid).context())


# InputParameters --------------------------------------------------------{{{2
class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


# functions =============================================================={{{1

# check_yn ---------------------------------------------------------------{{{2
def check_yn(x, r, p):
    if not x in ('Y', 'N'):
        raise ReplyError(r, status.INPUT_PARSER_FAILED, '%s must be one of ("Y", "N").' % (p,))
    return x == "Y"


# report -----------------------------------------------------------------{{{2
def report(
        requestName='CrewRoster',
        empno=None,
        getPublishedRoster=None,
        getTimesAsLocal=None,
        getCrewBasicInfo=None,
        getFlightLegSVC=None,
        getSling=None,
        startDate=None,
        endDate=None,
        rsLookupError=None):
    """
    Returns an XML-formatted string with the report.
    """
    try:
        supportedRequests = ('CrewRoster')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, "requestName '%s' not supported. This report supports '%s' requests."  % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'Request date outside CMS historic period (%s).' % startDate)
        # empno
        if empno is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No empno given.')
        if carmsystem_name == 'PROD_TEST' and empno == 'aik086':
            ip.empno = '999991'
            ip.crewid = 'aik086'
        else:
            ip.empno = empno
            ip.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % empno)[0]
        
        userId = ip.empno
        ip.getPublishedRoster = check_yn(getPublishedRoster, requestName, 'getPublishedRoster')
        ip.getTimesAsLocal = check_yn(getTimesAsLocal, requestName, 'getTimesAsLocal')
        ip.getCrewBasicInfo = check_yn(getCrewBasicInfo, requestName, 'getCrewBasicInfo')
        ip.getFlightLegSVC = check_yn(getFlightLegSVC, requestName, 'getFlightLegSVC')
        ip.getSling = check_yn(getSling, requestName, 'getSling')

        # getSling, startDate, endDate
        if ip.getSling:
            ip.startDate = None
            ip.endDate = None
        else:
            try:
                ip.startDate = AbsTime(startDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'startDate (%s) not usable.' % startDate)
            try:
                ip.endDate = AbsTime(endDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'endDate (%s) not usable.' % endDate)

        reply_result =  elements.report(Activity(ip))
        if carmsystem_name == 'PROD_TEST' and empno == 'aik086':
            import logging
            mylogger = logging.getLogger('crewroster')
            mylogger.setLevel(logging.INFO)
            myloggerf = logging.FileHandler('/var/carmtmp/logfiles/wefly_test.log')
            myloggerf.setFormatter(logging.Formatter('%(asctime)s -%(name)s: %(message)s'))
            mylogger.addHandler(myloggerf)
            mylogger.info(str(reply_result))

        return reply_result

    except ReplyError, re:
        # crew not found, etc.
        return str(re)

    except:
        # programming errors, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


def archive(crew, firstdate, lastdate):
    """  """
    ret = {}
    lc = len(crew)
    for i,(id,extperkey) in enumerate(crew):
        print "Crew roster Crew", id, extperkey, " (", i, "of", lc, ")"
        try:
            ret[extperkey] = report(requestName="CrewRoster",
                                    empno=extperkey,
                                    getPublishedRoster="Y",
                                    getTimesAsLocal="Y",
                                    getCrewBasicInfo="Y",
                                    getFlightLegSVC="Y",
                                    getSling="N",
                                    startDate=str(firstdate),
                                    endDate=str(lastdate))
        except:
            import traceback, sys
            traceback.print_exc()
            ret[extperkey] = "!!ERROR!!" + sys.exc_info()
    return ret


# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-In Test, for basic test purposes """

    status.debug = True
    crewId = None
    start_date = None
    end_date = None

    if carmsystem_name == 'PROD_TEST' and userId == 'aik086':
        crewId = userId
        start_date="20170901",
        end_date="20171101"
    else:
        crewId = '27878'
        start_date="20190901"
        end_date="20191001"
        
    print report(
          requestName="CrewRoster",
          empno=crewId,
          getPublishedRoster="Y",
          getTimesAsLocal="Y",
          getCrewBasicInfo="Y",
          getFlightLegSVC="Y",
          getSling="N",
          startDate=start_date,
          endDate=end_date
    )


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    # This is for the first basic tests.

    #import sys
    #bit(sys.argv[1:])
    import profile
    profile.run("bit()")


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
