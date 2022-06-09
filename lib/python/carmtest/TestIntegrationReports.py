
# [acosta:06/340@14:33] Extended to include crewlists
# [acosta:07/163@13:28] Rewritten completely

"""
Quick-and-dirty UI builder to run some of the integrations.
"""

# imports ================================================================{{{1
import os
import re
import sys

import Cfh
import Cui

from tempfile import mkstemp

from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from carmstd import cfhExtensions
from tm import TM
import utils.CfhFormClasses as F
import carmensystems.rave.api as R
from utils.mailtools import send_mail


# exports ================================================================{{{1
__all__ = ['run']


# globals ================================================================{{{1
mailAddress = None # Will be set in a form...
wantMail = True

# Used to keep references to TempFile objects so they will not get destroyed
# prematurely.
temp_files = []


# help classes ==========================================================={{{1

# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    """ For anticipated errors. """
    msg = ''
    def __init__(self, msg, *additional):
        self.msg = msg
        self.additional = additional

    def __str__(self):
        L = [str(self.msg)]
        L.extend([str(x) for x in self.additional])
        return ' : '.join(L)


# FaultMessage -----------------------------------------------------------{{{2
class FaultMessage(Cfh.Box):
    """ Present a dialog with message and other information. """
    def __init__(self, title, message, *additional):
        Cfh.Box.__init__(self, title)
        self.layout = ErrLayoutFile(title, message, *additional)
        c = 0
        self.banner = Cfh.Label(self, "LABEL%d" % (c))
        for x in additional:
            c += 1
            setattr(self, "label%d" % (c), Cfh.Label(self, 'LABEL%d' % (c)))
        self.ok = Cfh.Done(self, "B_OK")
        self.load(self.layout.writeFile())
        self.show(True)
        self.loop()


# LayoutFile -------------------------------------------------------------{{{2
class LayoutFile(list):
    """ Used to create the layout for Cfh. """
    def __init__(self, title):
        list.__init__(self)
        (fd, self.fileName) = mkstemp(suffix='.tmp', prefix='TestIntegrationReports_',
                dir=os.environ['CARMTMP'], text=True)
        self.file = os.fdopen(fd, 'w')
        self.prolog = [
            "FORM;ReportForm;%s" % (title),
            "GROUP"
        ]
        self.epilog = [
            "EMPTY",
            "BUTTON;B_OK;`OK`;`_OK`",
            "BUTTON;B_CANCEL;`Cancel`;`_Cancel`"
        ]

    def appendField(self, name, label):
        """ Add a new field to the layout file. """
        self.append('FIELD;%s;`%s`' % (name, label))

    def __str__(self):
        """ Return the layout file as a string. """
        return '\n'.join(self.prolog + self + self.epilog)

    def __del__(self):
        """ Remove temporary file when object is discarded. """
        os.unlink(self.fileName)

    def writeFile(self):
        """ Write the file to disk, close and return file name. """
        self.file.write(str(self))
        self.file.close()
        return self.fileName


# ErrLayoutFile ----------------------------------------------------------{{{2
class ErrLayoutFile(LayoutFile):
    """ Used by FaultMessage to create Cfh layout for dialog. """
    def __init__(self, title, errtext, *additional):
        LayoutFile.__init__(self, title)
        (fd, self.fileName) = mkstemp(suffix='.tmp', prefix='TestIntegrationReports_',
                dir=os.environ['CARMTMP'], text=True)
        self.file = os.fdopen(fd, 'w')
        self.prolog = ["FORM;ReportForm;%s" % (title)]
        self.epilog = ["BUTTON;B_OK;`OK`;`_OK`"]
        c = 0
        self.append('BANNER:LABEL%d;`%s`' % (c, errtext))
        for text in additional:
            c += 1
            self.append('LABEL:LABEL%d;`%s`' % (c, text))


# GenericForm ------------------------------------------------------------{{{2
class GenericForm(Cfh.Box):
    """ Base class for the different forms. """
    def __init__(self, title):
        Cfh.Box.__init__(self, title)
        self.layout = LayoutFile(title)
        self.ok = Cfh.Done(self, "B_OK")
        self.quit = Cfh.Cancel(self, "B_CANCEL")
        self.fieldNum = 0

    def addFieldRave(self, label, typeName, *args):
        """ Add a field, where the initial value has to be evalutated by Rave. """
        self.fieldNum += 1
        fieldName = "FIELD%d" % (self.fieldNum)
        self.layout.appendField(fieldName, label)
        return getattr(self, "_" + typeName)(fieldName, *args)

    def addField(self, label, typeName, *args):
        """ Add a field, with optional initial values and field length. """
        self.fieldNum += 1
        fieldName = "FIELD%d" % (self.fieldNum)
        self.layout.appendField(fieldName, label)
        return getattr(Cfh, typeName)(self, fieldName, *args)

    def loadForm(self):
        """ Load the form and show it. """
        self.load(self.layout.writeFile())
        self.show(True)

    def _String(self, fieldName, len, raveVar):
        return Cfh.String(self, fieldName, len, self._CuiGet('String', raveVar))

    def _Date(self, fieldName, raveVar):
        return Cfh.Date(self, fieldName, int(self._CuiGet('Abstime', raveVar)))

    def _DateTime(self, fieldName, raveVar):
        return Cfh.DateTime(self, fieldName, int(self._CuiGet('Abstime', raveVar)))

    def _Number(self, fieldName, raveVar):
        return Cfh.Number(self, fieldName, int(self._CuiGet('Int', raveVar)))

    def _Clock(self, fieldName, raveVar):
        return Cfh.Clock(self, fieldName, int(self._CuiGet('Abstime', raveVar)))

    def _Toggle(self, fieldName, value):
        return Cfh.Toggle(self, fieldName, value)

    def _CuiGet(self, type, raveVar):
        """ Return evaluated Rave value. """
        return getattr(Cui, 'CuiCrcEval' + type)(Cui.gpc_info, Cui.CuiWhichArea, 'object', raveVar)


# TempFile ---------------------------------------------------------------{{{2
class TempFile:
    def __init__(self, remove_when_destroyed=False):
        (fd, self.fn) = mkstemp(suffix='.html', prefix='TempFile_',
                dir=os.environ['CARMTMP'], text=True)
        self.file = os.fdopen(fd, 'w')
        self.remove_when_destroyed = remove_when_destroyed

    def __del__(self):
        #Will be removed after contents have been shown.
        if self.remove_when_destroyed and os.path.exists(self.fn):
            os.unlink(self.fn)

    def __str__(self):
        return self.fn

    def close(self):
        self.file.close()

    def write(self, *a, **k):
        self.file.write(*a, **k)


# CFH Forms =============================================================={{{1

# MailAddressForm --------------------------------------------------------{{{2
class MailAddressForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, 'Enter mail address')
        try:
            if mailAddress is None:
                ma = ""
            else:
                ma = mailAddress
            self.f_mailAddress = self.addField('Mail address', 'String', 50, ma)
            self.f_wantMail = self.addField('Send mail', 'Toggle', wantMail)
        except Exception, msg:
            raise UsageException('Operation failed', msg)
        self.loadForm()

    def getMailAddress(self):
        return self.f_mailAddress.valof()
    mailAddress = property(getMailAddress)

    def getWantMail(self):
        return self.f_wantMail.valof()
    wantMail = property(getWantMail)


# MCLForm ----------------------------------------------------------------{{{2
class MCLForm(GenericForm):
    """ For Master Crew List """
    def __init__(self, title):
        GenericForm.__init__(self, title)
        now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
        self.f_now = self.addField('Changes after this date', 'Date', int(now))
        self.f_incremental = self.addField('Incremental', 'Toggle', 1)
        self.loadForm()

    def getNow(self):
        return AbsTime(self.f_now.valof())
    start = property(getNow)

    def getIncremental(self):
        return bool(self.f_incremental.valof())
    incremental = property(getIncremental)


# CompDaysForm -----------------------------------------------------------{{{2
class CompDaysForm(GenericForm):
    def __init__(self, title="32.21 Compensation Days"):
        GenericForm.__init__(self, title)
        try:
            self.f_extperkey = self.addFieldRave('extperkey', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            self.f_year = self.addField('year (yyyy)', 'String', 10, "%04d" % (now.split()[0]))
            self.f_daytype = self.addField('dayType', 'String', 10, "VA")
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getExtperkey(self):
        return self.f_extperkey.valof()
    extperkey = property(getExtperkey)

    def getDaytype(self):
        return self.f_daytype.valof()
    daytype = property(getDaytype)

    def getYear(self):
        return self.f_year.valof()
    year = property(getYear)


# CrewBaggageForm --------------------------------------------------------{{{2
class CrewBaggageForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, '40.1 Crew Baggage Reconciliation')
        try:
            self.f_fd = self.addFieldRave('fd', 'String', 10, 'leg.%flight_id%')
            self.f_udor = self.addFieldRave('udor', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_adep = self.addFieldRave('adep', 'String', 10, 'leg.%start_station%')
        except Exception, msg:
            raise UsageException('No valid flight leg marked.', msg)
        self.loadForm()

    def getFd(self):
        return self.f_fd.valof()
    fd = property(getFd)

    def getUDOR(self):
        return "%04d%02d%02d" % AbsDate(self.f_udor.valof()).split()[:3]
    udor = property(getUDOR)

    def getADEP(self):
        return self.f_adep.valof()
    adep = property(getADEP)



# CrewSheetForm ----------------------------------------------------------{{{2
class CrewSheetForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, '41.1 Number of Crew to Load Sheet')
        try:
            self.f_flightId = self.addFieldRave('flightId', 'String', 10, 'leg.%flight_descriptor%')
            self.f_originDate = self.addFieldRave('originDate', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_adep = self.addFieldRave('adep', 'String', 3, 'leg.%start_station%')
        except Exception, msg:
            raise UsageException('No valid flight leg marked.', msg)
        self.loadForm()

    def getFlightId(self):
        return _flightId(self.f_flightId.valof())
    flightId = property(getFlightId)

    def getOriginDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_originDate.valof()).split()[:3]
    originDate = property(getOriginDate)

    def getAdep(self):
        return self.f_adep.valof()
    adep = property(getAdep)


