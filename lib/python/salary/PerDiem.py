"""
Per Diem Evaluation and Operations module.
"""

import carmensystems.rave.api as r
from AbsDate import AbsDate
from RelTime import RelTime
from AbsTime import AbsTime

from utils.RaveData import DataClass

import math


ROSTER_CREW_ID = 0
ROSTER_FIRST_NAME = 1
ROSTER_LAST_NAME = 2
ROSTER_HOMEBASE = 3
ROSTER_RANK = 4
ROSTER_MAIN_FUNC = 5
ROSTER_DEPARTMENT = 6
ROSTER_CREW_EMPNO = 7
ROSTER_AC_QUALS = 8
ROSTER_CONTACT = 9
ROSTER_CONTACT_PHONE = 10
ROSTER_CONTACT_EMAIL = 11
ROSTER_CONTACT_DEPARTMENT = 12
ROSTER_EXCLUDED = 13
ROSTER_HOME_CURRENCY = 14
ROSTER_VALUES = ('report_common.%crew_id%',
                 'report_common.%crew_firstname%',
                 'report_common.%crew_surname%',
                 'report_common.%crew_homebase_salary%',
                 'report_common.%crew_rank_salary%',
                 'report_common.%crew_main_func_salary%',
                 'default(report_per_diem.%crew_department%, "")',
                 'report_common.%employee_number_salary%',
                 'report_common.%ac_quals_salary%',
                 'default(report_per_diem.%contact%, "")',
                 'default(report_per_diem.%contact_phone%, "")',
                 'default(report_per_diem.%contact_email%, "")',
                 'default(report_per_diem.%contact_department%, "")',
                 'salary.%crew_excluded%',
                 'report_per_diem.%per_diem_home_currency%')


TRIP_ENTITLED = 0
TRIP_TIME = 1
TRIP_TIME_TAX = 2
TRIP_PER_DIEM_ESTIMATE = 3
TRIP_PER_DIEM_TOTAL = 4
TRIP_COMPENSATION_UNIT = 5
TRIP_COUNTRY = 6
TRIP_START_UTC = 7
TRIP_START_UTC_TAX = 8
TRIP_END_UTC = 9
TRIP_END_UTC_TAX = 10
TRIP_INTERNATIONAL = 11
TRIP_HAS_INTERNATIONAL_STOP_TAX = 12
TRIP_LAYOVER = 13
TRIP_LAYOVER_TAX_DEDUCT_NO = 14
TRIP_COURSE_PER_DIEM = 15
TRIP_NUM_LAYOVERS = 16
TRIP_END_LOCAL = 17
TRIP_ACTUAL_START_LOCAL = 18
TRIP_ACTUAL_END_LOCAL = 19
TRIP_START_DAY_TAX_SKS = 20
TRIP_TAX_DEDUCTABLE_SKS = 21
TRIP_TAX_DEDUCT_DOMESTIC = 22
TRIP_TAX_DEDUCT_DOMESTIC_LOW1 = 23
TRIP_TAX_DEDUCT_DOMESTIC_LOW2 = 24
TRIP_TAX_DEDUCT_DOMESTIC_LOW3 = 25
TRIP_PER_DIEM_EXTRA = 26
TRIP_PER_DIEM_EXTRA_START_TIMES = 27
TRIP_PER_DIEM_EXTRA_END_TIMES = 28
TRIP_PER_DIEM_EXTRA_COMPENSATION = 29
TRIP_PER_DIEM_EXTRA_CURRENCY = 30
TRIP_PER_DIEM_EXTRA_EXCHANGE_RATE = 31
TRIP_PER_DIEM_EXTRA_EXCHANGE_UNIT = 32
TRIP_PER_DIEM_EXTRA_TYPE = 33
TRIP_HAS_AGMT_GROUP_QA = 34
TRIP_START_DAY_TAX_SKN = 35
TRIP_END_DAY_TAX_SKN = 36
TRIP_HAS_AGMT_GROUP_SKN_CC = 37
TRIP_VALUES = ('report_per_diem.%trip_per_diem_entitled%',
               'report_per_diem.%trip_per_diem_time%',
               'report_per_diem.%trip_per_diem_time_tax%',
               'report_per_diem.%trip_per_diem_estimated%',
               'trip.%per_diem_total_at_date%(salary.%salary_month_start_p%)',
               'report_per_diem.%per_diem_price_unit%',
               'report_per_diem.%country%',
               'report_per_diem.%trip_per_diem_start_UTC%',
               'report_per_diem.%trip_per_diem_start_UTC_tax%',
               'report_per_diem.%trip_per_diem_end_UTC%',
               'report_per_diem.%trip_per_diem_end_UTC_tax%',
               'report_per_diem.%trip_is_international%',
               'report_per_diem.%trip_has_international_stop_tax%',
               'report_per_diem.%trip_has_layover%',
               'report_per_diem.%trip_per_diem_layover_tax_deduct_no%',
               'report_per_diem.%trip_course_per_diem%',
               'report_per_diem.%trip_num_layovers%',
               'report_per_diem.%trip_per_diem_end_local%',
               'report_per_diem.%trip_actual_start_local%',
               'report_per_diem.%trip_actual_end_local%',
               'report_per_diem.%trip_start_day_tax_sks%',
               'report_per_diem.%trip_tax_deductable_sks%',
               'report_per_diem.%tax_deduct_domestic%',
               'report_per_diem.%tax_deduct_domestic_low_1%',
               'report_per_diem.%tax_deduct_domestic_low_2%',
               'report_per_diem.%tax_deduct_domestic_low_3%',
               'report_per_diem.%trip_per_diem_extra%',
               'report_per_diem.%trip_per_diem_extra_start_times%',
               'report_per_diem.%trip_per_diem_extra_end_times%',
               'report_per_diem.%trip_per_diem_extra_compensation%',
               'report_per_diem.%trip_per_diem_extra_currency%',
               'report_per_diem.%trip_per_diem_extra_exchange_rate%',
               'report_per_diem.%trip_per_diem_extra_exchange_unit%',
               'report_per_diem.%trip_per_diem_extra_type%',
               'crew.%has_agmt_group_qa_at_date%(salary.%salary_month_start_p%)',
               'report_per_diem.%trip_start_day_tax_skn%',
               'report_per_diem.%trip_end_day_tax_skn%',
               'crew.%has_agmt_group_skn_cc_at_date%(salary.%salary_month_start_p%)')

DUTY_PER_DIEM_ALLOCATED = 0
DUTY_PER_DIEM_REST_TIME = 1
DUTY_ACTUAL_REST_TIME = 2
DUTY_PER_DIEM_START_LT = 3
DUTY_PER_DIEM_END_LT = 4
DUTY_PER_DIEM_EXTENDED = 5
DUTY_PER_DIEM_EXTENDED_CODE = 6
DUTY_PER_DIEM_EXTENDED_COMPENSATION = 7
DUTY_PER_DIEM_EXTENDED_CURRENCY = 8
DUTY_PER_DIEM_EXTENDED_EXCHANGE_RATE = 9
DUTY_PER_DIEM_EXTENDED_EXCHANGE_UNIT = 10
DUTY_VALUES = ('report_per_diem.%duty_per_diem_duty_amount%',
               'report_per_diem.%duty_rest_time_per_diem%',
               'report_per_diem.%duty_rest_time_actual%',
               'report_per_diem.%duty_per_diem_start_lt%',
               'report_per_diem.%duty_per_diem_end_lt%',
               'report_per_diem.%duty_per_diem_extended%',
               'report_per_diem.%duty_per_diem_extended_code%',
               'report_per_diem.%duty_per_diem_extended_compensation%',
               'report_per_diem.%duty_per_diem_extended_currency%',
               'report_per_diem.%duty_per_diem_extended_exchange_rate%',
               'report_per_diem.%duty_per_diem_extended_exchange_unit%')

