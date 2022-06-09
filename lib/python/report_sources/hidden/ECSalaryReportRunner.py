
import sys
import os
import report_sources.hidden.ECSalaryReport as SEC
import salary.ECSupervis as ECS
import salary.ECPerDiem as ECP
import salary.ECOvertime as ECO

# path: lib/python/report_sources/hidden/ECSalaryReportRunner.py

def reload_all():
    reload(SEC)
    reload(ECP)
    reload(ECS)
    reload(ECO)

def run():
    reload_all()
    ecrun = SEC.ECReport(salary_system='all', release=True, test=True)
    ecrun.generate()
    print "END OF RUN"
    if os.getenv('RUN_AND_EXIT', default='FALSE').lower() == 'true':
        import sys
        sys.exit(0)


if __name__ == '__main__':
    print "RUNNING ON MAIN"
    run()
else:
    print "RUNNING"
    run()
