
#
#######################################################
#
#   Publish
#
#######################################################
"""
The publish script performs the necessary operations needed for
publishing rosters at roster release. Publishing in the tracking phase
is handled elsewhere although that functionality is also called upon here.
For rostering, publish is done at least once for every planning month. 
Each publication must be done for both the publish-types defined in
the tracking version of publication.Publishing is always done for all
crew in plan that are in the planning area. This includes hidden crew.

The actions taken are:
 1) Set compensation days to published
 2) Accumulate publication accumulators
 3) Convert BL and SBY trips to PACT:s
 4) Create rescheduling data (Tracking)
 5) Publish crew for the publish period

Anna Olsson, Jeppesen 2008-01-28

"""


# CARMSYS imports
import Errlog
import Gui
import Cui
import carmensystems.rave.api as R
from tm import TM
from utils.guiutil import UpdateManager
import utils.Names as Names
import time
from AbsTime import AbsTime
from RelTime import RelTime
import Dates
from modelserver import TableNotFoundError, EntityNotFoundError, EntityError
# Standard library imports
import tempfile
import os
import inspect
import traceback
# CARMUSR imports
import carmusr.AccountHandler as AccountHandler
import carmusr.Accumulators as Accumulators
import Select as Select
import carmusr.tracking.Rescheduling as Rescheduling
import carmusr.tracking.CrewMeal
import carmusr.ConfirmSave as cs
import carmusr.Attributes as Attributes
import carmusr.AssignActivities as AssignActivities
import carmusr.training_attribute_handler as Training
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew
import carmusr.rostering.Fairness as Fairness
import carmstd.cfhExtensions as cfhExtensions
import carmusr.Cimber as Cimber
from Variable import Variable 
from utils.performance import clockme

# Crewinfoserver(CIS) imports
import crewinfoserver.data.crew_rosters as crew_rosters

# These are the possible 'pubtype' values that can exist in 'published_roster'.
# Note: There are corresponding Rave constants in 'publish'. Keep in sync!!!
PUBLICATION_TYPES = (
    ROSTERING_PUBLISHED_TYPE,
    TRACKING_PUBLISHED_TYPE,
    TRACKING_INFORMED_TYPE,
    TRACKING_DELIVERED_TYPE,
    ) = (
    "SCHEDULED",
    "PUBLISHED",
    "INFORMED",
    "DELIVERED",
    )

MODULE = 'carmusr.rostering.Publish.py'
# ****************** Timer functionality **********************
__times = []
__t = None

def timer(txt=None):
    global __t
    global __times
    if not txt is None:
        __times.append("%s: %.2f s" %(txt, time.time() - __t))
    __t = time.time()

def printTimes(txt=""):
    global __t
    global __times
    try:
        time_txts = reduce(lambda a, b: "%s\n    %s" %(a,b), __times)
    except:
        time_txts = ""
    print "**************************************************"
    print "%s:\n     %s" % (txt, time_txts)
    print "**************************************************"
    __times = []
    __t = time.time()
# *************************************************************

class CrewAndTimeStruct(object):
    """
    Used to store calculated values so we don't need to look them up all the time
    """
    def __init__(self, crewid, start_utc, end_utc, start_hb, end_hb, tracking_published_end_utc):
        self.crewid = crewid
        self.start_utc = start_utc
        self.end_utc = end_utc
        self.tracking_published_end_utc = tracking_published_end_utc
        self.start_hb = start_hb
        self.end_hb = end_hb
        
    def __str__(self):
        tpx = self.tracking_published_end_utc
        return "<CrewAndTimeStruct %s utc: %s-%s, hb: %s-%s, prepub: %s>" % (
               self.crewid,
               self.start_utc, self.end_utc,
               self.start_hb, self.end_utc,
               (tpx and ("extension to %s utc" % tpx)) or "no extension")


# Function for setting the published attribute on crew
def setPublishedAttr(crew_structs=[]):
    Errlog.log("Publish::setPublishedAttr:: Setting PUBLISHED attribute on crew")
    # Note: This is an initial solution. To make it better we could use the fact
    # that crew_attr has validfrom as a key and validto as a value (in addition
    # to value_abs). This means we could check if the last period was published
    # and if so, extend validto with this period.
    # This way we would have a record for all published periods for crew.
    publ_end, = R.eval("fundamental.publ_period_end")
    user = Names.username()
    publ_time = AbsTime(*time.gmtime()[:5])
    si_string = "Last published by %s at %s" %(user, publ_time)
    attr_values = {}
    attr_values["si"] = si_string
    try:
        for crew in crew_structs:
            try:
                current_publ_date = Attributes.GetCrewAttr(crew.crewid, "PUBLISHED")['abs']
                # Don't move published date back incase publishing earlier period
                attr_values["abs"] = max(crew.end_hb,current_publ_date)
            except Attributes.CrewAttrNotFoundError, err:
                Errlog.log("Publish::setPublishedAttr:: %s, will create with publ. period end."%err)
                attr_values["abs"] = publ_end
            Attributes.SetCrewAttr(crew.crewid, "PUBLISHED", refresh=False, **attr_values)
        Cui.CuiReloadTable("crew_attr")
    except TableNotFoundError:
        Errlog.log("Publish::setPublishedAttr:: PUBLISHED attribute could"+\
                   " not be set due to missing table")
    except EntityNotFoundError:
        Errlog.log("Publish::setPublishedAttr:: PUBLISHED attribute could"+\
                   " not be set due to old table data (crew_attr_set)")
    return


