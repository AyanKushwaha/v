
# changelog {{{2
# [acosta:06/262@00:06] First version.
# [acosta:06/319@13:04] Uses named arguments.
# [acosta:07/094@16:03] Restructured, using Reply and ReplyError.
# }}}

"""
This is the CrewListService report, described in interfaces
16.1, 32.6.1, 32.11, 41.2, 46.1.1, 46.1.2 and 46.2.
"""

# imports ================================================================{{{1
import crewlists.elements as elements
import crewlists.status as status
import utils.exception
import datetime

from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
from tempfile import mkstemp

from crewlists.replybody import Reply, ReplyError
from utils.rave import RaveIterator
from utils.selctx import SelectionFilter, FlightFilter, GroundDutyFilter, BasicContext
from utils.divtools import fd_parser, is_base_activity
from utils.paxfigures import CIOStatus


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
        self.cioinfo = CIOStatus()

        #   flight_set (to be able to get number of legs in multi-legged flight)
        #       flight_leg_set (to get info about leg)
        #          leg_set (to get info about crew)
        #              times(...) (to get crew documents)

        # Filter for flights
        self.isFlight = True
        if is_base_activity(inparams.activityId):
            self.isFlight = False
            # Convert eventually redefined leg code to real task code (Y3->S3,Z3->S3...)
            # Notice this is pretty time consuming, and if it becomes a performance problem  this could be changed to use:
            # %external_task_code2internal% in report_crewlists
            flightTaskSetIterator = RaveIterator(RaveIterator.iter('iterators.flight_task_set',  
              where='(default(training.%%leg_code_redefined%%,"") = "%s" or leg.%%code%% = "%s") and leg.%%start_date_utc%% = %s ' % (inparams.activityId, inparams.activityId, inparams.date)), {'code':'leg.%code%', })
            bc = BasicContext()
            activities = flightTaskSetIterator.eval(bc.getGenericContext())
            
            # If not activities for that day is found, return FLIGHT_NOT_FOUND
            if len(activities) == 0:
                raise ReplyError(inparams.requestName, status.FLIGHT_NOT_FOUND, inparams=inparams)
                
            inparams.activityId = activities[0].code
            ff = GroundDutyFilter(inparams.activityId, inparams.date,
                    requestDateAsOrigin=inparams.requestDateAsOrigin, requestDateInLocal=inparams.requestDateInLocal)
        else:
            ff = FlightFilter.fromComponents(inparams.activityId, inparams.dateRaw, None,
                    inparams.requestDateAsOrigin, inparams.requestDateInLocal)

        #### This can be used if CrewServices demands 1/1 for specific BaseActivities, with dep and std given.
        #### Otherwise CrewServices will get 1/8 or 3/8 ... depending on which activity the user points, just as for a multileget flight.
        ####if not self.isFlight and inparams.depStation is not None:
        ####    ff.add('report_crewlists.%leg_adep%', '=', '"%s"' % inparams.depStation)
        ####    if inparams.requestDateInLocal:
        ####        ff.add('report_crewlists.%std_time_lt%', '=', '%s' % inparams.std)
        ####    else:
        ####        ff.add('report_crewlists.%std_time_utc%', '=', '%s' % inparams.std)
        ####    flightSetIterator = RaveIterator(RaveIterator.iter('iterators.flight_std_leg_set', where=ff.asTuple()))
        ####else:
        ####    flightSetIterator = RaveIterator(RaveIterator.iter('iterators.flight_set', where=ff.asTuple()))

        flightSetIterator = RaveIterator(RaveIterator.iter('iterators.flight_set', where=ff.asTuple()))

        # Filter for legs
        leg_set='iterators.flight_std_leg_set'
        ufilter = SelectionFilter(ff)
        if inparams.depStation is not None:
            ufilter.add('report_crewlists.%leg_adep%', '=', '"%s"' % inparams.depStation)
            if not self.isFlight and not inparams.std is None:
                if inparams.requestDateInLocal:
                    ufilter.add('report_crewlists.%std_time_lt%', '=', '%s' % inparams.std)
                else:
                    ufilter.add('report_crewlists.%std_time_utc%', '=', '%s' % inparams.std)
        else:
            if not self.isFlight:
                leg_set='iterators.unique_leg_set'

        # SASCMS-2712 Due to this issue we have added ades for filtering.
        # Return-to-ramp flights caused a problem where two flights were found
        # and the crewlist contained them both.
        if inparams.arrStation is not None:
            ufilter.add('report_crewlists.%leg_ades%', '=', '"%s"' % inparams.arrStation)

        uniqueLegSetIterator = RaveIterator(
            RaveIterator.iter(leg_set, sort_by='report_crewlists.%leg_start_utc%', where=ufilter.asTuple()),
            elements.FlightInfo()
        )

        # Criteria for selecting crew
        cfilter = SelectionFilter(ff)
        cfilter.add('fundamental.%is_roster%','','')

        # Note: this calculation could be faulty as we don't have control over LDOR.
        if not self.isFlight and not inparams.std is None:
            if inparams.requestDateInLocal:
                cfilter.add('report_crewlists.%std_time_lt%', '=', '%s' % inparams.std)
            else:
                cfilter.add('report_crewlists.%std_time_utc%', '=', '%s' % inparams.std)
        if not inparams.depStation is None:
            cfilter.add('report_crewlists.%leg_adep%', '=', '"%s"' % inparams.depStation)
        if not inparams.arrStation is None:
            cfilter.add('report_crewlists.%leg_ades%', '=', '"%s"' % inparams.arrStation)

        if inparams.mainRank == 'F':
            cfilter.append('report_crewlists.%crew_main_rank%(report_crewlists.%leg_start_lt%) = "F"')
        elif inparams.mainRank == 'C':
            cfilter.append('report_crewlists.%crew_main_rank%(report_crewlists.%leg_start_lt%) = "C"')

        leg_set = RaveIterator.iter(
            'iterators.leg_set', 
            where=cfilter.asTuple(), 
            sort_by='report_crewlists.%sort_key%'
        )

        if inparams.getPackedRoster:
            legSetIterator = RaveIterator(leg_set, elements.CrewInfoForLegWithRoster(inparams.date, inparams.getPackedRosterFromDate, inparams.getPackedRosterToDate))
        else:
            legSetIterator = RaveIterator(leg_set, elements.CrewInfoForLeg(inparams.date))

        # Document info iteration
        docInfoIterator = RaveIterator(RaveIterator.times('report_crewlists.%document_count%'), elements.DocumentInfo())

        # Connect the iterators
        flightSetIterator.link(uniqueLegSetIterator)
        uniqueLegSetIterator.link(crew=legSetIterator)
        legSetIterator.link(doc=docInfoIterator)

        try:
            # Join all iterator results (n.b. changed with SASCMS-3399)
            self.iterator = []

            res = flightSetIterator.eval(ff.context())
            for e in res:
                print "Leg, first attempt, count", len(e.chain()), e
                self.iterator.extend(e.chain())
            # Change made in SASCMS-3399 caused issue SASCMS-4015. Reverting SASCMS-3399 is no option.
            # SASCMS-4015 Problems with flights with different UTC and local times. No flights were found.
            # So we are using the search used prior to the change in SASCMS-3399 but only if the flight is not found.
            if len(res) == 0:
                for e in flightSetIterator.eval(ff.context(None,True)):
                    print "Leg, second attempt, count", len(e.chain()), e
                    self.iterator.extend(e.chain())
        except:
            # Not sure this code is ever executed.
            try:
                # Third (?) attempt: Flip udor over day shift
                self.iterator = flightSetIterator.eval(ff.context(None,True))[0].chain()
            except:
                raise ReplyError(inparams.requestName, status.FLIGHT_NOT_FOUND, inparams=inparams)


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
        requestName='CrewList',
        activityId=None,
        date=None,
        requestDateAsOrigin=None,
        requestDateInLocal=None,
        depStation=None,
        arrStation=None,
        std=None,
        mainRank=None,
        getPublishedRoster=None,
        getTimesAsLocal=None,
        getLastFlownDate=None,
        getNextFlightDuty=None,
        getPrevNextDuty=None,
        getPrevNextAct=None,
        getCrewFlightDocuments=None,
        getPackedRoster=None,
        getPackedRosterFromDate=None,
        getPackedRosterToDate=None,
        rsLookupError=None):
    """
    Returns an XML-formatted string with the report.
    """

    try:
        supportedRequests = ('CrewList')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, "requestName '%s' not supported. This report supports '%s' requests."  % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'Request date outside CMS historic period (%s).' % date)

        # activityId
        if activityId is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No activityId given.')
        ip.activityId = activityId.upper()

        # date
        if date is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No date given.')
        ip.dateRaw = date
        try:
            ip.date = AbsTime(date)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'date (%s) not usable.' % date)

        #requestDateAsOrigin
        ip.requestDateAsOrigin = check_yn(requestDateAsOrigin, requestName, 'requestDateAsOrigin')

        #requestDateInLocal
        ip.requestDateInLocal = check_yn(requestDateInLocal, requestName, 'requestDateInLocal')

        # depStation
        ip.depStation = None
        if not depStation in ('', 3 * ' ', None):
            ip.depStation = depStation

        # arrStation
        ip.arrStation = None
        if not arrStation in ('', 3 * ' ', None):
            ip.arrStation = arrStation

        # std
        if std is None or str(std) == '' or str(std) == '00:00':
            ip.std = None
        else:
            try:
                ip.std = RelTime(std)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'std (%s) not usable.' % std)

        ip.mainRank = mainRank

        ip.getPublishedRoster = check_yn(getPublishedRoster, requestName, 'getPublishedRoster')
        ip.getTimesAsLocal = check_yn(getTimesAsLocal, requestName, 'getTimesAsLocal')
        ip.getLastFlownDate = check_yn(getLastFlownDate, requestName, 'getLastFlownDate')
        ip.getNextFlightDuty = check_yn(getNextFlightDuty, requestName, 'getNextFlightDuty')
        ip.getPrevNextDuty = check_yn(getPrevNextDuty, requestName, 'getPrevNextDuty')
        ip.getPrevNextAct = check_yn(getPrevNextAct, requestName, 'getPrevNextAct')
        ip.getCrewFlightDocuments = check_yn(getCrewFlightDocuments, requestName, 'getCrewFlightDocuments')
        ip.getPackedRoster = check_yn(getPackedRoster, requestName, 'getPackedRoster')

        # getPackedRosterFromDate, getPackedRosterToDate
        if ip.getPackedRoster:
            try:
                ip.getPackedRosterFromDate = AbsTime(getPackedRosterFromDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'getPackedRosterFromDate (%s) not usable.' % getPackedRosterFromDate)
            try:
                ip.getPackedRosterToDate = AbsTime(getPackedRosterToDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'getPackedRosterToDate (%s) not usable.' % getPackedRosterToDate)
        else:
            ip.getPackedRosterFromDate = 'fundamental.%pp_start%'
            ip.getPackedRosterToDate = 'fundamental.%pp_end%'

        return elements.report(Activity(ip))
    
    except ReplyError, ere:
        # flight not found, etc.
        return str(ere)

    except:
        # programming errors, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


