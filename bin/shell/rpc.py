import sys
import os.path
import datetime
import readline
import xmlrpclib
import traceback
import time
import random
import zipfile
from utils import etree
from xml.dom import minidom
from utils.ServiceConfig import ServiceConfig
from StringIO import StringIO

def _RPC(uri):
    import httplib,xmlrpclib
    class htconn(httplib.HTTPConnection):
        def connect(self):
            httplib.HTTPConnection.connect(self)
            self.sock.settimeout(600)
    class http(httplib.HTTP):
        _connection_class = htconn
    class tpt(xmlrpclib.Transport):
        def make_connection(self, host):
            return http(host)
    t = tpt()
    s = xmlrpclib.ServerProxy(uri, transport=t)
    return s

def _getrpc(host):
    if host[:5] == "http:":
        return host[7:].split('/')[0],_RPC(host)
    if ':' in host:
        return host,_RPC("http://%s/RPC2" % host)

    config = ServiceConfig()
    for (service, _, _, url) in config.getServices():
        if service == host:
            return host,_RPC(url)

    print >>sys.stderr, "Invalid RPC host '%s', try host:port"%host
    sys.exit(1)

def console(host):
    h,rpc = _getrpc(host)
    from xmlrpclib import Fault
    try:
        while True:
            s = raw_input("%s >>> " % h)
            try:
                print rpc.RaveServer.evalPythonString(s)
            except Fault,f:
                print >>sys.stderr, f.faultString
    except EOFError:
        print
        return

def python(host, code):
    "Evaluate a single Python statement"
    h,rpc = _getrpc(host)
    if code == '-':
        print rpc.RaveServer.evalPythonCode(sys.stdin.read())
    else:
        print rpc.RaveServer.evalPythonString(code)

def list_functions(host):
    h,rpc = _getrpc(host)
    return sorted(rpc.xmlrpc_listfunctions())

def list_functions_named_like(host, named_like):
    return [ fn for fn in list_functions(host) if named_like in fn.lower() ]

def report(host, report=None, **args):
    "Run a reportWorker report"
    h,rpc = _getrpc(host)
    server_args = None
    if report is None:
        while True:
            s = raw_input("Report args %s >>>" % h)
            try:
                args = eval(s)
                if isinstance(args, tuple):
                    server_args, args = args
                if 'report' in args:
                    report = args['report']
                    del args['report']
                    break
                else:
                    print >>sys.stderr, "'report' arg missing"
            except:
                print >>sys.stderr, "Unable to parse args"
    if server_args is None:
        server_args = {}
        for arg in ('delta','reload'):
            if arg in args:
                server_args[arg] = args[arg]
                del server_args[arg]
    print rpc.generate(server_args, report, args)

def version(host="portal_latest"):
    h,rpc = _getrpc(host)
    print rpc.version()

def toggle_call_log(host="portal_latest"):
    h,rpc = _getrpc(host)
    return "Call log: %s"%rpc.toggle_call_log()

def toggle_profiling(host="portal_latest"):
    h,rpc = _getrpc(host)
    return "Profiling: %s"%rpc.toggle_profiling()