def rosters_ok_for_publish(currentArea, start_hbt, end_hbt):
    """
    Checks rosters for crew in publish planning area for holes and overlapping activties,
    which is not allowed in published rosters.
    Computes the dates in which crew belongs to planning area and checks holes n' overlaps in
    that period
    """
    # Get all crew to be published
    Cui.CuiAreaRevealAllSubplanCrew(Cui.gpc_info, currentArea)
    crewList, = R.eval("sp_crew", R.foreach(
        R.iter('iterators.roster_set',
               where=(
        'planning_area.%crew_is_in_planning_area_in_publ_period%'
        )),
        'crew.%id%',
        'planning_area.%%changes_planning_area_in_period%%(%s,%s)'%(start_hbt, end_hbt)
        ))
    crew_messages = []
    crew_structs = []
    ok_to_publish = True
    # Check each crew in list for errors
    for  ix, crew_id,  area_change in crewList:
        crew_object = HF.CrewObject(str(crew_id),currentArea)
        start_hb_tmp = start_hbt
        end_hb_tmp = end_hbt
        if area_change:
            # Only check roster between dates when crew actually belong to planning area
            start_hb_tmp,end_hb_tmp = _get_in_period_dates(crew_object, start_hbt,end_hbt)
        # These prevent publish
        (overlap,
         hole,
         no_employment,
         extra_seat,
         crew_start_utc,
         crew_end_utc,
         tracking_published_end_utc,
         ) = crew_object.eval(
            'publish.%%has_any_overlap%%(%s,%s) '% (start_hb_tmp, end_hb_tmp),
            'publish.%%has_empty_holes_in_period%%(%s,%s)' % (start_hb_tmp, end_hb_tmp),
            'publish.%%has_activity_without_employment%%(%s,%s)' % (start_hbt, end_hbt), # check full publ. period here
            'publish.%%has_extra_seat_in_period%%(%s,%s)' % (start_hb_tmp, end_hb_tmp),
            'publish.%%crew_hb_date_to_utc_time%%(%s) '% start_hb_tmp,
            'publish.%%crew_hb_date_to_utc_time%%(%s)' % end_hb_tmp,
            'publish.%crew_pp_tracking_published_extension_end_utc%',
            )
        # Check for the different conditions 
        ok_to_publish &= not (overlap or hole or no_employment or extra_seat)
        # get messages to be prompted
        if overlap:
            crew_messages += _get_overlaps_for_crew(currentArea, crew_object, start_hbt,end_hbt)
        if hole:
            crew_messages += _get_holes_for_crew(currentArea, crew_object, start_hbt, end_hbt)
        if no_employment:
            crew_messages += _get_no_emp_period(currentArea, crew_object, start_hbt, end_hbt)
        if area_change:
            crew_messages += _get_in_period_message(currentArea, crew_object,
                                                    start_hb_tmp, end_hb_tmp)
        if extra_seat:
            crew_messages += _get_extra_seat_for_crew(currentArea, crew_object, start_hb_tmp, end_hb_tmp)
            
        # Store times in struct object
        crew_struct = CrewAndTimeStruct(crew_id, crew_start_utc, crew_end_utc,
                                                 start_hb_tmp, end_hb_tmp,
                                                 tracking_published_end_utc)
        crew_structs.append(crew_struct)

    return (ok_to_publish, crew_structs, crew_messages)
    
# Function for converting certain ground duties to PACT:s
def convertGDtoPACT(current_area = Cui.CuiArea0):
    """
    This function loops over certain ground duty activities on the roster
    overlapping the publishing period and create PACT:s.
    The actual codes will be retained.

    Window 0 must contain rosters.
    """
    Errlog.log("Publish::in convertGDtoPACT")    
        
    # Set the correct context
    # iterate over crew
      # iterate over rosters
        # if activity is applicable GD
          # save start, end, base, code etc.
          # deassign trip
          # create personal activity with the same attributes as the
    
    # Get the legs that need to be recreated as PACT:s
    where_expr = ("leg.%sby_or_bl_wop_starting_in_publ%",
                  "planning_area.%crew_is_in_planning_area_at_leg_start_hb%")
    ground_duties_expr, = R.eval(
        "sp_crew",
        R.foreach(R.iter('iterators.roster_set',
                         where = 'planning_area.%crew_is_in_planning_area_in_publ_period%'),
                  "crew.%id%",
                  R.foreach(R.iter('iterators.leg_set',
                                   where=where_expr),
                            "leg_identifier",
                            "leg.create_pact_at_publish",
                            "leg.%code%",
                            "ground_duty_code_suffix",
                            "leg.start_station",
                            "leg.end_station",
                            "leg.start_hb",
                            "leg.end_hb",
                            "leg.%sby_after_publ_period%",
                            "wop.%sby_start_hb%",
                            "leg.%start_utc%",
                            "leg.%published_wop_start%")
                  )
        )


    # Select legs that match the criteria, unlock the trips and
    # remove the legs (this will split trips over the period end and
    # deassign the part that is inside the period)
    # NOTE: If a trip starts before the period the trip locks will not be updated
    # and the legs will not be deassigned. The assumption is that the previous
    # period has already been published using this script and therefore there will be no
    # trips across the period start.
    leg_list = []
    Select.select({'FILTER_METHOD':'REPLACE',
                   'leg.sby_or_bl_wop_starting_in_publ':'TRUE',
                   'planning_area.%crew_is_in_planning_area_at_leg_start_hb%':'TRUE'},
                  current_area, Cui.CrewMode)

    Cui.CuiUnmarkAllLegs(Cui.gpc_info,current_area,"WINDOW")
    Select.select({'FILTER_METHOD':'REPLACE',
                   'FILTER_MARK':'LEG',
                   'leg.create_pact_at_publish':'TRUE',
                   'planning_area.%crew_is_in_planning_area_at_leg_start_hb%':'TRUE'},
                  current_area, Cui.CrewMode)
    
    if Cui.CuiGetNumberOfChains(Cui.gpc_info, current_area) != 0:
        Cui.CuiUpdateTripLocks(Cui.gpc_info, current_area, "marked", 0)
        leg_list =  []
    
        Cui.CuiRemoveAssignments(Cui.gpc_info, current_area, "", Cui.CUI_MOVE_ASMT_IGNORE_NEW_AREA,
                                 leg_list)
    
        leg_list = [str(l) for l in leg_list]

    Cui.CuiRevealAllCrrs(Cui.gpc_info, current_area)
    Cui.CuiDisplayObjects(Cui.gpc_info, current_area, Cui.CrrMode, Cui.CuiShowAll)
    Select.select({'FILTER_METHOD':'REPLACE',
                   'trip.starts_in_publ_period':'TRUE',
                   'leg.sby_or_bl_wop_starting_in_publ':'TRUE',
                   'planning_area.leg_is_in_planning_area':'TRUE'},
                  current_area, Cui.CrrMode)
    crr_legs = Cui.CuiGetLegs(Cui.gpc_info, current_area, "WINDOW")
    leg_list.extend([str(crr_leg) for crr_leg in crr_legs])
    

    if leg_list:
        pub_start, pub_end = R.eval('default_context',
                                    'fundamental.%publ_period_start%',
                                    'fundamental.%publ_period_end%')
        lock_bypass = {'FORM':'LOCK_DATES_DATED',
                       'HARD_LOCK_FROM_DATE':str(pub_start)[0:9] ,
                       'HARD_LOCK_TO_DATE': str(pub_end)[0:9],
                       'HARD_LOCK_FIRST_LEG': 'No',
                       'HARD_LOCK_LAST_LEG': 'No',
                       'OK': '' }
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, current_area,
                                   Cui.CrrMode,
                                   Cui.LegMode, leg_list)
        
        Cui.CuiUpdateTripLocks(Cui.gpc_info, current_area, "WINDOW", 0)
        Cui.CuiUpdateConnectionLocks(lock_bypass,Cui.gpc_info, current_area,"WINDOW", 0)
        Cui.CuiRemoveActivities(Cui.gpc_info, current_area, "WINDOW",
                                "CRR", "LEG", "DISSOLVE" , 0)

  
    
    error_log = []
    convertcount = 0
    for (ix, crew_id, legs) in ground_duties_expr:
        for (ix, leg_id, create_pact, gd_code, gd_code_suffix,
             leg_start_station, leg_end_station,
             leg_start_hb, leg_end_hb, sby_after_publ_period, wop_start, leg_start_utc,
             publ_wop_start) in legs:
            
            try:
                if create_pact:
                    # If the BL or SBY is a ground duty we convert it to PACT
                    Cui.CuiCreatePact(Cui.gpc_info,
                                      crew_id,
                                      gd_code,
                                      gd_code_suffix,
                                      leg_start_hb,
                                      leg_end_hb,
                                      leg_start_station,
                                      Cui.CUI_CREATE_PACT_DONT_CONFIRM |
                                      Cui.CUI_CREATE_PACT_SILENT |
                                      Cui.CUI_CREATE_PACT_NO_LEGALITY |
                                      Cui.CUI_CREATE_PACT_FORCE | 
                                      Cui.CUI_CREATE_PACT_TASKTAB)
                    convertcount += 1
                if sby_after_publ_period and wop_start <> publ_wop_start:
                    # If the SBY wop started in publ period, we tag it with wop start,
                    # but only if this is necessary
                    attr_vals = {"abs":wop_start}
                    Attributes.SetCrewActivityAttr(crew_id, leg_start_utc, gd_code,
                                                   "SBY", refresh=False,
                                                   **attr_vals)
                    print "Tagged %s at %s with %s" %(gd_code, leg_start_utc, wop_start)
            except Exception, e:
                traceback.print_exc()
                # Somehow the pact creation failed, compile a log statement
                log_msg = "%s : %s : %s : %s : %s : %s" % (crew_id,
                                                           gd_code,
                                                           gd_code_suffix,
                                                           leg_start_hb,
                                                           leg_end_hb,
                                                           leg_start_station,)
                error_log.append(log_msg)
                Errlog.log(log_msg)

    # Show errors
    if error_log:
        Errlog.set_user_message(
            "Failed to create pacts for the following activities:\n%s" % ("\n".join(error_log)))
    Attributes._refresh("crew_activity_attr")
    Errlog.log("Publish::convertGDtoPACT finished (converted to %d PACTs)" % convertcount)

    
