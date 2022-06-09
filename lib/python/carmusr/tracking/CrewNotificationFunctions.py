
#
# Purpose: Functions for notifications
#
# Sections: 1 Shared functions
#           2 Manual notifications
#           3 Automatic notifications
#            .1 Automatic Assignment Notifications
#            .2 Automatic Rest Schedule Notifications
#           4 View notifications
#
# [acosta:08/059@10:34] Removed Hermes logic, since we don't have an interface
# to Hermes (yet).  If you want to see this code, look at Revision 1.46 or older.

"""
Server code for the Crew Notification application.
"""

import copy
import re
import string
import time

import Cui
import modelserver as M
import StartTableEditor
import carmensystems.services.dispatcher as CSD
import Errlog
import carmensystems.rave.api as r
import carmstd.rave
import utils.Names as Names
import Gui
import carmstd.cfhExtensions as cfhExtensions

#import utils.divtools
import utils.wave

from Airport import Airport
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
from tm import TM, TempTable
from utils.rave import RaveIterator, RaveEvaluator
from utils.wave import LocalService
from utils.performance import clockme, log
# from rosterserver.roster import roster_push

ONE_DAY = RelTime(24, 0)

#******************************************************************************
# Section 1: Shared functions
#******************************************************************************
        
# Globals
crewNotification = None
viewNotifications = None
        
def any(iter):
    for i in iter:
        if i: return True
    return False

START_SEQ_NO = 1

# @clockme
# def update_rosterserver(crew, start, end):
#     log( "Pushing data for crew: %s , start time: %s, end_time: %s "% (crew, start, end))
#     Cui.CuiDisplayGivenObjects(Cui.gpc_info,
#                                Cui.CuiScriptBuffer,
#                                Cui.CrewMode,
#                                Cui.CrewMode,
#                                [crew])
#     Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
#
#     roster_push.get_rosters(start, end)

def alert_type(is_alert):
    """Return subtype of the Notification."""
    return ('!NoAlert', '*Alert')[bool(is_alert)]


def getOneCrew(fields):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    context = carmstd.rave.Context("object", area)
    crewItr = RaveIterator(RaveIterator.iter('iterators.roster_set'), fields)
    returnObject = crewItr.eval(context)
    return returnObject


def getAllCrewInWindow(fields):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea) 
    context = carmstd.rave.Context("window", area)
    crewItr = RaveIterator(RaveIterator.iter('iterators.roster_set'), fields)
    returnObject = crewItr.eval(context)
    return returnObject


def getCrewOnLeg(crewFields):
    # The info fields needs to be defined within a class. 
    class CrewInfo:
        fields = crewFields
    
    # Set the area
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # Find some key values regarding the selected leg.
    a_id = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "activity_id")
    c_id = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crew.%id%")
    key = Cui.CuiCrcEval(Cui.gpc_info, area, "object", "leg_identifier") 

    # Make the selected leg default context.
    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(key))
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'OBJECT')

    flight_condition = ('fundamental.%is_roster%', 'activity_id="%s"' %a_id)
    crew_condition = list(flight_condition)
    crew_condition.append('leg.%is_active_flight%')
    crew_condition = tuple(crew_condition)

    # Find all crew using the rave util.        
    fi = RaveIterator(RaveIterator.iter("iterators.leg_set",
                                     where=flight_condition))

    ei = RaveIterator(RaveIterator.iter('equal_legs'))
    ci = RaveIterator(RaveIterator.iter('iterators.leg_set',
                                     where=crew_condition,
                                     sort_by=('crew_pos.%func2pos%(crew.%rank_trip_start%)',
                                              'crew.%seniority%')), CrewInfo())
    fi.link(ei)
    ei.link(ci)
    flights = fi.eval('default_context')

    for flight in flights:
        for equal_leg in flight.chain():
            return equal_leg.chain()

    return


class NotificationSystemError(IndexError):
    def __init__(self, system):
        "Incorrect notification system: %s" %system


class NotificationError(Exception):
    msg = ''
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return str(self.msg)


def formatTime(someAbsTime):
    return str(someAbsTime)[10:12] + str(someAbsTime)[13:]

    
#******************************************************************************
# Section 2: Manual notifications
#******************************************************************************