def get_rosters(crewid, host="portal_latest"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.get_rosters,
                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getRosterParameters biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"/>'%locals())
#                           req_xsd=_bid_xsd("getroster.xsd"),
#                           resp_xsd=_bid_xsd("getroster.xsd"))

def get_all_trips(host="portal_latest"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.get_all_trips,
                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns:getAllTripsParameters xmlns:ns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips"/>')


def test1(port="11002"):
    print python(
        "localhost:" + port,
        """
from interbids.rostering.days_off_response_handler import create_days_off
handler = create_days_off('10123', 'FW', '2016-03-06 00:00', '2016-06-06 00:00', '2016-03-06', 1)
print "  ## handler:", handler
print "  ## dir(handler):", dir(handler)
#print "  ## dir(status):", dir(handler.get_status())
print "  ## status:   ", handler.get_status().text
print "  ## errors:   ", handler.get_errors().text

""")


def get_available_days_off(crewid, time_start=None, time_end=None, category="FS", host="portal_latest"):
    h,rpc = _getrpc(host)
    if time_start is None:
        time_start = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()
    if time_end is None:
        time_end = (datetime.date.today() + datetime.timedelta(days=60+360)).isoformat()

    req = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
             <ns4:availableDaysOffParameters id="id" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" category="%(category)s"
                       xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import"
                       xmlns:ns4="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication"
                       xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip">
                <ns4:interval>
                   <ns3:from>%(time_start)s</ns3:from>
                   <ns3:to>%(time_end)s</ns3:to>
                </ns4:interval>
             </ns4:availableDaysOffParameters>'''%locals()
    return _call_xml_xmlrpc(rpc.get_rosters,
                           req)
#                           ,req_xsd=_bid_xsd("request.xsd"),
#                           resp_xsd=_bid_xsd("request.xsd"))

def create_request(crewid, date=None, nr_of_days=1, type="A_FS", host="portal_latest"):
    h,rpc = _getrpc(host)
    if date is None:
        date = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()
    period_start = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()
    period_end = (datetime.date.today() + datetime.timedelta(days=420)).isoformat()

    req = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
             <ns7:requestParameters type="%(type)s" category="A_%(type)s" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="id"
                  xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common"
                  xmlns:ns7="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"
                  xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication">
             <ns7:period>
                 <ns6:from>%(period_start)s</ns6:from>
                 <ns6:to>%(period_end)s</ns6:to>
             </ns7:period>
             <ns7:attributes>
                 <attribute name="startDate" value="%(date)s"/>
                 <attribute name="start" value="%(date)s 00:00"/>
                 <attribute name="nr_of_days" value="%(nr_of_days)s"/>
             </ns7:attributes>
             </ns7:requestParameters>'''%locals()

    return _call_xml_xmlrpc(rpc.create_request,
                           req)
#                           req_xsd=_bid_xsd("request.xsd"),
#                           resp_xsd=_bid_xsd("request.xsd"))


def jmp_crew_init(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_crew_init,
                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><crewInitRequest awardingCategory="LEAVE" awardingType="ANNUAL_LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2"/>'%locals())
#                           req_xsd=_leave_bid_xsd("jmpCommunication.xsd"),
#                           resp_xsd=_leave_bid_xsd("jmpCommunication.xsd"))

# Depricated method?
#def jmp_crew_group(crewid, host="portal_manpower_f"):
#    h,rpc = _getrpc(host)
#    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.leave.jmp_crew_group,
#                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><crewGroupRequest biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/leave"/>'%locals())
#                           req_xsd=_leave_bid_xsd("jmpCommunication.xsd"),
#                           resp_xsd=_leave_bid_xsd("jmpCommunication.xsd"))

# Depricated method?
#def jmp_assignments(crewid, host="portal_manpower_f"):
#    h,rpc = _getrpc(host)
#    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.leave.jmp_assignments,
#                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getRosterParameters biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"/>'%locals())
#                           req_xsd=_leave_bid_xsd("getroster.xsd"),
#                           resp_xsd=_leave_bid_xsd("getroster.xsd"))

def jmp_get_assignments(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_get_assignments,
                           '<?xml version="1.0" encoding = "UTF-8"?><getAssignmentsRequest authenticatedCrewId="automatic" biddingCrewId="%(crewid)s" id="automatic" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2" />'%locals())
#                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getRosterParameters biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"/>'%locals())
#                           req_xsd=_leave_bid_xsd("getroster.xsd"),
#                           resp_xsd=_leave_bid_xsd("getroster.xsd"))

def jmp_type_based_routing_info(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_type_based_routing_info,
                            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getTypeBasedRoutingInfoRequest awardingCategory="LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2"/>'%(locals()))
                           #'<?xml version="1.0" encoding = "UTF-8"?><getAssignmentsRequest authenticatedCrewId="automatic" biddingCrewId="%(crewid)s" id="automatic" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2" />'%locals())
#                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getRosterParameters biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"/>'%locals())
#                           req_xsd=_leave_bid_xsd("getroster.xsd"),
#                           resp_xsd=_leave_bid_xsd("getroster.xsd"))

def jmp_get_bid_list(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_get_bid_list,
                            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getBidListRequest awardingCategory="LEAVE" awardingType="ANNUAL_LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2" />'%(locals()))

def jmp_get_bid(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    req = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <getBidRequest awardingCategory="LEAVE" awardingType="ANNUAL_LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2">
                    <key type="VACATION" id="1" bidGroupId="VACATION"/>
                </getBidRequest>'''%(locals())
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_get_bid, req)



def jmp_create_bid(crewid, host="portal_manpower_f"):
    h,rpc = _getrpc(host)
    start_date = 6+random.randint(-2,2)
    end_date = 13+random.randint(-2,2)
    req = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?> 
                            <createBidRequest awardingCategory="LEAVE" awardingType="ANNUAL_LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2"> 
                                <overrideWarnings>false</overrideWarnings> 
                                <createBidData xsi:type="UpdateBidData" id="-1" prio="-1" bidGroupId="VACATION" type="VACATION" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
                                    <alternative index="1"> 
                                    <entry name="start">2020-02-0%(start_date)s 00:00</entry> 
                                    <entry name="end">2020-02-%(end_date)s 23:59</entry>
                                    </alternative> 
                                </createBidData> 
                            </createBidRequest>'''%(locals())
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_create_bid, req)

def jmp_delete_bid(crewid, host="portal_manpower_f", id=1):
    h,rpc = _getrpc(host)
    req = '''<?xml version="1.0" encoding = "UTF-8" standalone = "yes"?>
                <deleteBidRequest awardingCategory="LEAVE" awardingType="ANNUAL_LEAVE" biddingCrewId="%(crewid)s" authenticatedCrewId="%(crewid)s" id="testid" xmlns = "http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2"> 
                    <key type="VACATION" id="%(id)s" bidGroupId="VACATION"/>
                </deleteBidRequest>'''%(locals())
    return _call_xml_xmlrpc(rpc.carmensystems.manpower.bids.jmp_delete_bid, req)



def _leave_bid_xsd(name):
    return os.path.expandvars("$CARMUSR/current_carmsys_cmp/data/manpower/xsd/bids/" + name)

def _bid_xsd(name):
    ib_sys = os.path.expandvars("$CARMUSR/current_carmsys_bid")
    ib_zip_file = ib_sys + "/" + [x for x in os.listdir(ib_sys) if x.startswith("interbids-release-")][0]
    ib_file = zipfile.ZipFile(ib_zip_file, "r")
    backend_facade_name = [x for x in ib_file.namelist() if "backend-facade-" in x][0]
    backend_facade_file = zipfile.ZipFile(StringIO(ib_file.read(backend_facade_name)), "r")
    backend_facade_file.extractall(os.path.expandvars("$CARMTMP/cmsshell/rpc"),
                                                      [x for x in backend_facade_file.namelist() if x.endswith(".xsd")])
    return os.path.expandvars("$CARMTMP/cmsshell/rpc/xsd/"+name)

def explore(host, expr="", module="",variable="",rule=""):
    h,rpc = _getrpc(host)
    #uuid, type, module, variable, rule, expression
    if expr:
        type="Expression"
    else:
        raise Exception("No expression passed to explore()")
    def prettyPrint(elem,ind=''):
        if elem.nodeName == "Eval":
            if elem.getAttribute("keyword").lower() == "true":
               print "%s%s = %s       (keyword), scope=%s" % (ind,elem.getAttribute("name"),elem.getAttribute("value"),elem.getAttribute("effectiveScope"))
            else:
               print "%s%s.%%%s%% = %s      , scope=%s" % (ind,elem.getAttribute("module"),elem.getAttribute("value"), elem.getAttribute("name"),elem.getAttribute("effectiveScope"))
        for c in elem.getElementsByTagName("Eval"):
            prettyPrint(c,ind+'  ')
        
    for i,x in rpc.RaveServer.raveExplore("abc123",type,module,variable,rule,expr):
        from xml.dom.minidom import parseString
        print x
        x = parseString(x)
        prettyPrint(x.documentElement)

def _call_xml_xmlrpc(service, req, req_xsd=None, resp_xsd=None):
    if req_xsd is not None:
        try:
            _validate_xml(req, req_xsd)
        except:
            print >> sys.stderr, "Error validating request XML:"
            print req
            raise

    resp = None
    try:
        t1 = time.time()
        resp = service(req)
        t2 = time.time()
        # print >> sys.stderr, "XMPRPC RTT %f"%(t2-t1)
    except xmlrpclib.Fault, fault:
        print >> sys.stderr, fault.faultString
        raise

    # try to pretty-print the response
    try:
        pretty_resp = etree.to_pretty_string(etree.fromstring(resp))
    except:
        pretty_resp = resp

    if resp_xsd is not None:
        try:
            _validate_xml(pretty_resp, resp_xsd)
        except:
            print >> sys.stderr, "Error validating response XML:"
            print pretty_resp
            raise

    return pretty_resp

def _validate_xml(xml, xsd_file):
    try:
        from lxml import etree
    except ImportError:
        return

    xmlschema = etree.XMLSchema(etree.parse(open(xsd_file)))
    if not xmlschema.validate(etree.parse(StringIO(xml))):
        raise Exception("xml illegal according to %s: %s"%(xsd_file, xmlschema.error_log))
