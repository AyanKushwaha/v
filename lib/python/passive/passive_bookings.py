
from BSIRAP import AbsDate

"""
Passive Bookings

Two types of runs:
    (1) Initial run, where we create one booking per deadhead.
    (2) Update run, triggered by changes in roster, can update, delete or
    create booking.
Both runs are equal, the only difference between the two is that the former
uses a list of crew to consider.
"""

import os
import carmensystems.rave.api as R
import Cfh
import Crs
import Cui
import Errlog
import modelserver
import report_sources.hidden.PassiveForecastReport
import utils.xmlutil as xml
import traceback

from tempfile import mkstemp
from AbsTime import AbsTime,PREV_VALID_DAY
from RelTime import RelTime
from Airport import Airport
from crewlists.crewmessage import Message
from dig.DigJobQueue import DigJobQueue
from tm import TM
from utils.data_error_log import log
from utils.divtools import fd_parser
from utils.edifact import latin1_to_edifact
from utils.fmt import CHR
from utils.fmt import INT
from utils.rave import RaveIterator
from utils.selctx import BasicContext
from utils.selctx import SingleCrewFilter
from utils.TimeServerUtils import now, nowLocal

report_name = 'CrewPassiveBooking'


# Message format ========================================================={{{1

# passiveBooking ---------------------------------------------------------{{{2
class passiveBooking(xml.XMLElement):
    """XML - 'passiveBooking' tag."""
    def __init__(self, booking):
        xml.XMLElement.__init__(self)
        self['version'] = "1.0"
        self.append(xml.string('bookingMessage', booking))


# GenericBookingMessage --------------------------------------------------{{{2
class GenericBookingMessage:
    """Format specification for Passive Booking text based message."""
    def __init__(self, name=None, empno=None, rank=None, flight=None,
            udor=None, sobt=None, adep=None, ades=None, cancelled=False, book_class=None,
            typ=None, costcenter=None, phone=None):
        self.name = name
        self.empno = empno
        self.rank = rank
        self.flight = flight
        self.udor = udor
        self.sobt = sobt
        self.adep = adep
        self.ades = ades
        self.cancelled = cancelled
        self.book_class = book_class
        self.typ = typ
        self.costcenter = costcenter
        self.phone = phone

    def __str__(self):
        # Message format:
        #
        # To adress:                string 7 'CPHRMSK'
        # New line:                 '\n'
        # From address:             string 9 '.CPHBUSK '
        # Day in month:             int 2
        # Time of day:              int 4
        # New line:                 '\n'
        # CPHSK47:                  string 7 'CPHSK47'
        # New line:                 '\n'
        # Crew indicator:           string 5 '1CREW'
        # Crew category:            string 2 
        # Dash:                     '/'
        # Surname and first name:   string 20
        # New line:                 '\n'
        # Flight nr:                string 7
        # Booking class:            string 1 'C' 'Y' 'M' 'F'
        # Day of activity:          int 2
        # Month of activity:        int 2
        # From station:             string 3
        # To station:               string 3
        # Telex type:               string 3 'XX1' 'FS1'
        # New line:                 '\n'
        # Text:                     string 25 'OSI SK PCR DH' 'OSI SK PCR'
        # New line:                 '\n'
        # Text:                     string 12 'OSI SK CCR'
        # Costcenter:
        # New line:                 '\n'
        # See SASCMS-2413

        f = fd_parser(self.flight)

        if self.cancelled:
            telexType = 'XX1'