class CrewNotification:
    # This class contains the temporary tables which are used for the
    # notification xml-form

    MAX_MESSAGE_LENGTH = 200 # Max no of char in the not. mess.
    SINGLE_CREW_NOTIFICATION = "Single Crew Notification"
    FLIGHT_CREW_NOTIFICATION = "Flight Crew Notification"
    GROUP_CREW_NOTIFICATION = "Group Notification"
    # Hard coded, no current support for other systems.
    DEFAULT_SYSTEM = "Portal"

    def __init__(self, menu):
        self.fields = {
            'id': 'crew.%id%',
            'logname': 'crew.%login_name%',
            'next_cio': 'checkinout.%crew_next_visit_at_portal%',
            'emp': 'crew.%employee_number%'
        }
        deadline = r.eval("fundamental.%now%")[0] + RelTime(24,0)

        if menu == "crew_object":
            # Get first and last names
            self.form_header = CrewNotification.SINGLE_CREW_NOTIFICATION
            self.crew_list = getOneCrew(self.fields)
            flight_data = self.flight_info_crew()
            crew_entry = self.crew_list[0]
            deadline = crew_entry.next_cio or deadline
            msgbox = (
                "Empno: %s<BR>"
                "Login Name: %s<BR><BR>"
                "Next Check-in/out: %s") % (
                    crew_entry.emp,
                    crew_entry.logname,
                    crew_entry.next_cio or "-")
            self.tt_crew_info = self.CrewInfoTempTable(msgbox, '(&(typ.typ=Manual)(crew=%s))' % crew_entry.id,
                    crew_entry.emp)

        elif menu == "assignment_general":
            # Crew shown in window
            winnr = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            self.form_header = CrewNotification.GROUP_CREW_NOTIFICATION
            self.crew_list = getAllCrewInWindow(self.fields)
            flight_data = []
            # Note that windows in Studio are (0, 1, 2, 3) add 1 to get displayed number.
            msgbox = "Notifications will be sent to all crew in Window %d" % (winnr + 1)
            self.tt_crew_info = self.CrewInfoTempTable(msgbox, '(&(typ.typ=Manual))')

        elif menu == "assignment_object":
            # Get all crew on this leg.
            self.form_header = CrewNotification.FLIGHT_CREW_NOTIFICATION
            self.fields['inCommand'] = 'crew_pos.%acting_commander%' 
            self.crew_list = getCrewOnLeg(self.fields)
            if self.crew_list is None:
                raise NotificationError("Not possible to send notifications to "
                                        "an activity that is not an active flight")
            leg_info = self.FlightInfoLeg()
            flight_data = [leg_info]
            deadline = leg_info.ciOnTrip or deadline
            picInfo = "(None assigned)"
            for crew in self.crew_list:
                if crew.inCommand:
                    picInfo = "%s %s" % (crew.emp, crew.logname)
                    break
            msgbox = "Notifications will be sent to all crew currently" \
                     " rostered on the %s.<BR><BR>Pilot in command: %s" \
                     % (("activity", "flight")[leg_info.isFlight], picInfo)
            self.tt_crew_info = self.CrewInfoTempTable(msgbox, '(&(typ.typ=Manual))')

        else:
            raise NotificationError("Notification started with unknown argument %s." % menu)

        self.tt_flight_info = self.FlightInfoTempTable(flight_data or [])
        self.tt_form_info = self.FormInfoTempTable(self.form_header, deadline)

    def check_validity(self):
        """Check validity of notification."""
        for row in self.tt_form_info:
            if not row.message:
                raise NotificationError(
                        "Empty notifications not allowed. Please specify a message")
            elif row.alert:
                # Check for empty or too early deadlines.
                try:
                    if row.deadline <= r.eval("fundamental.%now%")[0]:
                        raise NotificationError("Please specify a deadline in the future")
                except ValueError:
                    raise NotificationError("No EMPTY deadline accepted. Please specify one.")

    def flight_info_crew(self):
        # If the form is started for a single crew: Get flight info until
        # the end of the next duty.
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                Cui.CrewMode, Cui.CrewMode, [str(self.crew_list[0].id)], 0)
        context = carmstd.rave.Context("window", Cui.CuiScriptBuffer)
        di = RaveIterator(RaveIterator.iter('iterators.duty_set', 
            where="duty.%end_UTC% > fundamental.%now%"))
        li = RaveIterator(RaveIterator.iter('iterators.leg_set', 
                where='leg.%end_UTC% > fundamental.%now%'),
            {
                'flight_number': 'leg.%flight_name%',
                'departure_airport': 'leg.%start_station%',
                'departure_time': 'leg.%start_utc%',
                'arrival_time': 'leg.%end_utc%'
            })
        di.link(li)
        for duty in di.eval(context):
            return duty

    def set_status_message(self, message, isWarning=False):
        # Sets the status message which will be displayed in the XML form
        for row in self.tt_form_info:
            if isWarning:
                row.status_color = "red"
                Errlog.log("CREW NOTIFICATION: " + message)
            else:
                row.status_color = "transparent"
            row.status_message = message

    class CrewInfoTempTable(TempTable):
        def __init__(self, msg, filter=None, empno=None):
            TempTable.__init__(self, "tmp_cn_crew_info3", 
                [M.StringColumn("row_id", "Row Id")], 
                [
                    M.StringColumn("crew_info_row", "Crew Info Row"),
                    M.StringColumn("filter", "Crew Filter"),
                    M.StringColumn("empno", "Extperkey"),
                ])
            self.removeAll()
            record = self.create(("0",))
            record.crew_info_row = msg
            if not filter is None:
                record.filter = filter
            if not empno is None:
                record.empno = empno

    class FlightInfoTempTable(TempTable):
        def __init__(self, flight_data=[]):
            TempTable.__init__(self, "tmp_cn_flight_info",
                [M.StringColumn("row_id", "Row Id")],
                [
                    M.StringColumn("flight_number", "Flight number"),
                    M.StringColumn("departure_airport", "Departure airport"),
                    M.TimeColumn("departure_time", "Departure time"),
                    M.TimeColumn("arrival_time", "Arrival time")
                ])
            self.removeAll()
            i = 0
            for entry in flight_data:
                rec = self.create((str(i),))
                rec.flight_number = entry.flight_number
                rec.departure_airport = entry.departure_airport
                rec.departure_time = entry.departure_time
                rec.arrival_time = entry.arrival_time
                i += 1

    class FormInfoTempTable(TempTable):
        def __init__(self, header, deadline):
            TempTable.__init__(self, "tmp_cn_form_info",
                [M.UUIDColumn("form_id", "Form Id")],
                [
                    M.StringColumn("form_header", "Form Header"),
                    M.StringColumn("status_message", "Status Message"),
                    M.StringColumn("status_color", "Status Color"),
                    M.StringColumn("message", "Message"),
                    M.StringColumn("si", "Supplementary Info", 100),
                    M.TimeColumn("deadline", "Deadline"),
                    M.BoolColumn("alert","True if message is should generate alert"),
                ])
            self.removeAll()
            formId = TM.createUUID()
            record = self.create((formId,))
            record.form_header = header
            record.status_message = ""
            record.message = ""
            record.si = ""
            record.deadline = deadline
            if header == CrewNotification.SINGLE_CREW_NOTIFICATION:
                # To generate alerts default for Single Crew Notifications, and
                # yeah, this way of finding out that it's for a single crew
                # member is ugly.
                record.alert = True
            else:
                record.alert = False

    class FlightInfoLeg:
        def __init__(self):
            # If the form is started for a flight: Get the departure time.
            area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            self.flight_number = Cui.CuiCrcEvalString(Cui.gpc_info, area,
                    "object", "leg.%flight_name%")
            self.departure_airport = str(Cui.CuiCrcEval(Cui.gpc_info, area,
                    "object", "leg.%start_station%"))
            self.departure_time = Cui.CuiCrcEval(Cui.gpc_info, area,
                    "object", "leg.%start_utc%")
            self.arrival_time = Cui.CuiCrcEval(Cui.gpc_info, area,
                    "object", "leg.%end_utc%")
            self.ciOnTrip = Cui.CuiCrcEval(Cui.gpc_info, area,
                    "object", "trip.%start_utc%")
            self.isFlight = Cui.CuiCrcEvalBool(Cui.gpc_info, area,
                    "object", "leg.%is_flight_duty%")


def createMessageBody(message):
    uuid = TM.createUUID()
    seq_no = START_SEQ_NO
    while message:
        messageRow = TM.notification_message.create((uuid, seq_no))
        messageRow.free_text = message[:crewNotification.MAX_MESSAGE_LENGTH]
        message = message[crewNotification.MAX_MESSAGE_LENGTH:]
        seq_no += 1
    return uuid


