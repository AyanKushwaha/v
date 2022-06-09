'''
Created on Apr 9, 2010

@author: rickard
'''
import carmensystems.rave.api as R
import carmensystems.publisher.api as prt
from report_sources.include.ValidityReport import ValidityReport, TableProblemSet, RosterProblemSet, RosterProblem, TableProblem
from AbsDate import AbsDate
from AbsTime import AbsTime
from tm import TM
from sets import Set
from utils.performance import clockme

class SalaryValidityReport(ValidityReport):
    def createContents(self, boxes, filter):
        TableProblem.colnames['home_country'] = 'Home'
        TableProblem.colnames['maincat'] = 'Cat'
        TableProblem.colnames['stop_country'] = 'Stop'
        
        prb = SalaryRosterProblemSet(filter=filter)
        crew = prb.getCrew()
        boxes.head("Roster (%d crew)" % len(crew))
        boxes.add("Overlapping activities", prb.checkOverlaps())
        boxes.add("Full-day activities", prb.checkFullDayActivities())
        boxes.add("Missing stations", prb.checkMissingStations())
        boxes.add("Off-duty / homebase mismatch", prb.checkCrewOffInWrongBase())
        boxes.add("Trip length", prb.checkTripLength())
        boxes.add("Ground transport length", prb.checkCrewDefaultGroundAct())
        
        prb = SalaryTableProblemSet(crew)
        boxes.head("Salary tables")
        boxes.add("salary_article", prb.checkSalaryArticleTable())
        boxes.add("exchange_rate", prb.checkValidityDates('exchange_rate', key=('reference','cur'), no_check_after_pp_end=True))
        boxes.add("per_diem_compensation", prb.checkPerDiemCompensationTable())
        boxes.add("per_diem_tax", prb.checkPerDiemTaxTable())
        boxes.head("Crew tables")
        boxes.add("crew_contract", prb.checkValidityDates('crew_contract', key=('crew',), display=('contract',), can_equal=True, filter=lambda x: x.crew.id in prb.crew))
        
        boxes.end()
        
        
class SalaryRosterProblemSet(RosterProblemSet):
    def __init__(self, context="default_context", filter=None):
        RosterProblemSet.__init__(self, context, filter)
        
    @clockme
    def checkCrewDefaultGroundAct(self):
        rv = []
        flt = ["leg.%is_ground_transport%",
               "leg.%time% = 1:00"]
        v, = R.eval(self.context, R.foreach(R.iter("iterators.leg_set", where=tuple(flt)),
                                       "crew.%id%", "crew.%extperkey%", "leg.%start_date%", "leg.%code%", "leg.%start_station%", "leg.%end_station%"))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]) or cmp(a[3], b[3]))
        for _, _, extPerKey, startDate, legCode, startStation, endStation in v:
            rv.append(RosterProblem(extPerKey, "Ground transport %s %s-%s has default length" % (legCode, startStation, endStation), key={'Date':AbsDate(startDate)}))
                
        return rv
        
