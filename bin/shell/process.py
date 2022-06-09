from xmlrpclib import ServerProxy
from utils import ServiceConfig
import os, sys
__C = None
def _C():
	global __C
	if __C == None: __C = ServiceConfig.ServiceConfig()
	return __C

def _carmweb():
    url = _C().getServiceUrl("carmweb")
    if not url:
        print >>sys.stderr, "carmweb service not defined"
        sys.exit(1)
    return ServerProxy("%s/RPC2" % url)
        
def _list_():
    print _carmweb().processmgr.listRunningProcesses()

def start(process):
    print _carmweb().processmgr.startProcess(process)