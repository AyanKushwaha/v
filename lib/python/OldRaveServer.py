# RaveServer.py
# coding=utf-8
# Purpose: Extend the Studio RPC server with the ability to run arbitraty Rave expressions on the marked legs or a custom selection.
# Created by: Rickard Petzäll (rickard)

# 
# See client.py for an example of how to use it
#
import carmensystems.studio.webserver.XMLRPCDispatcher as XD
import carmensystems.rave.api as R
import carmensystems.studio.webserver.WebServer as WS
try:
    import Cui
except:
    class CuiTempClass(object):
        CuiWhichArea=-2
    Cui = CuiTempClass()


import sys
import os
import subprocess
import signal
import shutil
import tempfile
from socket import getfqdn
from AbsTime import AbsTime
from RelTime import RelTime
# from xmlrpclib import Fault
from datetime import datetime
import time
import xmlrpclib
# import Cfh
# import Crs
# import Csl
# import Cps
import Localization

__remote_lcls = None
__remote_gbls = None
def ___invalid(): pass

def get(req):
    req.send_ok_headers()
    req.wfile.write("<h1>Hello world</h1>")

def cmdline(cmd):
    cmdpy = os.path.expandvars('$CARMSYS/lib/python/commandline/RunCommand.py')
    saveargs = sys.argv
    try:
        sys.argv = [cmdpy , cmd, 'execute']
        execfile(cmdpy)
    finally:
        sys.argv = saveargs
    return "OK"
    
def evalPython(code):
    global __remote_gbls, __remote_lcls
    if not __remote_gbls:
        __remote_gbls = globals()
        __remote_lcls = locals().copy()
    try:
        return eval(code, __remote_gbls, __remote_lcls)
    except SyntaxError:
        exec code in __remote_gbls, __remote_lcls
        return ___invalid

def evalPythonString(code):
    s = evalPython(code)
    if s is ___invalid: return ''
    return repr(s)
    
def getSelection(area=Cui.CuiWhichArea):
    sel = getSelectionAndArea()
    if not sel: return []
    return sel[1]
    
def getSelectionAndArea(area=Cui.CuiWhichArea):
    tryAll = area == Cui.CuiWhichArea
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    sel = Cui.CuiGetLegs(Cui.gpc_info, area, "marked")
    idx = 0
    if tryAll and not sel:
        area = (Cui.CuiArea0, Cui.CuiArea1, Cui.CuiArea2, Cui.CuiArea3)[idx]
        sel = Cui.CuiGetLegs(Cui.gpc_info, area, "marked")
        idx += 1
    return (area, sel)
    
def getMode(area=Cui.CuiWhichArea):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    ret = Cui.CuiGetAreaMode(Cui.gpc_info, area)
    
def getSuitableContext(area=Cui.CuiWhichArea):
    try:
        m = getMode(area)
    except Exception:
        return "default_context"
    if m == 5:
        return "sp_crew"
    elif m == 4:
        return "sp_crrs"
    elif m == 2:
        return "sp_legs"
    elif m == 7:
        return "ac_rotations"
    return "default_context"
    
def getModeForContext(ctx):
    if ctx == "sp_crew": return Cui.CrewMode
    if ctx == "sp_crrs": return Cui.CrrMode
    return Cui.LegMode
    
def getReportServerPublishType():
    try:
        import carmensystems.common.reportWorker as reportWorker
        publishType = reportWorker.ReportGenerator().getPublishType()
        if not publishType:
            return ''
    except:
        return None # No report server

        
