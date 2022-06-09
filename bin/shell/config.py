from jinja2 import Template, FileSystemLoader, Environment
import re, os, urlparse

from utils import ServiceConfig
__C = None
def _C():
	global __C
	if __C == None: __C = ServiceConfig.ServiceConfig()
	return __C

TEMPLATE_DIR = os.path.join(os.path.expandvars("$CARMUSR/data/monitoring/templates"))
CARMUSR_DIR = os.path.expandvars("$CARMUSR")
CARMUSR_TEMP_DIR = os.path.expandvars("$CARMTMP")
CARMUSR_CHECKS_DIR = os.path.expandvars("$CARMUSR/bin/testing/monitors")
CARMUSR_LOG_DIR = os.path.expandvars("$LOG_DIR")
PUBLISH_LOG_DIR = os.path.expandvars("/var/carmtmp/logfiles")
LATEST_LOG_DIR = os.path.expandvars("/var/carmtmp/logfiles")
PYTHON_INTERPRETER = "python26"

TEMPLATE_MAIN = 'base'
DEFAULT_OUTPUT_FILE = 'cms2-nagios.cfg'
SYSTEM_NAME=os.environ["CARMSYSTEMNAME"]

def _renderConfig(hosts, services, filename):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    t = env.get_template(TEMPLATE_MAIN)
    
    t.stream(
        hosts=hosts,
        services=services,
        carmusr_dir=CARMUSR_DIR,
        carmusr_temp_dir=CARMUSR_TEMP_DIR,
        carmusr_checks_path=CARMUSR_CHECKS_DIR,
        carmusr_log_dir=CARMUSR_LOG_DIR,
        publish_log_dir=PUBLISH_LOG_DIR,
        latest_log_dir=LATEST_LOG_DIR,
        python_interpreter=PYTHON_INTERPRETER
        ).dump(filename, encoding='utf-8')

def _getHosts():
    hosts = []
    
    #reading host config
    for n, _ in _C().getProperties("hosts/host"):
        node = n.split('/')[-1]
        host = _C().getProperty("hosts/%s@hostname" % node)[1]
        if node != "passive_node":
            hosts.append({'name':"%s_%s" % (node, SYSTEM_NAME),
                          'hostname':host,
                          'services':[]})

    #adding database node
    hosts.append({'name': "db_node_%s" % (SYSTEM_NAME),
                  'hostname': _C().getProperty("db/host")[1],
                  'services':[]})

    return hosts

def _getServices():
    #reading service config

    services = []

    for service in _C().getServices():
        srv = {}
        srv['name'] = "%s_%s" %(service[0], SYSTEM_NAME)
        srv['process'] = service[1]
        srv['node'] = "%s_%s" % (service[2], SYSTEM_NAME)
        srv['url'] = service[3]

        u = urlparse.urlparse(service[3])
        srv['url_path'] = u.path
        srv['url_scheme'] = u.scheme
        srv['url_hostname'] = u.hostname
        srv['url_port'] = u.port
        if u.scheme == 'oracle':
            # Handling case 2 clustered db hosts and stripping the second one
            srv['url_schema'] = u.path.split('/')[0]
            multiple_host_matcher = re.compile(r'@(.+)\%(.+)\/')
            host_match = multiple_host_matcher.search(srv['url'])
            if host_match:
                srv['url'] = re.sub(r'%.+\/', '/', srv['url'])
        services.append(srv)
    return services
    

def generatemonitorconfig(filename=DEFAULT_OUTPUT_FILE):
    "Generate a nagios configuration file"
    
    hosts = _getHosts()
    services = _getServices()
    
    _renderConfig(hosts=hosts, services=services, filename=filename)
    print "Configuration file written to '%s'" % (filename)
