"""
This module contains the logic for creating a Checkin/Checkout message
according to the ACCI format.

cio.acci  : Creation and formatting of ACCI message string.
cio.rv    : Rave interface.
cio.db    : Database interface.
"""

# imports ================================================================{{{1
import cio.acci as acci
import cio.rv as rv
import cio.db as db
import crewlists.status as status
import crewinfoserver.data.check_in as check_in

from AbsTime import AbsTime
from RelTime import RelTime
from utils.exception import getCause
import traceback

# setup logging =========================================================={{{1
import logging
log = logging.getLogger('cio.run')


# constants =============================================================={{{1
# Checkin/out status
NO_CIO = '0'
CI = '1'
CO = '2'
COI = '3'


# classes ================================================================{{{1

# CIOException -----------------------------------------------------------{{{2
class CIOException(Exception):
    """ Signals that checkin or checkout operation failed """
    msg = ''
    def __init__(self, msg):
        Exception.__init__(self, self.msg)
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# ReportMaker ------------------------------------------------------------{{{2
class ReportMaker:
    """ Build-up the actual report. """

    # Formatting strings
    h01 = ("H01", 0, 0)  # Arial 14pt bold
    p01 = ("P01", 0, 0)  # italic
    p02 = ("P02", 0, 0)  # bold
    p10 = ("P10", 0, 0)  # 12pt
    p50 = ("P50", 0, 0)  # underline
    #p51 = ("P51", 0, 0)  # line shift (not used)
    #del = ("DEL", 0, 0)  # Supress output (for TAP)

    # Indention width for rows where header is on the same row as content
    hwid = 12

    def __init__(self, extperkey, update_delivered=False):
        self.extperkey = extperkey
        self.update_delivered = update_delivered
        self.id = rv.extperkey2id(extperkey)
        if self.id is None:
            raise rv.NotFoundException(extperkey)
        self.r = rv.EvalRoster(self.id)
        self.status = str(self.r.cio_status).split('.')[1]
        self.acci = acci.ACCI()
        self.acci(mesno=status.NO_CIO)

    # The different reports ----------------------------------------------{{{3
    def checkin_report(self):
        self.report_header("CHECK IN VERIFICATION")
        self.going_to()
        if self.r.next_is_passive:
            self.pic_ca1()
        self.crew_info()
        self.expiry_info()
        self.passive_duty()
        self.preliminary_ca1()
        self.special_info()
        self.crew_list()
        self.revised_schedule()

        # [acosta:08/298@15:43] Added perkey, I don't know if this is correct
        # but it helps when searching for faults...
        self.acci(mesno=status.OK, cico=CI, perkey=self.extperkey)

        # SKCIS-91: Submit check_in status update to Crew Info Server
        check_in.submit(self.extperkey)
        return self.acci

    def checkout_report(self):
        self.report_header("CHECK OUT VERIFICATION")
        self.coming_from()
        self.next_duty()
        self.crew_info()
        self.revised_schedule()
        self.acci(
            mesno=status.OK, 
            cico=CO, 
            dutycd=self.r.co_dutycd,
            activityid=self.r.co_activityid,
            udor=self.r.co_origsdt_utc,
            adep=self.r.co_stnfr,
            std=self.r.co_std,
            sta=self.r.co_sta,
            eta=self.r.co_eta,
            perkey=self.extperkey,
        )
        return self.acci

    def coi_report(self):
        self.report_header("CHECK OUT VERIFICATION")
        self.coming_from()
        self.acci.append('')
        self.acci.appendf("CHECK IN VERIFICATION", self.h01)
        self.acci.append('')
        self.going_to()
        if self.r.next_is_passive:
            self.pic_ca1()
        self.crew_info()
        #self.expiry_info()
        self.passive_duty()
        self.special_info()
        self.crew_list()
        self.revised_schedule()

        self.acci(mesno=status.OK, cico=CI, perkey=self.extperkey)
        return self.acci

    def too_early_too_late_report(self):
        self.report_header("CHECK IN/CHECK OUT MESSAGE")
        self.acci.append("%s   %-30s" % (self.extperkey, self.r.logname))
        self.crew_info()
        self.reason()
        self.revised_schedule()
        self.acci(mesno=status.OK, cico=NO_CIO, perkey=self.extperkey)
        return self.acci

    def failed_report(self):
        msg = "Failed to create report"
        if self.status == 'ci':
            msg = "Checkin failed"
        elif self.status == 'co':
            msg = "Checkout failed"
        elif self.status == 'coi':
            msg = "Checkout/checkin failed"
        self.report_header(msg)
        self.acci(mesno=status.NO_CIO, cico=NO_CIO, perkey=self.extperkey)
        log.warning("failed_report() reason=%s, perkey=%s." % (msg, self.extperkey))
        return self.acci

    def unhandled_report(self):
        self.report_header("Cannot perform requested action, try again later")
        self.acci(mesno=status.NOT_AVAILABLE, cico=NO_CIO, perkey=self.extperkey)
        log.warning("unhandled_report() perkey=%s" % self.extperkey,)
        return self.acci

    # One-liners ---------------------------------------------------------{{{3
    def pic_ca1(self):
        # [acosta:08/168@16:24] WP Int 198
        if not self.r.ci_pic_logname is None:
            self.acci.append(self._hline("PIC", self.r.ci_pic_logname))
        if not self.r.ci_ca1_logname is None:
            self.acci.append(self._hline("AP, SCC", self.r.ci_ca1_logname))

    def going_to(self):
        if self.r.ci_udor is None:
            log.warning("going_to() - ci_udor was void.")
        else:
            self.acci.append("%-8.8s   %-30.30s DUTY %-20.20s STD %s" % (
                self.extperkey,
                self.r.logname,
                self._flight_id(self.r.ci_flight_name, self.r.ci_udor),
                "%02d:%02d" % self.r.ci_std.split()[3:5]
            ))

    def coming_from(self):
        if self.r.co_udor is None:
            log.warning("coming_from() - co_udor was void.")
        else:
            self.acci.append("%-8.8s   %-30.30s   %20.20s" % (
                self.extperkey,
                self.r.logname,
                self._flight_id(self.r.co_flight_name, self.r.co_udor)
            ))

    def next_duty(self):
        def check_in(req, ci):
            if req:
                return "  C/I %02d:%02d" % ci.split()[3:5]
            else:
                return ""
        if self.r.next_udor is None:
            log.warning("next_duty() - next_udor was void.")
        else:
            self.acci.append('')
            if self.r.next_is_pact:
                datum = self.r.next_std
            else:
                datum = self.r.next_udor
            self.acci.append(self._hline("Next duty", "%s STD %s%s" % (
                self._flight_id(self.r.next_flight_name, datum),
                "%02d:%02d" % self.r.next_std.split()[3:5],
                check_in(self.r.next_req_cio, self.r.next_checkin)
            )))

    # Building blocks ----------------------------------------------------{{{3
    def crew_info(self):
        """ Get Office info and Private info for a crew member. """
        ci = db.CrewInfo(self.id, self.r.now)
        if ci:
            self.acci.append('')
            first = True
            for msg in ci:
                if first:
                    self.acci.append(self._hline("Notification", msg.header))
                    first = False
                else:
                    self.acci.append(self._oline(msg.header))
                for row in msg.fmtList(50):
                    self.acci.append(self._oline(row))
            if self.update_delivered:
                ci.setDelivered()

    def crew_list(self):
        """ Get the crew list for next leg. """
        if self.r.next_is_active_another_day:
            return
        self.acci(cli_info=False)
        cl = rv.CrewList(self.id)
        if cl:
            self.acci.append('')
            self.acci(cli_info=True)
            self.acci.append('')
            if self.r.next_is_passive:
                htext = 'CREW-LIST FOR FIRST ACTIVE LEG'
            else:
                htext = 'CREW-LIST'
            self.acci.appendf(htext, self.h01)
            self.acci.append('')
            for c in cl:
                self.acci.append(c.flightindic)
                self.acci.append('')
                self.acci.appendf(c.header, self.p50)
                for e in c:
                    self.acci.append(e)

    def expiry_info(self):
        """ Information about documents that are about to expire. """
        ed = db.ExpiryInfo(self.id, self.r.now)
        if ed:
            self.acci.append('')
            first = True
            for e in ed:
                if first:
                    self.acci.append(self._hline("Expire info", str(e)))
                    first = False
                else:
                    self.acci.append(self._oline(str(e)))

    def passive_duty(self):
        """ Information about coming deadhead legs in the coming duty pass. """
        pl = rv.PassiveLegs(self.id)
        if pl:
            self.acci.append('')
            self.acci.appendf("Passive duty", self.p01)
            for leg in pl:
                self.acci.append("%s" % self._flight_id(leg.flight_name, leg.udor))

    def preliminary_ca1(self):
        """
        You are preliminary SCC on the following flights.
        """
        pc = rv.PrelCA1(self.id)
        if pc:
            self.acci.append('')
            self.acci.appendf("You are preliminary SCC on the following flight(s)", self.p01)
            for leg in pc:
                self.acci.append("%s  %s - %s" % (self._flight_id(leg.flight_name, leg.udor), leg.adep, leg.ades))

    def reason(self):
        """
        Print reason for not being checked in.
        """
        # Check-in already performed
        # Check-out already performed
        # Check-out/in already performed
        # Too early or too late for check-in/out
        # Check-in rejected - flight cancelled
        # Flight cancelled - Contact crew service center
        if self.status == 'alreadyci':
            self.acci.appendf("Already checked in.", self.h01)
        elif self.status == 'alreadyco':
            self.acci.appendf("Already checked out.", self.h01)
        elif self.status == 'late4co':
            self.acci.appendf("Too late for check-out.", self.h01)
        else:
            self.acci.appendf("Too early for check-in.", self.h01)

    def report_header(self, message):
        """
        Format the header of the different reports.
        """
        self.acci.appendf("%-50s%s" % (message, self.r.now_cph), self.h01)
        self.acci.append('')

    def revised_schedule(self):
        """
        Get a revised schedule (from crew_notification).
        """
        # Get crew which share the same leg and which fulfills the filters
        legFilter = 'rescheduling.%leg_inf_has_extended_fdp% or report_common.%is_extended_fdp%'
        equalLegFilter = 'crew_pos.%assigned_function% = "FC"' 
        equalLegsCrewlist = rv.getEqualLegsCrew(self.id, legFilter, equalLegFilter)
        
        self.acci(rev_info=False)
        ri = rv.RevisedRosterInfo(self.id, self.r.now)
        if ri:
            self.acci(rev_info=True)
            self.acci.append('')
            self.acci.appendf("REVISED ROSTER", self.h01)
            self.acci.append("%-8.8s %s" % (self.extperkey, self.r.logname))
            for duty in ri:
                self.acci.append('')
                period_start, period_end = duty.interval
                self.acci.appendf("PERIOD %s - %s" % (str(period_start).split()[0], str(period_end - RelTime(1)).split()[0]))
                self.acci.appendf("ORIGINAL SCHEDULE", self.p01)
                self.acci.append(duty.original_roster)
                #self.acci.appendf("COMMENTS", self.p01)
                self.acci.append('')
                self.acci.appendf("REVISED ROSTER:  (-->indicates changed roster)", self.p01)
                self.acci.appendf(duty.header, self.p50)
                for row in duty:
                    self.acci.append(row)
        if self.update_delivered:
            # Set notification status to 'delivered'
            ri.setDelivered()
            # *** Publish ***
            # The period will be from the first date loaded (see WP CCT-FAT
            # 417) in the plan till the last date used in comparison between
            # published and informed rosters. If RevRosterInfo did not get any
            # hits, we will still published everything until now.
            if ri.max_time is None:
                max_time = self.r.now
            else:
                max_time = ri.max_time
            rv.publish(self.id, self.r.f_loaded_data_period_start_utc, max_time, equalLegsCrewlist)

    def special_info(self):
        """
        Format the block of special messages, targeted for a specific flight.
        """
        self.acci(fli_info=False)
        si = db.SpecialInfo(self.id, self.r.now)
        if si:
            self.acci(fli_info=True)
            self.acci.append('')
            self.acci.appendf("SPECIAL INFORMATION", self.h01)
            ostd_lt = AbsTime(0)
            for s in si:
                if s.leg.std_lt != ostd_lt:
                    # Print flight info for each new leg
                    self.acci.append('')
                    self.acci.append(s.legHeader())
                self.acci.append('')
                self.acci.appendf("- %s" % s.messageHeader(), self.p01)
                ostd_lt = s.leg.std_lt
                self.acci.extend(s.fmtList(60))

    # Private methods ----------------------------------------------------{{{3
    def _hline(self, head, text):
        return "%-*s : %s" % (self.hwid, head, text)

    def _oline(self, text):
        return "%-*s   %s" % (self.hwid, ' ', text)

    def _flight_id(self, flight_name, udor):
        # Changed to correct WP Int-FAT 103, is it correct now?
        #import utils.divtools as divtools
        #if divtools.is_base_activity(flight_name):
        #    return flight_name
        #else:
        return "%s/%s" % (flight_name, str(udor).split()[0])