def createCrewHeader(crew, uuid):
    crewRef = TM.crew.getOrCreateRef((crew,))
    headerRow = TM.crew_notification.create((crewRef, uuid))
    for row in crewNotification.tt_form_info:
        headerRow.created = r.eval("fundamental.%now%")[0]
        headerRow.created_by = Names.username()
        headerRow.system = TM.notification_systems.getOrCreateRef((CrewNotification.DEFAULT_SYSTEM," "))
        headerRow.typ = TM.notification_set.getOrCreateRef(("Manual", alert_type(row.alert)))
        # Set deadline to now if the notification does not generate alerts.
        headerRow.deadline = (headerRow.created, row.deadline)[bool(row.alert)]
        headerRow.si = row.si
        headerRow.failmsg = "(Manual)"
 

def createNotification(crewList, message):
    uuid = createMessageBody(message)
    for crew in crewList:
        createCrewHeader(crew.id, uuid)


def saveNotifications(*args):
    """
    XML-RPC method.
    Save notification after validity check.
    """
    try:
        crewNotification.check_validity()
    except NotificationError, ne:
        crewNotification.set_status_message(str(ne), True)
        return
    for row in crewNotification.tt_form_info:
        createNotification(crewNotification.crew_list, row.message)
    Cui.CuiReloadTable("crew_notification", Cui.CUI_RELOAD_TABLE_SILENT)
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    Gui.GuiCallListener(Gui.ActionListener)
    crewNotification.set_status_message("")


def startCrewNotification(menu):
    """
    Called from Studio menu.
    Start the crew notification form.
    Note: Only one form is allowed to be open at any time.
    """
    # This variable is used to show user which window number.
    TM("crew", "crew_notification", "notification_systems", "notification_set",
            "notification_message")
    # Starts the notification form.
    form_name = '$CARMUSR/data/form/%s' % 'crew_notification.xml'
    state = StartTableEditor.getFormState(form_name)
    if state not in (None, 'error'):
        cfhExtensions.show("Crew notification form already opened.")
    else:
        global crewNotification
        try:
            crewNotification = CrewNotification(menu)
        except NotificationError, ne:
            Errlog.log("CREW NOTIFICATION: %s" % ne)
            cfhExtensions.show(str(ne))
            Errlog.log("CREW NOTIFICATION: Error collecting crew")
            return
        Errlog.log("CREW NOTIFICATION: The crew notification form is started")
        StartTableEditor.StartTableEditor( ['-fs', form_name],
                'crew_notification')


#******************************************************************************
# Section 3:   Automatic notifications
# Section 3.1: Automatic Assignment Notifications
#******************************************************************************

class FlightDescriptor:
    """
    Class containing the information needed about a flight.
    """
    # 'fields' is used in rave-api calls, in order to retrieve Entry records
    # with the same members as a FlightDescriptor.
    fields = {
        'key': 'publish.%leg_cuidiff_key%',
        'arrivalTime': 'leg.%end_utc%',
        'arrivalTimeLocal': 'leg.%end_lt%',
        'arrivalStation': 'leg.%end_station%',
        'departureStation': 'leg.%start_station%',
        'departureTime': 'leg.%activity_scheduled_start_time_UTC%',
        'departureTimeLocal': 'leg.%start_lt%',
        'actCode': 'publish.%leg_act_code%',
        'pos': 'publish.%leg_cuidiff_pos%',
        'changeType': None,
        'table': None,
        'split': None,
        'changed_checkin': 'rescheduling.%leg_is_noninformed_ci_change_via_override%',
        'checkin_utc': 'rescheduling.%trip_checkin_utc%',
        'checkinTimeHomebase': 'rescheduling.%trip_checkin_hb%',
        'inf_checkin_utc': 'rescheduling.%trip_inf_checkin_utc%',
        'informedCheckinHomebase': 'rescheduling.%trip_inf_checkin%',
        'changed_checkout': 'rescheduling.%leg_is_noninformed_co_change_via_override%',
        'checkout_utc': 'rescheduling.%trip_scheduled_checkout_utc%',
        'checkoutTimeHomebase': 'rescheduling.%trip_scheduled_checkout_hb%',
        'inf_checkout_utc': 'rescheduling.%trip_inf_checkout_utc%',
        'informedCheckoutHomebase': 'rescheduling.%trip_inf_checkout%',
        'trip_uuid': 'trip_uuid',
        }
    
    def __init__(self, key,
                 arrivalTime=None,
                 arrivalTimeLocal=None,
                 arrivalStation=None,
                 departureTime=None,
                 departureTimeLocal=None,
                 departureStation=None,
                 actCode=None,
                 pos=None,
                 changeType=None,
                 table=None,
                 split=False):
        self.key = key
        self.arrivalTime = arrivalTime
        self.arrivalTimeLocal = arrivalTime
        self.arrivalStation = arrivalStation
        self.departureTime = departureTime
        self.departureTimeLocal = departureTimeLocal
        self.departureStation = departureStation
        self.actCode = actCode
        self.pos = pos
        self.changeType = changeType
        self.table = table
        self.split = split
    
    def __getattr__(self, name):
        """Default unresolved attribute references to None."""
        if not name or name[0] == '_':
            raise AttributeError
        else:
            self.__dict__[name] = None
            return None
        
    def __str__(self):
        return ('<FlightDescriptor key="%s" changeType="%s"'
                ' departureTime=%s departureTimeLocal=%s arrivalTime=%s'
                ' arrivalTimeLocal=%s departureStation="%s" arrivalStation="%s"'
                ' actCode="%s" pos="%s"'
                ' changed_checkin=%s changed_checkout=%s'
                ' trip_uuid="%s" trip_span=%s split=%s>') % (
                        self.key, self.changeType,
                        self.departureTime, self.departureTimeLocal, self.arrivalTime,
                        self.arrivalTimeLocal, self.departureStation, self.arrivalStation,
                        self.actCode, self.pos,
                        self.changed_checkin, self.changed_checkout,
                        self.trip_uuid, self.trip_span, self.split)
                    
    def isidenticalpact(self, other):
        """
        To compare two entries from CuiDiffPublishedRoster(), that have been
        day-split. If an added and a removed entry exist on the same day, then
        they can be ignored; the diff entry exists because there has been a
        change in length of a multi-day activity.
        (See Publish.py::get_change_descriptions().)
        """
        return (self.table == 'crew_activity'
                and str(self.actCode) == str(other.actCode)
                and str(self.departureStation) == str(other.departureStation)
                and AbsTime(self.departureTime) == AbsTime(other.departureTime)
                and AbsTime(self.arrivalTime) == AbsTime(other.arrivalTime))
                

