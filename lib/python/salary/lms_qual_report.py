from modelserver import TableManager
from AbsTime import AbsTime
# from carmensystems.dbloader.replay.davedelta import DaveDelta
import carmensystems.rave.api as rave

import csv
from datetime import datetime 
# from dateutil.relativedelta import relativedelta
import logging
import os
from shutil import copyfile
import time

logging.basicConfig()
log = logging.getLogger('lms_qual_report')
log.setLevel(logging.INFO)

tm = TableManager.instance()

CARMDATA = os.getenv('CARMDATA')
REPORT_PATH = CARMDATA + '/REPORTS/HR/'
RELEASE_PATH = '/opt/Carmen/CARMTMP/ftp/out/SALARY_SEIP/'
test_crew_emp_no = ['999991']

class LMSQualReport:
    def __init__(self, test=False):
        self.test = test
        self.default_delta_date = today_in_abstime()
        self.assignment_writer = AssignmentReportWriter()
        self.deassignment_writer = DeassignmentReportWriter()
        self._stats = {
            'total_delta_count'     : 0,
            'updated_qual_count'    : 0,
            'updated_rank_count'    : 0,
            'skipped_same_rank_count'   : 0,
            'skipped_upgrade_rank_count'    : 0,
            'skipped_degrade_rank_count'    : 0,
            'emp_change_count'    : 0
        }
        if self.test:
            log.setLevel(logging.DEBUG)

    # you can paas date while calling ganerate method 
    # and formate is yyyymmdd
    # eg : delta_date = 20210525 
    # then it  will generate report for 24May2021  
    def generate(self, crew_ids=[], delta_date=None):
        exec_start = time.time()
        if delta_date is None:
            delta_date = today_in_abstime()
        else:
            delta_date = AbsTime(delta_date)
        
        log.info('Generating qualifications for LMS at {dt}...'.format(dt=delta_date))

        self._qualification_deltas(delta_date)
        self._crew_employment_deltas(delta_date)
        self._crew_employment_change(delta_date)
        exec_end = time.time()
        exec_time = round(exec_end - exec_start, 2)
        self._info_dump(exec_time)
        if not self.test:
            if self.assignment_writer.row_count > 0:
                self.assignment_writer.release()
            if self.deassignment_writer.row_count > 0:
                self.deassignment_writer.release()

    def _qualification_deltas(self,delta_date):
        
        crew_qual_table = tm.table('crew_qualification')
        curr_day = delta_date 

        assignment_filter = crew_qual_table.search("(validfrom={0})".format(curr_day))
        deassignment_filter = crew_qual_table.search("(validto={0})".format(curr_day))

        # checking for assignment qualification data 
        for rec in assignment_filter:
            crew = rec.crew.id
            qual = rec.qual.subtype
            validfrom = rec.validfrom
            validto = rec.validto

            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue

            # Check if crew qualification is applicable for interface
            if self._applicable_qual(qual, crew):
                self._stats['total_delta_count'] += 1
                self._stats['updated_qual_count'] += 1 
                log.info('''
                Qualification for crew {crew} - {qual}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    qual=qual,
                    validfrom=validfrom,
                    validto=validto
                    ))  

                # Create deassignment entries
                assignment_data = self._create_entries(crew, validfrom, validto, qual, None, "assignment_data")
                self.assignment_writer.write(assignment_data)

        # checking for qualification deassignment data 
        for rec in deassignment_filter:
            crew = rec.crew.id
            qual = rec.qual.subtype
            validfrom = rec.validfrom
            validto = rec.validto
            print rec 

            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue

            # Check if crew qualification is applicable for interface
            if self._applicable_qual(qual, crew):
                self._stats['total_delta_count'] += 1
                self._stats['updated_qual_count'] += 1 
                log.info('''
                Qualification for crew {crew} - {qual}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    qual=qual,
                    validfrom=validfrom,
                    validto=validto
                    ))    
    
                # Create & write qualification deassignment entries
                deassignment_data = self._create_entries(crew, validfrom, validto, qual, None, "deassignment_data")
                self.deassignment_writer.write(deassignment_data)

    
    def _crew_employment_deltas(self, delta_date):
        
        crew_emp_table = tm.table('crew_employment')
        curr_day = delta_date

        assignment_filter = crew_emp_table.search("(&(crewrank={crewrank})(validfrom={validfrom}))".format( crewrank="AP", validfrom=curr_day))
        deassignment_filter = crew_emp_table.search("(&(crewrank={crewrank})(validto={validto}))".format( crewrank="AP", validto=curr_day))

        total_assignment_data = []
        total_deassignment_data = []

        # checking for assignment data from crew employment table 
        for rec in assignment_filter:
            crew = rec.crew.id
            rank = rec.crewrank.id 
            validfrom = rec.validfrom
            validto = rec.validto
            
            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue

            # Only cabin crew applicable for rank based qualifications to LMS
            if is_cabin_crew(crew, rank):
                self._stats['total_delta_count'] += 1
                self._stats['updated_rank_count'] += 1
                log.info('''
                New cabin crew {crew} - {rank}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    rank=rank,
                    validfrom=validfrom,
                    validto=validto
                    ))

                assignment_data = self._create_entries(crew, validfrom, validto, None, rank, "assignment_data")
                total_assignment_data.append(assignment_data)

        # checking deassignment data from crew employment table 
        for rec in deassignment_filter:
            crew = rec.crew.id
            rank = rec.crewrank.id 
            validfrom = rec.validfrom
            validto = rec.validto
            
            if extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no:
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue
            

            # Only cabin crew applicable for rank based qualifications to LMS
            if is_cabin_crew(crew, rank):
                self._stats['total_delta_count'] += 1
                self._stats['updated_rank_count'] += 1
                log.info('''
                New cabin crew {crew} - {rank}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    rank=rank,
                    validfrom=validfrom,
                    validto=validto
                    ))

                deassignment_data = self._create_entries(crew, validfrom, validto, None, rank, "deassignment_data")
                total_deassignment_data.append(deassignment_data)

        for rec in total_assignment_data:
            if self.rank_status(rec,total_assignment_data,total_deassignment_data) in ("upgrade",True):
                self.assignment_writer.write(rec)
        
        for rec in total_deassignment_data:
            if self.rank_status(rec,total_assignment_data,total_deassignment_data) in ("degrade",True):
                self.deassignment_writer.write(rec)


    def rank_status(self,rec,total_assignment_data,total_deassignment_data):
        
        crew_rank_order = {"DN-Cabin AP":1, "DN-Cabin":2}
        
        for as_rec in total_assignment_data:
            for ds_rec in total_deassignment_data:
                if as_rec['studentID'] == ds_rec['studentID'] == rec['studentID']:
                    if as_rec['qualificationID'] == ds_rec['qualificationID']:
                        self._stats['skipped_same_rank_count'] += 1
                        return "same"
                    elif crew_rank_order[as_rec['qualificationID']] < crew_rank_order[ds_rec['qualificationID']]:
                        self._stats['skipped_upgrade_rank_count'] += 1
                        return "upgrade" 
                    elif crew_rank_order[as_rec['qualificationID']] > crew_rank_order[ds_rec['qualificationID']]:
                        self._stats['skipped_degrade_rank_count'] += 1
                        return "degrade"
        return True 


    def _create_entries(self, crew, validfrom, validto, qual=None,rank=None,report_flag=None):
        log.info('Creating new assignment and deassignment entries')
        base_data = {
            'studentID'         : extperkey_from_id(crew, today_in_abstime()),
            'qualificationID'   : self._map_to_LMS_name(crew, qual=qual, rank=rank),
            'priority'          : 1
        }
        if report_flag == "assignment_data":
            assignment_data = base_data
            assignment_data['assignmentDate'] = report_formatted_date(validfrom)
            return assignment_data
        elif report_flag == "deassignment_data":
            deassignment_data = base_data
            deassignment_data['deassignmentDate'] = report_formatted_date(validto)
            return deassignment_data
        
        
    def _applicable_qual(self, qual, crew_id):
        applicable_for_cc = ('MENTOR', 'PMM','A2', 'AL','38')
        applicable_for_fc = ('36', '37', '38', 'A2', 'A3', 'A4','A5')
        rank = rank_from_id(crew_id, today_in_abstime())
        
        if is_cabin_crew(crew_id, rank):
            return qual in applicable_for_cc
        else:
            return qual in applicable_for_fc

    def _map_to_LMS_name(self, crew_id, qual=None, rank=None): 
        name = ''
        rank = rank_from_id(crew_id, today_in_abstime()) if rank is None else rank
        cc = is_cabin_crew(crew_id, rank)
        if cc and qual is None:          
            name = rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
                % (True, rank, '', 'ALL'))[0]
        elif cc and qual in ('MENTOR', 'PMM','A2', 'AL','38'):
            name = rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
                % (True, 'CC', '', qual))[0]
        elif not cc and qual in ('36', '37', '38', 'A2', 'A3', 'A4','A5'):
            name = rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
                % (False, '', '', qual))[0]
        return name
    
    def _validto_changed(self, validto_before, validto_after):
        return validto_before != validto_after

    def _info_dump(self, exec_time):
        log.info('''
        ##########################################################
        # Qualifications report generated for LMS
        # -----
        # Total records count           : {total_deltas}
        # Qualifications count          : {updated_qual}
        # Rank (for CC) count           : {updated_rank}
        # Skipped Same Rank count       : {skipped_srank}
        # Skipped Upgrade Rank count    : {skipped_urank}
        # Skipped Degrade Rank count    : {skipped_drank}
        # Extperkey Change Count        : {emp_qual}
        # -----
        # Assignments created           : {assignment_rows}
        # Deassignments created         : {deassignment_rows}
        # -----
        # Execution time                : {exec_time} sec
        # Report location
        # {assignment_report}
        # {deassignment_report}
        # Report released to SEIP       : {released}
        ##########################################################
        '''.format(
            total_deltas=self._stats['total_delta_count'],
            updated_qual=self._stats['updated_qual_count'],
            updated_rank=self._stats['updated_rank_count'],
            skipped_srank=self._stats['skipped_same_rank_count'],
            skipped_urank=self._stats['skipped_upgrade_rank_count']//2,
            skipped_drank=self._stats['skipped_degrade_rank_count']//2,
            emp_qual = self._stats['emp_change_count'],
            assignment_rows=self.assignment_writer.row_count,
            deassignment_rows=self.deassignment_writer.row_count,
            exec_time=exec_time,
            assignment_report=self.assignment_writer.report_file,
            deassignment_report=self.deassignment_writer.report_file,
            released='True' if not self.test else 'False'       
        ))
       
    def _crew_employment_change(self, curr_date):

        crew_emp_table = tm.table('crew_employment')
        assignment_data = crew_emp_table.search("(validfrom={0})".format(curr_date))
        list_crew_empchange = []
        # Checking for extperkey change from crew employment table 
        for rec in assignment_data:
            crew = rec.crew.id
            rank = rec.crewrank.id
            extperkey = rec.extperkey 
            validfrom = rec.validfrom
            validto = rec.validto
            log.info('Crew having validfrom as today date: {crew}'.format(crew=crew))
            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue
           
           # Search in crew_employment table if same crew exists with validto as either today or old date
            deassignment_data = crew_emp_table.search('(&(crew={crew})(validto<={validto}))'.format(
            crew=crew,
            validto=curr_date
            ))
            for rec_end in deassignment_data:
                #If crew found in the crew_employment table having validto as either current date or less
                if rec_end.crew.id == crew:
                    if rec_end.extperkey != extperkey:
                        self._stats['emp_change_count'] += 1
                        log.info('''
                        Crew {crew} - Old Emp {oldextperkey} New Emp {newextperkey} 
                        Valid from {validfrom}
                        Valid to {validto}
                        '''.format(
                            crew=crew,
                            oldextperkey=rec_end.extperkey,
                            newextperkey=extperkey,
                            validfrom=validfrom,
                            validto=validto
                            ))                   
                        list_crew_empchange.append(crew)
                        break
        # Fetching all qualification and rank AP for the crew with employee number i.e. extperkey change
        for rec in list_crew_empchange:
            crew = rec
            crew_qual_table = tm.table('crew_qualification')
            assignment_data_qual = crew_qual_table.search('(&(crew={crew})(validto>{validto}))'.format(
            crew=crew,
            validto=curr_date
            ))
            # Creating assignment entries for all qualification belonging to a crew 
            for rec in assignment_data_qual:
                crew = rec.crew.id
                qual = rec.qual.subtype
                validfrom = rec.validfrom
                validto = rec.validto
                # Check if crew qualification is applicable for interface
                if self._applicable_qual(qual, crew):
                    self._stats['total_delta_count'] += 1
                    self._stats['updated_qual_count'] += 1
                    log.info('''
                    Qualification for crew {crew} - {qual}
                    Valid from {validfrom}
                    Valid to {validto}
                    '''.format(
                        crew=crew,
                        qual=qual,
                        validfrom=validfrom,
                        validto=validto
                        ))

                    # Create assignment entries
                    assignment_data = self._create_entries(crew, validfrom, validto, qual, None, "assignment_data")
                    self.assignment_writer.write(assignment_data)
            # DN-CABIN AP needs to be send again if crew employee number is changed
            crew_emp_table = tm.table('crew_employment')
            assignment_data_rank = crew_emp_table.search("(&(crew={crew})(crewrank={crewrank})(validto>{validto}))".format(crew=crew,crewrank="AP", validto=curr_date))
            # checking for assignment data from crew employment table
            for rec_emp in assignment_data_rank:
                crew = rec_emp.crew.id
                rank = rec_emp.crewrank.id
                validfrom = rec_emp.validfrom
                validto = rec_emp.validto

                if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                    log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                    continue
                # Only cabin crew applicable for rank based qualifications to LMS
                if is_cabin_crew(crew, rank):
                    self._stats['total_delta_count'] += 1
                    self._stats['updated_rank_count'] += 1
                    log.info('''
                    New cabin crew {crew} - {rank}
                    Valid from {validfrom}
                    Valid to {validto}
                    '''.format(
                        crew=crew,
                        rank=rank,
                        validfrom=validfrom,
                        validto=validto
                        ))
                    assignment_data = self._create_entries(crew, validfrom, validto, None, rank, "assignment_data")
                    self.assignment_writer.write(assignment_data)

