import Cui

def main():
    from tm import TM
    from AbsTime import AbsTime
    from datetime import datetime
    from AbsDate import AbsDate
    import utils.Names as Names
    import re
    import os
    import csv
    import shutil
    from modelserver import EntityNotFoundError
    from modelserver import EntityError
    from utils.selctx import  Flight
    import traceback

    def createSeqNr(crew_ref):
        """
        """
        rows = TM.crew_annotations.search("(crew=%s)" % str(crew_ref))
        seq_nrs = []
        for row in rows:
            seq_nrs.append(row.seqnr)
        if len(seq_nrs) == 0:
            return 1
        for nr in range(1, len(seq_nrs)+2):
            if nr in seq_nrs:
                continue
            return nr
        return max(seq_nrs)+1

    def _accept_csv(fname):
        pattern = re.compile(r'^(^crew_meal_optout_[0-9]{2}[0-9]{2}(?:[0-9]{2}|[0-9]{4}).csv)$')
        if pattern.match(fname) is not None:
            return True
        else:
            return False

    def _get_crew_from_extperkey(record_id):
        for i in TM.crew_employment.search("(extperkey={})".format(record_id)):
            crew_id = i.crew
            return crew_id
        print "Cannot find crew with empid '%s' in crew table." % record_id
    
    def getMonth(time):
        date_string = time.yyyymmdd()
        month = date_string[4:6]
        return int(month) 
    
    def getYear(time):
        date_string = time.yyyymmdd()
        year = date_string[:4]
        return int(year) 

    def record_process():
        for f in meal_opt_out_files:
            if _accept_csv(f):
                print "Found the Crew Meal opt out Files : " + f
                csv_path = path+"/"+f
                csv_file = open(csv_path,'r')
                csv_reader = csv.DictReader(csv_file,delimiter=',')
                print "csv_reader"
                print csv_reader
                data = [row for row in csv_reader]
                print("Processing the record: " + str(data))
                now_time = datetime.now()
                print now_time
                entry_time =AbsTime(now_time.year,now_time.month,now_time.day,now_time.hour,now_time.minute)
                
                unique_crew_annotation = []
 
                for row in data:
                    record_id =row['ID']
                    crew_id = _get_crew_from_extperkey(record_id)
        
                    current_time = AbsTime(now_time.year,now_time.month,now_time.day,now_time.hour,now_time.minute)
                    
                    if row['MONTH'] =='' and row['YEAR'] =='':
                        if len(unique_crew_annotation)==0:
                            unique_crew_annotation.append({'ID':row['ID'],'text':row['SCHEDULED_DEPARTURE_TIME'] + ' '+ row['FLIGHT_ID']})
                        else:
                            for unique_row in unique_crew_annotation:
                                if row['ID'] == unique_row['ID']:
                                    unique_row['text'] =unique_row['text'] + ', ' + row['SCHEDULED_DEPARTURE_TIME'] + ' '+ row['FLIGHT_ID'] 
                                else :
                                    unique_crew_annotation.append({'ID':row['ID'],'text':row['SCHEDULED_DEPARTURE_TIME'] + ' '+ row['FLIGHT_ID']} )
                                    break
 
                    try:   
                        if row['MONTH'] =='' and row['YEAR'] =='':
                            record_time =row['SCHEDULED_DEPARTURE_TIME']
                            record_time_new=AbsTime(record_time[0:4] +record_time[5:7] +record_time[8:10] + ' ' +record_time[11:16])
                            flight_id =row['FLIGHT_ID']
                            flight_id_new = flight_id[0:2] + ' 00' + flight_id[2:6]
                            flight_id_adep =row['FLIGHT_ID_ADEP']
                            flight_id_udor =AbsDate(record_time_new)
                            flt = Flight(flight_id_new,flight_id_udor,flight_id_adep)
                            ref_adep = TM.airport.getOrCreateRef(flt.adep)
                            ref_fd = TM.flight_leg[(flt.udor,flt.fd.flight_descriptor,ref_adep)]
                            new_rec_flight = TM.meal_flight_opt_out.create((crew_id,ref_fd,record_time_new))
                            print "Saved meal_flight_opt_out record for crew ={}".format(record_id) + str(new_rec_flight)     
                        else:
                            record_month =int(row['MONTH'])
                            record_year =int(row['YEAR'])
                            validfrom_date = AbsTime(AbsDate(record_year,record_month,1))
                            validto_date = AbsTime(AbsDate(record_year,record_month+1,1))
                            new_rec_month = TM.meal_opt_out.create((crew_id,record_month,record_year))
                            print "Saved meal_opt_out record for crew ={}".format(record_id) + str(new_rec_month) 

                            crew_ref = TM.crew.getOrCreateRef((crew_id.id,))
                            user_name = Names.username()
                            seqnr = createSeqNr(crew_ref)
                            new_crew_annotation_rec =TM.crew_annotations.create((crew_id,seqnr))
                            new_crew_annotation_rec.isvisible =True
                            new_crew_annotation_rec.validfrom = validfrom_date
                            new_crew_annotation_rec.validto = validto_date
                            new_crew_annotation_rec.entrytime =current_time
                            new_crew_annotation_rec.code = TM.annotation_set.getOrCreateRef(('CM',))
                            new_crew_annotation_rec.property =-1
                            new_crew_annotation_rec.username = user_name
                            print "Saved Crew annotation record for crew ={}".format(record_id) +str(new_crew_annotation_rec)
                    except:
                        print "Could not create entry for crew {}".format(record_id)
                        traceback.print_exc()
                
                try:
                    for rec in unique_crew_annotation:
                            month = getMonth(record_time_new)
                            year  = getYear(record_time_new)
                            validfrom_date = AbsTime(AbsDate(year,month,1))
                            validto_date = AbsTime(AbsDate(year,month+1,1))
                            unique_crew_id =_get_crew_from_extperkey(rec['ID'])
                            crew_ref = TM.crew.getOrCreateRef((unique_crew_id.id,))
                            user_name = Names.username()
                            seqnr = createSeqNr(crew_ref)
                            new_crew_annotation_rec =TM.crew_annotations.create((unique_crew_id,seqnr))
                            new_crew_annotation_rec.isvisible =True
                            new_crew_annotation_rec.validfrom = validfrom_date
                            new_crew_annotation_rec.validto = validto_date
                            new_crew_annotation_rec.entrytime =current_time
                            new_crew_annotation_rec.code = TM.annotation_set.getOrCreateRef(('CM',))
                            new_crew_annotation_rec.property =-1
                            new_crew_annotation_rec.username = user_name
                            new_crew_annotation_rec.text = rec['text'] 
                            print "Saved Crew annotation record for crew ={}".format(record_id) +str(new_crew_annotation_rec)
                except:
                        print "Could not create entry for crew {}".format(unique_crew_id)       
                
                TM.save()
                                
                csv_file.close()
                now = datetime.now()
                backup_file_name = f.split('.')[0]+str(now.strftime("%Y%m%d%H%M%S"))+".csv"
                shutil.move(csv_path,os.path.join(backup_folder,backup_file_name))

    def run_meal_opt_out():
        for f in os.listdir(path):
                meal_opt_out_files.append(f)
                record_process()
      
    meal_opt_out_files = []    

    backup_folder = os.path.join(os.environ['CARMTMP'], 'ftp', 'crew_meal_optout_imported')
    path = os.path.join(os.environ['CARMTMP'], 'ftp', 'in')
    print "after path"
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    run_meal_opt_out()
                       
def run():
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

     