def create_automatic_assignment_notifications(
        crew, home_airport,
        pub_st, pub_et,
        dnp_periods,
        roster_legs, changed_legs):
    """
    Creates notifications, comparing the original roster and the revised roster.
    """
    
    # LOCAL DECLARATIONS
    
    class NewNotif(object):
        """
        Manages crew_notification entries for one crew.
        """
        
        @classmethod
        def get_user(cls):
            try:
                return cls.user
            except:
                cls.user = Names.username()
                return cls.user
    
        @classmethod
        def get_typ(cls, is_preliminary):
            ix = bool(is_preliminary)
            try:
                return cls.typs[ix]
            except:
                try:    cls.typs
                except: cls.typs = {}
                subtype = ("Assignment", "PreliminaryAssignment")[ix]
                cls.typs[ix] = TM.notification_set[('Automatic', subtype)]
                return cls.typs[ix]
                
        @classmethod
        def get_system(cls, is_portal=True):
            ix = bool(is_portal)
            try:
                return cls.systems[is_portal]
            except:
                try:    cls.systems
                except: cls.systems = {}
                system = ("Hermes", "Portal")[ix]
                cls.systems[ix] = TM.notification_systems[(system, " ")]
                return cls.systems[ix]
                
        @classmethod
        def prepare_for_crew(cls, crew, home_airport, pstart, pend):
            """
            Get existing crew_notification entries.
            """
            #t = time.time()
            #print "--- NewNotif.prepare_for_crew() [%s @ %s]" % (crew, home_airport)
            cls.crew = TM.crew[(crew,)]
            cls.home = Airport(home_airport)
            cls.now, = r.eval("fundamental.%now%") 
            cls.new = [] # Notifications to exist after the save are instances
                         # of this class. '__init__()' adds all new instances to
                         # the cls.new list, for update_for_crew() to use when
                         # updating the crew_notification table.
            cls.old = [] # Here, we save references to existing notifications. 
            for cn in cls.crew.referers('crew_notification', 'crew'):
                if cn.typ.typ == 'Automatic' \
                and cn.typ.subtype in ('Assignment', 'PreliminaryAssignment') \
                and cn.delivered is None \
                and cn.st >= pstart and cn.st < pend:
                    cls.old.append(["nochange", cn])
            #print "--- NewNotif.prepare_for_crew() %.2fs" % (time.time() - t)
                    
        @classmethod
        def update_for_crew(cls):
            """
            Update the crew_notification table to reflect the current roster.
            Keep as much of existing entries as possible.
            """
            #print "--- NewNotif.update_for_crew()"
            #t = time.time()
    
            # Exceptions to the default alert time are stored in a separate table.
            # An exception is applied to changes starting on a specific hb day.
            exc = {}
            for e in cls.crew.referers("alert_time_exception", "crew"):
                if e.alerttime is not None:
                    st_date = int(cls.home.getLocalTime(e.startdate).day_floor())
                    exc[st_date] = e.alerttime
                    
            changes = {}
            for new in cls.new:
                if new.alerttime is None:
                    st_date = int(cls.home.getLocalTime(new.st).day_floor())
                    new.alerttime = exc.get(st_date, None)
                            
                for ix, (status, old) in enumerate(cls.old):
                    if old.deadline == new.deadline \
                    and old.failmsg == new.failmsg:
                        if old.typ == new.typ \
                        and str(old.alerttime) == str(new.alerttime) \
                        and str(old.st) == str(new.st) \
                        and str(old.firstmodst) == str(new.firstmodst) \
                        and str(old.lastmodet) == str(new.lastmodet):
                            # (use str() so None doesn't raise an exception)
                            #print "keep", old
                            cls.old[ix][0] = "keep"
                        else:
                            #print "update", old,
                            cls.old[ix][0] = "update"
                            old.typ = new.typ
                            if new.alerttime and new.alerttime <= new.deadline:
                                old.alerttime = new.alerttime
                            else:
                                old.alerttime = None
                            old.st = new.st
                            old.firstmodst = new.firstmodst
                            old.lastmodet = new.lastmodet
                            old.delivered_seip = None
                            #print "-->", old
                            changes["update"] = changes.get("update", 0) + 1
                            # update_rosterserver(cls.crew.empno, new.firstmodst, new.lastmodet)
                        break
                else:
                    n = TM.crew_notification.create((cls.crew, TM.createUUID()))
                    changes["create"] = changes.get("create", 0) + 1 
                    n.created = cls.now
                    n.created_by = cls.get_user()
                    n.system = new.system
                    n.typ = new.typ
                    n.deadline = new.deadline
                    if new.alerttime and new.alerttime <= new.deadline:
                        n.alerttime = new.alerttime
                    n.st = new.st
                    n.failmsg = new.failmsg
                    n.firstmodst = new.firstmodst
                    n.lastmodet = new.lastmodet
                    n.si = new.si
                    # update_rosterserver(cls.crew.empno, new.firstmodst, new.lastmodet)

                    #print "create", n
                    
            for status, old in cls.old:
                if status == "nochange":
                    #print "remove",old
                    old.remove()
                    changes["remove"] = changes.get("remove", 0) + 1 
                    
            if changes:
                Cui.CuiReloadTable("crew_notification", Cui.CUI_RELOAD_TABLES_SILENT)
            #print "--- NewNotif.update_for_crew%s %.2fs" % (changes, time.time()-t)
    
        def __init__(self, is_preliminary):
            self.typ = self.get_typ(is_preliminary)
            self.system = self.get_system()
            self.new.append(self)
            
        def __getattr__(self, name):
            """Default unresolved attribute references to None."""
            self.__dict__[name] = None
            return None
            
        def __str__(self):
            return "<NewNotif %s>" \
                   % (" ".join("%s=%s" % (k,v) for k,v in self.__dict__.items()))
                   

    def convert_multi_day_to_single_days(leg_list):
        expanded = []
        for leg in leg_list:
            if leg.arrivalTime - leg.departureTime <= RelTime(24, 0):
                leg.split = False
                expanded.append(leg)
            else:
                leg.split = True
                dt = leg.departureTime
                at = leg.arrivalTime
                while dt < at:
                    dleg = copy.copy(leg)
                    dleg.departureTime = dt
                    dleg.arrivalTime = AbsTime(min(dt + RelTime(24,0), at))
                    expanded.append(dleg)
                    dt = AbsTime(dleg.arrivalTime)
        return expanded
        
    def fmtmsg(activity=None, category=None, callout=None,
               checkin=None, checkout=None, detail=None):
        # Note about the date shown in the msg:
        #   Normally the date is UTC, but on request from SAS, if the time is
        #   not shown, the date will be in homebase time. For all SAS crew,
        #   including asian, this will be the UTC date + 1 day. 
        msg = showdep = showarr = showdate = showtime = None
        if callout is not None:
            global CALLOUT_INDICATOR_STRING
            try:
                msg = CALLOUT_INDICATOR_STRING
            except:
                # CALLOUT_INDICATOR_STRING is used in rave evaluation logic. To
                # avoid typing errors, use the string defined in the rave code.
                rv = RaveEvaluator(cis='rules_notifications_cct.%notification_failmsg_sbycall_indicator%')
                CALLOUT_INDICATOR_STRING = rv.cis
                msg = rv.cis
            showdate = str(callout)[:2]
            showtime = str(callout)[-5:]
        elif checkin is not None:
            msg = "CHECKIN"
            showdate = str(checkin)[:2]
            showtime = str(checkin)[-5:]
            showdep = (activity is not None)
        elif checkout is not None:
            msg = "CHECKOUT"
            showdate = str(checkout)[:2]
            showtime = str(checkout)[-5:]
            showarr = (activity is not None)
        elif category is not None:
            msg = category
            showdate = str(AbsDate(activity.departureTimeLocal))[:2]
        elif activity is not None:
            print "activity"*3," + ", msg, ", activity: ", activity
            msg = str(activity.actCode).replace("SK 000","").replace("SK 00","").strip()
            showdate = str(activity.departureTimeLocal)[:2]
            showtime = str(activity.departureTimeLocal)[-5:]
            showdep = True
            showarr = str(activity.arrivalStation) != str(activity.departureStation)
        if showdate:
            msg += "/%s" % showdate

        if showtime:
            msg += " %s" % showtime
        if showdep and showarr:
            msg += " %s-%s" % (activity.departureStation,activity.arrivalStation)
        elif showdep:
            msg += " %s" % activity.departureStation

        elif showarr:
            msg += " %s" % activity.arrivalStation

        if detail:
            msg = "%s %s" % ((msg or ""), detail)

        return msg
        
    def fmtpos(pos):
        pos = str(pos)
        return (pos == "DH" and "DEADHEAD") or ("(%s)" % pos)
        
    # FUNCTION BODY
        
    #print "=== create_automatic_assignment_notifications(crew=%s,home=%s)" \
    #      % (crew, home_airport), len(changed_legs)

    # This is to handle multi-day activities. We want changes on them to be
    # detected for the day on which the change took place, instead of the
    # start day of the activity.
    # - Split both roster and change legs into single-day activities.
    # - Remove changes for days when the roster and the change are identical.
    
    roster_legs = convert_multi_day_to_single_days(roster_legs)
    changed_legs = convert_multi_day_to_single_days(changed_legs)
    for rev in roster_legs:
        for ix, chg in enumerate(changed_legs):
            if  (rev.split or chg.split) \
            and (rev.actCode == chg.actCode) \
            and (rev.departureTime == chg.departureTime) \
            and (rev.arrivalTime == chg.arrivalTime):
                #print "DEL", changed_legs[ix]
                del changed_legs[ix]
                break
          
    # Setup NewNotif class so new instances are connected to a specific crew,
    # and prepare for roster-level rave evaluation.

    NewNotif.prepare_for_crew(crew, home_airport, pub_st, pub_et)    
    reval = RaveEvaluator(area=Cui.CuiScriptBuffer, mode=Cui.CrewMode, id=crew)
                           
    # Generate separate crew_notification entries for each notification block.
    
    changed_blocks = get_notification_blocks(crew, roster_legs, changed_legs)
        
    for block_period, activity_block in sorted(changed_blocks.items()):
        
        # The notification is built up from the most significant information
        # from the changes covered by the current notification block.
        
        new_notif = None
        do_not_publish = False
        for (rev_activity, org_activity) in activity_block:
            #print "### REV",rev_activity
            if rev_activity == org_activity: continue # Skip non-changes.
            #print "    ORG",org_activity
            
            # Get some key values for this activity.
            
            if rev_activity: # Added or modified leg
                st = rev_activity.departureTime
                et = rev_activity.arrivalTime
                deadline, sby_call, inf_cat = reval.rEval(
                    'rules_resched_cct.%%crew_notification_deadline_changed_roster_utc%%(%s)' % st,
                    'rules_resched_cct.%%crew_leg_standby_callout_time_utc%%(%s)' % st,
                    'rules_resched_cct.%%crew_informed_activity_maincat%%(%s)' % st,
                    )
            else: # (deleted leg)
                st = org_activity.departureTime
                et = org_activity.arrivalTime
                deadline, = reval.rEval(
                    'rules_resched_cct.%%crew_notification_deadline_removed_roster_utc%%(%s)' % st)
                sby_call = inf_cat = None
            #print "       ","deadline",deadline, "sby_call",sby_call, "inf_cat",inf_cat
            
            # Create a crew_notification entry for each separate notification.
            # Normally, there will only be one per notification block,
            # but in case a do-not-publish period starts or ends within the
            # block, the block is split into several notifications.
            
            dnp = any(p.start_utc <= st < p.end_utc for p in dnp_periods)       
            if new_notif is None \
            or dnp != do_not_publish:
                do_not_publish = dnp 
                msg_org = msg_rev = ""
                new_notif = NewNotif(do_not_publish)
            
            # Sort out the details for the current notification that the current
            # activity provides. The deadline for the notification shall be the
            # earliest that any change generates. The failmsg shall point out
            # the original and revised activity that are most significant for
            # the notification (normally the change that gave the deadline).
            
            if not rev_activity: # deleted leg
                if not msg_org:
                    msg_org = fmtmsg(activity=org_activity)
            else: # rev_activity is not None: Added or modified leg
                if not msg_rev:
                    if new_notif.deadline is not None \
                    and new_notif.deadline < deadline:
                        msg_deadline = new_notif.deadline
                    else:
                        msg_deadline = deadline
                    fmtargs = {}
                    details = []
                    if rev_activity.changed_checkin:
                        fmtargs['checkin'] = rev_activity.checkinTimeHomebase
                        add_briefing_for_leg(crew, rev_activity)
                    elif rev_activity.changed_checkout:
                        fmtargs['checkout'] = rev_activity.checkoutTimeHomebase
                    elif rev_activity.departureTime >= msg_deadline:
                        if not org_activity:
                            fmtargs['activity'] = rev_activity
                    if org_activity:
                        # We have a MODIFIED leg (both org and rev exist).
                        if str(org_activity.actCode) != str(rev_activity.actCode):
                            details.append(rev_activity.actCode)
                        if org_activity.pos and rev_activity.pos \
                        and str(org_activity.pos) != str(rev_activity.pos):
                            details.append(fmtpos(rev_activity.pos))
                        if org_activity.departureTime != rev_activity.departureTime:
                            details.append("dep %s" % str(rev_activity.departureTimeLocal)[-5:])
                        if str(org_activity.departureStation) != str(rev_activity.departureStation):
                            if str(rev_activity.arrivalStation) != str(rev_activity.departureStation):
                                details.append("dep@%s" % rev_activity.departureStation)
                            else:
                                details.append("@%s" % rev_activity.departureStation)
                        if org_activity.arrivalTime != rev_activity.arrivalTime \
                        and not sby_call:
                            details.append("arr %s" % str(rev_activity.arrivalTimeLocal)[-5:])
                        if str(org_activity.arrivalStation) != str(rev_activity.arrivalStation):
                            if str(rev_activity.arrivalStation) != str(rev_activity.departureStation):
                                details.append("arr@%s" % rev_activity.arrivalStation)
                            else:
                                details.append("")
                    if details:
                        details = ",".join(d for d in details if d)
                        fmtargs['detail'] = \
                            re.sub(r"(arr|dep)( [0-9:]+),\1", r"\1\2", details)

                    if fmtargs:
                        #print ", ".join(sorted("%s=%s" % i for i in fmtargs.items()))
                        msg_rev = fmtmsg(**fmtargs)
                        
                if not msg_org:
                    fmtargs = {}
                    details = []
                    if org_activity:
                        # We have a MODIFIED leg (both org and rev exist).
                        if str(org_activity.actCode) != str(rev_activity.actCode) \
                        or org_activity.departureTime != rev_activity.departureTime \
                        or str(org_activity.departureStation) != str(rev_activity.departureStation):
                            # Actcode+Deptime/station are part of the std text in AlertMonitor.
                            details.append("")
                        if org_activity.arrivalTime != rev_activity.arrivalTime \
                        and not sby_call:
                            details.append("arr %s" % str(org_activity.arrivalTimeLocal)[-5:])
                        if str(org_activity.arrivalStation) != str(rev_activity.arrivalStation):
                            if str(org_activity.arrivalStation) != str(org_activity.departureStation):
                                details.append("arr@%s" % org_activity.arrivalStation)
                            else:
                                details.append("")
                        if org_activity.pos and rev_activity.pos \
                        and str(org_activity.pos) != str(rev_activity.pos):
                            details.append(fmtpos(org_activity.pos))
                    if sby_call is not None:
                        fmtargs['callout'] = sby_call
                    elif rev_activity.changed_checkin:
                        fmtargs['checkin'] = rev_activity.informedCheckinHomebase
                    elif rev_activity.changed_checkout:
                        fmtargs['checkout'] = rev_activity.informedCheckoutHomebase
                    if inf_cat and not fmtargs:
                        fmtargs['category'] = inf_cat
                        fmtargs['activity'] = rev_activity
                    if details:
                        details = ",".join(d for d in details if d)
                        fmtargs['detail'] = \
                            re.sub(r"(arr|dep)( [0-9:]+),\1", r"\1\2", details)
                        
                    if fmtargs:
                        fmtargs.setdefault('activity', org_activity)
                        msg_org = fmtmsg(**fmtargs)
                   
            #print "= %s = %s, dl: %s, dnp: %s" % (
            #    ["updated","removed"][rev_activity is None],
            #    st, deadline, do_not_publish
            #    ),
               
            # Update the notication deadline if moved to earlier.
            
            if new_notif.deadline is None \
            or deadline < new_notif.deadline:
                new_notif.deadline = deadline
                new_notif.st = st
                #print " *USE*",
            #else:
                #print "      ",
                
            # Update notification change timespan
            # (<start of first change> .. <end of last change>)
            
            if new_notif.firstmodst is None \
            or st < new_notif.firstmodst:
                new_notif.firstmodst = st
            if new_notif.lastmodet is None \
            or et > new_notif.lastmodet:
                new_notif.lastmodet = et
            
            # The notification is built up by looping through its activities.
            # Each activity can potentially add info to the notification; for
            # example a "delete" leg followed by an "added" leg would result in
            # a failmsg built up by a 'msg_org' from the removed leg and a
            # 'msg_rev' from the added leg.
            # Therefore, the failmsg is updated for each leg in order to catch
            # up any new info as long as there are remaining legs.
            
            failmsg = "%s->%s" % ((msg_org or "(empty)").strip(),
                                  (msg_rev or "(removed)").strip())
            new_notif.failmsg = failmsg[:100]

            #print failmsg
                
    NewNotif.update_for_crew()
    #print "==="

