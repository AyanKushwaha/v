#!/bin/env python
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/services_stats.py,v 1.4 2009/10/07 15:48:10 ade409 Exp $
#########################################
# Copyright Jeppesen Systems AB

"""
Script for analyzing SAS DIG channel 'services' log file.
The channel must have Debug log level.

Options:
    -o file Output file (default stdout)
    -h      Print headers
    -r      Print all requests
    -a      Print average response times per request type and time period
    -t      Print total average response times per request type
    -d      Print duplicate requests
    -e      Print duplicate request summary
    -i      Exclude cached responses when calculating average response times
    --duplicateDelta <secs>     If identical request received within this
                                time, it is considered duplicate.
    --duplicateThreshold <n>    With -d only print duplicates if they exceed
                                this number.
    --averagePeriodKey <format> Time format string used as key for periods used
                                in average calculation (default "%Y%m%d/%H")

Example: carmpython services_stats.py -death $CARMTMP/logfiles/DIG/services.log
"""
__author__ = "kenneth.altsjo@jeppesen.com"

import os, sys, getopt
import re
import datetime
from carmensystems.dig.support.queryparser import QueryParser

regex_request = re.compile(r'^\[D (.*) ReportCacheDispat.*Using(.*)ReportRequestHandler for request: (.*)$')
regex_reply = re.compile(r'^\[D (.*) ReportCacheDispat.*Received (.*) the report server.*rs_(\w+)\', \[\[(.*)\], (.*)\]$')
regex_restart = re.compile(r'^\[S 2')

def makeRqStr(params):
    if params.startswith('['):
        return params.strip("[]")
    plist = params.strip("{}").replace(',',':').split('\':')
    exclude = False
    rqstr = ""
    for p in plist:
        exclude = not exclude
        if not exclude:
            rqstr += p.strip('\' ')
            rqstr += ','
    rqstr = rqstr.rstrip(',')
    return rqstr

def runningAvg(newItem, nItems, oldAvg=None):
    if oldAvg:
        return oldAvg - (oldAvg - newItem)/nItems
    else:
        return newItem

class Request:
    def __init__(self,requestTime,rqstr):
        self.requestTime = requestTime
        self.requestStr = rqstr
        self.replyTime = None
        self.cache = False
        self.status = 'W'

    def getType(self):
        return self.requestStr.split(',')[0]


