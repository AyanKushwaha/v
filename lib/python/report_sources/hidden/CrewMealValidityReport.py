import carmensystems.rave.api as R
import carmensystems.publisher.api as prt
import krasch
from report_sources.include.ValidityReport import ValidityReport, TableProblemSet, RosterProblemSet, RosterProblem, TableProblem
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from tm import TM
from utils.performance import clockme
from utils.TimeServerUtils import now

class CrewMealValidityReport(ValidityReport):
    """ Improvment: Check that referred entries actually exists.
    
    """
        
    def createContents(self, boxes, filter):
        prb = CrewMealTableProblemSet()
        boxes.head("Crew Meal tables")
        boxes.add("meal_airport", prb.checkMealAirportTable())
        boxes.add("meal_cons_correction", prb.checkMealConsCorrectionTable())
        boxes.add("meal_load_correction", prb.checkMealLoadCorrectionTable())
        boxes.add("meal_consumption_code", prb.checkMealConsumptionCodeTable())
        boxes.add("meal_supplier", prb.checkMealSupplierTable())
        boxes.end()
        
        
class CrewMealRosterProblemSet(RosterProblemSet):
    def __init__(self, context="default_context", filter=None):
        RosterProblemSet.__init__(self, context, filter)
        
class CrewMealTableProblemSet(TableProblemSet):       
    def __init__(self):
        TableProblemSet.__init__(self)
    
    @clockme
    def checkMealAirportTable(self):
        "Reports problems with the meal_airport table"
        combo = {}
        rv = []
        for r in TM.meal_airport:
            k = (r.station.id, r.region.id)
            if r.validto > now():
                if not k in combo:
                    combo[k] = []
                combo[k].append((r.validfrom, r.validto))
                
                if r.rest_close is None:
                    rv.append(TableProblem("meal_airport", "No Restaurant closing time specified", dict(zip(("Station", "Region"), k))))
                elif not r.rest_close > RelTime('0:00'):
                    rv.append(TableProblem("meal_airport", "The Restaurant closing time %s is invalid" % r.rest_close, dict(zip(("Station", "Region"), k))))
                
        for k in combo.keys():
            v = combo[k]
            errs = self._checkDateRange(v)
            if errs:
                rv.append(TableProblem("meal_airport", errs, dict(zip(("Station", "Region"), k))))
        return rv
    
    @clockme
    def checkMealConsCorrectionTable(self):
        "Reports problems with the meal_cons_correction table"
        combo = {}
        rv = []
        for r in TM.meal_cons_correction:
            k = (r.flt_nr, r.stn_from.id, r.stn_to.id, r.maincat.id, r.stc)
            if r.validto > now():
                if not k in combo:
                    combo[k] = []
                combo[k].append((r.validfrom, r.validto))

                if r.corr_type == "N" and not r.corr_code == "*":
                        rv.append(TableProblem("meal_cons_correction", "The correction type 'N' should have correction code '*', not '%s'" % r.corr_code, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
                
                if not r.maincat.id in ("F", "C"):
                    rv.append(TableProblem("meal_cons_correction", "The maincat '%s' is invalid, should be either 'F' or 'C'" % r.maincat.id, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
                    
                if not r.stc in ("J", "C", "P"):
                    rv.append(TableProblem("meal_cons_correction", "The STC '%s' is invalid, should be either 'J', 'C' or 'P'" % r.stc, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
                
                if not r.corr_type in ("A", "N", "O", "S"):
                    rv.append(TableProblem("meal_cons_correction", "The correction type '%s' is invalid" % r.corr_type, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
                
                for c in r.corr_code.split(','):
                    if (len(c) > 0) and c not in ("B", "C", "F", "H", "M", "Q", "S", "X", "Z", "*"):
                        rv.append(TableProblem("meal_cons_correction", "The correction code '%s' is invalid" % c, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
                
        for k in combo.keys():
            v = combo[k]
            errs =self._checkDateRange(v, allow_gaps=True)
            if errs:
                rv.append(TableProblem("meal_cons_correction", errs, dict(zip(("Flight", "From", "To", "Maincat", "STC"), k))))
        return rv
    
    @clockme
    def checkMealLoadCorrectionTable(self):
        "Reports problems with the meal_load_correction table"
        combo = {}
        rv = []
        for r in TM.meal_load_correction:
            k = (r.cons_flt, r.cons_stn.id)
            if r.validto > now():
                if not k in combo:
                    combo[k] = []
                combo[k].append((r.validfrom, r.validto))
            
        for k in combo.keys():
            v = combo[k]
            errs =self._checkDateRange(v, allow_gaps=True)
            if errs:
                rv.append(TableProblem("meal_load_correction", errs, dict(zip(("Flight", "From"), k))))
        return rv

    @clockme
    def checkMealConsumptionCodeTable(self):
        """ Reports problems with the meal_consumption_code table
            Improvement: Use the start_time end end_time when checking dates in order to find overlapping 
                         opening times during a period.
        
        """
        combo = {}
        rv = []
        for r in TM.meal_consumption_code:
            k = (r.region.id, r.maincat.id, r.stc, r.meal_code, r.start_time)
            if r.validto > now():
                if not k in combo:
                    combo[k] = []
                combo[k].append((r.validfrom, r.validto))
                
                c = r.cons_code.code
                if not c in ("B", "C", "F", "H", "M", "Q", "S", "X", "Z"):
                    rv.append(TableProblem("meal_consumption_code", "The meal consumption code %s is not found in meal_codes" % c, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
                
                if not r.maincat.id in ("C", "F", "T"):
                    rv.append(TableProblem("meal_consumption_code", "Invalid crew category set id %s in maincat" % r.maincat.id, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
                
                if not r.stc in ("C", "J", "P"):
                    rv.append(TableProblem("meal_consumption_code", "Invalid service type code %s in stc" % r.stc, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
                
                if not r.start_time <= RelTime('23:59'):
                    rv.append(TableProblem("meal_consumption_code", "Invalid start time %s" % r.end_time, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
                    
                if not r.end_time <= RelTime('23:59'):
                    rv.append(TableProblem("meal_consumption_code", "Invalid end time %s" % r.end_time, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
                
        for k in combo.keys():
            v = combo[k]
            errs =self._checkDateRange(v)
            if errs:
                rv.append(TableProblem("meal_consumption_code", errs, dict(zip(("Region", "Maincat", "STC", "Meal Code"), k))))
        return rv
    
    @clockme
    def checkMealSupplierTable(self):
        "Reports problems with the meal_supplier table"
        combo = {}
        rv = []
        for r in TM.meal_supplier:

            if r.supplier_id == "DEFAULT":
                continue
            
            k = (r.supplier_id, r.region.id, r.pref_stc, r.station.id)
            
            if r.validto > now():
                if not k in combo:
                    combo[k] = []
                combo[k].append((r.validfrom, r.validto))

                if not r.pdf and not r.xml:
                    rv.append(TableProblem("meal_supplier", "A supplier must have at least support for PDF or XML ", dict(zip(("Supplier id", "Region", "Pref", "Station"), k))))
                
                if r.email is None or r.email.find('@') < 0:
                    rv.append(TableProblem("meal_supplier", "Invalid email address '%s' " % (r.email), dict(zip(("Supplier id", "Region", "Pref", "Station"), k))))
                
        for k in combo.keys():
            v = combo[k]
            errs =self._checkDateRange(v, allow_gaps=True)
            if errs:
                rv.append(TableProblem("meal_supplier", errs, dict(zip(("Supplier id", "Region", "Pref", "Station"), k))))
        return rv
    
    
    
      
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
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope, 'CrewMealValidityReport.py', 0, args)
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
