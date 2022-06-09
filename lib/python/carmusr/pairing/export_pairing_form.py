

# Sys imports
import Cui
import Cfh
import weakref
import AbsTime
import carmensystems.rave.api as R
from export_pairing_data import ExportPairingData

class BaseDate(Cfh.Date):
    def __init__(self, *args):
        self.parent = weakref.ref(args[0])
        Cfh.Date.__init__(self, *args)
    
    def date(self):
        return AbsTime.AbsTime(Cfh.Date.toRepr(self.getValue()))
    
class FromDate(BaseDate):
    def __init__(self, *args):
        BaseDate.__init__(self, *args)

    def compute(self, *args):
        d2 = self.parent().d2
        if d2.getValue() == "":
            from_date_rave_string = str(self.date())
            d2.setValue(Cfh.Date.toString(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, "None", "add_months(" +from_date_rave_string+ ", 1)")))

class ToDate(BaseDate):
    def __init__(self, *args):
        BaseDate.__init__(self, *args)

class DateInterval(Cfh.Box):
    def __init__(self, start, end , name = "", title = ""):
        Cfh.Box.__init__(self, name, title)
        self.d1 = FromDate(self, "CT_DATE1", Cfh.CfhArea(1,1,-1,-1), int(start))
        self.d2 = ToDate(self, "CT_DATE2", Cfh.CfhArea(1,14,-1,-1), int(end))
        self.d1.compute()
        self.driverNameBox  = Cfh.String(self, "CT_STRING", Cfh.CfhArea(2,1,-1,-1),15,"Pairing")
        self.o = Cfh.Done(self, "CT_OK")
        self.o.setText("Ok")
        self.c = Cfh.Cancel(self, "CT_CANCEL")
        self.c.setText("Cancel")
        self.build()

    def check(self, *args):
        r = Cfh.Box.check(self, *args)
        if r: return r
        if self.d1.getValue() == "":
            return "You must specify the from-date"
        if self.d2.getValue() == "":
            return "You must specify the to-date"
        if Cfh.Date.toRepr(self.d1.getValue()) > Cfh.Date.toRepr(self.d1.getValue()):
            return "From-date should be before to-date"
        if len(self.driverNameBox.getValue()) == 0:
            return "You must specify the driver name"

        return None

    def start(self):
        return self.d1.date()
    
    def end(self):
        return self.d2.date()

    def driverName(self):
        return self.driverNameBox.valof()
    
def getPeriodStart():
    return R.eval('fundamental.%pp_start%')[0]

def getPeriodEnd():
    return R.eval('fundamental.%pp_end%')[0]

def show(area=Cui.CuiWhichArea):
    """
    Creates a select form
    """
    global export_pairing_form
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    
    export_pairing_form = DateInterval(getPeriodStart(), getPeriodEnd(), "Export Pairing Data For Period", "Export Pairing Data For Period")
    export_pairing_form.show(1)
    if export_pairing_form.loop() == Cfh.CfhOk:
        # Ok button pressed, get the values
        start = export_pairing_form.start()
        end = export_pairing_form.end()
        driverName = export_pairing_form.driverName()
        exporter = ExportPairingData(export_pairing_form.start(), export_pairing_form.end(), export_pairing_form.driverName())
        exporter.export()
    
    