#        elif f.carrier == 'KF':
#            telexType = 'LL1'
        else:
            telexType = 'FS1'
        
        ldor = Airport(self.adep).getLocalTime(self.sobt)
        
        result = [
            'CPHSK47',
            '1CREW%s/%s' % (
                CHR(2, self.rank),
                CHR(20, latin1_to_edifact(self.name, level='MRZ'))),
            '%s %s%s%s%s%s%s' % (
                CHR(2, f.carrier), 
                INT(4, f.number),
                CHR(1, self.book_class), 
                CHR(5, ('%s' % ldor)[:5]),
                CHR(3, self.adep), 
                CHR(3, self.ades), 
                CHR(3, telexType))]

        if self.typ == 'P':
            result.append(CHR(25, 'OSI SK PCR'))
        else:
            result.append(CHR(25, 'OSI SK PCR DH'))

        result.append('OSI SK CCR  %s' % (CHR(8, self.costcenter)))
        result.append('OSI SK IDC %s' % (CHR(6, self.empno)))
        result.append('OSI SK CTCM %s' % (CHR(11, ''.join([x for x in self.phone if x in '0123456789']))))
        result.append('OSI SK CTCE %s//SAS.DK' % (CHR(5, self.empno)))

        if f.carrier in ('SK','KF','WF'):
            result.append('OSI %s ID1/C1PA' % CHR(2, f.carrier))

        if f.carrier == 'KF':
            result.append('OSI KF C1PA')
            result.append('SSR FOID KF HK/ .ID96000%s/P1' % (CHR(5, self.empno)))
        else:
            result.append('SSR FOID SK HK/ .ID96000%s/P1' % (CHR(5, self.empno)))
        ticketingDate = max(ldor - RelTime(3 * 1440), nowLocal()) # SASCMS-4189 now() changed to nowLocal().
        result.append('XXXTKTL/%s/CPH026' % (str(ticketingDate)[:5]))
        result.append('XXXXI:FS/ETKT')
        result.append('XXXFPNO') # form of payment: NO
        result.append('XXXFFFNOFARE/A0') # FFF - No fare - no payment
        result.append('XXXFE %s' % (CHR(8, self.costcenter)))
        validTo = str(ldor.addmonths(3,PREV_VALID_DAY))[:5]
        result.append('XXXFC:%s L-%s %s %s 0.00YID00C1PA NUC0.00END' % (self.adep, validTo, f.carrier, self.ades))
        
        return '\n'.join(result)


# BookingMessage ---------------------------------------------------------{{{2
class BookingMessage(GenericBookingMessage):
    def __init__(self, b):
        emp = self.get_crew_employment(b.crew.id, b.flight.udor)
        if emp.carrier.id == 'SVS':
            if emp.base.id=='CPH':
                if emp.crewrank.maincat.id == 'F':
                    costcenter='00-17412'
                else:
                    costcenter='00-17415'
            else:
                if emp.crewrank.maincat.id == 'F':
                    costcenter='00-17152'
                else:
                    costcenter='00-17155'
        elif emp.carrier.id == 'SK':
            if emp.base.id=='CPH':
                if emp.crewrank.maincat.id == 'F':
                    costcenter='00-63209'
                else:
                    costcenter='00-65209'
        
            elif emp.base.id=='OSL':
                if emp.crewrank.maincat.id == 'F':
                    costcenter='00-69745'
                else:
                    costcenter='00-69765'
            else:
                if emp.crewrank.maincat.id == 'F':
                    costcenter = '00-62109'
                else:
                    costcenter = '00-65109'
        else:
            if emp.crewrank.maincat.id == 'F':
                costcenter = '00-62109'
            else:
                costcenter = '00-65109'
        phone = self.get_crew_phone(b.crew.id, b.flight.udor)
        GenericBookingMessage.__init__(self, 
            name="%s/%s" % (b.crew.name, b.crew.forenames),
            empno=emp.extperkey,
            rank=emp.crewrank.id,
            flight=b.flight.fd,
            udor=b.flight.udor,
            sobt=b.flight.sobt,
            adep=b.flight.adep.id,
            ades=b.flight.ades.id,
            cancelled=b.cancelled,
            book_class=b.book_class,
            typ=b.typ,
            costcenter=costcenter,
            phone=phone)
        
    def get_crew_phone(self, crewid, date):
        for w in ('main','home1','home2','other1'):
            for rec in TM.crew[(crewid,)].referers('crew_contact', 'crew'):
                if rec.typ.typ.lower() == 'tel' and rec.which.which == w :
                    return rec.val
        return "00000000"

    def get_crew_employment(self, crewid, date):
        """Return employment data at date."""
        for rec in TM.crew[(crewid,)].referers('crew_employment', 'crew'):
            if rec.validfrom <= date and date < rec.validto:
                return rec
        raise ValueError("Could not find valid employment data for crew = '%s' at date '%s'.")


