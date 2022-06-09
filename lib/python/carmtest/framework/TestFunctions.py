'''
Created on Feb 11, 2010

@author: rickard
'''

import carmtest.framework
import os, os.path
import sys
from datetime import datetime
from xml.dom.minidom import parseString

try:
    import carmtest.framework.Measure as Measure
except:
    Measure = None
    
_SKIP_MEASUREMENTS = False
_SKIP_COVERAGE = False


def run_tests(cat, mod, testname):
    "Run test FROM MENU! Not used when running as a batch job"
    if mod:
        if testname:
            case = "%s.%s.%s" % (cat, mod, testname)
        else:
            case = "%s.%s" % (cat, mod)
    else:
        case = cat
    print "Running testcases matching %s" % case
    run(case)
    
    try:
        import StudioHtml
        if 1 or mod:
            transform = os.path.expandvars("$CARMUSR/lib/python/carmtest/framework/TestReport.xslt")
        else:
            transform = os.path.expandvars("$CARMUSR/lib/python/carmtest/framework/TestSummary.xslt")
        print file(_lastResult).read()
        StudioHtml.displayXmlFile(_lastResult, transform, title="Test results for %s" % case)
    except:
        import carmstd.studio.cfhExtensions as ext
        ext.showFile(_lastResult, "Test results for %s" % case)
    
def list_categories():
    f = os.path.dirname(carmtest.__file__)
    subs = []
    for sf in os.listdir(f):
        if sf[:5] == 'test_' and os.path.isdir(os.path.join(f, sf)):
            subs.append(sf)

    subs.sort()
    return subs

def list_tests(category, delimited=False, reloadTests=True, preconds=None):
    f = os.path.dirname(carmtest.__file__)
    f = os.path.join(f, category)
    if not os.path.isdir(f): return []
    subs = []
    for sf in os.listdir(f):
        if sf[0] != '_' and sf[-3:] == '.py' and os.path.isfile(os.path.join(f, sf)):
            if delimited and len(subs) > 0: subs.append('-')
            mname = sf[:sf.index('.')]
            mpath = 'carmtest.%s.%s' % (category, mname)
            try:
                mod = __import__(mpath)
            except ImportError,e:
                print >>sys.stderr, e
                print >>sys.stderr, "WARNING: Test '%s' could not be imported." % mpath
                print >>sys.stderr, "         Make sure not to have any non-trivial (i.e. Studio) imports in"
                print >>sys.stderr, "         test module header. Test modules must *always* be importable!"
                continue
            smod = getattr(getattr(mod, category), mname) 
            if reloadTests:
                smod = reload(smod)
            for clsname in dir(smod):
                cls = getattr(smod, clsname)
                if type(cls) == type(type):
                    if issubclass(cls, carmtest.framework.TestFixture):
                        if cls.__module__ == mpath:
                            if preconds == None or test_has_prerequisites(cls, preconds):
                                subs.append(cls)
            
    return subs

parsed_logs = {}

def get_test_result(fn):
    from xml.dom.minidom import parseString
    import re
    
    if fn in parsed_logs:
        return parsed_logs[fn]
    
    try:
        with open(fn, "r") as f:
            xml = f.read()
            
        # Make sure that what we parse is a string with:
        #  - exactly one "<?xml" declaration.
        #  - an <OuterTestRun> enclosing the <TestRun> items. 
        #  - only one level of <TestRun>. Remove outer start/end tags, should they exist.

        fixxml = re.search(r"<\?xml .*? \?>", xml)
        fixxml = (fixxml.group() + "\n") if fixxml else '''<?xml version="1.0" encoding="UTF-8" ?>\n'''
        fixxml += "<OuterTestRun>\n"
        st = -1
        in_run = False
        for m in re.finditer("</?TestRun.*?>", xml):
            if m.group().startswith("<TestRun"):
                st = m.start()
                in_run = True
            else:
                if in_run:
                    fixxml += xml[st:m.end()] + "\n"
                in_run = False
        fixxml += "</OuterTestRun>\n"
        if fixxml != xml:
            xml = fixxml
            with open(fn, "w") as f:
                f.write(xml)
        
        parsed_logs[fn] = parseString(xml)
        return parsed_logs[fn]

    except Exception, e:
        print >>sys.stderr, "WARNING: Failed to parse %s: %s" % (fn, e)
        parsed_logs[fn] = parseString("<OuterTestRun></OuterTestRun>")
        return parsed_logs[fn]