def findAllEval(context, where, raveExprs, sort_by = None, iter='iterators.leg_set'):
    if not raveExprs:
        raise Exception("No expressions")
    elif type(raveExprs) is str:
        raveExprs = raveExprs,
    else:
        raveExprs = tuple(raveExprs)
    if not R.ruleset_loaded(): raise Exception("Ruleset not loaded")
    if where:
        if not type(where) is str:
            where = tuple(where)
        else:
            where = where,
    else:
        where = None
    if sort_by:
        if not type(sort_by) is str:
            sort_by = tuple(sort_by)
        else:
            sort_by = sort_by,
    else:
        sort_by = None
    it = R.iter(iter, where=where, sort_by=sort_by)
    if not context: context = "-1"
    print "Evaluating %s in %s from RPC" % (str(raveExprs), str(context))
    if type(context) is str:
        if context == "-1":
            area = Cui.CuiWhichArea
        elif context == "0":
            area = Cui.CuiArea0
        elif context == "1":
            area = Cui.CuiArea1
        elif context == "2":
            area = Cui.CuiArea2
        elif context == "3":
            area = Cui.CuiArea3
        elif context.isdigit():

            #Crew id
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            if getReportServerPublishType():
                Cui.gpc_set_one_published_crew_chain(Cui.gpc_info, context)
            else:
                Cui.gpc_set_one_crew_chain(Cui.gpc_info, context)
            context = 'default_context'
            area = None
        else:
            area = None
        if area != None:
            area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
            try:
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
            except:
                # Probably window not open
                raise Exception("Unable to use window " + str(context))
            context = "default_context"
        else:
            context = R.context(context)
    rv = []

    rs, = R.eval(context, R.foreach(it, *raveExprs))


    for r in rs:
        rv.append([safeMarshal(x) for x in r[1:]])
    print rv
    return rv
    
    
def safeParse(e):
    try:
        return R.expr(e)
    except R.ParseError,x:
        s = x.args[0]
        if "ERROR:" in s: s = s[s.index("ERROR:")+6:]
        return s.replace("\n", " ")
    except:
        return str(sys.exc_info()[0])
    
def safeEval(x, e):
    if type(e)==str: return "###ERR### " + e
    try:
        return R.eval(x, e)[0]
    except Exception, ex:
        if ex.args:
            return "###ERR### " + str(ex.args[0])
        else:
            return "###ERR### " + str(ex)
    except:
        return "###ERR### " + str(sys.exc_info()[0])
    
def findAll(context, where, sort_by = None):
    if not R.ruleset_loaded(): raise Exception("Ruleset not loaded")
    cbag = R.context(context).bag()
    return [x.leg_identifier() for x in cbag.iterators.leg_set(where=where, sort_by=sort_by)]
    
def evalRave(context, items, raveExprs):
    if not R.ruleset_loaded(): raise Exception("Ruleset not loaded")
    if items:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        if type(items) == tuple: items = list(items)
        if type(items) != list: items = [items]
    else: #Selection
        area, items = getSelectionAndArea()[:20]
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    if not context:
        context = getSuitableContext(area)
    rv = []
    if not items: return rv
    
    # Option 1:
    for itm in items:
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(itm))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
        rv += findAllEval(R.selected(R.Level.atom()), None, raveExprs) #"leg_identifier="+str(itm)
    if not rv: return [items + [area]]#raise Exception("Selection failed")
    return rv
    # Option 2:
    
    # This is a prototype. Slow. Optimize if it is really needed
    #cond = ' or '.join([("leg_identifier = %s" % x) for x in items])
    #return findAllEval(context, cond, raveExprs)
    
# Converts the argument into something that can be sent over XML-RPC. Works with RelTime and AbsTime.
def safeMarshal(o):
    if type(o) == list: return [safeMarshal(x) for x in o]
    if type(o) == tuple: return tuple((safeMarshal(x) for x in o))
    if type(o) == AbsTime:
        dt = xmlrpclib.DateTime(time.mktime(datetime(*o.split()).timetuple()))
        return dt
    if type(o) == str: return unicode(o, 'latin1').encode('utf-8')
    if type(o) == RelTime:
        hh,mm = o.split()
        return float(hh*3600+mm*60)
    return o
    
__crc_compile_progress = {}

