#####

##
#####
"""
Module for editing exceptions on composition and briefings for simulators
@date: 5Jan2010
@author: Erik Arnstrom
@org: Jeppesen systems AB
"""
import Cui
from RelTime import RelTime
import tempfile
import carmusr.HelperFunctions as HF
import utils.CfhFormClasses as CFC
import Errlog
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions
import Attributes
from tm import TM
from AbsTime import AbsTime

ONE_MINUTE = RelTime(0,1)
brief_names = ("Brief","Midbrief","Debrief")
comp_names = ("FC","FP","FR","TL","TR")

class SimExceptionForm(CFC.BasicCfhForm):
    """
    Edit the exceptions of the selected simulator
    """
    def __init__(self, comp, briefings, multisim,  *args):
        CFC.BasicCfhForm.__init__(self, "Simulator exceptions")
        self._delta_y = 0
        self._delta_x = 1
        ix = 0
        for (need, pos) in zip(comp, comp_names):
            self.add_number_combo(1, ix*6, pos, pos, need, 19)
            ix += 1

        ix = 0
        for (brief, name) in zip(briefings, brief_names):
            self.add_number_combo(3, ix*10, name, name, brief,999)
            ix += 1

        self.add_toggle_combo(5, 0, 'multisim','Two-parted:', multisim)
        
    @property
    def comp(self):
        return (self.FC_field.valof(), self.FP_field.valof(), self.FR_field.valof(), self.TL_field.valof(), self.TR_field.valof())

    @property
    def briefings(self):
        return (self.Brief_field.valof(), self.Midbrief_field.valof(), self.Debrief_field.valof())

    @property
    def multisim(self):
        return self.multisim_field.valof()


def _update_sim(legs, comp=None, briefings=None, multisim=False):
    """
    Updates the ground tasks.
    If comp isn't supplied it is assumed that attribute should be removed.
    Composition is saved as an integer with base 20.
    Briefings are saved in a reltime with base 1000 (minutes).
    """

    sim_exc_attr = "SIM EXC"
    if comp is None:
        for (ix, udor, uuid) in legs:
            Attributes.RemoveGroundTaskAttr(udor, uuid, sim_exc_attr)
    else:
        comp_int = 0
        fact = 4
        for pos in comp:
            comp_int += pos * (20**fact)
            fact -= 1
        brief_rel = RelTime(0,0)
        fact = 2
        for tim in briefings:
            brief_rel += ONE_MINUTE*tim*(1000**fact)
            fact -= 1

        if multisim:
            mult_str = "multisim"
        else:
            mult_str = None

        attr_vals = {"int":comp_int,
                     "rel":brief_rel,
                     "str":mult_str}
        for (ix, udor, uuid) in legs:
            Attributes.SetGroundTaskAttr(udor, uuid, sim_exc_attr, refresh=False, **attr_vals)
    Attributes._refresh("ground_task_attr")

def _update_booking(trip_obj):
    (is_roster, uuid, udor) = trip_obj.eval('fundamental.%is_roster%',
                                            'trip.%uuid%',
                                            'trip.%udor%')
    # 1. Find the trip in the model
    try:
        udor = AbsTime(udor*1440)
        trip = TM.trip[(udor, uuid)]
    except TypeError, e:
        error = "Warning: booked value could not be modified"
        Errlog.log("sim_exception_handler.py::_update_booking: Warning: %s" %error)
        cfhExtensions.show(error)
        return

    # 2. Find the current need
    needs = trip_obj.eval("studio_assign.%sim_need_fc%",
                          "studio_assign.%sim_need_fp%",
                          "studio_assign.%sim_need_fr%",
                          "studio_assign.%sim_need_tl%",
                          "studio_assign.%sim_need_tr%")
    
    # 3. Find the current booking
    books = trip_obj.eval("studio_assign.%sim_book_fc%",
                          "studio_assign.%sim_book_fp%",
                          "studio_assign.%sim_book_fr%",
                          "studio_assign.%sim_book_tl%",
                          "studio_assign.%sim_book_tr%")
    
    # 4. Adjust current trip with the diff in need vs booked
    positions = ("0","1","2","8","9")

    changed_book = False
    change_ok = True
    for (need, book, pos) in zip(needs, books, positions):
        diff = need - book
        if diff != 0 :
            changed_book = True
            if not is_roster:
                change_ok &= _adjust_book(trip, pos, need-book)
    
    # 5. Report errors
    if changed_book:
        if is_roster:
            error = "Booked value can not be changed on assigned simulator"
        elif not change_ok:
            error = "Booked value could not be reduced on this trip"
        else:
            error = False
    else:
        error = False

    if error:
        Errlog.log("sim_exception_handler.py::_update_booking: Error: %s" %error)
        cfhExtensions.show(error)
    else:
        Errlog.log("sim_exception_handler.py::_update_booking: Finished ok")
    return

