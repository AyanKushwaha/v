import os, sys, re, time, datetime
import sqlite3

num_unchanged_files=0
num_changed_files=0
num_inspected_files=0
num_new_files=0
num_new_perf_entries=0

print "%s   Defining and compiling regular expressions..." % (datetime.datetime.now())
#
# These regular expressions specify the non-rotating log files (i.e.
# those whose file names uniquely idenify them). Non-rotating log files
# are easier to implement.
# Named groups are used to provide the following info:
#   username, hostname, processtype, subtype
#
PERMANENTFILES = [
    r'(?P<processtype>studio)\.(?P<subtype>Tracking|AlertMonitor|AlertMonitorDayOfOps|DayOfOps)\.(?P<username>[^\.]+)\.[0-9]+\.[0-9]+\.[0-9]+\.(?P<hostname>[^\.]+)'
]
#
# These regular expressions specify the rotating log files. Rotating log files
# are checked more thoroughly for if they contain new data and it is assumed that
# they can be renamed.
# In addition to the above, a named should specify base name (for example if the
# log files are appended with .1, .2, etc, the base name is the full name without the .1)
#
ROTATINGFILES = [
    r'(?P<base>(?P<processtype>alertgenerator)\.AlertGenerator\.(?P<username>[^\.]+)\.(?P<hostname>[^\.]+))\..*',
    r'(?P<base>(?P<processtype>reportworker)\.(?P<subtype>[^\.]+)\.(?P<username>[^\.]+)\.(?P<hostname>[^\.]+))\..*'
]

WEEKDAYS = "Mon|Tue|Wed|Thu|Fri|Sat|Sun"
MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
MONTHSET = [x.lower() for x in MONTHS.split('|')]
TIMESTAMPS = [
    r'Studio Log: started on (?P<weekday>%(WEEKDAYS)s) (?P<month>%(MONTHS)s) (?P<date>[0-9]{1,2}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}) UTC (?P<year>[0-9]{4})' % locals(),
    r'.. (?P<weekday>%(WEEKDAYS)s) (?P<month>%(MONTHS)s) (?P<date>[0-9]{1,2}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}) (?P<year>[0-9]{4}):.*' % locals(),
    r'(?P<weekday>%(WEEKDAYS)s), (?P<date>[0-9]{1,2}) (?P<month>%(MONTHS)s) (?P<year>[0-9]{4}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}) (INFO|DEBUG)' % locals(),
    r'Time: (?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<date>[0-9]{2}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})',
    r'Using system time: (?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<date>[0-9]{2}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})',
    r'(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<date>[0-9]{2}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}),[0-9]+:.*',
]
RULES = {}
def addrule(name, cond, globalprops=False, processtype=None, subtype=None, start_cond=None, func=None):
    global RULES
    assert not name in RULES
    RULES[name] = [ name, globalprops, re.compile(cond), start_cond and re.compile(start_cond), 
                    processtype and re.compile(processtype), subtype and re.compile(subtype), func]

PERMANENTFILES = map(re.compile, PERMANENTFILES)
ROTATINGFILES = map(re.compile, ROTATINGFILES)
TIMESTAMPS = map(re.compile, TIMESTAMPS)

# If this is changed the database needs to be recreated
VALID_PROPERTIES = ["processtype", "subtype", "hostname", "username", "filterregion", "filterstart", "filterend"]
VALID_FLOATVALS = ["timestamp", "cputime", "realtime", "waittime", "memuse", "value1", "value2"]
VALID_STRINGVALS = ["perfprops"]



#
# These are the rules for performance logging
#
addrule('RS_LOADPLAN', r'.*INFO prepare\(\) \.\.\. finished.*', 
        processtype="reportworker", 
        start_cond=r'.* INFO reportserver::about to open subplan: .*')

addrule('plan start', r'DaveFilterTool: Set Filter: period.start = (?P<filterstart>.+)', True,
        processtype="studio")
addrule('plan end', r'DaveFilterTool: Set Filter: period.end = (?P<filterend>.+)', True, 
        processtype="studio")
addrule('plan region', r'DaveFilterTool: Set Filter: crew_user_filter_cct.rankregion1 = \_\|(?P<filterregion>.+)', True, 
        processtype="studio")
#
addrule('AG_LOADPLAN', r'.*INFO Initial setup of alerts.*', 
        processtype="alertgenerator", 
        start_cond=r'.*INFO AlertGenerator::about to open subplan*')
        