def add_briefing_for_leg(crew, leg):
    """
    SKCMS-566 Updates the briefing time for a crew-flight-duty. This is used to calculate the start of the FDP.
    The FDP should be calculated from the time of the second notification + 1 hour, or the first delayed check-in-time, 
    whichever is earliest. The actual calculation is in rave, but the needed values are stored here.
    """
    try:
        legKeys = string.split(leg.key,'+')
        adep = TM.airport[legKeys[2]]
        legRef = TM.flight_leg[(AbsTime(legKeys[0]),legKeys[1],adep)]
        crewRef = TM.crew[crew]
        crewFlightDuty = TM.crew_flight_duty[(legRef,crewRef)]
        briefNotifNumType = TM.assignment_attr_set["BRIEF_NOTIF_NUM"]
    except:
        print "The OMA16 rules for delayed reporting will not apply due to data faults. Save will continue"
        return
    
    try:
        numberOfPreviousNotifications = TM.crew_flight_duty_attr.create((crewFlightDuty, briefNotifNumType))
        numberOfPreviousNotifications.value_int = 0
    except:
        numberOfPreviousNotifications = TM.crew_flight_duty_attr[crewFlightDuty, briefNotifNumType]

    
def get_notification_blocks(crew, roster_legs, changed_legs):
    """
    Divide the current and original roster into notification blocks.
    
    A notification block is a time-interval containing all flights which
    depart within 24h of the previous or next flight in the block. Also,
    all changes that are on the same roster trip are kept in the same block.
    
    Only blocks where there are any roster changes are returned.
    """
    
    #print "get_notification_blocks():",len(roster_legs),"roster_legs,", \
    #                                   len(changed_legs),"change_legs"
    
    changed_legs = sorted(changed_legs, key=lambda leg: leg.departureTime)
    roster_legs = sorted(roster_legs, key=lambda leg: leg.departureTime)

    #---------------------------------------------------------------------------
    # First, create a list of notification block timespans by merging and
    # analysing the legs in the current roster and roster changes lists.
    #---------------------------------------------------------------------------
    
    # Create an initial list of time spans from the changed legs.
    # A new time span begins when there is 24h or more between two changed legs.
    # Each timespan will correspond to a separate notification.
    
    timespans = []
    for leg in changed_legs:
        timespan = (leg.departureTime, leg.arrivalTime)
        for timespan in timespans:
            if timespan[0] <= leg.departureTime < timespan[1] + ONE_DAY:
                timespan[1] = max(timespan[1], leg.arrivalTime)
                break
        else:
            timespans.append([leg.departureTime,leg.arrivalTime])
    
    #print "TIMESPANS, CALCULATED FROM CHANGED LEGS"
    #for t in timespans: print " ",t[0],t[1]
    
    # Find trip start-end spans from non-pact roster legs.
    # Consider overlapping legs.
    # These spans will be used to merge change time spans in case there are
    # +24h layovers that otherwise would result in separate notifications.
    
    tripspans = []
    for leg in roster_legs:
        if leg.trip_uuid and leg.trip_uuid.strip():
            for tripspan in tripspans:
                if (tripspan[0] <= leg.departureTime <= tripspan[1]
                 or leg.trip_uuid in tripspan[2]):
                    tripspan[0] = min(tripspan[0], leg.departureTime)
                    tripspan[1] = max(tripspan[1], leg.arrivalTime)
                    tripspan[2].add(leg.trip_uuid)
                    break
            else:
                tripspans.append([leg.departureTime,leg.arrivalTime,
                                  set([leg.trip_uuid])])
    
    #print "TRIPSPANS, CALCULATED FROM ROSTER LEGS"
    #for t in tripspans: print " ",t[0],t[1],t[2]
    
    # Merge timespans that cover the same roster non-pact trips (tripspans).
    # Ignore non-changed tripspans (those that do not overlap any timespan).
    
    def overlap(ts1, ts2):
        return (ts1[0] <= ts2[0] < ts1[1]) or (ts2[0] <= ts1[0] < ts2[1])
    def merge(ts1, ts2):
        ts1[0] = min(ts1[0], ts2[0])
        ts1[1] = max(ts1[1], ts2[1])

    for timespan in timespans:
        for tripspan in tripspans:
            if overlap(timespan, tripspan):
                merge(timespan, tripspan)
                
    for ix,timespan in enumerate(timespans):
        while ix+1 < len(timespans) and overlap(timespan, timespans[ix+1]):
            merge(timespan, timespans[ix+1])
            del timespans[ix+1]
            
    del tripspans
    
    #print "TIMESPANS AFTER MERGE ACCORDING TO TRIPSPANS"
    #for t in timespans: print " ",t[0],t[1]

    #---------------------------------------------------------------------------
    # Then, create notification blocks for timespans in which changes exist.
    #
    # Each notification block will be identified with a timespan,
    # and it will contain a list of leg pairs [[revised, original], ...].
    #---------------------------------------------------------------------------
    
    timespans = [tuple(t) for t in timespans]
    notifications = {}
    
    # Create a notification entry for each timespan where there is a change.
    # Initialize it with an empty list.
    
    for timespan in timespans:
        for change in changed_legs:
            if change.departureTime >= timespan[0] \
            and change.departureTime <= timespan[1]:
                notifications[timespan] = []
    
    # From the revised roster leg list, append a [revised, revised] leg pair
    # for each leg that is within a notification timespan (ignore others).
    
    for timespan in sorted(notifications.keys()):
        #print "TIMESPAN",timespan[0],timespan[1]
        for element in roster_legs:
            if element.departureTime >= timespan[0] \
            and element.departureTime <= timespan[1]:
                #print "  (x2)",element
                notifications[timespan].append([element, element])

    # For each changed leg reported by CuiDiffPublishedRoster, find the
    # notification it belongs to and update the corresponding
    # [revised,original] pair in the list.
    #
    # The changed_legs legs contain an indicator on the type of change
    # (added, modified or removed) + values from the original roster (i.e. from
    # the revision (INFORMED) pointed out at the CuiDiffPublishedRoster call.
    #
    #  change-type ->  revised-leg     original-leg
    #  "added"     ->  <roster leg>    None
    #  "removed"   ->  None            <CuiDiff leg>
    #  "modified"  ->  <roster leg>    <CuiDiff leg>
    
    timespans_logged = False
    for diffleg in changed_legs:
        # Find the timespan the modification belongs to, 
        for timespan in notifications:
            if diffleg.departureTime >= timespan[0] \
            and diffleg.departureTime <= timespan[1]:
                notification = notifications[timespan]
                break
        else:
            print "*************************************************"
            print "*Program error* Notification not found for change"
            if not timespans_logged:
                print "Notification scopes:"
                for timespan in notifications:
                    print " ",timespan[0], "-", timespan[1]
                timespans_logged = True
            print "Ignored leg change:",diffleg
            print "*************************************************"
            continue
        
        #print "+",diffleg
        if diffleg.changeType == "removed":
            # A leg was removed, so it only exists in the change list.
            # We have to add a proper leg pair at the proper place in the list.
            for nix, (rev, org) in enumerate(notification):
                if org and org.departureTime > diffleg.departureTime:
                    #print " ",org.departureTime,">",diffleg.departureTime
                    notification.insert(nix, [None, diffleg])
                    break
            else:
                notification.append([None, diffleg])
        elif diffleg.changeType == "added":
            # A leg was added to the roster. Indicate this by setting
            # original to None in the proper pair in the list.
            for nix, (rev, org) in enumerate(notification):
                #print "--rev",rev
                if rev and rev.key == diffleg.key:
                    notification[nix][1] = None
                    #print ">>org None"
                    break
            else:
                print "*** CrewNotificationFunctions::get_notification_blocks()"
                print "*** ERROR: No matching notification timespan for:"
                print "***", diffleg
        elif diffleg.changeType == "modified":
            # A leg was modified. Set the original in the proper list pair.
            for nix, (rev, org) in enumerate(notification):
                #print "--rev",rev
                if rev and rev.key == diffleg.key:
                    notification[nix][1] = diffleg
                    #print ">>org",diffleg
                    break
            else:
                print "*** CrewNotificationFunctions::get_notification_blocks()"
                print "*** ERROR: No matching notification timespan for:"
                print "***", diffleg
           
    return notifications

    
