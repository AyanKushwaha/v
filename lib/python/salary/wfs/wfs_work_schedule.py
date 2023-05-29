"""
Handler for generating roster/schema data and storing as file
"""

from AbsTime import AbsTime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import carmensystems.rave.api as r
import logging
import os, stat
from utils.selctx import SingleCrewFilter
from salary.wfs.wfs_report import WFSReport
from salary.wfs.wfs_report import abs_to_datetime, extperkey_from_id, country_from_id
from RelTime import RelTime



PAYCODE = 'SAS_SCHEDULE'
HEADERS = ('EMPLOYEE_ID', 'PAY_CODE', 'WORK_DT', 'HOURS', 'START_DTTM', 'END_DTTM')


logging.basicConfig()
log = logging.getLogger('wfs_work_schedule')
log.setLevel(logging.INFO)



class WorkSchedule(WFSReport):

    def __init__(self, release=True, test=False):
        type = 'SCHEDULE'
        WFSReport.__init__(self, type, release, test)
        self.headers = HEADERS

        if self.test:
            log.setLevel(logging.DEBUG)
    
    def format_row(self, extperkey, start_dt, end_dt):
        duty_start_date = start_dt.strftime('%Y-%m-%d')           
        row = [
            extperkey,
            PAYCODE,
            duty_start_date,
            None, 
            str(start_dt), 
            str(end_dt)
            ]
        return row

    def extract_data(self, crew_id):
        curr_date = AbsTime(datetime.now().strftime('%d%b%Y'))
        for roster_bag in r.context(SingleCrewFilter(crew_id).context()).bag().chain_set():
            log.info('NORDLYS: Extracting roster data for {0}'.format(crew_id))
            data = []
            crew = roster_bag.crew.id()
            crew = crew_id if crew is None else crew 
            log.debug('NORDLYS: Converting crew_id to extperkey on date {d}'.format(d=curr_date))
            extperkey = extperkey_from_id(crew, curr_date)
            where_filter = self.create_filter(self.start, self.end)
            log.info('NORDLYS: crew_id {0} converted to extperkey {1}'.format(crew, extperkey))
            for trip_bag in roster_bag.iterators.trip_set():
                for duty_bag in trip_bag.iterators.duty_set(where=where_filter):
                    start_hb = duty_bag.duty.start_hb()
                    end_hb = duty_bag.duty.end_hb()
                    # start_day and end_day used for eval IL7
                    start_day = duty_bag.duty.start_day()
                    end_day = start_day + RelTime('24:00')
                    log.info('NORDLYS: Extracting duty data for {0} between {1} - {2}'.format(
                        duty_bag.duty.code(),
                        start_hb,
                        end_hb)
                        )
                    if self.eligible_for_split(duty_bag):
                        # enough to check if first leg is a non-activity?
                        data.extend(self.split_activities(extperkey, duty_bag))
                    elif duty_bag.report_overtime.has_il7_in_hb_interval(start_day, end_day):
                        log.info('NORDLYS: Skipping duty combined with IL7. Counting hours in IL7...')
                        continue
                    elif duty_bag.report_overtime.has_uf_star_in_hb_interval(start_day, end_day):
                        log.info('NORDLYS: Skipping duty combined with UF codes. Counting hours in UF...')
                        continue
                    elif duty_bag.duty_period.is_split():
                        if duty_bag.duty_period.is_last_duty_in_duty_period():
                            # Skip reporting second duty in split duty to avoid reporting double values
                            log.info('NORDLYS: Skipping second duty in split duty to avoid double reporting...')
                            continue
                        duty_start_hb = abs_to_datetime(duty_bag.duty_period.start_hb())
                        duty_end_hb = abs_to_datetime(duty_bag.duty_period.end_hb())
                        nr_d = abs(duty_end_hb - duty_start_hb).days
                        if nr_d > 0:
                            res = self._split_long_duty(extperkey, duty_start_hb, duty_end_hb)
                            log.debug(res)
                            data.extend(res)
                        else:
                            row = self.format_row(extperkey, duty_start_hb, duty_end_hb)
                            log.debug(row)
                            data.append(row)
                    else:        
                        log.info('NORDLYS: Normal active duty found...')
                        duty_start_hb = abs_to_datetime(duty_bag.duty.start_hb())
                        duty_end_hb = abs_to_datetime(duty_bag.duty.end_hb())
                        nr_d = abs(duty_end_hb - duty_start_hb).days
                        if nr_d > 0:
                            res = self._split_long_duty(extperkey, duty_start_hb, duty_end_hb)
                            log.debug(res)
                            data.extend(res)
                        else:
                            row = self.format_row(extperkey, duty_start_hb, duty_end_hb)
                            log.debug(row)
                            data.append(row) 

            return data

    def _split_long_duty(self,extperkey, duty_start_hb, duty_end_hb):

        log.info('NORDLYS: Normal active long duty found...')
        new_data = []

        day_start = datetime(duty_start_hb.year, duty_start_hb.month, duty_start_hb.day, 0, 0)
        day_end = datetime(duty_end_hb.year, duty_end_hb.month, duty_end_hb.day, 0, 0)

        nr_days = (day_end - day_start).days

        for i in range(nr_days+1):
            if i == 0:
                # day1 calculation
                start_time = duty_start_hb
                end_time = duty_start_hb + timedelta(days=i+1) 
                end_time = datetime(end_time.year, end_time.month, end_time.day, 0, 0)
            elif i == nr_days:
                # last day calculation 
                start_time = duty_start_hb + timedelta(days=i)
                start_time = datetime(start_time.year, start_time.month, start_time.day, 0, 0)
                end_time = duty_end_hb
            else:
                # in b/w days calculation
                start_time = duty_start_hb + timedelta(days=i)
                end_time = start_time + timedelta(days=1)
                start_time = datetime(start_time.year, start_time.month, start_time.day, 0, 0)
                end_time = datetime(end_time.year, end_time.month, end_time.day, 0, 0)

            row = self.format_row(extperkey, start_time, end_time)
            new_data.append(row)

        return new_data

    
    def eligible_for_split(self, duty_bag):
        return duty_bag.duty.is_freeday() \
        or duty_bag.duty.is_vacation() \
        or duty_bag.duty.is_blank_day() \
        or duty_bag.duty.is_illness() \
        or duty_bag.duty.is_loa() \
        or duty_bag.duty.is_cmp() \
        or duty_bag.duty.has_unfit_for_flight_star() \
        or duty_bag.duty.is_f36() \
        or duty_bag.duty.is_sd() \
        or duty_bag.duty.is_kd() \
        or duty_bag.duty.is_gd() \
        or duty_bag.duty.is_cd()  \
        or duty_bag.duty.is_longterm_illness() \
        or duty_bag.duty.is_loa_la12()


    def split_activities(self, extperkey, duty_bag):
        
        data = []
        start = duty_bag.duty.start_day()
        end = duty_bag.duty.end_hb()
        log.info('NORDLYS: Splitting activity between {st} and {end}'.format(st=start, end=end))

        start_dt = abs_to_datetime(start)
        end_dt = abs_to_datetime(end)

        nr_days = abs(end_dt - start_dt).days
	# Added to handle the one day scenarios,When duty starts and end on same day, the day should be reported
        if nr_days == 0: 
            nr_days = 1 

        log.info('NORDLYS: Splitted into {nr} parts'.format(nr=nr_days))

        code = duty_bag.duty.code()

        for day in range(0, nr_days):
            duty_start, duty_end = self.distribute_non_activity_hours(start_dt, day, duty_bag)
            if duty_start > abs_to_datetime(self.end):
                log.debug('NORDLYS: Activity starts after set end date {0} for this schedule. Skipping activity...'.format(self.end))
                break
            log.debug('NORDLYS: Activity {0} reformatted start - end {1} - {2}'.format(code, duty_start, duty_end))

            row = self.format_row(
                extperkey, 
                duty_start, 
                duty_end
                ) 
            data.append(row)
            log.debug(row)
        return data

    def distribute_non_activity_hours(self, start_dt, day_nr, duty_bag):
        '''
        Activities considered as not having any activity on roster
        such as "F" should be splitted if assigned in block and
        the hours reported should be zero

        Example for "F":
        "F" on 20SEP2020 -> 22SEP2020 assigned as block should be reported as

        'EMPLOYEE_ID', 'PAY_CODE', 'WORK_DT', 'HOURS', 'START_DTTM', 'END_DTTM'
        12345, SAS_SCHEDULE, 20SEP2020, , 20SEP2020 00:00, 20SEP2020 00:00
        12345, SAS_SCHEDULE, 21SEP2020, , 21SEP2020 00:00, 21SEP2020 00:00
        12345, SAS_SCHEDULE, 22SEP2020, , 22SEP2020 00:00, 22SEP2020 00:00 

        Vacation acitivities should be splitted and the reported hours should always
        equal 8hr. 

        Example for "VA":
        'EMPLOYEE_ID', 'PAY_CODE', 'WORK_DT', 'HOURS', 'START_DTTM', 'END_DTTM'
        12345, SAS_SCHEDULE, 20SEP2020, , 20SEP2020 00:00, 20SEP2020 08:00         
        '''
        duty_start = None
        duty_end = None
        if duty_bag.duty.is_freeday() and not duty_bag.duty.is_vacation():
            duty_start = start_dt + timedelta(days=day_nr) 
            duty_end = duty_start
        elif duty_bag.duty.is_vacation() or duty_bag.duty.is_loa() or duty_bag.duty.is_cmp() or duty_bag.duty.is_blank_day() or duty_bag.duty.is_f36() or duty_bag.duty.is_cd():
            duty_start = start_dt + timedelta(days=day_nr)
            duty_end = datetime(duty_start.year, duty_start.month, duty_start.day, 8, 0)
        elif duty_bag.duty.is_gd() or duty_bag.duty.is_kd() or duty_bag.duty.is_sd():
            duty_start = start_dt + timedelta(days=day_nr)
            if(self.is_weekday(duty_start)):                
                duty_end = datetime(duty_start.year, duty_start.month, duty_start.day, 8, 0)
            else:
                duty_end = datetime(duty_start.year, duty_start.month, duty_start.day, 0, 0)
        elif duty_bag.duty.is_longterm_illness() or duty_bag.duty.is_loa_la12():
            duty_start = start_dt + timedelta(days=day_nr)
            if(self.is_weekday(duty_start)):                
                duty_end = datetime(duty_start.year, duty_start.month, duty_start.day, 8, 0)
            else:
                duty_end = datetime(duty_start.year, duty_start.month, duty_start.day, 0, 0) 
        
        elif duty_bag.duty.is_illness() or duty_bag.duty.has_unfit_for_flight_star():
            start_dt = start_dt + timedelta(days=day_nr)
            start_dt_start_abs = AbsTime(start_dt.year, start_dt.month, start_dt.day, 0, 0)
            start_dt_end_abs = start_dt_start_abs + RelTime('24:00')
            log.debug('NORDLYS: Checking prev duty hours between {st} - {end}'.format(st=start_dt_start_abs, end=start_dt_end_abs))
            prev_duty_hours = RelTime('00:00')
            
            if duty_bag.duty.is_illness() and self.prev_inf_is_std_hrs(duty_bag, start_dt_start_abs, start_dt_end_abs):
                prev_duty_hours = RelTime('08:00')
            else:
                prev_duty_hours = duty_bag.rescheduling.period_inf_prev_duty_time(start_dt_start_abs, start_dt_end_abs)
            
            log.debug('''#####################################
                        # NORDLYS: Illness or Unfit found {code}
                        # crew {crew}
                        # date {dt}
                        # prev_inf_hours {hrs}
                        #####################################'''.format(
                            code=duty_bag.duty.code(),
                            crew=duty_bag.crew.id(),
                            dt=start_dt_start_abs,
                            hrs=prev_duty_hours
            ))
            # Reported start time will be 00:00 and end will be start + previously worked hours
            duty_start = abs_to_datetime(start_dt_start_abs)
            duty_end = abs_to_datetime(start_dt_start_abs + prev_duty_hours)
        return (duty_start, duty_end)

    def prev_inf_is_std_hrs(self, duty_bag, start, end):
        if duty_bag.rescheduling.prev_inf_VA_at_dt(start):
            log.debug('NORDLYS: Found previously informed VA in period {start} - {end}'.format(start=start, end=end))
            return True
        elif duty_bag.rescheduling.prev_inf_BL_at_dt(start):
            log.debug('NORDLYS: Found previously informed BL in period {start} - {end}'.format(start=start, end=end))
            return True
        elif duty_bag.rescheduling.prev_inf_CMP_at_dt(start):
            log.debug('NORDLYS: Found previously informed CMP in period {start} - {end}'.format(start=start, end=end))
            return True
        elif duty_bag.rescheduling.prev_inf_LOA_at_dt(start):
            log.debug('NORDLYS: Found previously informed LOA in period {start} - {end}'.format(start=start, end=end))
            return True
        return False
        

    def report_start_date(self):
        now = datetime.now()
        year = now.year if now.month != 1 else now.year - 1
        month = now.month - 1 if now.month != 1 else 12
        return AbsTime(year, month, 1, 0, 0)

    def report_end_date(self):
        '''
        :return: AbsTime date of either last day in month or 28 days ahead, whichever greater
        
        Example 1:
        now = 01JAN
        then return 31JAN since difference between 01JAN and 31JAN > 28 

        Example 2:
        now = 10JAN
        then return 7FEB since 28 days forward from 10JAN = 7FEB
        '''
        now = datetime.now()
        curr_day = now.day
        curr_month_end = datetime(now.year, now.month, 1) + relativedelta(months=1, days=-1)
        
        day_range = curr_month_end.day - curr_day
        
        end_year = now.year
        end_month = now.month
        
        if day_range < 28:
            end_year = end_year if end_month != 12 else end_year + 1
            end_month = end_month + 1 if end_month != 12 else 1
        end_day = curr_month_end.day if day_range >= 28 else (28 - day_range)
        
        end_dt_abs = AbsTime(end_year, end_month, end_day, 0, 0)
        return end_dt_abs

    def is_weekday(self,start):
        weekday_num = start.weekday()
        log.info('NORDLYS: Weekday Day Number {sd}'.format(sd=weekday_num))
        if weekday_num <= 4:
            log.debug('NORDLYS: Day is between Monday-Friday {day}'.format(day=weekday_num))
            return True
        else:
            log.debug('NORDLYS: Day is between Saturday or Sunday {day}'.format(day=weekday_num))
            return False
        return False

    
