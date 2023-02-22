'''
Base report class WFSReport for producing .csv report files for both 
Time Entry and Work Schedule WFS interfaces. 
Also includes general utility functions.
'''
import csv
import json
import os, stat
import carmensystems.rave.api as r
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from AbsTime import AbsTime
from RelTime import RelTime
from carmensystems.dave import dmf
import modelserver
import time
from shutil import copyfile

NO = 'NO'
SE = 'SE'
DK = 'DK'

CARMDATA = os.getenv("CARMDATA")
REPORT_PATH = CARMDATA + "/REPORTS/SALARY_WFS/"
ARCHIVE_PATH = "/samba-share/reports/SALARY_WFS/"
RELEASE_PATH = '/opt/Carmen/CARMTMP/ftp/out/SALARY_SEIP/'
seq_salary_rec_wfs = 'seq_salary_rec_wfs'
seq_salary_run_wfs = 'seq_salary_run_wfs'
crew_exclusion_list = ['92742','92589','92462','92510']

logging.basicConfig()
log = logging.getLogger('wfs_report')
log.setLevel(logging.INFO)

tm = modelserver.TableManager.instance()

class WFSReport():
    def __init__(self, type, release=True, test=False, studio=False):
        self.type = type
        self.test = test
        self.release = release
        self.start = self.report_start_date()
        self.end = self.report_end_date()
        self.start_dt = abs_to_datetime(self.start)
        self.end_dt = abs_to_datetime(self.end)
        self.studio = studio

	if self.type == 'TIME':
            self.runid = getNextRunId()

        if self.test:
            log.setLevel(logging.DEBUG)

    def generate(self, crew_ids):
        # Entry point from report server
        start_t = time.time()
        if not os.path.exists(REPORT_PATH):
            os.makedirs(REPORT_PATH)
        if not os.path.exists(RELEASE_PATH):
            os.makedirs(RELEASE_PATH)
	
	log.debug('NORDLYS: Generating report for the period {0} to {1}'.format(self.start, self.end))
	
	csv_files = []
	
        se_report_name = self.report_name(SE)
        no_report_name = self.report_name(NO)
        dk_report_name = self.report_name(DK)
        se_report = self.create_report_file(se_report_name)
        no_report = self.create_report_file(no_report_name)
        dk_report = self.create_report_file(dk_report_name)
        
	csv_files.append(se_report)
        csv_files.append(no_report)
        csv_files.append(dk_report)

        curr_date = AbsTime(datetime.now().strftime('%d%b%Y'))
        log.debug('NORDLYS: curr_date: {0} , self.start: {1}'.format(curr_date, self.start))
       
        if crew_ids is None or len(crew_ids) == 0:
            crew_ids = []
            log.info('NORDLYS: Generating {0} report for all crew'.format(self.type))
            roster_bag = r.context('sp_crew').bag()
            for crew_bag in roster_bag.iterators.crewid_set(where=('crew.%is_homebase_SKS% or crew.%is_homebase_SKD% or crew.%is_homebase_SKN%')):
                crew_id = crew_bag.crew.id()
                if r.eval('model_crew.%crewrank_at_date_by_id%("{crew_id}", {dt})'.format(crew_id=crew_id, dt=self.start))[0] == 'FS':
                    log.debug('NORDLYS: Skipping crew {c} with FS rank'.format(c=crew_id))
                    continue
                extperkey = extperkey_from_id(crew_id, self.start)
                if extperkey == crew_id:
                    # Try converting crew_id as extperkey to actual crew_id
                    crew_id = convert_extperkey_to_crew_id(crew_id, self.start)
                # This is placed here so that we should not skip the crew who is retired for some time
                # during the report start date but they have valid contract in between the report run period
                if crew_info_changed_in_period(crew_id, self.start, self.end):
                    log.info('NORDLYS: Crew Info has been changed for crew {c} on {d}'.format(c=crew_id, d = self.start))
                else:# If crew contract hasnt been changed in the report period, Skip the retired crew.
                    if crew_has_retired_at_date(crew_id, self.start):
                        log.info('NORDLYS: Skipping retired crew {c} on {d}'.format(c=crew_id, d = curr_date))
                        continue
                if crew_excluded(crew_id, curr_date):
                    log.info('NORDLYS: Skipping the excluded SAS Link crew {c}'.format(c=crew_id))
                    continue 
                    
                crew_ids.append(crew_id)
        else:
            for crew_id in crew_ids:
                # This is placed here so that we should not skip the crew who is retired for some time
                # during the report start date but they have valid contract in between the report run period
                if crew_info_changed_in_period(crew_id, self.start, self.end):
                    log.info('NORDLYS: Crew Info has been changed for crew {c} on {d}'.format(c=crew_id, d = self.start))
                else:# If crew contract hasnt been changed in the report period, Skip the retired crew.
                    if crew_has_retired_at_date(crew_id, self.start):
                        log.info('NORDLYS: Skipping retired crew {c} on {d}'.format(c=crew_id, d = self.start))
                        crew_ids.remove(crew_id)
                if crew_excluded(crew_id, curr_date):
                    log.info('NORDLYS: Skipping the excluded SAS Link crew {c}'.format(c=crew_id))
                    crew_ids.remove(crew_id)
            log.debug('NORDLYS: Generating {0} report for crew {1}'.format(self.type, crew_ids))

        state_before = tm.currentState()
        tm.newState()

        log.info('NORDLYS: {0} report period {1} - {2}'.format(self.type, self.start, self.end))
        rec_counter = 0
        for crew_id in crew_ids:
            data = self.extract_data(crew_id)
            rec_counter += len(data)
            country = country_from_id(crew_id, self.start)
            if crew_info_changed_in_period(crew_id, self.start, self.end):
                self.write_to_report_per_date(crew_id, data, se_report, no_report, dk_report)
            else: 
                if country == SE:
                    self.write_to_report(data, se_report)
                elif country == NO:
                    self.write_to_report(data, no_report)
                elif country == DK:
                    self.write_to_report(data, dk_report)
            log.debug('\nNORDLYS: {0} data for {1} sent to WFS'.format(self.type, crew_id))
            log.debug(json.dumps(data, indent=4, default=lambda x: str(x)))
        
        # Save all committed data to db
        if self.type == 'TIME':
            save_data()
        
        if self.release:
            # move copies of se_, no_ and dk_* reports
            # to RELEASE_PATH
            copyfile(se_report, RELEASE_PATH + se_report_name)
            copyfile(no_report, RELEASE_PATH + no_report_name)
            copyfile(dk_report, RELEASE_PATH + dk_report_name)
        else:
            # move copies of se_, no_ and dk_* reports
            # to ARCHIVE_PATH
            copyfile(se_report, ARCHIVE_PATH + se_report_name)
            copyfile(no_report, ARCHIVE_PATH + no_report_name)
            copyfile(dk_report, ARCHIVE_PATH + dk_report_name)
        
        # Benchmarking and general infodump
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
        # Release path :  {report_path}
        # Archive path :  {archive_path}
        # SE : {se_report}
        # NO : {no_report}
        # DK : {dk_report}
        # {release_info}
        # {archive_info}
        #########################################################'''.format(
            type=self.type,
            runid=('N/A' if self.type == 'SCHEDULE' else self.runid),
            dt=datetime.now(),
            nr_crew=len(crew_ids), 
            nr_recs=rec_counter, 
            time=exec_time,
            report_path=REPORT_PATH,
            archive_path=ARCHIVE_PATH,
            se_report=se_report,
            no_report=no_report,
            dk_report=dk_report,
            release_info='Released to : {dst}'.format(dst=RELEASE_PATH if self.release else 'Report not released'),
            archive_info='Archived to : {dst}'.format(dst=ARCHIVE_PATH if not self.release else 'Report not archived')
            ))
        state_after = tm.currentState()
        log.debug('NORDLYS: DB difference : \n{diff}'.format(diff=tm.difference(state_before, state_after).uxm()))
	
	return csv_files

    def extract_data(self, crew_id):
        pass

    def create_filter(self, start, end):
        where_str = '(duty.%start_hb% >= {start} and duty.%start_hb% <= {end}) '.format(
                            start=start,
                            end=end)
        return where_str

    def create_report_file(self, report_name):
        report_name = REPORT_PATH + report_name
        with open(report_name, 'wb') as f:
            writer = csv.writer(f, delimiter = ',')
            writer.writerow(self.headers)
        return report_name
    
    def report_name(self, country):
        report_name = '{country}_CMS_{type}_IMPORT{studio}'.format(
            country=country,
            type=self.type if self.type != 'RERUN' else 'TIME',
            studio='_STUDIO_' if self.studio else '_'
        )
        if self.test:
            report_name = report_name + 'TEST.csv'
        else:
            report_dt = datetime.now().strftime('%Y%m%d%H%M%S')
            report_name = report_name + '{date}.csv'.format(date=report_dt)
        return report_name

    def write_to_report(self, data, report):
        with open(report, 'a+') as f:
            writer = csv.writer(f, delimiter = ',')
            for row in data:
                writer.writerow(row)
    
    def write_to_report_per_date(self, crew_id ,data, se_report, no_report, dk_report):
        for d in data:
            dt = datetime.strptime(d[2], '%Y-%m-%d') # d[2] = duty_start_date string formatted as %Y-%m-%d
            abs_dt = AbsTime(dt.year, dt.month, dt.day, 0, 0)
            d = [d]
            country = country_from_id(crew_id, abs_dt)
            if country == SE:
                self.write_to_report(d, se_report)
            elif country == NO:
                self.write_to_report(d, no_report)
            elif country == DK:
                self.write_to_report(d, dk_report)

    def report_start_date(self):
        return r.eval('fundamental.%pp_start%')[0]

    def report_end_date(self):
        return r.eval('fundamental.%pp_end%')[0]