#******************************************************************************
# Section 4: View notifications
#******************************************************************************

class ViewNotifications:
    def __init__(self, menu):
        self.fields = {
            'id': 'crew.%id%',
            'empno': 'crew.%employee_number%',
            'logname': 'crew.%login_name%',
        }
        self.crew_list = getOneCrew(self.fields)
        self.tt_view_form_info = self.ViewFormInfoTempTable(self.crew_list[0])
        self.tt_crew_notification = self.CrewNotificationTempTable(self.crew_list[0])

    class ViewFormInfoTempTable(TempTable):
        """This table contains the form information."""
        def __init__(self, crew):
            TempTable.__init__(self, "tmp_cn_view_form_info2",
                [M.UUIDColumn("form_id", "Form Id")],
                [
                    M.BoolColumn("crew_filter_enabled", "Crew Filter Enabled"),
                    M.BoolColumn("crew_filter_on", "Crew Filter On/Off"),
                    M.StringColumn("crew_filter", "Crew Filter"), 
                    M.TimeColumn("deadline_filter", "Deadline Filter"),
                    M.StringColumn("not_show", "Formatted notification", 10000),
                    M.StringColumn("cb_show", "created_by"),
                    M.StringColumn("si_show", "Formatted SI"),
                    M.StringColumn("crew_info", "Crew name and employee number"),
                ])
            self.removeAll()
            formId = TM.createUUID()
            record = self.create((formId,))
            record.deadline_filter, = r.eval("fundamental.%now%")
            record.crew_info = "%s %s" % (crew.empno, crew.logname)
        
    class CrewNotificationTempTable(TempTable):
        """This table contains all the notifications which shall be visible in
        the form."""
        def __init__(self, crew):
            TempTable.__init__(self, "tmp_cn_crew_notification",
                [
                    M.RefColumn("crew", "crew", "Crew Id"), 
                    M.UUIDColumn("idnr", "Id Nr"),
                ],
                [
                    M.StringColumn("crew_employee_number", "Crew Employee Number"),
                    M.TimeColumn("created", "Created"),
                    M.StringColumn("created_by", "Created by (username)"),
                    M.RefColumn("system", "notification_systems", "Receiver system"),
                    M.RefColumn("typ", "notification_set", "Type"),
                    M.TimeColumn("deadline", "Deadline"),
                    M.TimeColumn("delivered", "Delivered time"),
                    M.StringColumn("message", "Message"),
                    M.StringColumn("recipients", "Number of recipients for this message"),
                    M.StringColumn("si", "Si"),
                ])
            self.removeAll()
            # Copies notifications from the crew_notification to this table
            # The header field contains pointers to the messages for the crew. It
            # also contains metadata.
            crew_ref = TM.crew[(crew.id,)]
            for row in [r for r in crew_ref.referers('crew_notification', 'crew')
                    if r.typ is not None and r.typ.typ == 'Manual']:
                uuid = row.idnr
                viewRow = self.create((row.crew, uuid))
                viewRow.si = row.si
                viewRow.crew_employee_number = crew.empno
                viewRow.created = row.created
                viewRow.deadline = row.deadline
                viewRow.system = row.system
                viewRow.typ = row.typ
                viewRow.delivered = row.delivered
                viewRow.recipients = " "
                if row.typ.typ == 'Manual':
                    viewRow.message = self.get_message(uuid)
                    viewRow.created_by = row.created_by
                    if row.typ.typ == 'Manual':
                        # Rather expensive search, but we need to know if the
                        # message is intended for several recipients.
                        viewRow.recipients = str(len([x for x in TM.crew_notification.search(
                            '(idnr=%s)' % row.idnr)]))
                        if viewRow.recipients == "1":
                            # We are not printing out '1'
                            viewRow.recipients = " "
                else:
                    viewRow.message = row.failmsg
                    viewRow.created_by = " "
        
        def get_message(self, uuid):
            rows = []
            for row in TM.notification_message.search("(idnr=%s)" % uuid):
                rows.append((row.seq_no, row.free_text))
            rows.sort()
            return ' '.join([txt for (seqno, txt) in rows])


