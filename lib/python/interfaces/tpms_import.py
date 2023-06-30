import Cui
from tpms_exlude_records_mail import send_email

#sys.exit() #TODO

def main():
    import csv
    import os
    import re
    import time
    import datetime
    import carmusr.HelperFunctions as HF
    import carmensystems.rave.api as R
    import carmusr.Attributes as Attributes
    import shutil

    from datetime import datetime, timedelta, date

    from AbsTime import AbsTime
    from AbsDate import AbsDate
    from modelserver import EntityNotFoundError

    from tm import TM

    source_folder = os.path.join(os.environ['CARMTMP'], 'ftp', 'in')
    backup_folder = os.path.join(os.environ['CARMTMP'], 'ftp', 'tpms_import_processed')
    exclude_folder= os.path.join(os.environ['CARMTMP'], 'ftp', 'exclude_records')
    DOCUMENT_WHITELIST = ['LC', 'PC', 'OPC', 'CRM', 'CRMC', 'PGT', 'REC']

    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    if not os.path.exists(exclude_folder):
        os.makedirs(exclude_folder)

    firstcol = 'IICMEQ_OML'  # first column in file
    remark = 'IICMEQ_REMARK'  # empty
    act_group_name = 'IICMEQ_ACT_GROUP_NAME'  # all | ac_qual ?
    qual_code = 'IICMEQ_QUAL_CODE'  # doc.subtype
    qual_code_type = 'IICMEQ_QUAL_CODE_TYPE'  # doc.typ
    staff_id = 'IICMEQ_STAFF_ID'  # crew
    valid_from = 'IICMEQ_VALID_FROM'  # validfrom
    end_date = 'IICMEQ_END_DATE'  # validto
    exam_date = 'IICMEQ_EXAMINATION_DATE' # examination date
    last_action = 'IICMEQ_LAST_ACTION' # New/updated or deleted in TPMS
    
    verbose = False

    def _get_key(row, row_number):
        try:
            crew = TM.crew[(row[staff_id],)]
            doc_type = TM.crew_document_set[(row[qual_code_type], row[qual_code],)]
            return crew, doc_type, _date_to_abs_time(row[valid_from])
        except EntityNotFoundError:
            # Unable to fetch crew id from crew table, id unavailable due to retirement?
            print "TPMS: Unable to import line number %d, data:%s" % (row_number, row)
            import traceback
            traceback.print_exc()
            return None

    def _date_to_abs_time(date_string, offset_days=0):
        d = datetime.strptime(date_string, '%Y-%m-%d') + timedelta(offset_days)
        return AbsTime(d.year, d.month, d.day, d.hour, d.minute)

    def  _abs_time_now():
        now = time.gmtime()
        return AbsTime(now[0], now[1], now[2], now[3], now[4]) 

    pattern = re.compile(r'[0-9]{14}') # we guess this looks up first consecutive substring of 14 digits
    # TODO move inside function below

    def _accept_csv(fname):
        if os.path.splitext(fname)[1].lower() == '.csv':
            res = pattern.search(fname)
            if res:
                margin = timedelta(days=7)  # Set how long span should be allowed
                today = date.today()
                filedate = datetime.strptime(res.group(), '%Y%m%d%H%M%S')
                if today - margin <= filedate.date() and filedate.date() <= today:
                    return True
                else:
                    print "TPMS: filename ",fname, "outside valid date interval"
                    return False
        return False

    def _handle_entry(row_no, row):
        if row[qual_code] in DOCUMENT_WHITELIST:  # This also handles eof and other cases
            if row[act_group_name] != "A3A5":
                if not _exam_date_check(row[exam_date], row[last_action]): return False   # TODO change to False
                return True
            else: return True
        return False

    def _exam_date_check(examdate, lastaction):
        exam_d = _date_to_abs_time(examdate)
        now_d = _abs_time_now()
        if exam_d > now_d or (exam_d < (now_d.adddays(-90)) and (lastaction == 'NU' or lastaction == 'N')):
            global errmsg
            errmsg = "TPMS: Exam date " + str(AbsDate(exam_d)) + " for crew " + row[staff_id] + " outside valid interval " + str(AbsDate(now_d.adddays(-90))) + "-" + str(AbsDate(now_d))
            print errmsg
            return False
        else:
            return True


    def _update_crew_document(row_no, row):
        split_sub_type = row[qual_code] in ('OPC', 'PC') and row[act_group_name] in ('A3','A4','A5','A3A5')
        if split_sub_type:
            row[qual_code] += row[act_group_name]
        key = _get_key(row, row_no)
  
        print "******Will try to find the entity in crew_document table"
        if key:
            try:
                entity = TM.crew_document[key]
                print "*******Found the entity, will try to update"
                print "TPMS TRYTRY: ", row[staff_id], row[last_action]
                
                #If validto is the same as in qualifications file, nothing should get updated
                if entity.validto != _date_to_abs_time(row[end_date], 1):  # TODO maybe enough to look at ">"???
                    entity.validto = _date_to_abs_time(row[end_date], 1)
                    entity.si = "TPMSu"
                    print "TPMS: document expiry updated for " + row[staff_id] + " " + row[qual_code]
                else:
                    print "Same entry exists in table, no update will be performed."
                    print " TPMS: key", entity.validto
                    _tag_leg(row[staff_id], row[exam_date], row[qual_code])

                    
            except EntityNotFoundError:
                print "Entity was not found, will create new one"
                print "TPMS EXCEPT: ", row[staff_id], row[last_action]
                entity = TM.crew_document.create(key)
                entity.ac_qual = '' if row[act_group_name] == 'ALL' or split_sub_type else row[act_group_name]
                entity.validto = _date_to_abs_time(row[end_date], 1)
                entity.si = "TPMSn" #row[remark] #TODO is the remark ever used?
                _tag_leg(row[staff_id], row[exam_date], row[qual_code])


    def _tag_leg(crew_id, examination_date, tpms_training_type):
        exam_date = _date_to_abs_time(examination_date)
        #area = Cui.CuiArea0 # TODO how should it be handled when run as a script?
        area = Cui.CuiScriptBuffer
        crew_object = HF.CrewObject(crew_id, area)
        rec_expr = R.foreach(
            R.iter("iterators.leg_set",
                   sort_by = 'leg.%start_utc%',
                   where = ('leg.%%end_date%% = %s' % str(exam_date), 'leg.%is_pc_or_opc% or leg.%is_crm% or leg.%is_crmc% or leg.%is_pgt% or leg.%is_rec%')), #TODO update criteria for PGT CRM etc.
            # These values are keys in the attr tables
            'training_log.%rec_leg_type%',
            'training_log.%rec_leg_time%',
            'training_log.%rec_leg_code%',
            'leg.%start_station%'
            #
            ,'training_log.%%leg_extends_any_recurrent_doc%%(%s)' % str(exam_date)

        )
        rec_activities, = crew_object.eval(rec_expr)
        if len(rec_activities) > 0:
            print "TPMS: num of activities: ", len(rec_activities)
            for (ix, leg_type, leg_time, leg_code, adep, ext) in rec_activities:
                leg_key = (crew_id, leg_type, leg_time, leg_code, adep)
                if ext:
                    print "TPMS: TAG LEG", leg_key, tpms_training_type
                    _tag_leg_performed(leg_key, tpms_training_type)
                    return True
        return False

    def _tag_leg_performed(leg_key, main_doc):
        """
        This function is used to primarily to tag a leg so that CMS knows it has
        updated a document (by having the RECURRENT attribute).
        It also sets a value to indicate which document was primarily updated
        (typically PC if more than one).
        This function is copied from CrewTableHandler
        """
        (crew_id, leg_type, leg_time, leg_code, adep) = leg_key
        attr_vals = {"str":main_doc}
        if leg_type == "FD":
            Attributes.SetCrewFlightDutyAttr(crew_id, leg_time, leg_code, adep, "RECURRENT", refresh=False, **attr_vals)
        elif leg_type == "GD":
            Attributes.SetCrewGroundDutyAttr(crew_id, leg_time, leg_code, "RECURRENT", refresh=False, **attr_vals)
        elif leg_type == "ACT":
            Attributes.SetCrewActivityAttr(crew_id, leg_time, leg_code, "RECURRENT", refresh=False, **attr_vals)
        else:
            print "TPMS Tagging recurrent performed failed, unknown leg type", main_doc, leg_key


    csv_files = []
    for root, _, files in os.walk(source_folder):
        if verbose:
            print "files", root, files
        csv_files += [os.path.join(root, f) for f in files if _accept_csv(f)]

    if verbose:
        print "========================== Import from TPMS =================="
        print "at ",source_folder
        print "found ",csv_files

    for f in csv_files:
        with open(f, 'rb') as csv_file:
            print "TPMS FILENAME: ", f
            line = csv_file.readline()
            if not "###II_CrewMemExpQualif###" in line:
                raise ValueError("Unable to find TPMS header")
            header = csv_file.readline()
            fieldnames = [tag[1:-1] for tag in header.strip().split(';')]
            exc_data_list = []
            header=[ "Staff_Id", "Qual_Code_Type", "Qual_Code", "Act_Group", "Exam_Date", "Valid_From", "Valid_To", "Error_Message"]
            timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
            exc_file_name = exclude_folder + '/TPMS_Qual_Update_Rejected_by_CMS_{}.csv'.format(timestamp)
            for row_number, row in enumerate(csv.DictReader(csv_file, fieldnames=fieldnames, delimiter=';')):
                if row[firstcol]=='### eof ###':
                    print "TPMS EOF"
                    break
                print ("TPMS: ", row[staff_id], row[qual_code_type], row[qual_code], row[act_group_name], row[exam_date] , row[valid_from], row[end_date])
                if not _handle_entry(row_number, row):
                    print "TPMS EXCLUDE RECORD - ", row[remark]
                    errormsg=errmsg
                    data = [[row[staff_id], row[qual_code_type], row[qual_code], row[act_group_name], row[exam_date], row[valid_from], row[end_date], errormsg]]
                    exc_data_list.append(data)
                    continue
                print "Going to update Crew Docs"
                _update_crew_document(row_number, row)
        with open(exc_file_name, mode='wb+') as exc_csv_file:
            writer = csv.writer(exc_csv_file)
            writer.writerow(header)
            for each_row in exc_data_list:
                writer.writerows(each_row)
        TM.save()
        shutil.move(f, backup_folder)
        send_email()

def run():
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

#main()
