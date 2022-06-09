"""
Creates CrewNotifications Messages that is sent to SEIP and is used by IPAD applications by the crew
"""

from report_sources.report_server.rs_if import add_reportprefix, argfix
from report_sources.hidden.CrewNotifications import CrewNotifactions
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

    c=CrewNotifactions(creationtime_offset,deadline_offset)
    crew_notification_messages = c.make_reports()
    reports = []
    for report in crew_notification_messages:
        reports.append({'content':report,
                        'content-type': 'application/xml',
                        'destination':[('default', {})],
                        })

    return reports, True
