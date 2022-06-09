
#
#
import Cfh
import Errlog
import Cui
import tempfile
import os
import modelserver as M
import carmensystems.rave.api as R
import RelTime
from utils.rave import RaveIterator
import carmstd.cfhExtensions as cfhExtensions
import carmusr.HelperFunctions as HF

class TransportTimeField(Cfh.Duration):
    def __init__(self,*args):
        Cfh.Duration.__init__(self, *args)
        self.min = 10 # 10 min
        self.max = 360 # 6 hours

    def check(self, text):
        # Checks the limits min and max
        text_int = Cfh.Duration.toRepr(text) # Convert to integer for compare
        checkDuration = Cfh.Duration.check(self, text)
        if checkDuration:
            return checkDuration
        elif text_int != 0:
            if (text_int < self.min) or (text_int > self.max):
                return "Transport time must be between 10 min and 6 hours long"
            else:
                return None
        
class TransportTimeSet(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)
        
        self.layover_head = Cfh.String(self, "LAYOVER_HEAD", 0)
        self.layover_head.setEditable(0)
        
        # Time fields
        self.transport_time_before = TransportTimeField(self, "TRANSPORT_BEFORE")
        self.transport_time_after = TransportTimeField(self, "TRANSPORT_AFTER")

        # OK and CANCEL buttons
        self.ok = Cfh.Done(self, "B_OK")
        self.quit = Cfh.Cancel(self, "B_CANCEL")

        # Creating the form
        form_layout = """
FORM;TRANSPORT_FORM;Set Local Transport Time

LFIELD;LAYOVER_HEAD
GROUP;NOSEP
FIELD;TRANSPORT_BEFORE;To hotel:
FIELD;TRANSPORT_AFTER;From hotel:
LABEL;  Insert 0 to use default values

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""

        transport_form_file = tempfile.mktemp()
        f = open(transport_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(transport_form_file)
        os.unlink(transport_form_file)
        
    def getValues(self):
        """
        Function returning the values set in the form
        """
        before =  self.transport_time_before.valof()

        if before == 0:
           before = None
        else:
            before = RelTime.RelTime(before)

        after =  self.transport_time_after.valof()

        if after == 0:
            after = None
        else:
            after = RelTime.RelTime(after)
        
        return [before, after]

    def setValues(self, before, after, span, station):
        self.layover_head.assign("Layover at %s: %s" % (station, span))
        
        if before is not None:
            # Convert it to an appropriate format
            before = Cfh.Duration.toRepr(str(before))
            if before < self.transport_time_before.max and \
               before >= self.transport_time_before.min:
                self.transport_time_before.assign(before)
                
        if after is not None:
            # Convert it to an appropriate format
            after = Cfh.Duration.toRepr(str(after))
            if after < self.transport_time_after.max and \
               after >= self.transport_time_after.min:
                self.transport_time_after.assign(after)

def setTransportTime():
    """
    Creates a select form and set default values
    """

    try:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        leg, station, crewId, defaultTimeTo, defaultTimeFrom, span = (
            Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "hotel.%slt_leg%"),
            Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "hotel.%slt_station%"),
            Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crew.%id%"),
            Cui.CuiCrcEval(Cui.gpc_info, area, "object", "hotel.%slt_default_time_apt_to_hotel%"),
            Cui.CuiCrcEval(Cui.gpc_info, area, "object", "hotel.%slt_default_time_hotel_to_apt%"),
            Cui.CuiCrcEval(Cui.gpc_info, area, "object", "hotel.%slt_layover_span_str%"),
            )
    except:
        cfhExtensions.show("The selected leg is not followed by any special local transport")
        return 1

    if not station:
        # None if there are no more duties in trip. If this is
        # the case there is no layover to do the slt on.
        cfhExtensions.show("No layover after this duty. Not possible to "
                           "set special local transport")
        return 1

    tm = M.TableManager.instance()
    tm.loadTables(["spec_local_trans", "crew"])
    sltTable = tm.table("spec_local_trans")
    crewTable = tm.table("crew")
    
    crewRef = crewTable.getOrCreateRef((crewId,))
    
    try:
        dbRow = sltTable[(leg, station, crewRef)]
    except:
        dbRow = None
        
    transport_time_form = TransportTimeSet("Transport_Time")

    if dbRow is None:        
        transport_time_form.setValues(defaultTimeTo, defaultTimeFrom, span, station)
    else:
        # If null values in table.
        actual_to_rest = dbRow.to_rest or RelTime.RelTime(0)
        actual_from_rest = dbRow.from_rest or RelTime.RelTime(0)
        transport_time_form.setValues(actual_to_rest, actual_from_rest, span, station)
        
    transport_time_form.show(1)

    # Perform form event loop.
    if transport_time_form.loop() != Cfh.CfhOk:
        # Cancel button was pressed. 
        return 1

    # OK button was pressed.
    
    [form_before, form_after] = transport_time_form.getValues()

    form_before = form_before or defaultTimeTo
    form_after = form_after or defaultTimeFrom

    modified = False
    if dbRow is None:
        # There exist no entry in slt table for this rest.
        if form_before != defaultTimeTo or form_after != defaultTimeFrom:
            db_row = sltTable.create((leg, station, crewRef))
            modified = True
            db_row.to_rest = form_before
            db_row.from_rest = form_after
    else:
        # There was already an slt entry for this rest
        if form_before != actual_to_rest or form_after != actual_from_rest:
            # The existing slt entry has been changed.
            if form_before == defaultTimeTo and form_after == defaultTimeFrom:
                # Default times used. No slt needed -> remove row.
                dbRow.remove()
            else:
                # The canges made should be saved
                dbRow.to_rest = form_before
                dbRow.from_rest = form_after
            modified = True

    if modified:
        Cui.CuiReloadTable("spec_local_trans", 1)
        HF.redrawAllAreas(Cui.CrewMode)
        
    return 0
