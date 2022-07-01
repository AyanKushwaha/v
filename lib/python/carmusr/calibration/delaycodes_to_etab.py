import csv  
import re
from datetime import datetime
from dateutil.parser import parse
import Crs
import os
import getopt
import sys
import re
from datetime import datetime, timedelta, date
import shutil

# UsageException ---------------------------------------------------------{{{2
class UsageException(RuntimeError):
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

        
class Reader(object):
    ''' 
    A class to read a table from SAS with delay codes  and convert 
    it to the operational code data format.
    '''
    def do_it(self):
        
        source_folder = os.path.join(os.environ['CARMTMP'], 'ftp', 'in')
        backup_folder = os.path.join(os.environ['CARMTMP'], 'ftp', 'delaycode_import_processed')
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        NEW_PATH =os.path.join(os.environ['CARMDATA'], 'ETABLES', 'calibration','db')

        csv_files = []
        for root, _, files in os.walk(source_folder):
            if self.verbose:
                print "files", root, files
            csv_files += [os.path.join(root, f) for f in files if self._accept_csv(f)]
        if self.verbose:
            print "========================== Import from Delay codes =================="
            print "at ",source_folder
            print "found ",csv_files

        for f in csv_files:    
            new_List = ['/*',
                        '@pmp 500', 
                        '@departure_early_limit 0:30',
                        '@departure_late_limit 4:00',
                        '*/',
                        '',
                        '9',
                        'Sflight_carrier,',
                        'Iflight_number,',
                        'Sleg_flight_suffix,',
                        'Sdeparture_airport_name,',
                        'Adeparture_utc,',
                        'Sdelay_code1,',
                        'Idelay_duration1,',
                        'Sdelay_code2,',
                        'Idelay_duration2,',
                        '']
            
            with open(f,'rb') as csvfile:
                reader = csv.reader(csvfile,delimiter=';')
                header_size = 1
                for _ in xrange(header_size):
                    row = reader.next()

                for row in reader:
                    delay_code1 =  '\"' + row[4] + '\"'
                    if row[5] == "":
                        delay_duration1 = "0"
                    else:
                        delay_duration1 = "%d" % (int(row[5]))
                    delay_code2 = '\"' + row[6] + '\"'
                    if row[7] == "":
                        delay_duration2 =  "0"
                    else:
                        delay_duration2 = "%d" % (int(row[7]))

                    if delay_code1 == '':
                        continue
                    
                    flight_carrier = '\"' + row[1][:2] + '\"'
                    flight_number = row[1][2:]
                    
                    departure_utc = row[0] 

                    try:
                        departure_datetime = parse(row[0])
                        departure_date = departure_datetime.strftime('%d%b%Y').upper()
                    except (ValueError): 
                        departure_date = row[0]

                    dep_time_utc = row[2].zfill(4)
                    hour = dep_time_utc[:2]
                    minute = dep_time_utc[2:]
                    departure_utc = departure_date + ' ' + hour + ':' + minute

                    departure_airport =  '\"' + row[3] + '\"'

                    operational_code_row = [ flight_carrier,
                                            flight_number,
                                            '"*"' ,
                                            departure_airport,
                                            departure_utc,
                                            delay_code1,
                                            delay_duration1,
                                            delay_code2,
                                            delay_duration2 ]

                    new_List.append(', '.join(operational_code_row) + ';')
           
            filename_pattern = re.compile(r'(DelayCode_[0-9]{2}[a-zA-Z]{3}(?:[0-9]{4}))')
            filename = filename_pattern.search(f).group()
            print "Delay Code: csvfilename ",filename
            print "Delay Code: csvfilepath ",NEW_PATH
            NEW_FILE_PATH= "%s/%s.etab" % (NEW_PATH,filename)
            print "ETAB file Path: ",NEW_FILE_PATH
            with open(NEW_FILE_PATH,'wb') as file:
                for row in new_List:
                    file.write(row + '\n')
            shutil.move(f, backup_folder)
            
    def _accept_csv(self, fname):
        pattern = re.compile(r'^(DelayCode_[0-9]{2}[a-zA-Z]{3}(?:[0-9]{2}|[0-9]{4}).csv)$')
        if pattern.match(fname) is not None:
            if os.path.splitext(fname)[1].lower() == '.csv':
                date_pattern = re.compile(r'([0-9]{2}[a-zA-Z]{3}(?:[0-9]{4}))')
                res = date_pattern.search(fname)
                if res:
                    margin = timedelta(days=30)  # Set how long span should be allowed
                    today = date.today()
                    filedate = datetime.strptime(res.group(), '%d%b%Y')
                    if today - margin <= filedate.date() and filedate.date() <= today:
                        return True
                    else:
                        print "Delay Code: filename ",fname, "outside valid date interval"
                        return False
        return False

    def getResource(self,module,property):
        """
        Reads personal resource from module/property
        """
        return  Crs.CrsGetModuleResource(module,
                                           Crs.CrsSearchModuleDef,
                                           property)
    
    def __init__(self):
    
        self.verbose = False
        if len(sys.argv) != 0:
            print sys.argv
            try:
                try:
                    optlist, params = getopt.getopt(sys.argv[1:], "v",
                            [
                                "verbose",
                            ]
                    )
                except getopt.GetoptError, msg:
                    raise UsageException(msg)
                print optlist
                for (opt, value) in optlist:
                    if opt in ('-v', '--verbose'):
                        self.verbose = True
                    else:
                        pass
            except Exception, err:
                print >>sys.stderr, err.msg
                print >>sys.stderr, "only available option --verbose"

                

if __name__ == "__main__":
    transformer = Reader()
    transformer.do_it()