def aggregate_results(files):
    "Parses a list of test log XML files and produces aggregate test results"
    sys.stdout.flush()
    results = {}
    for fn in files:
        doc = get_test_result(fn)
        for testRun in doc.getElementsByTagName("TestRun"):
            rundate = testRun.getAttribute("date")
            for testFixture in testRun.getElementsByTagName("TestFixture"):
                name = testFixture.getAttribute("name")
                module = testFixture.getAttribute("module")
                category = testFixture.getAttribute("category")
                k = (module, name)
                if not category in results:
                    results[category] = {}
                    results[category]['totalResult'] = "NoTest"
                if not k in results[category]:
                    results[category][k] = {}
                    results[category][k]['totalResult'] = "NoTest"
                nc = nt = nr = 0
                for testCase in testFixture.getElementsByTagName("TestCase"):
                    nc += 1
                    test = testCase.getElementsByTagName("Test")
                    if (test):
                        nt += 1
                        try:
                            result = test[0].getElementsByTagName("Result")[0].childNodes[0].nodeValue
                            nr += 1
                        except:
                            result = None
                        else:
                            if (result == "Failure") or (results[category][k]['totalResult'] == "NoTest"):
                                results[category][k]['totalResult'] = result
                                if (result == "Failure") or (results[category]['totalResult'] == "NoTest"):
                                    results[category]['totalResult'] = result
    sys.stdout.flush()
    return results

def aggregate_coverage(files, gatherSourceCodeStatistics=True, perDirStat=True):
    if gatherSourceCodeStatistics:
        from figleaf import get_lines
    covfiles = {}
    sys.stdout.flush()
    
    for fn in files:
        doc = get_test_result(fn)
        for testRun in doc.getElementsByTagName("TestRun"):
            rundate = testRun.getAttribute("date")
            for testFixture in testRun.getElementsByTagName("TestFixture"):
                name = testFixture.getAttribute("name")
                module = testFixture.getAttribute("module")
                category = testFixture.getAttribute("category")
                for coverage in testFixture.getElementsByTagName("Coverage"):
                    for cfile in coverage.getElementsByTagName("File"):
                        pth = cfile.getAttribute("path")
                        if "/lib/python/contrib" in pth or "/lib/python/carmtest" in pth: continue
                        pars = []
                        if perDirStat:
                            rt = covfiles
                            for p in pth.split('/'):
                                if not p: continue
                                pars.append(rt)
                                if not p in rt:
                                    rt[p] = {}
                                    rt["//dir"] = True
                                rt = rt[p]
                        else:
                            if not pth in covfiles:
                                covfiles[pth] = {}
                            rt = covfiles[pth]
                            
                        for line in cfile.childNodes[0].nodeValue.split(","):
                            line = int(line)
                            if not line in rt:
                                rt[line] = []
                            k = (rundate, name, module, category)
                            if not k in rt[line]:
                                rt[line].append(k)
                        if gatherSourceCodeStatistics:
                            if os.path.exists(pth):
                                lines = get_lines(file(pth,'r'))
                                for line in lines:
                                    line = int(line)
                                    if not line in rt:
                                        rt[line] = []
                                    else:
                                        rt['//covered'] = rt.get('//covered',0) + 1
                                rt['//total'] = rt.get('//total',0) + len(lines)
                                for par in pars:
                                    par['//total'] = par.get('//total',0) + rt['//total']
                                    par['//covered'] = par.get('//covered',0) + rt.get('//covered',0)
    sys.stdout.flush()
    return covfiles

def collect_coverage(files, outf=sys.stdout, gatherSourceCodeStatistics=True, perDirStat=False):
    "Parses a list of test log XML files and produces aggregate coverage information in XML format"
    covfiles = aggregate_coverage(files, gatherSourceCodeStatistics, perDirStat)
    print >>outf, '<?xml version="1.0" encoding="UTF-8"?>'
    if perDirStat:
        print >>outf, '<CoverageData total="%d" covered="%d">' % (covfiles.get("//total",0), covfiles.get("//covered",0))
    else:
        print >>outf, '<CoverageData>'
    def pathelem(dic, indent):
        for file, dat in sorted(dic.items()):
            if file[:2] == '//' or type(file) is int: continue
            if dat.get("//dir",False):
                print >>outf, '%s<Dir name="%s" total="%d" covered="%d">' % (' '*indent, file.encode("UTF-8"), dat.get("//total",0), dat.get("//covered",0))
                pathelem(dat, indent+2)
                print >>outf, '%s</Dir>' % (' '*indent)
            else:
                print >>outf, '%s<File name="%s" total="%d" covered="%d">' % (' '*indent, file.encode("UTF-8"), dat.get("//total",0), dat.get("//covered",0))
                for ln,sq in sorted(dat.items()):
                    if not type(ln) is int: continue
                    if len(sq) > 0:
                        print >>outf, '%s  <Line num="%d">' % (' '*indent, ln)
                        for (rundate, name, module, category) in sq:
                            print >>outf, '%s    <Test name="%s" module="%s" category="%s" date="%s"/>' % (' '*indent, name.encode("UTF-8"), module.encode("UTF-8"), category.encode("UTF-8"), rundate.encode("UTF-8"))
                        print >>outf, '%s  </Line>' % (' '*indent)
                    else:
                        print >>outf, '%s  <Line num="%d"/>' % (' '*indent, ln)
                print >>outf, '%s</File>' % (' '*indent)
    pathelem(covfiles, 2)
    print >>outf, '</CoverageData>'

