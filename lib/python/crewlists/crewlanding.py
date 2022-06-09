
# Changelog {{{
# [acosta:07/029@14:26] First version
# [acosta:07/095@12:39] Refactoring... uplink messages removed.
# [acosta:07/122@10:04] Moved source file, added report server 'save()'
# [acosta:07/129@11:36] Moved reports to better location.
# }}}

"""
Landings - request from HERMES to update crew_landing, sends reply with update
status.

See interface 46.3 - Landings.

Also used for CR 184 - Landings on non-ACARS aircraft, where all pilots flying
F50 or B737 Classic will get landing records based on even landing distribution
between Captain and First Officer. This will have to be reviewed at a later
stage. This batch job is run every day and will "adjust" landings for the prior
date.

root element is <replyBody>, so this report is related to CrewList et al.
"""

# imports ================================================================{{{1
import sys
import warnings
from optparse import OptionParser

import carmensystems.rave.api as rave
import crewlists.status as status
import utils.exception

from AbsTime import AbsTime
from RelTime import RelTime
from crewlists.replybody import Reply, ReplyError, schema_version
from tm import TM
from utils.rave import RaveIterator
from utils.selctx import FlightFilter, Flight
from utils.xmlutil import XMLElement, CDATA


# exports ================================================================{{{1
__all__ = ['report', 'run', 'main']


# globals ================================================================{{{1
report_name = 'CrewLanding'

# RaveIterator classes ==================================================={{{1

# CrewIterator -----------------------------------------------------------{{{2
class CrewIterator(RaveIterator):
    """ Loop crew """
    def __init__(self, crewid):
        fields = {
            'is_school_flight': 'report_crewlists.%leg_is_school_flight%',
            'is_test_flight': 'report_crewlists.%leg_is_test_flight%',
            'is_active_flight': 'report_crewlists.%leg_is_active_flight%',
            'relief_pilot': 'report_crewlists.%crew_pos_relief_pilot%',
            'main_func': 'report_crewlists.%crew_main_rank%(report_crewlists.%leg_std_utc%)',
            'pic': 'report_crewlists.%rc_pic%',
            'id': 'report_crewlists.%crew_id%',
            'start_utc': 'report_crewlists.%leg_start_utc%',
            'now': 'fundamental.%now%',
        }
        iterator = RaveIterator.iter('iterators.leg_set', where='report_crewlists.%%crew_id%% = "%s"' % crewid)
        RaveIterator.__init__(self, iterator, fields)


# InputData =============================================================={{{1
class InputData:
    """ This class keeps and formats the input parameters. """
    def __init__(self, requestName=report_name, flightId=None, originDate=None,
            depStation=None, arrStation=None, empno=None):
        """ Input format checks. """
        self.requestName = requestName
        if requestName != report_name:
            msg = "This report supports '%s' only." % report_name
            raise ReplyError(requestName, status.REPORT_NOT_FOUND, msg, payload=crewLanding(msg))

        if flightId is None:
            msg = "No flightId given."
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))
        if originDate is None:
            msg = "No originDate given."
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))
        if depStation is None:
            msg = "No depStation given."
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))
        if arrStation is None:
            msg = "No arrStation given."
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))

        try:
            self.ff = FlightFilter.fromComponents(flightId, originDate, depStation)
        except ValueError:
            msg = "flightId has invalid format (%s)." % flightId
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))
        except:
            msg = "Cannot use date '%s'." % originDate
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))

        self.ff.flight.ades = arrStation
        self.ff.add('report_crewlists.%leg_ades%', '=', '"%s"' % arrStation)

        if empno is None:
            msg = "No empno given."
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, msg, payload=crewLanding(msg))
        self.empno = empno

        # Convert extperkey to crewid
        self.crewid = rave.eval(self.ff.context(), 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % empno)[0]
        if self.crewid is None:
            msg = "Could not get crewid for crew with extperkey = '%s'." % (empno)
            raise ReplyError(requestName, status.CREW_NOT_FOUND, msg, payload=crewLanding(msg))

    def __str__(self):
        """ For basic tests """
        L = ['%s="%s"' % (k, v) for (k, v) in self.__dict__.iteritems()]
        return '<InputData ' + ' '.join(L) + '>'


