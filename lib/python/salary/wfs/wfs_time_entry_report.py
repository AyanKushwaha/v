"""
Handler for generating time entry report data for WFS
"""
from AbsTime import AbsTime
from AbsDate import AbsDate
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import carmensystems.rave.api as rave
import collections
from functools import reduce
import logging
from itertools import chain
import heapq
import copy
import os, stat
from utils.selctx import SingleCrewFilter
import modelserver
from RelTime import RelTime
from salary.wfs.wfs_report import WFSReport
from salary.wfs.wfs_report import (abs_to_datetime, extperkey_from_id, country_from_id, 
    getNextRecordId, getNextRunId, add_to_salary_wfs_t, rank_from_id, actual_rank_from_id, reltime_to_decimal, default_reltime,
    integer_to_reltime, crew_info_changed_in_period, crew_has_retired_at_date,planninggroup_from_id)
from salary.wfs.wfs_config import PaycodeHandler
import time

HEADERS = ('EMPLOYEE_ID', 'PAY_CODE', 'WORK_DT', 'HOURS', 'DAYS_OFF')
EXCLUDED_RANKS=['AA']

logging.basicConfig()
log = logging.getLogger('wfs_time_entry')
log.setLevel(logging.INFO)

tm = modelserver.TableManager.instance()