def get_prerequisites(test):
    "Returns a list of prerequisites for a test fixture(class)"
    if not hasattr(test, '__init__'): return []
    cons = getattr(test, '__init__')
    if not hasattr(cons, '_prerequisite'): return []
    pr = getattr(cons, '_prerequisite')
    if not isinstance(pr, list): return []
    return pr

def test_has_prerequisites(test, requirements):
    "Returns true if the test has all the specified prerequisites"
    if requirements == None or requirements == []: return True
    if isinstance(requirements, str):
        if not requirements: return True 
        requirements = requirements.split(',')
        
    pr = get_prerequisites(test)
    for req in requirements:
        if not req in pr: return False
    return True

_TestResult = None
_lastResult = None
            

def run(test, logFile=None, preconds=None, skipMeasurements=False, coverage=True):
    global _TestResult
    global _SKIP_MEASUREMENTS
    global _SKIP_COVERAGE
    oldSkipMeasurements = _SKIP_MEASUREMENTS
    oldSkipCoverage = _SKIP_COVERAGE
    _SKIP_MEASUREMENTS = skipMeasurements
    _SKIP_COVERAGE = not coverage
    if not _SKIP_COVERAGE:
        import figleaf
    try:
        import traceback
        if not logFile or _TestResult and _TestResult.fileName() != logFile:
            _TestResult = None
        logfile(logFile).startRun(test)
        if test == 'test_all':
            for cat in list_categories():
                run(cat, logFile, preconds, skipMeasurements)
        else:
            t = test.split('.')
            assert len(t) > 0 and t[0] in list_categories(), "Invalid test '%s' specified" % test
            for tst in list_tests(t[0], reloadTests=False, preconds=preconds):
                if len(t) > 1:
                    tmod = tst.__module__.split('.')[-1]
                    tname = tst.__name__
                    if t[1] != tmod: continue
                    if len(t) > 2:
                        if t[2] != tname: continue
                try:
                    pqs = []
                    if not tst.available(pqs):
                        print "Skipping", tst
                        logfile().startTestFixture(tst)
                        logfile().startPrereq(tst)
                        logfile().skip(', '.join(pqs))
                        logfile().endPrereq(tst)
                        logfile().endTestFixture(tst)
                        continue
                except:
                    print "Precondition check failed for", tst
                    logfile().startTestFixture(tst)
                    logfile().startPrereq(tst)
                    logfile().error(sys.exc_info()[1])
                    logfile().endPrereq(tst)
                    logfile().endTestFixture(tst)
                    continue
                try:
                    print "Running", tst
                    testFixture = tst()
                except:
                    continue
                logfile().startTestFixture(tst)
                if not _SKIP_COVERAGE:
                    figleaf.init(include_only=os.path.expandvars("$CARMUSR/lib/python"))
                    figleaf.start()
                try:
                    for testfunc in [x for x in dir(testFixture) if x[:4] == 'test' and hasattr(getattr(testFixture, x), '__call__')]:
                        logfile().startTestCase(testFixture, testfunc)
                        if not tst.hasPrerequisites(getattr(testFixture,testfunc).__name__, pqs):
                            print " - Skipping test \"%s\"" % testfunc
                            logfile().startPrereq(tst)
                            logfile().skip(', '.join(pqs))
                            logfile().endPrereq(tst)
                            logfile().endTestCase(testFixture, testfunc)
                            continue
                        else:
                            print " - Running test \"%s\"" % testfunc
                        logfile().startSetUp(testFixture, testfunc)
                        try:
                            testFixture.setUp()
                        except:
                            traceback.print_exc()
                            logfile().error(sys.exc_info()[1])
                            logfile().endSetUp(testFixture, testfunc)
                            logfile().startTestCaseBase(testFixture, testfunc)
                            logfile().result(testFixture, testfunc, "Failure")
                            logfile().endTestCaseBase(testFixture, testfunc)
                            logfile().endTestCase(testFixture, testfunc)
                            continue
                        
                        logfile().endSetUp(testFixture, testfunc)
                        
                        logfile().startTestCaseBase(testFixture, testfunc)
                        try:
                            getattr(testFixture, testfunc)()
                            logfile().result(testFixture, testfunc, "Success")
                        except:
                            traceback.print_exc()
                            logfile().error(sys.exc_info()[1])
                            logfile().result(testFixture, testfunc, "Failure")
                        logfile().endTestCaseBase(testFixture, testfunc)
                        
                        logfile().startTearDown(testFixture, testfunc)
                        try:
                            testFixture.tearDown()
                        except:
                            traceback.print_exc()
                            logfile().error(sys.exc_info()[1])
                        logfile().endTearDown(testFixture, testfunc)
                        logfile().endTestCase(testFixture, testfunc)
                finally:            
                    if not _SKIP_COVERAGE:
                        figleaf.stop()
                        logfile().coverage()
                    logfile().endTestFixture(tst)
        logfile().endRun()
        ret = logfile().get_text()
        global _lastResult
        _lastResult = logfile().fileName()
        return ret
    finally:
        _SKIP_MEASUREMENTS = oldSkipMeasurements
        _SKIP_COVERAGE = oldSkipCoverage
        logfile().dispose()
        _TestResult = None
       
