from __future__ import print_function

import sys
import os
import salary.ec.ECSalaryReport as SEC
import salary.ec.ECSupervis as ECS
import salary.ec.ECPerDiem as ECP
import salary.ec.ECOvertime as ECO
from datetime import datetime
from dateutil.relativedelta import relativedelta

# path: lib/python/report_sources/hidden/ECSalaryReportRunner.py

def reload_all():
    reload(SEC)
    reload(ECP)
    reload(ECS)
    reload(ECO)

def run():
    release = os.getenv("RELEASE_RUN", default='FALSE').lower() == 'true'
    test = os.getenv("TEST_RUN", default='TRUE').lower() == 'true'
    if test:
        reload_all()
    report_start_date = os.getenv("PERIOD_START", default=None)
    report_end_date = os.getenv("PERIOD_END", default=None)
    run_ec_and_exit = os.getenv("RUN_EC_AND_EXIT", default=None)
    
    print("release is: " + str(release))
    print("test is: " + str(test))
    print("report_start_date is: " + str(report_start_date))
    print("report_end_date is: " + str(report_end_date))
    if run_ec_and_exit: # check if it is running with ec_report.sh 
        ecrun = SEC.ECReport(salary_system='all', report_start_date=datetime.strptime(report_start_date,"%d%b%Y") + relativedelta(months=1), report_end_date=report_end_date, release=release, test=test)
    else:
        ecrun = SEC.ECReport(salary_system='all', release=release, test=test)
    csv_files = ecrun.generate()
    for csv in csv_files:
        print(csv)
    print ("END OF RUN")
    if os.getenv('RUN_EC_AND_EXIT', default='FALSE').lower() == 'true':
        import sys
        sys.exit(0)


if __name__ == '__main__':
    print("RUNNING ON MAIN")
    run()
else:
    print("RUNNING")
    run()