class ReportWriter:
    def __init__(self):
        self._create_report_dir()
        self._report_name = self._report_name()
        self._report_file = self._report_file(self._report_name)
        self._row_count = 0

    @property
    def row_count(self):
        return self._row_count
    
    @property
    def report_file(self):
        return self._report_file

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def __str__(self):
        return self.get_classname()

    def _report_type(self):
        pass

    def write(self, raw_data):
        """
        Entry point for creating the CSV reports. 
        :param
        raw_data either assignement or deassignments of qualifications
        """
        if not os.path.exists(self._report_file):
            self._create_report_file()
        formatted_data = self._format_row(raw_data)
        self._write_to_file(formatted_data)
  
    def release(self):
        """
        Called to release generated report files to SEIP pickup
        directory /opt/Carmen/CARMTMP/ftp/out/
        """
        log.info('Releasing {type} report to {path}'.format(type=self._report_type(), path=RELEASE_PATH))
        copyfile(self._report_file, RELEASE_PATH + self._report_name)

    def _format_row(self, raw_data):
        student_id = raw_data['studentID']
        qualification_id = raw_data['qualificationID']
        date = raw_data['{type}Date'.format(type=self._report_type())]
        priority = raw_data['priority']
        return (student_id, qualification_id, date, priority)

    def _report_name(self):
        report_filename = 'LMS_{type}_{date}.csv'.format(type=self._report_type(), date=report_name_date())
        return report_filename

    def _report_file(self, filename):        
        report_path = '{path}{report}'.format(path=REPORT_PATH, report=filename)
        return report_path

    def _create_report_dir(self):
        if not os.path.exists(REPORT_PATH):
            os.makedirs(REPORT_PATH)

    def _create_report_file(self):
        with open(self._report_file, 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(self.headers)

    def _write_to_file(self, formatted_data):
        log.info('Writing {row} to {report}'.format(row=formatted_data, report=self._report_name))
        with open(self._report_file, 'a+', 1000) as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(formatted_data)
            self._row_count += 1


class AssignmentReportWriter(ReportWriter):
    def __init__(self):
        ReportWriter.__init__(self)
        self.headers = ('studentID', 'qualificationID', 'assignmentDate', 'priority')

    def _report_type(self):
        return 'assignment'


class DeassignmentReportWriter(ReportWriter):
    def __init__(self):
        ReportWriter.__init__(self)
        self.headers = ('studentID', 'qualificationID', 'deassignmentDate', 'priority')

    def _report_type(self):
        return 'deassignment'


# Utilities
def today_in_abstime():
    now = datetime.now()
    return AbsTime(now.year, now.month, now.day, 0, 0)

def default_delta_in_abstime():    
    previous_day = datetime.now() + relativedelta(days=-1)
    return AbsTime(previous_day.year, previous_day.month, previous_day.day, 0, 0)

def report_name_date():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def report_formatted_date(abstime):
    dt = abs_to_datetime(abstime)
    return dt.strftime('%Y-%m-%d')


def abs_to_datetime(abstime):
    abs_str = abstime.getValue()
    day     = int(abs_str[0:2])
    month   = datetime.strptime(abs_str[2:5], '%b').month
    year    = int(abs_str[5:9])
    hour    = int(abs_str[10:12])
    minute  = int(abs_str[13:15])

    return datetime(year, month, day, hour, minute)


def extperkey_from_id(crew_id, date):
    extperkey = rave.eval('model_crew.%extperkey_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id,
        dt=date)
        )[0]
    if extperkey is None:
        # In some cases crew has their extperkeys seen as crew id when using r.context('sp_crew')
        log.debug('Actual extperkey used as used as crew id')
        return crew_id
    return extperkey


