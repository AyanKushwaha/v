import carmensystems.publisher.api as P
import carmensystems.rave.api as R
import carmusr.HelperFunctions as HF
import Cui
import Variable
import Errlog

import os

sk_app = os.environ.get("SK_APP")

class Report(P.Report):


    def set_period(self):
        period, = R.eval('crg_info.%period%')
        self.add(P.Text("Period: %s"%str(period)))

    def set_crew_area(self):
        crew_area, = R.eval('crg_info.%planning_area_crew%')
        self.add(P.Text("Planning area crew: %s"%str(crew_area)))
        
    def set_trip_area(self):
        if sk_app.upper() == 'PREPLANNING':
            return
        trip_area, = R.eval('crg_info.%planning_area_trip%')
        self.add(P.Text("Planning area trip: %s"%str(trip_area)))

    def set_planinfo(self):
        if sk_app.upper() == 'PREPLANNING':
            return
        plan_type = ("File","Database")[HF.isDBPlan()]
        v = Variable.Variable("")
        Cui.CuiCrcGetParameterSetName({'WRAPPER': Cui.CUI_WRAPPER_NO_EXCEPTION},v)
        plan_paramset = v.value.split("/")[-1]
        self.add(P.Text("Storage: %s / Parameterset: %s"%(plan_type,plan_paramset)))
        
    def create(self):
        status_items = [("Period",self.set_period),
                        ("Planinfo",self.set_planinfo),
                        ("Crew area",self.set_crew_area),
                        ("Trip area",self.set_trip_area)]
        for (name, set_func) in status_items:
            try:
                set_func()
            except Exception, err:
                Errlog.log("show_status_planning.py:: Error setting %s in status windows;\n%s"%\
                           (name,str(err)))