def remove(plan, idnr, crew):
    """XML-RPC method.  Remove all notifications with given idnr."""
    for rec in TM.crew_notification.search('(idnr=%s)' % idnr):
        rec.remove()
    for rec in viewNotifications.tt_crew_notification.search('(idnr=%s)' % idnr):
        rec.remove()
    for rec in TM.notification_message.search('(idnr=%s)' % idnr):
        rec.remove()
    Cui.CuiReloadTable('crew_notification', Cui.CUI_RELOAD_TABLE_SILENT)
    Cui.CuiReloadTable('notification_message', Cui.CUI_RELOAD_TABLE_SILENT)
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    Gui.GuiCallListener(Gui.ActionListener)


def setDelivered(plan, idnr, crew):
    """
    XML-RPC method.
    This function sets the delivered information in both the model and the
    temporary table used in the notifications form
    If the optional argument delivered is set to 0, the notification will be
    set to undelivered.
    """
    # Change the model and the temporary table (the temporary table in order to
    # see the change in the form)
    crewRef = TM.crew.getOrCreateRef((crew,))
    db_row = TM.crew_notification[(crewRef, idnr)]
    tmp_row = viewNotifications.tt_crew_notification[(crewRef, idnr)]
    if not tmp_row.delivered:
        db_row.delivered, = r.eval("fundamental.%now%")
        tmp_row.delivered = AbsTime(db_row.delivered)
    else:
        db_row.delivered = None
        tmp_row.delivered = None
    Cui.CuiReloadTable('crew_notification', Cui.CUI_RELOAD_TABLE_SILENT)
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    Gui.GuiCallListener(Gui.ActionListener)