class TimeEntryReport(WFSReport):

    def __init__(self, type='TIME', report_start_date=None, report_end_date=None, release=False, test=False, studio=False):
        WFSReport.__init__(self, type, release, test, studio)
        self.headers = HEADERS
        
        report_end_date = (datetime.strptime(report_end_date,'%d%b%Y') -timedelta(days=1)).strftime("%d%b%Y")
        report_end_date= datetime.strptime(report_end_date, "%d%b%Y")
        month = report_end_date.month
        year = report_end_date.year
        day= report_end_date.day
        report_end_date = AbsTime(year, month, day, 23, 59)
        
        self.start = AbsTime(report_start_date)
        self.end = AbsTime(report_end_date)

        log.info('NORDLYS: TimeEntryReport Generating report for the period {0} to {1}'.format(self.start, self.end))

        self.cached_account_data = self.generate_account_data()

        self.paycode_handler = PaycodeHandler()
        
        self.start_dt = self.start
        self.end_dt = self.end

        # Setup salary month parameters. Some rave variables used
        # checks against these parameters for validity.
        #rave.param('salary.%salary_month_start_p%').setValue(self.start)
        #rave.param('salary.%salary_month_end_p%').setValue(self.end)
        
        if self.test:
            log.setLevel(logging.DEBUG)
    '''
    Overridden functions START
    '''
    def format_row(self, row_data):
        duty_start_date = row_data['start_dt'].strftime('%Y-%m-%d')

        if row_data['days_off'] not in (0,1,None):
            row_data['days_off'] = format(row_data['days_off'] / 100.0,'.2f')

        row = [
            row_data['extperkey'],
            row_data['paycode'],
            duty_start_date,
            reltime_to_decimal(row_data['hours']),
            row_data['days_off']
            ]
        return row

    def extract_data(self, crew_id):
        log.info('NORDLYS: Extracting data for Time Entry report for crew {crew}...'.format(crew=crew_id))
        data = []
        data.extend(self._wfs_corrected(crew_id))
        data.extend(self._roster_events(crew_id))
        data.extend(self._account_transactions(crew_id))
        return data
    '''
    Overridden functions END
    '''

    '''
    Main data extraction START
    '''
    def _roster_events(self, crew_id):
        data = []
        where_filter = self.create_filter(self.start, self.end)
        monthly_ot = self._monthly_ot_template()
        valid_events = []
        calulated_tmp_hrs = []
        crew_info_changes_in_period = crew_info_changed_in_period(crew_id, self.start, self.end)
        
        non_mid_tmp_hrs = []
        mid_tmp_hrs = []
        unfit_tmp_hrs = []
        split_tmp_hrs  = []
        sick_tmp_hrs = []

        log.info('NORDLYS: Extracting roster data for {0}'.format(crew_id))

        is_unfit_spanning = False

        is_split = False
        split_count = 1

        last_overtime_date = {"crew":crew_id,"date": self.report_start_date()}

        for roster_bag in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
            for trip_bag in roster_bag.iterators.trip_set(): 
                trip_start_day = trip_bag.trip.start_day()
                extperkey = extperkey_from_id(crew_id, trip_start_day)
                rank = rank_from_id(crew_id, trip_start_day)
                #log.debug('NORDLYS: Crew {e} has rank {r}'.format(e=extperkey, r=rank))
                #actual_rank = actual_rank_from_id(crew_id, trip_start_day)
                #log.debug('NORDLYS: Crew {e} has actual rank {r}'.format(e=extperkey, r=actual_rank))
                country = country_from_id(crew_id, trip_start_day)
                for duty_bag in trip_bag.iterators.duty_set(where=where_filter):
                    if not rank or not country:
                        # Not possible to evaluate anything without rank and country
                        log.info('NORDLYS: Rank or country not found')
                        continue
                    #if actual_rank in EXCLUDED_RANKS:
                        #log.info('NORDLYS: Skipping  crew {e} with excluded rank {r}'.format(e=extperkey, r=actual_rank))
                        #continue
                    event_data = self._event_data_template()
                    duty_start = duty_bag.duty.start_hb()
                    duty_end = duty_bag.duty.end_hb()
                    duty_start_day = duty_bag.duty.start_day()
                    duty_end_day = duty_bag.duty.end_day()
                    
                    log.info('NORDLYS: Checking roster events on {dt}'.format(dt=duty_start_day))

                    if duty_bag.duty.is_F7() or duty_bag.duty.is_F3():
                        # Skip any F7 or F3 duties from roster being reported
                        log.info('NORDLYS: Skipping F3 or F7 roster events on {dt}'.format(dt=duty_start_day))
                        continue

                    if crew_info_changes_in_period:
                        # Whenever crew information has changed within the period we need to update 
                        # the information included in reports. This needs to be checked on each duty
                        # to catch the actual changed information
                        extperkey, country, rank = self._update_crew_info(crew_id, duty_start_day)

                    # to pick only temp crew hrs 
                    
                    if duty_bag.crew.is_temporary_at_date(duty_start_day): 
                        
                        temp_contract_changes_in_period = duty_bag.crew.is_temporary_at_date(duty_start_day) <> duty_bag.crew.is_temporary_at_date(self.end)
                        crew_info_changes_in_period = crew_info_changed_in_period(crew_id, self.start, self.end)
        
                        if temp_contract_changes_in_period:
                            if not duty_bag.crew.is_temporary_at_date(duty_start_day):
                                # Crew is no longer temporary
                                log.info('NORDLYS: Crew {crew} is no longer temporary at {dt}'.format(crew=crew_id, dt=duty_start_day))
                                continue
                        elif duty_bag.report_overtime.has_bl_in_hb_interval(duty_start_day, duty_start_day + RelTime('24:00')):
                            log.info('NORDLYS: Found blank day for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            continue
                        elif duty_bag.duty.is_freeday():
                            log.info('NORDLYS: Found Free day for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            continue
                        
                        tmp_paycode = self.paycode_handler.paycode_from_event('TEMP', crew_id, country, rank)

                        if duty_bag.duty.has_unfit_for_flight_star():
                            log.info('NORDLYS: Found unfit duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            if is_unfit_spanning == True:
                                is_unfit_spanning = False
                            else:
                                is_unfit_spanning,unfitData = self._calculate_unfit_hrs(duty_bag,duty_start_day,is_unfit_spanning,country)
                                unfit_tmp_hrs.extend(unfitData)
                        elif duty_bag.duty.is_child_illness() or duty_bag.duty.is_on_duty_illness() or duty_bag.duty.is_on_duty_illness_link():
                            log.info('NORDLYS: Found ILL duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            sickData = self._calculate_before_sick_hrs(duty_bag,country)
                            if sickData:
                                sick_tmp_hrs.extend(sickData)
                        elif duty_bag.duty_period.is_split():
                            log.info('NORDLYS: Found split duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            if duty_bag.duty_period.start_day_hb() < self.start:
                                continue
                            if is_split == False and split_count == 1:
                                splitData,is_split = self._temporary_split_hours(duty_bag, duty_start_day, tmp_paycode, crew_id, extperkey,is_split)
                                split_count += 1 
                                if splitData:
                                    split_tmp_hrs.extend(splitData)
                            elif split_count == 2:
                                is_split = False 
                                split_count = 1
                        elif self._is_mid_night_spanning(duty_bag):
                            log.info('NORDLYS: Found midnight spanning duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            midData = self._temporary_mid_hours(duty_bag, duty_start_day, tmp_paycode, crew_id, extperkey)
                            if midData:
                                mid_tmp_hrs.extend(midData)
                        else:
                            log.info('NORDLYS: Found normal duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            nonMidData = self._temporary_non_mid_hours(duty_bag, duty_start_day, tmp_paycode, crew_id, extperkey)
                            if nonMidData:
                                non_mid_tmp_hrs.extend(nonMidData)

                    if monthly_ot[abs_to_datetime(duty_start_day).month]['val'] == None:
                        month = abs_to_datetime(duty_start_day).month
                        monthly_ot = self._distribute_monthly_ot(monthly_ot, month, duty_bag)
                    
                    planning_group = planninggroup_from_id(crew_id, duty_start_day)
                    if planning_group == "SVS":
                        if 'report_common.%%number_of_active_legs%%' > 0:
                            if 'duty.%%has_active_flight%%' or 'standby.%%duty_is_standby_callout%%':
                                start_dt = abs_to_datetime(duty_start_day)
                                end_dt = abs_to_datetime(duty_end_day)
                                nr_days = abs(end_dt - start_dt).days
                                # if nr_days == 0:
                                #     nr_days = 1
                                active_hours = default_reltime(duty_bag.report_overtime.active_duty_hrs())
                                public_holiday= duty_bag.report_roster.is_public_holiday_link(duty_start_day)
                                if start_dt==end_dt:
                                    if self.is_weekend(start_dt) or public_holiday:
                                        paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND',crew_id,country,rank)
                                        event_data['CNLN_PROD_WEEKEND']['hrs'] = active_hours
                                        event_data['CNLN_PROD_WEEKEND']['paycode'] = paycode
                                        event_data['CNLN_PROD_WEEKEND']['dt'] = abs_to_datetime(duty_end_day)
                                    else:   
                                        paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY',crew_id,country,rank)
                                        event_data['CNLN_PROD_WEEKDAY']['hrs'] = active_hours
                                        event_data['CNLN_PROD_WEEKDAY']['paycode'] = paycode
                                        event_data['CNLN_PROD_WEEKDAY']['dt'] = abs_to_datetime(duty_end_day)
                                else:
                                    for day in range(0, nr_days+1):
                                        curr_dt = abs_to_datetime(duty_start_day) + timedelta(days=day)
                                        start_time = RelTime(duty_bag.report_overtime.duty_starttime())
                                        end_dttime = RelTime(duty_bag.report_overtime.duty_endtime())
                                        log.info('NORDLYS:{END_TIME},{START_TIME}'.format(END_TIME=end_dttime,START_TIME=start_time))

                                        if day == 0:
                                            duty_hrs = (RelTime('24:00') - start_time)
                                        elif day==nr_days:
                                            duty_hrs = end_dttime
                                            log.info('NORDLYS:{DUTY_HRS},{duty_end}'.format(DUTY_HRS=duty_hrs,duty_end=end_dttime))

                                        if (self.is_weekend(curr_dt) or public_holiday):
                                            paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND',crew_id,country,rank)
                                            event_data['CNLN_PROD_WEEKEND']['hrs'] = duty_hrs
                                            event_data['CNLN_PROD_WEEKEND']['paycode'] = paycode
                                            event_data['CNLN_PROD_WEEKEND']['dt'] = curr_dt
                                        else:
                                        # if(self.is_weekday(curr_dt) and public_holiday) or (self.is_weekday(curr_dt)):
                                            paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY',crew_id,country,rank)
                                            event_data['CNLN_PROD_WEEKDAY']['hrs'] = duty_hrs
                                            event_data['CNLN_PROD_WEEKDAY']['paycode'] = paycode
                                            event_data['CNLN_PROD_WEEKDAY']['dt'] = curr_dt
                    
                        duty_illness = duty_bag.report_overtime.is_on_duty_illness_link()
                        if duty_illness == True:
                            start_dt = abs_to_datetime(duty_start_day) + timedelta(days=0)
                            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
                            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')
                            prev_duty_hrs_before_sick = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)
                            log.info('NORDLYS:{DUTY_ILLNESS}{PREV_DUTY_HRS}'.format(DUTY_ILLNESS=duty_illness,PREV_DUTY_HRS=prev_duty_hrs_before_sick))
                            if (prev_duty_hrs_before_sick != 0) :
                                general_sick_paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_SICK',crew_id,country,rank)
                                general_sick_hrs = RelTime('24:00')
                                event_data['CNLN_PROD_SICK']['hrs'] = general_sick_hrs 
                                event_data['CNLN_PROD_SICK']['paycode'] = general_sick_paycode
                                event_data['CNLN_PROD_SICK']['dt'] = abs_to_datetime(duty_start_day)
                                
                            
                        # Checkout on Day-off overtime 
                        general_ot_paycode_day_off = self.paycode_handler.paycode_from_event('CNLN_LAND_DAY_OFF', crew_id, country,rank)
                        general_ot_hrs_day_off = integer_to_reltime(duty_bag.report_overtime.OT_units_SVS())
                        event_data['CNLN_LAND_DAY_OFF']['hrs'] = general_ot_hrs_day_off                 
                        event_data['CNLN_LAND_DAY_OFF']['paycode'] = general_ot_paycode_day_off
                        event_data['CNLN_LAND_DAY_OFF']['dt'] = abs_to_datetime(duty_start_day)

                    	general_ot_hrs_45_50 = default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot_45_50_svs())
                        general_ot_hrs_50 = default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot_50_svs())
                        general_ot_paycode_45_50_ot = self.paycode_handler.paycode_from_event('CNLN_OT_45_50', crew_id, country,rank)
                        general_ot_paycode_50_ot = self.paycode_handler.paycode_from_event('CNLN_OT_50_PLUS', crew_id, country,rank)
                        if general_ot_hrs_day_off == RelTime('0:00'):

                            if (general_ot_hrs_45_50 > RelTime('0:00') or general_ot_hrs_50 > RelTime('0:00')) and (last_overtime_date['crew'] == crew_id and last_overtime_date['date'].adddays(6) < duty_start_day):
                                last_overtime_date['crew'] = crew_id
                                last_overtime_date['date'] = duty_start_day

                                event_data['CNLN_OT_45_50']['hrs'] = general_ot_hrs_45_50
                                event_data['CNLN_OT_45_50']['paycode'] = general_ot_paycode_45_50_ot
                                event_data['CNLN_OT_45_50']['dt'] = abs_to_datetime(duty_start_day)
                                event_data['CNLN_OT_50_PLUS']['hrs'] = general_ot_hrs_50                 
                                event_data['CNLN_OT_50_PLUS']['paycode'] = general_ot_paycode_50_ot
                                event_data['CNLN_OT_50_PLUS']['dt'] = abs_to_datetime(duty_start_day)
    
                            
                        # Filter out events with hour count > RelTime('00:00')
                        # These are the records that can be reported
                        # to WFS and stored in salary_wfs table
                        valid_events.extend([event for event in event_data.values() if event['hrs'] > RelTime('00:00')])
                
                    else:
                    # Check general overtime
                        general_ot_hrs = default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot())

                        if general_ot_hrs > RelTime('0:00') and (last_overtime_date['crew'] == crew_id and last_overtime_date['date'].adddays(6) < duty_start_day):
                            last_overtime_date['crew'] = crew_id
                            last_overtime_date['date'] = duty_start_day

                            general_ot_paycode = self.paycode_handler.paycode_from_event('OT', crew_id, country, rank)
                            event_data['OT']['hrs'] = general_ot_hrs
                            event_data['OT']['paycode'] = general_ot_paycode
                            event_data['OT']['dt'] = abs_to_datetime(duty_start_day)
                            
                        # Late checkout overtime. FC has its own paycode for this while
                        # CC has theirs merged with general overtime
                        ot_late_co_hrs = default_reltime(duty_bag.report_overtime.overtime_late_checkout_ot())

                        ot_late_co_hrs_fc = duty_bag.report_overtime.OT_FD_units()

                        event = 'OT_LATE_CO' if rank == 'FC' else 'OT'  # For CC late co is merged into general overtime
                        ot_late_co_paycode = self.paycode_handler.paycode_from_event(event, crew_id, country, rank)
                        if event_data[event]['hrs']:
                            # add to existing if already present in general ot for CC
                            event_data[event]['hrs'] += ot_late_co_hrs
                        if rank == 'FC':
                            # For FC the units are picked by OT_FD_units, this needs to be reported in hours col with format 1.00
                            if ot_late_co_hrs_fc > 0:
                                ot_late_co_hrs_fc = integer_to_reltime(ot_late_co_hrs_fc)
                                event_data[event]['hrs'] = ot_late_co_hrs_fc
                                log.debug('NORDLYS: Crew: {crew}, Date: {dt} and FC Late CO Hrs:{fch}'.format(crew=crew_id,dt=duty_start_day,fch=ot_late_co_hrs_fc))

                        event_data[event]['paycode'] = ot_late_co_paycode
                        event_data[event]['dt'] = abs_to_datetime(duty_start_day)
                                        
                        # Filter out events with hour count > RelTime('00:00')
                        # These are the records that can be reported
                        # to WFS and stored in salary_wfs table
                        valid_events.extend([event for event in event_data.values() if event['hrs'] > RelTime('00:00')])
                
            # Do general overtime vs monthly overtime evaluation
            if rank and country:
                paycode = self.paycode_handler.paycode_from_event(
                    'OT', crew_id, country, rank
                    )
                valid_events = self._overtime_evaluation(
                    valid_events, monthly_ot, paycode
                    )
                for val in valid_events:
                    chk_wfs_corrected = self._check_in_wfs_corrected(crew_id, extperkey, val['paycode'], val['dt'], val['hrs'], None)
                    if chk_wfs_corrected:
                        continue
                    new_recs = self._latest_record(
                        crew_id,
                        extperkey,
                        val['paycode'],
                        val['dt'],
                        val['hrs'],
                        None
                        )
                    data.extend(new_recs)

                final_calulated_tmp_hrs = []
                final_calulated_tmp_dates = []

                # unfit hrs will get prefrence over split , mid night and normal duty for same day as PREV_INFORMED_DUTY_TIME column contains full previously informed duty time
                
                for rec_tmp in unfit_tmp_hrs:
                    if rec_tmp[0] not in final_calulated_tmp_dates:
                        final_calulated_tmp_hrs.append(rec_tmp)
                        final_calulated_tmp_dates.append(rec_tmp[0])

                for rec_tmp in sick_tmp_hrs:
                    if rec_tmp[0] not in final_calulated_tmp_dates:
                        final_calulated_tmp_hrs.append(rec_tmp)
                        final_calulated_tmp_dates.append(rec_tmp[0])

                for rec_tmp in split_tmp_hrs:
                    if rec_tmp[0] not in final_calulated_tmp_dates:
                        final_calulated_tmp_hrs.append(rec_tmp)
                        final_calulated_tmp_dates.append(rec_tmp[0])

                for rec_tmp in mid_tmp_hrs:
                    if rec_tmp[0] not in final_calulated_tmp_dates:
                        final_calulated_tmp_hrs.append(rec_tmp)
                        final_calulated_tmp_dates.append(rec_tmp[0])

                for rec_tmp in non_mid_tmp_hrs:
                    if rec_tmp[0] not in final_calulated_tmp_dates:
                        final_calulated_tmp_hrs.append(rec_tmp)
                        final_calulated_tmp_dates.append(rec_tmp[0])

                log.info("NORDLYS: Unfit_tmp_hrs for crew {crew} and hrs {hrs}".format(crew=crew_id,hrs=unfit_tmp_hrs))
                log.info("NORDLYS: Sick_tmp_hrs for crew {crew} and hrs {hrs}".format(crew=crew_id,hrs=sick_tmp_hrs))
                log.info("NORDLYS: Split_tmp_hrs for crew {crew} and hrs {hrs}".format(crew=crew_id,hrs=split_tmp_hrs))
                log.info("NORDLYS: Mid_tmp_hrs for crew {crew} and hrs {hrs}".format(crew=crew_id,hrs=mid_tmp_hrs))
                log.info("NORDLYS: Non_mid_tmp_hrs for crew {crew} and hrs {hrs}".format(crew=crew_id,hrs=non_mid_tmp_hrs))


                final_calulated_tmp_hrs = sorted(final_calulated_tmp_hrs,key=lambda x:x[0])

                log.info("NORDLYS: Tmp hrs for crew {crew} is {tmp_hrs}".format(crew=crew_id,tmp_hrs=final_calulated_tmp_hrs))

                # for tmp hrs in file 
                for tmp in final_calulated_tmp_hrs:
                    if crew_info_changes_in_period:
                        # Ensure correct extperkey is reported in case of base switching
                        extperkey, country, rank = self._update_crew_info(crew_id, tmp[0])
                    paycode = self.paycode_handler.paycode_from_event('TEMP', crew_id, country, rank)
                    curr_dt = abs_to_datetime(tmp[0])
                    hrs = tmp[1]
                    chk_wfs_corrected = self._check_in_wfs_corrected(crew_id, extperkey, paycode, curr_dt, hrs, None)
                    if chk_wfs_corrected:
                        continue
                    new_recs = self._latest_record(crew_id, extperkey, paycode, curr_dt, hrs, None)
                                        		    
		    data.extend(new_recs)
                    
        return data

    def _wfs_corrected(self,crew_id):
        data = []
        table = tm.table('wfs_corrected')
        uniq_dates = set()
        wfs_corrected_data = []
        final_wfs_corrected_data = []

        for i in table.search("(&(crew_id={crew})(work_day>={start})(work_day<={end}))".format(crew=crew_id,start=self.start,end=self.end)):

            rec = [i.correction_id,i.crew_id.id,i.extperkey,i.wfs_paycode,i.work_day,i.amount,i.days_off]

            wfs_corrected_data.append(rec)
            uniq_dates.add(i.work_day)

        for dt in uniq_dates:
            mx_id = -1
            for rec in wfs_corrected_data:
                if rec[4] == dt:
                    if rec[0] > mx_id:
                        mx_id = rec[0]
                        mx_rec = rec
            final_wfs_corrected_data.append(mx_rec) 

        for rec in final_wfs_corrected_data:
            corrected_rec = self._latest_record(rec[1], rec[2], rec[3], abs_to_datetime(rec[4]), rec[5], rec[6])
            log.info("NORDLYS : wfs_corrected Record generated : {0}".format(corrected_rec))
            data.extend(corrected_rec)
        return data

    
    def _check_in_wfs_corrected(self, crew_id, extperkey, wfs_paycode, curr_dt, hrs, days_off):
        
        table = tm.table('wfs_corrected')

        # curr_dt = abs_to_datetime(curr_dt) + timedelta(days=0)
        curr_dt = AbsTime(curr_dt.year,curr_dt.month,curr_dt.day,0,0)

        rec = table.search("(&(extperkey='{extperkey}')(wfs_paycode='{wfs_paycode}')(work_day={dt}))".format(
            extperkey = extperkey,
            wfs_paycode = wfs_paycode,
            dt = curr_dt
            ))
        
        if len(list(rec)) == 0:
            return False
        else:
            return True


    def _calculate_before_sick_hrs(self,duty_bag,country):

        rec = []

        if country == 'DK' or (country == 'NO' and duty_bag.duty.active_duty_within_15x24_bwd()):

            duty_start_day = duty_bag.duty.start_day()
            duty_end_day = duty_bag.duty.end_day()

            days = (int(str(duty_end_day - duty_start_day).split(':')[0])//24) + 1

            for i in range(days):
                start_dt = abs_to_datetime(duty_start_day) + timedelta(days=i)
                start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
                start_dt_end_abs = start_dt_start_abs + RelTime('24:00')

                prev_duty_hrs_before_sick = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)

                data_day = duty_start_day.adddays(i)

                if country == 'NO' and prev_duty_hrs_before_sick < RelTime('06:00'):
                    prev_duty_hrs_before_sick = RelTime('06:00')

                data = (data_day,prev_duty_hrs_before_sick)

                rec.append(data)

        return rec
    
    def _calculate_unfit_hrs(self,duty_bag,duty_start_day,is_spanning,country):

        duty_start_day = duty_bag.duty.start_day()
        duty_end_day = duty_bag.duty.end_day()

        start_dt = abs_to_datetime(duty_start_day) + timedelta(days=0)
        start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
        start_dt_end_abs = start_dt_start_abs + RelTime('24:00')

        end_dt = abs_to_datetime(duty_end_day) + timedelta(days=0)
        end_dt_end_abs = AbsTime(end_dt.year, end_dt.month, end_dt.day, 0, 0)

        prev_inf_ref_chk_out = duty_bag.rescheduling.period_inf_prev_checkout(start_dt_start_abs,start_dt_end_abs)
        log.info("NORDLYS: prev_inf_ref_chk_out {0}".format(prev_inf_ref_chk_out))

        prev_inf_ref_chk_out = duty_bag.rescheduling.period_inf_prev_checkout(start_dt_start_abs,start_dt_end_abs)
        if prev_inf_ref_chk_out is None:
            prev_inf_ref_chk_out_day = start_dt_start_abs
            log.info("NORDLYS: Crew ref checkout date {date} is None".format(date=duty_start_day))
        else:
            prev_inf_ref_chk_out_day = abs_to_datetime(prev_inf_ref_chk_out) + timedelta(days=0)
            prev_inf_ref_chk_out_day = AbsTime(prev_inf_ref_chk_out_day.year, prev_inf_ref_chk_out_day.month, prev_inf_ref_chk_out_day.day, 0, 0)
        
        if start_dt_start_abs != end_dt_end_abs and prev_inf_ref_chk_out_day == start_dt_start_abs:
            nr_days = int(str(end_dt_end_abs - start_dt_start_abs)[:-3]) // 24
        else:
            nr_days = int(str(prev_inf_ref_chk_out_day - start_dt_start_abs)[:-3]) // 24
        nr_days += 1

        day1_hrs = RelTime('00:00')
        day2_hrs = RelTime('00:00')
        
        data = []
        total_hrs = []

        if nr_days == 1:

            start_dt = abs_to_datetime(duty_start_day) + timedelta(days=0)
            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')

            day1_hrs = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)
            
            if day1_hrs > RelTime('0:00') and day1_hrs < RelTime('6:00') and country in ('SE','NO'):
                day1_hrs = RelTime('6:00')

            total_hrs = [(start_dt_start_abs,day1_hrs)]

            log.info("NORDLYS: Single day unfit duty found {dt} and total hrs {hrs}".format(dt=start_dt_start_abs,hrs=total_hrs))

        elif nr_days == 2:

            start_dt = abs_to_datetime(duty_start_day) + timedelta(days=0)
            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')

            day1_hrs = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)
            day1_active_duty_hrs = duty_bag.rescheduling.period_inf_duty_time(start_dt_start_abs,start_dt_end_abs)
            day1_unfit_duty_hrs = day1_hrs - day1_active_duty_hrs
            unfit_day1 = start_dt_start_abs

            start_dt = abs_to_datetime(duty_start_day) + timedelta(days=1)
            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')

            day2_hrs = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)
            day2_active_duty_hrs = duty_bag.rescheduling.period_inf_duty_time(start_dt_start_abs,start_dt_end_abs)
            day2_unfit_duty_hrs = day2_hrs - day2_active_duty_hrs
            unfit_day2 = start_dt_start_abs

            total_unfit_hrs = day1_unfit_duty_hrs + day2_unfit_duty_hrs

            if total_unfit_hrs > RelTime('0:00') and total_unfit_hrs < RelTime('6:00') and country in ('SE','NO'):
                extra_hrs = RelTime('6:00') - total_unfit_hrs
            else:
                extra_hrs = RelTime('0:00')

            if day2_active_duty_hrs > RelTime('0:00') and day2_active_duty_hrs < RelTime('6:00') and country in ('SE','NO'):
                day2_active_duty_hrs = RelTime('0:00')

            day1_rec = (unfit_day1,day1_active_duty_hrs+day1_unfit_duty_hrs+extra_hrs)
            day2_rec = (unfit_day2,day2_unfit_duty_hrs+day2_active_duty_hrs)

            total_hrs = [day1_rec,day2_rec]

            log.info("NORDLYS: Double day unfit duty found {dt1} , {dt2} and total hrs {hrs}".format(dt1=unfit_day1,dt2=unfit_day2,hrs=total_hrs))

        return is_spanning,total_hrs 


    def _is_mid_night_spanning(self,duty_bag):
        tmp_hrs_start_day = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_bag.duty.start_day()))
        tmp_hrs_end_day = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_bag.duty.end_day()))
        if tmp_hrs_start_day != tmp_hrs_end_day and duty_bag.duty.start_day() != duty_bag.duty.end_day():
            return True
        else:
            return False

    def active_duty_hrs(self,duty_bag):
        duty_start_hb = default_reltime(duty_bag.duty.start_hb())
        duty_end_hb = default_reltime(duty_bag.duty.end_hb())
        if duty_bag.duty.has_active_flight:
            if duty_bag.standby.duty_is_standby_callout:
                return duty_bag.standby.active_duty_hrs()
        else:
            return 0
    
    def is_weekend(self,start):
        weekday_num = start.weekday()
        log.info('######################: Weekday Day Number {sd}'.format(sd=weekday_num))
        if (weekday_num <= 4):
            log.debug('NORDLYS: Day is Sunday and Saturday {day}'.format(day=weekday_num))
            return False
        else:
            log.debug('NORDLYS: Day is between Monday or Firday {day}'.format(day=weekday_num))
            return True
        return False

    def is_weekday(self,start):
        weekday_num = start.weekday()
        log.info('######################: Weekday Day Number {sd}'.format(sd=weekday_num))
        if (weekday_num <= 4):
            log.debug('NORDLYS: Day is Sunday and Saturday {day}'.format(day=weekday_num))
            return True
        else:
            log.debug('NORDLYS: Day is between Monday or Firday {day}'.format(day=weekday_num))
            return False 
        return False

    def _temporary_split_hours(self, duty_bag, start_dt, paycode, crew_id, extperkey,split_found):

        duty_start_hb = duty_bag.duty.start_hb()
        duty_end_hb = duty_bag.duty.end_hb()
        
        duty_start_day = duty_bag.duty.start_day()
        duty_end_day = duty_bag.duty.end_day()

        country = country_from_id(crew_id, duty_start_day)

        split_found = True
        day1_tmp_hrs = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_start_day))
        day2_tmp_hrs = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_start_day + RelTime('24:00')))
        final_hrs = day1_tmp_hrs + day2_tmp_hrs
        final_day = duty_start_day
        if final_hrs > RelTime('24:00'):
            first_day_hrs = RelTime('24:00')
            first_day = final_day
            second_day_hrs = final_hrs - first_day_hrs
            second_day = final_day + RelTime('24:00')
            data_split = [(first_day,first_day_hrs),(second_day,second_day_hrs)]
        else:
            data_split = [(final_day,final_hrs)]

        log.info("NORDLYS: Split duty found for crew is {0} , started at {1} , end at {2} and country {3}".format(crew_id,duty_start_hb,duty_end_hb,country))
        log.info("NORDLYS: Split hrs are {0}".format(data_split))
        
        return data_split,split_found
    
    def _temporary_non_mid_hours(self, duty_bag, start_dt, paycode, crew_id, extperkey):
        tmp_hrs_list = []
        curr_abs = start_dt
               
        if duty_bag.report_overtime.has_il7_in_hb_interval(curr_abs, curr_abs + RelTime('24:00')) and not duty_bag.duty.is_flight_duty():
           log.info('NORDLYS: Found IL7 day for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=curr_abs)) 
        else:
            tmp_hrs = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(curr_abs))
            if tmp_hrs > RelTime('00:00'):
                log.info('NORDLYS: Found temporary hours {hrs} on {dt}'.format(hrs=tmp_hrs, dt=curr_abs))
                tmp_hrs_list.append((curr_abs, tmp_hrs))
            elif tmp_hrs == RelTime('00:00') and duty_bag.duty.is_privately_traded() and country_from_id(crew_id, start_dt) == 'DK':
                hrs1 = (duty_bag.duty.end_UTC() - duty_bag.duty.start_UTC()) + duty_bag.duty.short_stop_duty_time_contribution()
                hrs2 = duty_bag.duty.duty_time_standby_reduction_16(duty_bag.duty.start_UTC(), duty_bag.duty.end_UTC())
                tmp_hrs = hrs1 - hrs2 
                tmp_hrs_list.append((curr_abs, tmp_hrs))
                log.info('NORDLYS: Found Privately traded DK duty having {hrs} on {dt}'.format(hrs=tmp_hrs, dt=curr_abs))

        return tmp_hrs_list

    def _temporary_mid_hours(self,duty_bag,start_dt, paycode, crew_id, extperkey):

        duty_start_hb = duty_bag.duty.start_hb()
        duty_end_hb = duty_bag.duty.end_hb()
        
        duty_start_day = duty_bag.duty.start_day()
        duty_end_day = duty_bag.duty.end_day()

        country = country_from_id(crew_id, duty_start_day)

        day1_tmp_hrs = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_start_day))
        day2_tmp_hrs = default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_end_day))
        
        if country == 'DK':
            day1_final = day1_tmp_hrs
            day2_final = day2_tmp_hrs
        elif country == 'SE':
            day1_final = (duty_start_day + RelTime('24:00')) - duty_start_hb
            day2_final = day1_tmp_hrs - day1_final + day2_tmp_hrs
        elif country == 'NO':
            day1_final = (duty_start_day + RelTime('24:00')) - duty_start_hb
            day2_final = day2_tmp_hrs - day1_final + day1_tmp_hrs            
        
        mid_night_data = [(duty_start_day,day1_final),(duty_end_day,day2_final)]

        log.info("NORDLYS: Crew is {0} , start date {1} , end date {2} and country {3}".format(crew_id,duty_start_hb,duty_end_hb,country))
        log.info("NORDLYS: Mid night spanning hrs are {0}".format(mid_night_data))

        return mid_night_data

    def _days_of_spanning(self,duty_bag,is_midnight_spanning):
        if is_midnight_spanning:
            duty_start_day = duty_bag.duty.start_day()
            duty_end_day = duty_bag.duty.end_day()
            nr = int(str(duty_end_day - duty_start_day)[:-3]) // 24
            return nr 
        else:
            return 0
    
    def _overtime_evaluation(self, valid_events, monthly_ot, paycode):
        '''
        Evaluates general overtime
        First checks for obvious duplicates not catched by rave code.
        Secondly evaluates if the monthly overtime i.e any time past 166 hrs
        exceeds the general overtime gained from working more than 47:30 hrs in
        one week. The primary overtime wins, described below:

        Example:
        Crew 12345 has 176 hrs worked in DEC2020, which equals 10 hrs overtime
        Crew 12345 also has 6 overtime hours due to exceeding the weekly limits
        Since 10 > 6 the overtime becomes 10 hrs and is reported on 1DEC2020
        '''
        valid_events = self._remove_overtime_duplicates(valid_events, paycode)

        # Filter out OT events for certain month
        for month in monthly_ot:
            if monthly_ot[month]['val'] is None:
                log.debug('NORDLYS: Monthly OT not set. No data for this month...')
                # Shouldn't be any values for this month
                continue
            start_of_month = monthly_ot[month]['month']
            end_of_month = start_of_month + relativedelta(months=1, days=-1)

            # Filter out all general ot for specific dates in monthly periods
            filtered_ot = list(filter(
                    lambda e: (e['dt'] >= start_of_month and e['dt'] <= end_of_month) and 
                    e['paycode'] == paycode
                    , valid_events))
            log.debug('NORDLYS: Found the following OT for {m}: \n{f}'.format(m=start_of_month, f=filtered_ot))
            # Summarize all general ot in month
            summarized_ot = RelTime('00:00') if not filtered_ot else reduce(lambda x, y : x + y['hrs'], filtered_ot, RelTime('00:00'))
            # Compare with monthly value, if higher keep general ot else remove general and add monthly
            if summarized_ot > monthly_ot[month]['val']:
                log.debug('''
                NORDLYS: Summarized OT is higher than monthly OT:
                Summarized: {s}
                Monthly: {m}
                '''.format(s=summarized_ot, m=monthly_ot[month]['val']))
                # No changes needed since general ot is higher than monthly
                continue
            elif summarized_ot < monthly_ot[month]['val']:
                log.debug('''
                NORDLYS: Summarized OT is lower than monthly OT:
                Summarized: {s}
                Monthly: {m}
                '''.format(s=summarized_ot, m=monthly_ot[month]['val']))
           
                if summarized_ot > RelTime('00:00'):
                    # Filter out general ot in favor of monthly ot
                    valid_events = list(filter(
                        lambda e: (e['dt'] < start_of_month and e['dt'] > end_of_month) and
                        e['paycode'] == paycode
                        , valid_events))
                # Add monthly overtime
                valid_events.append({
                        'hrs'     : monthly_ot[month]['val'],
                        'paycode' : paycode,
                        'dt'      : monthly_ot[month]['month'] 
                    })
            else:
                continue
        return valid_events
    
    def _remove_overtime_duplicates(self, valid_events, paycode):
        '''
        This function handles cases that doesn't get picked up in rave by
        report_overtime.%overtime_7_calendar_days_ot%. Primarily this seems to
        happen whenever consecutive duties has the same amount of overtime and
        could possibly be a bug related to private trades. Evaluates if there
        are any general overtime present in a 7 day period forwards.
        '''
        # Filter out general OT
        general_ot = list(filter(lambda e: e['paycode'] == paycode, valid_events))
        removals = []
        for i in range(0, len(general_ot)):
            try:
                if general_ot[i+1]['dt'] <= (general_ot[i]['dt'] + relativedelta(days=7)):  # Check 7 days forward
                    # mark index to be removed
                    log.debug('NORDLYS: Marking {ot} as duplicate for removal'.format(ot=general_ot[i]))
                    removals.append(general_ot[i])
            except IndexError:
                # No more events to check
                break
        for r in removals:
            log.debug('NORDLYS: Removing {r} from valid events'.format(r=r))
            general_ot = list(filter(lambda e: e['dt'] != r['dt'], general_ot))
        if general_ot:
            # Cut all general ot events and reapply the processed list
            log.debug('NORDLYS: valid_events before cutting general ot : {0}'.format(valid_events))
            valid_events = list(filter(lambda e: e['paycode'] != paycode, valid_events))
            valid_events.extend(general_ot)
            log.debug('NORDLYS: valid_events after reapplying processed list : {0}'.format(valid_events))
        return valid_events

    def _distribute_monthly_ot(self, ot_dict, month, duty_bag):
        '''
        Any duty time exceeding 166 hours in a single
        month will be counted towards the monthly overtime.
        Calculations depend on salary month parameters that
        need to be changed during the calculation to get the
        correct values

        :param ot_dict
        '''
        # Temporary alter salary_month parameters for monthly ot calculations
        start = ot_dict[month]['month']
        end = start + relativedelta(months=1)
        rave.param('salary.%salary_month_start_p%').setValue(AbsTime(start.year, start.month, start.day, 0, 0))
        rave.param('salary.%salary_month_end_p%').setValue(AbsTime(end.year, end.month, end.day, 0, 0))
        # Register monthly overtime if applicable. If the rave function voids it will default to '00:00'
        ot_dict[month]['val'] = default_reltime(duty_bag.report_overtime.overtime_month_ot())
        log.info('NORDLYS: Monthly OT set to {ot} for {st} - {end}'.format(ot=ot_dict[month]['val'], st=start, end=end))
        # reset salary_month parameters
        rave.param('salary.%salary_month_start_p%').setValue(self.start)
        rave.param('salary.%salary_month_end_p%').setValue(self.end)
        return ot_dict

    def _monthly_ot_template(self):
        '''
        Sets up a structure for storing monthly overtime for easier
        evaluation in _overtime_evaluation

        ext_last_month is included due to reportworker publish_short has
        end of current month + 31d set as its period end. 
        '''
        prev_month = abs_to_datetime(self.start)
        #curr_month = prev_month + relativedelta(months=1)
        curr_month = prev_month
        #last_month = curr_month + relativedelta(months=1)
        last_month = prev_month
        # Reportworker publish_short has end of current month + 31d
        #ext_last_month = last_month + relativedelta(months=1)
        ext_last_month = prev_month
        template = dict()
        # .month = int, used as key for easy lookup from duties
        template.setdefault(prev_month.month, {'month' : prev_month, 'val' : None})
        template.setdefault(curr_month.month, {'month' : curr_month, 'val' : None})
        template.setdefault(last_month.month, {'month' : last_month, 'val' : None})
        template.setdefault(ext_last_month.month, {'month' : ext_last_month, 'val' : None})
        log.debug('NORDLYS: template instantiated :  {0}'.format(template))
        return template
            
    def _event_data_template(self):
        '''
        Example event_data structure
        ---
        event_data = {
           'OT' : {
               'hrs' : RelTime('00:00'),
               'paycode' : 'SAS_NO_CMS_OT',
               'dt'  : AbsTime(2020, 12, 24, 0, 0)
           },
           'TEMP' : {
               ...
           }
        }
        '''
        event_types = ('OT', 'OT_LATE_CO', 'TEMP','CNLN_OT_45_50','CNLN_OT_50_PLUS','CNLN_LAND_DAY_OFF','CNLN_PROD_WEEKEND','CNLN_PROD_WEEKDAY','CNLN_PROD_SICK')
        event_data_t = dict()
        
        for e in event_types:
            event_data_t.setdefault(e, {})
            event_data_t[e] = {
                'hrs'       : RelTime('00:00'),
                'paycode'   : '',
                'dt'        : AbsTime(1986, 1, 1, 0, 0)
            }
        return event_data_t

    def _account_transactions(self, crew_id):
        '''
        Compares records from account_entry table to eventual pre-existing
        records in salary_wfs (already sent to WFS at previous date)

        :param crew_id
        needed for doing lookups in account_entry
        extperkey needed for doing the actual reporting to WFS
        '''
        data = []
        curr_date = AbsTime(datetime.now().strftime('%d%b%Y'))
        extperkey = extperkey_from_id(crew_id, curr_date)
        log.debug('NORDLYS: crew_id {0} converted to extperkey {1}'.format(crew_id, extperkey))
        if extperkey == crew_id:
            # Try converting crew_id as extperkey to actual crew_id
            crew_id = rave.eval('model_crew.%crew_id_from_extperkey%("{0}", {1})'.format(crew_id, curr_date))[0]
        country = country_from_id(crew_id, curr_date)
        rank = rank_from_id(crew_id, curr_date)
        
        crew_info_changed = crew_info_changed_in_period(crew_id, self.start, self.end)
        planning_group = planninggroup_from_id(crew_id, curr_date)

        try:
            transactions = self.cached_account_data[crew_id]
        except KeyError:
            log.info('NORDLYS: No account entries found for {crew}'.format(crew=crew_id))
            return []

        for dated_tnx in transactions:
            tnx = dated_tnx['tnx']
            tnx_dt = dated_tnx['tnx_dt']
            days_off = dated_tnx['days_off']
            if crew_info_changed:
                extperkey, country, rank = self._update_crew_info(crew_id, tnx_dt)
            log.debug('NORDLYS: Transaction on {account} for amount {d} on {dt}'.format(account=tnx.account.id, d = days_off, dt=tnx_dt))
            accountid = tnx.account.id
            if planning_group == 'SVS' and tnx.account.id == 'SOLD':
                accountid = 'CNLN_SOLD'
            wfs_paycode = self.paycode_handler.paycode_from_event(accountid, crew_id, country, rank)
            log.debug('NORDLYS: wfs_paycode {0} mapped from account {1}'.format(wfs_paycode, tnx.account.id))
            # Check if this transaction already has been sent
            chk_wfs_corrected = self._check_in_wfs_corrected(crew_id, extperkey, wfs_paycode, abs_to_datetime(tnx_dt), None, 1)
            if chk_wfs_corrected:
                continue
            new_recs = self._latest_record(crew_id, extperkey, wfs_paycode, abs_to_datetime(tnx_dt), None, days_off)
            data.extend(new_recs)

        log.info('NORDLYS: Extracting data from accounts finished!')
        log.info('NORDLYS: {0} new records created for Time Entry report'.format(len(data)))
        return data

    def _update_crew_info(self, crew_id, dt):
        # Catch cases where crew has their information changed in period
        extperkey = extperkey_from_id(crew_id, dt)
        country = country_from_id(crew_id, dt)
        rank = rank_from_id(crew_id, dt)
        if any(attr is None for attr in [extperkey, country, rank]):
            # Check if crew has retired in at the date of transaction
            if crew_has_retired_at_date(crew_id, dt):
                # Revert to extperkey, country and rank at period start
                extperkey = extperkey_from_id(crew_id, self.start)
                country = country_from_id(crew_id, self.start)
                rank = rank_from_id(crew_id, self.start)
        return (extperkey, country, rank)

    def _latest_record(self, crew_id, extperkey, wfs_paycode, curr_dt, hours, days_off):
        data = []
        curr_abs = AbsTime(curr_dt.year, curr_dt.month, curr_dt.day, 0, 0)        
	log.info('NORDLYS: Skipped pre-existing records... Adding new record')

        if (hours and hours > RelTime('0:00')) or (days_off and days_off != 0):
            insert_row_data = {
                'extperkey' : extperkey,
                 'paycode' : wfs_paycode,
                 'hours' : hours, 
                 'days_off' : days_off,
                 'start_dt' : curr_dt
            }
       
            row = self.format_row(insert_row_data)
            log.info(row)
            data.append(row) 

	return data

    '''
    Main data extraction END
    '''
    def report_start_date(self):
        now = datetime.now()
        year = now.year if now.month != 1 else now.year - 1
        month = now.month - 1 if now.month != 1 else 12
        return AbsTime(year, month, 1, 0, 0)

    def report_end_date(self):
        '''
        :return: AbsTime date of either last day of next month or 31 days ahead of last day of current month, whichever greater
                
        '''
        now = datetime.now()
        curr_month_end = datetime(now.year, now.month, 1) + relativedelta(months=1, days=-1)
        thirtyone_days_ahead = curr_month_end + relativedelta(days=31)
        next_month_end = datetime(now.year, now.month, 1) + relativedelta(months=2, days=-1)

        if next_month_end > thirtyone_days_ahead:
            end_dt_abs = AbsTime(next_month_end.year, next_month_end.month, next_month_end.day, 0, 0)    
        else:
            end_dt_abs = AbsTime(thirtyone_days_ahead.year, thirtyone_days_ahead.month, thirtyone_days_ahead.day, 0, 0)

        return end_dt_abs
    
    '''
    Cache functions START
    '''

   
    def generate_account_data(self):
        account_entry_t = tm.table('account_entry')
        account_query = '(|(account=BOUGHT)(account=BOUGHT_BL)(account=BOUGHT_FORCED)(account=BOUGHT_8)(account=SOLD))'
        reasoncode_query = '(|(reasoncode=BOUGHT)(reasoncode=SOLD))'
        query_f3_f7 = '&(|(account=F3)(account=F7))(|(reasoncode=OUT Payment)(reasoncode=IN Payment Correction))'

        transactions = account_entry_t.search('(&(tim>={st})(tim<={end})(|(&{account_query}{reasoncode_query})({query_f3_f7})))'.format(
            st=self.start,
            end=self.end,
            account_query=account_query,
            reasoncode_query=reasoncode_query,
            query_f3_f7=query_f3_f7
        ))
        
        dict_t = {}
        for tnx in transactions: 
            dict_t.setdefault(tnx.crew.id, [])
            nr_days = abs(int(tnx.amount / 100))
            curr_abs = tnx.tim

            if tnx.account.id in ('F3','F7'):
                if tnx.reasoncode == 'OUT Payment':
                    nr_days = abs(tnx.amount)
                elif tnx.reasoncode == 'IN Payment Correction':
                    nr_days = - tnx.amount
                if curr_abs > self.end:
                        # Activity starts after set end date
                        break
                dict_t[tnx.crew.id].append({
                        'tnx_dt'        : curr_abs,
                        'tnx'           : tnx,
                        'days_off'      : nr_days})
                log.info('NORDLYS: Found {0} account for crew {1} on date {2} with days_off {3}'.format(tnx.account.id,tnx.crew.id,curr_abs, nr_days))                
            else:
                for day in range(0, nr_days):                    
                    if curr_abs > self.end:
                        # Activity starts after set end date
                        break                    
                    dict_t[tnx.crew.id].append({
                        'tnx_dt'        : curr_abs,
                        'tnx'           : tnx,
                        'days_off'      : 1})
                    curr_abs = curr_abs.adddays(1)

        log.info('NORDLYS: {0} nr of crew with account data extracted without VA/VA1'.format(len(dict_t)))
        return dict_t
    '''
    Cache functions END
    '''
     