def remove_hard_locks_from_trips(workarea=Cui.CuiScriptBuffer):
    """
    This function removes hard locks from open time trips.
    
    Only affects legs in the current planning area
      and starting before the publication period ends.
    Locks removed include start/end leg + connections,
      including those between duties.
    
    Changes the contents of workarea.
    Changes leg marking.
    """
    msg = "Removed hard locks"
    try:
        # Select planning area trips with legs starting in publication period.
        Select.select({'FILTER_METHOD': 'REPLACE',
                       'FILTER_PRINCIP': 'ANY',
                       'FILTER_MARK': 'NONE',
                       'leg.%in_publ_period%': 'TRUE',
                       'planning_area.%trip_is_in_planning_area%': 'TRUE',
                       }, workarea, Cui.CrrMode)
        
        # Make sure no legs are marked in the selected trips.
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, "WINDOW")
        
        # Within the selected trips;
        #   mark planning area legs starting before publication period end.
        Select.select({'FILTER_METHOD': 'SUBSELECT',
                       'FILTER_PRINCIP': 'ANY',
                       'FILTER_MARK': 'LEG',
                       'leg.%in_or_before_publ_period%': 'TRUE',
                       }, workarea, Cui.CrrMode)
                       
        # Remove hard locks from marked legs.
        Cui.CuiUpdateConnectionLocks(Cui.gpc_info, workarea, "WINDOW",
            0,                              # Remove locks 
            1, Dates.LAST_OK_CARMTIME,      # No period limit, use mark instead
            1,                              # Between duties
            3,                              # Both at start and end of chain 
            2)                              # Operate on marked legs only
            
        # Clean up the marking made in this function.
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, "WINDOW")
    except Exception,e:
        Errlog.log("Publish::remove_hard_locks_from_trips: DEBUG traceback follows")
        traceback.print_exc()
        msg = "Warning: Failed to remove one or more locks"
    Errlog.log("Publish::remove_hard_locks_from_trips: %s" % msg)
    
    
    
def split_pacts_at_period_start(workarea):
    """
    Split pacts (crew_activity) crossing the publish period start into two parts;
    one in the current publish period, and one before. Even though most splits
    have already been done in the previous publish (through split_pacts_at_period_end below)
    some PACTs may have been extended after that publish.
    Note: Currently, the split occurs at 'fundamental.%publ_period_start_utc%',
          which is common to all crew, including Asian.
    """
    Errlog.log("Publish::in split_pacts_at_period_start")
    
    _split_pacts_at_period_border(workarea, 'publish.%split_pact_at_period_start%', "fundamental.%publ_period_start_utc%")
    
def split_pacts_at_period_end(workarea):
    """
    Split pacts (crew_activity) crossing the publish period end into two parts;
    one in the current publish period, and one after.
    Note: Currently, the split occurs at 'fundamental.%publ_period_end_utc%',
          which is common to all crew, including Asian.
    """
    Errlog.log("Publish::in split_pacts_at_period_end")
    
    _split_pacts_at_period_border(workarea, 'publish.%split_pact_at_period_end%', "fundamental.%publ_period_end_utc%")
    
