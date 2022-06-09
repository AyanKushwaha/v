import sys, os
from carmensystems.dig.framework.dave import DaveSearch, DaveMultiSearch, DaveConnector, DaveStorer
from AbsTime import AbsTime
from time import strftime, time, localtime

__C = None
def _C():
    from utils import ServiceConfig
    global __C
    if __C == None: __C = ServiceConfig.ServiceConfig()
    return __C

_dc = None
def _dbsearch(entity, expr=[], entity2=None, expr2=[], withDeleted=False):
    global _dc
    if not _dc: _dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    if isinstance(expr, str):
        expr = [expr]
    if isinstance(expr2, str):
        expr = [expr2]
    if entity2:
        return dict(_dc.runSearch(DaveMultiSearch([DaveSearch(entity, expr, withDeleted), DaveSearch(entity2, expr2, withDeleted)])))
    else:
        return list(_dc.runSearch(DaveSearch(entity, expr, withDeleted)))

def _ptbl(tbl):
    data = [
      (str(r['id']), r['status'], r['channel'], r['start_at'], r['started_at'], r['ended_at'])
      for r in tbl
    ]
    if not len(data):
        print >>sys.stderr, "There are no jobs"
        return
    ms = [max([max(8,len(y[x] or ''))] for y in data)[0] for x in range(len(data[0]))]
    print ms
    
    fmt = ("%%-%ds "*len(ms)) % tuple(ms)
    print fmt % ("ID", "Status", "Channel", "Starts", "Started", "Ended")
    print '-'*(sum(ms)+len(ms))
    for t in data:
        print fmt % t

def _list_(channel=None):
    """ Shows  pending dig jobs
        @param channel - if specified, only jobs for certain channel will be shown
    """
    match = False
    if channel:
        flt = " AND channel = '%s'" % channel
    else:
        flt = ""
    _ptbl(_dbsearch("job","ended_at = 'not_ended'"+flt))

def completed(channel=None,days=1):
    """ Shows completed jobs.

        Example:
        digjobs completed --days=2

        @param channel - if specified only jobs for a certain channel is shown 
        @param days - number of days back that will be searced. Default = 1
        
    """
    match = False
    if channel:
        flt = " AND channel = '%s'" % channel
    else:
        flt = ""
    tim = strftime('%Y-%02m-%02dT%02H:%02M:%02S', localtime(time()-24*3600*int(days)))
    _ptbl(_dbsearch("job","ended_at != 'not_ended' AND ended_at >= '%s'" % tim + flt))
    

def failed(channel=None,days=1):
    """ Shows failed jobs.

        Example:
        digjobs failed --days=2

        @param channel - if specified only jobs for a certain channel is shown 
        @param days - number of days back that will be searced. Default = 1
        
    """
    match = False
    if channel:
        flt = " AND channel = '%s'" % channel
    else:
        flt = ""
    tim = strftime('%Y-%02m-%02dT%02H:%02M:%02S', localtime(time()-24*3600*int(days)))
    _ptbl(_dbsearch("job","ended_at != 'not_ended' AND ended_at >= '%s' AND status != 'ok'" % tim + flt))


def schedule(channel=None):
    """ Displays the DIG schedule 

        @param channel - displays the schedule for a certain channel when set 

    """
    tasks = _C().getProperties("schedule/task@*")
    def sched(task):
        params = {}
        for taskline,v in tasks:
            p = taskline.split('@')[-1]
            t = taskline.split('@')[-2].split('/')[-1]
            if task == t:
                if p in ("hours","minutes","pattern","days","weekdays","months","years"):
                    params[p] = v
        return ', '.join(['%s=%s' % x for x in params.items()])
    def job(task):
        for taskline,v in tasks:
            p = taskline.split('@')[-1]
            t = taskline.split('@')[-2].split('/')[-1]
            if task == t and p == 'job':
                return v
        return ""
    data = [
      (t.split('/')[-1],sched(t.split('/')[-1]))
      for t,v in _C().getProperties("dig/schedule/task")
      if not channel or job(t.split('/')[-1]) == channel
    ]
    if not len(data):
        print >>sys.stderr, "There are no tasks"
        return
    ms = [max([max(8,len(y[x] or ''))] for y in data)[0] for x in range(len(data[0]))]
    
    fmt = "%-"+str(ms[0])+"s%s"
    print fmt % ("Task","Schedule")
    print '-' * (sum(ms)+2)
    print '\n'.join([fmt % x for x in data])
    