def logfile(fileName=None):
    global _TestResult
    if not _TestResult:
        _TestResult = TestResult(fileName)
    return _TestResult

def run_cmdline(cmdline, preconds=None):
        
    if type(cmdline) is tuple:
        cmdline = list(cmdline)
    elif type(cmdline) is str:
        cmdline = cmdline.split()
    if not preconds:
        preconds = []
        for i in range(1, len(cmdline) - 1):
            if cmdline[i] == "-p":
                preconds = cmdline[i + 1:]
                cmdline = cmdline[:i]
                break
    if cmdline[0] == "list_categories":
        print '\n'.join(list_categories())
    elif cmdline[0] == "list_categories_full":
        for cat in list_categories():
            #print ":: %s ::" % cat
            run_cmdline("list_tests_full %s" % cat, preconds)
    elif cmdline[0] == "list_tests":
        assert len(cmdline) > 1 and cmdline[1], "Expected argument"
        assert cmdline[1] in list_categories(), "Invalid category"
        print '\n'.join([(x.__module__[9:] + "." + x.__name__) for x in list_tests(cmdline[1], reloadTests=False) if test_has_prerequisites(x, preconds)])
    elif cmdline[0] == "list_tests_full":
        assert len(cmdline) > 1 and cmdline[1], "Expected argument"
        assert cmdline[1] in list_categories(), "Invalid category"
        l = ["%-52s%s" % ((x.__module__[9:] + "." + x.__name__), ','.join(get_prerequisites(x))) for x in list_tests(cmdline[1], reloadTests=False) if test_has_prerequisites(x, preconds)]
        if len(l) > 0: print '\n'.join(l)
    elif cmdline[0] == "run_test":
        return run(cmdline[1], preconds=preconds)
    else:
        assert False, "Incorrect argument"
        