def _split_pacts_at_period_border(workarea, rave_condition, rave_split_time):

    Errlog.log("Publish::in split_pacts_at_period_border")
    
    # Make sure no legs are marked.
    # Subselect crew with pacts to split.
    # Mark the pacts.
    
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, 'WINDOW')
    Select.select({
        'FILTER_METHOD': 'SUBSELECT',
        'FILTER_MARK': 'LEG',
        rave_condition: 'TRUE',
        'planning_area.%crew_is_in_planning_area_at_leg_start_hb%': 'TRUE',
        }, workarea, Cui.CrewMode)
    
    Cui.CuiSetCurrentArea(Cui.gpc_info, workarea)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, workarea, 'WINDOW')
    
    # This is the split time used by publish.%split_pact_at_period_end%.
    # We'll use it for the actual split operation, too.
    publ_period_border_utc, = R.eval(rave_split_time)
        
    # Get some useful info regarding the pacts to split.
    # The info will be used to recreate the pacts in split form.
    
    import utils.rave
    pact_iter = utils.rave.RaveIterator(
        R.iter('iterators.leg_set', where="marked"), {
            'crew_id':        'crew.%id%',
            'location':       'leg.%start_station%',
            'task_code':      'leg.%code%',
            'start_utc':      'leg.%start_utc%',
            'end_utc':        'leg.%end_utc%',
            }).eval('default_context')
     
    # Recreate each pact in two parts; before and after period border.
    # Update the original PACT to end at the period border, and
    # create a copy starting at period border and ending at original PACT end.
    #
    # NOTE: Due to problems with using Cui for these operations, use TM.
    #       a) Many Cui calls may result in "Max number of indices" errors.
    #       b) CuiCreatePact fails when there are overlapping legs.

    splitcount = 0
    error_log = []
    needsync = False
    errcount = {}
    trace_limit = 1
    for pact in pact_iter:
        try:
            crew = TM.crew[(pact.crew_id,)]
            activity = TM.activity_set[(pact.task_code,)]
        except:
            errcount["LOOKUP"] = errcount.get("LOOKUP", 0) + 1
            if errcount["LOOKUP"] <= trace_limit:
                traceback.print_exc()
            error_log.append("LOOKUP : %s : %6s : %s : %s : %s : %s" % (
                             pact.crew_id, pact.task_code, " ",
                             pact.start_utc, pact.end_utc, pact.location))
        else:
            try:
                head = TM.crew_activity[(pact.start_utc,crew,activity)]
                head.et = AbsTime(publ_period_border_utc)
                needsync = True
                splitcount += 1
            except:
                errcount["UPDATE"] = errcount.get("UPDATE", 0) + 1
                if errcount["UPDATE"] <= trace_limit:
                    traceback.print_exc()
                error_log.append("SHORTEN : %s : %6s : %s : %s : %s : %s" % (
                    pact.crew_id, pact.task_code, " ",
                    pact.start_utc, pact.end_utc, pact.location))
            else:
                try:
                    key = (AbsTime(publ_period_border_utc),crew,activity)
                    tail = TM.crew_activity.create(key)
                    needsync = True
                    tail.et = pact.end_utc
                    tail.adep = tail.ades = head.ades
                    # Putting different value in personaltrip to avoid merging
                    # of PACTs to a trip.  See SASCMS-926.
                    tail.personaltrip = TM.createUUID()
                except:
                    errcount["CREATE"] = errcount.get("CREATE", 0) + 1
                    if errcount["CREATE"] <= trace_limit:
                        traceback.print_exc()
                    error_log.append("TAIL OF : %s : %6s : %s : %s : %s : %s" % (
                        pact.crew_id, pact.task_code, " ",
                        pact.start_utc, pact.end_utc, pact.location))
        
    if needsync:
        # A sync is required for the core-table modifications to be recognized.
        Cui.CuiSyncModels(Cui.gpc_info)

    if error_log:
        Errlog.set_user_message(
            "Failed to split the following PACTs at publish period end:\n%s"
            % ("\n".join(error_log)))
        return 1

    if errcount:
        elog = ", ".join("%s=%d" % (k,v) for (k,v) in errcount.items() if v)
    else:
        elog = "NONE"
    Errlog.log("Publish::split_pacts_at_period_border finished"
               " (%d splits performed; Errors: %s.)" % (splitcount,elog))
    return 0

def merge_pacts_in_period(workarea):
    """
    Merge adjacent pacts (crew_activity) of same type within the publish period.
    
    Purpose:
      TAP exports single day PACTs.
      Results in many trips (one/day), which has a negative performance impact.
      It also gives a "messy" roster.
    """
    Errlog.log("Publish::in merge_pacts_in_period")
    try:
        # Make sure no legs are marked.
        # Subselect crew with pacts to merge.
        # Mark the first pact in each group to merge.
        
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, 'WINDOW')
        Select.select({
            'FILTER_METHOD': 'SUBSELECT',
            'FILTER_MARK': 'LEG',
            'publish.%leg_is_pact_merge_start%': 'TRUE',
            }, workarea, Cui.CrewMode)
        
        Cui.CuiSetCurrentArea(Cui.gpc_info, workarea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, workarea, 'WINDOW')
        
        # Get some useful info regarding the pacts merge.
        # The info will be used to recreate the pacts in merged form.
        
        import utils.rave
        pact_iter = utils.rave.RaveIterator(
            R.iter('iterators.leg_set', where="marked"), {
                'crew_id':        'crew.%id%',
                'location':       'leg.%start_station%',
                'task_code':      'leg.%code%',
                'start_utc':      'leg.%start_utc%',
                'merge_end_utc':  'publish.%leg_pact_merge_end_utc%',
                }).eval('default_context')
     
        # For each block of PACTs to merge:
        # - Adjust end time of the first.
        # - Remove the rest (they are now covered by the first one).
        #
        # NOTE: Due to problems with using Cui for these operations, use TM.
        #       a) Many Cui calls may result in "Max number of indices" errors.
        #       b) CuiCreatePact fails when there are overlapping legs.
               
        removecount = 0
        mergecount = 0
        cset = set()
        needsync = False
        for pact in pact_iter:
            cset.add(pact.crew_id)
            crew = TM.crew[(pact.crew_id,)]
            for db_pact in crew.referers("crew_activity", "crew"):
                if db_pact.activity.id == pact.task_code \
                and db_pact.adep.id == pact.location \
                and db_pact.st >= pact.start_utc \
                and db_pact.et <= pact.merge_end_utc:
                    if db_pact.st == pact.start_utc:
                        # Make first pact in group longer.
                        db_pact.et = pact.merge_end_utc
                        mergecount += 1
                    else:
                        # Remove pact now covered by first pact in group.
                        db_pact.remove()
                        removecount += 1
                    needsync = True
        
        Errlog.log("Publish::merge_pacts_in_period:"
                   " %s pacts merged to %s (%s crew)"
                   % (mergecount+removecount, mergecount, len(cset)))
            
        if needsync:
            # A sync is required for the core-table modifications to be recognized.
            Cui.CuiSyncModels(Cui.gpc_info)
            
        Errlog.log("Publish::merge_pacts_in_period finished")
        return 0
        
    except:
        Errlog.log("Publish::merge_pacts_in_period failed")
        traceback.print_exc()
        return 1    
        
def move_AS_to_AH_on_shorthaul(crew_structs,area=Cui.CuiScriptBuffer):
    """
    Moves crew assigned in AS on shorthaul to AH
    """
    
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    mark_leg_bypass = {
        'FORM': 'form_mark_leg_filter',
        'FL_TIME_BASE': 'RDOP',
        'FILTER_MARK': 'LEG',
        'CRC_VARIABLE_0': 'crew_pos.%AS_to_AH_at_publish%',
        'CRC_VALUE_0': 'T',
        'CRC_VARIABLE_1': 'planning_area.crew_is_in_planning_area_at_leg_start_hb',
        'CRC_VALUE_1': 'T',
        'OK': ''}
    
    Cui.CuiMarkLegsWithFilter(mark_leg_bypass, Cui.gpc_info, area, 0)

    try:
        flags = 16|Cui.CUI_CHANGE_ASS_POS_SUPPRESS_DIALOGUE
        Cui.CuiChangeAssignedPosition(Cui.gpc_info,"C","AH",flags)
    except Exception, err:
        Errlog.log('Publish::move_AS_to_AH_on_shorthaul:%s'%err)
        Errlog.log('Publish::move_AS_to_AH_on_shorthaul: '+\
                   'Failed to change positions for AS assigned shorthaul legs')
    
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    Cui.CuiSyncModels(Cui.gpc_info)
    return