addrule('RS_REFRESH', r'.* INFO #(?P<followid>[0-9]+) refresh  took (?P<realtime>[\.0-9]+) secs.', 
        processtype="reportworker", 
        start_cond=r'.* INFO #(?P<followid>[0-9]+) refreshing parent, about to reopen db connection')
        
addrule('LOADPLAN', r'.*End   openPlanPostProc.*', 
        processtype="studio", 
        start_cond=r'.*End   openPlanPreProc.*')
        
addrule('LOADPLAN_STATS', r'    Total: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Open Plan Times \(20..-..-.. ..:..\):')
        
addrule('LOADPLAN_CARMSYS', r'    CARMSYS Loading time: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Open Plan Times \(20..-..-.. ..:..\):')
        
addrule('LOADPLAN_PRELOADTABLES', r'    Preloading tables to model: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Open Plan Times \(20..-..-.. ..:..\):')
        
addrule('LOADPLAN_PRELOADRAVE', r'    Preloading tables to rave: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Open Plan Times \(20..-..-.. ..:..\):')
        
addrule('SAVEPLAN_STATS', r'    Total: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Save Plan Times \(20..-..-.. ..:..\):')
        
addrule('SAVEPLAN_CARMSYS', r'    Actual \(sys\) save: (?P<realtime>[\.0-9]+) s \(cpu: (?P<cputime>[\.0-9]+) s\)', 
        processtype="studio", 
        start_cond=r'  Save Plan Times \(20..-..-.. ..:..\):')




def opendb(dbpath):
    conn = sqlite3.connect(dbpath)
    conn.execute("""create table if not exists logrotation(
    filename text, firsttimestamp real, lasttimestamp real,
    %s
    )""" % ', '.join(("%s text" % x for x in VALID_PROPERTIES)) )
    conn.execute("""create table if not exists performance(
    filename text, perftype text, %s, %s
    )""" % (', '.join(("%s text" % x for x in VALID_STRINGVALS)), ', '.join(("%s real" % x for x in VALID_FLOATVALS))) )
    
    return conn

def getlogfiles(logdir):
    perm = {}
    rotating = {}
    
    for f in os.listdir(logdir):
        for r in PERMANENTFILES+ROTATINGFILES:
            m = r.match(f)
            if m:
                d = m.groupdict()
                if r in PERMANENTFILES:
                    perm[f] = d
                else:
                    if not 'base' in d:
                        d["base"] = f
                    rotating[f] = d
    return perm, rotating
    
def gettimestamp(tsdict):
    cur = time.gmtime()
    def getint(key, default=None):
        ret = str(tsdict.get(key, default))
        if not ret.isdigit():
            return default
        return int(ret)
        
    year = getint('year', cur.tm_year)
    month = str(tsdict.get('month',cur.tm_mon))
    if month.isdigit():
        month = int(month)
    elif month.lower() in MONTHSET:
        month = MONTHSET.index(month.lower()) + 1
    else:
        month = cur.tm_mon
    date = getint('date')
    hour = getint('hour')
    minute = getint('minute')
    second = getint('second',0)
    if date is None or hour is None or minute is None:
        return None
    return time.mktime((year, month, date, hour, minute, second, 0, 0, 0))
    
def checkrule(rulestate, name, cond, start_cond, func, line, curts):
    ret = None
    startcond = False
    endcond = False
    if start_cond is None:
        m = cond.match(line)
        if m:
            ret = m.groupdict()
        if ret is None: return None
    elif not name in rulestate:
        m = start_cond.match(line)
        if m:
            ret = m.groupdict()
        if ret is None: return None
        startcond = True
    else:
        m = cond.match(line)
        if m:
            ret = m.groupdict()
        if ret is None: return None
        if 'followid' in ret:
            ofollowid = rulestate[name].get('followid')
            if ret['followid'] != ofollowid:
                return None
        endcond = True
    
    ret['timestamp'] = curts
    if func:
        ret = func(startcond, rulestate.get(name), ret)
    if startcond:
        rulestate[name] = ret
        return None
    if endcond:
        if not 'realtime' in ret and 'timestamp' in rulestate[name]:
            ret['realtime'] = ret['timestamp'] - rulestate[name]['timestamp']
        del rulestate[name]
    return ret
            