# CrewSlipForm -----------------------------------------------------------{{{2
class CrewSlipForm(GenericForm):
    months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
        'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
    def __init__(self):
        GenericForm.__init__(self, '32.13.3 Crew Slip')
        try:
            self.f_extperkey = self.addFieldRave('extperkey', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            (y, m) = now.split()[:2]
            self.f_year = self.addField('year (yyyy)', 'String', 10, "%04d" % (y))
            #self.f_month = self.addField('month (mm)', 'String', 10, "%02d" % (m))
            self.f_monthabbr = self.addField('Month (MMM)', 'String', 10, self.months[now.split()[1] - 1])
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getExtperkey(self):
        return self.f_extperkey.valof()
    extperkey = property(getExtperkey)

    def getMonth(self):
        return self.f_month.valof()
    month = property(getMonth)

    def getMonthAbbr(self):
        m =  self.f_monthabbr.valof()
        if not m in self.months:
            raise UsageException('Invalid month.', 'The month should be one of {JAN, FEB, ..., DEC}.')
        return m
    monthabbr = property(getMonthAbbr)

    def getYear(self):
        return self.f_year.valof()
    year = property(getYear)


# CrewLandingForm --------------------------------------------------------{{{2
class CrewLandingForm(GenericForm):
    requestName = 'CrewLanding'
    def __init__(self):
        GenericForm.__init__(self, '46.3 Landings')
        try:
            self.f_requestName = self.addField('requestName', 'String', 20, self.requestName)
            self.f_requestName.setEditable(False)
            self.f_flightId = self.addFieldRave('flightId', 'String', 10, 'leg.%flight_id%')
            self.f_originDate = self.addFieldRave('originDate', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_depStation = self.addFieldRave('depStation', 'String', 10, 'leg.%start_station%')
            self.f_arrStation = self.addFieldRave('arrStation', 'String', 10, 'leg.%end_station%')
            self.f_empno = self.addFieldRave('empno', 'String', 10, 'crew.%employee_number%')
        except Exception, msg:
            raise UsageException('No valid flight leg marked.', msg)
        self.loadForm()

    def getFlightId(self):
        return _flightId(self.f_flightId.valof())
    flightId = property(getFlightId)

    def getOriginDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_originDate.valof()).split()[:3]
    originDate = property(getOriginDate)

    def getDepStation(self):
        return self.f_depStation.valof()
    depStation = property(getDepStation)

    def getArrStation(self):
        return self.f_arrStation.valof()
    arrStation = property(getArrStation)

    def getEmpno(self):
        return self.f_empno.valof()
    empno = property(getEmpno)


# CrewBasicForm ----------------------------------------------------------{{{2
class CrewBasicForm(GenericForm):
    requestName = 'CrewBasic'
    def __init__(self):
        GenericForm.__init__(self, 'Crew Basic Service')
        try:
            self.f_requestName = self.addField('requestName', 'String', 10, self.requestName)
            self.f_requestName.setEditable(0)
            self.f_empno = self.addFieldRave('empno', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            self.f_searchDate = self.addField('searchDate', 'Date', int(now))
            self.f_getCrewBasicInfo = self.addField('getCrewBasicInfo', 'Toggle', 0)
            self.f_getCrewContact = self.addField('getCrewContact', 'Toggle', 0)
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getEmpno(self):
        return self.f_empno.valof()
    empno = property(getEmpno)

    def getSearchDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_searchDate.valof()).split()[:3]
    searchDate = property(getSearchDate)

    def getGetCrewBasicInfo(self):
        return ("N", "Y")[self.f_getCrewBasicInfo.valof()]
    getCrewBasicInfo = property(getGetCrewBasicInfo)

    def getGetCrewContact(self):
        return ("N", "Y")[self.f_getCrewContact.valof()]
    getCrewContact = property(getGetCrewContact)


# CrewFlightForm ---------------------------------------------------------{{{2
class CrewFlightForm(GenericForm):
    requestName = 'CrewFlight'
    def __init__(self):
        GenericForm.__init__(self, self.requestName)
        try:
            self.f_requestName = self.addField('requestName', 'String', 10, self.requestName)
            self.f_requestName.setEditable(0)
            self.f_flightId = self.addFieldRave('flightId', 'String', 10, 'leg.%flight_id%')
            self.f_originDate = self.addFieldRave('originDate', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_depStation = self.addFieldRave('depStation', 'String', 10, 'leg.%start_station%')
            self.f_arrStation = self.addFieldRave('arrStation', 'String', 10, 'leg.%end_station%')
            self.f_getTimesAsLocal = self.addField('getTimesAsLocal', 'Toggle', 0)
        except Exception, msg:
            raise UsageException('No valid leg marked.', msg)
        self.loadForm()

    def getFlightId(self):
        return _flightId(self.f_flightId.valof())
    flightId = property(getFlightId)

    def getOriginDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_originDate.valof()).split()[:3]
    originDate = property(getOriginDate)

    def getDepStation(self):
        return self.f_depStation.valof()
    depStation = property(getDepStation)

    def getArrStation(self):
        return self.f_arrStation.valof()
    arrStation = property(getArrStation)

    def getGetTimesAsLocal(self):
        return ("N", "Y")[self.f_getTimesAsLocal.valof()]
    getTimesAsLocal = property(getGetTimesAsLocal)


# CrewListForm -----------------------------------------------------------{{{2
class CrewListForm(GenericForm):
    requestName = 'CrewList'
    def __init__(self):
        GenericForm.__init__(self, self.requestName)
        try: 
            self.f_requestName = self.addField('requestName', 'String', 10, self.requestName)
            self.f_requestName.setEditable(0)
            self.f_activityId = self.addFieldRave('activityId', 'String', 10, 'leg.%flight_id%')
            self.f_date = self.addFieldRave('date', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_requestDateAsOrigin = self.addField('requestDateAsOrigin', 'Toggle', 0)
            self.f_requestDateInLocal = self.addField('requestDateInLocal', 'Toggle', 0)
            self.f_depStation = self.addFieldRave('depStation', 'String', 10, 'leg.%start_station%')
            self.f_arrStation = self.addFieldRave('arrStation', 'String', 10, 'leg.%end_station%')
            self.f_std = self.addFieldRave('std', 'Clock', 'leg.%start_UTC%')
            self.f_mainRank = self.addField('mainRank', 'String', 10, "")
            self.f_getPublishedRoster = self.addField('getPublishedRoster', 'Toggle', 0)
            self.f_getTimesAsLocal = self.addField('getTimesAsLocal', 'Toggle', 0)
            self.f_getLastFlownDate = self.addField('getLastFlownDate', 'Toggle', 0)
            self.f_getNextFlightDuty = self.addField('getNextFlightDuty', 'Toggle', 0)
            self.f_getPrevNextDuty = self.addField('getPrevNextDuty', 'Toggle', 0)
            self.f_getPrevNextAct = self.addField('getPrevNextAct', 'Toggle', 0)
            self.f_getCrewFlightDocuments = self.addField('getCrewFlightDocuments', 'Toggle', 0)
            self.f_getPackedRoster = self.addField('getPackedRoster', 'Toggle', 0)
            self.f_getPackedRosterFromDate = self.addFieldRave('getPackedRosterFromDate', 'Date', 'fundamental.%pp_start%')
            self.f_getPackedRosterToDate = self.addFieldRave('getPackedRosterToDate', 'Date', 'fundamental.%pp_end%')
        except Exception, msg:
            raise UsageException('No valid activity marked.', msg)
        self.loadForm()

    def getActivityId(self):
        return _flightId(self.f_activityId.valof())
    activityId = property(getActivityId)

    def getDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_date.valof()).split()[:3]
    date = property(getDate)

    def getRequestDateAsOrigin(self):
        return ("N", "Y")[self.f_requestDateAsOrigin.valof()]
    requestDateAsOrigin = property(getRequestDateAsOrigin)

    def getRequestDateInLocal(self):
        return ("N", "Y")[self.f_requestDateInLocal.valof()]
    requestDateInLocal = property(getRequestDateInLocal)

    def getDepStation(self):
        return self.f_depStation.valof()
    depStation = property(getDepStation)

    def getArrStation(self):
        return self.f_arrStation.valof()
    arrStation = property(getArrStation)

    def getStd(self):
        return "%02d:%02d" % RelTime(self.f_std.valof()).split()[:2]
    std = property(getStd)

    def getMainRank(self):
        return self.f_mainRank.valof()
    mainRank = property(getMainRank)

    def getGetPublishedRoster(self):
        return ("N", "Y")[self.f_getPublishedRoster.valof()]
    getPublishedRoster = property(getGetPublishedRoster)

    def getGetTimesAsLocal(self):
        return ("N", "Y")[self.f_getTimesAsLocal.valof()]
    getTimesAsLocal = property(getGetTimesAsLocal)

    def getGetLastFlownDate(self):
        return ("N", "Y")[self.f_getLastFlownDate.valof()]
    getLastFlownDate = property(getGetLastFlownDate)

    def getGetNextFlightDuty(self):
        return ("N", "Y")[self.f_getNextFlightDuty.valof()]
    getNextFlightDuty = property(getGetNextFlightDuty)

    def getGetPrevNextDuty(self):
        return ("N", "Y")[self.f_getPrevNextDuty.valof()]
    getPrevNextDuty = property(getGetPrevNextDuty)

    def getGetPrevNextAct(self):
        return ("N", "Y")[self.f_getPrevNextAct.valof()]
    getPrevNextAct = property(getGetPrevNextAct)

    def getGetCrewFlightDocuments(self):
        return ("N", "Y")[self.f_getCrewFlightDocuments.valof()]
    getCrewFlightDocuments = property(getGetCrewFlightDocuments)

    def getGetPackedRoster(self):
        return ("N", "Y")[self.f_getPackedRoster.valof()]
    getPackedRoster = property(getGetPackedRoster)

    def getGetPackedRosterFromDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_getPackedRosterFromDate.valof()).split()[:3]
    getPackedRosterFromDate = property(getGetPackedRosterFromDate)

    def getGetPackedRosterToDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_getPackedRosterToDate.valof()).split()[:3]
    getPackedRosterToDate = property(getGetPackedRosterToDate)


