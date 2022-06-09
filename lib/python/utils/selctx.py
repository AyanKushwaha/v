
# [acosta:07/239@14:49] First version.
# [acosta:07/257@12:31] Now using gpc_set_one_crew_chain()

"""
Use Cui functions to set default context, to speed things up.
"""

# imports ================================================================{{{1
from AbsTime import AbsTime
from RelTime import RelTime
from Airport import Airport
from utils.divtools import fd_parser
# NOTE: Cui and Select are imported within try blocks, to be able to use these
# classes in a GUI-less environment.


# exports ================================================================{{{1
__all__ = ['SelectionFilter', 'FlightFilter', 'GroundDutyFilter', 'CrewFilter', 'SingleCrewFilter']

PUBLICATION_TYPES = (
   "SCHEDULED",
   "PUBLISHED",
   "INFORMED",
   "DELIVERED",
)

# classes ================================================================{{{1

# BasicContext -----------------------------------------------------------{{{2
class BasicContext:
    """
    Determines if running in interactive Studio or in Report Server
    environment. If in Report Server, it also extracts the publish_type
    configured for the actual Report Server instance.
    """
    def __init__(self):
        self.publishType = None
        try:
            import carmensystems.common.reportWorker as reportWorker
            self.publishType = reportWorker.ReportGenerator().getPublishType()
            if self.publishType == '':
                self.publishType = None
            self.isRS = True
        except:
            self.isRS = False

    def getGenericContext(self):
        if self.isRS and not self.publishType is None:
            return 'plan_1_sp_crew'
        return 'sp_crew'

# SelectionFilter --------------------------------------------------------{{{2
class SelectionFilter(list):
    """
    Keep a list of expressions that have to be fulfilled.  Use Studio's select
    to create a 'default_context'.
    Usage example: see below
    """
    def __init__(self, l=None):
        list.__init__(self)
        if not l is None:
            self.extend(l)

    def add(self, a, op, b):
        self.append((a, op, b))

    def __str__(self):
        """ Return string adapted for iterator. """
        return ' and '.join(self.asTuple())

    def asDict(self):
        """ Used by select(), a dictionary adapted to Studio's select. """
        d = {}
        for a, op, b in self:
            try: # Strip strings
                b = b.strip('"')
            except: # Strip will not work on integers etc.
                pass
            if op == '=':
                d[a] = str(b)
            else:
                d[a] = op + str(b)
        return d

    def asTuple(self):
        """ Return tuple for 'where' parameter to Rave iterator. """
        return tuple("%s %s %s" % x for x in self)

    def context(self):
        """
        Try to set default_context and return string 'default_context.
        If default_context can't be set, return the string 'sp_crew'.
        """
        try:
            import Cui
            import Select
            Select.select(self.asDict(), Cui.CuiScriptBuffer, Cui.CrewMode)
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
            return 'default_context'
        except:
            return 'sp_crew'


# Flight -----------------------------------------------------------------{{{2
class Flight:
    def __init__(self, fd, udor, adep=None):
        self.fd = fd_parser(fd)
        self.udor = AbsTime(udor)
        self.adep = adep

    def __str__(self):
        s = "%s%03d%s/%02d" % (self.fd.carrier, self.fd.number, self.fd.suffix, self.udor.split()[2])
        if self.adep is not None:
            return s + " (%s)" % self.adep
        else:
            return s


# ActivityFilter ---------------------------------------------------------{{{2
class ActivityFilter(SelectionFilter):
    """ base class for FlightFilter and GroundDutyFilter. """
    def __init__(self, date, adep=None, requestDateAsOrigin=True, requestDateInLocal=False):
        SelectionFilter.__init__(self)
        self.requestDateAsOrigin = requestDateAsOrigin
        self.requestDateInLocal = requestDateInLocal
        self.date = date
        self.adep = None
        if not adep in ('', 3 * ' ', None):
            self.adep = adep
        if date is not None:
            if requestDateAsOrigin:
                if requestDateInLocal:
                    self.add('report_crewlists.%leg_ldor%', '=', date)
                else:
                    self.add('report_crewlists.%leg_udor%', '=', date)
            else:
                if requestDateInLocal:
                    self.add('report_crewlists.%std_date_lt%', '=', date)
                else:
                    self.add('report_crewlists.%std_date_utc%', '=', date)
        
    def prepareContext(self, type=None, alterDate=False):
        bc = BasicContext()
        if bc.isRS:
            type = bc.publishType
        self.published = (type in PUBLICATION_TYPES)

        self.defcontext = 'plan_1_sp_crew'
        if type is None:
            self.defcontext = 'sp_crew'
            
        if alterDate:
            # Try to find the leg by using udor adjascent to the date
            # given in the request. Problem is that if requestDateInLocal
            # is true, we can only assume that udor is equal to the 
            # given date. If the activity is close to a day shift and/or
            # the activity adep is 'far away' this assuption is likely
            # to fail. Without knowing the activity start time we cannot
            # directly calculate the correct udor based on the given date.
            if not self.requestDateInLocal or self.adep is None:
                raise Exception("ActivityFilter prepareContext(): Unable to switch date")
            ap = Airport(self.adep)
            if ap.getUTCTime(self.date) > self.date:
                self.date = self.date + RelTime(1,0,0)
            else:
                self.date = self.date - RelTime(1,0,0)