def compileRulesetStart(uuid, ruleset, *args):
    global __crc_compile_progress
    print "Starting compilation job: "+uuid
    xpnd = lambda st: os.path.expanduser(os.path.expandvars(st))
    cmd = [ xpnd('$CARMSYS/bin/crc_compile') ]
    error_file_folder = xpnd('$CARMTMP/compile')
    if not os.path.exists(error_file_folder):
        os.makedirs(error_file_folder)
    error_file = error_file_folder + "/" +uuid
    cmd.append("-xmlerror")
    cmd.append(error_file)
    cmd += args[0]
    rs = xpnd('$CARMUSR/crc/source/'+ruleset)
    cmd.append(rs)
    print "Running command " + str(cmd)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    __crc_compile_progress[uuid] = proc 
    
def compileRulesetReportProgress(uuid):
        # 0 = All done
        # 128 = Still running
        # 256 = All done, some error
    global __crc_compile_progress
    xpnd = lambda st: os.path.expanduser(os.path.expandvars(st))
    print "Checking job: "+uuid
    if not uuid in __crc_compile_progress:
        return (256, "Could not find process with id: "+uuid)
    print "1"
    print str(__crc_compile_progress[uuid])
    m = __crc_compile_progress[uuid].poll()
    print "m:" +str(m) + ":"+str(type(m))
    rc = __crc_compile_progress[uuid].returncode
    if rc == None and not os.path.exists('/proc/%d' % __crc_compile_progress[uuid].pid):
        print "Aha: Pid is not there anymore! Assume success"
        rc = 128
    print "rc:" +str(rc) + ":"+str(type(rc))
    if rc == None:
        return (128, "Still running")
    else:
        #stdout, stderr = __crc_compile_progress[uuid].communicate()
        stdout = __crc_compile_progress[uuid].stdout.read() or ''
        stderr = __crc_compile_progress[uuid].stderr.read() or ''
        error_file = xpnd('$CARMTMP/compile/'+uuid)
        if os.path.exists(error_file):
            xmlerr = file(error_file, 'r').read()
        else:
            xmlerr = ""
        if rc == 128:
            # This is a hack for when the returncode was lost. Assume there was an error
            # if stderr has some data.
            if stdout.find("Compiling... done.") < 0:
                rc = 256
            else:
                rc = 0
        print "Stdout=",stdout
        print "Stderr=",stderr
        return (rc, stdout, stderr, xmlerr)

def compileRulesetCancel(uuid):
    print "Canceling job: "+uuid
    if uuid in __crc_compile_progress:
        try:
            os.kill(__crc_compile_progress[uuid].pid, 15)
        except:
            pass # os.kill throws if pid is already dead
        del __crc_compile_progress[uuid]
    else:
        print "Job not found in dict "+uuid
        
def reloadRuleset(rulesetName=None):
    """Reload ruleset and refresh GUI."""
    try:
        import carmensystems.studio.rave.Ruleset as Ruleset
    except ImportError:
        msg = R.eval("rule_set_name")[0]
        if rulesetName:
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, rulesetName)
        else:
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, msg)
        return msg
    msg = Ruleset.reload(rulesetName)
    Gui.GuiCallListener(Gui.RefreshListener, "rulesetReloaded")
    return msg


def raveExplore(uuid, type, module, variable, rule, expression):
    print "Exploring ",type,module,variable,rule,expression
    if not R.ruleset_loaded(): raise Exception("Ruleset not loaded")
    area, items = getSelectionAndArea()[:20]
    rv = []
    if not items:
        return rv

    xpnd = lambda st: os.path.expanduser(os.path.expandvars(st))
    folder = xpnd('$CARMTMP/RaveX')
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for itm in items[:8]: # Max 5 items
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, str(itm))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
        file = folder + "/" + uuid + "_" + str(itm).replace('-','_')
        xml = ''
        status = -1
        try:
            _raveExplore(area, file, type, module, expression, rule, variable)
            f = open(file, 'r')
            xml = f.read()
            f.close()
            status = 0
        finally:
            if os.path.exists(file):
                print "File exists "+file
                os.unlink(file)
            rv.append((status, xml))
    return rv

