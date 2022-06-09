import utils
import os
import carmtest.framework.TestFunctions as TF
reload(TF)
from time import strftime, localtime
import subprocess

def _absolutize(dir, pth):
    if '$' in pth: pth = os.path.expandvars(pth)
    if pth[0] == '/': return pth
    return os.path.join(dir, pth)

@utils.webpage
def list(request):
    tests = TF.list_categories()
    return utils.template('root.html', locals())

@utils.webpage
def logs(request):
    testlogdir = os.path.expandvars("$CARMTMP/testlogs")
    logs = []
    for log in os.listdir(testlogdir):
        s = os.stat(os.path.join(testlogdir, log))
        logs.append({'name':log, 'size':s.st_size, 'date':strftime("%Y-%m-%d %02H:%02M", localtime(s.st_mtime))})
    #logs.sort(cmp=lambda x,y:x["date"]<y["date"])
    logs.sort(key=lambda x:x["date"])
    logs.reverse()
    return utils.template('testlogs.html', locals())


@utils.webpage
def aggregate(request):
    fileArg = '/'.join(request.path.split("/")[3:])
    files=fileArg.split(",")
    testlogdir = os.path.expandvars("$CARMTMP/testlogs")
    testcats = []
    totalRun = 0
    totalSuccess = 0
    totalFailed = 0
    totalCount = 0
    for cat in TF.list_categories():
        tcat = {'name':cat[5:], 'testfixtures':[], 'result':'notest', 'count':0, 'successCount':0, 'runCount':0}
        testcats.append(tcat)
        for tst in TF.list_tests(category=cat):
            dc = {'module':tst.__module__[9:],'name':tst.__name__, 'displayName':tst.__name__}
            if hasattr(tst, '__doc__'): dc['displayName'] = tst.__doc__            
            tcat["testfixtures"].append(dc)
            tcat['count'] += 1
            totalCount += 1
    results = TF.aggregate_results([_absolutize(testlogdir, x) for x in files])
    for cat in testcats:
        if "test_"+cat["name"] in results:
            result = results["test_"+cat["name"]]
            cat['result'] = result["totalResult"].lower()
            for testfixture in cat['testfixtures']:
                k = (testfixture["module"].split(".")[-1], testfixture["name"])
                if k in result:
                    res = result[k].get("totalResult","notest").lower()
                    if res == "success":
                        cat["successCount"] += 1
                        totalSuccess += 1
                    elif res == "failure":
                        totalFailed += 1
                    d = result[k]
                    testfixture["result"] = res
                    if res != "notest":
                        cat['runCount'] += 1
                        totalRun += 1
    return utils.template('testoverview.html', locals())


@utils.webpage
def coverage(request):
    fileArg = '/'.join(request.path.split("/")[3:])
    files=fileArg.split(",")
    testlogdir = os.path.expandvars("$CARMTMP/testlogs")
    coverage = TF.aggregate_coverage([_absolutize(testlogdir, x) for x in files])
    fileList = []
    fileCount = 0
    def addToFileList(d, indent=0, fileCount=0, path=""):
        for f,k in sorted(d.items()):
            if type(f) is int or f[:2] == '//': continue
            pth = path+"/"+f
            df = {'path':pth, 'name':f, 'type': (k.get("//dir", False)) and "dir" or "file", 'lines':k.get('//total',0), 'covered':k.get('//covered',0), 'level':indent, 'categories':[]}
            fileList.append(df)
            if k.get("//dir", False):
                fileCount = addToFileList(k, indent+1, fileCount, pth)
            else:
                fileCount += 1
                for kk,v in k.items():
                    if not type(kk) is int or not v: continue
                    for vv in v:
                        cat = vv[3][5:] 
                        if not cat in df["categories"]:
                            df["categories"].append(cat)
        return fileCount
    fileCount = addToFileList(coverage, 0, fileCount)
    totalCovered = coverage.get("//covered",0)
    totalCount = coverage.get("//total",1)
    return utils.template('testcoverageoverview.html', locals())

@utils.webpage
def filecoverage(request):
    fileArg = request.path.split("/")[3]
    path = request.path.split("/")[4:]
    pth = '/'+'/'.join(path)
    if not os.path.exists(pth):
        return "File not found"
    files=fileArg.split(",")
    testlogdir = os.path.expandvars("$CARMTMP/testlogs")
    coverage = TF.aggregate_coverage([_absolutize(testlogdir, x) for x in files])
    cvr = coverage
    while len(path) > 0:
        cvr = cvr[path[0]]
        del path[0]
    lines = []
    totalCount = 0
    totalCovered =0
    for ct, line in enumerate(file(pth)):
        ct = ct + 1
        covered = "empty"
        tests = ""
        if ct in cvr:
            totalCount += 1
            if len(cvr[ct]) > 0:
                covered = "covered"
                totalCovered += 1
                tcat = None
                tname = None
                for tt in cvr[ct]:
                    if tcat is None or tcat == tt[3][5:]:
                        tcat = tt[3][5:]
                    else:
                        tcat = tcat + "," + tt[3][5:]
                    if tests == "": tests = tt[3][5:]
                    #tests.append({'category':tt[3], 'name':tt[1]})
            else:
                covered = "notcovered"
        lines.append({'number':ct, 'text':line, 'covered':covered, 'tests':tests})
    
    return utils.template('testcoveragefile.html', locals())

@utils.webpage
def runlog(request):
    type = request.path.split("/")[3]
    xslt = os.path.expandvars("$CARMUSR/lib/python/carmtest/framework/%s.xslt") % type
    if not os.path.exists(xslt):
        return "Report type '%s' not found" % type
    fileArg = request.path.split("/")[4:]
    if len(fileArg) == 1:
        testLog = os.path.join(os.path.expandvars("$CARMTMP/testlogs"), fileArg[0])
    else:
        testLog = '/'.join(fileArg)
        if testLog[0] != '/': testLog = '/%s' % testLog
    import sys, time
    sys.stdout.flush()
    t = time.time()
    stdout, _ = subprocess.Popen("xsltproc '%s' '%s'" % (xslt, testLog), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    sys.stdout.flush()
    
    return stdout
    