# CrewManifestForm -------------------------------------------------------{{{2
class CrewManifestForm(GenericForm):
    def __init__(self, title):
        GenericForm.__init__(self, title)
        try:
            self.f_flightId = self.addFieldRave('flightId', 'String', 10, 'leg.%flight_name%')
            self.f_originDate = self.addFieldRave('originDate', 'Date', 'default(leg.%udor%, fundamental.%now%)')
            self.f_depStation = self.addFieldRave('depStation', 'String', 10, 'leg.%start_station%')
            self.startCountry = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%start_country%')
            self.endCountry = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'leg.%end_country%')
        except Exception, msg:
            raise UsageException('No valid leg marked.', msg)
        self.loadForm()

    def getFlightId(self):
        return _flightId(self.f_flightId.valof()).strip()
    fd = property(getFlightId)

    def getOriginDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_originDate.valof()).split()[:3]
    udor = property(getOriginDate)

    def getDepStation(self):
        return self.f_depStation.valof()
    adep = property(getDepStation)

    def getCountry(self):
        allowed_countries = R.set('leg.apis_countries').members()
        if self.startCountry in allowed_countries:
            return self.startCountry
        elif self.endCountry in allowed_countries:
            return self.endCountry
        else:
            raise UsageException('Neither start country (%s) nor end country (%s) in allowed countries %s.' % (self.startCountry, self.endCountry, allowed_countries))
    country = property(getCountry)


# CrewRosterForm ---------------------------------------------------------{{{2
class CrewRosterForm(GenericForm):
    requestName = 'CrewRoster'
    def __init__(self):
        GenericForm.__init__(self, self.requestName)
        try:
            self.f_requestName = self.addField('requestName', 'String', 10, self.requestName)
            self.f_requestName.setEditable(0)
            self.f_empno = self.addFieldRave('empno', 'String', 10, 'crew.%employee_number%')
            self.f_getPublishedRoster = self.addField('getPublishedRoster', 'Toggle', 0)
            self.f_getTimesAsLocal = self.addField('getTimesAsLocal', 'Toggle', 0)
            self.f_getCrewBasicInfo = self.addField('getCrewBasicInfo', 'Toggle', 0)
            self.f_getFlightLegSVC = self.addField('getFlightLegSVC', 'Toggle', 0)
            self.f_getSling = self.addField('getSling', 'Toggle', 0)
            self.f_startDate = self.addFieldRave('startDate', 'Date', 'fundamental.%pp_start%')
            self.f_endDate = self.addFieldRave('endDate', 'Date', 'fundamental.%pp_end%')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getEmpno(self):
        return self.f_empno.valof()
    empno = property(getEmpno)

    def getGetPublishedRoster(self):
        return ("N", "Y")[self.f_getPublishedRoster.valof()]
    getPublishedRoster = property(getGetPublishedRoster)

    def getGetTimesAsLocal(self):
        return ("N", "Y")[self.f_getTimesAsLocal.valof()]
    getTimesAsLocal = property(getGetTimesAsLocal)

    def getGetCrewBasicInfo(self):
        return ("N", "Y")[self.f_getCrewBasicInfo.valof()]
    getCrewBasicInfo = property(getGetCrewBasicInfo)

    def getGetFlightLegSVC(self):
        return ("N", "Y")[self.f_getFlightLegSVC.valof()]
    getFlightLegSVC = property(getGetFlightLegSVC)

    def getGetSling(self):
        return ("N", "Y")[self.f_getSling.valof()]
    getSling = property(getGetSling)

    def getStartDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_startDate.valof()).split()[:3]
    startDate = property(getStartDate)

    def getEndDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_endDate.valof()).split()[:3]
    endDate = property(getEndDate)


# DateIntervalForm -------------------------------------------------------{{{2
class DateIntervalForm(GenericForm):
    def __init__(self, title):
        GenericForm.__init__(self, title)
        self.now = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
            'NONE', "fundamental.%now%"))
        (y, m) = self.now.split()[:2]
        if m == 1:
            py = y - 1
            pm = 12
        else:
            py = y
            pm = m - 1
        self.f_startDate = self.addField('Start Date', 'Date', int(AbsDate(py, pm, 1)))
        self.f_endDate = self.addField('End Date', 'Date', int(AbsDate(y, m, 1)))
        self.loadForm()

    def getStartDate(self):
        return AbsTime(self.f_startDate.valof())
    startDate = property(getStartDate)

    def getEndDate(self):
        return AbsTime(self.f_endDate.valof())
    endDate = property(getEndDate)


# DutyCalculationForm ----------------------------------------------------{{{2
class DutyCalculationForm(GenericForm):
    requestName = 'DutyCalculation'
    def __init__(self, cr426=True):
        if cr426:
            title = 'Duty Calculation (CR 426)'
        else:
            title = '(obsolete) 32.14 Duty Calculation'
        GenericForm.__init__(self, title)
        try:
            self.f_requestName = self.addField('requestName', 'String', 20, self.requestName)
            self.f_requestName.setEditable(False)
            self.f_perKey = self.addFieldRave('perKey', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            (y, m, d) = now.split()[:3]
            if m == 1:
                py = y - 1
                pm = 12
            else:
                py = y
                pm = m - 1
            self.f_startDate = self.addField('startDate', 'Date', int(AbsDate(py, pm, 1)))
            self.f_endDate = self.addField('endDate', 'Date', int(AbsDate(y, m, 1)))
            if not cr426:
                self.f_showNI = self.addField('showNI', 'Toggle', 0)
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getPerKey(self):
        return self.f_perKey.valof()
    perKey = property(getPerKey)

    def getStartDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_startDate.valof()).split()[:3]
    startDate = property(getStartDate)

    def getEndDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_endDate.valof()).split()[:3]
    endDate = property(getEndDate)

    def getShowNI(self):
        try:
            return ("N", "Y")[self.f_showNI.valof()]
        except:
            return "N"
    showNI = property(getShowNI)


# DutyOvertimeForm -------------------------------------------------------{{{2
class DutyOvertimeForm(GenericForm):
    months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
        'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
    def __init__(self):
        GenericForm.__init__(self, '32.13 Duty Overtime')
        try:
            self.f_extperkey = self.addFieldRave('extperkey', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            self.f_monthabbr = self.addField('Month (MMM)', 'String', 10, self.months[now.split()[1] - 1])
            self.f_year = self.addField('Year (yyyy)', 'Number', now.split()[0])
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getExtperkey(self):
        return self.f_extperkey.valof()
    extperkey = property(getExtperkey)

    def getMonthAbbr(self):
        m =  self.f_monthabbr.valof()
        if not m in self.months:
            raise UsageException('Invalid month.', 'The month should be one of {JAN, FEB, ..., DEC}.')
        return m
    monthabbr = property(getMonthAbbr)
    #def getMonth(self):
    #    return int(self.f_month.valof())
        #m =  self.f_month.valof()
        #if not m in self.months:
        #    raise UsageException('Invalid month.', 'The month should be one of {JAN, FEB, ..., DEC}.')
        #return m
    #month = property(getMonth)

    def getYear(self):
        return int(self.f_year.valof())
    year = property(getYear)


# FutureActivitiesForm ---------------------------------------------------{{{2
class FutureActivitiesForm(GenericForm):
    requestName = 'FutureActivities'
    def __init__(self):
        GenericForm.__init__(self, '32.15 Future Activities')
        try:
            self.f_requestName = self.addField('requestName', 'String', 20, self.requestName)
            self.f_requestName.setEditable(False)
            self.f_empno = self.addFieldRave('empno', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            self.f_startDate = self.addField('startDate', 'Date', int(now))
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getEmpno(self):
        return self.f_empno.valof()
    empno = property(getEmpno)

    def getStartDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_startDate.valof()).split()[:3]
    startDate = property(getStartDate)


# ExtperkeyYearmonthForm -------------------------------------------------{{{2
class ExtperkeyYearmonthForm(GenericForm):
    """ Base class for PilotLogCrewForm and PilotLogSimForm. """
    months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
        'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
    def __init__(self, title):
        GenericForm.__init__(self, title)
        try:
            self.f_extperkey = self.addFieldRave('extperkey', 'String', 10, 'crew.%employee_number%')
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            #self.f_yearmonth = self.addField('yearmonth (yyyymm)', 'String', 10, "%04d%02d" % now.split()[:2])
            self.f_monthabbr = self.addField('Month (MMM)', 'String', 10, self.months[now.split()[1] - 1])
            self.f_year = self.addField('Year (yyyy)', 'Number', now.split()[0])
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getExtperkey(self):
        return self.f_extperkey.valof()
    extperkey = property(getExtperkey)

    def getMonthAbbr(self):
        m =  self.f_monthabbr.valof()
        if not m in self.months:
            raise UsageException('Invalid month.', 'The month should be one of {JAN, FEB, ..., DEC}.')
        return m
    monthabbr = property(getMonthAbbr)

    def getYear(self):
        return self.f_year.valof()
    year = property(getYear)


# List12Form -------------------------------------------------------------{{{2
class List12Form(GenericForm):
    companies = ('Company', 'SK', 'BU')
    bases = ('Base', 'CPH', 'OSL', 'STO', 'SVG', 'TRD', 'NRT', 'BJS', 'SHA')
    categories = ('Main Cat.', 'CA', 'FD')
    def __init__(self):
        GenericForm.__init__(self, "List 12")
        self.now = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
            'NONE', "fundamental.%now%"))
        (y, m) = self.now.split()[:2]
        if m == 1:
            py = y - 1
            pm = 12
        else:
            py = y
            pm = m - 1
        self.f_startDate = self.addField('Start Date', 'Date', int(AbsDate(py, pm, 1)))
        self.f_startDate.setMandatory(1)
        self.f_endDate = self.addField('End Date', 'Date', int(AbsDate(y, m, 1)))
        self.f_endDate.setMandatory(1)
        self.f_company = self.addField('Company', 'String', 8, "SK")
        self.f_company.setMenuString(';'.join(self.companies))
        self.f_company.setMenuOnly(1)
        self.f_company.setMandatory(1)
        self.f_base = self.addField('Base', 'String', 8, "CPH")
        self.f_base.setMenuString(';'.join(self.bases))
        self.f_base.setMenuOnly(1)
        self.f_base.setMandatory(1)
        self.f_category = self.addField('Category', 'String', 8, "CA")
        self.f_category.setMenuString(';'.join(self.categories))
        self.f_category.setMenuOnly(1)
        self.f_category.setMandatory(1)
        self.loadForm()

    def getStartDate(self):
        return AbsTime(self.f_startDate.valof())
    startDate = property(getStartDate)

    def getEndDate(self):
        return AbsTime(self.f_endDate.valof())
    endDate = property(getEndDate)

    def getBase(self):
        return self.f_base.valof()
    base = property(getBase)

    def getCompany(self):
        return self.f_company.valof()
    company = property(getCompany)

    def getCategory(self):
        return self.f_category.valof()
    category = property(getCategory)