def _raveExplore(area, file, type, module, expression, rule, variable):
    print "Writing to file: "+file

    b0 = {'FORM': 'RaveExplorer',
        'EXPLORE_TYPE':type,
        'ONE_ALL': 'One'}

    if os.environ['CarmReleaseMajor']=="16" or os.environ['CarmReleaseMajor'] =="CMS2"	:
        b0['ONE_ALL'] = "Current"

    if type=="Rule":
        b0['VARIABLE_MODULE'] = module
        b0['RULE_NAME'] = rule
    elif type=="Expression":
        b0['EXPRESSION'] = expression
    elif type=="Variable":
        b0['VARIABLE_MODULE'] = module
        b0['VARIABLE_NAME'] = variable
    else:
        raise Exception("Error type, must be Variable/Rule/Expression")

    b2 = {
        "ID" : "",
        "TYPE" : "NOTICE",
        "button" : Localization.MSGR("OK")
    }

    print str(b0)
    print str(b2)

    try:
        Cui.CuiCrcExploreRuleValues(b0, Cui.gpc_info,area,file,0)
    except:
        Cui.CuiBypassWrapper("CuiProcessInteraction",Cui.CuiProcessInteraction,(b2, "NOTICE", ""))
        try:
            Cui.CuiCrcExploreRuleValues(b0,Cui.gpc_info,area,file,32)
        except:
            Cui.CuiBypassWrapper("CuiProcessInteraction",Cui.CuiProcessInteraction,(b2, "NOTICE", ""))
            print "ERROR trying with const!"
            raise Exception("Error getting data")

def listDirectory(path):
    path = os.path.expandvars(os.path.expanduser(path))
    rv = []
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        size = -1
        linkto = ''
        type = 0
        if os.path.islink(fp):
            try:
                linkto = os.readlink(fp)
            except:
                linkto = ''
            if os.path.isdir(os.path.realpath(fp)):
                type = 1
            else:
                type = 2
        elif os.path.isdir(fp):
            type = 1
        elif not os.path.isfile(fp):
            type = 3
        else:
            size = os.path.getsize(fp)
        rv.append([f, type, size, linkto])
    return rv
    
def getFileContents(path, offset=0, length=-1):
    path = os.path.expandvars(os.path.expanduser(path))
    f = file(path, "rb")
    if offset > 0:
        f.seek(offset)
    r = f.read(length)
    f.close()
    return xmlrpclib.Binary(r)
    
def getFileHashes(paths):
    import md5
    if type(paths) is str:
        paths = [paths]
        
    rv = []
    for path1 in paths:
        path = os.path.expandvars(os.path.expanduser(path1))
        f = file(path, "rb")
        m = md5.new()
        l = f.readline()
        while l:
            m.update(l)
            l = f.readline()
        f.close()
        rv.append(xmlrpclib.Binary(m.digest()))
    return rv

def listTables():
    from  modelserver import TableManager
    t = TableManager.instance()
    return t.tableNames()

def getSchema(table):
    from  modelserver import TableManager
    t = TableManager.instance()
    tab = t.table(table)
    d = tab.entityDesc()
    return str(d.keysize()) + " " + str(d.size()) + " " + str(tab.isLoaded())
    
def getTableData(table, filter):
    from  modelserver import TableManager
    t = TableManager.instance()
    tab = t.table(table)
    if not tab.isLoaded(): raise Exception("Table not loaded")
    return xmlrpclib.Binary(tab.toXML())
    
