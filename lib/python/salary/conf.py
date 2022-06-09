#!/bin/env python

# [acosta:06/073@15:15] Common functions.
# [acosta:06/251@13:32] Renamed.
# [acosta:08/111@19:41] Removed references to CRS, since that's not available
# when running from launcher.
#==============================================================================
import logging
import os
import Crs

"""
This module contains some constants.
Some of these can be altered, some other can be altered only after some
programming effort.
"""

# Set up logging --------------------------------------------------------{{{1
#__console = logging.StreamHandler()
#__console.setLevel(logging.DEBUG)
#__console.setFormatter(logging.Formatter('%(asctime)s: %(name)-12s: %(levelname)-8s %(message)s'))
#__rootlogger = logging.getLogger('')
#if len(__rootlogger.handlers) == 0:
#    __rootlogger.addHandler(__console)

logging.basicConfig(format='%(asctime)s: %(name)-12s: %(levelname)s: %(message)s')
# To change logging level -> conf.log.setLevel(logging.<LEVEL>)
log = logging.getLogger('salary')
log.setLevel(logging.DEBUG)


# These constants are safe to alter. -------------------------------------{{{1

# DIG channels for manual jobs
channel = 'salary_manual'
emailchannel = 'crewmailer'

# Job submitter for manual jobs
submitter = 'salary_manual_jobs'

# Where to store export files
exportDirectory = Crs.CrsGetModuleResource("salary", Crs.CrsSearchModuleDef, "ExportDirectory")
# Where to store released files
releaseDirectory = Crs.CrsGetModuleResource("salary", Crs.CrsSearchModuleDef, "ReleaseDirectory")
# Where to store generated PDF reports
reportDirectory = Crs.CrsGetModuleResource("salary", Crs.CrsSearchModuleDef, "ReportDirectory")
# Where to store generated PDF reports
crewStatementsDirectory = Crs.CrsGetModuleResource("salary", Crs.CrsSearchModuleDef, "CrewStatementsDirectory")

# NOTE!
# If any of the table names are changed, the file 'salary.xml' also has to 
# be updated.

# Names of temporary (memory) tables
tmp_salary_admin_code = 'tmp_salary_admin_code'
tmp_salary_format = 'tmp_salary_format'
tmp_salary_messages = 'tmp_salary_messages'
tmp_salary_pick_format = 'tmp_salary_pick_format'
tmp_salary_region = 'tmp_salary_region'
tmp_salary_run_id = 'tmp_salary_run_id'
tmp_salary_run_type = 'tmp_salary_run_type'

# For dynamic loading of file formatting record types
fileRecordPackage = "salary.rec"

# For dynamic loading of run type modules
runTypePackage = "salary.type"

# For dynamic loading of report type modules
rptPackage = "salary.rpt"

# These constants would need some programming effort to change. ---------{{{1

# Which context should be used
context = 'sp_crew'

# Run types, don't change order, the first should be about Per Diem, the second overtime

allowedRunTypes = ('PERDIEM', 'PERDIEMTAX', 'TEMP_CREW', 'OVERTIME', 'COMPDAYS', 'VACATION_R',
                   'VACATION_P', 'VACATION_Y', 'VACATIONYF', 'VACATIONYC', 'AMBI', 'SUPERVIS',
                   'ABSENCE', 'BUDGETED', 'OTHER', 'ALLOWNCE_M', 'ALLOWNCE_D', 'SCHEDULE', 'TCSCHEDULE',
                   'SCHED_CCSE')
runTypeDescription = {
    'AMBI': 'AMBI',
    'ABSENCE' : "Absence",
    'ALLOWNCE_M': 'Allowance (monthly)',
    'ALLOWNCE_D': 'Allowance (daily)',
    'BUDGETED' : "Budgeted time",
    'COMPDAYS': 'Comp. days',
    'OTHER': 'Other transactions',
    'OVERTIME': 'Overtime',
    'PERDIEM': 'Per Diem', 
    'PERDIEMTAX': 'Per Diem Tax', 
    'SUPERVIS': "Instructor's Allowance",
    'SCHEDULE': "Work Schedule",
    'TCSCHEDULE': "Work Schedule for temporary crew",
    'SCHED_CCSE': "Work Schedule CC SE",
    'TEMP_CREW': 'Temp. crew salary',
    'VACATION_P': 'Vacation (performed)',
    'VACATION_R': 'Vacation (remaining)',
    'VACATION_Y': 'Vacation (yearly)',
    'VACATIONYF': 'Vacation (yearly, Flight Deck)',
    'VACATIONYC': 'Vacation (yearly, Cabin Crew)',
}

# Run types listed here will not be checked against the currently
# loaded data period (i.e. for runs not requiring roster data).
runTypesWithoutCheckPlanningPeriod = [
    'VACATION_P',
    'VACATION_R'
] 



