'''
The carmweb server
'''
from twisted.web import server, resource, xmlrpc, http, resource, static
from twisted.web import xmlrpc
from twisted.internet import reactor
from twisted.python import log
from carmensystems.common.ServiceConfig import ServiceConfig
import sys,os
from time import strftime
utilspath = os.path.expandvars("$CARMUSR/lib/python/utils")
if not utilspath in sys.path: sys.path.append(utilspath)
from jinja2 import Template

os.environ["CARMWEB_DEBUG"] = "1"
 
class XmlRpc(xmlrpc.XMLRPC):
    def _getFunction(self, functionPath):
        lf = functionPath.split('.',1)
        if len(lf) < 2:
            raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "Expected module.function")
        module,func = lf
        if not module:
            module = 'root'
        if module in ('server', '__init__') or '.' in module or '\n' in module:
            raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "Bad module")
        if not func:
            raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "Bad module")
        try:
            M = __import__("carmweb_%s" % module)
            if os.environ.get("CARMWEB_DEBUG",""):
                reload(M)
        except ImportError:
            raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "Module '%s' not found" % module)
        
        if hasattr(M, func):
            f = getattr(M, func)
            print f
            if not hasattr(f, '__xmlrpc'):
                raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "'%s' is not a valid XMLRPC function in %s" % (func, module))
            return f
        else:
            raise xmlrpc.NoSuchFunction(self.NOT_FOUND, "'%s' is not a XMLRPC function in %s" % (func, module))
 
class WebPages(resource.Resource):
    def getChild(self, name, request):
        if name in ('RPC2','static'):
            return Resource.getChild(self, name, request)
        if ".." in name: return None
        return self
    def render_GET(self, request):
        module = request.prepath[0]
        if not module:
            module = 'root'
        if module in ('server', '__init__') or '.' in module or '\n' in module:
            return "Bad module"
        try:
            M = __import__("carmweb_%s" % module)
            if os.environ.get("CARMWEB_DEBUG",""):
                reload(M)
        except ImportError:
            return "Module '%s' not found" % module
        if hasattr(M, '__HTTP_GET__'):
            return M.__HTTP_GET__(request)
        else:
            cmd = None
            if len(request.prepath) > 1:
                cmd = request.prepath[1]
            if not cmd:
                if not hasattr(M, '__root__'):
                    return "Module '%s' has no root" % (module,)
                else:
                    return M.__root__(request)
            else:
                if hasattr(M, cmd):
                    f = getattr(M, cmd)
                    if hasattr(f, '__web'):
                        return f(request)
                return "Module '%s' does not support %s" % (module, cmd)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        progname = sys.argv[1]
        if "$" in progname: progname = os.path.expandvars(progname)
        
    else:
        progname = "carmweb"
    os.environ["CARMWEB"] = progname
    C = ServiceConfig()
    proc = C.getProperty("programs/*/%s")[0]
    svc = None
    if proc:
        svc = C.getProperty("%s/service" % proc)[0]
        proc = proc.split("/")
    else:
        proc = []
    if not svc: svc = "carmweb"
    port = None
    try:
        port = int(C.getServicePort(svc))
    except:
        print "Unable to get port, using default 8080"
    if not port:
        port = 8080
    import socket
    os.environ["CARMWEB_URI"] = "http://%s:%d/RPC2" % (socket.getfqdn(), port)
    pth = None
    nm = None
    while (not pth or not nm) and len(proc) > 0:
        ps = '/'.join(proc)
        if not pth: pth = C.getProperty("%s/log_dir" % '/'.join(proc))[1]
        if not nm: nm = C.getProperty("%s/log_name" % '/'.join(proc))[1]
        del proc[-1]
    
    if not pth:
        pth = os.path.expandvars("$CARMTMP")
    if nm:
        if '$' in nm: nm = os.path.expandvars(nm)
    else:
        nm = strftime(os.path.expandvars("CW.$USER.$HOST.%Y%m%d.%H%M.log"))
        
    if not os.path.exists(pth):
        os.makedirs(pth)
    os.environ["LOGDIR"] = pth
    fn = os.path.join(pth, nm)
    print "Start logging to",fn
    log.startLogging(sys.stdout)
    print "Program is",progname
    root = WebPages()
    root.putChild('RPC2', XmlRpc())
    root.putChild('static', static.File(os.path.expandvars("$CARMUSR/data/web/static")))
    reactor.listenTCP(port, server.Site(root))
    reactor.run()
