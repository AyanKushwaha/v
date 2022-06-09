#!/usr/bin/env python

import sys, os
from carmensystems.dig.framework.dave import DaveConnector
from AbsTime import AbsTime
import fixrunner
import utils.dt as dt


def sql(query):
    schema =os.environ['DB_SCHEMA']
    url =os.environ['DB_URL']
    dc = DaveConnector(url, schema)
    try:
        conn = dc.getL1Connection()
        #print dc.getConnectionInfo()
        conn.rquery(query, None)
        rv = []
        while True:
            a = conn.readRow()
            if a == None: break
            rv.append(a.valuesAsList())
        conn.endQuery()
        return rv
    finally:
        dc.close()
# Return the 15th in the month before our date
def getLimitTime(startDate, useMinutes=True):
    return dt.dt2m(dt.m2dt(startDate.month_floor().addmonths(-1).adddays(15)))

def sqlTest(ppstart, ppend, crew):
    publishdate = ppstart.month_floor().addmonths(-1).adddays(15)    
    crewSql =""
    if crew != 0:
        crewSql = " and e.crew =%s" % crew
    
    # First use the F36 activites created in prestudio, saved in crew_activity table
    query ="""select DISTINCT id, a.crew, e.reasoncode, 
    to_char(to_date('01-jan-1986', 'DD-MON-YYYY HH:MI') + a.st/1440 , 'DDMONYYYY HH24:MI') st_utc,
   to_char(to_date('01-jan-1986', 'DD-MON-YYYY HH:MI') + a.et/1440 , 'DDMONYYYY HH24:MI') et_utc,
   to_char(to_date('01-jan-1986', 'DD-MON-YYYY HH:MI') + d.committs/86400 , 'DDMONYYYY HH24:MI') commited
 from account_entry e 
join crew_activity a on a.crew = e.crew and a.activity = e.account 
join dave_revision d on a.revid = d.revid
where e.account='F36' and e.deleted = 'N' and e.next_revid = 0 and a.deleted = 'Y' 
and e.source = 'F36 on Roster' and a.next_revid = 0
and to_date('01jan1986', 'DDMONYYYY')+a.et/1440 > to_date('%s','DDMONYYYY HH24:MI')\
and to_date('01jan1986', 'DDMONYYYY')+a.st/1440 < to_date('%s','DDMONYYYY HH24:MI')\
and to_date('01jan1986','DDMONYYYY')+d.committs/86400<to_date('%s','DDMONYYYY HH24:MI')
and (tim-st = 120 or tim-st = 60) %s
order by a.crew,st_utc,commited""" % (ppstart, ppend, publishdate, crewSql)
    #print "db sql \" %s \"" % query
    result1 = sql(query)
    
    # Use the ground_activity approach, F36 created in file plan in planning studio and then fetched to database
    query = """select DISTINCT e.id, c.crew, task_id,
to_char(to_date('01jan1986', 'DDMONYYYY HH:MI') + d.committs/86400 , 'DDMONYYYY HH24:MI') committs,
to_char(to_date('01jan1986', 'DDMONYYYY HH:MI') + g.st/1440 , 'DDMONYYYY HH24:MI') st_utc, 
to_char(to_date('01jan1986', 'DDMONYYYY HH:MI') + g.et/1440 , 'DDMONYYYY HH24:MI') et_utc,
to_char(to_date('01jan1986', 'DDMONYYYY HH:MI') + e.tim/1440 , 'DDMONYYYY HH24:MI') tim_utc,
g.adep, g.ades, e.revid from crew_ground_duty c 
left join ground_task g on task_id = g.id 
join dave_revision d on c.revid = d.revid
join account_entry e on account = activity and e.crew = c.crew and e.deleted = 'N' and e.next_revid = 0
where activity = 'F36' and c.next_revid = 0 and c.deleted = 'Y' and source = 'F36 on Roster'
and to_date('01jan1986', 'DDMONYYYY')+g.et/1440 > to_date('%s','DDMONYYYY HH24:MI')\
and to_date('01jan1986', 'DDMONYYYY')+g.st/1440 < to_date('%s','DDMONYYYY HH24:MI')\
and to_date('01jan1986','DDMONYYYY')+d.committs/86400<to_date('%s','DDMONYYYY HH24:MI')
and (tim-g.st = 120 or tim-g.st = 60) %s
order by c.crew, st_utc, et_utc""" % (ppstart, ppend, publishdate, crewSql)
    #print "Found %d rows\n" % len(result)
    result2 = sql(query)

    return result1+result2
__version__ = '1'


@fixrunner.run
def fixit(dc, ppstart, ppend, crew, dryrun, *a, **k):
    
    ops = []
    accounts = sqlTest(ppstart, ppend, crew)
    print "\n"
    for account in accounts:
        for entry in fixrunner.dbsearch(dc, 'account_entry', " id='%s'" % account[0]):
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (entry['id'], entry['crew'], entry['account'], entry['reasoncode'], entry['revid'], 
                                                  AbsTime(int(entry['tim'])), AbsTime(int(entry['entrytime'])),
                                                  account[5])
            ops.append(fixrunner.createOp('account_entry', 'D', entry))

    records =len(ops)
    if records > 0:
        print "\n"
        print "Found %s records" % records
        if dryrun:     # We should not save anything
            print "Exiting without deleting any records in database"
            return []
        print "Will now delete them..."
    else:
        print "No invalid entries found"
    
    
    return ops

fixit.remark = 'SASCMS-6019 (%s)' % __version__


if __name__ == "__main__":
    argc = 1
    ppstart = AbsTime("01Mar2013")
    if len(sys.argv) > argc:
        ppstart = AbsTime(sys.argv[argc])
    
    argc = 2
    ppend = ppstart.addmonths(1)
    no_commit = True
    if len(sys.argv) > argc:
        no_commit =sys.argv[argc].lower() != "commit"

    argc = 3
    crew = 0
    if len(sys.argv) > argc:
        crew = int(sys.argv[argc])
    fixit(ppstart,ppend, crew, no_commit)

