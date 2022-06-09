'''
Created on 10 feb 2012

@author: sven.olsson

Modified on 12 Dec 2013

@author Agne Frisch

Conversion into class and addition of duty time save.
'''

import Cui
from tm import TM
import carmensystems.rave.api as R
import carmusr.tracking.DragDrop as DD
import carmusr.HelperFunctions as HF
import carmusr.Assign as Assign
import carmstd.rave as rave
import modelserver as M
from utils.performance import log

import carmstd.cfhExtensions as cfhExtensions
import carmensystems.studio.Tracking.OpenPlan as OpenPlan
from AbsTime import AbsTime
from RelTime import RelTime

class PrivatelyTrade:

    PT_TYPES  = {'OT_PART_7x24_FWD' : 0, 'OT_PART_7x24_BWD' : 4, 'OT_PART_CALENDARWEEK' : 8,
                 'OT_PART_1x24_FWD' : 12, 'OT_PART_1x24_BWD' : 16, 'OT_PART_DUTYPASS' : 20,
                 'OT_PART_LATE_CHECKOUT' : 24, 'OT_PART_PARTTIME_MONTH' : 28, 
                 'MT_PART_PARTTIME_CC_MONTH' : 32, 'MT_PART_PARTTIME_CC_3_MONTHS' : 36, 
                 'OT_PART_PARTTIME_CC_MONTH' : 40, 'OT_PART_PARTTIME_CC_3_MONTHS' : 44, 
                 'OT_PART_MONTH' : 48, 
                 'OT_PART_7_CALENDAR_DAYS' : 52, 
                 'DT_PART' : 56,
                 'OT_PART_LATE_CHECKOUT_FREEDAY' : 59, 'OT_PART_LATE_CHECKOUT_RESCHED' : 60, 'OT_PART_LATE_CHECKOUT_FREE_WEEKEND' : 61}

    PT_VALUES = ('report_overtime.%overtime_7x24_fwd_ot%',
                 'report_overtime.%overtime_7x24_fwd_start%',
                 'report_overtime.%overtime_7x24_fwd_end%',
                 'report_overtime.%overtime_7x24_fwd_duty%',
        
                 'report_overtime.%overtime_7x24_bwd_ot%',
                 'report_overtime.%overtime_7x24_bwd_start%',
                 'report_overtime.%overtime_7x24_bwd_end%',
                 'report_overtime.%overtime_7x24_bwd_duty%',
                
                 'report_overtime.%overtime_calendar_week_ot%',
                 'report_overtime.%overtime_calendar_week_start%',
                 'report_overtime.%overtime_calendar_week_end%',
                 'report_overtime.%overtime_calendar_week_duty%',
                
                 'report_overtime.%overtime_1x24_fwd_ot%',
                 'report_overtime.%overtime_1x24_fwd_start%',
                 'report_overtime.%overtime_1x24_fwd_end%',
                 'report_overtime.%overtime_1x24_fwd_duty%',
                
                 'report_overtime.%overtime_1x24_bwd_ot%',
                 'report_overtime.%overtime_1x24_bwd_start%',
                 'report_overtime.%overtime_1x24_bwd_end%',
                 'report_overtime.%overtime_1x24_bwd_duty%',
                
                 'report_overtime.%overtime_dutypass_ot%',
                 'report_overtime.%overtime_dutypass_start%',
                 'report_overtime.%overtime_dutypass_end%',
                 'report_overtime.%overtime_dutypass_duty%',
                 
                 'report_overtime.%overtime_late_checkout_ot%',
                 'report_overtime.%overtime_late_checkout_start%',
                 'report_overtime.%overtime_late_checkout_end%',
                 'report_overtime.%overtime_late_checkout_duty%',

                 # "Mertid"
                 'report_overtime.%overtime_part_time_month_ot%',
                 'report_overtime.%overtime_part_time_month_start%',
                 'report_overtime.%overtime_part_time_month_end%',
                 'report_overtime.%overtime_part_time_month_duty%',
                
                 # 1 month part time CC mertid
                 'report_overtime.%mertid_part_time_cc_one_month%',
                 'report_overtime.%mertid_part_time_cc_one_month_start%',
                 'report_overtime.%mertid_part_time_cc_one_month_end%',
                 'report_overtime.%mertid_part_time_cc_one_month_duty%',
                
                 # 3 month part time CC mertid
                 'report_overtime.%mertid_part_time_cc_three_months%',
                 'report_overtime.%mertid_part_time_cc_three_months_start%',
                 'report_overtime.%mertid_part_time_cc_three_months_end%',
                 'report_overtime.%mertid_part_time_cc_three_months_duty%',

                 # 1 month part time CC overtime
                 'report_overtime.%overtime_part_time_cc_one_month%',
                 'report_overtime.%overtime_part_time_cc_one_month_start%',
                 'report_overtime.%overtime_part_time_cc_one_month_end%',
                 'report_overtime.%overtime_part_time_cc_one_month_duty%',

                 # 3 month part time CC overtime
                 'report_overtime.%overtime_part_time_cc_three_months%',
                 'report_overtime.%overtime_part_time_cc_three_months_start%',
                 'report_overtime.%overtime_part_time_cc_three_months_end%',
                 'report_overtime.%overtime_part_time_cc_three_months_duty%',

                 'report_overtime.%overtime_month_ot%',
                 'report_overtime.%overtime_month_start%',
                 'report_overtime.%overtime_month_end%',
                 'report_overtime.%overtime_month_duty%',
                
                 'report_overtime.%overtime_7_calendar_days_ot%',
                 'report_overtime.%overtime_7_calendar_days_start%',
                 'report_overtime.%overtime_7_calendar_days_end%',
                 'report_overtime.%overtime_7_calendar_days_duty%',
                
                 # Duty time
                 'report_common.%duty_duty_time%', 
                 'duty.%start_hb%',
                 'duty.%end_hb%',

                 'salary_overtime.%overtime_before_freeday_ot%',
                 'salary_overtime.%overtime_late_checkout_rescheduling_ot%',
                 'salary_overtime.%overtime_before_free_weekend_ot%')


    def __init__(self, crew, area, start_time, end_time):
        self.crew = crew
        self.area = area
        self.start_time = start_time
        self.end_time = end_time

    def splitPacts(self):
        splitPactsExpression = 'crew.%%id%% = "%s" and overlap(duty.%%start_UTC%%, duty.%%end_UTC%%, %s, %s) > 0:00 and leg.%%is_pact%%' % (self.crew, self.start_time, self.end_time)
        Assign.splitPacts(workArea=self.area, scope='object', selection=splitPactsExpression)

    def getDuties(self):
        crew_object = HF.CrewObject(self.crew, self.area)
        dutyExpression = 'duty.%%start_hb%%+(duty.%%end_hb%%-duty.%%start_hb%%)/2 >= %s' % (self.start_time)
        dutyExpression += 'and duty.%%start_hb%%+(duty.%%end_hb%%-duty.%%start_hb%%)/2 <= %s' % (self.end_time)
        duties, = crew_object.eval(R.foreach(R.iter('iterators.duty_set', where=dutyExpression), *self.PT_VALUES))
        return duties

    def pushPtEntry(self, entry):
        crew_generic_entity = TM.table('crew')[(str(entry[0]),)]
        try:
            rec = TM.privately_traded_days.create((crew_generic_entity, str(entry[1]), AbsTime(entry[3])))
        except M.EntityError:
            self.removePrivateTradeValues()
            rec = TM.privately_traded_days.create((crew_generic_entity, str(entry[1]), AbsTime(entry[3])))

        rec.duty_end = AbsTime(entry[4])
        rec.period_start = AbsTime(entry[3]).day_floor()
        rec.period_end = AbsTime(entry[4]).day_ceil()
        rec.duty_time = RelTime(entry[5])
        rec.duty_overtime = RelTime(entry[2])

    def storeOvertimeValues(self):
        """
        Store overtime values crew had in period which is privately traded
        """
        log("Beginning storage of overtime values")
        duties = self.getDuties()
        ptd_table_entry = []
        for dt in duties:
            ot_values = dt[1:]
            for i in xrange(0,len(ot_values)-6, 4):
                if ot_values[i] and ot_values[i] > RelTime('0:00'):
                    ot_type_str = [ot_type for ot_type in self.PT_TYPES if self.PT_TYPES[ot_type] == i][0]
                    ot_value = ot_values[i]
                    log("Overtime value found! Storing %s with value of %s" % (str(ot_type_str), str(ot_value)))
                    
                    # Crew is given overtime for late checkout either if it is before freeday , late checkout due to rescheduling or before free weekend.  
                    if ot_type_str == 'OT_PART_LATE_CHECKOUT':
                        for j in xrange(len(ot_values)-3, len(ot_values)):
                            if ot_values[j] and ot_values[j] > RelTime('0:00'):
                                # Found the correct variable for overtime due to late checkout.
                                ot_type_str = [ot_type for ot_type in self.PT_TYPES if self.PT_TYPES[ot_type] == j][0]
                                ot_value = ot_values[j]
                                break
                    
                    # 0 crew_id, 1 overtime type as string, 2 overtime, 3 duty_start, 4 duty_end, 5 duty_time
                    ptd_table_entry.append((self.crew, ot_type_str, ot_value, ot_values[i+1], ot_values[i+2], ot_values[i+3]))
                        
        for entry in ptd_table_entry:
            self.pushPtEntry(entry)

    def storeDutyValues(self):
        """
        Store duty times crew had in period which is privately traded
        """
        duties = self.getDuties()
        ptd_table_entry = []
        dt_type_str = 'DT_PART'
        dt_start_index = self.PT_TYPES[dt_type_str]
        # We are not interested in any overtime values in this part
        ot_dummy = RelTime('0:00')

        log("Beginning storage of overtime values")
        for dt in duties:
            dt_values = dt[1:]
            for dt_item in xrange(dt_start_index, dt_start_index+1):
                if dt_values[dt_item] and dt_values[dt_item] > RelTime('0:00'):
                    dt_value = dt_values[dt_item] 
                    dt_start = dt_values[dt_item+1]
                    dt_end   = dt_values[dt_item+2]
                    log("Duty time value found! Storing %s with value of %s" % (dt_type_str, str(dt_value)))

                    # 0 crew_id, 1 duty as string identifier, 2 overtime, 3 duty_start, 4 duty_end, 5 duty_time
                    ptd_table_entry.append((self.crew, dt_type_str, ot_dummy, dt_start, dt_end, dt_value))
                        
        for entry in ptd_table_entry:
            self.pushPtEntry(entry)

    #def removeOvertimeValues(crew, start_time, end_time):
    def removePrivateTradeValues(self):
        """
        Removes stored overtime or duty time values from table 
        'privately_traded_days'
        """
        crew_generic_entity = TM.table('crew')[(str(self.crew),)]
        start_dates = []
        
        for row in TM.privately_traded_days.search('(&(crew=%s)(duty_start<%s)(duty_start>=%s))' % (self.crew, AbsTime(self.end_time), AbsTime(self.start_time))):
            start_dates.append(row.duty_start)
        
        for pt_type in self.PT_TYPES.keys():
            for start_date in start_dates:
                try:
                    TM.privately_traded_days[(crew_generic_entity, pt_type, AbsTime(start_date))].remove()
                except: continue

    def run(self, delete=False):
        """
        Start saving or removig overtime and duty values when executing a private trade.
        """
        if delete:
            self.removePrivateTradeValues()
        else:
            # Split Pacts in period in order to calculate overtime values prior to private trade
            self.splitPacts()
            self.storeOvertimeValues()
            self.storeDutyValues()
