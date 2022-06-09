#! /usr/bin/env python

########################################################
#
# Display Reports
#
# ------------------------------------------------------
# Main module for Displaying Python Reports from menues.
# ------------------------------------------------------
# Created:    2005-12-21
# By:         Carmen Systems AB, Risto Mitrevski
#
########################################################

from Cfh import *
from Cui import *
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from Localization import MSGR

import Localization

import Crs
#import RaveWrap as RW
import carmensystems.rave.api as R

# reportValues is used for reports that require additional information.
# Info such as LegTimePresentation (UTC or local time), start dates and end dates to base the report on.
reportValues = {}

def displayReport(rpt, scope = "object", context=None, type='standard', reportdir="include/"):
    path = "../lib/python/report_sources/"+reportdir

    # This information is passed to the reports that need it.
    area = CuiAreaIdConvert(gpc_info, CuiWhichArea)

    # This information is passed to the reports that need it.
    reportValues['context'] = context
    reportValues['scope'] = scope
    reportValues['area'] = area
    reportValues['presentation'] = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "LegTimePresentation")

    if scope == 'object':
        args = ' '.join(['%s=%s' % (key, value) for key, value in reportValues.iteritems()])
        try:
            # Required to set the area since the current area can change.
            CuiSetCurrentArea(gpc_info, area)
            CuiCrgSetDefaultContext(gpc_info, area, scope)
            CuiCrgDisplayTypesetReport(gpc_info, area, scope, path + rpt, 0, args)
        except Exception, e:
            print e
    elif scope == 'window':
        try: del rptForm
        except: pass
        if type == 'simple':
            rptForm = reportFormSimple(rpt)
        else:
            rptForm = reportForm(rpt)
        rptForm.show(1)
        if rptForm.loop() == CfhOk: # This info is used in the reports.
            reportValues['startDate'] = rptForm.getStartDate()
            reportValues['endDate'] = rptForm.getEndDate()
            reportValues['startTime'] = rptForm.getStartTime()
            reportValues['endTime'] = rptForm.getEndTime()
            args = ' '.join(['%s=%s' % (key, value) for key, value in reportValues.iteritems()])
            try:
                # Required to set the area since the current area can change.
                CuiSetCurrentArea(gpc_info, area)
                CuiCrgSetDefaultContext(gpc_info, area, scope)
                CuiCrgDisplayTypesetReport(gpc_info, area, scope, path + rpt, 0, args)
            except Exception, e:
                print e

# This form is a simple one. Only start date and end date.
class reportForm(Box) :
    def __init__(self, hdrTitle):
        Box.__init__(self, "reportForm", hdrTitle)
        
        # Get Default Dates
        (d1, d2) = self.setDefaultDates()
        (t1, t2) = self.setDefaultTimes()

        form_hdr = 'HEADER;' + hdrTitle
        form_hdr_d1 = 'FIELD;DATE_1;`Start date`'
        form_hdr_d2 = 'FIELD;DATE_2;`End date`'
        form_hdr_t1 = 'FIELD;TIME_1;'
        form_hdr_t2 = 'FIELD;TIME_2;'
        form_time_label = 'FIELD;LABEL;`UTC or Local depending on settings in Preferences`'

        layout = """
FORM;ReportForm;DisplayReport
%s
GROUP
%s
%s
COLUMN
%s
%s
GROUP
%s
EMPTY
BUTTON;B_OK;`OK`;`_OK`
BUTTON;B_CANCEL;`Cancel;`_Cancel`
""" % (form_hdr, form_hdr_d1, form_hdr_d2, form_hdr_t1, form_hdr_t2, form_time_label)

        filepath = tempfile.mktemp()
        f = open(filepath, "w")
        f.write(layout)
        f.close()

        self.f_label = String(self, 'LABEL', 0)
        self.f_label.setStyle(CfhSLabelNormal)

        # STARTDATE and ENDDATE
        self.startDateField = self.createDateField("DATE_1", d1)
        self.endDateField = self.createDateField("DATE_2", d2)
        self.startTimeField = self.createTimeField("TIME_1", t1)
        self.endTimeField = self.createTimeField("TIME_2", t2)

        self.ok = Done(self, "B_OK")
        self.quit = Cancel(self, "B_CANCEL")

        self.load(filepath)
        os.unlink(filepath)

    # reportForm Create-functions
    def createDateField(self, name, initialValue):
        timeField = Date(self, name, initialValue)
        timeField.setMandatory(1)
        return timeField

    def createTimeField(self, name, initialValue):
        timeField = Clock(self, name, initialValue)
        return timeField

    # reportForm Set-functions
    def setDefaultDates(self):
        """
        Get default dates for selection mask
        d2 == d1 -> Today has the same start date and end date.
        """
        now = AbsTime(CuiCrcEvalAbstime(
            gpc_info, CuiNoArea, 'NONE', "calendar.%month_start%"))
        d1 = R.eval('round_down(%s,%d:%02d)' % (str(now), 24, 0))[0]
        d2 = d1
        d1 = int(d1)
        d2 = int(d2)
        return (d1,d2)

    def setDefaultTimes(self):
        """
        Get default start/end time for selection mask.
        """
        t1 = 0
        t2 = 1439 # 23:59
        return (t1,t2)

    # reportForm Get-functions
    def getStartDate(self):
        return self.startDateField.valof()

    def getEndDate(self):
        return self.endDateField.valof()

    def getStartTime(self):
        return self.startTimeField.valof()

    def getEndTime(self):
        return self.endTimeField.valof()

