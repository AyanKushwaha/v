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
            'updated_MFF_qual_count'     :0,
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
        # Added for SKCMS-3296
        self._crew_qualification_A2NX(delta_date)
        self._crew_MFF_contract(delta_date)
        # End for SKCMS-3296
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

            # Check if crew qualification is applicable for interface, A2NX is not added here
            if self._applicable_qual(qual, crew):
                # In case crew is having valid MFF-A2A3 or A2A5 contract,
                # no assigment will be send for seperate qualifications
                MFF_contract_group = crew_MFF_congrouptype(crew,curr_day,True)
                if (MFF_contract_group == "MFF-A2A3") or (MFF_contract_group == "MFF-A2A5"):
                    log.info('Skipping sending update for MFF crew {crew}'.format(crew=crew))
                    continue
                else:
                    # Assignment will be send for all valid qualifications
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

        # Checking for qualification deassignment data
        for rec in deassignment_filter:
            crew = rec.crew.id
            qual = rec.qual.subtype
            validfrom = rec.validfrom
            validto = rec.validto

            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue

            # Check if crew qualification is applicable for interface, A2NX added only for deassigment for pilots
            rank = rank_from_id(crew, curr_day)
            is_cc = is_cabin_crew(crew, rank)

            if self._applicable_qual(qual, crew) or (qual == "A2NX" and not is_cc):
                # In case crew is having valid MFF-A2A3 or A2A5 contract,
                # no deassigment will be send for seperate qualifications except A2NX
                MFF_contract_group = crew_MFF_congrouptype(crew,curr_day,False)
                if ((MFF_contract_group == "MFF-A2A3") or (MFF_contract_group == "MFF-A2A5")) and qual != "A2NX":
                    log.info('Skipping sending deassigment for MFF crew {crew}'.format(crew=crew))
                    continue
                else:
                    # Deassigment will be send for all qualifications

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

        # Checking for assignment data from crew employment table
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

        # Checking deassignment data from crew employment table
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
        applicable_for_fc = ('38', 'A2', 'A3','A5')
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
        elif not cc and qual in ('38', 'A2', 'A3','A5', 'A2NX', 'A2A3', 'A2A5'):
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
        # MFF Qualification count       : {updated_MFF_qual}
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
            updated_MFF_qual = self._stats['updated_MFF_qual_count'],
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
        crew_data = crew_emp_table.search("(validfrom={0})".format(curr_date))
        list_crew_empchange = []
        # Checking for extperkey change from crew employment table 
        for rec in crew_data:
            crew = rec.crew.id
            rank = rec.crewrank.id
            extperkey = rec.extperkey 
            validfrom = rec.validfrom
            validto = rec.validto
            log.info('Crew having validfrom as today date: {crew}'.format(crew=crew))
            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue
           

           
           # Search in crew_employment table is same crew exists with validto as either today or old date
            crew_change_extperkey_data = crew_emp_table.search('(&(crew={crew})(validto={validto}))'.format(
            crew=crew,
            validto=curr_date
            ))
            for rec_end in crew_change_extperkey_data:
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
                if self._applicable_qual(qual, crew) or qual == "A2NX":
                    # In case crew is having valid MFF-A2A3 or MFF-A2A5 contract,
                    # assigment will be send for DN-Pilot A32 A330/DN-Pilot A32 A350
                    MFF_contract_group = crew_MFF_congrouptype(crew,curr_date,True)
                    if (MFF_contract_group == "MFF-A2A3") or (MFF_contract_group == "MFF-A2A5"):
                        if MFF_contract_group == "MFF-A2A3":
                            qual = "A2A3"
                        else:
                            qual = "A2A5"
                        self._stats['total_delta_count'] += 1
                        self._stats['updated_MFF_qual_count'] += 1
                    else:
                        # Assignment will be send for all valid qualifications
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

    def _crew_qualification_A2NX(self, curr_date):

        crew_training_log_t = tm.table('crew_training_log')
        curr_date_dt = abs_to_datetime(curr_date)
        curr_date_ext= AbsTime(curr_date_dt.year, curr_date_dt.month, curr_date_dt.day, 24, 0)

        # Checking for assignment data from crew_training_log table
        assignment_data = crew_training_log_t.search('(&(code={code})(tim>={curr_date})(tim<={curr_date_ext}))'.format(
        code="LRP2",
        curr_date=curr_date,
        curr_date_ext=curr_date_ext
        ))
        for rec in assignment_data:
            crew = rec.crew.id
            typ = rec.typ
            code = rec.code
            time = rec.tim
            validfrom = curr_date
            validto = curr_date
            if is_retired(crew) or (extperkey_from_id(crew, today_in_abstime()) in test_crew_emp_no):
                log.info('Skipping sending update for retired crew {crew}'.format(crew=crew))
                continue

            log.info('Crew having LRP2 code {crew}'.format(crew=crew))
            # Create assignment entries
            assignment_data = self._create_entries(crew, validfrom, validto, "A2NX", None, "assignment_data")
            self.assignment_writer.write(assignment_data)
        # For  deassignment of A2NX the code in _qualification_deltas will take care, Added A2Nx in deassigment qualification check

    def _crew_MFF_contract(self, curr_date):

        crew_contract_t = tm.table('crew_contract')
        crew_contract_set_t = tm.table('crew_contract_set')
        crew_qual_t = tm.table('crew_qualification')
        congrouptype_query = '(|(congrouptype=MFF-A2A3)(congrouptype=MFF-A2A5))'

        assignment_crew_filter = crew_contract_t.search('(validfrom={validfrom})'.format(
        validfrom=curr_date))
        # Checking in crew_contract table for the crew who got their contarct updated on today's date
        for rec in assignment_crew_filter:
            crew = rec.crew.id
            contract = rec.contract.id
            validfrom = rec.validfrom
            validto = rec.validto
            log.info('Crew got contract updated on todays date: {crew} and contract id {contractid}'.format(crew=crew, contractid=contract))
            # Checking for MFF contract in crew_contract_set table

            mff_records_assign = crew_contract_set_t.search('(&(id={contract}){congrouptype_query})'.format(
                contract=contract,
                congrouptype_query=congrouptype_query))
            for rec_congrouptype in mff_records_assign:
                congrouptype=rec_congrouptype.congrouptype.id
                if congrouptype == "MFF-A2A3":
                    qual = "A2A3"
                elif congrouptype == "MFF-A2A5":
                    qual = "A2A5"
                else:
                    continue
                #Create an assigment entry for MFF Qualification such as DN-Pilot A32 A330/DN-Pilot A32 A350
                self._stats['total_delta_count'] += 1
                self._stats['updated_MFF_qual_count'] += 1
                log.info('''
                MFF Qualification for crew {crew} - {qual}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    qual=congrouptype,
                    validfrom=validfrom,
                    validto=validto
                    ))

                assignment_data = self._create_entries(crew, validfrom, validto, qual, None, "assignment_data")
                self.assignment_writer.write(assignment_data)

                # Checking for deassignment data from crew_qualification table
                for rec_qual in crew_qual_t.search('(&(crew={crew})(validfrom<{validfrom})(validto>{validto}))'.format(
                    crew=crew,
                    validfrom=curr_date,
                    validto=curr_date)):
                    validfrom=rec_qual.validfrom
                    validto=rec_qual.validto
                    qual_subtype= rec_qual.qual.subtype
                    # Create deassigment for all qualifications except A2NX which are valid in crew_qualification table
                    # as the assignment has been send for MFF qualification
                    if self._applicable_qual(qual_subtype, crew) and qual_subtype != "A2NX":
                        self._stats['total_delta_count'] += 1
                        self._stats['updated_qual_count'] += 1
                        log.info('''
                        Deassigment Qualification for crew due to MFF{crew} - {qual}
                        Valid from {validfrom}
                        Valid to {validto}
                        '''.format(
                            crew=crew,
                            qual=congrouptype,
                            validfrom=validfrom,
                            validto=validto
                            ))
                        deassignment_data = self._create_entries(crew, validfrom, validto, qual_subtype, None, "deassignment_data")
                        self.deassignment_writer.write(deassignment_data)

        # Checking for deassignment data from crew_contract table
        deassignment_crew_filter = crew_contract_t.search('(validto={validto})'.format(validto=curr_date))
        # Checking in crew_contract table for the crew who got their contarct updated on today's date
        for rec in deassignment_crew_filter:
            crew=rec.crew.id
            contract=rec.contract.id
            validfrom =rec.validfrom
            validto = rec.validto
            log.info('Crew got contract end date as todays date:{crew} and contract id {contractid}'.format(crew=crew, contractid=contract))

            # Checking for MFF contract in crew_contract_set table
            mff_records_deassign = crew_contract_set_t.search('(&(id={contract}){congrouptype_query})'.format(
                contract=contract,
                congrouptype_query=congrouptype_query))

            for rec_congrouptype in mff_records_deassign:
                congrouptype=rec_congrouptype.congrouptype.id
                if congrouptype == "MFF-A2A3":
                    qual = "A2A3"
                elif congrouptype == "MFF-A2A5":
                    qual = "A2A5"
                else:
                    continue
                log.info('Crew - {crew} is having end date for MFF contract'.format(crew=crew))
                #Create an deassigment entry for MFF Qualification such as DN-Pilot A32 A330/DN-Pilot A32 A350
                self._stats['total_delta_count'] += 1
                self._stats['updated_MFF_qual_count'] += 1
                log.info('''
                MFF Qualification deassigment for crew {crew} - {qual}
                Valid from {validfrom}
                Valid to {validto}
                '''.format(
                    crew=crew,
                    qual=congrouptype,
                    validfrom=validfrom,
                    validto=validto
                    ))
                deassignment_data = self._create_entries(crew, validfrom, validto, qual, None, "deassignment_data")
                self.deassignment_writer.write(deassignment_data)

                # Checking for assignment data from crew_qualification table as MFF contract is ended
                for rec_qual in crew_qual_t.search('(&(crew={crew})(validto>{validto}))'.format(crew=crew,validto=curr_date)):
                    validfrom=rec_qual.validfrom
                    validto=rec_qual.validto
                    qual_subtype= rec_qual.qual.subtype
                    # Create assigment for all qualifications except A2NX which are valid in crew_qualification table
                    # as the MFF contract is ended
                    if self._applicable_qual(qual_subtype, crew) and qual_subtype != "A2NX":
                        self._stats['total_delta_count'] += 1
                        self._stats['updated_qual_count'] += 1
                        log.info('''
                        Qualification assigment for crew due to MFF ended {crew} - {qual}
                        Valid from {validfrom}
                        Valid to {validto}
                        '''.format(
                            crew=crew,
                            qual=congrouptype,
                            validfrom=validfrom,
                            validto=validto
                            ))
                        assignment_data = self._create_entries(crew, validfrom, validto, qual_subtype, None, "assignment_data")
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


def crew_MFF_congrouptype(crew_id,curr_date,assignment):
    # Pick the crew contract from crew_contract table,
    # condition is validto greater than as we are picking the valid contract for this crew
    # and later checking in the crew_contract_set table for MFF contract
    crew_contract_t = tm.table('crew_contract')
    crew_contract_set_t = tm.table('crew_contract_set')
    # assignment condition is added so that when MFF is deassigned the deassigment of qualification 
    # is not send for the qualification which is ended on that particular day
    if assignment:
        crew_contract_data = crew_contract_t.search('(&(crew={crew})(validto>{validto}))'.format(
        crew=crew_id,
        validto=curr_date
        ))
    else:
        crew_contract_data = crew_contract_t.search('(&(crew={crew})(validto={validto}))'.format(
        crew=crew_id,
        validto=curr_date
        ))
    # Checking for the contract of this crew in crew_contract table
    congrouptype = None
    for rec in crew_contract_data:
        crew=rec.crew.id
        contract=rec.contract.id
        validfrom =rec.validfrom
        validto = rec.validto
        log.info('Crew having valid contract: {crew} and contract id {contractid}'.format(crew=crew, contractid=contract))
        # Picking the congrouptype from crew_contract_set table on the basis of contract id
        crew_MFFcontract = crew_contract_set_t.search('(id={contract})'.format(
            contract=contract
        ))
        for rec_congroup in crew_MFFcontract:
            if rec_congroup.congrouptype != None:
                congrouptype = rec_congroup.congrouptype.id
    return congrouptype


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
        % (False, '', '', '38'))[0] == 'DN-Pilot 737'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A2'))[0] == 'DN-Pilot A32'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A3'))[0] == 'DN-Pilot A330'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A5'))[0] == 'DN-Pilot A350'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A2NX'))[0] == 'DN-Pilot A32 A321NX'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'

        % (False, '', '', 'A2A3'))[0] == 'DN-Pilot A32 A330'
    assert rave.eval('qualification.%%lms_qualification_name%%(%s, "%s", "%s", "%s")'
        % (False, '', '', 'A2A5'))[0] == 'DN-Pilot A32 A350'
    log.info('Mapping of CMS qualifications to LMS names OK!')


if __name__ == '__main__':
    test_mappings()