# functions =============================================================={{{1

# error ------------------------------------------------------------------{{{2
def error(num):
    rec = acci.ACCI()
    rec(mesno=num, cico=NO_CIO)
    return rec


# prt_report -------------------------------------------------------------{{{2
def prt_report(crewid):
    """Wrapper to PRT report."""
    import report_sources.hidden.CIOReport
    return report_sources.hidden.CIOReport.run_report(crewid)


# report -----------------------------------------------------------------{{{2
def report(empno=None, status_change=True, decode=False, raw=False):
    """ Used by GUI, etc. """
    acci = run(empno, status_change)
    if decode:
        return acci.decode()
    if raw:
        return str(acci)
    return acci.asXML()
    

# report_delta -----------------------------------------------------------{{{2
def report_delta(empno=None, status_change=True):
    """ Used by Report Server, returns XML formatted report and status flag. """
    acci = run(empno, status_change)
    return (acci.asXML(), acci.ok())

def any_crew():
    fc = None
    bc = None
    for r in rv.EvalRoster(None).rosters:
        if not fc:
            fc = r.extperkey
        if str(r.cio_status) in ("checkinout.ci", "checkinout.coi"):
            bc = r.extperkey
            break
    return bc or fc


# run --------------------------------------------------------------------{{{2
def run(extperkey=None, status_change=True):
    """ 
    'extperkey' is the crew employee number of the person that is performing
    the checkin or checkout.

    If 'status_change' is False, then nothing is recorded in the database.

    All Exceptions are captured.

    An ACCI object is returned
    """
    if extperkey is None:
        return error(status.WRONG_NUMBER_OF_ARGUMENTS)

    try:
        r = ReportMaker(extperkey, status_change)
    except rv.NotFoundException, e:
        log.error(getCause())
        a = acci.ACCI()
        a.appendf(e)
        a(mesno=status.CREW_NOT_FOUND, cico=NO_CIO)
        return a
    except Exception, e:
        log.error(getCause())
        a = acci.ACCI()
        a.appendf("SYSTEM FAILURE FOR CREW '%s'" % (extperkey), ("H01", 0, 0))
        a(mesno=status.UNEXPECTED_ERROR, cico=NO_CIO)
        return a
    try:
        if r.status == 'ci':
            if status_change:
                try:
                    db.record_cio_event(r.r.id, r.r.now, st=r.r.estimated_st,
                            et=r.r.estimated_et, status=db.ciostatus.CI)
                    db.set_ci_frozen(r.r.id, r.r.estimated_st, 
                            comment="Frozen at check-in")
                except Exception, e:
                    log.error(getCause())
                    raise CIOException("Checkin for '%s' failed." % (extperkey))
            return r.checkin_report()

        elif r.status == 'co':
            if status_change:
                try:
                    db.record_cio_event(r.r.id, r.r.now, et=r.r.now,
                            status=db.ciostatus.CO)
                except Exception, e:
                    log.error(getCause())
                    raise CIOException("Checkout for '%s' failed." % (extperkey))
            return r.checkout_report()

        elif r.status == 'coi':
            if status_change:
                try:
                    db.record_cio_event(r.r.id, r.r.now, st=r.r.estimated_st,
                            et=r.r.estimated_et, status=db.ciostatus.COI)
                    # Don't freeze at optional CI/CO, that affects legs way behind
                except Exception, e:
                    log.error(getCause())
                    raise CIOException("Checkin/Checkout for '%s' failed." % (extperkey))
            return r.coi_report()

        elif r.status in ('alreadyci', 'alreadyco', 'early4ci', 'late4co'):
            return r.too_early_too_late_report()

        else:
            return r.unhandled_report()

    except CIOException, e:
        traceback.print_exc()
        log.error(e)
        return r.failed_report()

    except Exception, e:
        traceback.print_exc()
        log.error(getCause())
        return r.failed_report()


# bit --------------------------------------------------------------------{{{2
def bit(id):
    """
    Built-In Test
    Runs _bit for each argument
    -or-
    if no arguments, for all crewid's and finally one impossible crewid.
    
    """
    s = report(id)
    print s


# main ==================================================================={{{1
if __name__ == '__main__':
    """ Run Built-In Test """
    #import sys
    #bit(sys.argv[1:])
    def profrun():
        bit("25727")
    import profile
    profile.run("profrun()")
