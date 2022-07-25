__version__ = "$Revision$"
"""
training_attribute_handler
Module for doing:
Various fucntions for setting
training attributes to trips, legs, etc, either via formor on assigning

@date: 09jul2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


import AttributesForm as AF
import HelperFunctions as HF
import Attributes
import carmusr.Assign as Assign
import Cui
import Gui
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions
import Errlog
import carmusr.modcrew as modcrew
import carmusr.application as application
import AbsTime
import RelTime
from AbsDate import AbsDate
from tm import TM
from sets import Set

import carmusr.tracking.TripTools as TripTools
MODULE = "training_attribute_handler"
SILENT_FORM = 1
ASSIGN_SILENT = 2
STOP_ON_ERROR = 4

class ObjAttrDict(dict):

    def _create_object(self):
        raise NotImplementedError
    def eval(self, *expr):
        if not self.has_key('object'):
            raise Exception('No roster object defined')
        return self.object.eval(*expr)

    def _my_getattr(self, attr):
        return None
    
    def __setattr__(self, attr, value):
        attr = str(attr).lower()
        self[attr] = value
    
    def __getattr__(self, attr):
        attr = str(attr).lower()
        try:
            my_attr = self._my_getattr(attr)
            if my_attr:
                return my_attr
            return self[attr]
        except:
            raise AttributeError('%s does not have attr %s'%(self.__class__.__name__, attr))
        
class AssignTrip(ObjAttrDict):
    def __init__(self):
        self._create_object()
        (self.valid,
         self.invalid_message,
         self.start_hb,
         self.is_flightdeck,
         self.is_training,
         self.id,
         self.training_set,
         self.start_utc) = self.eval('trip.%can_be_assigned_with_attribute%',
                                     'trip.%invalid_for_attribute_text%',
                                     'trip.%start_hb%',
                                     'fundamental.%flight_crew%',
                                     'crew_pos.%trip_has_assigned_trtl%',
                                     'crr_identifier',
                                     'attributes.%trip_set_var%',
                                     'trip.%start_utc%')
    def _create_object(self):
        self.object = HF.TripObject()
    def _my_getattr(self, attr):
        if attr == 'maincat':
            if self.is_training:
                return 'T'
            else:
                return ('C','F')[self.is_flightdeck]
        if attr == 'legs' and not self.has_key('legs'):
            self._get_legs()
        return None
    
        
    def _get_legs(self):
        legs, = self.object.eval(R.foreach(R.iter("iterators.leg_set",
                                                  sort_by='leg.%start_utc%',
                                                  where='not leg.%is_deadhead%'),
                                           "leg.%is_flight_duty%",
                                           "leg.%is_ground_duty%",
                                           "leg.%udor%",
                                           "leg.%fd_or_uuid%",
                                           "leg.%start_station%"))
        self.legs = []
        for (ix,  flight_duty, ground_duty, udor, fd, adep) in legs:
            # Store leg values
            leg = {'flight_duty':flight_duty,
                   'ground_duty':ground_duty,
                   'udor':udor,
                   'fd':fd,
                   'adep':adep,
                   'attribute':""}
            self.legs.append(leg)
            
    def is_assignable_rank(self, rank):
        # The training positions can always be assigned
        if rank.upper() in("FU","AU"):
            return True
        # Check for free slice of normal position
        okRank, = self.object.eval('crew_pos.%%trip_assigned_func%%("%s") > 0' % rank)
        return okRank
    
class DnDAssignTrip(AssignTrip):
    def __init__(self, src_id, src_area):
        self.object = HF.TripObject(str(src_id), src_area)
        AssignTrip.__init__(self)

    def _create_object(self):
        return

class AssignCrew(ObjAttrDict):
    def __init__(self):
        (self['id'],
         self['object'],
         self['area'],
         self['empno'])= (None, None, None, None)

    def __call__(self):
        try:
            crew_area, crew_id, _ = HF.roster_selection()
            self.area = crew_area
            self.id = crew_id
            self.object = HF.CrewObject(crew_id, crew_area)
            self.empno, = self.object.eval('crew.%employee_number%')
            return ""
        except HF.RosterSelectionError:
            return "Interrupted by user"

    def maincat(self, date):
        crew_maincat, = R.eval('crew.%maincat_for_rank%('+\
                               'crew_contract.%%crewrank_at_date_by_id%%("%s",%s))'%(self.id,
                                                                            date))
        return crew_maincat
    
class DnDAssignCrew(AssignCrew):
    def __init__(self, id, area):
        AssignCrew.__init__(self)
        self.area = area
        self.id = str(id)
        self.object = HF.CrewObject(str(id), area)
        self.empno, = self.object.eval('crew.%employee_number%')
    def __call__(self):
        pass
    
class Assigner(ObjAttrDict):
    def __init__(self, attribute=""):
        self._create_object()
        self.show_popup, = R.eval('fundamental.%debug_verbose_mode%')
        self.attribute = attribute
        self.according_to_need = False #according to need
        self.legs = []
        
    def _create_object(self):
        self.trip = AssignTrip()
        self.crew = AssignCrew()
        
    def assign(self):
        """
        Tries to assign trip with attribute
        """
        self.log_start()
        if not self.ok_to_assign():
            return 1
        if not self.get_training_attribute():
            return 1
        return self.assign_impl()
        
    def ok_to_assign(self):
        if not self.trip.valid:
            self.assignment_done('ok_to_assign',self.trip.invalid_message,True)
            return False
        message = self.crew()
        if message:
            self.assignment_done('ok_to_assign',message)
            return False
        if self.trip.maincat != 'T' and \
                self.trip.maincat != self.crew.maincat(self.trip.start_hb):
            self.assignment_done("ok_to_assign", "Crew has wrong maincat for trip.", True)
            return False
        return True


    def get_training_attribute(self):
        # training_codes
        set_var = self.trip.training_set
        training_codes = R.set(set_var).members()
        form_values = _get_attribute_form(training_codes=training_codes)
        if not form_values:
            self.assignment_done('get_training_attribute', "Cancelled by user" )
            return False
        self.attribute, _ = form_values
        return True
        
    def assign_impl(self):
        """
        Basic assign func.
        Implementation of the assign command.
        """
    
        if self.attribute == "NONE":
            # 'NONE' was selected in the form, we assign the trip without any
            # attributes
            try:
                self.cui_assign()
                return 0
            except Exception, e:
                Errlog.log(str(e))
                return 1
        # Ok, get assign rank and needed attribute if attribute is ""
        self.attribute, assignRank = _find_crew_position(self.trip.object,
                                                         self.attribute,
                                                         area=self.crew.area,
                                                         crew_id=self.crew.id)
        if self.attribute == "":
            # This means we tried to assign according to need, but none was found
            self.assignment_done(self.err_log_prefix,
                                 "There is no training need defined to assign", True)
            return 1
        if not assignRank:
            self.assignment_done(self.err_log_prefix,
                                 "A correct assignment couldn't be found", True)
            return 1
        if not self.trip.is_assignable_rank(assignRank):
            self.assignment_done(self.err_log_prefix,
                                 "The trip has no free position for %s" % assignRank, True)
            return 1
        # We should now have an attribute. 
        # Lets find legs in trip which should have attribute
        self.get_leg_with_attribute_to_tag_in_assign()
        try:
            # If crew need e.g. RELEASE and we assign a RELEASE flight,
            # the rule that crew needs a RELEASE-flight should not be violated.
            # Hence we set the attribute before assignment, and if user cancels
            # operation, we toggle it back.
            self.toggle_training_attributes(set_attr=True)
            self.cui_assign(rank=assignRank)
        except:
            # Remove training attribute due to cancel (or something else)
            self.toggle_training_attributes(set_attr=False)
            # Probably just cancelled by user
            self.assignment_done(self.err_log_prefix, "Cancelled by user")
            return 1
    
        done_mess = "%s assigned to trip in pos %s with attribute %s" %(self.crew.empno,
                                                                        assignRank,
                                                                        self.attribute)
        self.assignment_done(self.err_log_prefix, done_mess)
        R.param('training.%use_flight_buffer_p%').setvalue(False)
        return 0

    def cui_assign(self,rank=""):
        args = [Cui.gpc_info,
                self.crew.id,
                str(self.trip.id),
                Cui.CUI_ASSIGN_CRR_BY_ID_CHECK_LEGALITY]
        
        cui_func = Cui.CuiAssignCrrById
        if rank:
            args += [rank, rank]
            cui_func = Cui.CuiAssignCrrByIdAt
            
        cui_func(*args)
        Assign.remove_trip_if_no_need(self.trip.object)
        if not rank:
            self.assignment_done("assign_impl", "Assigned without attribute")
    
    def get_leg_with_attribute_to_tag_in_assign(self):

    
        # Function return -1 if max_legs do not apply
        # Lifus requires special handling when assigning according to need
        max_legs = -1

        if self.attribute == "LC":
            if self.according_to_need:
                max_legs, =  self.crew.object.eval('training.%nr_remaining_flights_by_attr_at_time%'+\
                                                   '("%s",%s)'%("LC",self.trip.start_utc))
            else:
                max_legs = 2
                
        self.legs = []
        # collect variables
        index = 1
        for leg in self.trip.legs:
            if max_legs >= 0 and index > max_legs: #If apply, tag first X legs
                break
            index += 1
            # Store leg values
            leg['attribute'] = self.attribute
            self.legs.append(leg)

    def toggle_training_attributes(self,set_attr=True):
        """
        Uses flag set_attr to either set training attribute to trip or remove
        all training attributes from trip
        """
        refresh_flight_duty = False
        refresh_ground_duty = False
        for leg  in self.legs:
            flight_duty = leg['flight_duty']
            ground_duty = leg['ground_duty']
            udor = leg['udor']
            fd = leg['fd']
            adep = leg['adep']
            refresh_flight_duty |= flight_duty
            refresh_ground_duty |= ground_duty 
            if set_attr:
                attr_vals = {"str":leg['attribute']}
                if flight_duty:
                    Attributes.SetCrewFlightDutyAttr(self.crew.id, udor, fd, adep,
                                                     "TRAINING", refresh=False,
                                                     **attr_vals)
                else:
                    Attributes.SetCrewGroundDutyAttr(self.crew.id, udor, fd,
                                                     "TRAINING", refresh=False,
                                                     **attr_vals)
            else:
                if flight_duty:
                    Attributes.RemoveCrewFlightDutyAttr(self.crew.id, udor, fd, adep,
                                                        "TRAINING", refresh=False)
                else:
                    Attributes.RemoveCrewGroundDutyAttr(self.crew.id, udor, fd,
                                                        "TRAINING", refresh=False)
                
        if refresh_flight_duty:
            Attributes._refresh("crew_flight_duty_attr")
        if refresh_ground_duty:
            Attributes._refresh("crew_ground_duty_attr")
        
    def assignment_done(self, function, message, popup_override=False):
        # We print a message to log, but also show a popup
        Errlog.log(function+':' + message)
        if self.show_popup or popup_override:
            cfhExtensions.show(message)
            
    def log_start(self):
        Errlog.log(self.err_log_prefix +
                   "Assigning a trip with attribute %s"%self.attribute)
        
    def _my_getattr(self, attr):
        
        if attr == "err_log_prefix":
            return MODULE +"::assign"
        return None  

class AccordingToNeedAssigner(Assigner):
    def __init__(self, attribute=""):
        Assigner.__init__(self, attribute)
        self.according_to_need = True
        self.attribute = ""
        R.param('training.%use_flight_buffer_p%').setvalue(True)
                
    def get_training_attribute(self):
        # training_codes
        self.attribute = ""
        return True
    
    def get_leg_with_attribute_to_tag_in_assign(self):
        Assigner.get_leg_with_attribute_to_tag_in_assign(self)
        try:
            self.attribute.index("LIFUS")
            self.lifus_according_to_need()
        except ValueError:
            pass
            
    def lifus_according_to_need(self):
        ##
        ## ZFTT is first lifus training and xlifus is the last lifus training legs
        ## Tag whole trip as lifus and then place ZFTT and XLIFUS where it fits
        (zftt_lifus_code,
         lifus_code,
         xlifus_code) = ("ZFTT LIFUS", "LIFUS", "X LIFUS")
        
        # Lookup need in rave
        (zftt_need,
         lifus_need,
         xlifus_need) = self.crew.object.eval('training.%nr_remaining_flights_by_attr_at_time%'+\
                                              '("%s",%s)'%(zftt_lifus_code,self.trip.start_utc),
                                              'training.%nr_remaining_flights_by_attr_at_time%'+\
                                              '("%s",%s)'%(lifus_code,self.trip.start_utc),
                                              'training.%nr_remaining_flights_by_attr_at_time%'+\
                                              '("%s",%s)'%(xlifus_code,self.trip.start_utc))
        
        if zftt_need+lifus_need+xlifus_need == 0:
            Errlog.log('training_attribute_handler::Could not find any separate lifus needs')
            return
    
        nr_legs = len(self.legs)
        # Start with assuming LIFUS
        leg_attrs = [lifus_code]*nr_legs
        # Start with ZFTT
        nr_zftt = min(nr_legs,zftt_need)
        leg_attrs[:nr_zftt] = [zftt_lifus_code]*nr_zftt

        # then lifus
        nr_lifus = max(min(nr_legs-nr_zftt,lifus_need),0)
        leg_attrs[nr_zftt:nr_zftt+nr_lifus] =  [lifus_code]*nr_lifus

        # then xlifus if possible
        nr_xlifus = max(min(nr_legs-nr_lifus-nr_zftt,xlifus_need),0)
        
        if (lifus_need == 0 and zftt_need == 0) and nr_xlifus>0:
            # We can fill with xlifus since other lifus complete, we must however fill all legs
            leg_attrs = [xlifus_code]*nr_legs
        elif nr_xlifus == xlifus_need:
            # It fits in current legs, lets fill 'em in
            leg_attrs[nr_legs-nr_xlifus:] =  [xlifus_code]*nr_xlifus
        else:
            # We cannot fill all xlifus, keep lifus tags set earlier
            pass
    
        # Set attribute in leg-collection
        for ix,leg in enumerate(self.legs):
            leg['attribute'] = leg_attrs[ix]    
        Errlog.log('training_attribute_handler::Assigning following LIFUS:'+\
                   ','.join([str(leg['attribute']) for leg in self.legs]))
        
class PreSelectedAssigner(Assigner):     
    def __init__(self, attribute=""):
        Assigner.__init__(self, attribute)
        self.according_to_need = False
        self.attribute = attribute
        
    def get_training_attribute(self):
        return True # No need to get new attribute
    
class ManualAttributeAssigner(Assigner):
    pass # no overloads yet

class DnDManualAttributeAssigner(ManualAttributeAssigner):
    def __init__(self, dst_crew_id, dst_area,
                 src_id, src_area):
        self.trip = DnDAssignTrip(src_id,src_area )
        self.crew = DnDAssignCrew(dst_crew_id,dst_area)
        ManualAttributeAssigner.__init__(self)


    def _create_object(self):
        return
    def assign(self):
        self.get_training_attribute()
        self.assign_impl()
        
class DnDNeedAttributeAssigner(AccordingToNeedAssigner):
    def __init__(self, dst_crew_id, dst_area,
                 src_id, src_area):
        self.trip = DnDAssignTrip(src_id,src_area )
        self.crew = DnDAssignCrew(dst_crew_id,dst_area)
        AccordingToNeedAssigner.__init__(self)

    def _create_object(self):
        return
    def assign(self):
        self.get_training_attribute()
        self.assign_impl()
#########################################################################
#
# Section 1. Assign trip with attribute code
#
########################################################################

def assign(accordingToNeed=False, withManualAttribute=False, attribute=""):
    """
    Assigns a trip and sets attributes.
    
    If accordingToNeed is True (default) training attributes are set
    on all legs in the trip according to need (from table crew_training_need).
    
    If accordingToNeed is False attributes on all legs in the trip are set
    according to selection form.
    """
    if not HF.isDBPlan():
        message = "Only available in databaseplan"
        Errlog.log('traning_attribute_handler::assign: '+message)
        Gui.GuiMessage(message)
        return 1
    assigner = None
    if accordingToNeed:
        assigner = AccordingToNeedAssigner()
    elif withManualAttribute:
        assigner = ManualAttributeAssigner()
    else:
        assigner = PreSelectedAssigner(attribute)

    return assigner.assign()
        

#######################################################
#
# Section 2: The main functions called by the user
#            when setting attribute
#######################################################

        
def remove_training_attribute(mode='TRIP'):
    FUNK = MODULE + "::removeAttribute: "
    leg_ids = []
    if mode.upper() == 'TRIP':
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        trip = HF.TripObject(area=area)
        leg_ids, = trip.eval(R.foreach('iterators.leg_set','leg_identifier'))
        leg_ids = [leg_id for ix, leg_id in leg_ids]
    else:
        Errlog.log(FUNK+"WARNING: Mode %s not implemented."%mode)
        return 1
    set_training_attribute(leg_ids, 'NONE')
    
def set_training_attribute(leg_objects=[],attribute="", area=None):
    """
    Sets a training attribute on either on a specified range of legs.
    Work on a list of LegObjects or leg_ids
    """
    FUNK = MODULE + "::setAttribute: "

    Errlog.log(FUNK + "Setting attribute on a range of legs.")

    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    Cui.CuiSyncModels(Cui.gpc_info)
    if area is None:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    # Make sure we operate on LegObjects
    for ix in xrange(len(leg_objects)):
        leg = leg_objects[ix]
        if not isinstance(leg, HF.LegObject):
            leg_objects[ix] = HF.LegObject(str(leg), area)

    if not leg_objects or not attribute:    
        #We need to get attribute from form!
        form_values = _get_legs_and_attribute_form(area, verbose=verbose)
        if not form_values:
            Errlog.log(FUNK + "No values from form, "+\
                       "User cancelled operation or no change.")
            return 1
        leg_objects, attribute = form_values

    excepted_attr = attribute in Set(["CC INSTR AUSC", "CC INSTR EXAM", "CC INSTR SEN", "FAM FLIGHT", "LINE FLIGHT", "LINE FLIGHT SCC"])
    if application.isPlanning and not excepted_attr: # Only check need in Planning, ok for tracking to overbook
        leg_objects, messages = _check_legs_for_need(area,leg_objects, attribute)
        if messages:
            Gui.GuiMessage("Unable to set/remove training attribute %s:\n\n"%attribute+\
                           "\n".join(messages))
    if not leg_objects:
        Errlog.log(FUNK + "Not enough booked in any positions")
        return 1
    #Work the magic!
    _update_legs(area,leg_objects, attribute,  verbose=verbose)
    Cui.CuiSyncModels(Cui.gpc_info)
    return 0


def set_instructor_tag(mode="",attribute="", area=Cui.CuiWhichArea, flags = 0):
    """
    Set INSTRUCTOR Attribute to trip, changes pos of instructor if need by student
    """
    FUNK = "::tag_trip_as_instructor, "
    silent = 0|flags
    mode = mode.upper()
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    Cui.CuiSyncModels(Cui.gpc_info)
    if mode == "TRIP":
        trip = HF.TripObject(area=area)
        leg_ids, = trip.eval(R.foreach('iterators.leg_set','leg_identifier'))
        leg_ids = [leg_id for ix, leg_id in leg_ids]
    elif mode == "MARKED":
        leg_ids = Cui.CuiGetLegs(Cui.gpc_info,area, "marked")
    elif mode in ("ALL","PUBLISH"):
        where_expr = ['leg.%in_pp%',
                      'leg.%is_active_flight%',
                      'leg.%has_any_training_code_any_crew%']

        if mode == "PUBLISH":
            Errlog.log(MODULE +"::tag_trip_as_instructor, "+\
                       "will set INSTRUCTOR tag to"+\
                       " published crew's legs where needed.")
            silent |= ASSIGN_SILENT #Silent and do not stop on error
            # At publish the requirement is stricter, to not change roster in a way affecting legality
            where_expr = ['leg.%in_publ_period%',
                          'not leg.%has_instructor_code%',
                          'training.%instructor_to_be_tagged_at_publish%']

        else:
            silent |=ASSIGN_SILENT|STOP_ON_ERROR# Silent but stop on error
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        
        leg_ids, = R.eval('default_context',
                          R.foreach(R.iter('iterators.leg_set',
                                           where = tuple(where_expr)),
                                    'leg_identifier'))
        leg_ids = [leg_id for (ix, leg_id) in leg_ids]
    else:
        Errlog.log(MODULE +"::tag_trip_as_instructor, "+\
                   "Mode %s not supported"%mode)
        return 1
    
    if not leg_ids:
        Errlog.log(MODULE + FUNK+  "No marked trips")
        return 1
    crew_cached_legs, message = _get_attributes_and_positions_for_INSTRUCTOR(leg_ids,
                                                                             area,
                                                                             attribute,
                                                                             silent=silent)
    if not crew_cached_legs and mode == "TRIP":
        if not silent&ASSIGN_SILENT:
            cfhExtensions.show("Operation aborted!\n\n"+\
                               message+\
                               "\nPlease address issue and tag trips again!",
                               title="    Unable to tag as instructor")
        return 1
    if not crew_cached_legs and mode == "MARKED" and message:
        if not silent&ASSIGN_SILENT:
            find_str=message.find("(NotValid)")
            if find_str != -1:
                cfhExtensions.show("No all tags set!\n"+\
                                   "Please check INSTRUCTOR qualification (CRM/OPT).",
                                   title=" Unable to tag as instructor")
    # Ok, now we have leg(s) to set INSTRUCTOR to,training attribute(s)
    # and desired position(s)
    _update_legs_INSTRUCTOR(area, crew_cached_legs)
    Cui.CuiSyncModels(Cui.gpc_info)
    return 0
    
#######################################################
#
# Section 3: General helper functions
#
#######################################################
def _get_attributes_and_positions_for_INSTRUCTOR(leg_ids, area,
                                                 attribute, silent=0):
    """
    Loops through legs and checks for students and instructors!
    """
    FUNK = '_get_attributes_and_positions_for_INSTRUCTOR'
    crew_cached_legs = {}
    message = None
    for leg_id in leg_ids:
        selected_pos, selected_attribute = -1, 'NONE'
        leg_object = HF.LegObject(str(leg_id) ,area)
        (crew_id,
         crew_empno,
         instr_maincat,
         is_sim,
         can_have_attr,
         assigned_pos,
         existing_ok_training,
         leg_fd) = leg_object.eval('crew.%id%',
                                   'crew.%extperkey_at_date%(leg.%start_hb%)',
                                   'crew.%main_func_at_date%(leg.%start_hb%)',
                                   'leg.%is_simulator%',
                                   'leg.%can_have_attribute%',
                                   'crew_pos.%assigned_pos%',
                                   'training.%instructor_for_training_type%',
                                   'leg.%flight_descriptor%')

        if not can_have_attr and attribute != 'NONE': #All legs can have no attribute
            continue
        # If simulator, then we only need to set position to 4
        elif is_sim and attribute != 'NONE':
            selected_pos, =  leg_object.eval('training.%simulator_instructor_pos%')
            selected_attribute = 'SIM INSTR' #Dummy
        # Crew is already assigned as ok instructor
        elif attribute == "" and existing_ok_training is not None and existing_ok_training != "FLT INSTR OL":
            selected_pos = assigned_pos
            selected_attribute = existing_ok_training
        # If no attribute given, lets get it from students
        elif attribute == "":
            rave_expr = ['training.%find_instructor_pos%('+\
                         'leg.%training_code_safe%,'+\
                         'leg.%is_long_haul_aircraft%,'+\
                         'leg.%qual%,'+\
                         'leg.%start_hb%)',
                         'leg.%training_code_safe%',
                         'crew.%extperkey_at_date%(leg.%start_hb%)']
            # We want student that have same mainfunc as instructor!
            where_expr = ('leg.%has_training_code%',
                          'not training.%has_acceptable_companion%',
                          'crew.%%main_func_at_date%%(leg.%%start_hb%%) = "%s"'%instr_maincat,
                          'crew.%%id%% <> "%s"'%crew_id)
            #Eval needed ravevalues
            raw_positions = leg_object.eval(R.foreach('equal_legs',
                                                      R.foreach(R.iter('iterators.leg_set',
                                                                       where=where_expr),
                                                                *rave_expr)))[0][0][1]

            # Ok, now we got the students training attribute
            # and needed instructor positions
            # CC: AP TRAINING > RELEASE > X SUPERNUM > SUPERNUM
            # FD: ILC > LC
            positions = {}
            training_exists = False
            possible_instructor = False
            for tmp,pos,training,empno in raw_positions:
                training_exists = True
                if pos:
                    acceptable_companion, = leg_object.eval('training.%%possible_acceptable_companion%%("%s")'%training)
                    if acceptable_companion:
                        positions[training] = pos
                        possible_instructor = True
                        
            training_order = ('AP TRAINING', 'RELEASE', 'X SUPERNUM', 'SUPERNUM', "ILC", "LC")
            if len(positions) > 1:
                for t_type in training_order:
                    if t_type in positions:
                        selected_pos = positions[t_type]
                        selected_attribute = t_type
                        break
            # We haven't found a position yet, we take any given
            if selected_attribute == "NONE":
                for attr in positions:
                    selected_pos = positions[attr]
                    selected_attribute = attr
                    break

            # If we're planning, check if the position is available
            if application.isPlanning and selected_pos != assigned_pos:
                available_pos, = leg_object.eval('crew_pos.%%leg_available_pos%%(%s)'%selected_pos)
            else:
                available_pos = True

            if not training_exists or not possible_instructor or not available_pos:
                if message is None:
                    message = ""
                else:
                    message += "\n"
            if not training_exists:
                message += "No training for any crew on flight %s"%leg_fd
            elif not possible_instructor:
                message += "%s not valid as instructor for any crew on flight %s (NotValid)" %(crew_empno, leg_fd)
            elif not available_pos:
                message += "Not enough booked value in pos %s on flight %s" %(selected_pos, leg_fd)
                selected_pos = -1
            
            if message is not None:
                Errlog.log(MODULE +":: Tag as instructor: "+message.replace("\n"," "))
            else:
                pass
        else:
            # see if we are removing instructor tag
            old_attr, = leg_object.eval('leg.%instructor_code_safe%')
            if old_attr != 'NONE' and attribute == 'NONE':
                # we are removing instructor tag, set crew back in original pos
                selected_pos, = leg_object.eval('attributes.%leg_instructor_prev_pos%')
                selected_attribute = 'NONE'
            else:
                continue  #No attr to remove on this leg
        # Store needed updates, i.e. cancel in _select_attribute_form will cancel
        # all operation, no update done
        if selected_pos > -1:
            if crew_cached_legs.has_key(crew_id):
                crew_cached_legs[crew_id].append((leg_object,selected_pos,selected_attribute))
            else:
                crew_cached_legs[crew_id] = [(leg_object,selected_pos,selected_attribute)]
        else:
            # This leg had no training to be instructor for
            continue
    return crew_cached_legs, message

def _select_attribute_form(pos_and_attributes,student_empnos, empno, start_t, silent=0):
    attributes=dict([(attr, pos) for pos,attr in pos_and_attributes])
    cancel_text = ("Cancel will skip INSTRUCTOR tag,\n"+\
                   "this will become an illegality.\n",
                   "Cancel will cancel whole operation!\n")[bool(not silent&ASSIGN_SILENT or \
                                                               silent&STOP_ON_ERROR)]
    #              Bit ugly silent-flag handling, but it works
    try:
        attributes_form = AF.SelectAttributeForm(attributes,'Please select attribute!',
                                                 "Multiple students on training on flight\n"+\
                                                 "starting %s (UTC)\n"%start_t+\
                                                 "Student empnos: "+\
                                                 ", ".join(student_empnos)+"\n"+\
                                                 "Instructor empno: %s\n"%empno+\
                                                 cancel_text +\
                                                 "Select attribute for INSTRUCTOR\n")
        attributes_form() #show form
        attribute = attributes_form.attribute
    except AF.CancelFormError:
        Errlog.log('training_attribute_handler::User cancelled form')
        return None
    else:
        return (attributes[attribute],attribute)
    
def _get_attribute_form(old_attr='NONE',
                        rangeOption=False, training_codes=[], form_label=""):
    # Show dialog
    try:
        attributes_form = AF.AttributesForm(old_attr,
                                            training_codes,
                                            rangeOption,
                                            "Attributes Setting",
                                            label=form_label)
        attributes_form()
    except AF.CancelFormError:
        Errlog.log('training_attribute_handler::User cancelled form')
        return None
    # We want to assign the trip regardless of whether an attribute was set,
    # but not if Cancel was pressed.
    else:
        # range is not used in this case, we set attribute on all legs
        return attributes_form.attribute,attributes_form.range_int


def _get_legs_and_attribute_form(area, verbose=False):
    """
    returns a tuple with leg_objects to work on and choosen attribute
    """
    FUNK = MODULE+"::_get_legs_and_attribute_form"
    leg_object = HF.LegObject(area=area)
    trip_object = HF.TripObject(area=area)
    #crew_obj = HF.CrewObject(area=area)
    (crew_id, valid_leg, is_sim,
     old_attr, training_codes, multiple_sim_duties) = _get_leg_values(leg_object, verbose)
    
    if not valid_leg:
        err_mess, = R.eval('leg.%invalid_for_attribute_text%')
        cfhExtensions.show(err_mess)
        Errlog.log(FUNK + err_mess)
        return None

    # Set form label for sim with multiple duties
    if is_sim and multiple_sim_duties:
        form_label = "Range: Duty"
    else:
        form_label = ""
    
    # Show dialog
    form_values = _get_attribute_form(old_attr=old_attr,
                                      rangeOption=not is_sim,
                                      training_codes = training_codes,
                                      form_label = form_label)
    if form_values is None or \
           (form_values[0] == old_attr and form_values[1] == AF.LEG):
        if verbose:
            Errlog.log(FUNK + "No change.")
        return None
    else:
        attribute, range = form_values
        Errlog.log(FUNK + "Setting attribute to: %s for range: %s" %(attribute,
                                                                     AF.RANGES[range]))
        if range == AF.LEG:
            obj = leg_object
        elif range == AF.TRIP:
            obj = trip_object
        else:
            obj = None
            crew_id = None
        leg_objects = _get_legs(area,obj, verbose=verbose) # Get needed leg variables

        # Only set simulator attributes for legs in same duty
        if is_sim:
            leg_objects = _get_same_duty_legs(leg_objects, leg_object)

        return leg_objects, attribute

def _get_same_duty_legs(leg_objects, leg_object):
    duty_nr = leg_object.eval('attributes.%duty_number%')[0]
    legs = []
    for leg in leg_objects:
        dtnr = leg.eval('attributes.%duty_number%')[0]
        if dtnr == duty_nr:
            legs.append(leg)
    return legs

def _get_leg_values(leg_object, verbose=False):
    """
    Returns various values for a clicked leg.
    """
    FUNK = MODULE + "::_getValues: "
    leg_vars = leg_object.eval('crew.%id%',
                               'crew.%is_pilot%',
                               'leg.%can_have_attribute_assigned%',
                               'leg.%is_simulator%',
                               'leg.%training_code_safe%',
                               'attributes.%set_var%',
                               'attributes.%trip_has_multiple_sim_duties%'
                               )
    (crewId, FC, valid, is_sim,  attr, set_var, multiple_sim_duties) = leg_vars

    training_codes = R.set(set_var).members()
    if verbose:
        Errlog.log(FUNK + "crewId: %s, FC: %s, attr: %s" %(crewId, FC, attr))
    
    return (crewId, valid, is_sim, attr, training_codes, multiple_sim_duties)
    
    
def _get_legs(area,object, verbose=False):
    """
    Returns the legs in the wanted range.

    'area' is needed to re-set default context to 'window' for marked legs when
    'object' is None.
    """
    FUNK = MODULE + "::_getLegs: "
    Errlog.log(FUNK + "Getting legs to set attribute for")
   
    legs = []
    if (object is None):
        # This means we want all marked legs
        if verbose:
            Errlog.log(FUNK + "Getting values for marked legs in window")
        leg_ids = Cui.CuiGetLegs(Cui.gpc_info, area, "marked")
    else:
        leg_ids, = object.eval(R.foreach("iterators.leg_set",'leg_identifier'))
        leg_ids = [leg_id for ix, leg_id in leg_ids]
        
    for leg_id in leg_ids:
        leg = HF.LegObject(str(leg_id),area=area)
        legs.append(leg)
        
    return legs

######## UPDATE FUNCTIONS #########################################
def _update_legs_INSTRUCTOR(area, crew_cache):
    refresh_ground_duty = False
    refresh_flt_duty = False

    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, area, "marked") #Store marked legs
    HF.unmarkLegs(area, marked_legs) #Unmark legs
    for crew_id in crew_cache:
        #crew_object = HF.CrewObject(str(crew_id),area)
        leg_objects = []
        for leg_object, selected_pos, selected_attribute in crew_cache[crew_id]:
            old_attr, = leg_object.eval('leg.%instructor_code_safe%')
            current_pos, = leg_object.eval('crew_pos.%assigned_pos%')
            
            if selected_pos != -1 and current_pos != selected_pos:
                #convert position to rank
                assign_rank = HF.pos2rank(selected_pos)
                leg_object.assign_rank = assign_rank
                if application.isTracking:
                    _update_crew_position_for_cct(area,
                                                  leg_object,
                                                  selected_attribute,
                                                  assign_rank=assign_rank)
            leg_objects.append(leg_object)
                        
            # store current pos if we remove instructor!
            if old_attr == 'NONE' and selected_attribute != 'NONE':
                _update_attribute_for_leg(leg_object,
                                          "INSTRUCTOR",
                                          current_pos,
                                          old_attr) 
            (refresh1, refresh2) = _update_attribute_for_leg(leg_object,
                                                             "INSTRUCTOR",
                                                             selected_attribute,
                                                             old_attr)
            
            refresh_flt_duty = refresh_flt_duty or refresh1
            refresh_ground_duty = refresh_ground_duty or refresh2
        if application.isPlanning:
            _update_crew_position_for_ccr(area,
                                          leg_objects)
    HF.markLegs(area, marked_legs)
    TripTools.tripClean(area, marked_legs)
    if refresh_flt_duty:
        Attributes._refresh("crew_flight_duty_attr")
    if refresh_ground_duty:    
        Attributes._refresh("crew_ground_duty_attr")

def _update_legs(area,leg_objects, attribute, verbose=False):
    """
    update attribute and position
    """
    
    refresh_ground_duty = False
    refresh_flt_duty = False

    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, area, "marked") #Store marked legs
    HF.unmarkLegs(area, marked_legs) #Unmark legs

    for leg_object in leg_objects:
        (old_attr, valid, deadhead,
         crew_id) = leg_object.eval('leg.%training_code_safe%',
                                    'attributes.%leg_can_have_attribute%'+\
                                    '("%s")'% attribute,
                                    'leg.%is_deadhead%',
                                    'crew.%id%')

        if (attribute == old_attr) or not valid or deadhead:
            # We only write data when necessary.
            continue
        
        old_rank = ""
        # place back crew in old position!
        if attribute == 'NONE' and old_attr != 'NONE':
            # We will remove attribute, retrive previous position before
            prev_pos, = leg_object.eval('attributes.%leg_training_prev_pos%')

            if prev_pos != -1:
                old_rank = HF.pos2rank(prev_pos)
        # store current pos if we remove training!
        if old_attr == 'NONE' and attribute != 'NONE':
            current_pos, = leg_object.eval('crew_pos.%assigned_pos%')
            _update_attribute_for_leg(leg_object,
                                      "TRAINING",
                                      current_pos,
                                      old_attr)
        # Update the attribute
        (refresh1, refresh2) = _update_attribute_for_leg(leg_object,
                                                         "TRAINING",
                                                         attribute,
                                                         old_attr) 
        
        refresh_flt_duty = refresh_flt_duty or refresh1
        refresh_ground_duty = refresh_ground_duty or refresh2

        # update crew position due to new attribute
        if application.isTracking: # single leg position change
            _update_crew_position_for_cct(area,
                                          leg_object,
                                          attribute, 
                                          verbose=verbose,
                                          assign_rank=old_rank)
    if application.isPlanning: # change full trip position
        _update_crew_position_for_ccr(area,
                                      leg_objects,
                                      verbose=verbose)
                    
    if refresh_flt_duty:
        Attributes._refresh("crew_flight_duty_attr")
    if refresh_ground_duty:
        Attributes._refresh("crew_ground_duty_attr")
    HF.markLegs(area, marked_legs) #Reset leg marking!
    return 

def _update_attribute_for_leg(leg_object, attribute, attr_val, old_attr_val):
    """
    Operates on assigned leg objects
    """
    # Old pos is original pos, copy it along if we remove attributes
    old_pos = {"TRAINING":"attributes.%leg_training_prev_pos%",
               "INSTRUCTOR":"attributes.%leg_instructor_prev_pos%"}.get(attribute,-1)
    (crew_id, is_sim, is_ol123, is_olntc17, udor,
     adep, fd_uuid,old_pos) = leg_object.eval('crew.%id%',
                                              'leg.%is_simulator%',
                                              'leg.%is_ol123%',
                                              'leg.%is_cc_inst_activity_ntc17%',
                                              "leg.%udor%",
                                              "leg.%start_station%",
                                              "leg.%fd_or_uuid%",
                                              old_pos)
    refresh_ground_duty = False
    refresh_flt_duty = False
    if old_attr_val != "NONE":
        if is_sim or is_ol123 or is_olntc17:
            refresh_ground_duty = True
            Attributes.RemoveCrewGroundDutyAttr(crew_id,
                                                udor, fd_uuid,
                                                attribute, refresh=False)

            
        else:
            refresh_flt_duty = True  
            Attributes.RemoveCrewFlightDutyAttr(crew_id,
                                                udor, fd_uuid, adep,
                                                attribute, refresh=False)

    if (attr_val != "NONE"):
        if isinstance(attr_val,str):
            typ = 'str'
        elif isinstance(attr_val,int):
            typ = 'int'
        elif isinstance(attr_val,AbsTime.AbsTime):
            typ = 'abs'
        elif isinstance(attr_val,RelTime.RelTime):
            typ = 'rel'
        else:
            raise ValueError, "Undefiended type for attribute %s"%type(attr_val)
        attr_vals = {typ:attr_val}

        if old_pos > 0 and typ != 'int': #Don't overwrite if we set int-values!
            attr_vals['int'] = old_pos
            
        if is_sim or is_ol123 or is_olntc17:
            refresh_ground_duty = True
            Attributes.SetCrewGroundDutyAttr(crew_id,
                                             udor, fd_uuid,
                                             attribute,
                                             refresh=False,
                                             **attr_vals)
        else:
            refresh_flt_duty = True
            Attributes.SetCrewFlightDutyAttr(crew_id,
                                             udor, fd_uuid, adep,
                                             attribute,
                                             refresh=False,
                                             **attr_vals)
                    
    if (old_attr_val != "NONE" or attr_val != "NONE"):
        modcrew.add(crew_id)

    return (refresh_flt_duty, refresh_ground_duty)


def _update_crew_position_for_cct(area,
                                  leg_obj,
                                  attribute,
                                  assign_rank="",
                                  verbose=False):
    
    #CCT can change to individual legs
    if not assign_rank:
        attribute_validated, assign_rank = _find_crew_position(leg_obj,
                                                               attribute)    
    if assign_rank:
        leg_id, maincat = leg_obj.eval('leg_identifier','crew.%main_func%')
        HF.markLegs(area, [leg_id])
        flags = 16|Cui.CUI_CHANGE_ASS_POS_SUPPRESS_DIALOGUE
        #16 makes function work on segment rather than CRR
        if assign_rank in ("TL","TR"):
            maincat = "T"
        Cui.CuiChangeAssignedPosition({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                      Cui.gpc_info,
                                      maincat,
                                      assign_rank,
                                      flags)
        
        HF.unmarkLegs(area, [leg_id])
                
 
        if verbose:
            Errlog.log(MODULE + "::_update_crew_position_for_cct: changing position to "+\
                       "%s due to attribute %s" % (assign_rank,attribute_validated ))
    else:
        if verbose:
            Errlog.log(MODULE +  \
                       "::_update_crew_position: unable to determine new rank for attribute")
            
def _update_crew_position_for_ccr(area,
                                  leg_objects,
                                  verbose=False):
    #CCR must work on trips rather than single legs
    touched_trips = {}
    touched_trips_assign_rank = {}
    # Build 'trips'
    for leg_object in leg_objects:
        #Just to be sure 
        if not hasattr(leg_object,'assign_rank'):
            if verbose:
                Errlog.log(MODULE + "::_update_crew_position_for_ccr, no need for change to  "+\
                           "Crew id: %s, Legs start utc : %s"%\
                           (leg_object.eval('crew.%id%','leg.%start_utc%')))
            continue
        
        if verbose:
            Errlog.log(MODULE + "::_update_crew_position_for_ccr, Will change position to %s for "+\
                       "Crew id: %s, Legs start utc : %s"%\
                       (leg_object.assign_rank, leg_object.eval('crew.%id%','leg.%start_utc%')))
        trip_id, leg_id, maincat = leg_object.eval('crr_identifier',
                                                   'leg_identifier',
                                                   'crew.%main_func%')
        
        if touched_trips.has_key(trip_id):
            continue #trip already accounted for by other leg
        else:
            touched_trips[trip_id] = [leg_id]
            touched_trips_assign_rank[trip_id] = (leg_object.assign_rank,maincat)

    if touched_trips:
        for trip_id in touched_trips:
            assign_rank, maincat = touched_trips_assign_rank[trip_id]
            #HF.markLegs(area, touched_trips[trip_id])
            Cui.CuiSetSelectionObject(Cui.gpc_info, area , Cui.CrrMode, str(trip_id))
            Cui.CuiMarkCrrs(Cui.gpc_info, area, "object", Cui.CUI_MARK_SET)
            if assign_rank in ("TL","TR"):
                maincat = "T"
            Cui.CuiChangeAssignedPosition({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                          Cui.gpc_info,
                                          maincat,
                                          assign_rank,
                                          Cui.CUI_CHANGE_ASS_POS_SUPPRESS_DIALOGUE)
            Cui.CuiMarkCrrs(Cui.gpc_info, area, "object", Cui.CUI_MARK_CLEAR)
        Cui.CuiSyncModels(Cui.gpc_info) #DO NOT remove this sync, removing will cause studio crash

            
def _check_legs_for_need(area,leg_objects, attribute):
    # Return legs where trip has unbooked seats in needed position
    # Checks whole trip for each leg
    ok_leg_objects = []
    trips_without_open_seats = []
    messages = []
    if attribute == 'NONE':
        for leg_object in leg_objects:
            old_attr, = leg_object.eval('leg.%training_code_safe%')
            if old_attr != 'NONE':
                prev_pos,assigned_pos = leg_object.eval('attributes.%leg_training_prev_pos%',
                                                         'crew_pos.%assigned_pos%')
                if prev_pos != -1 and prev_pos != assigned_pos: # no need to change is chaning
                                                                # to the same
                    old_rank = HF.pos2rank(prev_pos)
                    setattr(leg_object, "assign_rank",old_rank) #Reset pos if needed
        return leg_objects, [] #always remove attribute
    for leg_object in leg_objects:
        (crew_id,
         deadhead,
         valid,
         empno,
         trip_start_utc,
         trip_id,
         assigned_func) = leg_object.eval('crew.%id%',
                                          'leg.%is_deadhead%',
                                          'attributes.%%leg_can_have_attribute%%("%s")'%attribute,
                                          'crew.%extperkey%',
                                          'trip.%start_utc%',
                                          'crr_identifier',
                                          'crew_pos.%assigned_function%')
        if deadhead or not valid:
            continue
        open_pos_exists = False
        assign_rank_range = ('FU', 'AU')

        if trip_id not in trips_without_open_seats:
            tmp, assign_rank =  _find_crew_position(leg_object,
                                                    attribute)
            if assign_rank == assigned_func:
                ok_leg_objects.append(leg_object)
                continue
            open_pos_exists, = leg_object.eval('crew_pos.%%trip_has_open_func%%("%s")'%assign_rank)
            if open_pos_exists or assign_rank in assign_rank_range: #Always room in FU
                #Store rank, so we don't need lookup again!
                setattr(leg_object, "assign_rank",assign_rank)
                ok_leg_objects.append(leg_object)
        # Only store one message per trip
        if (not open_pos_exists and assign_rank not in assign_rank_range) \
               and trip_id not in trips_without_open_seats:
            message = "Crew Empno %s, not enough need for %s in all legs in trip starting %s"%\
                      (empno, ["", "for %s"%assign_rank][bool(assign_rank)], trip_start_utc)
            trips_without_open_seats.append(trip_id)
            messages.append(message)
            Errlog.log(message)
            
    return ok_leg_objects, messages
        
######### FIND FUNCTIONS ########################################
def _find_crew_position(chain_object, attribute, area=None, crew_id=""):
    verbose = False
    """
    Find crew position
    if attribute == "", then training_attribute_validated will be needed attribute
    from training requirements!
    """
    # Find assignment position
    if isinstance(chain_object,HF.LegObject):
        # This is a leg, we are trying to modify assigned object
        ac_qual = 'leg.%qual%'
        start_hb = 'leg.%start_hb%'
        is_lh = 'leg.%is_long_haul_aircraft%'
        is_sim = 'leg.%is_simulator%'
        simtype = 'leg.%group_code%'
        is_ol456 = 'leg.%is_ol456%'
        is_ol123 = 'leg.%is_ol123%'
        is_olntc17 = 'leg.%is_cc_inst_activity_ntc17%'
        start_utc= 'leg.%start_utc%'
        end_utc= 'leg.%end_utc%'
        first_open = 1
    else:
        # This is a trip, we are trying to assign
        ac_qual = 'trip.%first_active_ac_qln%' 
        start_hb = 'trip.%start_hb%'
        is_lh = 'trip.%with_long_haul_ac%'
        is_sim = 'trip.%is_simulator%'
        simtype = 'trip.%group_code%'
        is_ol456 = 'trip.%is_ol456%'
        is_ol123 = 'trip.%is_ol123%'
        is_olntc17 = 'trip.%is_cc_inst_activity_ntc17%'
        start_utc= 'trip.%start_utc%'
        end_utc= 'trip.%end_utc%'
        first_open = -1

    if verbose:
        print "_find_crew_position called "

    _first_open = 'studio_assign.%first_open_position%'
    rostered = 'fundamental.%is_roster%'
    (ac_qual,start_hb,
     is_lh,is_sim,simtype,
     is_ol456, is_ol123, is_olntc17, _first_open,
     rostered, start_utc, end_utc) = chain_object.eval(ac_qual,
                                   start_hb,
                                   is_lh,
                                   is_sim,
                                   simtype,
                                   is_ol456,
                                   is_ol123,
                                   is_olntc17,
                                   _first_open,
                                   rostered, 
                                   start_utc,
                                   end_utc)

    supervising_instructor_rank = 'training.%%find_supervising_instructor_rank%%("%s")'%(attribute)
    (supervising_instructor_rank,) = chain_object.eval(supervising_instructor_rank)
    if supervising_instructor_rank == 'FU':
        _first_open = 4
    elif supervising_instructor_rank == 'FR':
        _first_open = 3

    if (first_open < 0):
        # If there is no _first_open, check the course on the crew and assign in the supernum position with a 
        # crew pos set to "FU" if the course block is supernum
        is_supernum = _is_supernum(attribute, crew_id, start_utc, end_utc, area)
        if is_supernum:
            _first_open = 4 
        # We only try and use first available position when assigning trip
        first_open = _first_open

    attr_expr = 'training.%%training_attribute_validated%%("%s", %s)'%(ac_qual,
                                                                       start_hb)
    if (not rostered) and crew_id and (area is not None):
        chain_object = HF.CrewObject(crew_id,area)
    if attribute == "":
        attributeValidated, = chain_object.eval(attr_expr)
    else:
        attributeValidated = attribute
    if verbose:
        print "attrib validated", attribute, attributeValidated
        
    pos_expr = ('training.%%find_trainee_pos%%("%s", %s, "%s", %s, %s)'%(attributeValidated,
                                                                         is_lh,
                                                                         ac_qual,
                                                                         start_hb,
                                                                         first_open),
                'training.%%find_simulator_rank%%(%s,"%s","%s")'% (start_hb,
                                                                   attributeValidated,
                                                                   simtype),
                'crew.%%rank_at_date%%(%s)'%start_hb)
    
    
    (traineePos, simRank, crewRank) = chain_object.eval(*pos_expr)
    if verbose:
        print "final", is_sim, rostered, traineePos, simRank, crewRank

    if attribute == 'NONE':
        if is_ol123:
            assignRank = False
        else:
            assignRank = crewRank
    elif attributeValidated:
        if is_sim:
            if rostered:
                current_assigned_pos, = chain_object.eval('crew_pos.%assigned_pos%')
                assigned_rank = HF.pos2rank(current_assigned_pos)
                # We should keep the assigned_rank for OPC since it can be a lower assignment.
                # For other cases we should move the position.
                if simRank in ("FC", "FP"):
                    assignRank = assigned_rank
                else:
                    assignRank = simRank
            else:
                assignRank = simRank
        elif attributeValidated == "FLT INSTR OL":
            assignRank = supervising_instructor_rank
        elif traineePos:
            # Found a valid position to assign in
            assignRank = HF.pos2rank(traineePos)
        elif is_ol456:
            assignRank = "FU"
        elif is_ol123:
            if attributeValidated == "IO SUPERVISOR":
                assignRank = "AU"
            else:
                assignRank = "TR"
        else:
            assignRank = False
    else:
        assignRank = False
    if verbose:
        print "return", attributeValidated, assignRank

    return attributeValidated, assignRank

def _is_supernum(attribute, crew_id, start_utc, end_utc, area):
    if attribute =="SUPERNUM":
        return True
    if crew_id == None or crew_id == "":
        return False
    crew_object = HF.CrewObject(crew_id,area) 

    no_of_courses, = crew_object.eval("training.%count_crew_course_name%")
    if no_of_courses <= 0:
        return False;
    ix = 1
    while(ix <= no_of_courses):
        course_name, = crew_object.eval("training.%%course_name_ix%%(%s)"%ix)
        ix+=1
        course_block_name, = crew_object.eval('training.%%course_activity_course_block%%("%s",%s,%s)'%(course_name,start_utc,end_utc))
        if course_block_name == "SUPERNUM":
            return True
    
    return False
    

"""
 Functionality for special training companions.