def disconnect_variants(crew_structs,area=Cui.CuiScriptBuffer):
    """
    Disconnects base variants from assigned trips
    """
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    mark_leg_bypass = {
        'FORM': 'form_mark_leg_filter',
        'FL_TIME_BASE': 'RDOP',
        'FILTER_MARK': 'LEG',
        'CRC_VARIABLE_0': 'studio_select.%trip_has_variant%',
        'CRC_VALUE_0': 'T',
        'CRC_VARIABLE_1': 'planning_area.crew_is_in_planning_area_at_leg_start_hb',
        'CRC_VALUE_1': 'T',
        'OK': ''}
    
    Cui.CuiMarkLegsWithFilter(mark_leg_bypass, Cui.gpc_info, area, 0)

    try:
        Cui.CuiCrrMakePersonal(Cui.gpc_info, "MARKED")
    except Exception, err:
        Errlog.log('Publish::disconnect_variants:%s'%err)
        Errlog.log('Publish::disconnect_variants: '+\
                   'Failed to disconnect base variants')    
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    Cui.CuiSyncModels(Cui.gpc_info)
    return

def remove_open_time_variants(workarea=Cui.CuiScriptBuffer):
    """
    This function removes any and all base variants from trips in open plan
    that are a part of the planning area.
    """

    # Get current state of Trip Filter.
    crew_filter_crr = Variable("")
    Cui.CuiGetSubPlanCrewFilterCrr(Cui.gpc_info, crew_filter_crr)

    # Turn off Trip Filter.
    Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, 0)

    # Make sure no legs are marked in the work area.
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, "WINDOW")
    
    # Select all trips containing a base variant in the planning area.
    Select.select({'FILTER_METHOD': 'REPLACE',
                       'FILTER_PRINCIP': 'ANY',
                       'FILTER_MARK': 'Trip', # All segments in the trip must be marked
                       'leg.%in_publ_period%': 'TRUE',
                       'planning_area.%trip_is_in_planning_area%': 'TRUE',
                       'studio_select.%trip_has_variant%': 'TRUE',
                       }, workarea, Cui.CrrMode)
    
    # Get number of chains.
    nbr_of_chains = Cui.CuiGetNumberOfChains(Cui.gpc_info, workarea)

    # Remove optional variants (if any). According to the man page this can pop up an unsuppressable
    # dialog but when checking the source code the dialog will not be shown when base is "" as below.
    # This will remove variants for all bases in one go.
    if nbr_of_chains:
        Cui.CuiRemoveOptionalCrrVariants(Cui.gpc_info, "MARKED", "")

    # Make sure no legs are marked in the work area.
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, "WINDOW")

    # Restore Trip Filter state.
    if crew_filter_crr.value:
        Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, 1)
        
def convert_extra_seats_in_unassigned_trips(workarea=Cui.CuiScriptBuffer):
    """
    This function converts any extra seat to deadhead in all unassigned trips. 
    """

    # Get current state of Trip Filter.
    crew_filter_crr = Variable("")
    Cui.CuiGetSubPlanCrewFilterCrr(Cui.gpc_info, crew_filter_crr)

    # Turn off Trip Filter.
    Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, 0)

    # Set current area.
    Cui.CuiSetCurrentArea(Cui.gpc_info, workarea)

    # Select all trips
    Select.selectTripUsingPlanningAreaBaseFilter()

    # Get number of chains.
    nbr_of_chains = Cui.CuiGetNumberOfChains(Cui.gpc_info, workarea)

    # Convert all extra seats to deadheads.
    if nbr_of_chains:
        Cui.CuiUndoAllExtraSeat(Cui.gpc_info)

    # Restore Trip Filter state.
    if crew_filter_crr.value:
        Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, 1)
    else:
        Cui.CuiSetSubPlanCrewFilterCrr(Cui.gpc_info, 0)
   
def _get_empno_or_id(crew_object):
    empno, =  crew_object.eval('crew.%extperkey%')
    if not empno:
        empno, = crew_object.eval('crew.%id%')
        empno += ' (id)'
    return empno
    
def _get_in_period_dates(crew_object, start_hbt,end_hbt):
    fwd, = crew_object.eval('planning_area.%%crew_is_in_planning_area_at_date%%(%s)'%start_hbt)
    empno = _get_empno_or_id(crew_object)
    
    change_date, = crew_object.eval('planning_area.%%get_change_date%%(%s,%s,%s)'%\
                                    (start_hbt,end_hbt,fwd))
    if not change_date:
        Errlog.log('Publish::_get_in_period_dates, Unable to get change date for crew empno %s'%empno)
        return (start_hbt, end_hbt)
    if fwd:
        return (start_hbt, change_date)
    else:
        return (change_date.adddays(1), end_hbt) # add one day to get inclusive dates

def _get_in_period_message(area, crew_object, in_period_start_hbt, in_period_end_hbt):
    if not isinstance(crew_object,HF.CrewObject):
        crew_object = HF.CrewObject(str(crew_object),currentArea)
    empno = _get_empno_or_id(crew_object)
    return ['Info: Crew %s belongs to planning area between %s and %s\n'%\
            (empno,in_period_start_hbt.ddmonyyyy(True),
             in_period_end_hbt.adddays(-1).ddmonyyyy(True))]


def _get_no_emp_period(area, crew_object, start_time, end_time):
    if not isinstance(crew_object,HF.CrewObject):
        crew_object = HF.CrewObject(str(crew_object),currentArea)
    end, = crew_object.eval('crew.%available_end%')
    empno = _get_empno_or_id(crew_object)
    return ['Error: Crew %s has activity outside employment ending %s\n'%(empno, end.ddmonyyyy(True))]

def _get_holes_for_crew(area, crew_object,start_time, end_time):
    if not isinstance(crew_object,HF.CrewObject):
        crew_object = HF.CrewObject(str(crew_object),currentArea)
    # Code stolen from assign activities
    ONE_DAY = RelTime('24:00')
    rave_exp = R.foreach(R.iter('iterators.trip_set',
                                where='trip.%%start_hb%%<=%s and trip.%%end_hb%%>=%s'%\
                                (end_time, start_time),
                                 sort_by="trip.%start_hb%"),
                         "trip.%start_hb%",         
                         "trip.%end_hb%"
                         )
    trips, = crew_object.eval(rave_exp)
    empno = _get_empno_or_id(crew_object)
    start_time = start_time.day_floor()
    end_time = end_time.day_ceil()
    possible_days= [True] * int((end_time-start_time)/ONE_DAY) # All days are open
    
    for ix, start_hb, end_hb in trips:
        trip_start = max(start_hb.day_floor(),start_time)
        trip_end = min(end_hb.day_ceil(), end_time)
        start_index = int((trip_start-start_time)/ONE_DAY)
        end_index = int((trip_end-start_time)/ONE_DAY)
        possible_days[start_index:end_index]=[False]*(end_index-start_index) #Mark days in trip as busy

    possible_periods = {}
    current_time = None
    for ix in range(0,len(possible_days)):
        time = start_time + ONE_DAY*ix
        if not current_time and possible_days[ix]:
            possible_periods[time] = time
            current_time = time
        elif current_time and not possible_days[ix]:
            possible_periods[current_time] = time
            current_time = None
        if ix == len(possible_days)-1 and possible_days[ix] and current_time:
            possible_periods[current_time] = end_time
    if possible_periods:
        return ["Error: Crew %s has hole in roster starting %s\n"%(empno,time) \
                for time in possible_periods.keys()]
    else:
        return ["Error: Crew %s has hole(s) in roster\n"%empno]