# PilotLogCrewForm -------------------------------------------------------{{{2
class PilotLogCrewForm(ExtperkeyYearmonthForm):
    def __init__(self):
        ExtperkeyYearmonthForm.__init__(self, '32.3.2 Pilot Log Crew Activity')


# PilotLogFlightForm -----------------------------------------------------{{{2
class PilotLogFlightForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, '32.3.3 Pilot Log Get Flight Leg')
        try:
            self.f_flight = self.addFieldRave('flight', 'String', 10, 'leg.%flight_id%')
            self.f_date = self.addFieldRave('date', 'Date', 'default(leg.%udor%, fundamental.%now%)')
        except Exception, msg:
            raise UsageException('No valid flight marked.', msg)
        self.loadForm()

    def getFlight(self):
        return _flightId(self.f_flight.valof())
    flight = property(getFlight)

    def getDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_date.valof()).split()[:3]
    date = property(getDate)


# PilotLogSimForm --------------------------------------------------------{{{2
class PilotLogSimForm(ExtperkeyYearmonthForm):
    def __init__(self):
        ExtperkeyYearmonthForm.__init__(self, '32.3.7 Pilot Log Get Simulator Activity')


# ReplicationForm --------------------------------------------------------{{{2
class ReplicationForm(GenericForm):
    """ base class for X3 and TI2 """
    def __init__(self, title):
        GenericForm.__init__(self, title)
        now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
        self.f_now = self.addField('Activities after this date', 'Date', int(now))
        self.loadForm()

    def getNow(self):
        return AbsTime(self.f_now.valof())
    now = property(getNow)


# VacationForm -----------------------------------------------------------{{{2
class VacationForm(CompDaysForm):
    def __init__(self):
        CompDaysForm.__init__(self, '32.17 Vacation Balance and Postings')


# VacationListForm -------------------------------------------------------{{{2
class VacationListForm(GenericForm):
    """ Base class for Vacation STO and Vacation OSL. """
    def __init__(self, title):
        GenericForm.__init__(self, title)
        try:
            now = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "fundamental.%now%"))
            (y, m) = now.split()[:2]
            start= AbsDate(y, m, 1)
            if m == 12:
                end = AbsDate(y + 1, 1, 1)
            else:
                end = AbsDate(y, m + 1, 1)
            self.f_startdate = self.addField('startDate', 'Date', int(start))
            self.f_enddate = self.addField('endDate', 'Date', int(end))
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        self.loadForm()

    def getStartDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_startdate.valof()).split()[:3]
    startDate = property(getStartDate)

    def getEndDate(self):
        return "%04d%02d%02d" % AbsDate(self.f_enddate.valof()).split()[:3]
    endDate = property(getEndDate)


# VacationListFormSTO ----------------------------------------------------{{{2
class VacationListFormSTO(VacationListForm):
    def __init__(self):
        VacationListForm.__init__(self, '44.6.1 Vacation List STO')


# VacationListFormOSL ----------------------------------------------------{{{2
class VacationListFormOSL(VacationListForm):
    def __init__(self):
        VacationListForm.__init__(self, '44.6.2 Vacation List OSL')


# X3Form -----------------------------------------------------------------{{{2
class X3Form(ReplicationForm):
    def __init__(self):
        ReplicationForm.__init__(self, 'X.3 Replicate Vacation Data')



class CrewDataExportForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, 'CrewDataExport: Crew data to Interbids')
        self.f_reportFilename = self.addField('Report file: $CARMDATA/REPORTS/CREW_PORTAL', 'String', 30, 'crewdata.xml')
        self.f_debug = self.addField('Debug printout', 'Toggle', 0)
        self.loadForm()

    def getReportFilename(self):
        return self.f_reportFilename.valof()
    reportFilename = property(getReportFilename)

    def getReportType(self):
        return self.f_reportType.valof()
    reportType = property(getReportType)

    def getDebug(self):
        return self.f_debug.valof()
    debug = property(getDebug)

# MealForm ---------------------------------------------------------------{{{2
class MealForm(GenericForm):
    """ Base class for meal forms """
        
    regions = ('Regions', 'SKD', 'SKI', 'SKL', 'SKN', 'SKS',)
    def __init__(self, title):
        GenericForm.__init__(self, title)
        self.now = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
            'NONE', "fundamental.%now%"))
            
        self.f_station = self.addField('Station', 'String', 3, 'CPH')
        self.f_region = self.addField('Region', 'String', 8, "SKD")
        self.f_region.setMenuString(';'.join(self.regions))
        
    def getStation(self):
        return self.f_station.valof()
    station = property(getStation)
    
    def getRegion(self):
        return self.f_region.valof()
    region = property(getRegion)

class StandardMealForm(MealForm):
    """ Form used when testing ordinary meal order and forecasts """

    def __init__(self, title):
        MealForm.__init__(self, title)
        (y, m) = self.now.split()[:2]
        if m == 12:
            ny = y + 1
            nm = 1
        else:
            ny = y
            nm = m + 1
            
        self.f_startDate = self.addField('Start Date', 'Date', int(AbsDate(y, m, 1)))
        self.f_endDate = self.addField('End Date', 'Date', int(AbsDate(ny, nm, 1)))
        self.f_getIsForecast = self.addField('isForecast', 'Toggle', 0)
            
        self.loadForm()
        
    def getStartDate(self):
        return AbsTime(self.f_startDate.valof())
    startDate = property(getStartDate)

    def getEndDate(self):
        return AbsTime(self.f_endDate.valof())
    endDate = property(getEndDate)

    def getIsForecast(self):
        return self.f_getIsForecast.valof()
    isForecast = property(getIsForecast)


class UpdateMealForm(MealForm):
    """ Form used when testing meal update """

    def __init__(self, title):
        MealForm.__init__(self, title)
        self.f_updateTime = self.addField('Update Time', 'DateTime', int(self.now))
        self.f_nofRuns = self.addField('Nof of runs', 'Number', 1)
        self.f_nofRuns.setMandatory(1)
        self.loadForm()
        
    def getUpdateTime(self):
        return AbsTime(self.f_updateTime.valof())
    updateTime = property(getUpdateTime)

    def getNofRuns(self):
        return int(self.f_nofRuns.valof())
    nofRuns = property(getNofRuns)

class ProcessMealForm(GenericForm):
    """ Base class for meal forms """
        
    def __init__(self, title):
        GenericForm.__init__(self, title)
        self.f_orders = self.addField('Order numbers', 'String', 30, '')
        self.f_send = self.addField('Send', 'Toggle', 0)
        self.f_cancel = self.addField('Cancel', 'Toggle', 0)
        self.f_getIsForecast = self.addField('isForecast', 'Toggle', 0)
        self.loadForm()
        
    def getOrderNumbers(self):
        return self.f_orders.valof().split(',')
    orderNumbers = property(getOrderNumbers)

    def isForecast(self):
        return self.f_getIsForecast.valof()
    isForecast= property(isForecast)
        
    def getSend(self):
        return self.f_send.valof()
    send = property(getSend)

    def getCancel(self):
        return self.f_cancel.valof()
    cancel = property(getCancel)


# AfstemningsForm --------------------------------------------------------{{{2
class AfstemningsForm(GenericForm):
    def __init__(self):
        GenericForm.__init__(self, 'Afstemningsunderlag')
        self.f_runId = self.addField('Run Id', 'Number', 0)
        self.f_runId.setMandatory(1)
        self.loadForm()

    def getRunId(self):
        return int(self.f_runId.valof())
    runid = property(getRunId)


    
# setProfile=============================================================={{{1
PROFILE = False

def setProfile(prof=True):
    """ Enable or disable profiling for reports. """
    global PROFILE
    PROFILE = prof