# XML formatting ========================================================={{{1
class crewLanding(XMLElement):
    def __init__(self, msg):
        XMLElement.__init__(self)
        self['version'] = schema_version
        self.append(XMLElement('uplinkMessage', CDATA(msg)))


# internal functions ====================================================={{{1

nr_warnings = 0

# acars_batch ------------------------------------------------------------{{{2
def acars_batch(firstdate, lastdate):
    """Iterate flights which has no landing registrered. 
    For these flights we will have to assume who landed the aircraft. 
    Commander is supposed to land legs 1, 3, 5, ...
    See CR 184 and CR 220."""

    global nr_warnings 
    nr_warnings = 0

    def warn(s):
        global nr_warnings
        nr_warnings += 1
        warnings.warn(s, stacklevel=2)

    leg_info = {
        'fd': 'report_crewlists.%leg_flight_descriptor%',
        'udor': 'report_crewlists.%leg_udor%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'crewid': 'report_crewlists.%crew_id%',
        'no_suitable': 'report_crewlists.%no_suitable_pilot_found%',
        'several': 'report_crewlists.%several_pilots_found%',
    }

    ni = RaveIterator(RaveIterator.iter('report_crewlists.no_landing_recorded_iterator',
        where='report_crewlists.%no_landing_recorded%'))
    fi = RaveIterator(RaveIterator.iter('iterators.leg_set', where=(
                'report_crewlists.%designated_landing%',
                'report_crewlists.%%leg_end_utc%% >= %s' % firstdate,
                'report_crewlists.%%leg_end_utc%% < %s' % lastdate
                ), sort_by='leg.%start_utc%'),
                leg_info)
    xi = RaveIterator(RaveIterator.iter('iterators.flight_leg_set', where=(
                'report_crewlists.%no_suitable_pilot_found% or report_crewlists.%several_pilots_found%',
                'report_crewlists.%%leg_end_utc%% >= %s' % firstdate,
                'report_crewlists.%%leg_end_utc%% < %s' % lastdate
                ), sort_by='leg.%start_utc%'),
                leg_info)
    ni.link(legs=fi, faults=xi)

    try:
        flights = ni.eval('sp_crew')[0]
    except:
        raise ValueError('No flights where no landing is registrered within interval (%s - %s).' % (firstdate, lastdate))

    handled_flights = set()
    for leg in flights.chain('legs'):
        f = Flight(leg.fd, leg.udor, leg.adep)
        f.ades = leg.ades
        if not (leg.fd, leg.udor, leg.adep) in handled_flights:
            # Avoid recording landing for both FC and FP (SASCMS-1616)
            try:
                _update_database(f, leg.crewid)
            except:
                warn("Could not update landing information for %s, crew = %s." % (
                    f, leg.crewid))
        handled_flights.add((leg.fd, leg.udor, leg.adep))

    for leg in flights.chain('faults'):
        if leg.no_suitable:
            reason = "no suitable pilot found"
        elif leg.several:
            reason = "several suitable pilots found"
        else:
            # Should never happen
            reason = "for an unknown reason(!)"
        warn("Could not handle flight %s (%s)." % (Flight(leg.fd, leg.udor, leg.adep), reason))

    if nr_warnings > 0:
        msg = "Job completed with %d warnings." % nr_warnings
        warnings.warn(msg)
        return msg
    else:
        return "Job completed without warnings."