def rank_from_id(crew_id, date):
    rank = rave.eval('model_crew.%crewrank_at_date_by_id%("{crew_id}", {dt})'.format(
        crew_id=crew_id,
        dt=date
    ))[0]
    return rank


def is_cabin_crew(crew_id, rank):
    crew_rank_set_t = tm.table('crew_rank_set')
    crew_rank_iter = crew_rank_set_t.search('(id={0})'.format(rank))
    crew_rank = next(crew_rank_iter)
    return crew_rank.maincat.id == 'C'


def is_retired(crew_id):
    at_date = today_in_abstime()
    employment_status = rave.eval('model_crew.%group_at_date%("{crew_id}", {dt})'.format(
        crew_id=crew_id,
        dt=at_date
    ))[0]
    if employment_status == 'R':
        return True
    elif employment_status is None:
        # Check if extperkey is used as crew id and do a re-evaluation
        possible_crew_id = extperkey_to_crew_id(crew_id)
        if possible_crew_id != crew_id:
            # Do a re-evaluation with the probable crew_id
            employment_status = rave.eval('model_crew.%group_at_date%("{crew_id}", {dt})'.format(
                crew_id=crew_id,
                dt=at_date
            ))[0]
            if employment_status == 'R' or employment_status is None:
                return True
    return False