def _get_overlaps_for_crew(area, crew_object,start_time, end_time):
    if not isinstance(crew_object,HF.CrewObject):
        crew_object = HF.CrewObject(str(crew_object),currentArea)
    ONE_DAY = RelTime('24:00')
    rave_exp = R.foreach(R.iter('iterators.trip_set',
                                where='trip.%%start_hb%%<=%s and trip.%%end_hb%%>=%s'%\
                                (end_time, start_time) +\
                                ' and studio_overlap.%trip_overlap%',
                                 sort_by="trip.%start_hb%"),
                         "trip.%start_hb%")
    trips,  = crew_object.eval(rave_exp)
    empno = _get_empno_or_id(crew_object)
    if trips:
        return ["Error: Crew %s has overlapping trips starting %s\n"%(empno,time) \
                for ix,time in trips]
    else:
        return ["Error: Crew %s has overlapping trip(s)\n" % empno]

def _get_extra_seat_for_crew(area, crew_object,start_time, end_time):
    if not isinstance(crew_object,HF.CrewObject):
        crew_object = HF.CrewObject(str(crew_object),currentArea)
    rave_exp = R.foreach(R.iter('iterators.trip_set',
                                where='trip.%%start_hb%%<=%s and trip.%%end_hb%%>=%s'%\
                                (end_time, start_time) +\
                                ' and trip.%has_extra_seat%',
                                 sort_by="trip.%start_hb%"),
                         "trip.%start_hb%")
    trips, = crew_object.eval(rave_exp)
    empno = _get_empno_or_id(crew_object)
    if trips:
        return ["Error: Crew %s has extra seat trips starting %s\n"%(empno,time) \
                for ix,time in trips]
    else:
        return ["Error: Crew %s has extra seat trip(s)\n" % empno]


def _show_messages(title, messages):
    if messages:
        errorLogPath = tempfile.mktemp()
        errorLog = None
        try:
            errorLog = open(errorLogPath, "w")
            errorLog.writelines(messages)
            errorLog.close()
            cfhExtensions.showFile(errorLogPath,title)
        finally:
            if errorLog:
                errorLog.close()
                os.unlink(errorLogPath)