"""

class SpecialCompanionBaseDuty:
    SC_ATTR = "SPEC COMP"
    INST_ATTR = "INSTRUCTOR"
    STUD_ATTR = "TRAINING"

class SpecialCompanionFlightDuty(SpecialCompanionBaseDuty):
    src_table = "crew_flight_duty_attr"
    dst_table = "flight_leg_attr"
       
    def src_leg_id(self, entry):
        return entry.cfd.leg._id
    
    def src_crew_id(self, entry):
        return entry.cfd.crew.id
    
    def src_attr(self, entry):
        return entry.attr.id
    
    def dst_leg_id(self, entry):
        return entry.leg._id
     
    def dst_attr(self, entry):
        return entry.attr.id
    
    def set_special_companion_attr(self, leg_id, instructors, students):
        udor = leg_id.split("+")[0]
        fd = leg_id.split("+")[1]
        adep = leg_id.split("+")[2]
        value_str = ','.join(sorted(instructors)) + ':' + ','.join(sorted(students))
        attr_vals = {"str": value_str}
        try:
            Attributes.SetFlightLegAttr(udor, fd, adep, self.SC_ATTR, refresh=False, **attr_vals)
        except:
            Errlog.log("training_attribute_handler: Could not store special flight duty companions.")
            
    def remove_special_companion_attr(self, leg_id):
        udor = leg_id.split("+")[0]
        fd = leg_id.split("+")[1]
        adep = leg_id.split("+")[2]
        try:
            Attributes.RemoveFlightLegAttr(udor, fd, adep, self.SC_ATTR, refresh=False)
        except:
            Errlog.log("training_attribute_handler: Could not clean special flight duty companions.")
              
    def valid_maincat(self, maincat):
        return maincat == "F"

class SpecialCompanionGroundDuty(SpecialCompanionBaseDuty):
    src_table = "crew_ground_duty_attr"
    dst_table = "ground_task_attr"
       
    def src_leg_id(self, entry):
        return entry.cgd.task._id
    
    def src_crew_id(self, entry):
        return entry.cgd.crew.id
    
    def src_attr(self, entry):
        return entry.attr.id
    
    def dst_leg_id(self, entry):
        return entry.task._id

    def dst_attr(self, entry):
        return entry.attr.id
    
    def set_special_companion_attr(self, leg_id, instructors, students):
        udor = leg_id.split("+", 1)[0]
        uuid = leg_id.split("+", 1)[1]
        value_str = ','.join(sorted(instructors)) + ':' + ','.join(sorted(students))
        attr_vals = {"str": value_str}
        try:
            Attributes.SetGroundTaskAttr(udor, uuid, self.SC_ATTR, refresh=False, **attr_vals)
        except:
            Errlog.log("training_attribute_handler: Could not store special ground duty companions.")
                
    def remove_special_companion_attr(self, leg_id):
        udor = leg_id.split("+", 1)[0]
        uuid = leg_id.split("+", 1)[1]
        try:
            Attributes.RemoveGroundTaskAttr(udor, uuid, self.SC_ATTR, refresh=False)
        except:
            Errlog.log("training_attribute_handler: Could not clean special ground duty companions.")
             
    def valid_maincat(self, maincat):
        return True;

def update_special_training_companions():
    """
    Updates attributes for special companions (instructors and students in different areas or main categories).
    Attributes are stored on leg level in tables flight_leg_attr and ground__duty_attr.
    Note: This command shall be called from the savePreProc function.
    """
    _update_special_training_companions_by_duty_type(SpecialCompanionFlightDuty())
    _update_special_training_companions_by_duty_type(SpecialCompanionGroundDuty())

def _update_special_training_companions_by_duty_type(dt):
    # Only update if in database plan.
    try:
        assert HF.isDBPlan()
    except:
        return
              
    # Clean special companion attributes for removed instructor/student attributes.
    for entry in TM.table(dt.dst_table).search("(&(attr=%s))" % (dt.SC_ATTR)):
        # Get legs current special instructors/students.
        instructors = entry.value_str.split(":")[0].split(",")
        students = entry.value_str.split(":")[1].split(",")
        
        # Get leg id.
        leg_id = dt.dst_leg_id(entry)
        
        # Rebuild the legs special training companions attribute.  
        # Keep instructors/students if the training attribute is still valid 
        # or if the crew is not loaded in the current plan.
        (_instructors, _students) = ([], [])     
 
        for inst_id in instructors:
            key = "+".join([leg_id, inst_id, dt.INST_ATTR])
            if (TM.table(dt.src_table).find(key) is not None or
                TM.table("crew").find(inst_id) is None):
                _instructors.append(inst_id)
                    
        for stud_id in students:
            key = "+".join([leg_id, stud_id, dt.STUD_ATTR])
            if (TM.table(dt.src_table).find(key) is not None or
                TM.table("crew").find(stud_id) is None): 
                _students.append(stud_id)
        
        # Update or remove changed special companion entries.
        if _instructors and _students:
            if _instructors != instructors or _students != students:
                dt.set_special_companion_attr(leg_id, _instructors, _students)
        else:
            dt.remove_special_companion_attr(leg_id)
 
    # Insert new special training companions attributes.
    # Create a list of all legs having training attributes.  
    legs = {}
    for entry in TM.table(dt.src_table).search("(|(attr=%s)(attr=%s))" % (dt.INST_ATTR, dt.STUD_ATTR)):
        leg_id = dt.src_leg_id(entry)
        crew_id = dt.src_crew_id(entry)
        attr = dt.src_attr(entry)
        
        udor = AbsDate(leg_id.split("+")[0])        
        maincat = R.eval('crew.%%maincat_for_rank%%(crew_contract.%%titlerank_at_date_by_id%%("%s", %s))' % (crew_id, udor))[0]                
        region = R.eval('crew_contract.%%region_at_date_by_id%%("%s", %s)' % (crew_id, udor))[0]

        # Create lists for instructors/students assigned to each leg.
        if dt.valid_maincat(maincat):
            if not leg_id in legs:
                legs[leg_id] = ([], [])
            
            (instructors, students) = legs[leg_id]
            if attr == dt.INST_ATTR:
                instructors.append((crew_id, attr, maincat, region))
            elif attr == dt.STUD_ATTR:
                students.append((crew_id, attr, maincat, region))
    
    # Create a list of legs having special training companions.
    spec_comp_legs = {}
    for leg in legs:
        (instructors, students) = legs[leg]
        for (inst_id, inst_attr, inst_maincat, inst_region) in instructors:
            for (stud_id, stud_attr, stud_maincat, stud_region) in students:
                if inst_maincat != stud_maincat or inst_region != stud_region:
                    if not leg in spec_comp_legs:
                        spec_comp_legs[leg] = ([], [])
                                       
                    (special_instructors, special_students) = spec_comp_legs[leg]
                    if not inst_id in special_instructors:
                        special_instructors.append(inst_id)
                    if not stud_id in special_students:
                        special_students.append(stud_id)
    
    # Add special companion attributes to each leg.
    for leg in spec_comp_legs:
        (instructors, students) = spec_comp_legs[leg]
        dt.set_special_companion_attr(leg, instructors, students)

    # End of file