LEG_START_STATION = 0
LEG_END_STATION = 1
LEG_START_UTC = 2
LEG_END_UTC = 3
LEG_PER_DIEM_ALLOCATED = 4
LEG_FLIGHT_NAME = 5
LEG_PER_DIEM_STOP_TIME = 6
LEG_ACTUAL_STOP_TIME = 7
LEG_STOP_COUNTRY = 8
LEG_COMPENSATION_PER_DIEM = 9
LEG_EXCHANGE_RATE = 10
LEG_EXCHANGE_UNIT = 11
LEG_CURRENCY = 12
LEG_TAX_DEDUCT = 13
LEG_MEAL_REDUCTION = 14
LEG_MEAL_REDUCTION_AMOUNT = 15
LEG_MEAL_REDUCTION_EXCHANGE_RATE = 16
LEG_MEAL_REDUCTION_EXCHANGE_UNIT = 17
LEG_STOP_START_DAY_LT = 18
LEG_STOP_END_DAY_LT = 19
LEG_FIRST_DAY_STOP_TIME_TAX_SKS = 20
LEG_LAST_DAY_STOP_TIME_TAX_SKS = 21
LEG_IS_LAST_INTL_PERIOD_TAX = 22
LEG_INTL_PERIOD_IS_INTL_TAX = 23
LEG_HAS_AGMT_GROUP_QA = 24
LEG_VALUES = ('report_per_diem.%leg_start_station%',
              'report_per_diem.%leg_end_station%',
              'report_per_diem.%leg_actual_start_UTC%',
              'report_per_diem.%leg_actual_end_UTC%',
              'leg.%per_diem_amount_at_date%(salary.%salary_month_start_p%)',
              'report_per_diem.%leg_flight_name%',
              'report_per_diem.%leg_stop_time_per_diem%',
              'report_per_diem.%leg_stop_time_actual%',
              'report_per_diem.%leg_stop_country%',
              'report_per_diem.%per_diem_compensation_at_date%(salary.%salary_month_start_p%)',
              'report_per_diem.%per_diem_exchange_rate%',
              'report_per_diem.%per_diem_exchange_unit%',
              'report_per_diem.%per_diem_stop_currency%',
              'report_per_diem.%per_diem_tax_deduct%',
              'report_per_diem.%leg_per_diem_meal_reduction%',
              'report_per_diem.%meal_reduction_amount%',
              'report_per_diem.%meal_reduction_exchange_rate%',
              'report_per_diem.%meal_reduction_exchange_unit%',
              'report_per_diem.%leg_stop_start_day_lt%',
              'report_per_diem.%leg_stop_end_day_lt%',
              'report_per_diem.%first_day_stop_time_tax_sks%',
              'report_per_diem.%last_day_stop_time_tax_sks%',
              'report_per_diem.%leg_is_last_in_intl_period_tax%',
              'report_per_diem.%intl_period_is_international_tax%',
              'crew.%has_agmt_group_qa_at_date%(salary.%salary_month_start_p%)')


class PerDiemRosterManager:
    """
    A class that creates and holds PerDiemRosters.
    """

    def __init__(self, context, iterator='iterators.roster_set', crewlist=None):
        self.context = context
        self.roster_iterator = iterator
        self.crewlist = crewlist
        self.tripManager = PerDiemTripManager(context)

    def getPerDiemRosters(self):

        perDiemRosters = []
        if self.crewlist:
            try:
                import Cui
                Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, self.crewlist)
                Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiScriptBuffer)
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
                self.context = "default_context"
            except:
                # CuiSetCurrentArea may fail (e.g. in report workers).
                # No real problem, just a bit slower. It is filtered later on anyway.
                pass
        tripIterator = r.iter('iterators.trip_set',
                              ('report_per_diem.%trip_per_diem_entitled%',
                               'report_per_diem.%in_salary_period%'))
        tripSequence = self.tripManager.getTripSequence(tripIterator)
        rosterSequence = self.getRosterSequence(tripSequence)

        # if instance of carmstd.rave.Context  else is string (or something else)
        rosters, = self.context.eval(rosterSequence) if hasattr(self.context, "eval") else \
            r.eval(self.context, rosterSequence)

        for rosterItem in rosters:
            if self.crewlist is None or rosterItem[ROSTER_CREW_ID + 1] in self.crewlist:
                perDiemRosters.append(self.createRoster(rosterItem))

        return perDiemRosters

    def getRosterSequence(self, tripSequence):

        return r.foreach(self.roster_iterator,
                         *(ROSTER_VALUES + (tripSequence,)))

    def createRoster(self, rosterItem):

        roster = rosterItem[1:-1]

        perDiemRoster = PerDiemRoster()
        perDiemRoster.crewId = roster[ROSTER_CREW_ID]
        perDiemRoster.empNo = roster[ROSTER_CREW_EMPNO]
        perDiemRoster.firstName = roster[ROSTER_FIRST_NAME]
        perDiemRoster.lastName = roster[ROSTER_LAST_NAME]
        perDiemRoster.homebase = roster[ROSTER_HOMEBASE]
        perDiemRoster.rank = roster[ROSTER_RANK]
        perDiemRoster.mainFunc = roster[ROSTER_MAIN_FUNC]
        perDiemRoster.department = roster[ROSTER_DEPARTMENT]
        perDiemRoster.acQuals = roster[ROSTER_AC_QUALS]
        perDiemRoster.contact = roster[ROSTER_CONTACT]
        perDiemRoster.contactPhone = roster[ROSTER_CONTACT_PHONE]
        perDiemRoster.contactEmail = roster[ROSTER_CONTACT_EMAIL]
        perDiemRoster.contactDepartment = roster[ROSTER_CONTACT_DEPARTMENT]
        perDiemRoster.excluded = roster[ROSTER_EXCLUDED]
        perDiemRoster.homeCurrency = roster[ROSTER_HOME_CURRENCY]
        perDiemRoster.trips = []
        
        trips = rosterItem[-1]
        for tripItem in trips:
            perDiemRoster.trips.append(self.tripManager.createTrip(tripItem))

        return perDiemRoster
        