def formatNotification(plan, idnr, crew):
    """
    XML-RPC method.
    Format the notification and write it to the form table.
    """
    if idnr == "NULL":
        return
    crewRef = TM.crew.getOrCreateRef((crew,))
    row = viewNotifications.tt_crew_notification[(crewRef, idnr)]
    for tmp_row in viewNotifications.tt_view_form_info:
        tmp_row.not_show = row.message
        tmp_row.cb_show = row.created_by
        tmp_row.si_show = row.si
        break

    
def startViewNotification(menu):
    """
    Called from Studio menu.
    Start Crew Notification Viewer.
    """
    TM("crew", "crew_notification", "crew_employment", "notification_message")
    form_name = '$CARMUSR/data/form/%s' % 'crew_notification_viewer.xml'
    state = StartTableEditor.getFormState(form_name)
    if state is not None and state != "error":
        cfhExtensions.show("Crew notification viewer already opened.")
    else:
        global viewNotifications
        try:
            viewNotifications = ViewNotifications(menu)
        except NotificationError, ne:
            Errlog.log("CREW NOTIFICATION VIEWER: %s" % ne)
            cfhExtensions.show(str(ne))
            Errlog.log("CREW NOTIFICATION VIEWER: Error collecting crew")
            return
        Errlog.log("CREW NOTIFICATION VIEWER: The view notification form is started")
        StartTableEditor.StartTableEditor(['-fs', form_name],
                'crew_notification_viewer')


#
# Register XML-RPC services.
#

class cn_save_notification(LocalService):
    func = saveNotifications


class cn_set_delivered(LocalService):
    func = setDelivered


class cn_format_notification(LocalService):
    func = formatNotification


class cn_remove(LocalService):
    func = remove

