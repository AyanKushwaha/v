
# changelog {{{2
# [acosta:07/108@09:26] First version.
# }}}

"""
This is the DutyCalculation report, described in interface 32.14.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
import crewlists.elements as elements
import crewlists.status as status
import utils.exception
import utils.extiter as extiter
import utils.briefdebrief as briefdebrief

from AbsTime import AbsTime

from crewlists.replybody import Reply, ReplyError
from utils.rave import RaveIterator, Entry
from utils.selctx import SingleCrewFilter


# classes ================================================================{{{1

# ExtEntry ---------------------------------------------------------------{{{2
class ExtEntry(extiter.ExtEntry):
    def chain(self, name=None):
        if name == 'legs':
            return extiter.ExtEntry.chain(self, name)
        return Entry.chain(self, name)


# SimBriefDebriefExtender ------------------------------------------------{{{2
class SimBriefDebriefExtender(briefdebrief.BriefDebriefExtender):
    times = (
        ('atd_utc', 'ata_utc'), ('atd_lt', 'ata_lt'),
        ('etd_utc', 'eta_utc'), ('etd_lt', 'eta_lt'),
        ('std_utc', 'sta_utc'), ('std_lt', 'sta_lt')
    )
    class Briefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkin) > 0):
                raise briefdebrief.BriefDebriefException('No briefing')
            self.__dict__ = a.__dict__.copy()
            self.code = 'B' + a.code[1:]
            for s, e in SimBriefDebriefExtender.times:
                setattr(self, s, getattr(a, s) - a.checkin)
                setattr(self, e, getattr(a, s))

    class Debriefing:
        def __init__(self, a):
            if not (a.is_simulator and int(a.checkout) > 0):
                raise briefdebrief.BriefDebriefException('No debriefing')
            self.__dict__ = a.__dict__.copy()
            self.code = 'D' + a.code[1:]
            for s, e in SimBriefDebriefExtender.times:
                setattr(self, s, getattr(a, e))
                setattr(self, e, getattr(a, e) + a.checkout)


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
        
        ci = extiter.ExtRaveIterator(
            RaveIterator.iter('iterators.roster_set', where='report_crewlists.%%crew_id%% = "%s"' % (inparams.crewid,)),
            elements.CrewInfoLegality(inparams.startDate, inparams.endDate),
            modifier=SimBriefDebriefExtender,
            entry=ExtEntry
        )

        # rulefailure
        wi = RaveIterator(RaveIterator.rulefailure(
            sort_by=rave.first(rave.Level.atom(), 'leg.%start_utc%'),
            where=(
                rave.first(rave.Level.atom(), 'leg.%%start_lt%% < %s' % inparams.endDate),
                rave.first(rave.Level.atom(), 'leg.%%end_lt%% > %s' % inparams.startDate),
            )))

        # Duty pass iteration
        dpi = RaveIterator(
            RaveIterator.iter('iterators.duty_set', where=(
                'report_crewlists.%%duty_start_lt%% >= %s' % (inparams.startDate),
                'report_crewlists.%%duty_end_lt%% < %s' % (inparams.endDate),
                'duty.%is_on_duty%',
            )),
            elements.DutyInfo()
        )

        ## Points iteration (simulated for now)
        #ppi = RaveIterator(
        #    RaveIterator.iter('iterators.leg_set', where=(
        #        'leg.%%start_lt%% >= %s' % (inparams.startDate),
        #        'leg.%%end_lt%% < %s' % (inparams.endDate),
        #        'true' # Activate iteration over points blocks
        #    )),
        #    elements.PointsInfo()
        #)

        # Activities, iterate over leg_set
        li = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where=(
                'report_crewlists.%%leg_start_lt%% >= %s' % (inparams.startDate),
                'report_crewlists.%%leg_end_lt%% < %s' % (inparams.endDate),
                'true' # Old Comment: Activate iteration over points blocks
            )),
            elements.LegInfoLegality()
        )

        # Montly stats, use times iterator
        mi = RaveIterator(RaveIterator.times(12, sort_by=('report_crewlists.%n_months_sort%')), elements.MonthInfo())

        ci.link(warnings=wi, dutypasses=dpi, legs=li, months=mi)

        self.iterator = ci.eval(SingleCrewFilter(inparams.crewid).context())


# InputParameters --------------------------------------------------------{{{2
class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(
        requestName='DutyCalculation',
        perKey=None,
        startDate=None,
        endDate=None,
        showNI=None,
        rsLookupError=None):
    """ Returns an XML-formatted string with the report. """

    try:
        supportedRequests = ('DutyCalculation')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.REQUEST_NOT_SUPPORTED, "requestName '%s' not supported. This report supports '%s' requests."  % (requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'Request date outside CMS historic period (%s).' % startDate)

        # perKey
        if perKey is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No perKey given.')
        ip.perKey = perKey
        ip.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % perKey)[0]

        # startDate
        if startDate is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No startDate given.')
        try:
            ip.startDate = AbsTime(startDate)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'startDate (%s) not usable.' % (startDate))

        # endDate
        if endDate is None:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'No endDate given.')
        try:
            # WP INT 128 - endDate should be included in period
            ip.endDate = AbsTime(endDate).adddays(1)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'endDate (%s) not usable.' % (endDate))

        # showNI
        if not showNI in ("Y", "N"):
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, 'showNI must be one of ("Y", "N").')
        ip.showNI = (showNI == "Y")

        return elements.report(Activity(ip))

    except ReplyError, re:
        # crew not found, etc.
        return str(re)

    except:
        # programming error, missing rave definitions.
        raise # XXX
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


# bit --------------------------------------------------------------------{{{2
def bit(s):
    """ Built-In Test, for basic test purposes. """

    status.debug = True
    print report(
        requestName="DutyCalculation", 
        perKey="15418", 
        startDate="20070201",
        endDate="20070228" 
    )


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """

    # This is for the first basic tests.

    import sys
    bit(sys.argv[1:])


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