def next(name=None, channel=None, time=None, lasttime=None):
    """ Shows the next time when a DIG scheduled task is to run
    
        @param name - task name 
        @param channel - dig channel
        @param time - start time, if not specified timeserver is used and system time as backup
        @param lasttime - end time, if not specified all jobs after time is shown
    """
    from carmensystems.dig.framework.carmentime import toCarmenTime,fromCarmenTime
    
    tasks = _C().getProperties("schedule/task@*")
    
    if time is None:
        from utils import TimeServerUtils
        from AbsTime import AbsTime
        timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
        time = timeserver.getTime()
    else:
        time = fromCarmenTime(AbsTime(time))
    if lasttime:
        lasttime = int(AbsTime(lasttime))
        
    def job(task):
        for taskline,v in tasks:
            p = taskline.split('@')[-1]
            t = taskline.split('@')[-2].split('/')[-1]
            if task == t and p == 'job':
                return v
        return ""
    def nextdate(task):
        params = {}
        for taskline,v in tasks:
            p = taskline.split('@')[-1]
            t = taskline.split('@')[-2].split('/')[-1]
            if task == t:
                if p in ("hours","minutes","pattern","days","weekdays","months","years","job","name"):
                    params[p] = v
                    
        from carmensystems.dig.scheduler.task import Task
        t = Task(**params)
        return t.cron.nextTriggerTime(time)
    data = [
      (t.split('/')[-1],
       str(AbsTime(toCarmenTime(nextdate(t.split('/')[-1])))),
       job(t.split('/')[-1]))
      for t,v in _C().getProperties("dig/schedule/task")
      if (not channel or job(t.split('/')[-1]) == channel)
      and (not name or name == t.split('/'))
    ]
    if lasttime:
        data = [x for x in data if int(AbsTime(x[1])) <= lasttime]
    data.sort(key=lambda x:int(AbsTime(x[1])))
    if not len(data):
        print >>sys.stderr, "There are no tasks"
        return
    ms = [max([max(8,len(y[x] or ''))] for y in data)[0] for x in range(len(data[0]))]
    
    fmt = "%-"+str(ms[0]+3)+"s%-"+str(4+ms[1])+"s%s"
    print fmt % ("Task","Next run date","Channel")
    print '-' * (sum(ms)+10)
    print '\n'.join([fmt % x for x in data])

def detail(job):
    """ Gets the details for a job i.e. the paramters  

        Example:
        digjobs detail 123345 

        @param job - Job id
        
    """    
    
    job_params = _dbsearch("job_parameter","job=%s" % (job))
    
    for r in job_params:
        print str(r['paramname']), str(r['paramvalue'])
        
    
    
def submit(task=None,channel=None,report=None,name=None,starttime=None,**params):
    """ Submits a job to DIG.  

        Example:
        digjobs submit job_SubqViolationTask 
        digjobs submit --channel=subq_violation --name=job_SubqViolationTask --report="report_sources.report_server.rs_subq_violation" --rerun=True

        @param task - When specified, the job parameters will be extracted from the schedule
        @param channel - dig channel
        @param report - report
        @param name - task name
        @param startime - starttime, the time server if not specified 
        @param params - any additional parameter 
        
    """    
    
    if task:
        if channel or report or name or len(params):
            print >>sys.stderr, "Either specify task, or specify job parameters"
            sys.exit(1)
        for p,v in _C().getProperties("schedule/%s@*" % task):
            p = p.split('@')[-1]
            if p == "job":
                channel = v
            elif p == "name":
                name = v
            elif p == "report":
                report = v
            elif not p in ("hours","minutes","pattern","days","weekdays","months","years"):
                params[p] = v
    
    if not channel:
        print >>sys.stderr, "Channel must be specified"
        sys.exit(1)
    if not name:
        print >>sys.stderr, "Name must be specified"
        sys.exit(1)
    if not report:
        print >>sys.stderr, "Report must be specified"
        sys.exit(1)
    if starttime is None:
        from utils import TimeServerUtils
        from AbsTime import AbsTime
        from carmensystems.dig.framework.carmentime import toCarmenTime
        timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
        starttime = AbsTime(toCarmenTime(timeserver.getTime()))
    else:
        from AbsTime import AbsTime
        starttime = AbsTime(starttime)
    from dig.DigJobQueue import DigJobQueue
    djq = DigJobQueue(channel, name, report, params.get('delta','1'), os.environ["DB_URL"], os.environ["DB_SCHEMA"], False)
    id = djq.submitJob(params, 0, starttime)
    print "Job ID: %s" % (id)
    