# Data Model ============================================================={{{1

# Booking ----------------------------------------------------------------{{{2
class Booking(tuple):
    """Booking is used to store bookings in memory and be able to compare
    them."""
    def __new__(cls, crewid, code, book_class, fd, udor, adep):
        return tuple.__new__(cls, (crewid, code, book_class, fd, udor, adep))

    def __init__(self, crewid, code, book_class, fd, udor, adep):
        self.crewid = crewid
        self.code = code
        self.book_class = book_class
        self.fd = fd
        self.udor = udor
        self.adep = adep

    def __str__(self):
        return ('<' + self.__class__.__name__ + ' crew=%(crewid)s, code=%(code)s, '
                'class=%(book_class)s, fd=%(fd)s, udor=%(udor)s, adep=%(adep)s />') % self.__dict__

    def create(self):
        """Create a new passive booking line in the model."""
        airport = TM.airport[(self.adep,)]
        flight = TM.flight_leg[(self.udor, self.fd, airport)]
        crew = TM.crew[(self.crewid,)]
        booking = TM.passive_booking.create((crew, flight, self.code,
            self.book_class))
        booking.sent = False
        booking.cancelled = False


# PassiveBookingManager --------------------------------------------------{{{2
class PassiveBookingManager:
    """Create Passive Bookings, generate files with bookings, handle updates of
    database."""

    def __init__(self, context=None):
        """Set attributes that depend on if the script is run from within the
        Report Server or not."""
        bc = BasicContext()
        if context is None:
            self.context = bc.getGenericContext()
        else:
            self.context = context
        self.isRS = bc.isRS

    def create_bookings(self, from_date, to_date, modified_crew=[]):
        """Create/Update passive bookings for all crew (or modified_crew if
        modified_crew is given) and create/update bookings for all open
        trips."""

        from_date = AbsTime(from_date).day_floor()
        to_date = AbsTime(to_date).day_floor()

        rave_filter = [
            'leg.%%udor%% >= %s' % from_date,
            'leg.%%udor%% < %s' % to_date,
            'report_passive.%leg_is_deadhead%',
            'report_passive.%deadhead_ticket_required%',
            'fundamental.%is_roster%',
        ]
        model_filter = [
            '(flight.udor>=%s)' % from_date,
            '(flight.udor<%s)' % to_date,
        ]

        # Create/update bookings for assigned flights
        li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=tuple(rave_filter)), {
            'crewid': 'report_passive.%crew_id%',
            'empno': 'report_passive.%employee_number%',
            'code': 'report_passive.%code%',
            'booking_class': 'report_passive.%booking_class%',
            'fd': 'report_passive.%flight_descriptor%',
            'udor': 'report_passive.%flight_udor%',
            'adep': 'report_passive.%flight_start_stn%',
        })

        Errlog.log("passive_bookings: rave_filter = (%s)." % rave_filter)
        Errlog.log("passive_bookings: model_filter = (%s)." % model_filter)

        roster_bookings = set() 
        # First loop the rosters
        if modified_crew: #Booking update
            model_filter.append('(|%s)' % ''.join(['(crew=%s)' % c for c in modified_crew])) #Only include modified crew in cancellations loop
            for crew in modified_crew:
                for leg in li.eval(SingleCrewFilter(crew).context()):
                    roster_bookings.add(Booking(leg.crewid, leg.code, leg.booking_class,
                        leg.fd, leg.udor, leg.adep))
        else: #Night job
            for leg in li.eval(self.context):
                roster_bookings.add(Booking(leg.crewid, leg.code, leg.booking_class,
                    leg.fd, leg.udor, leg.adep))

        # Loop passive_booking:
        #  - if the booking has been removed from roster, cancel the booking
        #  - if the booking is marked as cancelled and crew has been
        #    re-assigned, remove cancel flag
        for pb in TM.passive_booking.search('(&%s)' % ''.join(model_filter)):
            try:
                b = Booking(pb.crew.id, pb.typ, pb.book_class, pb.flight.fd,
                        pb.flight.udor, pb.flight.adep.id)
            except Exception, e:
                # Referential errors, etc.
                msg = "Removed entry (%s) with errors in 'passive_booking'. Reason = %s" % (pb, e)
                log.error(msg)
                Errlog.log("passive_bookings: %s" % msg)
                pb.remove()
                continue

            if b in roster_bookings:
                if pb.cancelled:
                    # Re-activate booking
                    pb.cancelled = False
                    pb.sent = False
                roster_bookings.remove(b)
            else:
                # Booking is only in 'passive_booking', not on roster.
                if pb.sent:
                    if not pb.cancelled:
                        # Cancel and send again
                        pb.cancelled = True
                        pb.sent = False
                else:
                    # Remove from model
                    pb.remove()

        if not self.isRS:
            TM.refresh()

        for booking in roster_bookings:
            # Remaining bookings are new
            try:
                booking.create()
                Errlog.log("passive_bookings: Created booking for %s %s %s crew=%s" % (
                    booking.fd, booking.udor, booking.adep, booking.crewid))
            except modelserver.ModelError, me:
                err='passive_bookings:  ModelError - could not create Passive Booking: %s, reason = %s' % (str(booking), me)
                log.error(err)
                Errlog.log(err)
            except Exception, e:
                err='passive_bookings: Passive Booking not created: %s, reason = %s' % (str(booking), e)
                log.error(err)
                Errlog.log(err)

        # Force reload of Rave tables
        Cui.CuiReloadTable('passive_booking')

    def get_export_dir(self, create_dir=True):
        """Return the directory where passive bookings are written."""
        # Where to store export files
        exportDir = Crs.CrsGetModuleResource("passive", Crs.CrsSearchModuleDef, "ExportDirectory")
        # Create directory if it does not exist
        if create_dir and not os.path.exists(exportDir):
            os.makedirs(exportDir)
        return exportDir

    def get_not_sent(self):
        """Get all bookings that are not sent."""
        if not self.isRS:
            TM.refresh()
        return TM.passive_booking.search('(sent=false)')

    def send_bookings(self):
        """Create booking files, set status to sent if file creation succeded,
        return list of filenames written to."""
        L = []
        for b in self.get_not_sent():
            try:
                (fd, fn) = mkstemp(prefix='PassiveBooking', dir=self.get_export_dir(),
                        text=True)
                f = os.fdopen(fd, 'w')
                booking = BookingMessage(b)
                msg = str(Message(report_name, passiveBooking(booking)))
                f.write(msg)
                f.write('\n\n')
                f.close()
                os.chmod(fn, 0666)
                # Lastly, set booking as sent and append to list
                b.sent = True
                L.append(fn)
            except Exception, e:
                msg = "Could not create booking '%s'. %s" % (b, e)
                traceback.print_exc()
                log.error(msg)
                Errlog.log(msg)
        return L

    def set_default_context(self, modified_crew):
        """Set context to 'modified_crew'."""
        if self.isRS:
            # Don't run this on report server!
            return
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode,
                Cui.CrewMode, modified_crew, 0)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
        self.context = 'default_context'