class PerDiemTripManager:
    """
    A class that creates and holds PerDiemTrips.
    """

    def __init__(self, context):
        self.context = context

    def getPerDiemTrips(self):

        perDiemTrips = []
        tripIterator = r.iter('iterators.trip_set',
                              ('report_per_diem.%trip_per_diem_entitled%'))
        tripSequence = self.getTripSequence(tripIterator)
        trips, = r.eval(self.context, tripSequence)
        for tripItem in trips:
            perDiemTrips.append(self.createTrip(tripItem))
          
        return perDiemTrips
    
    def getTripSequence(self, tripIterator):


        leg = r.foreach(r.iter('iterators.leg_set', where=('report_per_diem.%leg_is_per_diem%')), *LEG_VALUES)
        duty = r.foreach('iterators.duty_set', *(DUTY_VALUES + (leg,)))
        trip = r.foreach(tripIterator, *(TRIP_VALUES + (duty,)))
        return trip
    

    def createTrip(self, tripItem):
        trip = tripItem[1:-1]
        duties = tripItem[-1]

        perDiemTrip = PerDiemTrip()
        perDiemTrip.perDiemTrip = trip[TRIP_ENTITLED]
        perDiemTrip.tripTime = trip[TRIP_TIME]
        perDiemTrip.tripTimeTax = trip[TRIP_TIME_TAX]
        perDiemTrip.estimatedPerDiem = trip[TRIP_PER_DIEM_ESTIMATE] / 4.0
        if trip[TRIP_HAS_AGMT_GROUP_QA]:
            perDiemTrip.actualPerDiem = trip[TRIP_PER_DIEM_TOTAL] / (24.0 * 60.0)
        else:    
            perDiemTrip.actualPerDiem = trip[TRIP_PER_DIEM_TOTAL] / 4.0
        perDiemTrip.hasAgmtGroupQa = trip[TRIP_HAS_AGMT_GROUP_QA]
        perDiemTrip.country = trip[TRIP_COUNTRY]
        perDiemTrip.startUTC = trip[TRIP_START_UTC]
        perDiemTrip.startUTCtax = trip[TRIP_START_UTC_TAX]
        perDiemTrip.endUTC = trip[TRIP_END_UTC]
        perDiemTrip.endUTCtax = trip[TRIP_END_UTC_TAX]
        perDiemTrip.international = trip[TRIP_INTERNATIONAL]
        perDiemTrip.hasInternationalStopTax = trip[TRIP_HAS_INTERNATIONAL_STOP_TAX]
        perDiemTrip.layover = trip[TRIP_LAYOVER]
        perDiemTrip.layoverTaxDeductNo = trip[TRIP_LAYOVER_TAX_DEDUCT_NO]
        perDiemTrip.coursePerDiem = trip[TRIP_COURSE_PER_DIEM]
        perDiemTrip.numLayovers = trip[TRIP_NUM_LAYOVERS]
        perDiemTrip.endLocal = trip[TRIP_END_LOCAL]
        perDiemTrip.actualStartLocal = trip[TRIP_ACTUAL_START_LOCAL]
        perDiemTrip.actualEndLocal = trip[TRIP_ACTUAL_END_LOCAL]
        perDiemTrip.startDayTaxSKS = trip[TRIP_START_DAY_TAX_SKS]
        perDiemTrip.isTaxDeductableSKS = trip[TRIP_TAX_DEDUCTABLE_SKS]
        perDiemTrip.defaultTaxDeductDomestic = trip[TRIP_TAX_DEDUCT_DOMESTIC]
        perDiemTrip.defaultTaxDeductDomesticLow1 = trip[TRIP_TAX_DEDUCT_DOMESTIC_LOW1]
        perDiemTrip.defaultTaxDeductDomesticLow2 = trip[TRIP_TAX_DEDUCT_DOMESTIC_LOW2]
        perDiemTrip.defaultTaxDeductDomesticLow3 = trip[TRIP_TAX_DEDUCT_DOMESTIC_LOW3]
        perDiemTrip.startDayTaxSKN = trip[TRIP_START_DAY_TAX_SKN]
        perDiemTrip.endDayTaxSKN = trip[TRIP_END_DAY_TAX_SKN]
        perDiemTrip.hasAgmtGroupSKNCC = trip[TRIP_HAS_AGMT_GROUP_SKN_CC]

        if not trip[TRIP_PER_DIEM_EXTRA] == '':
            perDiemTrip.perDiemExtra = [int(perDiemExtra) / 4.0 for perDiemExtra in trip[TRIP_PER_DIEM_EXTRA].split(',')]
        else:
            perDiemTrip.perDiemExtra = []

        perDiemTrip.perDiemExtraStartTime = [AbsTime(starttime) for starttime in trip[TRIP_PER_DIEM_EXTRA_START_TIMES].split(',')]
        perDiemTrip.perDiemExtraEndTime = [AbsTime(endtime) for endtime in trip[TRIP_PER_DIEM_EXTRA_END_TIMES].split(',')]
        perDiemTrip.perDiemExtraCompensation = [int(compensation) / 100 for compensation in trip[TRIP_PER_DIEM_EXTRA_COMPENSATION].split(',')]
        perDiemTrip.perDiemExtraCurrency = trip[TRIP_PER_DIEM_EXTRA_CURRENCY].split(',')
        perDiemTrip.perDiemExtraExchangeRate = [float(rate) for rate in trip[TRIP_PER_DIEM_EXTRA_EXCHANGE_RATE].split(',')]
        perDiemTrip.perDiemExtraExchangeUnit = [int(unit) for unit in trip[TRIP_PER_DIEM_EXTRA_EXCHANGE_UNIT].split(',')]
        perDiemTrip.perDiemExtraType = trip[TRIP_PER_DIEM_EXTRA_TYPE].split(',')

        perDiemTrip.legs = []

        for dutyItem in duties:
            duty = dutyItem[1:-1]
            legs = dutyItem[-1]

            duty_start_day = None
            EXday = None

            if duty[DUTY_PER_DIEM_EXTENDED] > 0:
                for day in xrange(len(perDiemTrip.perDiemExtraStartTime)):
                    if perDiemTrip.perDiemExtraStartTime[day] <= duty[DUTY_PER_DIEM_START_LT] and perDiemTrip.perDiemExtraEndTime[day] >= duty[DUTY_PER_DIEM_START_LT]:
                        duty_start_day = day
                    if perDiemTrip.perDiemExtraStartTime[day] <= duty[DUTY_PER_DIEM_END_LT] and perDiemTrip.perDiemExtraEndTime[day] >= duty[DUTY_PER_DIEM_END_LT]:
                        # If more than 2 extended duties in month, take the largest per diem extra. If equal, use PH.
                        if duty[DUTY_PER_DIEM_EXTENDED] > perDiemTrip.perDiemExtra[day]:
                            EXday = day
                        elif duty[DUTY_PER_DIEM_EXTENDED] > perDiemTrip.perDiemExtra[duty_start_day]:
                            EXday = duty_start_day

                        if EXday:
                            perDiemTrip.perDiemExtra[EXday] = duty[DUTY_PER_DIEM_EXTENDED] / 4.0
                            perDiemTrip.perDiemExtraType[EXday] = duty[DUTY_PER_DIEM_EXTENDED_CODE]
                            perDiemTrip.perDiemExtraCompensation[EXday] = duty[DUTY_PER_DIEM_EXTENDED_COMPENSATION] / 100
                            perDiemTrip.perDiemExtraCurrency[EXday] = duty[DUTY_PER_DIEM_EXTENDED_CURRENCY]
                            perDiemTrip.perDiemExtraExchangeRate[EXday] = duty[DUTY_PER_DIEM_EXTENDED_EXCHANGE_RATE]
                            perDiemTrip.perDiemExtraExchangeUnit[EXday] = duty[DUTY_PER_DIEM_EXTENDED_EXCHANGE_UNIT]

            for legItem in legs:
                counter = legItem[0].index
                legCount = len(legs)
                leg = legItem[1:]
                
                perDiemLeg = PerDiemLeg()
                perDiemLeg.flight = leg[LEG_FLIGHT_NAME]
                perDiemLeg.startStation = leg[LEG_START_STATION]
                perDiemLeg.endStation = leg[LEG_END_STATION]
                perDiemLeg.startUTC = leg[LEG_START_UTC]
                perDiemLeg.endUTC = leg[LEG_END_UTC]
                perDiemLeg.stopCountry = leg[LEG_STOP_COUNTRY]
                if leg[LEG_COMPENSATION_PER_DIEM] == None:
                    perDiemLeg.compensationPerDiem = 0
                else:
                    perDiemLeg.compensationPerDiem = (
                        float(leg[LEG_COMPENSATION_PER_DIEM])
                         / trip[TRIP_COMPENSATION_UNIT])
                perDiemLeg.exchangeRate = (float(leg[LEG_EXCHANGE_RATE])
                                           / leg[LEG_EXCHANGE_UNIT])
                perDiemLeg.currency = leg[LEG_CURRENCY]
                perDiemLeg.taxDeduct = leg[LEG_TAX_DEDUCT]
                #Last leg of duty has per diem for the duty stop
                if counter < legCount:
                    if leg[LEG_PER_DIEM_ALLOCATED]:
                        if leg[LEG_HAS_AGMT_GROUP_QA]:
                            perDiemLeg.allocatedPerDiem = leg[LEG_PER_DIEM_ALLOCATED] / (24.0 * 60.0)
                        else:
                            perDiemLeg.allocatedPerDiem = (
                                            leg[LEG_PER_DIEM_ALLOCATED] / 4.0)
                        

                    else:
                        perDiemLeg.allocatedPerDiem = 0
                    perDiemLeg.perDiemStopTime = leg[LEG_PER_DIEM_STOP_TIME]
                    perDiemLeg.actualStopTime = leg[LEG_ACTUAL_STOP_TIME]
                else:
                    if leg[LEG_HAS_AGMT_GROUP_QA]:
                        perDiemLeg.allocatedPerDiem = leg[LEG_PER_DIEM_ALLOCATED] / (24.0 * 60.0) if leg[LEG_PER_DIEM_ALLOCATED] else 0
                    else:                        
                        perDiemLeg.allocatedPerDiem = (
                        duty[DUTY_PER_DIEM_ALLOCATED] / 4.0)

                    perDiemLeg.perDiemStopTime = duty[DUTY_PER_DIEM_REST_TIME]
                    perDiemLeg.actualStopTime = duty[DUTY_ACTUAL_REST_TIME]
                    if not perDiemLeg.perDiemStopTime:
                        perDiemLeg.perDiemStopTime = RelTime(0)
                    if not perDiemLeg.actualStopTime:
                        perDiemLeg.actualStopTime = RelTime(0)

                perDiemLeg.mealReduction = leg[LEG_MEAL_REDUCTION]
                perDiemLeg.mealReductionAmount = 0
                perDiemLeg.mealReductionExchangeRate = 0
                if perDiemLeg.mealReduction:
                    perDiemLeg.mealReductionAmount = (
                        float(leg[LEG_MEAL_REDUCTION_AMOUNT])
                        / trip[TRIP_COMPENSATION_UNIT])
                    perDiemLeg.mealReductionExchangeRate = (
                        float(leg[LEG_MEAL_REDUCTION_EXCHANGE_RATE])
                        / leg[LEG_MEAL_REDUCTION_EXCHANGE_UNIT])

                perDiemLeg.stopStartDayLocal = leg[LEG_STOP_START_DAY_LT]
                perDiemLeg.stopEndDayLocal = leg[LEG_STOP_END_DAY_LT]
                perDiemLeg.firstDayStopTimeTaxSKS = leg[
                    LEG_FIRST_DAY_STOP_TIME_TAX_SKS]
                perDiemLeg.lastDayStopTimeTaxSKS = leg[
                    LEG_LAST_DAY_STOP_TIME_TAX_SKS]
                perDiemLeg.isLastInIntlPeriod = leg[LEG_IS_LAST_INTL_PERIOD_TAX]
                perDiemLeg.isIntlPeriod = leg[LEG_INTL_PERIOD_IS_INTL_TAX]
                perDiemLeg.hasAgmtGroupQa = leg[LEG_HAS_AGMT_GROUP_QA]
                perDiemTrip.legs.append(perDiemLeg)

        return perDiemTrip

        
