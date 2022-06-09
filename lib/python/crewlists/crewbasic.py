
# changelog {{{2
# [acosta:06/262@00:06] First version.
# [acosta:06/314@17:06] Updated to use extperkey.
# [acosta:06/319@12:42] Uses named arguments.
# [acosta:07/094@16:03] Restructured, using Reply and ReplyError.
# }}}

"""
This is the CrewBasicService report, described in interface 32.0.1.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
import crewlists.elements as elements
import crewlists.status as status
import utils.exception
import traceback

from AbsTime import AbsTime

from crewlists.replybody import Reply, ReplyError
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
        crewInfoIter = RaveIterator(
            RaveIterator.iter('iterators.roster_set', where='report_crewlists.%%crew_id%% = "%s"' % inparams.crewid),
            elements.CrewInfo(inparams.searchDate)
        )
        self.iterator = crewInfoIter.eval(SingleCrewFilter(inparams.crewid).context())


# InputParameters --------------------------------------------------------{{{2
class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(
        requestName='CrewBasic',
        empno=None,
        searchDate=None,
        getCrewBasicInfo=None,
        getCrewContact=None, 
        rsLookupError=None):
    """ 
    Returns an XML-formatted string with the report.
    """

    try:
        supportedRequests = ('CrewBasic')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.REQUEST_NOT_SUPPORTED, "requestName '%s' not supported. This report supports '%s' requests." % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'Request date outside CMS historic period (%s).' % searchDate)
        # empno
        if empno is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No empno given.')
        if carmsystem_name == 'PROD_TEST' and empno == 'aik086':
            ip.empno = '999991'
            ip.crewid = 'aik086'
        else:
            ip.empno = empno
            ip.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % empno)[0]
                
        if ip.crewid is None:
            raise ReplyError(requestName, status.CREW_NOT_FOUND)

        userId = ip.empno
        # searchDate
        if searchDate is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No searchDate given.')
        try:
            ip.searchDate = AbsTime(searchDate)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'searchDate (%s) not usable.' % searchDate)

        # getCrewBasicInfo
        if not getCrewBasicInfo in ("Y", "N"):
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'getCrewBasicInfo must be one of ("Y", "N").')
        ip.getCrewBasicInfo = (getCrewBasicInfo == "Y")

        # getCrewContact
        if not getCrewContact in ("Y", "N"):
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'getCrewContact must be one of ("Y", "N").')
        ip.getCrewContact = (getCrewContact == "Y")


        reply_result =  elements.report(Activity(ip))
        if carmsystem_name == 'PROD_TEST' and empno == 'aik086':
            import logging
            mylogger = logging.getLogger('crewbasic')
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
        traceback.print_exc()
        # programming error, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-In Test, for basic test purposes """

    status.debug = True
    crewId = None
    if carmsystem_name == 'PROD_TEST' and userId == 'aik086':
        crewId = userId
    else:
        crewId = "27878"
    print report(
            requestName="CrewBasic", 
            empno=userId, 
            searchDate="20070501", 
            getCrewBasicInfo="Y",
            getCrewContact="Y"
    )


def archive(crew, date):
    """  """
    ret = {}
    lc = len(crew)
    for i,(id,extperkey) in enumerate(crew):
        print "Crew roster Crew", id, extperkey, " (", i, "of", lc, ")"
        try:
            ret[extperkey] = report(requestName="CrewBasic",
                                    empno=id, 
                                    searchDate=str(date), 
                                    getCrewBasicInfo="Y",
                                    getCrewContact="Y")
        except:
            import traceback, sys
            traceback.print_exc()
            ret[extperkey] = "!!ERROR!!" + sys.exc_info()
    return ret


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    # This is for the first basic tests.

    import profile
    profile.run("bit()")


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