# Interactive usage ======================================================{{{1

# PassiveBookingRunForm --------------------------------------------------{{{2
class PassiveBookingRunForm(Cfh.Box):
    """Form used to select date for a manual passive booking run."""
    def __init__(self, title):
        Cfh.Box.__init__(self, title)

        self.date = Cfh.Date(self, 'DATE')
        self.date.setMandatory(1)
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL')
        layout = '\n'.join((
            'FORM;A_FORM;Passive Booking Run',
            'FIELD;DATE;Date',
            'BUTTON;OK;`OK`;`_OK`',
            'BUTTON;CANCEL;`Cancel`;`_Cancel`',
        ))
        (fd, fn) = mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(layout)
        f.close()
        self.load(fn)
        os.unlink(fn)
        self.show(True)

    def getDate(self):
        return AbsTime(self.date.valof())


# Job submission ========================================================={{{1

# PassiveBookingSubmitter ------------------------------------------------{{{2
class PassiveBookingSubmitter(object):
    """Handle submissions to DIG channel for Passive Bookings, used by
    FileHandlingExt."""

    # Wait 'delay' minutes before the job is run
    delay = 2

    def __init__(self):
        self.modified_crew = []
        self.__job_queue = None

    @property
    def job_queue(self):
        """Return DigJobQueue object."""
        if self.__job_queue is None:
            self.__job_queue = DigJobQueue(channel='passive',
                    submitter='studio_save_passive_booking_job',
                    reportName='report_sources.report_server.rs_PassiveBooking',
                    useTimeServer=False)
        return self.__job_queue

    def prepare(self):
        """Check modified crew."""
        self.modified_crew = Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info)

    def crew_to_submit(self):
        search_string = "(&(job.channel=passive)(job.started_at=not_started)(job.submitter=studio_save_passive_booking_job)(paramname=crew*))"
        queued_crew = [row.paramvalue for row in TM.job_parameter.search(search_string)]
        return [crew for crew in self.modified_crew if crew not in queued_crew]

    def submit(self):
        """Submit Job if any crew was modified."""
        try:
            if self.modified_crew:
                params = {'bookingUpdate': 'True'}
                nr = 0
                submit_time, = R.eval('fundamental.%now%')

                for crewid in self.crew_to_submit():
                    params['crew%s' % nr] = crewid
                    nr=nr+1
                if nr == 0:
                    return
                # Add delay
                submit_time += RelTime(self.delay)
                self.job_queue.submitJob(params=params, reloadModel='1', curtime=submit_time)
        finally:
            # Just in case, to avoid two submit() without prepare() between
            self.modified_crew = []


