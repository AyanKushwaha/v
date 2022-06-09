#

#
"""
AlertTimeOverride
Module for doing:
Manual override of alert time.
Purpose: Alert time override form will show the calculated alert time of a change,
         and will give the user the possibility to change it.
@date:2008-12-03
@author: Andres Salvador (salvad).
@org: Jeppesen Systems AB

"""

import os
import Errlog
import time
import tempfile
import Cui
import Cfh
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
import modelserver as M
import CfhExtension
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as R
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import carmusr.HelperFunctions as HF
from tm import TM
import utils.Names as Names
import carmusr.modcrew as modcrew
    
class AlertTimeOverrideForm(Cfh.Box):
    """
    The form is used when the user wants to override the alert time of a change.
    """
    class RemoveButton(Cfh.Function):
        """
            Defines a default button, resetting all values to the default ones.
        """
    
        def __init__(self, parent, name, text, mnemonic):
            Cfh.Function.__init__(self, parent, name, text, mnemonic)
            self.parent = parent
            
        def action(self):
    
            key = self.parent.key
            try:
                TM.alert_time_exception[key].remove()
            except M.EntityNotFoundError:
                cfhExtensions.show("No record found. Nothing was removed!", \
                                   title="Message")
            except Exception, e:
                Errlog.log("%s" % e)
                Errlog.set_user_message("Error: Could not remove record!\n")
                return -20
            self.finishForm(1, 0)
            return 0
                
    class CfhCheckDone(Cfh.Done):

        def __init__(self, parent, name):
            Cfh.Done.__init__(self, parent, name)
            self.parent = parent
    
        def action(self):
                
            key = self.parent.key
            user = Names.username()
            publ_time = AbsTime(*time.gmtime()[:5])
            alert = AbsTime(self.parent.alert_time.getValue() or 0)

            try:
                row = TM.alert_time_exception[key]
                if alert <> self.parent.alertValuesDict["ALERT_TIME"]:
                    row.si = "Modified by %s at %s" % (user, publ_time)
                    row.alerttime = alert
            except M.EntityNotFoundError:
                try:
                    row = TM.alert_time_exception.create(key)
                    row.si = "Created by %s at %s" % (user, publ_time)
                    row.alerttime = alert
                except Exception, e:
                    Errlog.log("%s" % e)
                    Errlog.set_user_message("Error: Could not create DataBase record!\n")
                    return -30
            except Exception, e:
                Errlog.log("%s" % e)
                Errlog.set_user_message("Error: Access to Database information!\n")
                return -40
            Cfh.Done.action(self)
            
    class CfhCheckString(Cfh.String):
        def __init__(self, *args):
            Cfh.String.__init__(self, *args)
            self._check_methods = []
        def register_check(self,check_func, arg=None):
            if check_func not in self._check_methods:
                self._check_methods.append([check_func, arg])
                
        def check(self,text):
            message = Cfh.String.check(self, text)
            if message:
                return message
            for func,arg in self._check_methods:
                if arg:
                    message = func(arg)
                else:
                    message = func()
                if message:
                    return message
            return ''
    
    #
    # Definitions of the fields in the form,
    # and of the default values to display in the fields:
    #
    
    def __init__(self, *args):

        SMALL_FIELD_SIZE = 6
        MEDIUM_FIELD_SIZE = 8
        LARGE_FIELD_SIZE = 15
        
        Cfh.Box.__init__(self, *args)

        self.currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)
        self.contextlocator = CuiContextLocator(Cui.CuiWhichArea, "object")

        self.key = tuple()
        self.alertValuesDict = {}
        self.getDefaultInfo()
        self.getAlertTimeInfo()

        self.flight_id = Cfh.String(self,
                                    "FLIGHT_ID",
                                    MEDIUM_FIELD_SIZE, 
                                    self.alertValuesDict["FLIGHT_ID"])
        self.flight_id.setEditable(0)
    
        self.crew_id = Cfh.String(self,
                                    "CREW_ID",
                                    SMALL_FIELD_SIZE, 
                                    self.alertValuesDict["CREW_ID"])
        self.crew_id.setEditable(0)
    
        self.depAbsTimeRaveValue = self.alertValuesDict["DEPARTURE_TIME"]

        self.depAbsTimeRaveValue = self.alertValuesDict["DEPARTURE_DATE"]
        self.departure_time = Cfh.String(self,
                                         "DEPARTURE_DATE",
                                         LARGE_FIELD_SIZE,
                                         self.depAbsTimeRaveValue.ddmonyyyy()[:9])
        self.departure_time.setEditable(0)
    
        # Alert time:
        self.alertAbsTime = self.alertValuesDict["ALERT_TIME"] 
        self.alert_time = self.CfhCheckString(self,
                                     "ALERT_TIME",
                                     LARGE_FIELD_SIZE,
                                     self.alertAbsTime.ddmonyyyy())
        self.alert_time.setMandatory(1)
        self.alert_time.setEditable(1)
        self.alert_time.register_check(self.alert_time_check)
        
        self.ok = self.CfhCheckDone(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")
        self.remove_button = self.RemoveButton(self, "B_REMOVE", "Remove", "_R")
            
        self.formDefaultValues()
        # The form layout
        form_layout = """
FORM;ALERT_TIME_OVERRIDE;Alert Time Override Form
COLUMN
LABEL;Crew ID
COLUMN
LFIELD;CREW_ID
COLUMN
LABEL;Activity ID:
COLUMN
LFIELD;FLIGHT_ID
GROUP
COLUMN
LABEL
COLUMN
LABEL
COLUMN
LABEL;Date:
COLUMN
LFIELD;DEPARTURE_DATE
GROUP
COLUMN
LABEL
COLUMN
LABEL;`Alert time UTC`
COLUMN
FIELD;ALERT_TIME
EMPTY
BUTTON;B_OK;`Ok`;`_OK`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
BUTTON;B_REMOVE;`Remove`;`_R`
"""

        alertTime_form_file = tempfile.mktemp()
        f = open(alertTime_form_file, "w")
        f.write(form_layout)
        f.close()
        self.load(alertTime_form_file)
        os.unlink(alertTime_form_file)
            
    def alert_time_check(self):
        message = ""
        try:
            if self.alert_time.getValue() == "":
                time = AbsTime(self.alert_time.valof())
            else:
                time = AbsTime(self.alert_time.getValue())
        except:
            return "Enter Alert Time as valid abstime, e.g. 01Jan2007 10:00"
        if time > self.alertValuesDict["ARRIVAL_DATE"]:
            return "Alert: %s, after current date: %s" % \
                   (time, self.alertValuesDict["ARRIVAL_DATE"])
        return ""
    
    def getDefaultInfo(self):
        """
        Fills dictionary with basic data.
        """
        try:
            leg_object = HF.LegObject(area=self.currentArea)
            
            (self.alertValuesDict["CREW_ID"],\
            self.alertValuesDict["FLIGHT_ID"],\
            self.alertValuesDict["DEPARTURE_TIME"],\
            self.alertValuesDict["DEPARTURE_DATE"],\
            self.alertValuesDict["ARRIVAL_DATE"],\
            self.alertValuesDict["HB_START_DAY_UTC"]) = leg_object.eval('crew.%id%',
                                        'leg.%flight_id_min_3_digits%',
                                        'leg.%activity_scheduled_start_time_UTC%',
                                        'round_down(leg.%activity_scheduled_start_time_UTC%,24:00)',
                                        'round_up(leg.%activity_scheduled_end_time_UTC%,24:00)-0:01',
                                        'crew.%utc_time%(leg.%start_date%)'
                                       )
            return 0
        except Exception, e:
            Errlog.log("%s" % e)
            Errlog.set_user_message("Error: Not possible to get default information from RAVE!\n")
            return -10
        
    def getAlertTimeInfo(self):
        """
        Updatess dictionary with alert time/deadline info.
        """
        errKey = 0
        crewRef = TM.crew.getOrCreateRef((self.alertValuesDict["CREW_ID"],))
        self.key = (crewRef, AbsTime(self.alertValuesDict["HB_START_DAY_UTC"]))
        try:
            row1 = TM.alert_time_exception[self.key]
            alerttime = row1.alerttime

        except M.EntityNotFoundError:

            alerttime = self.alertValuesDict["DEPARTURE_TIME"] - RelTime('05:00')
            
        self.alertValuesDict["ALERT_TIME"] = alerttime
        return 0
    
    def formDefaultValues(self):        
        """
        Sets the form default values.
        """
        self.flight_id.assign(str(self.alertValuesDict["FLIGHT_ID"]))
        self.crew_id.assign(str(self.alertValuesDict["CREW_ID"]))
        self.alert_time.assign(str(self.alertValuesDict["ALERT_TIME"]))
        
        return 0
            
def overrideAlertTime():
    
    alert_time_dialog = AlertTimeOverrideForm("Alert Time Override Form")
        
    alert_time_dialog.show(1)
    Ret = alert_time_dialog.loop()
    
    if Ret <> Cfh.CfhOk: return Ret
    key = alert_time_dialog.key
    modcrew.add(str(key[0]))
    Cui.CuiReloadTable("alert_time_exception", 1)
