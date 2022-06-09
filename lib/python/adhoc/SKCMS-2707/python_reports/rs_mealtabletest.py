"""
Move this python file to lib/python/report_sources/report_server/ directory before executing it 
Also make sure that the file lib/python/report_sources/hidden/MealTabletest.py is available in the carmusr
To run this in report worker use the below command
digjobs submit --channel=crewnotifications --name=job_mealtabletest --report=report_sources.report_server.rs_mealtabletest --delta=1 --deadline_offset="02:00" --creationtime_offset="24:00"
"""

from report_sources.report_server.rs_if import add_reportprefix, argfix
from report_sources.hidden.MealTabletest import MealTabletest
from RelTime import RelTime

@argfix
@add_reportprefix
def generate(*a, **k):

    if k.has_key('creationtime_offset'):
        try:
            creationtime_offset = RelTime(k['creationtime_offset'])
            creationtime_offset = str(creationtime_offset)
        except:
            creationtime_offset ="24:00"
    else :
        creationtime_offset ="24:00"

    if k.has_key('deadline_offset'):
        try:
            deadline_offset = RelTime(k['deadline_offset'])
            deadline_offset = str(deadline_offset)
        except:
            deadline_offset = "02:00"
    else:
        deadline_offset = "02:00"
    
    c = MealTabletest(creationtime_offset,deadline_offset)
    crew_meal_test_messages = c.make_reports()
    
