# Unit tests
import sys, os
import carmtest.framework.TestFunctions as TF
import re
import datetime
from xml.dom.minidom import parseString


def _parse_log_file(logfilepath, verbose=True):
    """ Parses the log file and counts the number of successful and failed test cases """
    
    if not os.path.exists(logfilepath):
        return 0, 1 # This is considered a failure
    
    failed_test_cases = []
    passed_test_cases = []

    # Split the file into separate <TestRun>...</TestRun> blocks.
    # Ignore anything inbetween. If blocks are nested, ignore outer.
    
    with open(logfilepath, 'r') as f:
        xml = ""
        for line in f:
            if line.find("<TestRun "):
                xml = '''<?xml version="1.0" encoding="UTF-8" ?>\n''' + line
            else:
                xml += line
                if line.find("</TestRun>"):
                    _parse_test_case(xml, failed_test_cases, passed_test_cases)
                    xml = ""

    if verbose:
        print "="*80
        if len(failed_test_cases) > 0:
            print "The following test cases failed:"
            for failure in failed_test_cases:
                print "  ", failure
        else:
            print "All test cases passed"
        print "="*80    
                        
    return len(passed_test_cases), len(failed_test_cases)

def _parse_test_case(xml, failed_test_cases, passed_test_cases):
    """ Parses an XML file for the test and adds failed and passed 
        tests to the arguments
    """

    # Ignore empty xml data
    if len(xml) == 0:
        return
    
    # Ignore invalid xml data    
    try:
        dom = parseString(xml)
    except:
        return
    
    fixtures = dom.getElementsByTagName("TestFixture")
    for fixture in fixtures:
        f_name = fixture.getAttribute("name")
        
        test_cases = fixture.getElementsByTagName("TestCase")
        if test_cases is None or len(test_cases) == 0:
            continue
        
        for test_case in test_cases:
            tc_name = test_case.getAttribute("name")
            
            results = test_case.getElementsByTagName("Result")
            errors = test_case.getElementsByTagName("Error")

            if len(results) != 0:
                result = results[0]
                text = result.childNodes[0].data
                if text == "Success":
                    passed_test_cases.append("%s.%s passed." % (f_name, tc_name))
                elif len(errors) !=  0:
                    failed_test_cases.append("%s.%s failed: %s" % (f_name, tc_name, errors[0].childNodes[0].data))
                else:
                    failed_test_cases.append("%s.%s failed: Unknown reason" % (f_name, tc_name))


def _list_(cat=None,preconds=None):
    "Lists all tests and categories"
    if not cat:
        if preconds:
            print >>sys.stderr, "Warning: Argument",preconds,"ignored here"
        print '\n'.join(TF.list_categories())
    else:
        if cat == "all":
            cat = TF.list_categories()
        else:
            if not '_' in cat: cat = "test_"+cat
            cat = [cat]
        tc = []
        for c in cat: 
            tc += [(x.__module__[9:],x.__name__, ','.join(TF.get_prerequisites(x))) for x in TF.list_tests(c, reloadTests=False) if not preconds or TF.test_has_prerequisites(x, preconds)]
        if len(tc) == 0:
            print >>sys.stderr, "No tests found"
            return
        ms = [max([len(y[x])] for y in tc)[0] for x in range(3)]
        fmt = "%%-%ds %%-%ds %%-%ds" % tuple(ms)
        print fmt % ("Category", "Test suite", "Preconds")
        print '-'*(sum(ms)+3)
        
        for t in tc:
            print fmt % t
        #print '\n'.join(TF.list_tests(cat))
        
