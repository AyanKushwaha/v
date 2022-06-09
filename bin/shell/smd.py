import subprocess
import os,sys
from utils import ServiceConfig
__C = None
def _C():
    global __C
    if __C == None: __C = ServiceConfig.ServiceConfig()
    return __C

_conn = None
def _SQL(sql):
    from carmensystems.dig.framework.dave import DaveConnector
    global _conn
    if _conn is None:
        _conn = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    l1conn = _conn.getL1Connection()
    l1conn.rquery(sql, None)
    r = []
    try:
        while True:
            l = l1conn.readRow()
            if not l: return r
            r.append(l.valuesAsList())
    finally:
        l1conn.endQuery()
        _conn.close()
        _conn = None

def hosts():
    "Displays a list with information on all configured sysmond nodes"
    for n, _ in _C().getProperties("hosts/host"):
        node = n.split('/')[-1]
        host = _C().getProperty("hosts/%s@hostname" % node)[1]
        print "  %s => %s" % (node, host)
def nodes():
    "Displays a list of all configured sysmond nodes"
    for n, _ in _C().getProperties("hosts/host"):
        node = n.split('/')[-1]
        print node
def host(host=None, display="processes"):
    "Displays processes for a given host or node (default is current host)"
    if not host:
        host = os.environ["HOSTNAME"]
    if display == "processes":
        for n, _ in _C().getProperties("hosts/host"):
            nodename = n.split("/")[-1]
            hostname = _C().getProperty("%s@hostname" % n)[1]
            if not hostname:
                hostname = "(not set)"
            if host in (nodename, hostname):
                l =[x[1] for x in _C().getProperties("%s/start" % n)]
                if len(l) > 0:
                    print '\n'.join(l)
                else:
                    print >>sys.stderr, "No processes/groups defined for node"
    elif display in ("node","host"):
        for n, _ in _C().getProperties("hosts/host"):
            nodename = n.split("/")[-1]
            hostname = _C().getProperty("%s@hostname" % n)[1]
            if not hostname:
                hostname = "(not set)"
            if host in (nodename, hostname):
                if display == "node":
                    print nodename
                else:
                    print hostname
                return
    else:
        print >>sys.stderr, "Display must be one of {processes|node|host}"

def _execute_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def _split_service_string(key, line, start_pos):
    if key == 'service':
        delimiter = '/'
    elif key == 'process':
        delimiter = '@'
    elif key == 'node':
        delimiter = ' ='
    elif key == 'url':
        delimiter = '= '
    end_pos = line.find(delimiter, start_pos)
    if end_pos < start_pos:
        end_pos = len(line)
    line = line[start_pos:end_pos]
    
    return line.lstrip().rstrip(), end_pos + len(delimiter)
    
def _getServices():
    output = _execute_cmd(['xmlconfig', '--srv'])
    srv = []
    for line in iter(output.splitlines()):
        start_pos = 0
        service, start_pos = _split_service_string('service', line, start_pos)
        process, start_pos = _split_service_string('process', line, start_pos)
        node, start_pos = _split_service_string('node', line, start_pos)
        url, start_pos = _split_service_string('url', line, start_pos)
        srv.append((service, process, node, url))
    return srv

def services(node=None):
    "Displays a list of configured services, specify a node name to only display services on the given node"
    srv = _getServices()
    ms = [max([len(y[x])] for y in srv)[0] for x in range(4)]
    fmt = "%%-%ds %%-%ds %%-%ds %%-%ds" % tuple(ms)
    print fmt % ("Service", "Process", "Node", "URL")
    print '-'*(sum(ms)+3)
    if node:
        srv = [x for x in srv if x[2] == node]
    for s in sorted(srv, key=lambda x:(x[2],x[0])): print fmt % s

def startall():
    "Starts Sysmond on all configured nodes. Use instead of sysmondctl due to its limitation."
    for srv,proc,node,uri in _getServices():
        if srv.startswith('sysmond'):
            host = uri.split('//')[1].split(':')[0]
            print "Starting",srv,"on",host
            os.system("ssh -nTt '%s' '%s/bin/cmsshell' sysmondctl start" % (host, os.environ["CARMUSR"]))

def stopall():
    "Stops Sysmond on all running nodes. Equivalent of sysmondctl exit node=system"
    os.system("sysmondctl exit node=system")

def programs():
    for prog,_ in sorted(_C().getProperties("program")):
        print prog.split('/')[-1]
        
def nodeof(process):
    "Prints the node(s) which starts a process or group"
    v = []
    groups = []
    for prop,val in _C().getProperties("process_group/start"):
        if val == process:
            groups.append(prop.split('/')[-2])
    for prop,val in _C().getProperties("host/start"):
        if val == process:
            v.append(prop.split('/')[-2])
        if val in groups:
            v.append("%s (via %s)" % (prop.split('/')[-2], val))
    return ','.join(v)
        
def processes(program=None):
    """Lists processes with programs, specify a process name to show only this process"""
    xs = ''
    if not program: xs = '  '
    for prog,_ in sorted(_C().getProperties("program")):
        p = prog.split('/')[-1]
        if not program or p == program:
            if not program: print p 
            print xs+('\n'+xs).join([x[0].split('/')[-1] for x in _C().getProperties("%s/process" % prog)])
            
def groups(group=None):
    "Lists process groups"
    xs = ''
    if not group: xs = '  '
    for grp,_ in sorted(_C().getProperties("process_group")):
        p = grp.split('/')[-3]
        g = grp.split('/')[-1]
        if not group or p == group:
            if not group: print "%s (%s)" % (g, p)
            print xs+('\n'+xs).join([x[1] for x in _C().getProperties("%s/start" % grp)])
            
def statuscheck():
    "Performs a status check on known services"   
    for srv,proc,node,uri in _getServices():
        sys.stdout.write("%-26s" % srv)
        sys.stdout.flush()
        if uri.startswith('oracle:'):
            try:
                print _SQL("SELECT 'OK - SQL' FROM dual")[0][0]
            except:
                print "FAILURE"
        elif 'sysmond_' in srv and uri.startswith('http:'):
            host,port = uri[7:].split('/')[0].split(':')
            os.system("$CARMUSR/bin/testing/monitors/check_sysmond.py -H %s -p %s" % (host,port))
        elif 'time' in srv and uri.startswith('http:'):
            os.system("timeserver get")
        elif uri.startswith('http:') and uri.endswith('RPC2') and not '_custom' in srv:
            os.system("$CARMUSR/bin/testing/monitors/check_eval_python.py -u '%s'" % uri)
        else:
            print "(not checked)"

def checkintest(crew=None):
    "Tests crew portal checkin functionality for a specified crew or an automatically selected crew"
    portal = "portal_publish"
    uri = _C().getServiceUrl(portal)
    crewspec = ""
    if crew: crewspec = " -c '%s'" % crew
    os.system("$CARMUSR/bin/testing/monitors/check_check_in.py %s -u '%s'" % (crewspec, uri))