class RosterPublish(object):
    """
    Template Pattern class for publishing rosters. Instanciate the class and call
    publish()
    """
    def __init__(self):
        # Get start and end date for publication period
        self.start, = R.eval("fundamental.publ_period_start")
        self.end, = R.eval("fundamental.publ_period_end")
        
        # CPH are used as a default base since the local time is the same for
        # both CPH, STO and OSL. 
        self.utc_start, = R.eval("fundamental.publ_period_start_UTC")
        self.utc_end, = R.eval("fundamental.publ_period_end_UTC")
        
        self.currentArea = Cui.CuiScriptBuffer
        
        self.warningMessage = "Performing this operation is irreversible and can not be undone.\n" +\
                               "Rosters for crew in plan for the"+\
                               " time period %s to %s will be published.\n" %  (self.start,self.end)+\
                               "All changes made to plan before publishing will be saved.\n\n"

        self.crewList = []
        self.crew_structs = []
        self.crew_structs_all = []

    def checkTags(self, tries):
        """
        Checks that all tags are set for the relevant period
        """
        def crew_has_pub_tags(crew):
            crew_ent = TM.crew[(crew.crewid,)]
            ix = 0
            for ptype in PUBLICATION_TYPES:
                # For all pub types, find a row that complety covers the crew times
                for row in crew_ent.referers("published_roster", "crew"):
                    if row.pubtype.id == ptype and row.pubstart <= crew.start_utc and row.pubend >= crew.end_utc:
                        ix += 1
                        break
            if ix == len(PUBLICATION_TYPES):
                return True
            else:
                self._log("Crew %s lacks publication tags for %s - %s" %(crew.crewid, crew.start_utc, crew.end_utc))
                return False
            
        # At first iteration we save the complete crew_structs for future use
        if tries == 0:
            self.crew_structs_all = self.crew_structs
            return 0

        for crew in self.crew_structs_all:
            setattr(crew, "has_pub_tags", crew_has_pub_tags(crew))
       
        self.crew_structs = [crew for crew in self.crew_structs_all if not crew.has_pub_tags]
        
        self.crewList = [crew.crewid  for crew in self.crew_structs]
        timer("Checked tags")

    def markCrewModified(self):
        for crewid in self.crewList:
            modcrew.add(crewid)

    def savePreprocessing(self):
        """
        Pre-save processing steps for roster push to TripTrade, CIS and Airside
        """
        FUNCTION = '::savePreprocessing'
        try:
            crew_rosters.prepare()
            timer("Prepare crew rosters to CrewInfoServer")
        except Exception, e:
            Errlog.log(MODULE + FUNCTION + "failed to prepare crew rosters to CrewInfoServer update job " + str(e))

    def savePostprocessing(self):
        """
        Post-save processing steps for roster push to TripTrade, CIS and Airside
        """
        FUNCTION = '::savePostprocessing'

        try:
            crew_rosters.run.setSubmitter('studio_publish_crewroster_push_job')
            crew_rosters.submit()
            timer("Submit roster update to CrewInfoServer job")
        except Exception, e:
            Gui.GuiWarning(MODULE + FUNCTION + "failed to submit roster update to CrewInfoServer job " + str(e))
            Errlog.log(MODULE + FUNCTION + "failed to submit roster update to CrewInfoServer job " + str(e))

    def publish(self):
        """
        Performs the actual publishing steps
        """
        timer()
        Cui.CuiSyncModels(Cui.gpc_info)
        # Check for holes and/or overlaps and create crew structs and crew list
        ok_to_publish, message  = self.checkRosters()
        timer("Evaluate if rosters OK for publish")

        if not ok_to_publish:
            self._log(message)
            Gui.GuiWarning(message)
            printTimes("Publish rosters: Roster check failed")
            return 1

        if not self.handleContinueMessage(message):
            self._log("User aborted publication")
            printTimes("Publish rosters: User cancelled")
            return
        # Ok, we cannot get here unless we have ok rosters for publish and more than 0 crew in selection.
        self._log("About to publish: %s with %d crews"%(self.getPlanningAreaString(), len(self.crewList)))

        UpdateManager.start()
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)

        # Mark all crew as modified
        self.markCrewModified()

        # Perform the different publishing steps
        self.setCrewMealAttr()
        self.tagInstructors()
        self.splitPACTsAtPeriodStart()
        self.splitPACTsAtPeriodEnd()
        self.publishCompensationDays()
        self.publishAccumulators()
        self.convertToPACT()
        self.moveAStoAH()
        self.disconnectVariants()
        self.removeOpenTimeVariants()
        self.convertExtraSeatsInUnassignedTrips()
        self.removeHardLocks()
        self.updateCrewFairnessHistory()
        self.setCimberCabinCrewInCharge()

        # This report is disabled due to SKBMM-531
        # self.generateBidSatisfactionReports()

        self.savePreprocessing()

        save_ok = self.save("Save before actual publish", "Saved plan")
        if not save_ok:
            message = "Failed to save after pre-publish operations due to conflicts.\n"+\
                      "Inspect, refresh, save and try Publish again"
            self._log(message)
            Gui.GuiWarning(message)
            printTimes("Publish rosters: Initial save failed")
            return 1

        # Mark all crew as modified
        self.markCrewModified()

        tries = 0
        save_ok = False
    
        # First try is 0
        while (not save_ok):
            self.checkTags(tries)
            self.tagPublished()
            self.calculateRescheduleInformation()
            self.setPublishedAttributes()
            save_ok = self.save("Save after actual publish and rescheduling", "Saving published data")
            if not save_ok:
                self._log("Save failed at try %s" %(tries+1))
            else:
                self._log("Saved successfully at try %s" %(tries+1))
                self.savePostprocessing()
                break
            tries += 1
            if (tries == 5):
                message = "Failed to save after 5 tries. Refresh, save and try Publish again"
                self._log(message)
                Gui.GuiWarning(message)
                printTimes("Publish rosters: Save failed after 5 tries")
                return 1

        UpdateManager.done()

        self._log("Finished")
        printTimes("Publish rosters")
        self._log("Publish finished for area: %s with %d crews"%(self.getPlanningAreaString(), len(self.crewList)))
        self.displayFinishedOKMessage()
        
    def handleContinueMessage(self, message=''):
        return Gui.GuiContinue(None,"%s\n%s"%(message,self.warningMessage))
            
    def setCrewMealAttr(self):
        carmusr.tracking.CrewMeal.roster_release_publish_meals(self.currentArea)
        self._log("Set crew meal attributes")
        timer("Set crew meal attributes")

    def tagInstructors(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        Training.set_instructor_tag(mode='PUBLISH',area=self.currentArea)
        self._log("Tagged instructors")
        timer("Tag instructors")

    def publishCompensationDays(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        AccountHandler.setPublished(self.start, self.end, self.currentArea)
        self._log("Publishing compensation days")
        timer("Publish comp days")

    def publishAccumulators(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        Accumulators.accumulatePublished(self.currentArea)
        self._log("Accumulating publication accumulators")
        timer("Create pub. accumulators")

    def convertToPACT(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        convertGDtoPACT(self.currentArea)
        self._log("Converting GD:s to PACT:s")
        timer("Convert GD to PACTS")

    def splitPACTsAtPeriodStart(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        split_pacts_at_period_start(self.currentArea)
        self._log("Splitting PACT:s at period start")
        timer("Splitting PACTS")

    def splitPACTsAtPeriodEnd(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        split_pacts_at_period_end(self.currentArea)
        self._log("Splitting PACT:s at period end")
        timer("Splitting PACTS")

    def moveAStoAH(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        move_AS_to_AH_on_shorthaul(self.crew_structs, self.currentArea)
        self._log("Moving crew assigned in AS on shorthaul to AH")
        timer("Moving AS to AH on shorthaul")

    def disconnectVariants(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        disconnect_variants(self.crew_structs, self.currentArea)
        self._log("Removing base variants from assigned trips")
        timer("Removing base variants")
        
    def removeOpenTimeVariants(self):
        remove_open_time_variants()
        self._log("Removing base variants from trip window")
        timer("Removing base variants from trip window")

    def convertExtraSeatsInUnassignedTrips(self):
        convert_extra_seats_in_unassigned_trips()
        self._log("Converting extra seats to deadheads in trip window")
        timer("Converting extra seats to deadheads in trip window")
        
    def removeHardLocks(self):
        remove_hard_locks_from_trips()
        self._log("Removing hard locks from trips in open time")
        timer("Removing hard locks")

    def updateCrewFairnessHistory(self):
        Fairness.update_crew_fairness_history()
        self._log("Updating crew history for long term fairness")
        timer("Updating crew history for long term fairness")

    def setCimberCabinCrewInCharge(self):
        Cimber.init_cabin_in_charge_cimber()
        self._log("Init Cimber cabin crew in charge")
        timer("Init Cimber cabin crew in charge")

    def generateBidSatisfactionReports(self):
        import carmensystems.publisher.api as prt
        st = time.time()

        pub_start, = R.eval("fundamental.publ_period_start")
        pub_month = str(pub_start)[2:9]

        default_bag = R.context('sp_crew').bag()
        crewlist = [roster_bag.crew.id() for roster_bag in default_bag.iterators.roster_set()]

        for crew in crewlist:
            dir_path = os.path.join(os.environ['CARMDATA'],
                                    'crewportal',
                                    'datasource',
                                    'reports',
                                    'interbids',
                                    'user',
                                    crew[:3],
                                    crew)
            d = os.path.dirname(dir_path)
            if not os.path.exists(d):
                os.makedirs(d)
            file_path = os.path.join(dir_path,'BidSatisfaction_%s' % pub_month)

            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            Cui.gpc_set_one_crew_chain(Cui.gpc_info, crew)

            Errlog.log("Publish.generateBidSatisfactionReports:: Generating report for crew: %s" % crew)
            prt.generateReport('report_sources.crew_window_object.CrewBidOutcome',
                               file_path, prt.PDF)
        et = time.time()

        Errlog.log("Publish.generateBidSatisfactionReports:: Finished generating BidSatisfaction reports. Elapsed time %.2fs." % (et-st))

    def tagPublished(self):
        # CuiPublishRosters shall have a UTC time interval as argument.
        self._log("Perform actual publish")
        
        # Note that for the TRACKING_PUBLISHED_TYPE tag, the publish interval
        # may be extended to cover activities that already were published before
        # the rostering process. (See also split_pacts_at_period_end().) 

        publist = []
        for crew in self.crew_structs:
            pubext_end_utc = (crew.tracking_published_end_utc or crew.end_utc)
            for ptype in PUBLICATION_TYPES:
                publist.append((crew.crewid,
                                ptype,
                                int(crew.start_utc),
                                int(crew.end_utc)))
            if crew.tracking_published_end_utc:
                publist.append((crew.crewid,
                                TRACKING_PUBLISHED_TYPE,
                                int(crew.end_utc),
                                int(crew.tracking_published_end_utc)))

        Cui.CuiPublishRosters(Cui.gpc_info,
                              publist,
                              "ROSTER PUBLISH",
                              Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
                              | Cui.CUI_PUBLISH_ROSTER_SKIP_SAVE)
        UpdateManager.setDirtyTable("published_roster")
         
        UpdateManager.setGuiChange()
        timer("SYS-Publish")

    def calculateRescheduleInformation(self):
        # Homebase time used for rescheduling
        self._log("Write rescheduling information")
        Rescheduling.publish(crew_list=self.crewList,
                             start_date=self.start,
                             end_date=self.end,
                             sel_mode=Rescheduling.ROSTER_PUBLISH,
                             area=self.currentArea)
        timer("Update publish data")

    def setPublishedAttributes(self):
        setPublishedAttr(self.crew_structs)

    def displayFinishedOKMessage(self):
        Gui.GuiNotice("Publication finished ok")

    def getPlanningAreaString(self):
        crew_area, = R.eval('crg_info.%planning_area_crew%')
        return crew_area
        
    def checkRosters(self):
        """
        If zero crew -> return not ok for publish and warning message
        else return ok_to_publish together with message.
        """
        ok_to_publish, crew_structs, crew_messages = rosters_ok_for_publish(self.currentArea, self.start, self.end)
        planning_area = self.getPlanningAreaString()
        message = "Current selected crew planning area: %s contains %d crew."%(planning_area, len(crew_structs))
        if not crew_structs:
            #empty list, warn and abort
            message = message + "\nPlease check planning area settings and run publish again!\n"
            return False, message
        if crew_messages:
            crew_messages.sort()
            _show_messages('Publish Roster Message',crew_messages)
        self.crewList = [crew.crewid  for crew in crew_structs]
        self.crew_structs = crew_structs
        if not ok_to_publish:
            message = message + "\nPublish aborted due to holes, overlaps or extra seats in rosters.\n"+\
                                "Please fix the listed errors manually and run publish again.\n\n"
        return ok_to_publish, message

    def _log(self, logString):
        method = inspect.currentframe().f_back.f_code.co_name
        Errlog.log("%s::%s: %s" % (self.__class__.__name__, method, logString.replace('\n',':')))

    def save(self, logString, timerString):
        self._log(logString)
        old_dialog_value = cs.skip_confirm_dialog 
        cs.skip_confirm_dialog = True #Set global variable in carmusr/ConfirmSave.py
        Cui.CuiSavePlans(Cui.gpc_info,Cui.CUI_SAVE_DONT_CONFIRM+Cui.CUI_SAVE_SILENT+Cui.CUI_SAVE_FORCE)
        modified_crew = len(modcrew.get())
        timer(timerString)
        cs.skip_confirm_dialog = old_dialog_value
        # If the number of modified crew is zero we have a successful save
        return modified_crew == 0;


class BatchPublish(RosterPublish):
    """
    Class that performs a full roster publish, except that it will always pass the roster check.
    If there is any ambiguity in tagging instructors, the instructor will not be tagged and
    his crew id will be logged. One should always inspect the log afterwards
    """
    def __init__(self):
        RosterPublish.__init__(self)

    def checkRosters(self):
        ok_to_publish, crew_structs, crew_messages = rosters_ok_for_publish(self.currentArea, self.start, self.end)
        self.crew_structs = crew_structs
        self.crewList = [crew.crewid  for crew in crew_structs]
        return True, ''

    def displayFinishedOKMessage(Self):
        pass

    def handleContinueMessage(self, message=''):
        return True

    def splitPACTsAtPeriodEnd(self):
        RosterPublish.splitPACTsAtPeriodEnd(self)
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        merge_pacts_in_period(self.currentArea)
        self._log("Mergiing PACT:s in period")
        timer("Merging PACTS")

    def tagInstructors(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        Training.set_instructor_tag(mode='PUBLISH',area=self.currentArea, flags = Training.SILENT_FORM)
        timer("Tag instructors")
        self._log("Tagged instructors")


class HistoricPublish(BatchPublish):
    """
    This class tags all rosters with all publishing tags except SCHEDULED,
    so that crew can see their rosters through the report-servers
    """
    def __init__(self, split=True):
        BatchPublish.__init__(self)
        self._split = split

    def tagPublished(self):
        # CuiPublishRosters shall have a UTC time interval as argument.
        self._log("Perform actual publish")
        pubtypes = [ptype for ptype in PUBLICATION_TYPES
                    if ptype != ROSTERING_PUBLISHED_TYPE]
        publist = [(crew.crewid, ptype, int(crew.start_utc), int(crew.end_utc))
                   for crew  in self.crew_structs
                   for ptype in pubtypes ]

        Cui.CuiPublishRosters(Cui.gpc_info,
                              publist,
                              "HISTORIC PUBLISH",
                              Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
                              | Cui.CUI_PUBLISH_ROSTER_SKIP_SAVE)
        UpdateManager.setDirtyTable("published_roster")
        UpdateManager.setGuiChange()
        timer("SYS-Publish")

    def splitPACTsAtPeriodStart(self):
        if self._split:
            BatchPublish.splitPACTsAtPeriodStart(self)

    def splitPACTsAtPeriodEnd(self):
        if self._split:
            BatchPublish.splitPACTsAtPeriodEnd(self)

    def publish(self):
        timer()

        # create crew structs and crew list
        self.checkRosters()
        UpdateManager.start()
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)

        # Perform the different publishing steps
        self.tagInstructors()
        self.splitPACTsAtPeriodStart()
        self.splitPACTsAtPeriodEnd()
        self.publishCompensationDays()
        self.save("Save before actual publish", "Saved plan")

        self.tagPublished()
        self.setPublishedAttributes()
        self.save("Save after actual publish and rescheduling", "Saving published data")

        UpdateManager.done()
        
        self._log("Finished")
        printTimes("Publish rosters")


class TagPublish(BatchPublish):
    def __init__(self):
        BatchPublish.__init__(self)

    def tagPublished(self):
        # CuiPublishRosters shall have a UTC time interval as argument.
        self._log("Perform actual publish")
        pubtypes = [ptype for ptype in PUBLICATION_TYPES]
        publist = [(crew.crewid, ptype, int(crew.start_utc), int(crew.end_utc))
                   for crew  in self.crew_structs
                   for ptype in pubtypes ]

        Cui.CuiPublishRosters(Cui.gpc_info,
                              publist,
                              "TAG PUBLISH",
                              Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
                              | Cui.CUI_PUBLISH_ROSTER_SKIP_SAVE)
        UpdateManager.setDirtyTable("published_roster")
        UpdateManager.setGuiChange()
        timer("SYS-Publish")
        
    def publish(self):
        timer()

        # create crew structs and crew list
        self.checkRosters()
        UpdateManager.start()
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)

        # Perform the different publishing steps
        self.splitPACTsAtPeriodStart()
        self.splitPACTsAtPeriodEnd()
        self.save("Save before actual publish", "Saved plan")

        self.tagPublished()
        self.setPublishedAttributes()
        self.save("Save after actual publish", "Saving published data")

        UpdateManager.done()
        
        self._log("Finished")
        printTimes("Publish rosters")

@clockme
def publish():
    """
    Performs the normal rostering publish
    """
    publisher = RosterPublish()
    return publisher.publish()