class PerDiemRoster(DataClass):
    """
    A Roster for Per Diem evaluation.
    """

    def __init__(self):
        crewId = None #string
        empNo = None #string
        firstName = None #string
        lastName = None #string
        homebase = None #string
        rank = None #string
        mainFunc = None #string
        department = None #string
        acQuals = None #string
        contact = None #string
        contactPhone = None #string
        contactEmail = None #string
        contactDepartment = None #string
        trips = [] #list of PerDiemTrips
        excluded = False
        homeCurrency = None #string

    def getPerDiemCompensation(self):
        """
        Total per diem amount.
        """
        total = 0
        for trip in self.trips:
            total += trip.getCompensationSumHomeCurrency()       
        return round(total / 100, 2)
        
    def getPerDiemCompensationWithoutTax(self):
        """
        Total tax deductable amount of per diem.
        """
        total = 0
        for trip in self.trips:
            total += trip.getTaxDeduct()
        return round(total / 100, 2)

    def getPerDiemCompensationForTax(self):
        """
        Per Diem for taxation for all trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__all)

    def getMealReduction(self):
        """
        Total meal reduction for crew.
        """
        total = 0
        for trip in self.trips:
            total += trip.getMealReductionSumHomeCurrency()
        
        return round(total / 100, 2)

    def getPerDiemForTaxDomesticNO(self):
        """
        Per Diem for taxation for Norwegian crew domestic trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__isDomesticNO)

    def getPerDiemForTaxOneDayNO(self):
        """
        Per Diem for taxation for Norwegian crew one day trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__isOneDayNO)
        
    def getPerDiemForTaxInternationalSKS(self):
        """
        Per Diem for taxation for Swedish crew international trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__isInternationalSKS)

    def getPerDiemForTaxDomesticSKS(self):
        """
        Per Diem for taxation for Swedish crew domestic trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__isDomesticSKS)

    def getPerDiemForTaxOneDaySKS(self):
        """
        Per Diem for taxation for Swedish crew one day trips.
        """
        return self.__getPerDiemForTax(PerDiemRoster.__isOneDaySKS)
    
    def getPerDiemDaysTaxNO(self):
        days = 0
        for trip in self.trips:
            days += trip.getTripDaysTaxNorway()
        return int(days)

    def __all(trip):
        return True
    __all = staticmethod(__all)

    def __isDomesticNO(trip):
        return not PerDiemRoster.__isOneDayNO(trip)
    __isDomesticNO = staticmethod(__isDomesticNO)

    def __isOneDayNO(trip):
        return trip.tripTime <= RelTime(30, 0) and (not trip.layover or trip.hasInternationalStopTax)
    __isOneDayNO = staticmethod(__isOneDayNO)

    def __isInternationalSKS(trip):
        return trip.isTaxDeductableSKS and trip.international
    __isInternationalSKS = staticmethod(__isInternationalSKS)

    def __isDomesticSKS(trip):
        return trip.isTaxDeductableSKS and not trip.international
    __isDomesticSKS = staticmethod(__isDomesticSKS)

    def __isOneDaySKS(trip):
        return not trip.isTaxDeductableSKS
    __isOneDaySKS = staticmethod(__isOneDaySKS)

    def __getPerDiemForTax(self, func):
        """
        Returns Per diem for taxation for all trips which func is true.
        """
        beforeTax = 0
        taxDeduct = 0
        for trip in self.trips:
            if func(trip):
                beforeTax += trip.getCompensationSumHomeCurrency()
                taxDeduct += trip.getTaxDeduct()
        beforeTax = round(beforeTax, 2)
        taxDeduct = round(taxDeduct, 2)
        return round((max(beforeTax - taxDeduct, 0)) / 100, 2)
    
    def isExcludedFromSalaryFiles(self):
        return self.excluded


class PerDiemTrip(DataClass):
    """
    A Trip for Per Diem evaluation.
    """

    def __init__(self):
        self.perDiemTrip = None #boolean
        self.tripTime = None #RelTime
        self.tripTimeTax = None #RelTime
        self.estimatedPerDiem = None #float
        self.actualPerDiem = None #float
        self.country = None #string
        self.startUTC = None #AbsTime
        self.startUTCtax = None #AbsTime
        self.endUTC = None #AbsTime
        self.endUTCtax = None #AbsTime
        self.international = False #boolean
        self.hasInternationalStopTax = False #boolean
        self.layover = False #boolean
        self.layoverTaxDeductNo = False #boolean
        self.coursePerDiem = False #boolean        
        self.legsAdjusted = False #boolean
        self.numLayovers = None #integer
        self.endLocal = None #AbsTime
        self.actualStartLocal = None #AbsTime
        self.actualEndLocal = None #AbsTime
        self.startDayTaxSKS = None #AbsTime
        self.isTaxDeductableSKS = None #boolean
        self.defaultTaxDeductDomestic = None #integer
        self.defaultTaxDeductDomesticLow1 = None #integer
        self.defaultTaxDeductDomesticLow2 = None #integer
        self.defaultTaxDeductDomesticLow3 = None #integer
        self.startDayTaxSKN = None #AbsTime
        self.endDayTaxSKN = None #AbsTime
        self.legs = None #list of PerDiemLegs
        self.perDiemExtra = None # Comma separated string of integers (1/4)
        self.perDiemExtraStartTime = None # Comma separated string of AbsTimes
        self.perDiemExtraEndTime = None # Comma separated string of AbsTimes
        self.perDiemExtraCompensation = None # Comma separated string of Integers
        self.perDiemExtraCurrency = None # Comma separated string of Strings
        self.perDiemExtraExchangeRate = None # Comma separated string of Integers
        self.perDiemExtraExchangeUnit = None # Comma separated string of Integers
        self.perDiemExtraType = None # Comma separated string of Strings

    def getAdjustedLegs(self):
        self.adjustPerDiem()
        return self.legs

    def getCompensationSumHomeCurrency(self):
        sum = 0

        if not self.legsAdjusted:
            self.adjustPerDiem()
        for leg in self.legs:
            if not leg.isPerDiemExtra:
                sum += leg.getCompensationHomeCurrency()

        sum += self.getExtraCompensationSumHomeCurrency()

        return round(sum, 2)

    def getExtraCompensationSumHomeCurrency(self):
        sum = 0
        for i in xrange(len(self.perDiemExtra)):
            if self.perDiemExtraType[i] in ('EX', 'PH'):
                sum += self.perDiemExtra[i] * self.perDiemExtraCompensation[i] * self.perDiemExtraExchangeRate[i] / self.perDiemExtraExchangeUnit[i]
        return sum

    def getMealReductionSumHomeCurrency(self):
        sum = 0

        for leg in self.legs:
            sum += leg.getMealReductionHomeCurrency()

        return round(sum, 2)
        
    def sumAllocatedPerDiem(self):
        perDiemSum = 0
        for leg in self.legs:
            perDiemSum += leg.allocatedPerDiem
        return perDiemSum
            
    # This method will adjust the per diem for the legs of the trip
    # according to specification.
    def adjustPerDiem(self):
        if self.hasAgmtGroupQa :
            pass
        else:
            allocatedPerDiem = self.sumAllocatedPerDiem()
            
            #Per diem is adjusted if total entitled per diem differs from
            #the amount allocated to each stop
            while self.actualPerDiem != allocatedPerDiem:
                if self.actualPerDiem > allocatedPerDiem:
                    #We adjust with all extra per diem
                    adjust = self.actualPerDiem - allocatedPerDiem
                    leg = self.findForUpAdjust()
                else:
                    #We subtract with a quarter per diem
                    adjust = -0.25
                    leg = self.findForDownAdjust()
                leg.allocatedPerDiem += adjust
                allocatedPerDiem = self.sumAllocatedPerDiem()
            #We only need to adjust once if trip or legs doesn't change
            self.legsAdjusted = True



    #Finds the leg for upwards adjustment
    def findForUpAdjust(self):
        return reduce(PerDiemUtil.largestAndLongest, self.legs)
        
    #Finds the leg for downwards adjustment
    def findForDownAdjust(self):
        return reduce(PerDiemUtil.largestAndShortest, self.legs)

    #Gets tax deduct amount for the correct country
    def getTaxDeduct(self):
        if self.country == "DK":
            taxDeduct = self.getTaxDeductDenmark()
        elif self.country == "NO":
            taxDeduct = self.getTaxDeductNorway()
        elif self.country == "SE":
            taxDeduct = self.getTaxDeductSweden()
        else:
            taxDeduct = 0

        #Not more than compensation
        taxDeduct = min(self.getCompensationSumHomeCurrency(), taxDeduct)

        return round(taxDeduct, 2)

    #Calculates amount of tax deduction for per diem
    def getTaxDeductDenmark(self):
        result = 0
        for leg in self.legs:
            leg.clearTaxDeductCalcInfo()
        if self.tripTimeTax > RelTime(24, 0):            
            if self.hasAgmtGroupQa :
                result = self.getCompensationSumHomeCurrency()
            else:
              if not self.legsAdjusted:
                self.adjustPerDiem()
              nrOfDays = self.tripTimeTax / RelTime(1, 0, 0)
              for leg in self.legs:
                partOfTotalPerdiem = (float(leg.allocatedPerDiem) / self.actualPerDiem)
                result += partOfTotalPerdiem * nrOfDays * leg.taxDeduct
                if partOfTotalPerdiem * nrOfDays > 0:
                    leg.setTaxDeductCalcInfo(partOfTotalPerdiem * nrOfDays, leg.taxDeduct, None)                       
        return round(result, 2)
    
    def getTripDaysTaxNorwayBefore2019(self):
        if self.tripTimeTax >= RelTime(24, 0):
            (hours, days) = math.modf((self.tripTimeTax) / RelTime(24, 0))
            hours *= 24
            if hours >= 6:
                days += 1
            return days
        elif self.layoverTaxDeductNo:
            return 1
        else:
            return 0
                
    def getTripDaysTaxNorway(self):
        if self.startDayTaxSKN < AbsTime("1JAN2019"):
            return self.getTripDaysTaxNorwayBefore2019()

        trip_time_tax = self.endDayTaxSKN - self.startDayTaxSKN - RelTime(24, 0)
        if trip_time_tax >= RelTime(24, 0):
            days = trip_time_tax / RelTime(24, 0)
            return days
        elif self.layoverTaxDeductNo:
            return 1
        else:
            return 0
                
    def getTaxDeductNorwayBefore2019(self):
        """
        Calculates tax deductable amount according Norwegian rules
        """
        print "getTaxDeductNorway"
        result = 0
        if not self.legsAdjusted:
            self.adjustPerDiem()
            
        for leg in self.legs:
            leg.clearTaxDeductCalcInfo()
        #print "Trip: ", str(self.startUTC),"-", str(self.endUTC), "   ", str(self.tripTimeTax)
        if self.tripTimeTax >= RelTime(24, 0):
            #print ">24h: "
            def handleMultipleLegs(legs, first, end):
                legs[end - 1].dispTaxDeductLast = True
                sum = 0
                
                if end == len(legs): # Last period of trip
                    length = self.endUTCtax - legs[first].startUTC
                elif first == 0:
                    length = legs[end].startUTC - self.startUTCtax
                else:
                    length = legs[end].startUTC - legs[first].startUTC
                    
                if legs[first].isIntlPeriod:
                    for leg in legs[first:end]:
                        sum += leg.getCompensationHomeCurrency()
                        leg.setTaxDeductCalcInfoAll(False, length)
                else:
                    if first == 0 and end == len(legs):
                        days = self.getTripDaysTaxNorway()
                        length = RelTime(24, 0) * days
                    else:
                        (hours, days) = math.modf(length / RelTime(24, 0))
                        if days < 0: return 0
                        if hours * 24 >= 6: days += 1
                        elif days < 1: return 0
                    taxDeduct = legs[end - 1].taxDeduct
                    sum = days * taxDeduct
                    ad = None
                    for leg in legs[first:end]:
                        legDate = AbsDate(leg.startUTC)
                        if (not ad or legDate > ad) and leg.allocatedPerDiem > 0:
                            #print leg.flight, leg.startStation, leg.endStation, leg.allocatedPerDiem
                            ad = legDate
                            d = min(days, 1)
                            leg.setTaxDeductCalcInfo(d, taxDeduct, True, length)
                            length = None
                            days -= d
                            if days <= 0: break
                    if days > 0: self.legs[end - 1].setTaxDeductCalcInfo(days, taxDeduct, True, length)
                return sum
            
            lasti = 0
            #print "Per diem tax NO"
            #print "Self=", repr(self.__dict__)
            #print "Trip days=", self.getTripDaysTaxNorway()
            #print '  ' + '  \n'.join(map(lambda x: repr(x.__dict__), self.legs))
            for i in range(len(self.legs)):
                if i > 0 and self.legs[i - 1].isLastInIntlPeriod and self.legs[lasti].isIntlPeriod != self.legs[i].isIntlPeriod:
                    result += handleMultipleLegs(self.legs, lasti, i)
                    lasti = i
            result += handleMultipleLegs(self.legs, lasti, len(self.legs))
            print result
            print "END Per diem tax NO"
                
        elif self.layoverTaxDeductNo: # 2A, 3: if at least 5:00 between 22-06 and stop, or covering all of 22-06
            #print "Is layover: "
            if self.hasInternationalStopTax:
                result = self.getCompensationSumHomeCurrency()
                for leg in self.legs: leg.setTaxDeductCalcInfoAll(False)
            else:
                #Only used for domestic trips, therefore last leg is used
                result = self.defaultTaxDeductDomestic
                self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomestic, True)
        else: # 2B
            #print "Is short: "
            leg = reduce(PerDiemUtil.longestStop, self.legs)
            
            STOP_SHORT = self.hasInternationalStopTax and RelTime(6, 0) or RelTime(5, 0)
            STOP_MEDIUM = RelTime(9, 0)
            STOP_LONG = RelTime(12, 0)
            
            #print self.defaultTaxDeductDomestic, self.defaultTaxDeductDomesticLow1, self.defaultTaxDeductDomesticLow2, self.defaultTaxDeductDomesticLow3
            if leg.actualStopTime >= STOP_LONG: # 2B3
                if self.hasInternationalStopTax:
                    result = self.getCompensationSumHomeCurrency()
                    self.legs[-1].setTaxDeductCalcInfo(1, self.getCompensationSumHomeCurrency(), False)
                else:
                    result = self.defaultTaxDeductDomesticLow1
                    self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow1, True)
            elif leg.actualStopTime > STOP_MEDIUM and not self.hasInternationalStopTax: # 2B2
                result = self.defaultTaxDeductDomesticLow2
                self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow2, True)
            elif leg.actualStopTime > STOP_SHORT:
                if self.hasInternationalStopTax:
                    self.legs[-1].setTaxDeductCalcInfo(2.0 / 3.0, self.getCompensationSumHomeCurrency(), False)
                    result = self.getCompensationSumHomeCurrency() * (2.0 / 3.0)
                else:
                    result = self.defaultTaxDeductDomesticLow3
                    self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow3, True)
            else:
                if self.hasInternationalStopTax:
                    self.legs[-1].setTaxDeductCalcInfo(0.5, self.getCompensationSumHomeCurrency(), False)
                    result = self.getCompensationSumHomeCurrency() * 0.5
                else:
                    result = 0

        return round(result, 2)

    def getTaxDeductNorway(self):
        """
        Calculates tax deductable amount according Norwegian rules
        """
        print "getTaxDeductNorway"
        if self.startDayTaxSKN < AbsTime("1JAN2019"):
            return self.getTaxDeductNorwayBefore2019()
            
        result = 0
        if not self.legsAdjusted:
            self.adjustPerDiem()
            
        for leg in self.legs:
            leg.clearTaxDeductCalcInfo()
        #print "Trip: ", str(self.startUTC),"-", str(self.endUTC), "   ", str(self.tripTimeTax)
        if self.tripTimeTax >= RelTime(24, 0):
            #print ">24h: "
            def handleMultipleLegs(legs, first, end):
                legs[end - 1].dispTaxDeductLast = True
                sum = 0
                
                if end == len(legs): # Last period of trip
                    length = self.endUTCtax - legs[first].startUTC
                elif first == 0:
                    length = legs[end].startUTC - self.startUTCtax
                else:
                    length = legs[end].startUTC - legs[first].startUTC
                    
                if first == 0 and end == len(legs):
                    days = self.getTripDaysTaxNorway()
                    length = RelTime(24, 0) * days
                else:
                    (hours, days) = math.modf(length / RelTime(24, 0))
                    if days < 0: return 0
                    if hours * 24 >= 6: days += 1
                    elif days < 1: return 0
                taxDeduct = legs[end - 1].taxDeduct
                sum = days * taxDeduct
                ad = None
                for leg in legs[first:end]:
                    legDate = AbsDate(leg.startUTC)
                    if (not ad or legDate > ad) and leg.allocatedPerDiem > 0:
                        #print leg.flight, leg.startStation, leg.endStation, leg.allocatedPerDiem
                        ad = legDate
                        d = min(days, 1)
                        leg.setTaxDeductCalcInfo(d, taxDeduct, True, length)
                        length = None
                        days -= d
                        if days <= 0: break
                if days > 0: self.legs[end - 1].setTaxDeductCalcInfo(days, taxDeduct, True, length)
                return sum
            
            #print "Per diem tax NO"
            #print "Self=", repr(self.__dict__)
            #print "Trip days=", self.getTripDaysTaxNorway()
            #print '  ' + '  \n'.join(map(lambda x: repr(x.__dict__), self.legs))
            result = handleMultipleLegs(self.legs, 0, len(self.legs))
            print result
            print "END Per diem tax NO"
                
        elif self.layoverTaxDeductNo: # 2A, 3: if at least 5:00 between 22-06 and stop, or covering all of 22-06
            #print "Is layover: "
            if self.hasInternationalStopTax:
                result = self.getCompensationSumHomeCurrency()
                for leg in self.legs: leg.setTaxDeductCalcInfoAll(False)
            else:
                #Only used for domestic trips, therefore last leg is used
                result = self.defaultTaxDeductDomestic
                self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomestic, True)
        else: # 2B
            #print "Is short: "
            leg = reduce(PerDiemUtil.longestStop, self.legs)
            
            STOP_SHORT = self.hasInternationalStopTax and RelTime(6, 0) or RelTime(5, 0)
            STOP_MEDIUM = RelTime(9, 0)
            STOP_LONG = RelTime(12, 0)
            
            #print self.defaultTaxDeductDomestic, self.defaultTaxDeductDomesticLow1, self.defaultTaxDeductDomesticLow2, self.defaultTaxDeductDomesticLow3
            if leg.actualStopTime >= STOP_LONG: # 2B3
                if self.hasInternationalStopTax:
                    result = self.getCompensationSumHomeCurrency()
                    self.legs[-1].setTaxDeductCalcInfo(1, self.getCompensationSumHomeCurrency(), False)
                else:
                    result = self.defaultTaxDeductDomesticLow1
                    self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow1, True)
            elif leg.actualStopTime > STOP_MEDIUM and not self.hasInternationalStopTax: # 2B2
                result = self.defaultTaxDeductDomesticLow2
                self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow2, True)
            elif leg.actualStopTime > STOP_SHORT:
                if self.hasInternationalStopTax:
                    self.legs[-1].setTaxDeductCalcInfo(2.0 / 3.0, self.getCompensationSumHomeCurrency(), False)
                    result = self.getCompensationSumHomeCurrency() * (2.0 / 3.0)
                else:
                    result = self.defaultTaxDeductDomesticLow3
                    self.legs[-1].setTaxDeductCalcInfo(1, self.defaultTaxDeductDomesticLow3, True)
            else:
                if self.hasInternationalStopTax:
                    self.legs[-1].setTaxDeductCalcInfo(0.5, self.getCompensationSumHomeCurrency(), False)
                    result = self.getCompensationSumHomeCurrency() * 0.5
                else:
                    result = 0

        return round(result, 2)

    def getTaxDeductSweden(self):
        """
        Calculates tax deductable amount according to Swedish rules
        """
        if not self.isTaxDeductableSKS:
            return 0.0
        
        start = AbsTime(int(self.actualStartLocal))
        start = start.day_floor()
        startTime = self.actualStartLocal.time_of_day()
        end = AbsTime(int(self.actualEndLocal))
        end = end.day_floor()
        endTime = self.actualEndLocal.time_of_day()

        result = 0.0
        isNightTaxDeduct = False
        prevTaxDeduct = self.defaultTaxDeductDomestic
        prevLeg = self.legs[0]
        dayCounter = AbsTime(int(start))
        for leg in self.legs:
            leg.clearTaxDeductCalcInfo()
        while dayCounter <= end:
            factor = 1.0
            # First day in trip
            if dayCounter == start:
                # Half per diem if trip starts from 12:00 and forward
                if startTime >= RelTime(12, 0):
                    factor = 0.5
            # Last day in trip
            if dayCounter == end:
                # No per diem if trip ends before 04:30   
                if endTime < RelTime(4, 30):
                    factor = 0.0
                # Swedish Night tax deduct if trip ends between 04:30 and 06:00
                elif endTime <= RelTime(6, 0):
                    factor = 0.5
                    isNightTaxDeduct = True
                # Half per diem tax if trip end between 06:00 and 19:00
                elif endTime <= RelTime(19, 0):
                    factor = 0.5

            # Get legs in day
            legs = [leg for leg in self.legs if (leg.stopStartDayLocal == dayCounter) or\
                    (not leg.stopEndDayLocal is None and (leg.stopEndDayLocal == dayCounter))]
            
            #  no leg
            if len(legs) == 0 or isNightTaxDeduct:
                if (dayCounter == start) or (dayCounter == end):
                    # if its first day or last day, and its a day without stop, 
                    # is allocated to Sweden
                    taxDeduct = self.defaultTaxDeductDomestic
                    if dayCounter == end:
                        leg = self.legs[-1]
                    else:
                        legs = [leg for leg in self.legs if leg.stopStartDayLocal == dayCounter]
                        if len(legs) == 0: legs = [leg for leg in self.legs if leg.dispTaxDeductFactor == None]
                        if len(legs) > 0: leg = legs[0]
                        else: leg = None
                    if leg: leg.setTaxDeductCalcInfo(factor, taxDeduct, not self.international)
                else:
                    # Get the previous leg stop country, as its a day without legs 
                    # in the middle of the trip
                    taxDeduct = prevTaxDeduct
                    prevLeg.dispTaxDeductAmount = taxDeduct
                    prevLeg.setTaxDeductCalcInfo(factor, taxDeduct, not self.international)
            else:
                leg = reduce(PerDiemUtil.longestStopTaxSE, legs)
                taxDeduct = leg.taxDeduct
                leg.dispTaxDeductAmount = taxDeduct
                leg.setTaxDeductCalcInfo(factor, taxDeduct, not self.international)
                prevTaxDeduct = taxDeduct
                prevLeg = leg
                
            result += factor * taxDeduct
            dayCounter = dayCounter.adddays(1)
        
        return round(result, 2)

    def getLegsWithPerDiemExtra(self, legs):        
        legsWithPerDiemExtra = [leg for leg in legs]
        isSKNCC_perdiem_remove,= r.eval('system_db_parameters.%%k20_skn_cc_no_ph_perdiem_valid%%(%s)' % self.startUTC)
        for i in xrange(len(self.perDiemExtraType)):
            if self.hasAgmtGroupQa :
                pass
            elif isSKNCC_perdiem_remove and self.hasAgmtGroupSKNCC :
                pass
            else :
               if self.perDiemExtraType[i] in ('EX', 'PH'):
                    perDiemExtraLeg = PerDiemLeg()
                    perDiemExtraLeg.isPerDiemExtra = True
    
                    perDiemExtraLeg.startUTC = self.perDiemExtraStartTime[i]
                    perDiemExtraLeg.endUTC = self.perDiemExtraEndTime[i]
                    perDiemExtraLeg.perDiemStopTime = perDiemExtraLeg.endUTC - perDiemExtraLeg.startUTC
                    perDiemExtraLeg.startStation = self.perDiemExtraType[i]
                    perDiemExtraLeg.allocatedPerDiem = self.perDiemExtra[i]            
                    perDiemExtraLeg.compensationPerDiem = self.perDiemExtraCompensation[i]
                    perDiemExtraLeg.currency = self.perDiemExtraCurrency[i]
                    perDiemExtraLeg.exchangeRate = self.perDiemExtraExchangeRate[i] / self.perDiemExtraExchangeUnit[i]
    
                    legsWithPerDiemExtra.append(perDiemExtraLeg)
            legsWithPerDiemExtra = sorted(legsWithPerDiemExtra, key=lambda perDiemLeg: perDiemLeg.endUTC)
        
        return legsWithPerDiemExtra

class PerDiemLeg(DataClass):
    """
    A Leg for Per Diem evaluation.
    """

    def __init__(self):
        #These are used for displaying how Tax deduct was caclulated
        self.dispTaxDeductAmount = None
        self.dispTaxDeductFactor = None
        self.dispTaxDeductDomestic = None
        self.dispTaxDeductLast = False
        self.dispTaxDeductLength = None
        
        self.flight = None #string
        self.startStation = None #string
        self.endStation = None #string
        self.startUTC = None #AbsTime
        self.endUTC = None #AbsTime
        self.perDiemStopTime = None #RelTime
        self.actualStopTime = None #RelTime
        self.stopCountry = None #string
        self.allocatedPerDiem = None #float
        self.compensationPerDiem = None #float
        self.exchangeRate = None #float
        self.currency = None #string
        self.taxDeduct = None #float
        self.mealReduction = False #booelan
        self.mealReductionAmount = None #float
        self.mealReductionExchangeRate = None #float
        self.stopStartDayLocal = None #AbsTime
        self.stopEndDayLocal = None #AbsTime
        self.firstDayStopTimeTaxSKS = None #RelTime
        self.lastDayStopTimeTaxSKS = None #RelTime
        self.isLastInIntlPeriod = False
        self.isIntlPeriod = False
        self.isPerDiemExtra = False

    # Calculates the per diem compensation
    def getCompensation(self):
        return round(
            self.allocatedPerDiem * self.compensationPerDiem, 2)

    # Converts compensation to 'home' currency
    def getCompensationHomeCurrency(self):
        return round(
            self.getCompensation() * self.exchangeRate, 2)

    # Converts meal reduction to 'home' currency
    def getMealReductionHomeCurrency(self):
        return round(
            self.mealReductionAmount * self.mealReductionExchangeRate, 2)
        
    def setTaxDeductCalcInfoAll(self, isDomestic, length=None):
        self.dispTaxDeductDomestic = isDomestic
        if not self.allocatedPerDiem:
            self.clearTaxDeductCalcInfo()
        else:
            self.dispTaxDeductFactor = self.allocatedPerDiem
            self.dispTaxDeductAmount = self.compensationPerDiem * self.exchangeRate
            self.dispTaxDeductLength = length
        
    def setTaxDeductCalcInfo(self, factor, taxDeduct, isDomestic, length=None):
        self.dispTaxDeductDomestic = isDomestic
        if self.dispTaxDeductFactor == None:
            self.dispTaxDeductFactor = factor
        else:
            self.dispTaxDeductFactor += factor
            
        if self.dispTaxDeductAmount == None:
            self.dispTaxDeductAmount = taxDeduct
        elif self.dispTaxDeductAmount != taxDeduct:
            print "** Differing taxdeduct for %s %s-%s: %s vs %s" % (self.flight, self.startStation, self.endStation, self.dispTaxDeductAmount, taxDeduct)
            self.dispTaxDeductAmount = "(?)"
        self.dispTaxDeductLength = length
    def clearTaxDeductCalcInfo(self):
        self.dispTaxDeductAmount = None
        self.dispTaxDeductFactor = None
        self.dispTaxDeductDomestic = None
        self.dispTaxDeductLength = None


class PerDiemUtil:
    """
    Per Diem utility class.
    """

    # This method is implemented according to the per diem adjustment
    # specification when a leg is to be adjusted upwards.
    # Compares two legs and returns the leg with most per diem
    # If equal the longest and first is returned
    def largestAndLongest(leg1, leg2):
        if leg1.allocatedPerDiem < leg2.allocatedPerDiem:
            return leg2
        elif leg1.allocatedPerDiem > leg2.allocatedPerDiem:
            return leg1
        else:
            if leg1.perDiemStopTime < leg2.perDiemStopTime:
                return leg2
            else:
                return leg1
    # Make method static
    largestAndLongest = staticmethod(largestAndLongest)
    
            
    # This method is implemented according to the per diem adjustment
    # specification when a leg is to be adjusted downwards.
    # Compares two legs and returns the leg with most per diem
    # If equal the shortest and first is returned
    def largestAndShortest(leg1, leg2):
        if leg1.allocatedPerDiem < leg2.allocatedPerDiem:
            return leg2
        elif leg1.allocatedPerDiem > leg2.allocatedPerDiem:
            return leg1
        else:
            if leg1.perDiemStopTime > leg2.perDiemStopTime:
                return leg2
            else:
                return leg1
    # Make method static
    largestAndShortest = staticmethod(largestAndShortest)

    # Decides which leg has that has longest stop
    def longestStop(leg1, leg2):
        if leg1.actualStopTime >= leg2.actualStopTime:
            return leg1
        else:
            return leg2
    # Make method static
    longestStop = staticmethod(longestStop)
    
    # Decides which leg that has the "longest" stop according
    # to Swedish tax regulations
    def longestStopTaxSE(x, y):
        if y is None:
            return x
        elif x is None:
            return y
        
        if x.stopStartDayLocal == y.stopStartDayLocal:
            if x.firstDayStopTimeTaxSKS >= y.firstDayStopTimeTaxSKS:
                return x
        elif (y.stopEndDayLocal is not None
              and x.stopStartDayLocal == y.stopEndDayLocal):
            if x.firstDayStopTimeTaxSKS >= y.lastDayStopTimeTaxSKS:
                return x
        elif (x.stopEndDayLocal is not None
              and x.stopEndDayLocal == y.stopStartDayLocal):
            if x.lastDayStopTimeTaxSKS >= y.firstDayStopTimeTaxSKS:
                return x
        return y
    # Make method static
    longestStopTaxSE = staticmethod(longestStopTaxSE)
    
class AggregatedPerDiemTaxInfo:
    def __init__(self):
        # The month that this record represents
        self.period = "MMYY"
        # Total per diem
        self.perDiemTotal = 0
        # The part of total per diem reported for taxation
        self.perDiemForTaxation = 0
        # The part of total per diem that is without taxation
        self.perDiemWithoutTax = 0
        # True if record comes from current roster, false if it is precalculated
        self.fromRoster = False
        # Number of days of per diem (according to tax rules) in the period
        self.perDiemDays = 0


def getAggregatedPerDiemTax(context, iterator, firstdate, lastdate, useCurrentRoster, admcode, extsys, homebase, crewlist=None):
    """
    This function returns a tuple (rosters, perDiem),
       rosters - A list of crew information whose per diem is returned, sorted by employee nr
       perDiem - A dictionary keyed by crew id, each entry containing a list of
                 AggregatedPerDiemTaxInfo for each month in the period.
    The per diem data is taken from the salary_basic_data table for a matching PERDIEMTAX run, or
    from the current roster if in the planning period and useCurrentRoster=True.
    """
    #print "getAggregatedPerDiemTax(%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (str(context), str(iterator), str(firstdate), str(lastdate), str(useCurrentRoster), str(admcode), str(extsys), str(homebase), str(crewlist))
    R = r
    from tm import TM
    import salary.conf as conf
    perDiem = {}
    allrstrs = {}
    pstart = AbsTime(firstdate).month_floor()

    try:
        import carmstd.rave
        if isinstance(context, carmstd.rave.Context):
            pp_start = AbsTime(context.eval("fundamental.%pp_start%")[0])
            pp_end = AbsTime(context.eval("fundamental.%pp_end%")[0]).month_ceil()
        else:
            pp_start = AbsTime(R.eval(context, "fundamental.%pp_start%")[0])
            pp_end = AbsTime(R.eval(context, "fundamental.%pp_end%")[0]).month_ceil()
    except ImportError:
        pp_start = AbsTime(R.eval(context, "fundamental.%pp_start%")[0])
        pp_end = AbsTime(R.eval(context, "fundamental.%pp_end%")[0]).month_ceil()


    periods = []
    articles = None
    
    while True:
        y, m, _, _, _ = pstart.split()
        pend = (pstart + RelTime(1)).month_ceil()
        if pend > lastdate:
            break

        period = "%02d%02d" % (y % 100, m)
        periods.append(period)
        if not useCurrentRoster or (pstart < pp_start or pend > pp_end):
            #print " -- FROM DB"
            query = "(&(firstdate=%s)(lastdate=%s)(runtype=PERDIEMTAX)(admcode=%s)(extsys=%s))" % (pstart, pend, admcode, extsys)
            latestRun = None
            for run in TM.salary_run_id.search(query):
                if not latestRun or run.starttime > latestRun.starttime:
                    latestRun = run
            if latestRun:
                print "Found run", latestRun.runid, "for month", latestRun.firstdate

                if not articles:
                    #print "Building crew info cache..."
                    articles = {}
                    TM.loadTables(['salary_article', 'salary_admin_code'])
                    for art in TM.salary_article.search("(&(validfrom<=%s)(validto>%s)(extsys=%s))" % (pend, pstart, extsys)):
                        articles[art.extartid] = art.intartid
               
                r.param('salary.%salary_month_start_p%').setvalue(pstart)
                r.param('salary.%salary_month_end_p%').setvalue(pend)

                crews, = R.eval(context, R.foreach(iterator,
                                'report_common.%crew_firstname%', 'report_common.%crew_surname%',
                                'report_common.%crew_homebase_salary%', 'report_common.%employee_number_salary%',
                                'report_common.%crew_id%'))

                crewListMonthly = {}
                for crew in crews:
                    if len(crew) < 6: 
                        continue

                    crewListMonthly[crew[5]] = {'id':crew[5], 'empno':crew[4], 'first':crew[1], 'last':crew[2], 'base':crew[3]}
                
                print "----------Monthly crew list built with", len(crewListMonthly), "rows for period ", pstart, " to ", pend
 
                for data in TM.salary_basic_data.search("(runid=%d)" % latestRun.runid):
                    crewid = str(data.getRefI("crewid"))
                    scode = articles[data.extartid]
                    if not crewid in crewListMonthly:
                        continue
                    if not crewid in allrstrs:
                        allrstrs[crewid] = crewListMonthly[crewid]
                    if not crewid in perDiem: perDiem[crewid] = []
                    l = perDiem[crewid]
                    pd = None
                    for v in l:
                        if v.period == period: pd = v
                    if pd == None:
                        pd = AggregatedPerDiemTaxInfo()
                        l.append(pd)
                    pd.period = period
                    if scode == 'PERDIEM_TAX_DAY':
                        pd.perDiemDays = int(data.amount / 100.0)
                    elif scode == 'PERDIEM_SALDO':
                        pd.perDiemTotal = int(data.amount) / 100.0
                        pd.perDiemWithoutTax = pd.perDiemTotal - pd.perDiemForTaxation
                    elif scode == 'PERDIEM_TAX_DOMESTIC':
                        pd.perDiemForTaxation = int(data.amount) / 100.0
                        pd.perDiemWithoutTax = pd.perDiemTotal - pd.perDiemForTaxation
                    else:
                        print "Bad scode = ", scode
            else:
                print "Did not find run"
            
        else:
            #print " -- FROM ROSTER"
            
            R.param('salary.%salary_month_start_p%').setvalue(firstdate)
            R.param('salary.%salary_month_end_p%').setvalue(lastdate)
            
            try:
                old_salary_month_start = R.param(conf.startparam).value()
                R.param(conf.startparam).setvalue(pstart)
                old_salary_month_end = R.param(conf.endparam).value()
                R.param(conf.endparam).setvalue(pend)
                
                rosters = PerDiemRosterManager(context, iterator, crewlist).getPerDiemRosters()
                
                for roster in rosters:
                    if not roster.crewId in allrstrs or not allrstrs[roster.crewId]['base']:
                        allrstrs[roster.crewId] = {'id':roster.crewId, 'empno':roster.empNo, 'first':roster.firstName, 'last':roster.lastName, 'base':roster.homebase}
                    if roster.crewId not in perDiem:
                        perDiem[roster.crewId] = []
                    pd = AggregatedPerDiemTaxInfo()
                    pd.period = period
                    pd.fromRoster = True
                    pd.perDiemDays = roster.getPerDiemDaysTaxNO()
                    pd.perDiemTotal = roster.getPerDiemCompensation()
                    pd.perDiemForTaxation = roster.getPerDiemCompensationForTax()
                    pd.perDiemWithoutTax = roster.getPerDiemCompensationWithoutTax()
                    perDiem[roster.crewId].append(pd)                   
            finally:
                R.param(conf.startparam).setvalue(old_salary_month_start)
                R.param(conf.endparam).setvalue(old_salary_month_end)
        pstart = pend
    # Mark missing data
    for crewId in perDiem:
        v = perDiem[crewId]
        if len(v) < len(periods):
            for period in periods:
                if not period in (dt.period for dt in v):
                    pd = AggregatedPerDiemTaxInfo()
                    pd.period = period
                    v.append(pd)
        v.sort(cmp=lambda x, y: cmp(x.period, y.period))
    rosters = allrstrs.values()[:]
    rosters.sort(cmp=lambda x, y: cmp(x['empno'], y['empno']))
    
    return (rosters, perDiem)
    

def writeperdiemcalc(fd, crewlist):
    pdm = PerDiemRosterManager('default_context', crewlist=crewlist)
    for crew in pdm.getPerDiemRosters():
        fd.write("Crew %s (%s %s)  (%s / %s):\n" % (crew.crewId, crew.firstName, crew.lastName, crew.department, crew.mainFunc))
        if crew.isExcludedFromSalaryFiles():
            fd.write("  ** Is excluded from Per Diem salary file by manual filter **\n")
        fd.write("  Tax deductible: %10.2f\n" % (crew.getPerDiemCompensationWithoutTax()))
        fd.write("    For taxation: %10.2f\n" % (crew.getPerDiemCompensationForTax()))
        fd.write("  Total per diem: %10.2f\n" % (crew.getPerDiemCompensation()))
        fd.write("  Breakdown:\n")
        for trip in crew.trips:
            taxd_trip = trip.getTaxDeduct() # Calc this first to store debug info
            if trip.actualPerDiem <= 0 and taxd_trip <= 0: continue
            fd.write("  Trip %s-%s:\n" % (trip.startUTC, trip.endUTC))
            fd.write("    Flight         Compensation                   Tax-deduct\n")
            tripTaxDeductFactor = 0.0
            legsWithPerDiemExtra = trip.getLegsWithPerDiemExtra(trip.legs)
            for leg in legsWithPerDiemExtra:
                if leg.isPerDiemExtra:
                    fd.write("    %s %s          %s %6.2f =%9.2f\n" % (leg.startStation, str(leg.startUTC).split()[0], leg.currency, float(leg.getCompensation() / 100), float(leg.getCompensationHomeCurrency() / 100)))
                    continue
                writeNl = False
                if leg.allocatedPerDiem > 0:
                    currStr = round(leg.compensationPerDiem / 100, 2)
                    if currStr >= 10000 and currStr == int(currStr):
                        currStr = "%7d" % int(currStr)
                    else:
                        currStr = "%7.2f" % currStr
                    fd.write("    %4s %3s-%3s  %5.2f x %3s%s =%9.2f  " % (str(leg.flight[3:]).strip(), leg.startStation, leg.endStation, leg.allocatedPerDiem, leg.currency, currStr, round(leg.getCompensationHomeCurrency() / 100, 2)))
                    writeNl = True
                if leg.dispTaxDeductFactor <> None:
                    if not writeNl:
                        fd.write("    %4s %3s-%3s                                 " % (str(leg.flight[3:]).strip(), leg.startStation, leg.endStation))
                       
                    t = leg.dispTaxDeductAmount
                    tripTaxDeductFactor += leg.dispTaxDeductFactor
                    if type(t) == float or type(t) == int: t = "%8.2f" % round(t / 100, 2)
                    else: t = "%8s" % t
                    if isinstance(leg.dispTaxDeductAmount, str):
                        fd.write("  ??? x%s =     ???" % t)
                    else:
                        fd.write("%5.2f x%s =%8.2f" % (leg.dispTaxDeductFactor, t, round(leg.dispTaxDeductFactor * leg.dispTaxDeductAmount / 100, 2)))
                    if leg.dispTaxDeductLast:
                        fd.write("_")
                    else:
                        fd.write(" ")
                    if leg.dispTaxDeductDomestic == True:
                        fd.write("(d)")
                    elif leg.dispTaxDeductDomestic == False:
                        fd.write("(i)")
                    if leg.dispTaxDeductLength:
                        fd.write(" %s" % leg.dispTaxDeductLength)
                    writeNl = True
                if writeNl: fd.write("\n")
            fd.write("    TOTAL         %5.2f %23.2f %6.2f %19.2f\n" % (trip.actualPerDiem, round(trip.getCompensationSumHomeCurrency() / 100, 2), tripTaxDeductFactor, round(taxd_trip / 100, 2)))
            #fd.write(str(trip))
            pass

