import logging
from shutil import copyfile
import csv
import time, os, logging
import carmensystems.rave.api as rave
from datetime import date, datetime, timedelta
from AbsTime import AbsTime

CARMDATA = os.getenv("CARMDATA")
logging.basicConfig()
log = logging.getLogger('EC_Correction')

ORIGINAL_HEADERS = ('Currency Code','Issue Date','Type','User ID','Value','Reference ID','Number of units','Operation')

ORIGINAL_SALARY_FILES_PATH = '/opt/Carmen/CARMDATA/carmdata/SALARY_NL/salary_month/Original_Salary_Files/'
CORRECTION_SALARY_FILES_PATH = '/opt/Carmen/CARMDATA/carmdata/SALARY_NL/salary_month/Correction_Salary_Files/'
CORRECTED_SALARY_FILES_PATH = '/opt/Carmen/CARMDATA/carmdata/SALARY_NL/salary_month/Corrected_Salary_Files/'

DK_corrected_file = None
NO_corrected_file = None
SE_corrected_file = None

DK_original_file = None
NO_original_file = None
SE_original_file = None

correction_files = []

def run():  
    _find_salary_files()

def _find_salary_files():
    for f in os.listdir(CORRECTION_SALARY_FILES_PATH):
        if 'SE' in f or 'NO' in f or 'DK' in f:
            correction_files.append(f)

    for f in os.listdir(ORIGINAL_SALARY_FILES_PATH):
        if "Payments_CMS_DK" in f:
            DK_original_file = f
        elif "Payments_CMS_NO" in f:
            NO_original_file = f
        elif "Payments_CMS_SE" in f:
            SE_original_file = f

    log.debug("DK Original File : " + DK_original_file)
    log.debug("NO Original File : " + NO_original_file)
    log.debug("SE Original File : " + SE_original_file)

    for f in os.listdir(CORRECTED_SALARY_FILES_PATH):
        if "Payments_CMS_DK" in f:
            DK_corrected_file = f
        elif "Payments_CMS_NO" in f:
            NO_corrected_file = f
        elif "Payments_CMS_SE" in f:
            SE_corrected_file = f

    if os.path.exists(CORRECTED_SALARY_FILES_PATH):
        if not os.path.exists(DK_original_file):
            copyfile(ORIGINAL_SALARY_FILES_PATH + DK_original_file, CORRECTED_SALARY_FILES_PATH + DK_original_file)
            DK_corrected_file = DK_original_file
        if not os.path.exists(NO_original_file):
            copyfile(ORIGINAL_SALARY_FILES_PATH + NO_original_file, CORRECTED_SALARY_FILES_PATH + NO_original_file)
            NO_corrected_file = NO_original_file
        if not os.path.exists(SE_original_file):
            copyfile(ORIGINAL_SALARY_FILES_PATH + SE_original_file, CORRECTED_SALARY_FILES_PATH + SE_original_file)
            SE_corrected_file = SE_original_file

    log.debug("DK Corrected File : " + DK_corrected_file)
    log.debug("NO Corrected File : " + NO_corrected_file)
    log.debug("SE Corrected File : " + SE_corrected_file)

    if len(correction_files) != 0:
        log.info("Found the Salary Correction Files : " + str(correction_files))
        _correct_files(DK_corrected_file, NO_corrected_file, SE_corrected_file)
    else:
        log.info("Correction Files not Found : " + str(correction_files))

def _correct_files(DK_corrected_file, NO_corrected_file, SE_corrected_file):
    for f in correction_files:
        try:
            csv_file = open(CORRECTION_SALARY_FILES_PATH + f,'r')
            csv_reader = csv.DictReader(csv_file)
        except:
            log.info("Correction Files not found")
        for row in csv_reader:
            article_id = row["ArticleID"]
            extperkey = row["Crew"]            
            current_value = row["Value"]
            current_NoU = row["NumberOfUnits"]
            corrected_value = row["Corrected"]
            log.debug("Converting extperkey to crew_id : " + extperkey)
            crew_id = convert_extperkey_to_crew_id(extperkey, AbsTime((datetime.now()-timedelta(days=date.today().day)).strftime("%Y%m%d")))
            log.debug("Converted crew_id : " + crew_id)
            log.debug("Finding _country_from_id for crew_id : " + crew_id)
            crew_region = _country_from_id(crew_id, AbsTime((datetime.now()-timedelta(days=date.today().day)).strftime("%Y%m%d")))
            log.debug("Found _country_from_id as : " + crew_region)
            
            if crew_region == "DK":
                file_name = DK_corrected_file
            elif crew_region == "NO":
                file_name = NO_corrected_file
            elif crew_region == "SE":
                file_name = SE_corrected_file

            log.debug("=====================================")
            log.debug("extperkey : " + extperkey)
            log.debug("crew_id : " + crew_id)
            log.debug("article_id : " + article_id)
            log.debug("current_value : " + current_value)  
            log.debug("bool(current_value) : " + str(bool(current_value)))
            log.debug("current_NoU : " + current_NoU) 
            log.debug("bool(current_NoU) : " + str(bool(current_NoU)))          
            log.debug("corrected : " + corrected_value)            
            log.debug("crew_region : " +     crew_region)
            log.debug("file_name : " + file_name)
            log.debug("=====================================")

            if ((( not bool(current_value) and float(current_NoU) == 0) or ( not bool(current_NoU) and float(current_value) == 0)) and float(corrected_value) != 0):
                _insert_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value)
                log.info("Record inserted successfully ...")
            elif ((current_value != '' and float(corrected_value) == 0) or (current_NoU != '' and float(corrected_value) == 0)):
                _delete_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value)
                log.info("Record deleted successfully ...")
            elif (((not bool(current_value) and float(current_NoU) != 0) or (not bool(current_NoU) and float(current_value) != 0)) and float(corrected_value) != 0):
                _update_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value)
                log.info("Record updated successfully ...")
            log.debug("=====================================")

        csv_file.close() 

