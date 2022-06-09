from xmlrpclib import ServerProxy
from carmensystems.dig.framework.dave import DaveSearch, DaveMultiSearch, DaveConnector, DaveStorer
from utils import ServiceConfig
import os, sys
__C = None
def _C():
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

def submit(task=None,channel=None,report=None,name=None,starttime=None,**params):
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

def runtypes():
	"""Displays a list of available run types
	"""
	import re
	for f in os.listdir(os.path.expandvars("$CARMUSR/lib/python/salary/type")):
		if f[-3:] == '.py' and f != '__init__.py':
			sal_systems = []
			sal_file = open(os.path.expandvars("$CARMUSR/lib/python/salary/type/%s"%f), 'r')
			for line in sal_file:
				result = re.search(r'class\s(DK|SE|NO)\(.*?', line)
				if result:
					sal_systems.append(result.group(1))
			sal_file.close()
			
			print f[:-3], '(%s)' % ','.join(sal_systems)

def compconv(conversion, lastdate=None, accountdate=None, nocommit=False, debug=False):
	"""Starts a new compensation days run. Parameters are:
  conversion - One of F3S, F31, F33GAIN, F7SGAIN, RESET
  [lastdate] - End of period. Default depends on conversion.
  [accountdate] - The account date, default is now.
  [nocommit] - If set to True, does not write to the database. Default is False.
	"""
	flags = ''
	iflags = ''
	if nocommit: iflags += ' --nocommit'
	if debug: iflags += ' -d'
	if lastdate: flags += ' --lastdate="%s"' % lastdate
	if accountdate: flags += ' --accountdate="%s"' % accountdate
	cmd = os.path.expandvars('$CARMSYS/bin/mirador -s salary.batch %s --connect "$DB_URL" --schema "$DB_SCHEMA" compdays %s %s') % (iflags, conversion, flags)
	print cmd
	os.system(cmd)
			
def resetaccount(accounts, lastdate=None, region=None, maincat=None, base=None, accountdate=None, reason=None, nocommit=False, debug=False):
	"""Resets crew account(s):
  accounts - Comma-separated list of accounts
  [lastdate] - End of period. Default is start of current month.
  [region] - Comma-separated list of regions, e.g. SKN,SKS,SKD. Default is all regions.
  [maincat] - F or C. Default is both.
  [base] - Comma-separated list of bases, e.g. OSL,CPH. Default is all bases.
  [accountdate] - The account date, default is now.
  [reason] - The reason text. Optional.
  [nocommit] - If set to True, does not write to the database. Default is False.
	"""
	flags = ''
	iflags = ''
	accounts = ' '.join([x for x in map(lambda x:x.strip(), accounts.split(',')) if x])
	if len(accounts) == 0:
		raise ValueError("Must specify accounts")
	if nocommit: iflags += ' --nocommit'
	if debug: iflags += ' -d'
	if lastdate: flags += ' --lastdate="%s"' % lastdate
	if region: flags += ' --region="%s"' % region
	if maincat: flags += ' --maincat="%s"' % maincat
	if base: flags += ' --base="%s"' % base
	if reason: flags += ' --reason="%s"' % reason
	if accountdate: flags += ' --accountdate="%s"' % accountdate
	cmd = os.path.expandvars('$CARMSYS/bin/mirador -s salary.batch %s --connect "$DB_URL" --schema "$DB_SCHEMA" reset %s %s') % (iflags, flags, accounts)
	print cmd
	os.system(cmd)
	
def startrun(runtype, month, extsys, admcode='T', manual=False):
	"""Starts a new salary run. Parameters are:
  runtype - The run type, see "salary runtypes" for a list
  month - The salary month (and year), e.g. Jan2011
  extsys - one of DK, SE, NO, JP, CN
  [admcode] - The code for the type of run (e.g. N = normal, T = test, default=T)
  [manual] - True to use the salary_manual channel. Default is False.
	"""
	from AbsTime import AbsTime
	runtype = runtype.upper()
	if manual:
		channel = "salary_manual"
	else:
		channel = "salary"
	firstdate = AbsTime("01%s 00:00" % month)
	lastdate = firstdate.addmonths(1)
	from dig.DigJobQueue import DigJobQueue
	from utils import TimeServerUtils
	from carmensystems.dig.framework.carmentime import toCarmenTime
	djq = DigJobQueue(channel, 'salary_manual_jobs', 'report_sources.report_server.rs_SalaryServerInterface', '1', os.environ["DB_URL"], os.environ["DB_SCHEMA"], False)
	timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
	starttime = AbsTime(toCarmenTime(timeserver.getTime()))
	id = djq.submitJob({
		'admcode':admcode.upper(),
		'fromStudio':'False',
		'commands':'start_run',
		'exportformat':'CSV',
		'extsys':extsys.upper(),
		'firstdate':str(firstdate),
		'lastdate':str(lastdate),
		'monthsBack':'1',
		'noCheckPP':'False',
		'note':os.path.expandvars('Started by $USER'),
		'reload':'0',
		'runtype':runtype,
		'spooldir':'/tmp',
		'starttime':str(starttime),
	}, 0, starttime)
	print "Job ID: %s" % (id)

def emailbalancing(runid, recipient, manual=False):
	"""Email balancing report to recipient. Parameters are:
	runid - The run id.
	recipient - The recipient.
	[manual] - True to use the salary_manual channel. Default is False.
	"""
	from AbsTime import AbsTime
	if manual:
		channel = "salary_manual"
	else:
		channel = "salary"

	from dig.DigJobQueue import DigJobQueue
	from utils import TimeServerUtils
	from carmensystems.dig.framework.carmentime import toCarmenTime

	djq = DigJobQueue(channel, 'salary_manual_jobs', 'report_sources.report_server.rs_SalaryServerInterface', '1', os.environ["DB_URL"], os.environ["DB_SCHEMA"], False)
	timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
	starttime = AbsTime(toCarmenTime(timeserver.getTime()))
	id = djq.submitJob({
		'runid':runid,
		'commands':'send_balancing',
		'recipient': str(recipient),
		'delta': 1,
	}, reloadModel="1")
	print "Job ID: %s" % (id)

def emailcrew(runid):
	"""Sends email to crew for the specified run (if applicable)
	"""
	for x in _dbsearch("salary_run_id","runid=%s"%runid):
		os.system("$CARMUSR/bin/cmsshell digjobs submit --channel=crewmailer --runid=%d --runtype=%s --extsys=%s --firstdate=%s --lastdate=%s --name=CrewMailer --report=DontCare" % (int(runid), x['runtype'], x['extsys'], x['firstdate'], x['lastdate']))
		return
	print >>sys.stderr, "Run id not found"
	
def release(runid, manual=False):
	"""Releases a run. Parameters are:
	runid - The run id.
	[manual] - True to use the salary_manual channel. Default is False.
	"""
	
	from AbsTime import AbsTime
	if manual:
		channel = "salary_manual"
	else:
		channel = "salary"

	from dig.DigJobQueue import DigJobQueue
	from utils import TimeServerUtils
	from carmensystems.dig.framework.carmentime import toCarmenTime
	
	djq = DigJobQueue(channel, 'salary_manual_jobs', 'report_sources.report_server.rs_SalaryServerInterface', '1', os.environ["DB_URL"], os.environ["DB_SCHEMA"], False)
	timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
	starttime = AbsTime(toCarmenTime(timeserver.getTime()))
	id = djq.submitJob({
		'runid':runid,
		'commands':'release_run',
		'reload':'0',
	}, 0, starttime)
	print "Job ID: %s" % (id)