# run ===================================================================={{{1
def run(report,prof=True):
    """ Run the report in a "safe" environment. """
    
    try:
        if prof and PROFILE:
            import profile
            m = sys.modules[__name__]
            profile.runctx("m.run(report,False)", globals(), locals())
        else:
            _run(report)
    except UsageException, e:
        f = FaultMessage('Operation Failed', e.msg, *e.additional)
        print e
    except Exception, msg:
        f = FaultMessage('Operation Failed', msg)
        raise


# _run -------------------------------------------------------------------{{{2
def _run(report):
    """ Present an optional form to user and launch the report. """

    fileName = None

    # baggage ------------------------------------------------------------{{{3
    if report == 'baggage':
        #import report_sources.hidden.rs_crewbaggage
        import crewlists.baggage
        f = CrewBaggageForm()
        if f.loop() == Cfh.CfhOk:
            try:
                fileName = TempFile()
                reportlist = crewlists.baggage.reports(**{
                    'fd': f.fd,
                    'udor': f.udor,
                    'adep': f.adep,
                })
                print >>fileName, '\n'.join(reportlist)
                fileName.close()
            except Exception, m:
                raise UsageException('Failed', str(m))
        else:
            return 

    # loadsheet ----------------------------------------------------------{{{3
    elif report == 'loadsheet':
        import crewlists.loadsheet
        f = CrewSheetForm()
        if f.loop() == Cfh.CfhOk:
            try:
                fileName = TempFile()
                print >>fileName, crewlists.loadsheet.report(**{
                    'flightId': f.flightId,
                    'originDate': f.originDate,
                    'adep': f.adep,
                })
                fileName.close()
            except Exception, m:
                raise UsageException('Failed', str(m))
        else:
            return 

    # landings -----------------------------------------------------------{{{3
    elif report == 'landings':
        import crewlists.crewlanding
        f = CrewLandingForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.crewlanding.report(**{
                'requestName': f.requestName,
                'flightId': f.flightId,
                'originDate': f.originDate,
                'depStation': f.depStation,
                'arrStation': f.arrStation,
                'empno': f.empno,
            })
            fileName.close()
        else:
            return 

    # crewbasic ----------------------------------------------------------{{{3
    elif report == 'crewbasic':
        import crewlists.crewbasic
        f = CrewBasicForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.crewbasic.report(**{
                'requestName': f.requestName,
                'empno': f.empno,
                'searchDate': f.searchDate,
                'getCrewBasicInfo': f.getCrewBasicInfo,
                'getCrewContact': f.getCrewContact
            })
            fileName.close()
        else:
            return 

    # crewflight ---------------------------------------------------------{{{3
    elif report == 'crewflight':
        import crewlists.crewflight
        f = CrewFlightForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.crewflight.report(**{
                'requestName': f.requestName,
                'flightId': f.flightId,
                'originDate': f.originDate,
                'depStation': f.depStation,
                'arrStation': f.arrStation,
                'getTimesAsLocal': f.getTimesAsLocal
            })
            fileName.close()
        else:
            return 

    # crewlist -----------------------------------------------------------{{{3
    elif report == 'crewlist':
        import crewlists.crewlist
        f = CrewListForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.crewlist.report(**{
                'requestName': f.requestName,
                'activityId': f.activityId,
                'date': f.date,
                'requestDateAsOrigin': f.requestDateAsOrigin,
                'requestDateInLocal': f.requestDateInLocal,
                'depStation': f.depStation,
                'arrStation': f.arrStation,
                'std': f.std,
                'mainRank': f.mainRank,
                'getPublishedRoster': f.getPublishedRoster,
                'getTimesAsLocal': f.getTimesAsLocal,
                'getLastFlownDate': f.getLastFlownDate,
                'getNextFlightDuty': f.getNextFlightDuty,
                'getPrevNextDuty': f.getPrevNextDuty,
                'getPrevNextAct': f.getPrevNextAct,
                'getCrewFlightDocuments': f.getCrewFlightDocuments,
                'getPackedRoster': f.getPackedRoster,
                'getPackedRosterFromDate': f.getPackedRosterFromDate,
                'getPackedRosterToDate': f.getPackedRosterToDate,
            })
            fileName.close()
        else:
            return 

    # crewroster ---------------------------------------------------------{{{3
    elif report == 'crewroster':
        import crewlists.crewroster
        f = CrewRosterForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.crewroster.report(**{
                'requestName': f.requestName,
                'empno': f.empno,
                'getPublishedRoster': f.getPublishedRoster,
                'getTimesAsLocal': f.getTimesAsLocal,
                'getCrewBasicInfo': f.getCrewBasicInfo,
                'getFlightLegSVC': f.getFlightLegSVC,
                'getSling': f.getSling,
                'startDate': f.startDate,
                'endDate': f.endDate,
            })
            fileName.close()
        else:
            return 

    # cio_xml ------------------------------------------------------------{{{3
    elif report == 'cio_xml':
        import cio.run
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number_at_date%(fundamental.%now%)')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        fileName = TempFile()
        print >>fileName, cio.run.report(empno=empno, status_change=True)
        fileName.close()

    # cio_xml_no ---------------------------------------------------------{{{3
    elif report == 'cio_xml_no':
        import cio.run
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number_at_date%(fundamental.%now%)')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        fileName = TempFile()
        print >>fileName, cio.run.report(empno=empno, status_change=False)
        fileName.close()

    # cio_raw_no ---------------------------------------------------------{{{3
    elif report == 'cio_raw_no':
        import cio.run
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number_at_date%(fundamental.%now%)')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        fileName = TempFile()
        print >>fileName, cio.run.report(empno=empno, status_change=False, raw=True)
        fileName.close()

    # cio_text_no --------------------------------------------------------{{{3
    elif report == 'cio_text_no':
        import cio.run
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number_at_date%(fundamental.%now%)')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        fileName = TempFile()
        print >>fileName, cio.run.report(empno=empno, status_change=False, decode=True)
        fileName.close()

    # dutycalculation (obsolete) -----------------------------------------{{{3
    elif report == 'dutycalculation':
        import crewlists.dutycalculation
        f = DutyCalculationForm(cr426=False)
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.dutycalculation.report(**{
                'requestName': f.requestName,
                'perKey': f.perKey,
                'startDate': f.startDate,
                'endDate': f.endDate,
                'showNI': f.showNI,
            })
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
        else:
            return 

    # dutycalculation (CR 426) -------------------------------------------{{{3
    elif report == 'dutycalc':
        import crewlists.getreport
        f = DutyCalculationForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'DUTYCALC', 3, f.perKey, f.startDate, f.endDate)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # futureactivities ---------------------------------------------------{{{3
    elif report == 'futureactivities':
        import crewlists.futureactivities
        f = FutureActivitiesForm()
        if f.loop() == Cfh.CfhOk:
            fileName = TempFile()
            print >>fileName, crewlists.futureactivities.report(**{
                'requestName': f.requestName,
                'empno': f.empno,
                'startDate': f.startDate,
            })
            fileName.close()
        else:
            return 

    # getreportlist ------------------------------------------------------{{{3
    elif report == 'getreportlist':
        import crewlists.getreportlist
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number%')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        fileName = TempFile()
        print >>fileName, crewlists.getreportlist.report('GetReportList', empno)
        fileName.close()

    # pilotlogcrew -------------------------------------------------------{{{3
    elif report == 'pilotlogcrew':
        import crewlists.getreport
        f = PilotLogCrewForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'PILOTLOGCREW', 3, f.extperkey, f.monthabbr, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # pilotlogflight -----------------------------------------------------{{{3
    elif report == 'pilotlogflight':
        import crewlists.getreport
        f = PilotLogFlightForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'PILOTLOGFLIGHT', 3, "DUMMY", f.flight, f.date)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # pilotlogsim --------------------------------------------------------{{{3
    elif report == 'pilotlogsim':
        import crewlists.getreport
        f = PilotLogSimForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'PILOTLOGSIM', 3, f.extperkey, f.monthabbr, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # pilotlogaccum ------------------------------------------------------{{{3
    elif report == 'pilotlogaccum':
        import crewlists.getreport
        try:
            empno = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%employee_number%')
        except Exception, msg:
            raise UsageException('No valid crew marked.', msg)
        rep = crewlists.getreport.report('GetReport', 'PILOTLOGACCUM', 1, empno)
        fileName = TempFile()
        print >>fileName, rep
        fileName.close()
        show_html_contents(rep)

    # dutyovertime -------------------------------------------------------{{{3
    elif report == 'dutyovertime':
        import crewlists.getreport
        f = DutyOvertimeForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'DUTYOVERTIME', 3, f.extperkey, f.monthabbr, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # crewslip -----------------------------------------------------------{{{3
    elif report == 'crewslip':
        import crewlists.getreport
        f = CrewSlipForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'CREWSLIP', 3, f.extperkey, f.monthabbr, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # vacation -----------------------------------------------------------{{{3
    elif report == 'vacation':
        import crewlists.getreport
        f = VacationForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'VACATION', 3, f.extperkey, f.daytype, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # compdays -----------------------------------------------------------{{{3
    elif report == 'compdays':
        import crewlists.getreport
        f = CompDaysForm()
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'COMPDAYS', 3, f.extperkey, f.daytype, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # boughtdays -----------------------------------------------------------{{{3
    elif report == 'boughtdays':
        import crewlists.getreport
        f = CompDaysForm(title="Bought Days Report")
        if f.loop() == Cfh.CfhOk:
            rep = crewlists.getreport.report('GetReport', 'BOUGHTDAYS', 3, f.extperkey, f.daytype, f.year)
            fileName = TempFile()
            print >>fileName, rep
            fileName.close()
            show_html_contents(rep)
        else:
            return 

    # crew_manifest ------------------------------------------------------{{{3
    elif report == 'crew_manifest':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = False
        f = CrewManifestForm('Crew Manifest')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            rlist = []
            sa = carmusr.paxlst.crew_manifest.SITAAddresses(f.country)
            for message in carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country=f.country):
                for recipient in sa.recipients:
                    rlist.append(sa.add_recipient(recipient, message))
            print >>tmpf.file, "\n\n===\n\n".join(rlist)
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # crew_manifest_us ---------------------------------------------------{{{3
    elif report == 'crew_manifest_us':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = CrewManifestForm('33.8 Crew Manifest US')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='US'))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # crew_manifest_cn ---------------------------------------------------{{{3
    elif report == 'crew_manifest_cn':
        f = CrewManifestForm('33.9 Crew Manifest CN')
        if f.loop() == Cfh.CfhOk:
            args = 'FD=%s UDOR=%s ADEP=%s' % (f.fd, f.udor, f.adep)
            report = 'CrewManifestCN.py'
            Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report, 0, args)
            import carmusr.paxlst.crew_manifest
            import utils.edifact
            utils.edifact.debug = True
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='CN'))
            tmpf.close()
            fileName = tmpf.fn

    # crew_manifest_th ---------------------------------------------------{{{3
    elif report == 'crew_manifest_th':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = CrewManifestForm('CR26 Crew Manifest TH')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='TH'))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # crew_manifest_jp ---------------------------------------------------{{{3
    elif report == 'crew_manifest_jp':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = CrewManifestForm('CR12 Crew Manifest JP')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='JP'))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # crew_manifest_uk ---------------------------------------------------{{{3
    elif report == 'crew_manifest_uk':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = CrewManifestForm('CR140 Crew Manifest UK')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='GB'))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # crew_manifest_in ---------------------------------------------------{{{3
    elif report == 'crew_manifest_in':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = CrewManifestForm('CR164 Crew Manifest IN')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.crewlist(fd=f.fd, udor=f.udor, adep=f.adep, country='IN'))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # mcl ----------------------------------------------------------------{{{3
    elif report == 'mcl':
        import carmusr.paxlst.crew_manifest
        import utils.edifact
        utils.edifact.debug = True
        f = MCLForm('33.7 Master Crew List')
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            if f.incremental:
                print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.mcl(f.start))
            else:
                print >>tmpf.file, "\n\n===\n\n".join(carmusr.paxlst.crew_manifest.complete_mcl(f.start))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    # vacliststo ---------------------------------------------------------{{{3
    elif report == 'vacliststo':
        import salary.vacation_lists
        f = VacationListFormSTO()
        if f.loop() == Cfh.CfhOk:
            fileName = salary.vacation_lists.vacation("SE", AbsDate(f.startDate), AbsDate(f.endDate))
        else:
            return 

    # vaclistosl ---------------------------------------------------------{{{3
    elif report == 'vaclistosl':
        import salary.vacation_lists
        f = VacationListFormOSL()
        if f.loop() == Cfh.CfhOk:
            fileName = salary.vacation_lists.vacation("NO", AbsDate(f.startDate), AbsDate(f.endDate))
        else:
            return 

    # x12 ----------------------------------------------------------------{{{3
    elif report == 'x12':
        import replication.X12
        tmpf = TempFile()
        print >>tmpf.file, replication.X12.report()
        tmpf.close()
        fileName = tmpf.fn

    # x3 -----------------------------------------------------------------{{{3
    elif report == 'x3':
        import replication.X3
        f = X3Form()
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, replication.X3.report(now=f.now)
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 

    elif report == 'CrewDataExport':
        
        import replication.CrewDataExport
        f = CrewDataExportForm()
        if f.loop() == Cfh.CfhOk:
            reportDir = os.path.join(os.environ['CARMDATA'], 'REPORTS', 'CREW_PORTAL')
            if not os.path.exists(reportDir):
                try:
                    os.makedirs(dir, 0775)
                except Exception, e:
                    raise Exception('Unable to create directory "%s". %s' % (reportDir, e))
            reportPath = os.path.join(reportDir, f.reportFilename)
            args = ['-c', TM.getConnStr(),
                    '-s', TM.getSchemaStr(),
                    '-o', reportPath]
            if f.debug:
                args.append('-v')
            replication.CrewDataExport.main(args)
        return 

    # overtime -----------------------------------------------------------{{{3
    elif report == 'overtime':
        import report_sources.include.OvertimeStatement
        report_sources.include.OvertimeStatement.runReport()
        return # Don't send mail

    # perdiem ------------------------------------------------------------{{{3
    elif report == 'perdiem':
        import report_sources.include.PerDiemStatementReport
        report_sources.include.PerDiemStatementReport.runReport()
        return # Don't send mail
    
    # perdiem_list ------------------------------------------------------------{{{3
    elif report == 'perdiem_lists':
        import report_sources.include.PerDiemYearlyList
        report_sources.include.PerDiemYearlyList.runReport()
        return # Don't send mail

    # list9 --------------------------------------------------------------{{{3
    elif report == 'list9':
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        f = DateIntervalForm('List 9 - Who Flew What')
        if f.loop() == Cfh.CfhOk:
            args = ' '.join((
                'starttime=%d' % int(f.now),
                'firstdate=%d' % int(f.startDate),
                'lastdate=%d' % int(f.endDate), 
                'CONTEXT=default_context',
            ))
            run_report(area, 'List9.py', args)
        return # Don't send mail

    # list12 -------------------------------------------------------------{{{3
    elif report == 'list12':
        import report_sources.include.List12
        report_sources.include.List12.runReport()
        return # Don't send mail

    # annotations --------------------------------------------------------{{{3
    elif report == 'annotations':
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        #Cui.CuiSetCurrentArea(Cui.gpc_info, area)
        #Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'OBJECT')
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, 'window',
                '../lib/python/report_sources/crew_window_general/AnnotationsInfo.py', 0)
        #raise UsageException('"Annotations info" not implemented yet.')
        return # Don't send mail
    
    # convertible crew----------------------------------------------------{{{3
    elif report == 'convertible_crew':
        import report_sources.hidden.ConvertibleCrew
        report_sources.hidden.ConvertibleCrew.runReport()
        return # Don't send mail
    
    # crew portal----------------------------------------------------{{{3
    elif report == 'crewportal':
        reload(sys.modules[__name__]).test_crew_portal()
        return # Don't send mail

    # salary -------------------------------------------------------------{{{3
    elif report == 'salary':
        import StartTableEditor
        StartTableEditor.StartTableEditor(["-f", "%s/data/form/salary.xml" % os.environ['CARMUSR']])
        return # Don't send mail

    # employee central salary ---------------------------------------------{{{3
    elif report == 'ec_salary':
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        f = DateIntervalForm('Set month to run')
        if f.loop() == Cfh.CfhOk:
            args = ' '.join((
                'report_start_date=%s' % f.startDate,
                'report_end_date=%s' % f.endDate
            ))
        report_start_date = str(f.startDate).split()[0]
        report_end_date = str(f.endDate).split()[0]
        import salary.ec.ECSalaryReport as SEC
        reload(SEC)
        ecrun = SEC.ECReport(report_start_date=report_start_date, report_end_date=report_end_date, release=False, test=True, studio=True)
        csv_files = ecrun.generate()
        try:
            import Csl
            for csv in csv_files:
                Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (os.path.basename(csv), csv))
        except Exception as e:
            print "Cannot show csv files: " + str(e)
            cfhExtensions.show("Cannot show csv files", title="Error")
        return

    # time entry salary ---------------------------------------------{{{3
    elif report == 'te_wfs':
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        f = DateIntervalForm('Set month to run')
        if f.loop() == Cfh.CfhOk:
            args = ' '.join((
                'report_start_date=%s' % f.startDate,
                'report_end_date=%s' % f.endDate
            ))
        report_start_date = str(f.startDate).split()[0]
        report_end_date = str(f.endDate).split()[0]
        import salary.wfs.wfs_time_entry_report as TER
        te_run = TER.TimeEntry(report_start_date=report_start_date, report_end_date=report_end_date, release=False, test=False, studio=True)
        csv_files = te_run.generate([])
        try:
            import Csl
            for csv in csv_files:
                Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (os.path.basename(csv), csv))
        except Exception as e:
            print "Cannot show csv files: " + str(e)
            cfhExtensions.show("Cannot show csv files", title="Error")
        return

    # meal ---------------------------------------------------------------{{{3
    elif report == 'meal':
        import meal.MealOrderRun
        f = StandardMealForm('MealOrder/Forecast')
        if f.loop() == Cfh.CfhOk:
            result_list = meal.MealOrderRun.mealOrderRun(fromDate=AbsDate(f.startDate),
                                                         toDate=AbsDate(f.endDate),
                                                         forecast=f.isForecast,
                                                         loadAirport=f.station,
                                                         region=f.region,
                                                         send = True,
                                                         reportServer=False)

            # Write the output to a tempfile and send its content. This will not inlude
            # the attachments
            tmpf = TempFile()
            for result in result_list:
                tmpf.write("--- Item ---\n")
                for k, v in result.iteritems():
                    tmpf.write("%s : %s\n" % (k, v))
            tmpf.close()
            fileName = tmpf.fn
                    
    elif report == 'meal_update':
        import meal.MealOrderRun
        f = UpdateMealForm('UpdateMealOrder')
        if f.loop() == Cfh.CfhOk:

            result_list = []
            updateTime = f.updateTime
            for ix in range(f.nofRuns):
                
                tmp_list = meal.MealOrderRun.mealOrderUpdate(reportServer=False,
                                                             send = True,
                                                             updateTime = updateTime, 
                                                             loadAirport=f.station,
                                                             region=f.region)
                updateTime = updateTime + RelTime("0:10") 
                result_list.extend(tmp_list)
    
            # Write the output to a tempfile and send its content. This will not inlude
            # the attachments
            tmpf = TempFile()
            for result in result_list:
                tmpf.write("--- Item ---")
                for k, v in result.iteritems():
                    tmpf.write("%s : %s\n" % (k, v))
            tmpf.close()
            fileName = tmpf.fn
        
    elif report == 'meal_process':
        import meal.MealOrderRun
        f = ProcessMealForm('Process Orders')
        if f.loop() == Cfh.CfhOk:
            result_list = meal.MealOrderRun.processMealOrderList(mealOrderList = f.orderNumbers,
                                                                 send = f.send,
                                                                 cancel = f.cancel,
                                                                 forecast = f.isForecast) 
    
            # Write the output to a tempfile and send its content. This will not inlude
            # the attachments
            tmpf = TempFile()
            for result in result_list:
                tmpf.write("--- Item ---")
                for k, v in result.iteritems():
                    tmpf.write("%s : %s\n" % (k, v))
            tmpf.close()
            fileName = tmpf.fn

    # Passive bookings
    elif report == 'passive':
        import passive.passive_bookings
        reload(passive.passive_bookings).showTestReport()
            
        return # Don't send mail

    # afstemningsunderlag ------------------------------------------------{{{3
    elif report == 'afstemningsunderlag':
        import salary.run
        TM('salary_run_id', 'salary_basic_data')
        f = AfstemningsForm()
        if f.loop() == Cfh.CfhOk:
            tmpf = TempFile()
            print >>tmpf.file, salary.run.report(salary.run.RunData.fromRunId(f.runid))
            tmpf.close()
            fileName = tmpf.fn
        else:
            return 
    # accountbalances ----------------------------------------------------{{{3
    elif report == 'accountbalances':
        import report_sources.hidden.AccountBalances
        report_sources.hidden.AccountBalances.run_form()
        return # Don't send email

    # <...> --------------------------------------------------------------{{{3
    else:
        return # Don't send mail

    global mailAddress
    global wantMail
        
    if fileName is not None and os.path.exists(str(fileName)):
        if mailAddress is None:
            f = MailAddressForm()
            if f.loop() == Cfh.CfhOk:
                mailAddress = f.mailAddress
                wantMail = f.wantMail
        if wantMail and mailAddress:
            send_mail(str(fileName), mailAddress, subject=report)
            #os.system("cat %s | mail -s %s %s" % (fileName, report, mailAddress))
        cfhExtensions.showFile(str(fileName), report)
        os.unlink(str(fileName))
    else:
        print "The file %s does not exists" % (str(fileName))