# These systems are allowed
allowedSalarySystems = ('DK', 'NO', 'SE', 'S2', 'CN', 'JP', 'HK', 'S3')

# These are the currencies to be used (SAP, PERDIEM)
currencies = {
    'DK': 'DKK',
    'NO': 'NOK',
    'SE': 'SEK',
    'S2': 'SEK',
    'CN': 'CNY',
    'JP': 'JPY',
    'HK': 'HKD',
    'S3': 'SEK',
}

# These are the bases for each country/salary system.
bases = {
    'DK': ['CPH'],
    'NO': ['OSL', 'SVG', 'TRD'],
    'SE': ['STO'],
    'S2': ['STO'],
    'CN': ['BJS', 'SHA'],
    'JP': ['NRT'],
    'HK': ['HKG'],
    'S3': ['STO'],
}

# These are the reports that need currencies.
need_currencies = ('PERDIEM',)

# This is the default cost center to be used (SAP - DK and NO), see api.py
cost_center = ''

# These formats are implemented (first is default)
allowedExportFormats = ('FLAT', 'HTML', 'CSV')

# Mapping between formats and file extensions.
fileExtensions = { 'HTML': ".html", 'CSV': ".csv" }

# Start of salary month parameter
startparam = 'salary.%salary_month_start_p%'

# End of salary month parameter
endparam = 'salary.%salary_month_end_p%'

# AMBI norm hours per day
ambiparam = 'ambi.%ambi_norm_p%'

# Valid ranks for vacation lists
validVacationRanks = ('FC', 'FP', 'FR', 'AP', 'AS', 'AH')

# Convertible crew minutes to be considered as F0-days
convertible_time = 240

# Alphabet groups considered for Per Diem reports (BZ 33195)
alphabet_groups = ("A-E", "F-K", "L-R", "S-Z")

# File names for files picked up by the receiving system.
# The names are specified in site specific DIG configuration.
release_conf_fmt = 'files/dig_channels/salary/%s'
release_file_names = {
    'ABSENCE': {
        'S2': 'absence_s2',
    },
    'ABSENCE': {
        'S3': 'absence_s3',
    },
    'AMBI': {
        'DK': 'ambi_dk',
        # Not to be used for NO or SE
    },
    'ALLOWNCE_M': {
        'S3': 'allownce_m_s3',
    },
    'ALLOWNCE_D': {
        'S3': 'allownce_d_s3',
    },
    'BUDGETED': {
        'S2': 'budgeted_s2',
    },
    'PERDIEM': {
        'DK': 'perdiem_dk',
        'NO': 'perdiem_no',
        'SE': 'perdiem_se',
        'S2': 'perdiem_s2',
    },
    'PERDIEMTAX': {
        'DK': 'perdiem_dk',
        'NO': 'perdiem_no',
        'SE': 'perdiem_se',
    },
    'OTHER': {
        'S2': 'other_s2',
    },
    'OVERTIME': {
        'DK': 'overtime_dk',
        'NO': 'overtime_no',
        'SE': 'overtime_se',
        'S2': 'overtime_s2',
    },
    'TEMP_CREW': {
        'DK': 'temp_crew_dk',
        'NO': 'temp_crew_no',
        'SE': 'temp_crew_se',
    },
    'SCHEDULE': {
        'S3': 'schedule_s3',
    },
    'TCSCHEDULE': {
        'S3': 'tc_schedule_s3',
    },
    'SCHED_CCSE': {
        'S3': 'schedule_ccse',
    },
    'SUPERVIS': {
        'DK': 'supervis_dk',
        'NO': 'supervis_no',
        'SE': 'supervis_se',
    },
    'COMPDAYS': {
        'DK': 'compdays_dk',
        'NO': 'compdays_no',
        'SE': 'compdays_se',
    },
    'VACATION_R': {
        'DK': 'vacation_r_dk',
    },
    'VACATION_Y': {
        'SE': 'vacation_y_se',
    },
    'VACATIONYC': {
        'NO': 'vacationyc_no',
    },
    'VACATIONYF': {
        'DK': 'vacationyf_dk',
        'NO': 'vacationyf_no',
    },
    'VACATION_P': {
        'DK': 'vacation_p_dk',
        'NO': 'vac_lists_no',
        'SE': 'vac_lists_se',
    },
}
release_dir = 'release_dir'

# Email (Afstemningsunderlag)
balancing_report_sender = 'CMS.salary@localhost'

# Note the '%s' which is replaced with the runid
balancing_report_subject_fmt = 'Balancing report for %s'

# Validity check report
validity_check_report = 'report_sources.hidden.SalaryValidityReport'
validity_check_subtype = 'ValidityCheck'

# Overtime / Per Diem statements (see mmi.py, api.py)
report_prefix_fmt = "%08d"

# Convertible Crew report
convertible_overtime_subtype = 'ConvertibleOvertime'

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
