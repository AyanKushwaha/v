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
log = logging.getLogger('salary.ec.ec_perdiem_statement_mailer.Conf')
log.setLevel(logging.DEBUG)


# These constants are safe to alter. -------------------------------------{{{1

# DIG channels for manual jobs
emailchannel = 'ec_crewmailer'

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
ecRunTypePackage = "salary.ec.ec_perdiem_statement_mailer"

# For dynamic loading of report type modules
rptPackage = "salary.rpt"

# These constants would need some programming effort to change. ---------{{{1

# Which context should be used
context = 'sp_crew'

# Run types, don't change order, the first should be about Per Diem, the second overtime

allowedRunTypes = ('PERDIEM', 'PERDIEMTAX')
runTypeDescription = {
    'PERDIEM': 'Per Diem', 
    'PERDIEMTAX': 'Per Diem Tax'
}

# These systems are allowed
allowedSalarySystems = ('DK', 'NO', 'SE', 'S3')

# These are the currencies to be used (SAP, PERDIEM)
currencies = {
    'DK': 'DKK',
    'NO': 'NOK',
    'SE': 'SEK',
    'S3': 'SEK',
}

# These are the bases for each country/salary system.
bases = {
    'DK': ['CPH'],
    'NO': ['OSL', 'SVG', 'TRD'],
    'SE': ['STO'],
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
    'PERDIEM': {
        'DK': 'perdiem_dk',
        'NO': 'perdiem_no',
        'SE': 'perdiem_se',
    },
    'PERDIEMTAX': {
        'DK': 'perdiem_dk',
        'NO': 'perdiem_no',
        'SE': 'perdiem_se',
    }
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
