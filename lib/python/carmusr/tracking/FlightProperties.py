
#
#
# Purpose: FlightProperties provides a form for entering and editing
#          properties of a flight leg.
# Author:  Olof Mogren
# Date:    2007-10-17
#

import Crs
import Cui
import Cfh
import CfhExtension
import modelserver as M
import os
import tempfile
import Cui
import Select
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from carmstd.parameters import parameter
import carmstd
#import carmensystems.rave.api as R
#from utils.rave import RaveIterator
import carmstd.studio.area as StdArea
from utils.selctx import FlightFilter
import cmsadm
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import carmensystems.rave.api as R


#from utils.rave import RaveIterator
import string

# set the following to true to get verbose messages in the
# error log.
debugOutput = False

class FlightProperties(Cfh.Box):
    """
        A custom CFH box representing a flight leg properties form.
    """
    def __init__(self, *args):
        VERY_SMALL_FIELD_SIZE = 8
        SMALL_FIELD_SIZE = 10
        LARGE_FIELD_SIZE = 12

        Cfh.Box.__init__(self, *args)

        self.currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)
        self.contextlocator = CuiContextLocator(Cui.CuiWhichArea, "object")
        

        self.raveValuesDict = {}

        self.raveValuesDict["FLIGHT_ID"] = string.replace(Cui.CuiCrcEvalString(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%flight_id_min_3_digits%"),
                " ",
                "")
        self.raveValuesDict["SERVICE_TYPE"] = Cui.CuiCrcEvalString(Cui.gpc_info,
                self.currentArea, "object", "crg_info.%service_type%")
        self.raveValuesDict["DEPARTURE_TIME"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_scheduled_start_time_UTC%"))
        self.raveValuesDict["ARRIVAL_TIME"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_scheduled_end_time_UTC%"))
        self.raveValuesDict["eobt"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_estimated_start_time_UTC%"))
        self.raveValuesDict["eibt"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_estimated_end_time_UTC%"))
        self.raveValuesDict["aobt"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_actual_start_time_UTC%"))
        self.raveValuesDict["aibt"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%activity_actual_end_time_UTC%"))
        self.raveValuesDict["DEPARTURE_AIRPORT"] = Cui.CuiCrcEvalString(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%start_station%")
        self.raveValuesDict["ARRIVAL_AIRPORT"] = Cui.CuiCrcEvalString(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%end_station%")
        self.raveValuesDict["IATA_CODE"] = Cui.CuiCrcEvalString(Cui.gpc_info,
                self.currentArea, "object", "leg.%ac_type%")
        self.raveValuesDict["COC_EMP"] = Cui.CuiCrcEvalString(Cui.gpc_info,
                self.currentArea, "object", "cockpit_crew_employer")
        self.raveValuesDict["CAB_EMP"] = Cui.CuiCrcEvalString(Cui.gpc_info,
                self.currentArea, "object", "cabin_crew_employer")
        self.raveValuesDict["AC_OWNER"] = Cui.CuiCrcEvalString(Cui.gpc_info,
                self.currentArea, "object", "leg.%aircraft_owner%")
        self.raveValuesDict["LEG_NUMBER"] = str(Cui.CuiCrcEvalInt(Cui.gpc_info,
                self.currentArea, "object", "leg.%leg_number%") or "1")
        self.raveValuesDict["udor"] = AbsTime(Cui.CuiCrcEvalAbstime(\
                Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%udor%"))
        self.raveValuesDict["LEG_TYPE"] = Cui.CuiCrcEvalBool(Cui.gpc_info,
                self.currentArea,
                "object",
                "leg.%is_on_duty%") and "Yes" or "No"

        self.dataPeriodPre = 0
        self.dataPeriodPost = 0
        

        if debugOutput:
            print "*** FlightProperties debug: rave values:"
            for k in self.raveValuesDict.keys():
                print "   *** " + k + " = '" + str(self.raveValuesDict[k]) + "'"
        
        
        #
        # Definitions of the fields in the form,
        # and of the default values to display in the fields:
        #
        #

        # FIRST COLUMN
        
        self.flight_id = Cfh.String(self, "FLIGHT_ID", SMALL_FIELD_SIZE,
                self.raveValuesDict["FLIGHT_ID"])
        self.flight_id.setMandatory(1)
        self.flight_id.setEditable(0)


        self.service_type = CfhServiceTypeString(self,
                                                 "SERVICE_TYPE",
                                                 1,
                                                 self.raveValuesDict["SERVICE_TYPE"])
        self.service_type.setMandatory(1)

        self.leg_number = CfhExtension.CustomNumber(self, "LEG_NUMBER", 2,
                self.raveValuesDict["LEG_NUMBER"], True)
        self.leg_number.setMandatory(1)
        self.leg_number.setEditable(0)

        # scheduled start time
        self.depAbsTimeRaveValue = self.raveValuesDict["DEPARTURE_TIME"]
        self.depTimeRaveValue = AbsTime(self.depAbsTimeRaveValue).time_of_day()
        self.departure_time = Cfh.Duration(self,
                                           "DEPARTURE_TIME",
                                           self.depTimeRaveValue)
        self.departure_time.setEditable(0)



        # scheduled end time
        self.destAbsTimeRaveValue = self.raveValuesDict["ARRIVAL_TIME"] 
        self.destTimeRaveValue = AbsTime(\
                                    self.destAbsTimeRaveValue).time_of_day()
        self.arrival_time   = Cfh.Duration(self,
                                           "ARRIVAL_TIME",
                                           self.destTimeRaveValue)
        self.arrival_time.setEditable(0)



        # number of days between scheduled start time and end time
        # (normally 0 or 1)
        self.offset_days_int = self.daysOffset(\
                                       self.raveValuesDict["DEPARTURE_TIME"],
                                       self.raveValuesDict["ARRIVAL_TIME"])
        self.arrival_offset_days = CfhExtension.CustomNumber(self,
                                                      "ARRIVAL_OFFSET_DAYS",
                                                      SMALL_FIELD_SIZE,
                                                      str(self.offset_days_int),
                                                      False,
                                                      -1,
                                                      5)
        self.arrival_offset_days.setEditable(0)



        # SECOND COLUMN
        # dep airport
        self.departure_airport = CfhExtension.AirportString(self,
                                   "DEPARTURE_AIRPORT",
                                   SMALL_FIELD_SIZE,
                                   self.raveValuesDict["DEPARTURE_AIRPORT"])
        self.departure_airport.setMandatory(1)
        self.departure_airport.setEditable(0)

        # arrival airport
        self.arrival_airport = CfhExtension.AirportString(self,
                                   "ARRIVAL_AIRPORT",
                                   SMALL_FIELD_SIZE,
                                   self.raveValuesDict["ARRIVAL_AIRPORT"])
        self.arrival_airport.setMandatory(1)
        
        # estimated on-block time:
        if int(self.raveValuesDict["eobt"]):
            eobtRaveValue = AbsTime(self.raveValuesDict["eobt"]).time_of_day()
        else: eobtRaveValue = ""
        if debugOutput: print "FlightProperties: eobtRaveValue= " + \
                              str(eobtRaveValue)
        self.eobt = CfhExtension.RelTimeField(self,
                                              "eobt",
                                              SMALL_FIELD_SIZE,
                                              str(eobtRaveValue),
                                              False,
                                              False)
        
        eobtOffsetValue = str(self.daysOffset(self.depAbsTimeRaveValue,
                self.raveValuesDict["eobt"]))
        if not int(self.raveValuesDict["eobt"]): eobtOffsetValue = ""
        self.eobt_offset = CfhExtension.CustomNumber(self,
                                                     "eobt_offset",
                                                     SMALL_FIELD_SIZE,
                                                     eobtOffsetValue,
                                                     False,
                                                     -1,
                                                     5)

        # estimated off-block time:
        if int(self.raveValuesDict["eibt"]):
            eibtRaveValue = AbsTime(self.raveValuesDict["eibt"]).time_of_day()
        else: eibtRaveValue = ""
        if debugOutput: print "FlightProperties: eibtRaveValue= " + \
                              str(eibtRaveValue)
        self.eibt = CfhExtension.RelTimeField(self,
                                              "eibt",
                                              SMALL_FIELD_SIZE,
                                              str(eibtRaveValue),
                                              False,
                                              False)
        
        eibtOffsetValue = str(self.daysOffset(self.destAbsTimeRaveValue,
                self.raveValuesDict["eibt"]))
        if not int(self.raveValuesDict["eibt"]): eibtOffsetValue = ""
        self.eibt_offset = CfhExtension.CustomNumber(self,
                                                     "eibt_offset",
                                                     SMALL_FIELD_SIZE,
                                                     eibtOffsetValue,
                                                     False,
                                                     -1,
                                                     5)

        # THIRD COLUMN
        # aircraft/iata code:
        if self.raveValuesDict["IATA_CODE"] == "UNK":
            iata_c = ""
        else:
            iata_c = self.raveValuesDict["IATA_CODE"]
        self.iata_code = CfhIATAString(self, "IATA_CODE", SMALL_FIELD_SIZE, iata_c)

        # cockpit crew employer:
        self.coc_emp = CfhEmpString(self, "COC_EMP", SMALL_FIELD_SIZE,
                                  self.raveValuesDict["COC_EMP"])
        self.coc_emp.setMandatory(1)
        # cabin crew employer:
        self.cab_emp = CfhEmpString(self, "CAB_EMP", SMALL_FIELD_SIZE,
                                  self.raveValuesDict["CAB_EMP"])
        self.cab_emp.setMandatory(1)
        # aircraft owner:
        self.ac_owner = CfhEmpString(self, "AC_OWNER", SMALL_FIELD_SIZE,
                                   self.raveValuesDict["AC_OWNER"])
        self.ac_owner.setMandatory(1)

        # actual on-block time:
        if int(self.raveValuesDict["aobt"]):
            aobtRaveValue = AbsTime(self.raveValuesDict["aobt"]).time_of_day()
        else: aobtRaveValue = ""
        if debugOutput: print "FlightProperties: aobtRaveValue= " + \
                              str(aobtRaveValue)
        self.aobt = CfhExtension.RelTimeField(self,
                                              "aobt",
                                              SMALL_FIELD_SIZE,
                                              str(aobtRaveValue),
                                              False,
                                              False)
        self.aobt.setEditable(0)


        aobtOffsetValue = str(self.daysOffset(self.depAbsTimeRaveValue,
                self.raveValuesDict["aobt"]))
        if not int(self.raveValuesDict["aobt"]): aobtOffsetValue = ""
        self.aobt_offset = CfhExtension.CustomNumber(self,
                                                     "aobt_offset",
                                                     SMALL_FIELD_SIZE,
                                                     aobtOffsetValue,
                                                     False,
                                                     -1,
                                                     5)
        self.aobt_offset.setEditable(0)

        
        # actual off-block time:
        if int(self.raveValuesDict["aibt"]):
            aibtRaveValue = AbsTime(self.raveValuesDict["aibt"]).time_of_day()
        else: aibtRaveValue = ""
        if debugOutput: print "FlightProperties: aibtRaveValue= " + \
                              str(aibtRaveValue)
        self.aibt = CfhExtension.RelTimeField(self,
                                              "aibt",
                                              SMALL_FIELD_SIZE,
                                              str(aibtRaveValue),
                                              False,
                                              False)
        self.aibt.setEditable(0)


        aibtOffsetValue = str(self.daysOffset(self.destAbsTimeRaveValue,
                self.raveValuesDict["aibt"]))
        if not int(self.raveValuesDict["aibt"]): aibtOffsetValue = ""
        self.aibt_offset = CfhExtension.CustomNumber(self,
                                                     "aibt_offset",
                                                     SMALL_FIELD_SIZE,
                                                     aibtOffsetValue,
                                                     False,
                                                     -1,
                                                     5)
        self.aibt_offset.setEditable(0)

        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")
        self.reset = Cfh.Reset(self, "B_RESET")
        self.print_button = Cfh.Print(self, "B_PRINT")

        if debugOutput: print os.environ["CARMUSR"]+\
                              "/data/form/flight_properties_tracking"

        self.load(os.environ["CARMUSR"]+"/data/form/flight_properties_tracking")
        


    def daysOffset(self, absT1, absT2):
        """
            Computes the number of days between absT1 and absT2.
            If they are on the same day, return 0.
            If either date is 0 (1986-01-01), also return 0.
        """
        if not absT1 or not absT2: return 0
        a1 = AbsTime(absT1)
        a2 = AbsTime(absT2)
        a1 = a1.day_floor()
        a2 = a2.day_floor()
        difference = int(a2)/(24*60)-int(a1)/(24*60)
        return difference 
    
    def isChanged(self):
        """
            Checks if anything was changed in the form.
        """
        if debugOutput: print "*** FlightProp: isChanged() comparing: "
        v = self.getValues()
        for currValues in v:
            for k in currValues:
                if debugOutput:
                    try:
                        print "   *** " + k + ": " + \
                                str(self.raveValuesDict[k]) + \
                                ", " + str(currValues[k])
                    except:
                        print "   *** " + k + ": pass"
                if k == "FORM" or \
                   k == "FL_TIME_BASE" or \
                   k == "FREQUENCY" or \
                   k == "PERIOD_START" or \
                   k == "PERIOD_END" or \
                   k == "GDOR_OFFSET_DAYS" or \
                   k == "ONW_LEG_DEP":
                    pass
                elif k == "DEPARTURE_TIME" or k == "ARRIVAL_TIME":
                    t = AbsTime(self.raveValuesDict[k])
                    if self.relTimeToStr(t.time_of_day()) != currValues[k]:
                        if debugOutput: print "NOT EQUAL!"
                        return True
                elif k == "ARRIVAL_OFFSET_DAYS":
                    if str(self.offset_days_int) != currValues[k]:
                        if debugOutput: print "NOT EQUAL!"
                        return True
                elif k == "eobt" or k == "eibt":
                    if str(self.raveValuesDict[k]) != currValues[k]:
                        if int(self.raveValuesDict[k]) or currValues[k]:
                            if debugOutput: print "NOT EQUAL!"
                            return True
                elif str(self.raveValuesDict[k]) != currValues[k]:
                    # values in self.raveValuesDict are either str or AbsTime.
                    # currValues are always str.
                    if debugOutput: print "NOT EQUAL!"
                    return True
        return False

    def relTimeToStr(self, relTimeInput):
        """
            In the original form, times are inputted in a special format,
            (HHMM), without colon. This function takes a reltime as argument,
            and returns a string in this format.
        """
        return str(RelTime(relTimeInput))[:-3]+ \
                   str(RelTime(relTimeInput))[-2:]

    def getValues(self):
        """
            returns a list of dicts like the following:
            [{
            'FORM': 'DUMMY_FLIGHT',
            'FL_TIME_BASE': 'UDOP',
            'FLIGHT_ID': 'SK7325',
            'LEG_NUMBER': '1',
            'SERVICE_TYPE': 'C',
            'FREQUENCY': 'D',
            'PERIOD_START': '12Aug2007',
            'PERIOD_END': '12Aug2007',
            'GDOR_OFFSET_DAYS': '0',
            'DEPARTURE_TIME': '0440',
            'ARRIVAL_TIME': '0830',
            'ARRIVAL_OFFSET_DAYS': '0',
            'DEPARTURE_AIRPORT': 'OSL',
            'ARRIVAL_AIRPORT': 'SMI',
            'IATA_CODE': '73G',
            'COC_EMP': 'BU',
            'CAB_EMP': 'BU',
            'AC_OWNER': 'BU',
            'ONW_LEG_DEP': '0',
            'LEG_TYPE': 'Yes',
            'eobt': '12AUG2007 5:02',
            'eibt': '12AUG2007 8:57',
            'aobt': '12AUG2007 5:02',
            'aibt': '12AUG2007 8:57',
            'OK': '',
            }]

            when bypassing the original form, the first dicts in the list
            will be entered first.

            self.currentArea
            self.fl_time_base
            self.flight_id
            self.service_type
            self.departure_time
            self.arrival_time
            self.arrival_offset_days
            self.departure_airport
            self.arrival_airport
            self.iata_code
            self.coc_emp
            self.cab_emp
            self.ac_owner
            self.eobt
            self.eibt
            self.aobt
            self.aibt
            self.ok
            self.cancel
            self.reset
            self.print_button

        """

        if self.eobt.valof():
            # if offset is unset (empty string), 
            # assume it is the same day as scheduled.
            offset = int(self.eobt_offset.valof() or "0")
            eobtAbsTime = AbsTime(self.depAbsTimeRaveValue) - \
                        AbsTime(self.depAbsTimeRaveValue).time_of_day() + \
                        RelTime(offset, 0, 0) + \
                        RelTime(self.eobt.valof())
        else:
            eobtAbsTime = AbsTime(0)

        if self.eibt.valof():
            # if offset is unset (empty string),
            # assume it is the same day as scheduled.
            offset = int(self.eibt_offset.valof() or "0")
            eibtAbsTime = AbsTime(self.destAbsTimeRaveValue) - \
                        AbsTime(self.destAbsTimeRaveValue).time_of_day() + \
                        RelTime(offset, 0, 0) + \
                        RelTime(self.eibt.valof())
        else:
            eibtAbsTime = AbsTime(0)

        if self.iata_code.valof() == "":
            iata_code = "UNK"
        else:
            iata_code = self.iata_code.valof()

        return [{'FORM': 'DUMMY_FLIGHT',
            'FL_TIME_BASE': 'UDOP'},
            {'FORM': 'DUMMY_FLIGHT',
            'FLIGHT_ID': string.replace(self.flight_id.valof().upper()," ","")},
            {'FORM': 'DUMMY_FLIGHT',
            'LEG_NUMBER': str(self.leg_number.valof())},
            {'FORM': 'DUMMY_FLIGHT',
            'SERVICE_TYPE': self.service_type.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'FREQUENCY': 'D'},
            {'FORM': 'DUMMY_FLIGHT',
            'PERIOD_START': str(AbsDate(self.raveValuesDict["udor"]))},
            {'FORM': 'DUMMY_FLIGHT',
            'PERIOD_END': str(AbsDate(self.raveValuesDict["udor"]))},
            {'FORM': 'DUMMY_FLIGHT',
            'GDOR_OFFSET_DAYS': '0'},
            {'FORM': 'DUMMY_FLIGHT',
            'DEPARTURE_TIME': self.relTimeToStr(self.departure_time.valof())},
            {'FORM': 'DUMMY_FLIGHT',
            'ARRIVAL_TIME': self.relTimeToStr(self.arrival_time.valof())},
            {'FORM': 'DUMMY_FLIGHT',
            'ARRIVAL_OFFSET_DAYS': str(self.arrival_offset_days.valof())},
            {'FORM': 'DUMMY_FLIGHT',
            'DEPARTURE_AIRPORT': self.departure_airport.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'ARRIVAL_AIRPORT': self.arrival_airport.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'IATA_CODE': iata_code},
            {'FORM': 'DUMMY_FLIGHT',
            'COC_EMP': self.coc_emp.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'CAB_EMP': self.cab_emp.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'AC_OWNER': self.ac_owner.valof().upper()},
            {'FORM': 'DUMMY_FLIGHT',
            'ONW_LEG_DEP': '0'},
            {'FORM': 'DUMMY_FLIGHT',
            'LEG_TYPE': self.raveValuesDict["LEG_TYPE"]},
            {'FORM': 'DUMMY_FLIGHT',
            'eobt': str(eobtAbsTime)},
            {'FORM': 'DUMMY_FLIGHT',
            'eibt': str(eibtAbsTime)}]

    def saveChanges(self):
        """
        Example wrapping: (not right cui function)
        Cui.CuiDuplicateChains({'FORM': 'COPY_CHAIN', \
            'FL_CC': '0/0/0/0//0/0/0/2/0//0', \
            'FL_NR_COPIES': '1', 'FL_REDUCE_CC': 'Yes', \
            'FL_SPLIT_IMPLAUSIBLE_CC': 'No'}, Cui.gpc_info, \
            area, "WINDOW", 7)

            The values:
            {
            'FORM': 'DUMMY_FLIGHT',
            'FL_TIME_BASE': 'UDOP',
            'FLIGHT_ID': 'SK7325',
            'LEG_NUMBER': '1',
            'SERVICE_TYPE': 'C',
            'FREQUENCY': 'D',
            'PERIOD_START': '12Aug2007',
            'PERIOD_END': '12Aug2007',
            'GDOR_OFFSET_DAYS': '0',
            'DEPARTURE_TIME': '0440',
            'ARRIVAL_TIME': '0830',
            'ARRIVAL_OFFSET_DAYS': '0',
            'DEPARTURE_AIRPORT': 'OSL',
            'ARRIVAL_AIRPORT': 'SMI',
            'IATA_CODE': '73G',
            'COC_EMP': 'BU',
            'CAB_EMP': 'BU',
            'AC_OWNER': 'BU',
            'ONW_LEG_DEP': '0',
            'LEG_TYPE': 'Yes',
            'eobt': '12AUG2007 5:02',
            'eibt': '12AUG2007 8:57',
            'aobt': '12AUG2007 5:02',
            'aibt': '12AUG2007 8:57',
            'OK': '',
            }

            The right cui function:
            Cui.CuiLegSetProperties(Cui.gpc_info, Cui.CuiWhichArea, "object")
        """

        self.contextlocator.reinstate()                
        
        ##start = R.eval("crg_date.%abs2int%(fundamental.%pp_start%)")
        ##end = R.eval("crg_date.%abs2int%(fundamental.%pp_end%)")
        start = (R.eval("fundamental.%pp_start%")[0] - AbsTime("01Jan1986")) / RelTime("00:01")
        end = (R.eval("fundamental.%pp_end%")[0] - AbsTime("01Jan1986")) / RelTime("00:01")

        if self.dataPeriodPre == 0 or self.dataPeriodPost == 0:
            self.getPeriodResources()
            dataPeriodStart = AbsTime((start/1440 - self.dataPeriodPre)*1440)
            dataPeriodEnd = AbsTime((end/1440 + self.dataPeriodPost)*1440)
        print 'BEFORE: >>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodStart
        print '        >>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodEnd
        Cui.CuiSetLocalPlanPeriod(Cui.gpc_info, dataPeriodStart, dataPeriodEnd)
        
        vl = self.getValues()

        if debugOutput:
            print "*** FlightPropertiesForm setting leg properties " +\
                    "(wrapping dummy_flight):"
            for v in vl:
                for k in v.keys():
                    if k != "FORM":
                        print "  *** " + k + ": " + str(v[k])

        Cui.CuiLegSetProperties(vl[0], vl[1], vl[2], vl[3], vl[4],
                                vl[5], vl[6], vl[7], vl[8], vl[9],
                                vl[10], vl[11], vl[12], vl[13], vl[14],
                                vl[15], vl[16], vl[17], vl[18], vl[19],
                                vl[20],
                                Cui.gpc_info, self.currentArea, "object")
        
        #dataPeriodStart = AbsTime(start)
        #dataPeriodEnd = AbsTime(end)
        #print 'AFTER: >>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodStart
        #print '       >>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodEnd
        #Cui.CuiSetLocalPlanPeriod(Cui.gpc_info, dataPeriodStart, dataPeriodEnd)
        
    def getPeriodResources(self):
        if self.dataPeriodPre == 0:
            dataPeriodPre = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef, "DataPeriodDbPre")
            print '>>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodPre
            if dataPeriodPre:
                self.dataPeriodPre = long(dataPeriodPre)
            dataPeriodPost =  Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef, "DataPeriodDbPost")
            print '>>>>>>>>>>>>>>>>>>>>>>>>   ', dataPeriodPost
            if dataPeriodPost:
                self.dataPeriodPost = long(dataPeriodPost)



class CfhEmpString(Cfh.String):
    """
        CFH custom string input field for employer.
    """
    def __init__(self, box, name, maxLength, initial_value):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)

    def check(self, text):
        if len(text) < 2:
            return "Wrong format. Use aaa|xa|ax"
        elif len(text) == 2:
            if text.isalnum(): return None
            else: return "Wrong format. Use aaa|xa|ax"
        elif len(text) == 3:
            if text.isalpha(): return None
            else: return "Wrong format. Use aaa|xa|ax"

class CfhIATAString(Cfh.String):
    """
        CFH custom string input field for iata codes.
    """
    def __init__(self, box, name, maxLength, initial_value):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)

    def check(self, text):
        if len(text) != 3: return "Wrong format. Input three alphanumeric characters."
        else: return None

class CfhServiceTypeString(Cfh.String):
    """
        CFH custom string input field for service type codes.
    """
    def __init__(self, box, name, maxLength, initial_value):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)

    def check(self, text):
        if not text.isalpha(): return "Wrong format. Use only international alphanumeric characters."
        else: return None

def showFlightProperties():
    """
        Starts the flight properties form, using the FlightProperties class.
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    
    flight_properties_form = FlightProperties("Flight_Properties")

    flight_properties_form.show(1)

    if flight_properties_form.loop() == Cfh.CfhOk and \
                                        flight_properties_form.isChanged():
        flight_properties_form.saveChanges()
    
    