def _adjust_book(trip, pos, diff):
    current_book = getattr(trip, "cc_%s" %pos)
    new_book = current_book + diff
    if new_book < 0:
        return False
    else:
        setattr(trip, "cc_%s" %pos, new_book)
        return True

def edit_exception_marked(mode="SET"):
    # Get current area and trip_ids for marked trips
    cui_area = Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)
    trip_ids = Cui.CuiGetTrips(Cui.gpc_info, cui_area, "marked")

    # Find first simulator and get composition and brief times
    first_sim_crr_id = None
    for crr_id in trip_ids:
        trip = HF.TripObject(str(crr_id), cui_area)
        trip_is_sim, = trip.eval('trip.%is_simulator%')
        if trip_is_sim:
            first_sim_crr_id = crr_id
            first_sim = HF.TripObject(str(first_sim_crr_id), cui_area)
            break
    if first_sim_crr_id == None:
        cfhExtensions.show("No simulators marked")
        return
        
    (brief, midbrief, debrief,
     fc, fp, fr, tl, tr,
     multisim) = first_sim.eval("studio_assign.%sim_brief%",
                       "studio_assign.%sim_midbrief%",
                       "studio_assign.%sim_debrief%",
                       "studio_assign.%sim_need_fc%",
                       "studio_assign.%sim_need_fp%",
                       "studio_assign.%sim_need_fr%",
                       "studio_assign.%sim_need_tl%",
                       "studio_assign.%sim_need_tr%",
                       "studio_assign.%sim_is_multi%")
    
    comp = (fc, fp, fr, tl, tr)
    briefings = (brief, midbrief, debrief)

    # Display the form
    if mode == "SET":
        form = SimExceptionForm(comp, briefings, multisim)
        try:
            form()
        except CFC.CancelFormError, ef:
            Errlog.log("sim_exception_handler.py:: User canceled operation")
            return -1
    else:
        form = None

    for crr_id in trip_ids:
        trip = HF.TripObject(str(crr_id), cui_area)
        trip_is_sim, = trip.eval('trip.%is_simulator%')

        if trip_is_sim:
            edit_exception(mode, True, crr_id, form)

def edit_exception(mode="SET", marked_trips=False, crr_id=None, form=None):
    """
    Edits the exceptions on simulators.
    If mode is SET a form is presented.
    If mode is REMOVE current attribute is removed.
    """
    Errlog.log("...")
    if not HF.isDBPlan():
        Errlog.log("sim_exception_handler.py:: Only in database plan")
        cfhExtensions.show("Only in database plan")
        return
    # Sync if any open-time trips are recently created
    Cui.CuiSyncModels(Cui.gpc_info)

    # Get current area
    cui_area = Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)

    # Get current trip(s)
    if crr_id == None:
        crr_id = Cui.CuiCrcEvalInt(Cui.gpc_info,cui_area,"object","crr_identifier")

    trip = HF.TripObject(str(crr_id),cui_area)
    trip_is_sim, = trip.eval('trip.%is_simulator%')
    
    if not trip_is_sim:
        cfhExtensions.show("Only possible on simulators")
        return

    (has_exception,
     brief, midbrief, debrief,
     fc, fp, fr, tl, tr,
     multisim,
     legs) = trip.eval("studio_assign.%has_sim_exception%",
                       "studio_assign.%sim_brief%",
                       "studio_assign.%sim_midbrief%",
                       "studio_assign.%sim_debrief%",
                       "studio_assign.%sim_need_fc%",
                       "studio_assign.%sim_need_fp%",
                       "studio_assign.%sim_need_fr%",
                       "studio_assign.%sim_need_tl%",
                       "studio_assign.%sim_need_tr%",
                       "studio_assign.%sim_is_multi%",
                       R.foreach(R.iter("iterators.leg_set",
                                        where="leg.%is_simulator%"),
                                 "leg.%udor%",
                                 "leg.%uuid%"))

    if form == None:
        comp = (fc, fp, fr, tl, tr)
        briefings = (brief, midbrief, debrief)

    if mode == "SET":
        if form == None:
            form = SimExceptionForm(comp, briefings, multisim)
            try:
                form()
            except CFC.CancelFormError, ef:
                Errlog.log("sim_exception_handler.py:: User canceled operation")
                return -1

        comp = form.comp
        briefings = form.briefings
        multisim = form.multisim

        _update_sim(legs, comp, briefings, multisim)

    elif mode == "REMOVE":
        if has_exception:
            _update_sim(legs)
        else:
            if marked_trips == False:
                # Do not display message for every marked trip
                cfhExtensions.show("No exception to remove")
            return
    else:
        raise Exception("Invalid mode")

    _update_booking(trip)
    
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    HF.redrawArea(cui_area)
    Cui.CuiSortArea(Cui.gpc_info,cui_area,Cui.CuiSortDefault)
