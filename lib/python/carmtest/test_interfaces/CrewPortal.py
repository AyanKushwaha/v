import sys
import os
from carmtest.framework import *

SCHEMA = os.path.expandvars("$CARMUSR/lib/python/crewlists/schema/crewReply.xsd")

class interfaces_001_CrewPortalBasics(TestFixture):
    "GetReportList"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        
    def setUp(self):
        pass
        
    def test_001_reportlist(self):
        from crewlists.getreportlist import report as reportlist
        from xml.dom.minidom import parseString
        doc = parseString(xml_reply(reportlist("GetReportList")))
        rpts = [str(xml_innerText(nd, 'reportId')) for nd in xml_traverse(doc, "replyBody", "getReportListReply", "reportCollection", "report")]
        print rpts
        assert len(rpts) > 0, "Report list was empty"
        for rpt in rpts:
            assert rpt.strip(), "Report name was empty"
            assert rpt == rpt.upper(), "Report name %s must be uppercase" % rpt
        self.log("Reports: " + ", ".join(rpts))
        
    def test_002_malformedQuery(self):
        from crewlists.getreport import report
        from xml.dom.minidom import parseString
        doc = parseString(xml_reply(report("BLAH")))
        status = int(xml_innerText(doc.documentElement, "statusCode"))
        assert status == 990, "Expected error status, but got %s" % status