def archive(activities):
    """ This function creates and arhive file for an activity id and date. This
        is used later on in the crew portal to retrieve old data since the PUBLISH
        server load recent data
    """
    
    ret = {}
    lc = len(activities)
    for i,(id,udor) in enumerate(activities):
        print "crewlist activity ",id,udor," (",i,"of",lc,")"
        try:
            key = "%s" % (id)
            key = key.replace(" ", "")
            
            ret[key] = report(requestName="CrewList",
                                    activityId=id,
                                    date=AbsDate(udor).yyyymmdd(),
                                    requestDateAsOrigin="N",
                                    requestDateInLocal="Y",
                                    std="",
                                    mainRank="",
                                    getPublishedRoster="Y",
                                    getTimesAsLocal="Y",
                                    getLastFlownDate="Y",
                                    getNextFlightDuty="N",
                                    getPrevNextDuty="Y",
                                    getPrevNextAct="N",
                                    getCrewFlightDocuments="N",
                                    getPackedRoster="N") 
            
        except:
            import traceback, sys
            traceback.print_exc()
            ret[id] = "!!ERROR!!" + sys.exc_info()
    return ret



# bit --------------------------------------------------------------------{{{2
def bit():
    """ Built-In Test, for basic test purposes """
    status.debug = True
    # print report(
    return report(
        requestName="CrewList",
        activityId="844",
        date="20190827",
        requestDateAsOrigin="Y",
        requestDateInLocal="N",
        depStation="OSL",
        arrStation="ARN",
        std="",
        mainRank="",
        getPublishedRoster="Y",
        getTimesAsLocal="N",
        getLastFlownDate="Y",
        getNextFlightDuty="Y",
        getPrevNextDuty="Y",
        getPrevNextAct="Y",
        getCrewFlightDocuments="Y",
        getPackedRoster="N",
        rsLookupError="")


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    # This is for the first basic tests.
    import profile
    profile.run("bit()")


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