def run(testname=None, preconds=None, perf=True, coverage=False, reporttemplate=None, studio=None, planstart=None, planend=None, planregion=None):
    "Runs a certain test"
    if not testname and not preconds:
        print >>sys.stderr, "Must specify test name or preconditions"
        return 1
    if not studio and (planstart or planend or planregion):
        print >>sys.stderr, "Plan start/end/region requires --studio=True"
        return 1
    if studio and not studio in ("planning","tracking"):
        print >>sys.stderr, "Studio must be 'planning' or 'tracking'"
        return 1
    if (planstart or planend or planregion) and not (planstart and planend and planregion):
        print >>sys.stderr, "Must set all or none of --planstart, --planend and --planregion"
        return 1
    
    if planstart == "current":
        now = datetime.datetime.now()
        if now.month == 1:
            startofprevmonth = datetime.datetime(now.year - 1, 12, 1)
        else:
            startofprevmonth = datetime.datetime(now.year, now.month - 1, 1)

        planstart = startofprevmonth.strftime("%d%b%Y") #Start of month
        
    if planend == "current":
        now = datetime.datetime.now()
        if now.month == 12:
       	    endofmonth = datetime.datetime(now.year+1, 1, 1) - datetime.timedelta(days=1)
        else:
            endofmonth = datetime.datetime(now.year, max((now.month + 1) % 13, 1), 1) - datetime.timedelta(days=1)
        planend = endofmonth.strftime("%d%b%Y") #Start of month
    
    if testname and not '_' in testname: testname = "test_"+testname
    if not studio:
        log = TF.logfile(None)
        logfile = log.fileName()
        ret = TF.run(testname, logFile=logfile, preconds=preconds, skipMeasurements=not perf, coverage=coverage)
    else:
        log = None
        logfile = TF.logfile(None).dispose().fileName()
        os.environ["CARMTEST_LOG_FILE"] = logfile
        os.unlink(logfile)
        studioflag = 't'
        command = 'run_tests'
        flags = ''
        if studio == "planning":
            studioflag = 'p'
        if planstart:
            command = 'load_and_run_tests'
            flags = r',\"%s\",\"%s\",\"%s\"' % (planstart, planend, planregion)
        cmdline = r'$CARMUSR/bin/studio.sh -S %s -d -p "PythonRunFile(\"$CARMUSR/lib/python/carmtest/framework/StudioStartup.py\",\"%s\"%s,\"run_test\",\"%s\")"' % (studioflag, command, flags, testname)
        print "Running:",cmdline
        retcode = os.system(cmdline)
        nofSuccesses, nofFailures = _parse_log_file(logfile)
        
        print "Summary: Studio exit code %u, number of successful cases %u, number of failed cases %u" % (retcode, nofSuccesses, nofFailures)
        
        if retcode != 0 or nofFailures > 0:
            sys.exit(1)
        else:
            sys.exit(0)
        
        
    if reporttemplate:
        outFile = os.path.splitext(logfile)[0]+".html"
        if 'CARMTEST_REPORT_OUTFILE' in os.environ:
            outFile = os.environ['CARMTEST_REPORT_OUTFILE']
        if not '/' in reporttemplate:
            reporttemplate = os.path.join(os.path.expandvars("$CARMUSR/lib/python/carmtest/framework"), reporttemplate)
        if not os.path.exists(reporttemplate): reporttemplate += ".xslt"
        os.system("xsltproc '%s' '%s' > '%s'" % (reporttemplate, logfile, outFile))
        print "Report: %s" % outFile
        if log:
            if log.results().get("Success",0) < len(log.results()):
                for k in log.results():
                    print "%20s %s" % (k, log.results()[k])
                return 1
            else:
                print "All tests succeeded"
        
def coveragereport(*files, **kwargs):
    "Generates a test coverage report from a number of test logs"
    from time import strftime
    output = kwargs.get("output")
    if output:
        outdir = os.path.dirname(output)
        if not os.path.exists(outdir): os.makedirs(outdir)
        output = file(output,'w')
    else:
        output = sys.stdout
    dirs = kwargs.get("dirs", False)
    sourcestat = kwargs.get("sourcestat", False)
    TF.collect_coverage(files, output, perDirStat=dirs, gatherSourceCodeStatistics=sourcestat)
    #print TF.aggregate_coverage(files)
    
def reportsfromlogs(*logfiles, **kwargs):
    "Generates static HTML reports from test logs in XML format"
    from time import strftime
    
    class DummyRequest(object):
        def __init__(self, logfiles, reqfmt):
            self.path = reqfmt % (','.join(logfiles))

    if len(logfiles) == 1 and os.path.isdir(logfiles[0]):
        lf = []
        for f in os.listdir(logfiles[0]):
            fn = os.path.join(logfiles[0], f)
            if f[0] != '.' and os.path.isfile(fn):
                lf.append(fn)
        logfiles = lf
    logfiles = [x for x in logfiles if not ',' in x]
            
    outd = None
    if 'CARMTEST_REPORT_OUTDIR' in os.environ:
        outd = os.environ['CARMTEST_REPORT_OUTDIR']
        if not os.path.exists(outd):
            os.makedirs(outd)
    else:
        outdir = strftime(os.path.expandvars("$CARMTMP/testreports/$HOST.%Y%02m%02d.$USER"))
        for i in range(1,1000):
            outd = "%s.%d" % (outdir, i)
            if not os.path.exists(outd):
                os.makedirs(outd)
                break
    if not outd: raise ValueError, "Invalid out dir"
    import carmweb.carmweb_tests as CWT
    
    def fixupHTML(st):
        st = re.sub(r'/tests/coverage/[^"]+', 'coverage.html',
            re.sub(r'/tests/aggregate/[^"]+', 'aggregate.html',
            re.sub(r'/tests/runlog/TestReport/([^"]+)"', r'TestReport_\1.html"',
            st.replace("/static/carmweb.css", "carmweb.css"))))
        for fn in logfiles:
            trpt = fn.split('/')[-1]
            lfn = trpt.replace(':','.')
            st = st.replace(fn, lfn)
        st = st.replace("TestReport_aggregate/", "TestReport_")
        return st
    
    # Generate 'aggregate' report
    print >>file("%s/carmweb.css"%outd,"w"), file(os.path.expandvars("$CARMUSR/data/web/static/carmweb.css")).read()
    print >>file("%s/aggregate.html"%outd,"w"), fixupHTML(CWT.aggregate(DummyRequest(logfiles, "/tests/aggregate/%s")))
    print >>file("%s/coverage.html"%outd,"w"), fixupHTML(CWT.coverage(DummyRequest(logfiles, "/tests/coverage/%s")))
    for testrpt in logfiles:
        trpt = testrpt.split('/')[-1].replace(':','.')
        print >>file("%s/TestReport_%s.html"%(outd, trpt),"w"), fixupHTML(CWT.runlog(DummyRequest([testrpt], "/tests/runlog/TestReport/%s")))