class SalaryTableProblemSet(TableProblemSet):       
    def __init__(self, crew):
        TableProblemSet.__init__(self)
        self.crew = dict(zip(crew,crew))
        
    @clockme
    def checkSalaryArticleTable(self):
        "Reports problems with the salary_article table"
        intart = {}
        combo = {}
        rv = []
        for r in TM.salary_article:
            s = r.extsys
            k = (s, r.extartid)
            if not k in combo:
                combo[k] = []
            combo[k].append((r.validfrom, r.validto)) 
            if not k in intart:
                intart[k] = r.intartid
            elif intart[k] != r.intartid:
                rv.append(TableProblem("salary_article", "The external system %s extarticle %s specifies different internal articles %s and %s" % (s, r.extartid, r.intartid, intart[k])))
                
        for k in combo.keys():
            v = combo[k]
            errs = self._checkDateRange(v)
            if errs:
                rv.append(TableProblem("salary_article", errs, dict(zip(("System","Code"),k)))) 
        return rv
    
    @clockme
    def checkPerDiemCompensationTable(self):
        "Reports problems with the per_diem_compensation table"
        fcountries = Set()
        tcountries = Set()
        mcats = Set()
        combo = {}
        rv = []
        for r in TM.per_diem_compensation:
            fcountries.add(r.home_country.id)
            tcountries.add(r.stop_country.strip())
            mcats.add(r.maincat.id)
            k = (r.home_country.id, r.stop_country.strip(), r.maincat.id)
            if not k in combo:
                combo[k] = []
            combo[k].append((r.validfrom, r.validto))
        for f in fcountries:
            for t in tcountries:
                for c in mcats:
                    if not (f, t, c) in combo:
                        if f in ("CN", "JP", "HK"):
                            if t != "*" or c == "F": continue
                        rv.append(TableProblem("per_diem_compensation", "Expected, but missing", dict(zip(("Home","Stop","Cat"),(f,t,c)))))
        for dr in combo.keys():
            v = combo[dr]
            errs = self._checkDateRange(v)
            if errs:
                rv.append(TableProblem("per_diem_compensation", errs, dict(zip(("Home","Stop","Cat"),dr)))) 
        return rv + self.checkKeys('per_diem_compensation')
    
    @clockme
    def checkPerDiemTaxTable(self):
        "Reports problems with the per_diem_tax table"
        fcountries = Set()
        tcountries = Set()
        combo = {}
        rv = []
        for r in TM.per_diem_tax:
            k = (r.home_country.id, r.stop_country)
            if r.home_country.id in ("SE", "NO", "DK", "CN", "JP", "HK"):
                fcountries.add(r.home_country.id)
            else:
                rv.append(TableProblem("per_diem_tax", "Unexpected home country %s for stop country %s" % (r.home_country.id, r.stop_country),key=dict(zip(('Home','Stop'), k))))
            tcountries.add(r.stop_country)
            if not k in combo:
                combo[k] = []
            combo[k].append((r.validfrom, r.validto))
            if not r.home_country.id in ("CN", "JP", "HK"):
                if r.rate <= 100 or r.rate >= 500000:
                    rv.append(TableProblem("per_diem_tax", "The per diem tax rate %s for %s looks out of range" % (r.rate, str(k)),key=dict(zip(('Home','Stop'), k))))
        for d in [1,2,3]:
            k=("NO", "/%d"%d)
            if not k in combo:
                rv.append(TableProblem("per_diem_tax", "The per diem tax %s is unspecified" % str(k)))
        for f in fcountries:
            if not f in ("CN", "JP", "HK"):
                k = (f, "*")
                if not k in combo:
                    rv.append(TableProblem("per_diem_tax", "The per diem tax %s is unspecified" % str(k)))
            for t in tcountries:
                if not (f, t) in combo:
                    if not f in ("CN", "JP", "HK") and not t[0] == "/" and t != "*":
                        #rv.append(TableProblem("per_diem_tax", "The per diem tax %s is unspecified" % str((f,t))))
                        pass
        for dr in combo.keys():
            v = combo[dr]
            errs = self._checkDateRange(v)
            if errs:
                rv.append(TableProblem("per_diem_tax", errs, dict(zip(("Home","Stop"),dr)))) 
        return rv
    
def colnamedisp(name):
    if name == "stop_country":
        return "Stop"
    if name == "home_country":
        return "Home"

        
def runReport(scope='window', args=''):
    """Run PRT Report with data found in 'area', setting 'default_context'."""
    try:
        import Cui
        if scope == "window":
            area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
            Cui.CuiSetCurrentArea(Cui.gpc_info, area)
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
        else:
            area = Cui.CuiNoArea
            args += " PLAN=1"
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope, 'SalaryValidityReport.py', 0, args)
    except Exception, e:
        print e
        
def runSubplanReport():
    import utils.CfhFormClasses as F
    rgn, = R.eval("planning_area.%filter_company_p%")
    regions = ["ALL","SKD", "SKN", "SKS"]
    maincats = ["ALL","FD", "CC"]
    if not rgn in regions: rgn = "ALL" 
    class ParameterForm(F.BasicCfhForm):
        def __init__(self):
            F.BasicCfhForm.__init__(self, "Post-planning validity report")
            self.add_filter_combo(0, 0, "region", "Region", rgn, regions)
            self.add_filter_combo(1, 0, "maincat", "Category", "ALL", maincats)
        
    try:
        frm = ParameterForm()
        cat, rgn = frm()
        runReport(scope="plan", args="REGION=%s MAINCAT=%s" % (rgn, cat))
    except F.CancelFormError:
        pass 
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() == "subplan":
        runSubplanReport()
    else:
        runReport()