# _flightId --------------------------------------------------------------{{{2
def _flightId(activity):
    """ The CFH form strips ending space, so the string has to be
    reconstructed. """
    activity_re = re.compile(r'^([A-Za-z]{0,3})[ ]*(\d{3,6})([A-Za-z]?)')
    activity_match = activity_re.search(activity)
    if activity_match:
        carrier = activity_match.group(1)
        number = activity_match.group(2)
        suffix = activity_match.group(3)
        return "%-3s%04d%1s" % (carrier, int(number), suffix)
    else:
        return activity
    
# set_time ==============================================================={{{1
def set_time():
    #this is used in the integration test menu for changing now time
    import Variable
    import carmensystems.rave.api as R
    time_var = Variable.Variable(0)
    key_var = Variable.Variable("", 30)
    try:
        Cui.CuiSelectTimeAndResource(Cui.gpc_info, time_var, key_var, 30)
    except:
        return 1
    atime = AbsTime(time_var.value)
    R.param('fundamental.%now_debug%').setvalue(atime)
    R.param('fundamental.%use_now_debug%').setvalue(True)
    Cui.CuiReloadTables()


# misc functions ========================================================={{{1

# run_report -------------------------------------------------------------{{{2
def run_report(area, rpt, args):
    """Run PRT Report with data found in 'area', setting 'default_context'."""
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, 'window',
            '../lib/python/report_sources/include/%s' % rpt, 0, args)