class interfaces_002_CrewPortalReports(TestFixture):
    "GetReport reports"
    
    @REQUIRE("Tracking")
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self.crew_extperkey = str(self.rave().eval("sp_crew", self.rave().foreach("iterators.roster_set", "crew.%extperkey%"))[0][0][1])
        self.crew_id = str(self.rave().eval("sp_crew", self.rave().foreach("iterators.roster_set", "crew.%id%"))[0][0][1])
        self.pp_start = self.rave().eval("fundamental.%pp_start%")[0]
        
    def report(self, name, *pvals):
        from crewlists.getreport import report
        from xml.dom.minidom import parseString
        reply = xml_reply(report('GetReport', name, len(pvals), *pvals))
        self.validateXML(reply, SCHEMA)
        self.result = parseString(reply)
        print self.result        
        code = xml_innerText(self.result.documentElement, "statusCode").strip()
        if int(code) != 0:
            self.log(xml_innerText(self.result.documentElement, "statusText").strip(), severity="Warning")
            self.fail("Invalid response code %s for report %s" % (code, name))
        html = ""
        for nd in xml_traverse(self.result, "replyBody", "getReportReply", "reportBody"):
            html = xml_innerText(nd)
            break
        assert html and len(html) > 0, "No HTML content in report %s" % name
        try:
            parseString(html)
        except:
            self.fail("report %s was not wellformed: " % str(sys.exc_info()[1]))
        return html
     
    def test_001_DUTYCALC(self):
        html = self.report("DUTYCALC", self.crew_extperkey, self.pp_start, self.pp_start + RelTime(7*24,0))
        assert "<h1>Duty Calculation</h1>" in html, "Expected header 'Duty Calculation'"
 
    def test_002_DUTYOVERTIME(self):
        mon = str(self.pp_start)[2:5]
        year = str(self.pp_start)[5:9]
        html = self.report("DUTYOVERTIME", self.crew_extperkey, mon, year)
        assert "<h1>Duty Overtime</h1>" in html, "Expected header 'Duty Overtime'"
 
    def test_003_CREWSLIP(self):
        mon = str(self.pp_start)[2:5]
        year = str(self.pp_start)[5:9]
        html = self.report("CREWSLIP", self.crew_extperkey, mon, year)
        assert "<h1>Published Roster:" in html, "Expected header 'Published roster'..."
 
    def test_004_PILOTLOGCREW(self):
        mon = str(self.pp_start)[2:5]
        year = str(self.pp_start)[5:9]
        html = self.report("PILOTLOGCREW", self.crew_extperkey, mon, year)
        assert "<h1>Pilot Log - Flight Activities</h1>" in html, "Expected header 'Pilot Log - Flight Activities'"

    def test_005_COMPDAYS(self):
        empno = None
        reason = None
        year = str(self.pp_start)[5:9]
        start = "01Jan%s" % year
        end = "01Jan%s" % str(int(year)+1)
        for row in self.table("account_entry").search("(&(tim>=%s)(tim<%s)(account=%s))" % (start, end, "F7S")):
            empno = row.crew.empno
            reason = row.reasoncode
            if empno: break
        if not empno or not reason:
            self.dataError("Missing account entry with F7S")
            return
        html = self.report("COMPDAYS", empno, "F7S", year)
        assert "<h1>Compensation Days</h1>" in html, "Expected header 'Compensation Days'"
        empnostr = ' <td class="col1">%s</td>' % empno
        reasonstr = '<td class="col3">%s</td>' % reason
        assert empnostr in html, "Expected empno row '%s' in COMPDAYS report" % empno
        assert reasonstr in html, "Expected F7S row '%s' in COMPDAYS report" % reason

    def test_006_PILOTLOGACCUM(self):
        html = self.report("PILOTLOGACCUM", self.crew_extperkey)
        assert ("<title>Pilot Log - Crew Accumulated Info (%s)</title>" % self.crew_extperkey) in html, "Expected crew empno %s in report title" % self.crew_extperkey
        assert "<h1>Pilot Log - Crew Accumulated Info</h1>" in html, "Expected header 'Pilot Log - Crew Accumulated Info'"
 
    def test_007_PILOTLOGFLIGHT(self):
        self.select(crew=self.crew_id)
        for _,leg,flight_id,date in self.getLegs('leg.%is_flight_duty%', eval=("leg_identifier","leg.%flight_id%","leg.%start_UTC%",))[0]:
            date = date.split()
            date = "%d%02d%02d" % (date[0],date[1],date[2])
            html = self.report("PILOTLOGFLIGHT", self.crew_extperkey, flight_id, date)
            assert "<h1>Pilot Log - Flight</h1>" in html, "Expected header 'Pilot Log - Flight'"
            assert "<td class=\"col1\">%s</td>" % flight_id in html, "Expected flight %s in PILOTLOGFLIGHT report" % flight_id
            return
        self.dataError("No suitable legs found")
 
    def test_008_PILOTLOGSIM(self):
        mon = str(self.pp_start)[2:5]
        year = str(self.pp_start)[5:9]
        html = self.report("PILOTLOGSIM", self.crew_extperkey, mon, year)
        assert "<h1>Pilot Log - Simulator Activities</h1>" in html, "Expected header 'Pilot Log - Simulator Activities'"
 
    def test_009_VACATION(self):
        year = str(self.pp_start)[5:9]
        html = self.report("VACATION", self.crew_extperkey, "VA", year)
        assert "<h1>Vacation Balances and Postings</h1>" in html, "Expected header 'Vacation Balances and Postings'"
 
    def test_010_BOUGHTDAYS(self):
        accounts = {'BOUGHT&gt;6 HRS': "BOUGHT", 'BOUGHT=F3S': "BOUGHT_COMP_F3S",
                    'BOUGHT BL': "BOUGHT_BL", 'BOUGHT&lt;=6 HRS': "BOUGHT_8",
                    'BOUGHT+F3': "BOUGHT_COMP",
                    'BOUGHT>6 HRS': "BOUGHT", 'BOUGHT<=6 HRS': "BOUGHT_8"}
        for account_key, account_value in accounts.items():
            empno = None
            reason = None
            for row in self.table("account_entry").search("(&(tim>%s)(account=%s))" % (self.pp_start, account_value)):
                empno = row.crew.empno
                reason = row.reasoncode
                if empno: break
            if not empno or not reason:
                self.log(("Missing account entry with %s" % (account_value)), "ERROR")
                #self.dataError("Missing account entry with BOUGHT")
            else:
 
                year = str(self.pp_start)[5:9]
                html = self.report("BOUGHTDAYS", empno, account_key, year)
                assert "<h1>Bought Days</h1>" in html, "Expected header 'Compensation Days'"
                empnostr = '<td class="col1">%s</td>' % empno
                reasonstr = '<td class="col3">%s</td>' % reason
                assert empnostr in html, "Expected empno row '%s' in BOUGHTDAYS report" % empno
                assert reasonstr in html, "Expected %s row '%s' in BOUGHTDAYS report" % (account_value, reason)
                
 

def xml_reply(x):
    return x[x.index('\n')+1:]

def xml_traverse(nd, *elems):
    """
    Iterates "flat" over the specified node hierarchy.
    """
    if len(elems) == 0:
        yield nd
    else:
        for snd in nd.getElementsByTagName(elems[0]):
            for ssnd in xml_traverse(snd, *elems[1:]):
                yield ssnd
                
def xml_innerText(nd,subel=None):
    """
    Returns the inner text of an element.
    """
    from xml.dom.minidom import Node
    txt = []
    if subel:
        nds = nd.getElementsByTagName(subel)
        for nd in nds:
            txt.append(xml_innerText(nd))
    else:
        for snd in nd.childNodes:
            if snd.nodeType == Node.TEXT_NODE or snd.nodeType == Node.CDATA_SECTION_NODE:
                txt.append(snd.data.encode('ascii', 'ignore'))
    return str(''.join(txt))

def xml_allInner(nd, *subel):
    rv = []
    for snd in xml_traverse(nd, *subel):
        txt = xml_innerText(snd).strip()
        if txt: rv.append(txt)
    return rv
