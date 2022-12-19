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


HEADERS = ('EMPLOYEE_ID', 'PAY_CODE', 'WORK_DT', 'HOURS', 'DAYS_OFF', 'START_DTTM', 'END_DTTM', 'RECORD_ID', 'FLAG')
EXCLUDED_RANKS=['AA']

logging.basicConfig()
log = logging.getLogger('wfs_time_entry')
log.setLevel(logging.INFO)

tm = modelserver.TableManager.instance()


class TimeEntry(WFSReport):

    def __init__(self, type='TIME', release=True, test=False):
        WFSReport.__init__(self, type, release, test)
        self.headers = HEADERS
        self.cached_salary_wfs = self.generate_salary_wfs()
        self.cached_account_data = self.generate_account_data()
        self.paycode_handler = PaycodeHandler()

        # Setup salary month parameters. Some rave variables used
        # checks against these parameters for validity.
        rave.param('salary.%salary_month_start_p%').setValue(self.start)
        rave.param('salary.%salary_month_end_p%').setValue(self.end)

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
            row_data['days_off'],
            None,
            None,
            row_data['record_id'],
            row_data['flag']
            ]
        return row

    def extract_data(self, crew_id):
        log.info('NORDLYS: Extracting data for Time Entry report for crew {crew}...'.format(crew=crew_id))
        data = []
        # collects the data from wfs_corrected table for corrections 
        data.extend(self._wfs_corrected(crew_id))
        # collects data from roster for hrs 
        data.extend(self._roster_events(crew_id))
        # collects data from account_entry table for days_off         
        data.extend(self._account_transactions(crew_id))
        # collects all the records that are removed from roster 
        data.extend(self._removed_records(crew_id, data))
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
        
        # collects the data in diff list on the basis of type of duty 
        non_mid_tmp_hrs = []
        mid_tmp_hrs = []
        unfit_tmp_hrs = []
        split_tmp_hrs  = []
        sick_tmp_hrs = []

        #List used in Link
        total_duty_hrs_link = []
        final_link_hrs = []

        log.info('NORDLYS: Extracting roster data for {0}'.format(crew_id))

        is_unfit_spanning = False
        # we need to skip second split duty 
        is_split = False
        split_count = 1

        is_split_link = False
        split_count_link = 1

        last_overtime_date = {"crew":crew_id,"date":self.report_start_date()}

        for roster_bag in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
            for trip_bag in roster_bag.iterators.trip_set(): 
                trip_start_day = trip_bag.trip.start_day()
                extperkey = extperkey_from_id(crew_id, trip_start_day)
                log.info('NORDLYS:crew picked up {c} '.format(c = extperkey))
                rank = rank_from_id(crew_id, trip_start_day)
                #log.debug('NORDLYS: Crew {e} has rank {r}'.format(e=extperkey, r=rank))
                actual_rank = actual_rank_from_id(crew_id, trip_start_day)
                #log.debug('NORDLYS: Crew {e} has actual rank {r}'.format(e=extperkey, r=actual_rank))
                country = country_from_id(crew_id, trip_start_day)
                for duty_bag in trip_bag.iterators.duty_set(where=where_filter):
                    mid_hrs_link = []
                    non_mid_hrs_link = []
                    split_hrs_link = []
                
                    log.info('NORDLYS:crew picked up {e} '.format(e = crew_id))
                    if not rank or not country:
                        # Not possible to evaluate anything without rank and country
                        log.info('NORDLYS: Rank or country not found')
                        continue

                    if actual_rank in EXCLUDED_RANKS:
                        log.info('NORDLYS: Skipping  crew {e} with excluded rank {r}'.format(e=extperkey, r=actual_rank))
                        continue

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
                            # no need to report free day
                            log.info('NORDLYS: Found Free day for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            continue
                        
                        tmp_paycode = self.paycode_handler.paycode_from_event('TEMP', crew_id, country, rank)
                        
                        if duty_bag.duty.has_unfit_for_flight_star():
                            # in case of unfit we need to report prev hrs before unfit 
                            log.info('NORDLYS: Found unfit duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            if is_unfit_spanning == True:
                                is_unfit_spanning = False
                            else:
                                is_unfit_spanning,unfitData = self._calculate_unfit_hrs(duty_bag,duty_start_day,is_unfit_spanning,country)
                                unfit_tmp_hrs.extend(unfitData)
                        elif duty_bag.duty.is_child_illness() or duty_bag.duty.is_on_duty_illness():
                            # in case of ill or child ill need to report prev hrs 
                            log.info('NORDLYS: Found ILL duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day))
                            sickData = self._calculate_before_sick_hrs(duty_bag,country)
                            if sickData:
                                sick_tmp_hrs.extend(sickData)                        
                        elif duty_bag.duty_period.is_split():
                            # in case of split duty need to report hrs on first day only 
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
                            # if duty is spanning over midnight then report hrs accodingly 
                            log.info('NORDLYS: Found midnight spanning duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            midData = self._temporary_mid_hours(duty_bag, duty_start_day, tmp_paycode, crew_id, extperkey)
                            if midData:
                                mid_tmp_hrs.extend(midData)
                        else:
                            # othere remaining duties are reported in normal duties 
                            log.info('NORDLYS: Found normal duty for temporary crew {crew} at {dt}'.format(crew=crew_id, dt=duty_start_day)) 
                            nonMidData = self._temporary_non_mid_hours(duty_bag, duty_start_day, tmp_paycode, crew_id, extperkey)
                            if nonMidData:
                                non_mid_tmp_hrs.extend(nonMidData)
                    # Regarding Overtime :-
                    # it is for both RP crews and non RP crews 
                    # Overtime Types - ( Late checkout , 7_calendar_days overtime )
                    # Late checkout -> for FC there is FD units , for FC overtime merge with 7_calendar_days
                    # 7_calendar_days overtime -> reports if crew did more then 47.5 hrs duty in last 7 days                                

                    if monthly_ot[abs_to_datetime(duty_start_day).month]['val'] == None:
                        month = abs_to_datetime(duty_start_day).month
                        monthly_ot = self._distribute_monthly_ot(monthly_ot, month, duty_bag)
                    
                    planning_group = planninggroup_from_id(crew_id, duty_start_day)
                    log.info('NORDLYS: planning group {z} '.format(z = planning_group))
                    if planning_group == "SVS":
                        num_of_flight = duty_bag.report_common.number_of_active_legs()
                        active_flight= duty_bag.duty.has_active_flight()
                        stby_duties = duty_bag.standby.duty_is_standby_callout()
                        if num_of_flight > 0:
                            if active_flight or stby_duties:
                                if duty_bag.duty_period.is_split():
                                    if duty_bag.duty_period.start_day_hb() < self.start:
                                        continue
                                    if is_split_link == False and split_count_link == 1:
                                        splitData,is_split_link = self._split_hrs_link(duty_bag, crew_id, country,rank,is_split_link)
                                        split_count_link += 1
                                        if splitData:
                                            split_hrs_link.extend(splitData)
                                    elif split_count == 2:
                                        is_split_link = False
                                        split_count_link = 1
                                elif duty_bag.duty.start_day() != duty_bag.duty.end_day(): #mid-night spanning
                                    duty_hrs_link = self._mid_hours_link(duty_bag, crew_id, country, rank)
                                    if duty_hrs_link:
                                        mid_hrs_link.extend(duty_hrs_link)
                                else:
                                    duty_hrs_link = self._non_mid_hours_link(duty_bag,crew_id, country , rank)
                                    if duty_hrs_link:
                                        non_mid_hrs_link.extend(duty_hrs_link)

                                final_link_hrs = split_hrs_link + non_mid_hrs_link + mid_hrs_link
                                total_duty_hrs_link.extend(final_link_hrs)
                                                                               
                        duty_illness = duty_bag.report_overtime.is_on_duty_illness_link()
                        if duty_illness and not duty_bag.duty.has_unfit_for_flight_star():
                            start_dt = abs_to_datetime(duty_start_day) + timedelta(days=0)
                            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
                            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')
                            prev_duty_hrs_before_sick = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs)
                            if prev_duty_hrs_before_sick > RelTime('0:00'):
                                sick_data_link = self._calculate_before_sick_hrs_link(duty_bag)
                                log.info('NORDLYS:Link sick data {SICK_DATA}'.format(SICK_DATA=sick_data_link))
                                sick_paycode = self.paycode_handler.paycode_from_event('CNLN_PROD_SICK', crew_id, country,rank)
                                for val in sick_data_link:
                                    valid_events.append({'paycode':sick_paycode,
                                                          'hrs':val[1],
                                                          'dt':abs_to_datetime(val[0])})
                            
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
                        log.info('{ot_hrs_45_50} {ot_hrs_50} {ot_paycode_45_50} {ot_paycode_50}'.format(ot_hrs_45_50=general_ot_hrs_45_50 , ot_hrs_50 = general_ot_hrs_50,ot_paycode_45_50 = general_ot_paycode_45_50_ot,  ot_paycode_50 =general_ot_paycode_50_ot))
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
            # Calculation for flight duty hrs for link crew
            total_duty_hrs_link = sorted(total_duty_hrs_link,key=lambda x:x[0])
            total_duty_hrs_link = self._combine_duty_hours(total_duty_hrs_link)
            log.info('NORDLYS:Total duty hrs link {hrs}'.format(hrs=total_duty_hrs_link))

            for val in total_duty_hrs_link:
                valid_events.append({'paycode':val[2],
                                        'hrs':val[1],
                                        'dt':abs_to_datetime(val[0])})      
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
                    new_recs = self._insert_or_update_record(
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
                    new_recs = self._insert_or_update_record(crew_id, extperkey, paycode, curr_dt, hrs, None)
                    data.extend(new_recs)

        return data

    def _wfs_corrected(self,crew_id):
        # this method collects the TE corrections from wfs_corrected table 
        data = []
        table = tm.table('wfs_corrected')
        uniq_dates = set()
        wfs_corrected_data = []
        final_wfs_corrected_data = []

        prev_mnth_start_dt = self.report_start_date()

        for i in table.search("(&(crew_id={crew})(work_day>={last_month}))".format(crew=crew_id,last_month=prev_mnth_start_dt)):

            rec = [i.correction_id,i.crew_id.id,i.extperkey,i.wfs_paycode,i.work_day,i.amount,i.days_off]

            wfs_corrected_data.append(rec)
            uniq_dates.add(i.work_day)
        # if multiple records are present in table it will pick only max id record 
        for dt in uniq_dates:
            mx_id = -1
            for rec in wfs_corrected_data:
                if rec[4] == dt:
                    if rec[0] > mx_id:
                        mx_id = rec[0]
                        mx_rec = rec
            final_wfs_corrected_data.append(mx_rec) 

        for rec in final_wfs_corrected_data:
            corrected_rec = self._insert_or_update_record(rec[1], rec[2], rec[3], abs_to_datetime(rec[4]), rec[5], rec[6])
            log.info("NORDLYS : wfs_corrected Record generated : {0}".format(corrected_rec))
            data.extend(corrected_rec)
        return data 
    
    def _check_in_wfs_corrected(self, crew_id, extperkey, wfs_paycode, curr_dt, hrs, days_off):
        # if correction record is present in wfs_corrected table then no need to report other record         
        table = tm.table('wfs_corrected')

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
       # collect the data before the crew sick 
       # there is a crew publish info table which helps to get the previous informed data 

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
        # this is also collect data of previous informed duty from crew publish info table 
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

    def _temporary_split_hours(self, duty_bag, start_dt, paycode, crew_id, extperkey,split_found):
        # if there is split duty spanning b/w tow days then we need to report whole hrs on first day
        # if total hrs > 24 then need to report rem = total - 24 on second day 
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
        # all the normal duties are need to report in this category
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
        # if a duty spanning over mid night then 
        # the part of duty on day one need to report on day one 
        # the part of duty on day two need to report on day two 
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
        # if duty is spanning more then a day , it will return number of days 
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
        curr_month = prev_month + relativedelta(months=1)
        last_month = curr_month + relativedelta(months=1)
        # Reportworker publish_short has end of current month + 31d
        ext_last_month = last_month + relativedelta(months=1)
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
          if dated_tnx['tnx_dt'] >= self.start:
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
            chk_wfs_corrected = self._check_in_wfs_corrected(crew_id, extperkey, wfs_paycode, abs_to_datetime(tnx_dt), None, days_off)
            if chk_wfs_corrected:
                continue
            new_recs = self._insert_or_update_record(crew_id, extperkey, wfs_paycode, abs_to_datetime(tnx_dt), None, days_off)
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

    def _insert_or_update_record(self, crew_id, extperkey, wfs_paycode, curr_dt, hours, days_off):
        data = []
        curr_abs = AbsTime(curr_dt.year, curr_dt.month, curr_dt.day, 0, 0)
        pre_recs = self._pre_existing_records_for_paycode(crew_id, curr_abs, wfs_paycode)

        if pre_recs:
            for pre in pre_recs:

                log.info('NORDLYS: Pre-existing record found on {0}. Checking for difference...'.format(curr_abs))
                #   Check if new transaction differs from pre-existing
                #   If different then
                #       Create one row with 'D' flag
                if ((days_off and pre.days_off) and (days_off != pre.days_off) and (days_off != 0)) or \
                    ((hours and pre.amount) and (hours != pre.amount) and (hours != RelTime('00:00'))):
                    
                    if pre.days_off and pre.days_off not in (0,1):
                        continue

                    log.info('NORDLYS: New record differs from pre-existing')
                    log.info('''###########################################
                    # Type                     : {type}
                    # Date                     : {dt}
                    # Previous record days_off : {pre_days_off}
                    # New record days_off      : {new_days_off}
                    # Previous record hours    : {pre_hours}
                    # New record hours         : {new_hours}
                    ###########################################'''.format(
                       type=wfs_paycode,
                       dt=curr_dt,
                       pre_days_off=pre.days_off,
                       new_days_off=days_off,
                       pre_hours=pre.amount,
                       new_hours=hours
                    ))
                    # Create delete record for pre.record_id
                    delete_row_data = {
                        'extperkey' : pre.extperkey,
                        'paycode' : pre.wfs_paycode,
                        'hours' : pre.amount, 
                        'days_off' : pre.days_off,
                        'start_dt' : abs_to_datetime(pre.work_day),
                        'record_id' : pre.recordid,
                        'flag' : 'D'
                    }
                    flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                    if flag == 0:
                        continue
                    row = self.format_row(delete_row_data)
                    log.info(row)
                    data.append(row)

                    # Create new row with 'I' flag for update
                    insert_row_data = {
                        'extperkey' : extperkey,
                        'paycode' : wfs_paycode,
                        'hours' : hours, 
                        'days_off' : days_off,
                        'start_dt' : curr_dt,
                        'record_id' : getNextRecordId(),
                        'flag' : 'I' 
                    }
                    add_to_salary_wfs_t(insert_row_data, crew_id, self.runid)
                    row = self.format_row(insert_row_data)
                    log.info(row)
                    data.append(row)
                elif days_off == 0 or hours == RelTime('00:00'):
                    # Create delete record for pre.record_id in case of correction received as 0 
                    log.info('NORDLYS: Correction received as 0')
                    delete_row_data = {
                        'extperkey' : pre.extperkey,
                        'paycode' : pre.wfs_paycode,
                        'hours' : pre.amount, 
                        'days_off' : pre.days_off,
                        'start_dt' : abs_to_datetime(pre.work_day),
                        'record_id' : pre.recordid,
                        'flag' : 'D'
                    }
                    flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                    if flag == 0:
                        continue
                    row = self.format_row(delete_row_data)
                    log.info(row)
                    data.append(row)
                elif pre.flag == 'D':
                    if (days_off and days_off > 0) or (hours and hours > RelTime('00:00')):
                        log.info('NORDLYS: Deleted pre-existing records found... Adding new record')
                        insert_row_data = {
                            'extperkey' : extperkey,
                            'paycode' : wfs_paycode,
                            'hours' : hours, 
                            'days_off' : days_off,
                            'start_dt' : curr_dt,
                            'record_id' : getNextRecordId(),
                            'flag' : 'I'
                        }
                        add_to_salary_wfs_t(insert_row_data, crew_id, self.runid)
                        row = self.format_row(insert_row_data)
                        log.info(row)
                        data.append(row)
                else:
                    # No need for update on this record. Skipping to next....
                    log.debug('NORDLYS: No update needed for this record...')
        elif days_off == 0 or hours == RelTime('00:00'):
            # if days off or hrs of new record is 0 then no need to create any entry             
            log.info('NORDLYS: No pre-existing records found... days off or hrs found as 0')
        else:
            log.info('NORDLYS: No pre-existing records found... Adding new record')
            insert_row_data = {
                'extperkey' : extperkey,
                'paycode' : wfs_paycode,
                'hours' : hours, 
                'days_off' : days_off,
                'start_dt' : curr_dt,
                'record_id' : getNextRecordId(),
                'flag' : 'I'
            }
       
            add_to_salary_wfs_t(insert_row_data, crew_id, self.runid)
            row = self.format_row(insert_row_data)
            log.info(row)
            data.append(row)
        return data

    def _pre_existing_records_for_paycode(self, crew_id, work_day, paycode):
        if self.cached_salary_wfs.has_key(crew_id) and self.cached_salary_wfs[crew_id].has_key(work_day):
            return [r for r in self.cached_salary_wfs[crew_id][work_day] if r.wfs_paycode == paycode]
        else:
            # No pre-existing records for crew on selected date
            return []

    def _removed_records(self, crew_id, data):
        curr_date = AbsTime(datetime.now().strftime('%d%b%Y'))
        extperkey = extperkey_from_id(crew_id, curr_date)
        if extperkey == crew_id:
            # Try converting crew_id as extperkey to actual crew_id
            crew_id = rave.eval('model_crew.%crew_id_from_extperkey%("{0}", {1})'.format(crew_id, curr_date))[0]

        va_va1_paycodes = ['SAS_SE_CMS_CC_VA_PERFORMED','SAS_SE_CMS_FD_VA_PERFORMED','SAS_SE_CMS_UNPAID_VACATION','SAS_NO_CMS_VA_PERFORMED', 'SAS_NO_CMS_VA1_PERFORMED','SAS_DK_VACATION_D','SAS_DK_VACATION_UNPAID_D']
        self.start_date_check = self.report_start_date_VA()
        self.end_date_check = self.report_end_date_VA()
        date_to_check = self.start_date_check
        records_to_delete = []
        roster_candidates = dict()
        log.info('NORDLYS: Comparing records in salary_wfs to account and roster for removals...')
        while date_to_check <= self.end_date_check:
            # Check if salary_wfs has any records on given date
            # if it does,  
            if self.cached_salary_wfs.has_key(crew_id) and self.cached_salary_wfs[crew_id].has_key(date_to_check):
                # Cross check with data to send,
                for rec in [r for r in self.cached_salary_wfs[crew_id][date_to_check] if r.flag == 'I']:
                    # Check for 6 months back and 12 months forward in case of VA nd VA1
                    if rec.wfs_paycode in va_va1_paycodes:
                        if self._send_data_contains_record(rec.wfs_paycode, rec.work_day, data):
                            # We can safely skip a record that we know that we will report in this run
                            continue
                        # Check account and roster
                        elif self._check_in_wfs_corrected(rec.crew, rec.extperkey, rec.wfs_paycode, abs_to_datetime(rec.work_day), None, rec.days_off):
                            continue
                        elif self._check_in_wfs_corrected(rec.crew, rec.extperkey, rec.wfs_paycode, abs_to_datetime(rec.work_day),rec.amount,None):
                            continue
                        elif self.paycode_handler.is_account_paycode(rec.wfs_paycode):
                            # Check cached account_entry for removals
                            log.info('NORDLYS: Checking account_entry for removals on {dt}...'.format(dt=date_to_check))
                            if self._account_contains_data(crew_id, date_to_check, rec.wfs_paycode):
                                # Record hasn't been removed
                                continue
                            else:
                                # Record removed from account, create delete row
                                delete_row_data = {
                                    'extperkey' : rec.extperkey,
                                    'paycode' : rec.wfs_paycode,
                                    'hours' : rec.amount,
                                    'days_off' : rec.days_off,
                                    'start_dt' : abs_to_datetime(rec.work_day),
                                    'record_id' : rec.recordid,
                                    'flag' : 'D'
                                }
                                flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                                if flag == 0:
                                    continue
                                row = self.format_row(delete_row_data)
                                log.info(row)
                                records_to_delete.append(row)
                    #  Except VA and VA1 accounts, for other paycodes check for only 3 months
                    elif rec.wfs_paycode not in va_va1_paycodes and date_to_check >= self.start and date_to_check <= self.end:
                        if self._send_data_contains_record(rec.wfs_paycode, rec.work_day, data):
                            # We can safely skip a record that we know that we will report in this run
                            log.info('NORDLYS: Checking _send_data_contains_record on {dt}...'.format(dt=date_to_check))
                            continue 
                        # Check account and roster
                        elif self._check_in_wfs_corrected(rec.crew, rec.extperkey, rec.wfs_paycode, abs_to_datetime(rec.work_day), None, rec.days_off):
                            log.info('NORDLYS: Checking _check_in_wfs_corrected for days off on {dt}...'.format(dt=date_to_check))
                            continue
                        elif self._check_in_wfs_corrected(rec.crew, rec.extperkey, rec.wfs_paycode, abs_to_datetime(rec.work_day),rec.amount,None):
                            log.info('NORDLYS: Checking _check_in_wfs_corrected for hrs on {dt}...'.format(dt=date_to_check))
                            continue
                        elif self.paycode_handler.is_account_paycode(rec.wfs_paycode):
                            # Check cached account_entry for removals
                            log.info('NORDLYS: Checking account_entry for removals on {dt}...'.format(dt=date_to_check))
                            if self._account_contains_data(crew_id, date_to_check, rec.wfs_paycode):
                                # Record hasn't been removed
                                continue
                            else:
                                # Record removed from account, create delete row
                                delete_row_data = {
                                    'extperkey' : rec.extperkey,
                                    'paycode' : rec.wfs_paycode,
                                    'hours' : rec.amount,
                                    'days_off' : rec.days_off,
                                    'start_dt' : abs_to_datetime(rec.work_day),
                                    'record_id' : rec.recordid,
                                    'flag' : 'D'
                                }
                                flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                                if flag == 0:
                                    continue 
                                row = self.format_row(delete_row_data)
                                log.info(row)
                                records_to_delete.append(row)
                        else:
                            # Check roster for removals
                            roster_candidates.setdefault(date_to_check, [])
                            roster_candidates[date_to_check].append({
                                'rec'   : rec,
                                'event' : self.paycode_handler.event_from_paycode(rec.wfs_paycode)
                            })
            date_to_check = date_to_check.adddays(1)
 
        if len(roster_candidates) > 0:
            log.info('NORDLYS: About to check the following on roster: {0}'.format(roster_candidates))
            records_to_delete.extend(self._removed_from_roster(crew_id, roster_candidates))
        return records_to_delete

    def _account_contains_data(self, crew_id, dt, paycode):
        '''
        Checks if any account event has been removed since last run

        Example:
        salary_wfs table contains data on VA on 24DEC2020
        Since last run crew has become ill on 24DEC2020 and an
        IL4 has replaced the VA on roster, resulting in no deduction
        from VA account on 24DEC2020. A delete record must be sent
        for VA on 24DEC2020 to keep information in sync.
        '''
        account = self.paycode_handler.event_from_paycode(paycode)
        if self.cached_account_data.has_key(crew_id):
            return len([r for r in self.cached_account_data[crew_id] if r['tnx_dt'].day_floor() == dt and r['tnx'].account.id == account]) > 0
        else:
            return False

    def _removed_from_roster(self, crew_id, candidates):
        '''
        Checks if any event of OT, OT_LATE_CO or TEMP can be considered as 
        removed from the roster. 

        Example:
        salary_wfs table contains data on TEMP hours on 20DEC2020
        Since the last run these hours now has been removed, then
        we create a delete record for that previously sent record
        of TEMP hours on 20DEC2020.
        '''
        removed_from_roster = []
        roster_duty_dates = []
        mid_night_dates = []
        is_split = 0
        day1_rec = {}

        for roster_bag in rave.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
            for trip_bag in roster_bag.iterators.trip_set():
                for duty_bag in trip_bag.iterators.duty_set():
                    duty_start_dt = duty_bag.duty.start_day()
                    roster_duty_dates.append((crew_id,duty_start_dt))
                    recs_to_remove = []
                    if self._block_activity(duty_bag) and self._candidate_within_block(duty_bag, candidates):
                        # Start evaluation on second day of block. First day is still possible for normal evaluation
                        second_day = duty_start_dt.adddays(1)
                        log.info("NORDLYS: Before _remove_event_replaced_by_block working for dt {0}".format(duty_start_dt))
                        if duty_bag.crew.is_temporary_at_date(duty_start_dt):
                            if duty_bag.duty.has_unfit_for_flight_star():
                                if duty_bag.duty.start_day() != duty_bag.duty.end_day():
                                    log.info("NORDLYS: Found unfit , midnight or temp duty for removal")
                        else:
                            recs_to_remove.extend(self._remove_event_replaced_by_block(second_day, duty_bag.duty.end_day(), candidates))
                            log.info("NORDLYS: Added _remove_event_replaced_by_block {0}".format(recs_to_remove))
                    
                    if candidates.has_key(duty_start_dt) == False and duty_bag.duty_period.is_split():
                        log.info("NORDLYS: Setting is_split to zero in removal")
                        is_split = 0
                    
                    if candidates.has_key(duty_start_dt):
                        log.info('NORDLYS: Looking for removals on roster on {dt}'.format(dt=duty_start_dt))
                        general_ot = [r for r in candidates[duty_start_dt] if r['event'] == 'OT']
                        ot_late_co = [r for r in candidates[duty_start_dt] if r['event'] == 'OT_LATE_CO']
                        temp = [r for r in candidates[duty_start_dt] if r['event'] == 'TEMP']
                        saslink_7_calendar_45_50_ot = [r for r in candidates[duty_start_dt] if r['event'] == 'CNLN_OT_45_50']
                        saslink_7_calendar_50_ot = [r for r in candidates[duty_start_dt] if r['event'] ==  'CNLN_OT_50_PLUS']
                        saslink_land_day_off_ot = [r for r in candidates[duty_start_dt] if r['event'] ==  'CNLN_LAND_DAY_OFF']
                        saslink_weekend_holiday = [r for r in candidates[duty_start_dt] if r['event'] ==  'CNLN_PROD_WEEKEND']
                        saslink_weekday = [r for r in candidates[duty_start_dt] if r['event'] ==  'CNLN_PROD_WEEKDAY']
                        saslink_sick = [r for r in candidates[duty_start_dt] if r['event'] ==  'CNLN_PROD_SICK']

                        # Check if any event can be considered removed from the roster
                        if len(general_ot) > 0:
                            log.info('NORDLYS: Checking for removed general overtime on roster on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_general_ot(crew_id, duty_bag, duty_start_dt, general_ot))

                        elif len(ot_late_co) > 0:
                            log.info('NORDLYS: Checking for removed late checkout overtime on roster on {dt}'.format(dt=duty_start_dt))
                            if (duty_bag.report_overtime.OT_FD_units() == 0):
                                recs_to_remove.append(ot_late_co[0]['rec'])
                        
                        elif len(saslink_7_calendar_45_50_ot) > 0:
                            log.info('NORDLYS: Checking for removed overtime in 7 calendar day for 45 to 50 hrs on roster on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_7_calendar_45_50_ot(crew_id, duty_bag, duty_start_dt, saslink_7_calendar_45_50_ot))

                        elif len(saslink_7_calendar_50_ot) > 0:
                            log.info('NORDLYS: Checking for removed overtime in 7 calendar days for 50 hrs or more on roster on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_7_calendar_50_ot(crew_id, duty_bag, duty_start_dt, saslink_7_calendar_50_ot))
                        
                        elif len(saslink_land_day_off_ot) > 0:
                            log.info('NORDLYS: Checking for removed overtime on day-off on roster on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_land_day_off_ot(crew_id, duty_bag, duty_start_dt, saslink_land_day_off_ot))
                        
                        elif len(saslink_weekend_holiday) > 0:
                            log.info('NORDLYS: Checking for removed flight duty hrs on weekend or holiday for link on roster on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_weekend_holiday_hrs(crew_id, duty_bag, duty_start_dt, saslink_weekend_holiday))
                        
                        elif len(saslink_weekday) > 0:
                            log.info('NORDLYS: Checking for removed flight duty hrs on weekdays on roster for link on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_weekday_hrs(crew_id, duty_bag, duty_start_dt, saslink_weekday))

                        elif len(saslink_sick) > 0:
                            log.info('NORDLYS: Checking for removed sick hrs on roster for link on {dt}'.format(dt=duty_start_dt))    
                            recs_to_remove.extend(self._remove_saslink_sick(crew_id, duty_bag, duty_start_dt, saslink_sick))
                        
                        elif len(temp) > 0:
                            if duty_bag.crew.is_temporary_at_date(duty_start_dt):
                                log.info('NORDLYS: Checking for removed tempcrew hours on roster on {dt}'.format(dt=duty_start_dt))
                                if duty_bag.duty.has_unfit_for_flight_star():
                                    if duty_bag.duty.start_day() != duty_bag.duty.end_day():
                                        roster_duty_dates.append((crew_id,duty_bag.duty.end_day()))
                                elif country_from_id(crew_id, self.start) != 'SE' and (duty_bag.duty.is_child_illness() or duty_bag.duty.is_on_duty_illness()):
                                    days = (int(str(duty_bag.duty.end_day() - duty_bag.duty.start_day()).split(':')[0])//24) + 1
                                    for i in range(days):
                                        roster_duty_dates.append((crew_id,duty_bag.duty.start_day().adddays(i)))
                                        log.info('NORDLYS: Skip deletion of sick duty data')
                                elif duty_bag.duty_period.is_split():
                                    log.info('NORDLYS: Split duty checking for removal')
                                    is_split += 1
                                    day1_rec , is_del = self._remove_last_day_split(duty_bag,is_split,day1_rec)
                                    if is_del and is_split == 2:
                                        is_split = 0
                                        recs_to_remove.append(temp[0]['rec'])
                                        log.info('NORDLYS: Found hrs on second day of of split duty in salary wfs')
                                elif self._is_mid_night_spanning(duty_bag):
                                    roster_duty_dates.append((crew_id,duty_bag.duty.end_day()))
                                    mid_night_dates.append(duty_bag.duty.end_day())
                                elif duty_bag.duty.is_privately_traded() and duty_bag.duty.is_freeday():
                                    recs_to_remove.append(temp[0]['rec'])
                                    log.info('NORDLYS: Found Free Privately traded duty on roster')
                                elif duty_bag.duty.is_privately_traded() and country_from_id(crew_id, duty_bag.duty.start_day()) == 'DK':
                                    roster_duty_dates.append((crew_id,duty_bag.duty.start_day()))
                                    log.info('NORDLYS: Found DK Privately traded duty on roster')
                                elif default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_start_dt)) == RelTime('00:00'):
                                    if not duty_bag.duty_period.is_split() and not self._is_mid_night_spanning(duty_bag) and not duty_bag.duty.has_unfit_for_flight_star():
                                        if duty_start_dt not in mid_night_dates:
                                            recs_to_remove.append(temp[0]['rec'])
                                            log.info('NORDLYS: Found duty with 0 hrs on roster for removal')

                                # its creating wrong tmp hrs 
                                # if default_reltime(duty_bag.report_overtime.temporary_crew_hours_per_calendar_day(duty_start_dt)) == RelTime('00:00'):

                    for rec in recs_to_remove:
                        delete_row_data = {
                                'extperkey' : rec.extperkey,
                                'paycode' : rec.wfs_paycode,
                                'hours' : rec.amount, 
                                'days_off' : rec.days_off,
                                'start_dt' : abs_to_datetime(rec.work_day),
                                'record_id' : rec.recordid,
                                'flag' : 'D' 
                            }
                        flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                        if flag == 0:
                            continue
                        row = self.format_row(delete_row_data)
                        log.info('NORDLYS: Found removed record on roster {0}'.format(row))
                        removed_from_roster.append(row)

        roster_dates = [rec_roster[1] for rec_roster in roster_duty_dates]
        for rec_salary_wfs in candidates.keys():
            if rec_salary_wfs not in roster_dates:
                if not (candidates[rec_salary_wfs][0]['rec'].work_day >= self.start and candidates[rec_salary_wfs][0]['rec'].work_day <= self.end):
                    continue
                delete_row_data = {
                    'extperkey' : candidates[rec_salary_wfs][0]['rec'].extperkey,
                    'paycode' : candidates[rec_salary_wfs][0]['rec'].wfs_paycode,
                    'hours' : candidates[rec_salary_wfs][0]['rec'].amount, 
                    'days_off' : candidates[rec_salary_wfs][0]['rec'].days_off,
                    'start_dt' : abs_to_datetime(candidates[rec_salary_wfs][0]['rec'].work_day),
                    'record_id' : candidates[rec_salary_wfs][0]['rec'].recordid,
                    'flag' : 'D' 
                }

                # removed roster duty only for OT and TEMP code 
                if 'OT' in delete_row_data['paycode'] or 'TEMP' in delete_row_data['paycode']:
                    flag = add_to_salary_wfs_t(delete_row_data, crew_id, self.runid)
                    if flag == 0:
                        continue
                    row = self.format_row(delete_row_data)
                    log.info('NORDLYS: Record doesnt exist on roster {0}'.format(row))
                    removed_from_roster.append(row)

        return removed_from_roster

    def _remove_last_day_split(self, duty_bag,is_split,day1_rec):
        # to mark second day split duty as 'D' as now all the split hrs are reported on day1 
        if is_split == 1:
            day1_rec = {
                'day1_split': is_split ,
                'day1_start_dt' : duty_bag.duty.start_day(),
                'day1_end_dt': duty_bag.duty.end_day(),
            }
            return day1_rec,False
        elif is_split == 2:
            if day1_rec['day1_start_dt'] != duty_bag.duty.start_day():
                return day1_rec,True
            else:
                return day1_rec,False
    
    def _send_data_contains_record(self, wfs_paycode, abs_dt, data):
        # data is formatted as described in format_row() function
        dt = abs_to_datetime(abs_dt).strftime('%Y-%m-%d')
        try:
            rec_found = any((dt == rec[2] and wfs_paycode == rec[1]) for rec in data)
        except Exception:
            log.info('NORDLYS: _send_data_contains_record contains exception for {0}'.format(abs_dt))
            rec_found = False
        return rec_found

    def _block_activity(self, duty_bag):
        if duty_bag.duty.is_off_duty(): 
            return duty_bag.duty.start_day() <> duty_bag.duty.end_day()
        return False
    
    def _candidate_within_block(self, duty_bag, candidates):
        curr_day = duty_bag.duty.start_day().adddays(1)
        end_day = duty_bag.duty.end_day()
        while curr_day <= end_day:
            if candidates.has_key(curr_day):
                return True
            curr_day = curr_day.adddays(1)

    def _remove_event_replaced_by_block(self, block_start, block_end, candidates):
        curr = block_start
        block_removals = []
        while curr <= block_end:
            if candidates.has_key(curr):
                general_ot = [r for r in candidates[curr] if r['event'] == 'OT']
                ot_late_co = [r for r in candidates[curr] if r['event'] == 'OT_LATE_CO']
                temp = [r for r in candidates[curr] if r['event'] == 'TEMP']
                
                if len(general_ot) > 0:
                    log.debug('NORDLYS: General overtime replaced by off-duty block activity.. Removing old overtime record')
                    block_removals.append(general_ot[0]['rec'])
                elif len(ot_late_co) > 0:
                    log.debug('NORDLYS: Late checkout overtime replaced by off-duty block activity.. Removing old overtime record')
                    block_removals.append(ot_late_co[0]['rec'])
                elif len(temp) > 0:
                    log.debug('NORDLYS: Tempcrew hours replaced by off-duty block activity.. Removing old record')
                    block_removals.append(temp[0]['rec'])
            curr = curr.adddays(1)
        return block_removals
    
    def _remove_general_ot(self, crew_id, duty_bag, duty_start_dt, general_ot):
        general_ot_removals = []
        if default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot()) == RelTime('00:00'):
            if abs_to_datetime(duty_start_dt).day == 1 and default_reltime(duty_bag.report_overtime.overtime_month_ot()) > RelTime('00:00'):
                # Catch cases where monthly OT previously has been registered on this date
                log.debug('NORDLYS: Monthly overtime registered on {0}, no removal applicable'.format(duty_start_dt))
            elif rank_from_id(crew_id, duty_start_dt) == 'CC' and default_reltime(duty_bag.report_overtime.overtime_late_checkout_ot() > RelTime('00:00')):
                # late checkout overtime is merged into general overtime for cabin crew
                log.debug('NORDLYS: Cabin crew with late co ot on {0}, no removal applicable'.format(duty_start_dt))
            else:
                general_ot_removals.append(general_ot[0]['rec'])
        return general_ot_removals

    def _remove_saslink_7_calendar_45_50_ot(self, crew_id, duty_bag, duty_start_dt, saslink_7_calendar_45_50_ot):
        general_ot_45_to_50_removals_svs = []
        if (default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot_45_50_svs()) == RelTime('00:00')) :
            general_ot_45_to_50_removals_svs.append(saslink_7_calendar_45_50_ot[0]['rec'])
        return general_ot_45_to_50_removals_svs

    def _remove_saslink_7_calendar_50_ot(self, crew_id, duty_bag, duty_start_dt, saslink_7_calendar_50_ot):
        general_ot_50_removals_svs = []
        if (default_reltime(duty_bag.report_overtime.overtime_7_calendar_days_ot_50_svs()) == RelTime('00:00')) :
            general_ot_50_removals_svs.append(saslink_7_calendar_50_ot[0]['rec'])
        return general_ot_50_removals_svs
    
    def _remove_saslink_land_day_off_ot(self, crew_id, duty_bag, duty_start_dt, saslink_land_day_off_ot):
        general_ot_day_off_removals_svs = []
        if (default_reltime(duty_bag.report_overtime.OT_units_SVS()) == RelTime('00:00')) :
            general_ot_day_off_removals_svs.append(saslink_land_day_off_ot[0]['rec'])
        return general_ot_day_off_removals_svs

    def _remove_saslink_weekend_holiday_hrs(self, crew_id, duty_bag, duty_start_dt, saslink_weekend_holiday):
        general_weekend_holiday_hrs_removals = []
        if (RelTime(duty_bag.report_overtime.active_duty_hrs()) == RelTime('00:00')):
            general_weekend_holiday_hrs_removals.append(saslink_weekend_holiday[0]['rec'])
        return general_weekend_holiday_hrs_removals

    def _remove_saslink_weekday_hrs(self, crew_id, duty_bag, duty_start_dt, saslink_weekday):
        general_weekdays_hrs_removal = []
        if (RelTime(duty_bag.report_overtime.active_duty_hrs()) == RelTime('00:00')):
            general_weekdays_hrs_removal.append(saslink_weekday[0]['rec'])
        return general_weekdays_hrs_removal

    def _remove_saslink_sick(self, crew_id, duty_bag, duty_start_dt, saslink_sick):
        sick_hrs = []
        start_dt = abs_to_datetime(duty_start_dt) + timedelta(days=0)
        start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
        start_dt_end_abs = start_dt_start_abs + RelTime('24:00')
        prev_duty_hrs_before_sick = default_reltime(duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs,start_dt_end_abs))
        if prev_duty_hrs_before_sick == RelTime('00:00'):
            sick_hrs.append(saslink_sick[0]['rec'])
        return sick_hrs

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

    def report_start_date_VA(self):
        now = datetime.now()
        six_months_back = datetime(now.year, now.month, 1) + relativedelta(months=-6)
        va_start_dt = AbsTime(six_months_back.year, six_months_back.month, six_months_back.day, 0, 0)
        log.info('NORDLYS: Start Date for VA and VA1: {startdate}'.format(startdate=va_start_dt))
        return va_start_dt

    def report_end_date_VA(self):
        '''
        return: AbsTime date 12 months forward than the current month
        28 Jun 21 is Current Month then return 30 Jun 22        
        '''
        now = datetime.now()
        curr_month_end = datetime(now.year, now.month, 1) + relativedelta(months=1, days=-1)
        twelve_month_forward = datetime(now.year, now.month, 1) + relativedelta(months=13, days=-1)
        end_dt_abs = AbsTime(twelve_month_forward.year, twelve_month_forward.month, twelve_month_forward.day, 0, 0)
        log.debug('NORDLYS: End Date for VA and VA1: {enddate}'.format(enddate=end_dt_abs))
        return end_dt_abs

    '''
    Cache functions START
    '''
    def generate_salary_wfs(self, recs=None):
        '''
        Function for creating a cache of valid salary_wfs entries to check against.
        There is only ever a need to check for differences in values from the latest
        inserted value (i.e max(recordid)). The data is moved from an iterator
        to a dict structured like below:
            dict = {
                crewid_1 : {
                    work_day_1 : [
                        record_1_day_1,
                        record_2_day_1
                    ],
                    work_day_2 : [
                        record_1_day_2
                    ]
                },
                crewid_2 : {
                    ...
                }
            }
        '''
        log.info('NORDLYS: Executing generate_salary_wfs function...')
        salary_wfs_t = tm.table('salary_wfs')
        # Update this date duration as for VA and VA1 6 months back and 12 months forward data to be loaded
        self.start_date= self.report_start_date_VA()
        self.end_date=self.report_end_date_VA()
        
        log.info('NORDLYS: Start Date for VA and VA1: {startdate} and End Date: {enddate}'.format(startdate=self.start_date,enddate=self.end_date))
        
        va_va1_paycodes = ['SAS_SE_CMS_CC_VA_PERFORMED','SAS_SE_CMS_FD_VA_PERFORMED','SAS_SE_CMS_UNPAID_VACATION','SAS_NO_CMS_VA_PERFORMED', 'SAS_NO_CMS_VA1_PERFORMED','SAS_DK_VACATION_D','SAS_DK_VACATION_UNPAID_D']
        
        wfs_va_paycode_query = '(|(wfs_paycode=SAS_SE_CMS_CC_VA_PERFORMED)(wfs_paycode=SAS_SE_CMS_FD_VA_PERFORMED)(wfs_paycode=SAS_SE_CMS_UNPAID_VACATION)(wfs_paycode=SAS_NO_CMS_VA_PERFORMED)(wfs_paycode=SAS_NO_CMS_VA1_PERFORMED)(wfs_paycode=SAS_DK_VACATION_D)(wfs_paycode=SAS_DK_VACATION_UNPAID_D))'

        dict_r = {}

        if not recs:
            recs_va = salary_wfs_t.search('(&(work_day>={start})(work_day<={end}){wfs_va_paycode_query})'.format(
                        start=self.start_date,
                        end=self.end_date,
                        wfs_va_paycode_query = wfs_va_paycode_query
                    ))

        for rec in recs_va:
            # Setting default values for dynamic key allocation
            dict_r.setdefault(rec.crew, {})
            dict_r[rec.crew].setdefault(rec.work_day, [])
            # Store intermediate list while checking for max values
            sub_list = [r for r in dict_r[rec.crew][rec.work_day] if r.wfs_paycode == rec.wfs_paycode]
            largest_record_id = heapq.nlargest(1, sub_list, key=lambda r: r.recordid)
            
            # Cut checking values while doing checks
            dict_r[rec.crew][rec.work_day] = [r for r in dict_r[rec.crew][rec.work_day] if r.wfs_paycode != rec.wfs_paycode]
            if len(largest_record_id) == 0 or rec.recordid > largest_record_id[0].recordid:
                # Add record with highest recordid, or first record to be added
                dict_r[rec.crew][rec.work_day].append(rec)

        if not recs:
            recs = salary_wfs_t.search('(&(work_day>={start})(work_day<={end}))'.format(
                        start=self.start,
                        end=self.end
                    ))

        for rec in recs:
            if rec.wfs_paycode in va_va1_paycodes:
                continue
            # Setting default values for dynamic key allocation
            dict_r.setdefault(rec.crew, {})
            dict_r[rec.crew].setdefault(rec.work_day, [])
            # Store intermediate list while checking for max values
            sub_list = [r for r in dict_r[rec.crew][rec.work_day] if r.wfs_paycode == rec.wfs_paycode]
            largest_record_id = heapq.nlargest(1, sub_list, key=lambda r: r.recordid)
            
            # Cut checking values while doing checks
            dict_r[rec.crew][rec.work_day] = [r for r in dict_r[rec.crew][rec.work_day] if r.wfs_paycode != rec.wfs_paycode]
            if len(largest_record_id) == 0 or rec.recordid > largest_record_id[0].recordid:
                # Add record with highest recordid, or first record to be added
                dict_r[rec.crew][rec.work_day].append(rec)

        return dict_r
   
    def generate_account_data(self):
        account_entry_t = tm.table('account_entry')
        account_query = '(|(account=BOUGHT)(account=BOUGHT_BL)(account=BOUGHT_FORCED)(account=BOUGHT_8)(account=SOLD))'
        reasoncode_query = '(|(reasoncode=BOUGHT)(reasoncode=SOLD))'
        query_f3_f7 = '&(|(account=F3)(account=F7))(|(reasoncode=OUT Payment)(reasoncode=IN Payment Correction))'

        transactions = account_entry_t.search('(&(tim>={st})(tim<={end})(|(&{account_query}{reasoncode_query})({query_f3_f7})))'.format(
            st=self.start.adddays(-7),
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
        # Time duration changed for VA and VA1 Six months back and 12 months forward for vacation balance
        self.start_date_va = self.report_start_date_VA()
        self.end_date_va =  self.report_end_date_VA()
        account_query = '(|(account=VA)(account=VA1))'
        reasoncode_query = '(|(reasoncode=OUT Roster))'
        transactions_va = account_entry_t.search('(&(tim>={st})(tim<={end}){account_query}{reasoncode_query})'.format(
            st=self.start_date_va,
            end=self.end_date_va,
            account_query=account_query,
            reasoncode_query=reasoncode_query
        ))
        for tnx in transactions_va: 
            dict_t.setdefault(tnx.crew.id, [])
            nr_days = abs(int(tnx.amount / 100))
            curr_abs = tnx.tim
            for day in range(0, nr_days):
                if curr_abs >  self.end_date_va:
                    # Activity starts after set end date
                    break
                dict_t[tnx.crew.id].append({
                    'tnx_dt'        : curr_abs,
                    'tnx'           : tnx,
                    'days_off'      : 1})
                curr_abs = curr_abs.adddays(1)

        log.info('NORDLYS: {0} total nr of crew with account data extracted with VA/VA1'.format(len(dict_t)))
        return dict_t
    '''
    Cache functions END
    '''
     
    '''
    Link Flight Duty Function Start
    '''
    def _calculate_before_sick_hrs_link(self,duty_bag):
        '''reports illness hrs for link crew.'''
        rec = []
        duty_start_day = duty_bag.duty.start_day()
        duty_end_day = duty_bag.duty.end_day()

        days = abs(abs_to_datetime(duty_end_day) - abs_to_datetime(duty_start_day)).days
        sick_hrs = RelTime('24:00')
        for i in range(days+1):
            data_day = duty_start_day.adddays(i)

            data = (data_day,sick_hrs)

            rec.append(data)
				
        return rec

    def _mid_hours_link(self, duty_bag, crew_id, country, rank):
        '''Reports splitted duty hrs/paycode/day in case of mid night spanning'''
        duty_start_day = duty_bag.duty.start_day()
        duty_end_day = duty_bag.duty.end_day()
        checkin_post_stby = RelTime(duty_bag.report_overtime.checkin_post_sb())
        stby_start = duty_bag.report_overtime.stand_callout_at_start()
        start_dt = abs_to_datetime(duty_start_day)
        end_dt = abs_to_datetime(duty_end_day)
        start_time = RelTime(duty_bag.report_overtime.duty_starttime())
        end_dttime = RelTime(duty_bag.report_overtime.duty_endtime())
        day1_hrs = RelTime('0:00')
        day2_hrs = RelTime('0:00')
        if start_time > RelTime('0:00'):
            if stby_start:
                day1_hrs = RelTime('24:00') - checkin_post_stby
                day2_hrs = end_dttime
            else: 
                day1_hrs = RelTime('24:00') - start_time
                day2_hrs = end_dttime

        if self.is_weekend(start_dt) or duty_bag.report_roster.is_public_holiday_link(duty_start_day):
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND', crew_id, country,rank)
        else:
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY', crew_id, country,rank)

        if self.is_weekend(end_dt) or duty_bag.report_roster.is_public_holiday_link(duty_end_day):
            paycode_end_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND', crew_id, country,rank)
        else:
            paycode_end_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY', crew_id, country,rank)

        mid_night_data = None
        if day1_hrs != RelTime('0:00') and day2_hrs != RelTime('0:00'):
            mid_night_data = [(duty_start_day,day1_hrs,paycode_start_day),(duty_end_day,day2_hrs,paycode_end_day)]

        return mid_night_data
		

    def _non_mid_hours_link(self, duty_bag, crew_id, country, rank):
        '''Reports duty hrs/paycode/day when duty is ending on same day for link crew'''
        link_hrs_list = []
        duty_start_day = duty_bag.duty.start_day()
        curr_abs = abs_to_datetime(duty_start_day)

        if self.is_weekend(curr_abs) or duty_bag.report_roster.is_public_holiday_link(duty_start_day):
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND', crew_id, country,rank)
        else:
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY', crew_id, country,rank)       

        active_hours = RelTime(duty_bag.report_overtime.active_duty_hrs())

        link_hrs_list.append((duty_start_day, active_hours,paycode_start_day))
		
        return link_hrs_list
		
	
    def _combine_duty_hours(self, day_hours_link):
        '''Reports combined duty hrs for same day and same paycode in day_hours_link'''
        updated = []
        updated_dates = []
        for record in day_hours_link:
            if record[0] in updated_dates:
                for index, value in enumerate(updated):
                    if value[0] == record[0]:
                        active_hours = value[1] + record[1]
                        log.debug("NORDLYS: {0} First: {1}, Second: {2}".format(active_hours, value[1], record[1]))
                        updated[index] = (record[0], active_hours, record[2])
                        break
            else:
                updated.append(record)
                updated_dates.append(record[0])    
        return updated

    def _split_hrs_link(self,duty_bag, crew_id, country,rank,split_found):
        '''Reports duty hrs for split duty for link crew'''
        duty_start = duty_bag.duty_period.start_day_hb()
        duty_end = duty_bag.duty_period.end_day_hb()
        checkin_post_stby = RelTime(duty_bag.report_overtime.checkin_post_sb())
        stby_start = duty_bag.report_overtime.stand_callout_at_start()

        country = country_from_id(crew_id, duty_start)
        start_dt = abs_to_datetime(duty_start)
        end_dt = abs_to_datetime(duty_end)
        
        split_found = True
        day1_hrs = RelTime(duty_bag.report_overtime.split_duty_starttime())
        day2_hrs = RelTime(duty_bag.report_overtime.split_duty_endtime())

        if self.is_weekend(start_dt) or duty_bag.report_roster.is_public_holiday_link(duty_start):
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND', crew_id, country,rank)
        else:
            paycode_start_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY', crew_id, country,rank)

        if day1_hrs > RelTime('00:00'):
            if duty_start != duty_end:
                if self.is_weekend(end_dt) or duty_bag.report_roster.is_public_holiday_link(duty_end):
                    paycode_end_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKEND', crew_id, country,rank)
                else:
                    paycode_end_day = self.paycode_handler.paycode_from_event('CNLN_PROD_WEEKDAY', crew_id, country,rank)

                if stby_start:
                    first_day_hrs = RelTime('24:00') - checkin_post_stby
                    second_day_hrs = day2_hrs                    
                else:
                    first_day_hrs = RelTime('24:00') - day1_hrs
                    second_day_hrs = day2_hrs

                data_split = [(duty_start,first_day_hrs,paycode_start_day),(duty_end,second_day_hrs,paycode_end_day)]
                log.debug("NORDLYS: Split hrs are {0}".format(data_split))
            else:
                if stby_start:
                    final_hrs = day2_hrs - checkin_post_stby
                else:
                    final_hrs = day2_hrs - day1_hrs
                data_split = [(duty_start,final_hrs,paycode_start_day)]
                log.debug("NORDLYS: Split hrs are {0}".format(data_split))

        return data_split,split_found


    def is_weekend(self,start):
        '''function to check a day is weekday/weekend '''
        weekday_num = start.weekday()
        
        log.info('NORDLYS: Weekday Day Number {sd}'.format(sd=weekday_num))
        
        if ((weekday_num <= 4 )):
            log.debug('NORDLYS: Day is between Monday or Friday {day}'.format(day=weekday_num))
            return False
        else:
            log.debug('NORDLYS: Day is Sunday and Saturday or public holiday {day}'.format(day=weekday_num))
            return True
        return False

    '''
    Link Flight Duty Function End
    '''
		
'''
Class used for doing reruns from existing runid in salary_wfs table. 
Derived from TimeEntry class and overrides the generate function 
from WFSReport class. 
Only used for reruns, does not insert any new data in salary_wfs. 
'''
class Rerun(TimeEntry):

    def __init__(self, runid, type='RERUN', test=False):
        TimeEntry.__init__(self, type, test)
        self.runid = runid
        self.cached_salary_wfs = self._possible_updated_records()
        CARMDATA = os.getenv('CARMDATA')
        self.report_path = CARMDATA + '/REPORTS/SALARY_WFS/'     

    def generate(self, crew_ids):
        start_t = time.time()
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)

        se_report = self.create_report_file('SE')
        no_report = self.create_report_file('NO')
        dk_report = self.create_report_file('DK')

        data = self._rerun_from_db(self.runid)
        # crew_ids not supplied since rerun on existing data
        crew_ids = set([row[0] for row in data])
        for crew in list(crew_ids):
            crew_rows = [r for r in data if r[0] == crew]
            country = country_from_id(crew, self.start)
            if country == 'SE':
                self.write_to_report(crew_rows, se_report)
            elif country == 'NO':
                self.write_to_report(crew_rows, no_report)
            elif country == 'DK':
                self.write_to_report(crew_rows, dk_report)
        
        end_t = time.time()
        exec_time = round(end_t - start_t, 2)
        log.info('''
        #########################################################
        # WFS {type} report
        # Runid                 : {runid}
        # Execution date        : {dt}
        # Nr of crew evaluated  : {nr_crew}
        # Nr records created    : {nr_recs}
        # Execution time        : {time} sec
        # Report files located in {report_path}
        # SE : {se_report}
        # NO : {no_report}
        # DK : {dk_report}
        #########################################################'''.format(
            type=self.type,
            runid=self.runid,
            dt=datetime.now(),
            nr_crew='N/A', 
            nr_recs=len(data), 
            time=exec_time,
            report_path=self.report_path,
            se_report=se_report,
            no_report=no_report,
            dk_report=dk_report))

        
    def _possible_updated_records(self):
        salary_wfs_t = tm.table('salary_wfs')
        updates = salary_wfs_t.search('(runid>{runid})'.format(runid=self.runid))
        cached_updates = self.generate_salary_wfs(updates)
        return cached_updates

    def _rerun_from_db(self, runid):
        rerun_data = []
        salary_wfs_t = tm.table('salary_wfs')
        rerun_recs = salary_wfs_t.search('(runid={runid}))'.format(runid=self.runid))
    
        for rec in rerun_recs:
            log.info(rec)
            updated_records = self._pre_existing_records_for_paycode(rec.crew, rec.work_day, rec.wfs_paycode)
            if updated_records: 
                # this record has been exceeded by another update further ahead
                log.info('NORDLYS: Record exceeded by an update at a later time. Skipping generation of this record')
                log.info(rec)
                continue
            # format rows and write to new report files. No need to save
            rerun_row_data = {
                    'extperkey' : rec.extperkey,
                    'paycode' : rec.wfs_paycode,
                    'hours' : rec.amount, 
                    'days_off' : rec.days_off,
                    'start_dt' : abs_to_datetime(rec.work_day),
                    'record_id' : rec.recordid,
                    'flag' : rec.flag 
                }
            row = self.format_row(rerun_row_data)
            log.info('NORDLYS: Adding {row}'.format(row=row))
            rerun_data.append(row)
        return rerun_data

    