# dumpovertimecalc -------------------------------------------------------{{{2
def dumpovertimecalc(askDates=False):
    import salary.Overtime
    salary.Overtime.dumpovertimecalc(askDates)

# dumpovertimecalc for EC -------------------------------------------------------{{{2
def ecdumpovertimecalc(askDates=False):
    import salary.ec.ECOvertime
    salary.ec.ECOvertime.dumpovertimecalc(askDates)

# salaryfiletest ---------------------------------------------------------{{{2
def salaryfiletest():    
    class SalaryForm(GenericForm):
        def __init__(self):
            currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            std = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "round_down_month(fundamental.%pp_start%)"))
            edd = AbsDate(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, 'NONE', "round_up_month(fundamental.%pp_end%)"))
            try:
                cc  = Cui.CuiCrcEvalString(Cui.gpc_info, currentArea, 'object', "crew.%employment_country%") or "DK"
            except:
                cc = "DK"
            GenericForm.__init__(self, 'Salary export test')
            try:
                self.f_extsys = self.addField('Ext sys:', 'String', 2, cc)
                self.f_extsys.setMenuString("Ext sys;DK;NO;SE;S3")
                self.f_extsys.setMenuOnly(1)
                self.f_extsys.setMandatory(1)
                self.f_runtype = self.addField('Run type:', 'String', 12, "OVERTIME")
                self.f_runtype.setMenuString("Run type;OVERTIME;PERDIEM;PERDIEMTAX;TEMP_CREW;COMPDAYS;SUPERVIS;AMBI;VACATION_Y;ALLOWNCE_M;ALLOWNCE_D;ABSENCE;BUDGETED;SCHEDULE;TCSCHEDULE")
                self.f_runtype.setMenuOnly(1)
                self.f_runtype.setMandatory(1)
                self.f_format = self.addField('Format:', 'String', 4, "FLAT")
                self.f_format.setMenuString("Format;CSV;FLAT;HTML")
                self.f_format.setMenuOnly(1)
                self.f_format.setMandatory(1)
                self.f_sdate = self.addField('Start date', 'Date', int(std))
                self.f_edate = self.addField('End date', 'Date', int(edd))
                self.f_runid = self.addField('Run id', 'String', 5, '-1')
                self.f_action = self.addField('Action:', 'String', 6, "Normal")
                self.f_action.setMenuString("Action;Normal;Export;Cancel;Retro")
                self.f_action.setMenuOnly(1)
                self.f_action.setMandatory(1)
            except Exception, msg:
                raise UsageException('Eek.', msg)
            self.loadForm()
    
        def getExtSys(self):
            return self.f_extsys.valof()
        def getRunType(self):
            return self.f_runtype.valof()
        def getFormat(self):
            return self.f_format.valof()
        def getStartDate(self):
            return self.f_sdate.valof()
        def getEndDate(self):
            return self.f_edate.valof()
        def getRunId(self):
            return self.f_runid.valof()
        def getAction(self):
            return self.f_action.valof()
    f = SalaryForm()
    if f.loop() != Cfh.CfhOk:
        return

    action = f.getAction()
    import salary.run as run
    if action == "Normal":
        extSys = f.getExtSys()
        runType = f.getRunType()
        sd = f.getStartDate()
        x = run.job(run.RunData(fromStudio=True, extsys=extSys, runtype=runType, exportformat=f.getFormat(), firstdate=f.getStartDate(), lastdate=f.getEndDate()), export_run=True)
        print x
        filename = x
        cfhExtensions.showFile(filename, "Salary file: %s %s %s " % (extSys, runType, sd))
    elif action == "Export":
        runid = int(f.getRunId())
        rd = run.RunData.fromRunId(runid)
        rd.exportformat = f.getFormat()
        filename = run.export(rd)
        cfhExtensions.showFile(filename, "Export file: %s" % (runid))
    elif action == "Retro":
        runid = int(f.getRunId())
        rd = run.RunData.fromRunId(runid)
        new_runid = run.retro_run(rd)
        rd = run.RunData.fromRunId(new_runid)
        rd.exportformat = f.getFormat()
        filename = run.export(rd)
        cfhExtensions.showFile(filename, "Retro file: %s %s" % (runid, new_runid))
    elif action == "Cancel":
        runid = int(f.getRunId())
        rd = run.RunData.fromRunId(runid)
        new_runid = run.create_and_negate(rd)
        rd = run.RunData.fromRunId(new_runid)
        rd.exportformat = f.getFormat()
        filename = run.export(rd)
        cfhExtensions.showFile(filename, "Cancellation file: %s %s" % (runid, new_runid))
    else:
        raise