# This form is like previos but without times.
class reportFormDate(Box) :
    def __init__(self, hdrTitle, start_date=None, end_date=None):
        Box.__init__(self, "reportForm", hdrTitle)
        
        if (not start_date or not end_date):
            # Get Default Dates
            (d1, d2) = self.setDefaultDates()
        else:
            (d1, d2) = (start_date, end_date)
        
        form_hdr = 'HEADER;' + hdrTitle
        form_hdr_d1 = 'FIELD;DATE_1;`Start date`'
        form_hdr_d2 = 'FIELD;DATE_2;`End date`'
        form_time_label = 'FIELD;LABEL;`UTC or Local depending on settings in Preferences`'

        layout = """
FORM;ReportForm;DisplayReport
%s
GROUP
%s
%s
GROUP
%s
EMPTY
BUTTON;B_OK;`OK`;`_OK`
BUTTON;B_CANCEL;`Cancel;`_Cancel`
""" % (form_hdr, form_hdr_d1, form_hdr_d2, form_time_label)

        filepath = tempfile.mktemp()
        f = open(filepath, "w")
        f.write(layout)
        f.close()

        self.f_label = String(self, 'LABEL', 0)
        self.f_label.setStyle(CfhSLabelNormal)

        # STARTDATE and ENDDATE
        self.startDateField = self.createDateField("DATE_1", d1)
        self.endDateField = self.createDateField("DATE_2", d2)

        self.ok = Done(self, "B_OK")
        self.quit = Cancel(self, "B_CANCEL")

        self.load(filepath)
        os.unlink(filepath)

    # reportForm Create-functions
    def createDateField(self, name, initialValue):
        timeField = Date(self, name, initialValue)
        timeField.setMandatory(1)
        return timeField

    # reportForm Set-functions
    def setDefaultDates(self):
        """
        Get default dates for selection mask
        d2 == d1 -> Today has the same start date and end date.
        """
        now = AbsTime(CuiCrcEvalAbstime(
            gpc_info, CuiNoArea, 'NONE', "calendar.%month_start%"))
        d1 = R.eval('round_down(%s,%d:%02d)' % (str(now), 24, 0))[0]
        d2 = d1.addmonths(1)
        d1 = int(d1)
        d2 = int(d2)
        return (d1,d2)

    # reportForm Get-functions
    def getStartDate(self):
        return self.startDateField.valof()

    def getEndDate(self):
        return self.endDateField.valof()