def updatefile(db, path, filenameprops, rotatingbase):
    global num_unchanged_files
    global num_changed_files
    global num_new_files
    global num_new_perf_entries
    global num_inspected_files

    num_inspected_files+=1
    rulestate = {}
    basename = os.path.basename(path)
    startscanat = None
    curts = None
    firstts = None
    lastts = None
    rules = set()
    globalrules = set()
    # Extract the rules that apply to the current file
    for name, globalprops, cond, start_cond, processtype, subtype, func in RULES.values():
        if processtype is None or processtype.match(filenameprops.get('processtype','')):
            if subtype is None or subtype.match(filenameprops.get('subtype','')):
                if globalprops: globalrules.add(name)
                else: rules.add(name)
                
    # If the file was checked in the past and is now older than two days we can skip it.
    two_days_ago=int(time.time())-(2*86400)
    if not rotatingbase and db.execute("select count(*) from logrotation where filename = ? and lasttimestamp < ?", (basename, two_days_ago)).fetchone()[0] > 0:
        return
    else:
        if 'base' in filenameprops:
            basename = filenameprops['base']
        # Only add new entries they take place after the last previously known time stamp, if any.
        for ts, in db.execute("select lasttimestamp from logrotation where filename = ?", (basename,)):
            startscanat = float(ts)
            break

    now = time.time()
    dirty = False
    for line in file(path):
        line = line[:-1]
        for ts in TIMESTAMPS:
            m = ts.match(line)
            if m:
                newts = gettimestamp(m.groupdict())
                if newts > curts and newts < now:
                    curts = newts
                    if firstts is None:
                        firstts = curts
                        if startscanat is None:
                            db.execute('insert into logrotation(filename, firsttimestamp) values(?,?)', (basename, firstts))
                            num_new_files+=1
                            dirty = True
                    lastts = curts
                break
        if not curts: continue # We have no timestamp yet
        if startscanat is not None and startscanat > curts:
            continue
        for rule in rules:
            name, _, cond, start_cond, processtype, subtype, func = RULES[rule]
            r = checkrule(rulestate, name, cond, start_cond, func, line, curts)
            if r:
                dirty = True
                reals = [x for x in VALID_FLOATVALS if x in r]
                strs = [x for x in VALID_STRINGVALS if x in r]
                vs = [basename, name]
                vs.extend([r[x] for x in reals])
                vs.extend([r[x] for x in strs])
                db.execute("insert into performance(filename,perftype,%s) values(?,?,%s)" % (','.join(reals+strs), ','.join(['?' for _ in reals+strs])), tuple(vs))
                num_new_perf_entries+=1

        for rule in globalrules:
            name, _, cond, start_cond, processtype, subtype, func = RULES[rule]
            r = checkrule(rulestate, name, cond, start_cond, func, line, curts)
            if r:
                dirty = True
                props = [x for x in VALID_PROPERTIES if x in r]
                vs = [r[x] for x in props]
                vs.append(basename)
                db.execute("update logrotation set %s where filename = ?" % ','.join(["%s = ?" % x for x in props]), tuple(vs))
                
    
    if dirty:
        num_changed_files+=1
        db.execute('update logrotation set lasttimestamp = ? where filename = ?', (lastts, basename))
        db.commit()
    else:
        num_unchanged_files+=1


def run():
    try:
        carmtmp  = os.environ.get("CARMTMP",  os.path.dirname(__file__))
    	carmdata = os.environ.get("CARMDATA", os.path.dirname(__file__))
    	logdir = os.path.abspath(os.path.join(carmtmp, "logfiles"))
    	dbpath = os.path.abspath(os.path.join(carmdata, "performance.db"))

    	print "%s   Acquiring list of logfiles..." % (datetime.datetime.now())
    	perm, rotating = getlogfiles(logdir)

    	print "%s   Opening database file..." % (datetime.datetime.now())
    	db = opendb(dbpath)

    	print "%s   Processing non-rotating files..." % (datetime.datetime.now())
    	for f,d in perm.items():
        	updatefile(db, os.path.join(logdir, f), d, None)

    	print "%s   Processing rotating files..." % (datetime.datetime.now())
    	for f,d in rotating.items():
        	updatefile(db, os.path.join(logdir, f), d, True)

	print "%s   Inspected files: %i"  % (datetime.datetime.now(), num_inspected_files)
    	print "%s   Files with new performance events since last update: %i"  % (datetime.datetime.now(), num_changed_files)
    	print "%s   Files with new timestamps since last update: %i" % (datetime.datetime.now(), num_unchanged_files)
    	print "%s   New files: %i"  % (datetime.datetime.now(), num_new_files)
    	print "%s   New entries in performance table: %i"  % (datetime.datetime.now(), num_new_perf_entries)
    except Exception, message:
        print message
        exit(1)
    except KeyboardInterrupt, message:
        print "Program interrupted!"
        exit(1)
if __name__ == '__main__':
    run()