# duty_level_test --------------------------------------------------------{{{2
def duty_level_test():
    import carmstd.area
    import carmensystems.rave.api as R
    
    class VarForm(GenericForm):
        def __init__(self):
            GenericForm.__init__(self, 'Duty level change test')
            try:
                self.f_varName = self.addField('Variable name:', 'String', 50, "overtime.%overtime%")
                self.f_markInWindow = self.addField('Mark existing', 'Toggle', True)
                self.f_markInWindow = self.addField('Mark existing', 'Toggle', True)
            except Exception, msg:
                raise UsageException('Eek.', msg)
            self.loadForm()
    
        def getVarName(self):
            return self.f_varName.valof()
        def getMark(self):
            return self.f_markInWindow.valof()
    
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    
    f = VarForm()
    if f.loop() != Cfh.CfhOk:
        return
    varName = f.getVarName()
    doMark = f.getMark()
    if doMark:
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        ctx = 'default_context'
        iter = 'iterators.leg_set'
        ident = 'leg_identifier'
    else:
        ctx = 'sp_crew'
        iter = 'iterators.roster_set'
        ident = 'crew.%id%'
    connt = R.param('levels.%min_duty_connection_time_p%').value()
    R.param('levels.%min_duty_connection_time_p%').setvalue(RelTime("5:00"))
    sd, = R.eval('round_down_month(fundamental.%now%)')
    ed, = R.eval('round_up_month(fundamental.%now%)')
    R.param('salary.%salary_month_start_p%').setvalue(sd)
    R.param('salary.%salary_month_end_p%').setvalue(ed)
    print "Salary month: %s - %s" % (R.param('salary.%salary_month_start_p%').value(), R.param('salary.%salary_month_end_p%').value())
    print "Duty level = %s" % str(connt)
    vals, = R.eval(ctx, R.foreach(R.iter(iter, where=('not void(%s)' % varName)), ident, varName))
    newl = {}
    oldl = {}
    diffl = []
    for _,id,val in vals:
        newl[id] = val
        oldl[id] = None
    carmstd.area.promptPush("%d with non-void, new dutylevel" % len(newl))
    R.param('levels.%min_duty_connection_time_p%').setvalue(RelTime("8:00"))
    print "Duty level = 8:00"
    vals, = R.eval(ctx, R.foreach(R.iter(iter, where=('not void(%s)' % varName)), ident, varName))
    R.param('levels.%min_duty_connection_time_p%').setvalue(connt)
    for _,id,val in vals:
        oldl[id] = val
        if not id in newl:
            newl[id] = None
    carmstd.area.promptPush("%d with non-void, old dutylevel" % len(newl))
    for crew in newl.keys():
        if oldl[crew] != newl[crew]:
            diffl.append(crew)
    if doMark:
        for leg in diffl:
            try:
                Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(leg))
                Cui.CuiMarkLegs(Cui.gpc_info, area, 'object', Cui.CUI_MARK_SET)
            except:
                print "Could not mark leg with leg id = %s" % leg
        carmstd.area.promptPush("%d legs differ in %s" % (len(diffl), varName))
    else:
        if Cui.CuiDisplayGivenObjects({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, diffl) != 0:
            carmstd.area.promptPush("    No result found.")


# repair_crew_publish_info -----------------------------------------------{{{2
def repair_crew_publish_info():
    """ Allows post planner to manually repair crew_publish_info that is broken
        due to missing migrated rescheduling information. """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    legs = Cui.CuiGetLegs(Cui.gpc_info, area, "marked")
    if len(legs) == 1:
        print "repair_crew_publish_info: Legs:", legs
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(legs[0]))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
        id, sd,ed,flt,tcd, shortstop, lor, temp, illness = R.eval(R.selected("levels.leg"), "crew.%id%", "leg.%start_hb%", "leg.%end_hb%", "leg.%flight_nr%", "task.%code%", "rest.%is_short%", "rescheduling.%is_late_informed_short_stop%", "crew.%is_temporary%", "leg.%is_illness%")
        for row in TM.crew_publish_info.search("(&(crew=%s)(end_date>%s)(start_date<=%s))" % (id, str(sd), str(sd))):
            lor = ":cs2:" in row.flags or ":cs1:" in row.flags
            pcl = ":pcl:" in row.flags
            shortstop = ":ss2:" in row.flags or ":ss1:" in row.flags
            if tcd != "FLT": flt = tcd + " (non-flight)"
            class SelectionDlg(F.BasicCfhForm):
                def __init__(self):
                    F.BasicCfhForm.__init__(self, "Repair")
                    self.add_label(0,0, "lbl1", "Flight: %s" % flt)
                    self.add_label(1,0, "lbl2", "%s-%s" % (str(sd), str(ed)))
                    if shortstop:
                        self.add_label(2,0, "lbl3", "This is a short stop duty")
                    else:
                        self.add_label(2,0, "lbl3", "This is NOT a short stop duty")
                    self.add_toggle_combo(4,0, "LateInf", "Short stop late inf.", lor)
                    self.add_toggle_combo(6,0, "Pcl", "Prod. cancelled", pcl)
                    self.add_date_combo(8,0, "date", "Informed duty time", str(row.duty_time), False, True) 
                    self.add_label(9,0, "lbl4", "Flags: %s" % row.flags)
            try:
                frm = SelectionDlg()
                infdt, isli, pcl = frm()
                print "repair_crew_publish_info: Old flags:",row.flags
                print "repair_crew_publish_info: Old inf. duty time:", str(row.duty_time), int(row.duty_time)
                if not isli:
                    if":cs1:" in row.flags:
                        row.flags =  row.flags.replace(":cs1:",":")
                        print "repair_crew_publish_info: Removing :cs1: flag manually"
                    elif":cs2:" in row.flags:
                        row.flags =  row.flags.replace(":cs2:",":")
                        print "repair_crew_publish_info: Removing :cs2: flag manually"
                    else:
                        print "repair_crew_publish_info: Late informed: Nothing to do"
                else:
                    if":cs1:" in row.flags or ":cs2:" in row.flags:
                        print "repair_crew_publish_info: Late informed: Nothing to do"
                    elif ":ss1:" in row.flags:
                        row.flags += "cs1:"
                        print "repair_crew_publish_info: Adding :cs1: flag manually"
                    elif ":ss2" in row.flags: 
                        row.flags += "cs2:"
                        print "repair_crew_publish_info: Adding :cs2: flag manually"
                    if not row.flags[0] == ':': row.flags = ':'+row.flags
                    else:
                        cfhExtensions.show("This duty does not have a short stop.")
                if not pcl:
                    if ":pcl:" in row.flags:
                        row.flags =  row.flags.replace(":pcl:",":")
                        print "repair_crew_publish_info: Removing :pcl: flag manually"
                    else:
                        print "repair_crew_publish_info: Pcl: Nothing to do"
                else:
                    if not ":pcl:" in row.flags:
                        row.flags += "pcl:"
                        print "repair_crew_publish_info: Adding :pcl: flag manually"
                    else:
                        print "repair_crew_publish_info: Pcl: Nothing to do"
                row.duty_time = infdt
                print "repair_crew_publish_info: New flags:",row.flags
                print "repair_crew_publish_info: New inf. duty time:", str(row.duty_time)
                return
            except F.CancelFormError:
                print "repair_crew_publish_info: Cancelled"
                return
        print "repair_crew_publish_info: There are no rows in crew_publish_info"
        cfhExtensions.show("There are no rows in crew_publish_info. Inform crew about this duty first.")
    else:
        sd, ed = R.eval("default_context", "fundamental.%pp_start%", "fundamental.%pp_end%")
        class SelectionDlg(F.BasicCfhForm):
            def __init__(self):
                F.BasicCfhForm.__init__(self, "Select problematic data")
                self.add_filter_combo(0, 0, "f1", "Select problem", "LOSS_OF_REST", ["LOSS_OF_REST:Loss of rest","ILLNESS_TEMP_CREW:Illness, temporary crew"])
                self.add_toggle_combo(1, 0, "f2", "Subselect", False)
                self.add_date_combo(2, 0, "f3", "Start date", str(sd), True, False)
                self.add_date_combo(3, 0, "f4", "End date", str(ed), True, False)
                self.add_toggle_combo(4, 0, "f5", "Problematic only", False)
                self.add_label(6,0, "lbl1", "Mark one leg to change its")
                self.add_label(7,0, "lbl2", "rescheduling information.")
        try:
            frm = SelectionDlg()
            ed, sd, type,problem,subsel = frm()
            print "Type=",type,", subsel=",subsel, sd,'-', ed, problem
            if type == 'LOSS_OF_REST':
                if problem:
                    raveExpr = "rescheduling.%is_late_informed_short_stop%"
                else:
                    raveExpr = "rest.%is_short%"                
            else:
                if problem:
                    raveExpr = "crew.%is_temporary% AND leg.%is_illness% AND default(rescheduling.%dt_inf_duty_time%(leg.%start_UTC%), 0:00) <= 0:00"
                else:
                    raveExpr = "crew.%is_temporary% AND leg.%is_illness%"
            raveExpr = "%s and leg.%%start_utc%% <= %s and leg.%%end_utc%% >= %s" % (raveExpr, str(ed), str(sd))
            if subsel:
                context = "default_context"
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
            else:
                context = "sp_crew"
            
            ids = R.eval(context, R.foreach(R.iter("iterators.leg_set", where=raveExpr, sort_by="leg.%start_UTC%"), "leg_identifier"))[0]
            if len(ids) == 0:
                cfhExtensions.show("No matches found.")
                return
            ids = [str(id) for nr, id in ids]
            Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.LegMode, ids)
            for id in ids:
                Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, id)
                Cui.CuiMarkLegs(Cui.gpc_info, area, 'object', Cui.CUI_MARK_SET)
            #Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
            #Cui.CuiMarkLegs(Cui.gpc_info, area, "object", Cui.CUI_MARK_SET)
            #Cui.CuiMarkLegs(gpc_info, area, "object", 0)
        except F.CancelFormError:
            print "Cancelled"
            return
        print "Hello repair"
        

# show_html_contents -----------------------------------------------------{{{2
def show_html_contents(xml_blob):
    global temp_files
    from xml.dom.minidom import parseString
    lines = xml_blob.split('\n')
    header = lines[0]
    xml_doc = '\n'.join(lines[1:])
    try:
        H = []
        for rbody in parseString(xml_doc).getElementsByTagName('replyBody'):
            for grp in rbody.getElementsByTagName('getReportReply'):
                for rep in grp.getElementsByTagName('reportBody'):
                    for node in rep.childNodes:
                        if node.nodeType == node.CDATA_SECTION_NODE:
                            H.append(node.data)
        if not H:
            raise ValueError('Unable to parse result!')
        else:
            html = '\n'.join(H)
    except Exception, e:
        fault_title = "Format error!"
        fault_text = "Could not extract HTML info"
        html = '<html><head><title>%s</title></head><body><h1>%s</h1><hl/><h2>Reason: %s</h2></body></html>' % (fault_title, fault_text, e)
    tf = TempFile(remove_when_destroyed=True)
    # Keep reference...
    temp_files.append(tf)
    print >>tf, html.encode('latin1')
    tf.close()
    Cui.CuiStartEmbeddedBrowser(str(tf), "ABS", "0", header)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