def convert_extperkey_to_crew_id(extperkey, dt):
    # Sometimes crew appears with their extperkeys as crew ids. In these cases it is not possible
    # to traverse the roster on what the crew_set iterator thinks is a valid crew id
    # This is usually needed when crew has switched base and extperkey is used in place of crewid
    possible_crew_id = rave.eval('model_crew.%crew_id_from_extperkey%("{0}", {1})'.format(extperkey, dt))[0]
    if possible_crew_id:
        crew_id = possible_crew_id
    return crew_id

def _country_from_id(crew_id, dt):
    country = rave.eval('model_crew.%country_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id, 
        dt=dt)
        )[0]
    return country

def _insert_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value,path=CORRECTED_SALARY_FILES_PATH):
    csv_file = open(path + file_name,'r')
    csv_reader = csv.DictReader(csv_file,delimiter=',')
    data = [row for row in csv_reader]
    csv_file.close()

    temp = data[-1]

    log.debug("Last Record before Inserted : "+str(temp))

    temp['User ID'] = extperkey
    temp['Type'] = article_id
    
    if current_value == '':
        temp['Value'] = ''
        temp['Number of units'] = corrected_value
    else:
        temp['Value'] = corrected_value
        temp['Number of units'] = ''

    log.debug("Record Inserted : "+str(temp))
    
    data.append(temp)

    csv_file = open(path + file_name,'w')
    csv_writer = csv.DictWriter(csv_file,ORIGINAL_HEADERS,delimiter=',')
    csv_writer.writerow(dict(zip(ORIGINAL_HEADERS,ORIGINAL_HEADERS)))
    for i in data:
        csv_writer.writerow(i)
    csv_file.close()  

def _update_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value,path=CORRECTED_SALARY_FILES_PATH):
    csv_file = open(path + file_name,'r')
    csv_reader = csv.DictReader(csv_file,delimiter=',')
    data = [row for row in csv_reader]
    csv_file.close()

    for i in range(len(data)):
        if data[i]['User ID'] == extperkey and data[i]['Type'] == article_id:
            log.debug("Before updation : "+str(data[i]))
            if not data[i]['Value']:
                data[i]['Number of units'] = corrected_value
            else:
                data[i]['Value'] = corrected_value
            log.debug("After updation : "+str(data[i]))
            break
            
    csv_file = open(path + file_name,'w')
    csv_writer = csv.DictWriter(csv_file,ORIGINAL_HEADERS,delimiter=',')
    csv_writer.writerow(dict(zip(ORIGINAL_HEADERS,ORIGINAL_HEADERS)))
    for i in data:
        csv_writer.writerow(i)
    csv_file.close() 

def _delete_row(file_name,extperkey,article_id,current_value,current_NoU,corrected_value,path=CORRECTED_SALARY_FILES_PATH):
    csv_file = open(path + file_name,'r')
    csv_reader = csv.DictReader(csv_file,delimiter=',')
    data = [row for row in csv_reader]
    csv_file.close()

    for i in range(len(data)):
        if data[i]['User ID'] == extperkey and data[i]['Type'] == article_id:
            log.debug("Deleted Record : "+str(data[i]))
            del data[i]
            break
        
    csv_file = open(path + file_name,'w')
    csv_writer = csv.DictWriter(csv_file,ORIGINAL_HEADERS,delimiter=',')
    csv_writer.writerow(dict(zip(ORIGINAL_HEADERS,ORIGINAL_HEADERS)))
    for i in data:
        csv_writer.writerow(i)
    csv_file.close() 

if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
    """    
    log.setLevel(logging.DEBUG)
    log.info("Starting the EC Salary corrections....")
    start_time = time.time()
    run()
    end_time = time.time()
    log.info("End of the execution at %s and took: %0.2f seconds.\n\n" %  (time.ctime(end_time), end_time - start_time))
    