# _update_database -------------------------------------------------------{{{2
def _update_database(flight, crewid, replace=True):
    """ Update the database, add a new landing. """
    # Note, takes crew Id as argument, allowing override.
    ref_adep = TM.airport.getOrCreateRef(flight.adep)
    ref_ades = TM.airport.getOrCreateRef(flight.ades)
    ref_fd = TM.flight_leg[(flight.udor, flight.fd.flight_descriptor, ref_adep)]
    ref_crew = TM.crew[(crewid,)]
    if replace:
        for landing in ref_fd.referers('crew_landing', 'leg'):
            landing.remove()
    try:
        record = TM.crew_landing.create((ref_fd, ref_crew, ref_ades))
        record.nr_landings = 1
        record.activ = True
    except:
        # Could occur if 'return to station', the HERMES system does not know
        # our new flight suffix, so it will probably resend.
        record = TM.crew_landing[(ref_fd, ref_crew, ref_ades)]
        record.nr_landings += 1
        record.activ = True


# bit --------------------------------------------------------------------{{{2
def bit(s):
    """ Built-In Test, for basic test purposes """
    status.debug = True
    print report(
        requestName="CrewLanding", 
        flightId="SK485", 
        originDate="20060915", 
        depStation="ARN",
        empno="18943"
    )


# report ================================================================={{{1
def report(**k):
    """
    Create the report for given flight and employee number. Handle error
    conditions.  Check prerequisites and save landing.
    """
    try:
        i = InputData(**k)

        # Check if crew exists, if crew is working on flight, if crew has
        # qualifications to land the plane, and, if the flight is not a school
        # or test flight. If all conditions are met, save the landing.

        li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=i.ff.asTuple()))
        li.link(crew=CrewIterator(i.crewid))
        legs = li.eval(i.ff.context())
        if len(legs) < 1:
            msg = "Flight %s not found." % str(i.ff)
            raise ReplyError(i.requestName, status.FLIGHT_NOT_FOUND, msg, payload=crewLanding(msg))

        crew = None
        for leg in legs:
            for crew in leg.chain('crew'):
                break

        # If no crew found raise EmpnoNotOnFlightError
        if crew is None:
            msg = "Crew %s not found on this flight %s." % (i.empno, i.ff.flight)
            raise ReplyError(i.requestName, status.CREW_NOT_VALID, msg, payload=crewLanding(msg))

        # If flight has not started (see BZ 34913)
        if crew.now < crew.start_utc:
            msg = "Cannot handle landing for a future flight. Start time = %s, now = %s." % (crew.start_utc, crew.now)
            raise ReplyError(i.requestName, status.FLIGHT_NOT_VALID, msg, payload=crewLanding(msg))

        # Use first crew in result set
        if not crew.is_active_flight:
            msg = "Crew %s is not active on this flight %s." % (i.empno, i.ff.flight)
            raise ReplyError(i.requestName, status.CREW_NOT_VALID, msg, payload=crewLanding(msg))

        if crew.is_school_flight or crew.is_test_flight:
            msg = "The flight %s is a school or test flight." % (i.ff.flight,)
            raise ReplyError(i.requestName, status.FLIGHT_NOT_VALID, msg, payload=crewLanding(msg))

        if crew.main_func != "F" or crew.relief_pilot:
            # If crewid not qualified to land plane, update 'crew_landing' with
            # Pilot-In-Command instead.
            _update_database(i.ff.flight, crew.pic)
            # Raise InvalidLandingPilotWarning
            msg = "Crew %s not qualified to land this flight %s." % (i.empno, i.ff.flight)
            raise ReplyError(i.requestName, status.CREW_NOT_VALID, msg, payload=crewLanding(msg))
        else:
            _update_database(i.ff.flight, i.crewid)

        return str(Reply(i.requestName, payload=crewLanding("Ok")))

    except ReplyError, err:
        return str(err)

    except Exception, e:
        return str(Reply(report_name, status.UNEXPECTED_ERROR, utils.exception.getCause()))


