import sys
import os
import imp
import tempfile
fileName = ''    

def generate(report, filename, format, args):
    """
    Substitute for carmensystems.publisher.api, that generates the report
    to a metafile on disk.
    """
    fd = -1
    if not filename:
        filename = fileName
        if not filename:
            fd, filename = tempfile.mkstemp('.xml', os.path.basename(report))
    print "Generating to", filename
    import carmensystems.publisher.api
    #import __main__
    om = sys.modules["carmensystems.publisher.api"]
    R = None
    pth = sys.path[:]
    try:
        hook = _prtmf()
        sys.modules["carmensystems.publisher.api"] = hook
        sys.modules["carmensystems.publisher"].api = hook
        #sys.modules['__main__'] = ''
        import report_sources.include.SASReport
        reload(report_sources.include.SASReport)
        if ".py" in report:
            rname, rtit, report = _resolve(report)
            if report[-4:] == '.pyc':
                report = "%s.py" % (report[:-4])
            print "Y",report
            print "Importing",rtit
            print (rtit, report)
            R = imp.load_source(rtit, report)
        else:
            R = __import__(report)
            for md in report.split('.')[1:]:
                R = getattr(R, md)
            rtit = report.split('.')[-1]
        print R
        reload(R)
        md1 = None
        md2 = None
        for d in dir(R):
            o = getattr(R, d)
            if d == rtit:
                print "Report class is", d
                md1 = o
                print md1
            elif d == 'Report':
                md2 = o
                
        if md2 and not md1: md1 = md2
        print "Done"
        print md1
        rep = md1()
        b = type(rep)
        s = ""
        while b:
            s += "   "
            print s + str(b)
            b = b.__base__
        if isinstance(args, dict):
            for k in args:
                rep._args[k] = args[k]
        else:
            for a in args.split(' '):
                b = a.split('=')
                print b
                rep._args[b[0]] = b[1]
        rep.create()
        if fd > 0:
            f = os.fdopen(fd)
        else:
            f = file(filename, 'w')
        rep._write(f,1-1)
        f.close()
        print "Wrote report to",filename
    finally:
        sys.modules["carmensystems.publisher.api"] = om
        sys.modules["carmensystems.publisher"].api = om
        print sys.modules["carmensystems.publisher.api"]
        reload(report_sources.include.SASReport)
        if R: reload(R)
        
def _resolve(report):
    rname = report
    rtit,_ = os.path.splitext(os.path.basename(rname))
    for i in range(2):
        if not '/' in rname:
            p = ['$CARMUSR/lib/python/report_sources/hidden', '$CARMUSR/lib/python/report_sources/include']
            report = os.path.join(p[i],rname)
        elif not '$' in report:
            p = ['$CARMUSR/lib/python/report_sources', '$CARMUSR/lib']
            report = os.path.join(p[i],rname)
        print "X",report
        report = os.path.expandvars(report)
        if os.path.isfile(report): break
    return (rname, rtit, report)
    
def patch(oldmodname, newmod):
    for mod in sys.modules.values():
        if hasattr(mod, '__file__') and '.py' in mod.__file__:
            #print "Patching",mod
            for d in dir(mod):
                o = getattr(mod, d)
                if d == 'P':
                    print "P=",o
                #print "   >>  ",d,o
                if d == 'P':
                    print "P!!"
                    print o.__name__
                if str(type(o)) == "<type 'module'>" and hasattr(o,'__name__'):
                    #print "Module",o
                    if o == oldmodname or o.__name__ == oldmodname:
                        print 'Hooking',oldmodname,'with',newmod
                        #setattr(mod,d,newmod)
    
def _prtmf():
    pth = os.path.dirname(__file__)
    if not pth in sys.path:
        sys.path.append(pth)
    import prtmf
    reload(prtmf)
    return prtmf
    
