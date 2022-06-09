import logging
from shutil import copyfile
import csv
import modelserver
import time, os, logging
import carmensystems.rave.api as rave
from datetime import date, datetime, timedelta
from AbsTime import AbsTime
from salary.wfs.wfs_config import PaycodeHandler
from salary.wfs.wfs_report import rank_from_id,country_from_id

#CARMDATA = os.getenv("CARMDATA")
logging.basicConfig()
log = logging.getLogger('WFS_TE_Correction')

tablemanager = modelserver.TableManager.instance()
headers = ('EXTPERKEY','PAY_CODE','WORK_DT','HOURS','DAYS_OFF','SI')
path = r'/opt/Carmen/CARMDATA/carmdata/SALARY_NL/salary_month/Correction_TimeEntry_Files/'

correction_files = []
log_dict = {
        'path':path,
        'correction_files':correction_files,
        'no_correction_files':len(correction_files),
        'all_records':0,
        'inserted_records':0,
        'duplicated_records':0,
        'remaining_records':0
    }

table1 = tablemanager.table('wfs_corrected')

def run():  
    _find_correction_file()
    #correction_files = os.listdir(path)

def _find_correction_file():
    for f in os.listdir(path):
        correction_files.append(f)

    if len(correction_files) != 0:
        log.info("Found the TE Correction Files : " + str(correction_files))
        _process_correction_file()
    else:
        log.info("Correction Files not Found : " + str(correction_files))

def _process_correction_file():
    for f in correction_files:
        csv_file = open(path+"/"+f,'r')
        csv_reader = csv.DictReader(csv_file,delimiter=',')
        data = [row for row in csv_reader]
        log_dict['all_records'] += len(data)
        csv_file.close()
        if len(data) != 0:
            #print("Processing the record: " + str(data))
            _insert_record(data)

    log.info('''
        #########################################################
        # Time Entry Correction Records 
        # Path for files          : {log_path}
        # Processed Files are     : {log_files}
        # Nr Processed Files      : {log_nr_files}
        # Nr records in all file  : {log_all_records}
        # Nr records Inserted     : {log_inserted_records}
        # Nr records Duplicated   : {log_duplicated_records} 
        # Nr records Remaining    : {log_remaining_records}
        #########################################################'''.format(
            log_path=log_dict['path'],
            log_files=log_dict['correction_files'],
            log_nr_files = log_dict['no_correction_files'],
            log_all_records=log_dict['all_records'],
            log_inserted_records=log_dict['inserted_records'],
            log_duplicated_records=log_dict['duplicated_records'], 
            log_remaining_records=log_dict['all_records'] - log_dict['inserted_records'] - log_dict['duplicated_records']))

def _insert_record(data):
    for row in data:
        if _is_duplicate(row):
            log_dict['duplicated_records'] += 1
            continue
        else:
            record_crew_id = _get_crew_from_extperkey(row['EXTPERKEY'])
            record_extperkey = row['EXTPERKEY']
            record_work_day = AbsTime(row['WORK_DT'].replace('-','')+"00:00")
            
            if record_crew_id == None:
                log.info("No crew id exists for extperkey : {}".format(record_extperkey))
                continue
            
            if len(row['HOURS']) != 0:
                record_amount = RelTime(row['HOURS'].replace('.',':'))
            else:
                record_amount = None 

            # if len(row['DAYS_OFF']) != 0:
            #     if int(row['DAYS_OFF']) in (0,1):
            #         record_days_off = int(row['DAYS_OFF'])
            #     else:
            #         log.info("days off should be equal to either 1 or 0")
            #         continue
            # else:
            #     record_days_off = None 

            if len(row['DAYS_OFF']) != 0:
                record_days_off = int(row['DAYS_OFF'])
            else:
                record_days_off = None 

            record_wfs_paycode = row['PAY_CODE']
            log.info("wfs paycode: {} ".format(record_wfs_paycode))

            record_updated_at = AbsTime(str(datetime.now())[:11].replace('-','')+"00:00")
            record_flag = 'I'
            record_si = row['SI']

            # if PaycodeHandler().is_account_paycode(record_wfs_paycode):
            #     if record_days_off is None:
            #         log.info("we should received days off")
            #         continue 
            # else:
            #     if record_amount is None:
            #         log.info("we should received hrs")
            #         continue 

            correction_id = _get_next_correction_id()
            new_rec = table1.create((correction_id,))
            new_rec.crew_id = record_crew_id
            new_rec.extperkey = record_extperkey
            new_rec.wfs_paycode = record_wfs_paycode
            new_rec.work_day = record_work_day
            if record_amount is not None:
                new_rec.amount = record_amount
            if record_days_off is not None:
                new_rec.days_off = record_days_off
            new_rec.updated_at = record_updated_at
            new_rec.flag = record_flag 
            new_rec.si = record_si
            log.info("correction id {} inserted ..".format(correction_id))
            log_dict['inserted_records'] += 1
            tablemanager.save()
        
def _is_duplicate(record):
    # print("record: " + str(record))
    for i in table1.search("(&(extperkey={})(wfs_paycode={})(work_day={}))".format(
        record['EXTPERKEY'],
        record['PAY_CODE'],
        AbsTime(record['WORK_DT'].replace('-','')))):
        if (i.days_off is not None and str(i.days_off) == record['DAYS_OFF'])\
         or (i.amount is not None and RelTime(i.amount) == RelTime(record['HOURS'].replace('.',':'))):
            log.info("Extperkey : {} .. duplicated".format(record['EXTPERKEY']))
            return True
    else:
        # print("Record is unique")
        return False

def _get_crew_from_extperkey(extperkey):
    table2 = tablemanager.table('crew_employment')
    for i in table2.search("(extperkey={})".format(extperkey)):
        crew_id = i.crew
        return crew_id
    else:
        log.info("Extper key : {0} not found in table crew_employment".format(extperkey))
        return None

def _get_next_correction_id():
    max_id = -1
    for i in table1:
        if i.correction_id > max_id:
            max_id = i.correction_id
    return max_id + 1
    
if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
    """    
    log.setLevel(logging.DEBUG)
    log.info("Starting the WFS TE corrections....")
    start_time = time.time()
    run()
    end_time = time.time()
    log.info("End of the execution at %s and took: %0.2f seconds.\n\n" %  (time.ctime(end_time), end_time - start_time))
    