# Functions =============================================================={{{1

def initial_bookings_form():
    """Show form to let user pick date for initial Passive Bookings."""
    f = PassiveBookingRunForm('Initial Passive Booking Run')
    if f.loop() != Cfh.CfhOk:
        return
    initial_bookings(f.getDate())


def update_bookings_form():
    """Show form to let user pick date for Passive Bookings update job."""
    f = PassiveBookingRunForm('Update Passive Booking Run')
    if f.loop() != Cfh.CfhOk:
        return
    update_bookings(f.getDate())


def passive_bookings_forecast():
    """Opens passive booking forecast report form."""
    report_sources.hidden.PassiveForecastReport.runReport()


def initial_bookings(from_date, to_date=None):
    """Run initial Passive Bookings from 'from_date' until 'to_date'. Create
    bookings and return list of file names."""
    m = PassiveBookingManager()
    if to_date is None:
        to_date = from_date + RelTime(1, 0, 0)
    m.create_bookings(from_date, to_date)
    return m.send_bookings()


def update_bookings(from_date, to_date=None, modified_crew=None):
    """Run update job for Passive Bookings, 'modified_crew' is an optional list
    which forces the job to handle these crew members. If 'modified_crew' is
    not given, then use 'CuiGetLocallyModifiedCrew()' to get such a list."""
    if modified_crew is None:
        modified_crew = Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info)
    if not modified_crew:
        return []
    if to_date is None:
        to_date = from_date + RelTime(10, 0, 0)
    m = PassiveBookingManager()
    m.set_default_context(modified_crew)
    m.create_bookings(from_date, to_date, modified_crew)
    return m.send_bookings()

def showTestReport():
    from tempfile import mkstemp
    import carmstd.studio.cfhExtensions as ext
    from os import unlink,fdopen
    f, filename = mkstemp('.txt')
    f = fdopen(f,'w')
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'report_passive.%crew_id%')
    udor = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'format_time(report_passive.%flight_udor%, "%Y%02m%02d")')
    fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'report_passive.%flight_descriptor%')
    #flt = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'concat(format_time(report_passive.%flight_udor%, "%Y%m%d"),"+",report_passive.%flight_descriptor%,"+",report_passive.%flight_start_stn%)')
    print crew,udor,fd
    for b in TM.passive_booking.search('(&(crew=%s)(flight.udor=%s)(flight.fd=%s))' % (crew, udor, fd)):
        print >>f, str(BookingMessage(b))
    f.close()
    ext.showFile(filename, "Passive bookings %s %s" % (crew, fd))
    unlink(filename)
# "Singleton"
run = PassiveBookingSubmitter()

# Used by FileHandlingExt
prepare = run.prepare
submit = run.submit


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