def putFile(dest, data, replace, uncompress):
    dest = os.path.expandvars(os.path.expanduser(dest))
    if not replace and os.path.exists(dest):
        raise Exception("Target file exists")
    destDir = os.path.dirname(dest)
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    f = file(dest, "wb")
    if isinstance(data, xmlrpclib.Binary):
        data = data.data
    f.write(data)
    f.close()
    if uncompress:
        fileType, _ = subprocess.Popen("file -bi '%s'" % dest, shell=True, stdout=subprocess.PIPE).communicate()
        fileType = fileType.strip()
        ocwd = os.getcwd()
        os.chdir(destDir)
        try:
            if not fileType or fileType == "application/x-zip":
                os.system("unzip -o '%s'" % dest)
                os.unlink(dest)
            elif fileType == "application/x-gzip":
                fileType, _ = subprocess.Popen("file -zbi '%s'" % dest, shell=True, stdout=subprocess.PIPE).communicate()
                if fileType and "application/x-tar" in fileType:
                    os.system("tar -zxf '%s'" % dest)
                    os.unlink(dest)
                else:
                    os.system("gzip -d '%s'" % dest)
            else:
                raise Exception("Unknown compressed format '%s'" % fileType)
        finally:
            os.chdir(ocwd)
            
def invokePythonCode(dest, data, uncompress, subDir, module, code):
    delete = False
    if not dest:
        delete = True
        dest = tempfile.mkdtemp(prefix='py_')
    pypath = sys.path[:]
    rv = None
    try:
        destFile = dest
        if delete:
            if uncompress:
                destFile = os.path.join(dest,'python.zip')
            else:
                destFile = os.path.join(dest,'%s.py' % module)
        else:
            dest = os.path.dirname(destFile)
        putFile(destFile, data, True, uncompress)
        if subDir and uncompress:
            sys.path = [os.path.join(dest, subDir)] + sys.path
        else:
            sys.path = [dest] + sys.path
        if module:
            if module in sys.modules:
                del sys.modules[module]
            evalPythonString("import %s; print %s" % (module, module))
        rv = evalPythonString(code)
        os.system("ls %s" % dest)
    finally:
        sys.path = pypath
        if delete:
            if os.path.exists(dest):
                print "Removing %s" % dest
                if uncompress:
                    shutil.rmtree(dest)
                else:
                    os.unlink(destFile)
        print sys.path
    return rv
            
def invokeDebugger(rhost, rport, debugClientData, suspend, code):
    pydevd_modules = filter(lambda x : x.startswith('pydevd'), sys.modules)
    for pydevd_module in pydevd_modules:
        del sys.modules[pydevd_module]

    rport = int(rport)
    if not debugClientData:
        import pydevd
        pydevd.settrace(host=rhost, port=rport, suspend=suspend)
    else:
        dest = os.path.expandvars(os.path.expanduser('$CARMTMP/pydev/%s.%d/' % (rhost, rport)))
        invokePythonCode('%s/pydevd.zip' % dest, debugClientData, True, "pysrc", "pydevd", "pydevd.settrace(host='%s', port=%d, suspend=%s)" % (rhost, rport, suspend))
    return evalPythonString(code)
    
def _registerFunction(func):
    XD.xmlrpc_registerfunction(func, 'RaveServer.' + func.__name__)
    
_registerFunction(cmdline)
_registerFunction(evalPython)
_registerFunction(evalPythonString)
_registerFunction(evalRave)
_registerFunction(findAll)
_registerFunction(findAllEval)
_registerFunction(getSelection)
_registerFunction(getMode)
_registerFunction(compileRulesetStart)
_registerFunction(compileRulesetReportProgress)
_registerFunction(compileRulesetCancel)
_registerFunction(reloadRuleset)
_registerFunction(raveExplore)
_registerFunction(listDirectory)
_registerFunction(getFileContents)
_registerFunction(getFileHashes)
_registerFunction(listTables)
_registerFunction(getSchema)
_registerFunction(getTableData)
_registerFunction(getReportServerPublishType)
_registerFunction(putFile)
_registerFunction(invokePythonCode)
_registerFunction(invokeDebugger)

if len(sys.argv) > 1 and sys.argv[1] == "UI":

    import Gui
    msg = "RPC server URI:\n%s : %s" % (getfqdn(), WS.get_port_number(6705))
    Gui.GuiMessage(msg)