# FlightFilter -----------------------------------------------------------{{{2
class FlightFilter(ActivityFilter):
    """ default_context is set to a specific flight. """
    def __init__(self, flight, requestDateAsOrigin=True, requestDateInLocal=False, includeSuffix=False, onlyOperatedBySAS=False):
        """
            @param flight - Flight instance
            @param requestDateAsOrigin -
            @param requestDateInLocal -
            @param includeSuffix - Shall the Flight suffix be inluded in the filer or not
        """
        ActivityFilter.__init__(self, flight.udor, flight.adep, requestDateAsOrigin, requestDateInLocal)
        self.flight = flight
        self.add('report_crewlists.%leg_fd_carrier%', '=', '"%s"' % flight.fd.carrier)
        self.add('report_crewlists.%leg_fd_number%', '=', flight.fd.number)

        if includeSuffix:
            # The suffix was removed as part of SASCMS-3305 but it is needed for APIS
            # so an extra argument was added.
            self.add('report_crewlists.%leg_fd_suffix%', '=', '"%s"' % flight.fd.suffix)
        
        if not self.adep is None:
            self.add('report_crewlists.%leg_adep%', '=', '"%s"' % self.adep)

        if onlyOperatedBySAS:
            self.add('report_crewlists.%leg_operated_by_SAS%', '=', True)
            
    @classmethod
    def fromComponents(cls, fd, udor, adep=None, requestDateAsOrigin=True, requestDateInLocal=False, includeSuffix=False, onlyOperatedBySAS=False):
        obj = cls(Flight(fd, udor, adep), requestDateAsOrigin, requestDateInLocal, includeSuffix, onlyOperatedBySAS)
        return obj

    def context(self, type=None, alterDate=False, includeSuffix=False):
        try:
            self.prepareContext(type, alterDate)
            import Cui
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            
            # The suffix was removed in SASCMS-3305 but it was needed for APIS.
            if includeSuffix:
                suffix = self.flight.fd.suffix
            else:
                suffix = ""
            
            Cui.gpc_set_crew_chains_by_flight(Cui.gpc_info,
                                              self.flight.fd.carrier, 
                                              self.flight.fd.number,
                                              suffix,
                                              str(self.date), 
                                              0, 
                                              self.published)
            return 'default_context'
        except:
            print "FlightFilter: reverting to %s" % self.defcontext
            return self.defcontext

# GroundDutyFilter -----------------------------------------------------------{{{2
class GroundDutyFilter(ActivityFilter):
    """ default_context is set to a specific ground duty. """
    def __init__(self, activityId, date, adep=None, requestDateAsOrigin=True, requestDateInLocal=False):
        ActivityFilter.__init__(self, date, adep, requestDateAsOrigin, requestDateInLocal)
        self.activityId = activityId
        self.add('leg.%code%', '=', '"%s"' % self.activityId)
        if not self.adep is None:
            self.add('report_crewlists.%leg_adep%', '=', '"%s"' % self.adep)

    def context(self, type=None, alterDate=False):
        try:
            self.prepareContext(type, alterDate)
            import Cui
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            Cui.gpc_set_crew_chains_by_ground_duty(Cui.gpc_info,
                                                   self.activityId,
                                                   str(self.date),
                                                   self.adep,
                                                   self.published)
            return 'default_context'
        except Exception, e:
            print "GroundDutyFilter: reverting to %s (%s)" % (self.defcontext, e)
            return self.defcontext


# CrewFilter -------------------------------------------------------------{{{2
class CrewFilter(list):
    """ Create a context consisting of a number of crew. """
    def __init__(self, l=None):
        list.__init__(self)
        if l is not None:
            self.extend(l)

    def __str__(self):
        return ' or '.join(self.asTuple())
 
    def context(self):
        try:
            import Cui
            Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                    Cui.CrewMode, Cui.CrewMode, self, 0)
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
            return 'default_context'
        except:
            return 'sp_crew'

    def asTuple(self):
        raise NotImplementedError("Cannot use tuples with CrewFilter().")


# SingleCrewFilter -------------------------------------------------------{{{2
class SingleCrewFilter:
    """ Create a context consisting of one single crew member. """
    def __init__(self, crewid):
        self.crewid = crewid

    def __str__(self):
        return 'report_crewlists.%%crew_id%% = "%s"' % (self.crewid,)

    def context(self, type=None):
        customType = type
        bc = BasicContext()
        if bc.isRS and customType is None:
            type = bc.publishType

        if type is None:
            try:
                import Cui
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
                Cui.gpc_set_one_crew_chain(Cui.gpc_info, self.crewid)
                return 'default_context'
            except:
                print "SingleCrewFilter:context Reverting to sp_crew"
                return 'sp_crew'
        else:
            try:
                import Cui
                if bc.isRS and customType is None:
                    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
                    Cui.gpc_set_one_published_crew_chain(Cui.gpc_info, self.crewid)
                    return 'default_context'
                else:
                    Cui.CuiLoadPublishedRosters(Cui.gpc_info, [self.crewid], type)
                    return 'plan_1_sp_crew'
            except:
                print "SingleCrewFilter:context Reverting to plan_1_sp_crew"
                return 'plan_1_sp_crew'

    def asTuple(self):
        return (str(self),)


# Example of usage ======================================================={{{1
#
# s = SelectionFilter()
# s.add('leg.%start_station%', '=', '"ARN"')
# s.add('leg.%flight_nr%', '=', '3456')
# s.add('leg.%start_utc%', '>', '06May2007 10:00')
# s.add('leg.%start_utc%', '<', '06May2007 11:00')
#
# context = s.context() 
#             # will to filter based on the expressions and return 'default_context' 
#             # if this fails, then 'sp_crew' will be returned.
#
# leg_expr = rave.foreach(rave.iter('iterators.leg_set', where=s.asTuple()), ...)
# legs, = rave.eval(context, leg_expr)

# c = SingleCrewFilter('12345')
# leg_expr = rave.foreach(rave.iter('iterators.roster_set', where=c.asTuple()))

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