'''
Utility functions
'''
def abs_to_datetime(abstime):
    abs_str = abstime.getValue()
    day     = int(abs_str[0:2])
    month   = datetime.strptime(abs_str[2:5], '%b').month
    year    = int(abs_str[5:9])
    hour    = int(abs_str[10:12])
    minute  = int(abs_str[13:15])

    return datetime(year, month, day, hour, minute)

def extperkey_from_id(crew_id, dt):
    extperkey = r.eval('model_crew.%extperkey_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    if extperkey is None:
        # In some cases crew has their extperkeys seen as crew id when using r.context('sp_crew')
        log.debug('NORDLYS: Actual extperkey used as used as crew id')
        return crew_id
    return extperkey

def convert_extperkey_to_crew_id(crew_id, dt):
    # Sometimes crew appears with their extperkeys as crew ids. In these cases it is not possible
    # to traverse the roster on what the crew_set iterator thinks is a valid crew id
    # This is usually needed when crew has switched base and extperkey is used in place of crewid
    possible_crew_id = r.eval('model_crew.%crew_id_from_extperkey%("{0}", {1})'.format(crew_id, dt))[0]
    if possible_crew_id:
        crew_id = possible_crew_id

    return crew_id


def country_from_id(crew_id, dt):
    country = r.eval('model_crew.%country_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    return country

def rank_from_id(crew_id, dt):
    rank = r.eval('model_crew.%crewrank_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    crew_rank = None
    if rank:
        crew_rank_t = tm.table('crew_rank_set')
        rank_iter = crew_rank_t.search('(id={0})'.format(rank))
        crew_rank = next(rank_iter)
    if crew_rank:     
        return 'FC' if crew_rank.maincat.id == 'F' else 'CC'
    else:
        return None

def actual_rank_from_id(crew_id, dt):
    rank = r.eval('model_crew.%crewrank_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    if rank:
        return rank
    else:
        return None

def crew_info_changed_in_period(crew_id, start, end):
    extperkey_start = extperkey_from_id(crew_id, start)
    extperkey_end = extperkey_from_id(crew_id, end)
    country_start = country_from_id(crew_id, start)
    country_end = country_from_id(crew_id, end)
    rank_start = rank_from_id(crew_id, start)
    rank_end = rank_from_id(crew_id, end)
    if (extperkey_start != extperkey_end or country_start != country_end or rank_start != rank_end):
        log.info('''
        ###########################################
        # NORDLYS: Crew data has changed in period
        # extperkey at {start} {ext_start} vs extperkey at {end} {ext_end}
        # country at {start} {country_start} vs country at {end} {country_end}
        # rank at {start} {rank_start} vs rank at {end} {rank_end} 
        ###########################################'''.format(
            start=start, 
            end=end,
            ext_start=extperkey_start,
            ext_end=extperkey_end,
            country_start=country_start,
            country_end=country_end,
            rank_start=rank_start,
            rank_end=rank_end))
        return True
    return False

def crew_has_retired_at_date(crew_id, dt):
    employment_status = r.eval('model_crew.%group_at_date%("{crew_id}", {dt})'.format(crew_id=crew_id, dt=dt))[0]
    if employment_status == 'R':
        log.info('Crew {crew_id} has retired at {dt}'.format(crew_id=crew_id, dt=dt))
        return True
    return False

'''
The format to report hours required either numbers in N or N.NN
For clarity we always provide it in N.NN format with trailing zeroes

For example RelTime('1:00') would be translated to 1.00
and RelTime('2:30') would be translated to 2.50
'''
def reltime_to_decimal(reltime):
    decimal_time = None
    if reltime != None:
        decimal_time = ('%.2f' % (reltime.getRep() / 60.0))
    return decimal_time

def default_reltime(val):
    if val is None:
        return RelTime('00:00')
    return val

def integer_to_reltime(val):
    if val is None:
        return RelTime('00:00')
    else:
        val = ("%02d" % val) + ":00"
        val = RelTime(val)
    return val

def add_to_salary_wfs_t(data, crew_id, runid):
    salary_wfs_t = tm.table('salary_wfs')
    recordid = data['record_id']
    try :
        new_rec = salary_wfs_t.create((runid, recordid,))
    except Exception:
        log.info("Duplicate RecordID {0} and RunID {1} Found .....".format(recordid,runid))
        return 0
    new_rec.crew = crew_id
    new_rec.extperkey = data['extperkey']
    new_rec.work_day = AbsTime(data['start_dt'].strftime('%Y%m%d'))    
    new_rec.amount = data['hours']
    new_rec.days_off = data['days_off']
    new_rec.wfs_paycode = data['paycode']
    new_rec.flag = data['flag']
        

def save_data():
    log.info('NORDLYS: Saving record data...')
    tm.save('wfs_testing')

def setRecordIdSeqNo():
    """Set the sequence number to be the largest possible value in
    salary_wfs. Since we have some migrated data, we want our new runs to
    have sequence numbers that are larger than the largest value of the
    migrated data.  This function should only be called once, at
    installation."""
    log.debug("setRunIdSeqNo()")
    conn = dmf.BorrowConnection(TM.conn())
    conn.rquery('select max(recordid) from salary_wfs', None)
    max, = conn.readRow().valuesAsList()
    conn.endQuery()
    log.debug("...setting sequence number of '%s' to '%d'." % (seq_salary_rec_wfs, max))
    conn.setSeqValue(seq_salary_rec_wfs, max)
    return max


def getNextRecordId():
    """ Get next available record id """
    log.debug("getNextRecordId()")
    try:
        next_record_id = dmf.BorrowConnection(tm.conn()).getNextSeqValue(seq_salary_rec_wfs)
    except:
        # This is to enable salary file from the test menu in the history user,
        # where the salary run id sequence is not available
        max_record_id = -1
        for r in tm.seq_salary_rec_wfs:
            if r.recordid >= max_record_id: 
                max_record_id = r.recordid
                next_record_id = max_record_id + 1
    return next_record_id

def getNextRunId():
    """ Get next available run id """
    log.debug("getNextRunId()")
    try:
        next_run_id = dmf.BorrowConnection(tm.conn()).getNextSeqValue(seq_salary_run_wfs)
    except:
        # This is to enable salary file from the test menu in the history user,
        # where the salary run id sequence is not available
        max_run_id = -1
        for r in tm.seq_salary_run_wfs:
            if r.runid >= max_run_id: 
                max_run_id = r.runid
                next_run_id = max_run_id + 1
    return next_run_id

def planninggroup_from_id(crew_id, dt):
    planninggroup = r.eval('model_crew.%planning_group_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    return planninggroup

def base_from_id(crew_id, dt):
    crew_base= r.eval('model_crew.%base_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    return crew_base

def crew_not_BGOFD(crew_id, dt):
    crew_base= base_from_id(crew_id,dt)
    crewid_rank = rank_from_id(crew_id, dt)
    if crew_base != 'BGO':
        return True
    elif crewid_rank == 'FC':
        return False
    else:
        return True

def crew_excluded(crew_id, curr_date):
    if extperkey_from_id(crew_id,curr_date) in crew_exclusion_list:
        return True
    return False
def end_month_extended(e_month):
    end_month = abs_to_datetime(e_month)
    end_month_extended = datetime(end_month.year, end_month.month, 1) + relativedelta(months=2, days=-1)
    month = end_month_extended.month
    year = end_month_extended.year
    day= end_month_extended.day
    end_month_extended_abs = AbsTime(year, month, day, 0,0)
    return end_month_extended_abs