# This form shows station, start date and end date.
class reportFormExt(Box):
    def __init__(self, hdrTitle):
        Box.__init__(self, "ExtReportForm", hdrTitle)
        
        # Get Default Dates
        (d1, d2) = self.setDefaultDates()
        (t1, t2) = self.setDefaultTimes()

        # STATION, STARTDATE and ENDDATE
        form_hdr = 'HEADER;' + hdrTitle
        form_hdr_stn = 'FIELD;STRING;Station;'
        form_hdr_d1 = 'FIELD;DATE_1;Start date;'
        form_hdr_d2 = 'FIELD;DATE_2;End date;'
        form_hdr_t1 = 'FIELD;TIME_1;'
        form_hdr_t2 = 'FIELD;TIME_2;'

        layout = """
FORM;ExtReportForm;DisplayReport
%s
GROUP
%s
GROUP
%s
%s
COLUMN
%s
%s
EMPTY
BUTTON;B_OK;`OK`;`_OK`
BUTTON;B_CANCEL;`Cancel;`_Cancel`
""" % (form_hdr, form_hdr_stn, form_hdr_d1, form_hdr_d2, form_hdr_t1, form_hdr_t2)

        filepath = tempfile.mktemp()
        f = open(filepath, "w")
        f.write(layout)
        f.close()

        self.station = self.createStringField("STRING", 3)
        self.startDateField = self.createDateField("DATE_1", d1)
        self.endDateField = self.createDateField("DATE_2", d2)
        self.startTimeField = self.createTimeField("TIME_1", t1)
        self.endTimeField = self.createTimeField("TIME_2", t2)

        self.ok = Done(self, "B_OK")
        self.quit = Cancel(self, "B_CANCEL")

        self.load(filepath)
        os.unlink(filepath)

    # reportForm Create-functions
    def createDateField(self, name, initialValue):
        timeField = Date(self, name, initialValue)
        timeField.setMandatory(1)
        return timeField

    def createTimeField(self, name, initialValue):
        timeField = Clock(self, name, initialValue)
        return timeField

    def createStringField(self, name,l):
        stringField = String(self, name, l)
        stringField.setTranslation(CfhEntry.ToUpper)
        return stringField

    # reportForm Set-functions
    def setDefaultDates(self):
        """
        Get default dates for selection mask
        d2 == d1 -> Today has the same start date and end date.
        """
        now = AbsTime(CuiCrcEvalAbstime(
            gpc_info, CuiNoArea, 'NONE', "calendar.%month_start%"))
        d1 = R.eval('round_down(%s,%d:%02d)' % (str(now), 24, 0))[0]
        d2 = d1
        d1 = int(d1)
        d2 = int(d2)
        return (d1,d2)

    def setDefaultTimes(self):
        """
        Get default start/end time for selection mask.
        """
        t1 = 0
        t2 = 1439 # 23:59
        return (t1,t2)

    # reportForm Get-functions
    def getStartDate(self):
        return self.startDateField.valof()

    def getEndDate(self):
        return self.endDateField.valof()

    def getStartTime(self):
        return self.startTimeField.valof()

    def getEndTime(self):
        return self.endTimeField.valof()

    def getStation(self):
        return self.station.valof()

# This form is a simple one. Only start date.
class reportFormSimple(Box) :
    def __init__(self, hdrTitle):
        Box.__init__(self, "reportForm", hdrTitle)
        
        # Get Default Dates
        d1 = self.setDefaultDates()
        

        form_hdr = 'HEADER;' + hdrTitle
        form_hdr_d1 = 'FIELD;DATE_1;`Month`'
        form_time_label = 'FIELD;LABEL;`UTC or Local depending on settings in Preferences`'

        layout = """
FORM;ReportForm;DisplayReport
%s
GROUP
%s
GROUP
%s
EMPTY
BUTTON;B_OK;`OK`;`_OK`
BUTTON;B_CANCEL;`Cancel;`_Cancel`
""" % (form_hdr, form_hdr_d1, form_time_label)

        filepath = tempfile.mktemp()
        f = open(filepath, "w")
        f.write(layout)
        f.close()

        self.f_label = String(self, 'LABEL', 0)
        self.f_label.setStyle(CfhSLabelNormal)

        # STARTDATE and ENDDATE
        self.startDateField = self.createDateField("DATE_1", d1)

        self.ok = Done(self, "B_OK")
        self.quit = Cancel(self, "B_CANCEL")

        self.load(filepath)
        os.unlink(filepath)

    # reportForm Create-functions
    def createDateField(self, name, initialValue):
        timeField = Date(self, name, initialValue)
        timeField.setMandatory(1)
        return timeField

    def createTimeField(self, name, initialValue):
        timeField = Clock(self, name, initialValue)
        return timeField

    # reportForm Set-functions
    def setDefaultDates(self):
        """
        Get default dates for selection mask
        d2 == d1 -> Today has the same start date and end date.
        """
        now = AbsTime(CuiCrcEvalAbstime(
            gpc_info, CuiNoArea, 'NONE', "calendar.%month_start%"))
        d1 = R.eval('round_down(%s,%d:%02d)' % (str(now), 24, 0))[0]
        d1 = int(d1)
        return d1

    def setDefaultTimes(self):
        """
        Get default start/end time for selection mask.
        """
        t1 = 0
        t2 = 1439 # 23:59
        return (t1,t2)

    # reportForm Get-functions
    def getStartDate(self):
        return self.startDateField.valof()

    def getEndDate(self):
        return None

    def getStartTime(self):
        return None

    def getEndTime(self):
        return None


# EOF