# Main ==================================================================={{{1
class Main:
    """Handle command line arguments. Run Batch job that records crew landings
    for crew members that have flown one of the A/C types that don't get crew
    landing messages."""

    def __call__(self, from_date=None, to_date=None):
        """If no argument is given, then use previous UTC day. Check
        dates/times for validity before calling acars_batch()."""
        now, = rave.eval('fundamental.%now%')
        if to_date is None:
            a_to_date = now.day_floor()
        else:
            try:
                a_to_date = AbsTime(to_date)
            except:
                raise ValueError("to_date is not a valid date (%s)." % to_date)
        if from_date is None:
            a_from_date = a_to_date - RelTime(1, 0, 0)
        else:
            try:
                a_from_date = AbsTime(from_date)
            except:
                raise ValueError("from_date is not a valid date (%s)." % from_date)
        a_from_date = min(a_from_date, a_to_date)
        a_to_date = max(a_from_date, a_to_date)
        if a_to_date > now:
            a_to_date = now
            warnings.warn("Setting to_date to now (%s), cannot record landings for future flights." % now)
        if a_from_date > now:
            raise ValueError("Cannot record crew landings for future flights.")
        return acars_batch(a_from_date, a_to_date)

    def main(self, *argv):
        """Command line parser. We don't support command line, but the same
        logic would apply."""
        rc = 0
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            parser = OptionParser(description=("Start batch job to update crew landings"
                " for A/C types that don't have the ACARS system."))
            parser.add_option("-f", "--from-date",
                dest="from_date",
                help="First date/time for updates.")
            parser.add_option("-t", "--to-date",
                dest="to_date",
                help="Last date/time for updates.")
            (opts, args) = parser.parse_args(list(argv))
            self(opts.from_date, opts.to_date)

        except SystemExit, se:
            # parser.error
            rc = 2
        return rc


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    """ start basic test """
    run()
    #globals().get('__warningregistry__', {}).clear() # Not so nice...
    #TM.crew_landing.removeAll()
    #import Cui
    #Cui.CuiReloadTable('crew_landing')
    #main('-f', AbsTime(2009, 6, 1, 0, 0), '-t', AbsTime(2009, 8, 1, 0, 0))


# Description of the output format ======================================={{{1
# Crew enters landing information from the 'Hermes' system (from within the
# aircraft) This report updates the 'crew_landing' table and sends feedback
# with status code to the 'Hermes' system.
#
# The report is an XML message:
#
#       <?xml version="1.0" encoding="UTF-8"?>
#       <replyBody version="1.00">
#           <requestName>CrewLanding</requestName>
#           <statusCode>0</statusCode>
#           <statusText>Ok</statusText>
#       </replyBody>
#
#
# NOTE NOTE NOTE
# new format!
#       <?xml version="1.0" encoding="UTF-8"?>
#       <replyBody version="1.00">
#           <requestName>CrewLanding</requestName>
#           <statusCode>202</statusCode>
#           <statusText>Crew not found.</statusText>
#       </replyBody>
#
# Error codes (not used anymore, just for info)
#-----------------------------------------------------------------------------
# 0       Ok                       0        1         2         3         4
#                                  1234567890123456789012345678901234567890
#
# 1       Invalid empno entered    LANDING REGISTRATION REJECTED -
#                                  INVALID EMPNO, MUST BE 5 DIGITS
#                                  RE-SEND OTHER TELEX TO LDGRP00
#                                  ONLY WITH 5 DIGITS EMPNO
#
# 2       Empno not on flight      LANDING REGISTRATION REJECTED -
#         crewlist                 EMPNO DOES NOT MATCH CURRENT FLIGHT
#                                  PLEASE CHECK/CORRECT INIT DATA/EMPNO
#                                  AND RE-SEND OTHER TELEX TO LDGRP00
#
# 3       School or test flight    LANDING REGISTRATION REJECTED -
#                                  FLIGHT IS SCHOOL OR TEST FLIGHT
#                                  PLEASE USE OPUS OPMVT/TRA
#
# 4       Too much information.    N/A
#
# 5       Index = 0 for A/C        INVALID LANDING PILOT SELECTION
#         type A330 .and. A340     LANDING ASSIGNED TO COMMANDER BY DEFAULT
#         .or. Index > nr of crew  IF NOT CORRECT PLEASE SEND OTHER REPORT
#         on crewlist .or. Index   TO LDGRP00 WITH THE CORRECT EMPLOYEE
#         points to crew where     NUMBER
#         mainRank <> 'F'

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