def extperkey_to_crew_id(crew_id_as_ext):
    at_date = today_in_abstime()
    crew_id = rave.eval('model_crew.%crew_id_from_extperkey%("{ext}", {dt})'.format(
        ext=crew_id_as_ext,
        dt=at_date
    ))[0]
    return crew_id


def test_mappings():
    log.info('Running tests on mappings between CMS qualifications and ranks to LMS names...')
    # Needs to be run in a studio instance
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, '', 'A', 'MENTOR'))[0] == 'DN-Cabin MT'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, '', 'A', 'PMM'))[0] == 'DN-Cabin PM'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, '', '', 'A2'))[0] == 'DN-Cabin A32'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, '', '', 'AL'))[0] == 'DN-Cabin A330/A350'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, '', '', '38'))[0] == 'DN-Cabin B737'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (True, 'AP', '', 'ALL'))[0] == 'DN-Cabin AP'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', '36'))[0] == 'DN-Pilot 737'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', '37'))[0] == 'DN-Pilot 737'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', '38'))[0] == 'DN-Pilot 737'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A2'))[0] == 'DN-Pilot A32'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A3'))[0] == 'DN-Pilot A34'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A5'))[0] == 'DN-Pilot A34'
    log.info('Mapping of CMS qualifications to LMS names OK!')


if __name__ == '__main__':
    test_mappings()