class TestResult(object):
    def __init__(self,fileName=None):
        if "CARMTEST_LOG_FILE" in os.environ:
            testLogDir = os.path.dirname(os.path.expandvars("$CARMTEST_LOG_FILE"))
            fileName = os.path.expandvars("$CARMTEST_LOG_FILE")
        elif "CARMTEST_LOG_DIR" in os.environ:
            testLogDir = os.path.expandvars("$CARMTEST_LOG_DIR")
        else:
            testLogDir = os.path.expandvars("$CARMTMP/testlogs")
        if not os.path.isdir(testLogDir):
            if os.path.exists(testLogDir) or os.path.islink(testLogDir): os.unlink(testLogDir)
            os.makedirs(testLogDir)
        
        idx = 1
        append = "a"
        if not fileName:
            append = "w"
            fileName = None
            while not fileName or os.path.exists(fileName): 
                fileName = os.path.join(testLogDir, "%s.%d.%s.%d.xml" % (os.environ["HOST"], os.getpid(), datetime.today().isoformat(), idx))
        
        print "== Logging test results to %s ==" % fileName
        self._filehandle = file(fileName, append)
        self._fileName = fileName
        self._results = {}
        print >> self._filehandle, '<?xml version="1.0" encoding="UTF-8" ?>'
        
    def startRun(self, filterString=""):
        print >> self._filehandle, '<TestRun date="%s" filterString="%s">' % (datetime.today().isoformat(), filterString)
        
    def endRun(self):
        print >> self._filehandle, '</TestRun>'
        
    def comment(self, msg):
        print >> self._filehandle, '  <!-- %s -->' % msg
        
    def startTestFixture(self, testcls):
        testFixtureName = testcls.__name__
        mod = testcls.__module__.split('.')
        print >> self._filehandle, '  <TestFixture name="%s" module="%s" category="%s">' % (testFixtureName, mod[-1], mod[-2])
        
    def endTestFixture(self, testcls):
        print >> self._filehandle, '  </TestFixture>'
        
    def startPrereq(self, testcls):
        print >> self._filehandle, '      <Prerequisites>'
        
    def endPrereq(self, testcls):
        print >> self._filehandle, '      </Prerequisites>'
        
    def startTestCase(self, testobj, testName):
        print >> self._filehandle, '    <TestCase name="%s">' % testName
        self._measurements("before")
        
    def endTestCase(self, testobj, testName):
        self._measurements("after")
        print >> self._filehandle, '    </TestCase>'
        
    def startSetUp(self, testobj, testName):
        print >> self._filehandle, '      <SetUp>'
        
    def endSetUp(self, testobj, testName):
        print >> self._filehandle, '      </SetUp>'
        
    def startTearDown(self, testobj, testName):
        print >> self._filehandle, '      <TearDown>'
        
    def endTearDown(self, testobj, testName):
        print >> self._filehandle, '      </TearDown>'
        
    def startTestCaseBase(self, testobj, testName):
        print >> self._filehandle, '      <Test>'
        
    def endTestCaseBase(self, testobj, testName):
        print >> self._filehandle, '      </Test>'
        
    def _measurements(self, where):
        global _SKIP_MEASUREMENTS
        if _SKIP_MEASUREMENTS: return
        print >> self._filehandle, '      <Measurements where="%s">' % where
        if Measure:
            try:
                for func in [x for x in dir(Measure) if not x[:1] == '_' and hasattr(getattr(Measure, x), '__call__')]:
                    try:
                        val = getattr(Measure, func)()
                    except:
                        val = "#ERROR"
                    print >> self._filehandle, '        <%s>%s</%s>' % (func, val, func)
            except:
                print >> self._filehandle, '      <!-- Error! -->'
        else:
            print >> self._filehandle, '      <!-- Not available -->'
        print >> self._filehandle, '      </Measurements>'
        
    def coverage(self):
        global _SKIP_COVERAGE
        if _SKIP_COVERAGE: return
        import figleaf
        print >> self._filehandle, '    <Coverage>'
        fi = figleaf.get_info()
        for row in fi:
            print >> self._filehandle,'      <File path="%s">%s</File>' % (row, ','.join(str(x) for x in fi[row]))
        print >> self._filehandle, '    </Coverage>'
    
    def dispose(self):
        if self._filehandle:
            self._filehandle.close()
        self._filehandle = None
        return self
        
    def reopen(self):
        assert self._fileName, "Filename not set"
        if not self._filehandle:
            self._filehandle = file(self._fileName, "a")
        
    def fileName(self):
        return self._fileName
    
    def log(self, msg, severity="Info"):
        print >> self._filehandle, '        <Log severity="%s">%s</Log>' % (severity, msg)

    def get_text(self):
        hadFilehandle = False
        if self._filehandle:
            hadFilehandle = True
            self.dispose()
        f = file(self._fileName, "r")
        ret = f.read()
        f.close()
        if hadFilehandle: self.reopen()
        return ret
    
    def error(self, msg):
        if msg[:5] == "DATA:":
            print >> self._filehandle, '        <Error type="data">%s</Error>' % msg[5:].strip()
        else:
            print >> self._filehandle, '        <Error>%s</Error>' % msg
            
    def skip(self, precond):
        print >> self._filehandle, '        <Error type="skip">%s</Error>' % precond
            
    def result(self, testobj, testName, res):
        self._results[res] = self._results.get(res, 0) + 1
        print >> self._filehandle, '        <Result>%s</Result>' % res
        
    def results(self):
        return self._results
