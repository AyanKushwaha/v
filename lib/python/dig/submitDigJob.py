#!/bin/env python
#
"""
Helper utility to post arbitrary jobs to any channel.
Note that there is also a more convenient command line wrapper available in 
[CARMUSR]/bin/submitDigJob.sh

Mandatory Parameters:
    -c <conn>                   Database connection string
    -s <schema>                 Database schema name
    --job <channel>             Dig channel to read job
    --name <submitter>          Job submitter

Optional Parameters:
    -x <YYYY-mm-ddTHH:MM>       Job execution time (default 'now')
    --report <script>           Report server script (if job is redirected
                                to a report server)
    --server <RS alias>         Report server alias name specified in dig
                                configuration
    --delta [0|1]               Should report server return DB delta
    --reload [0|1]              Should report server refresh first
    --<paramname> <paramvalue>  Any job parameter
"""

import sys
import time
from dig.DigJobQueue import DigJobQueue
from AbsTime import AbsTime
from utils import TimeServerUtils
from carmensystems.dig.framework.carmentime import toCarmenTime

params = {}
delta='0'
conn=schema=report=starttime=channel=submitter=None
for i in range(1,len(sys.argv)-1,2):
    if sys.argv[i] == '-c':
        conn = sys.argv[i+1]
    elif sys.argv[i] == '-s':
        schema = sys.argv[i+1]
    elif sys.argv[i] == '-x':
        ts = sys.argv[i+1]
        starttime = AbsTime(*time.strptime(ts,"%Y-%m-%dT%H:%M")[0:5])
    elif sys.argv[i] == '--delta':
        delta = sys.argv[i+1]
    elif sys.argv[i] == '--report':
        report = sys.argv[i+1]
    elif sys.argv[i] == '--job':
        channel = sys.argv[i+1]
    elif sys.argv[i] == '--name':
        submitter = sys.argv[i+1]
    else:
        params[sys.argv[i].lstrip('-')] = sys.argv[i+1]
if starttime is None:
    timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
    starttime = AbsTime(toCarmenTime(timeserver.getTime()))
djq = DigJobQueue(channel, submitter, report, delta, conn, schema, False)
id = djq.submitJob(params, 0, starttime)
print "Submitted job with id=%s" % (id)