def main(argv):
    ##################
    # Initialize
    ##################
    try:
        opts, args = getopt.getopt(argv[1:], "hiratdeo:",["duplicateDelta=","duplicateThreshold=","averagePeriodKey="])
    except getopt.GetoptError, e:
        print e
        return

    # Per unique request string - a list of the individual requests
    requestMap= {}
    # All requests in chronological order
    requestList = []

    out = sys.stdout
    queryConf = os.path.join(os.path.expandvars("$CARMUSR"),"data/config/dig/queries/reports.services")
    psep = ','
    printAllRequests = False
    printAveragesPerPeriod = False
    printTotals = False
    printDuplicates = False
    printDuplicatesSummary = False
    duplicateDelta = datetime.timedelta(seconds=40) # deemed duplicate if identical request follows within this time
    duplicateThreshold = 2
    avgPeriodKeyFormat = "%Y%m%d/%H"
    disregardCache = False # exclude cached requests from response time avg
    printHeaders = True
    for opt, val in opts:
        if opt == '-o':
            out = open(val,"w")
        elif opt == '-r':
            printAllRequests = True
        elif opt == '-a':
            printAveragesPerPeriod = True
        elif opt == '-t':
            printTotals = True
        elif opt == '-d':
            printDuplicates = True
        elif opt == '-e':
            printDuplicatesSummary = True
        elif opt == '-i':
            disregardCache = True
        elif opt == '-h':
            printHeaders = True
        elif opt == '--duplicateDelta':
            duplicateDelta = datetime.timedelta(seconds=int(val))
        elif opt == '--duplicateThreshold':
            duplicateThreshold = int(val)
        elif opt == '--averagePeriodKey':
            avgPeriodKeyFormat = val
    logPath = args[0]


    ##################
    # Parse
    ##################
    logfile = open(logPath, 'r')
    for line in logfile.readlines():
        m = regex_request.match(line)
        if m:
            (ts, handler, rqstr) = m.groups()
            plist = rqstr.split(psep)
            request = plist[0]
            tl = ts.replace('-','.').replace(' ','.').replace(':','.').split('.')
            dt = datetime.datetime(*[int(x) for x in tl])
            cache = [True,False]['non-caching' in handler]
            qpParam = {'config':queryConf, 'param_separator':psep}
            qp = QueryParser(qpParam)
            qp.readConfig()
            rq = qp.queries[request]
            raveDict,pList,pDict = rq._generateParameters(plist)
            pDict.pop('delta',None)
            pDict.pop('reload',None)
            key = pDict
            if len(pDict) == 0:
                key = pList[1:]
            r = Request(dt,rqstr)
            l = requestMap.setdefault(str(key), [])
            l.append(r)
            requestList.append(r)
            continue
        m = regex_reply.match(line)
        if m:
            (ts, handler, request, lparams, dparams) = m.groups()
            lparams = lparams[lparams.find("'",1)+1:].lstrip(", ")
            params = dparams
            if lparams != '':
                if params != '{}':
                    print >>sys.stderr, "ERROR Cannot handle both lparam and dparam"
                    continue
                params = "[%s]" % lparams
            tl = ts.replace('-','.').replace(' ','.').replace(':','.').split('.')
            dt = datetime.datetime(*[int(x) for x in tl])
            cache = [False,True]['from the cache' in handler]
            l = requestMap.get(params)
            if l is None:
                print >>sys.stderr, "No-requ %s %s,%s" % (dt, request, makeRqStr(params))
                continue
            for r in l:
                if r.status == 'W':
                    r.replyTime = dt
                    r.cache = cache
                    r.status = 'R'
                    break
            continue
        if regex_restart.match(line):
            # If channel restarts, cancel any outstanding requests
            for r in requestList:
                if r.status == 'W':
                    r.status = 'C'


    ##################
    # Analyze
    ##################
    if printHeaders:
        print >>out, "** Requests %s - %s" % (requestList[0].requestTime, requestList[-1].requestTime)
    if printHeaders and printAllRequests:
        print >>out, "****************************************************"
        print >>out, "**                All requests"
        print >>out, "** (type, req time, resp time, Cached/Non Cached)"
        print >>out, "****************************************************"
    nPeriod = {}
    avgPeriod = {}
    for r in requestList:
        if r.status == 'W':
            print >>sys.stderr, "No-repl %s %s" % (r.requestTime, r.requestStr)
        elif r.status == 'C':
            print >>sys.stderr, "Aborted %s %s" % (r.requestTime, r.requestStr)
        else:
            responseTime = r.replyTime-r.requestTime
            periodKey = r.requestTime.strftime(avgPeriodKeyFormat)
            if printAllRequests:
                cacheStr = ['NC','C'][r.cache]
                print >>out, "%s\t%s %s (%s)" % (r.getType()[:14], r.requestTime, responseTime, cacheStr)
            rqtyp = r.getType()
            # Update average statistics
            if r.cache and disregardCache:
                continue
            nPeriod.setdefault(rqtyp, {})
            n = nPeriod[rqtyp][periodKey] = nPeriod[rqtyp].setdefault(periodKey, 0) + 1
            avgPeriod.setdefault(rqtyp, {})
            avgPeriod[rqtyp][periodKey] = runningAvg(responseTime, n, avgPeriod[rqtyp].setdefault(periodKey, None))

    ##################
    # Print statistics
    ##################
    if printHeaders and (printAveragesPerPeriod or printTotals):
        print >>out, "**"
        print >>out, "****************************************************"
        if printAveragesPerPeriod:
            print >>out, "** Average response times per request type and period"
            print >>out, "** (type, period, avg, num req)"
        elif printTotals:
            print >>out, "** Average response times per request type"
            print >>out, "** (type, avg, num req)"
        print >>out, "****************************************************"
    ltyp = avgPeriod.keys()
    ltyp.sort()
    for rqtyp in ltyp:
        tw = datetime.timedelta(0)
        tn = 0
        lper = avgPeriod[rqtyp].keys()
        lper.sort()
        for periodKey in lper:
            avg = avgPeriod[rqtyp][periodKey]
            nRq = nPeriod[rqtyp][periodKey]
            if printAveragesPerPeriod:
                print >>out, "%s\t%s:\t %s (%s)" % (rqtyp[:14], periodKey, avg, nRq)
            tw += avg*nRq
            tn += nRq
        if printTotals:
            print >>out, "%s\tTOTAL_AVG\t %s (%s)" % (rqtyp[:14], tw/tn, tn)

    ##################
    # Track duplicates
    ##################
    ndup = {} # number of duplicates per request type
    ntot = {}
    if printHeaders and printDuplicates:
        print >>out, "**"
        print >>out, "****************************************************"
        print >>out, "**          Requests with duplicates"
        print >>out, "** (request, time first req, num dupl within %d secs)" % (duplicateDelta.seconds)
        print >>out, "****************************************************"
    keys = requestMap.keys()
    keys.sort()
    for rqKey in keys:
        l = requestMap[rqKey]
        t0 = datetime.datetime(1986,1,1)
        ndr = 0
        for r in l:
            if r.status in ['W','C']:
                continue  # exclude unfinished requests
            rt = r.getType()
            ndup.setdefault(rt, 0)
            ntot[rt] = ntot.get(rt, 0) + 1
            isDupl = False
            if r.requestTime-t0 < duplicateDelta:
                isDupl = True
                ndup[rt] += 1
                ndr += 1
            if not isDupl or r==l[-1]:
                if ndr+1 >= duplicateThreshold and printDuplicates:
                    print >>out, "%s %s (%d)" % (r.requestStr, t0, ndr+1)
                ndr = 0
                t0 = r.requestTime
    if printDuplicatesSummary:
        if printHeaders:
            print >>out, "**"
            print >>out, "****************************************************"
            print >>out, "**      Summary duplicates per request type"
            print >>out, "** (type, num duplicates, num total)"
            print >>out, "****************************************************"
        for rqtyp in ltyp:
            print >>out, "%s\t %d\t (%d)" % (rqtyp[:14], ndup[rqtyp], ntot[rqtyp])


if __name__ == "__main__":
    main(sys.argv)
