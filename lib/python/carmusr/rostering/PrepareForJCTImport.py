
#######################################################
#
#   Prepare for JCT import
#
#######################################################
"""
Prepare file base roster plan for import of assignments to JCT

The script performs the most important roster publish steps in order
to be able to import the assignments using Fetch Assignments in JCT


Steps done are the following:

1. Split PACTs at period end
2. Convert ground duties to pact
3. Disconnect base variants
4. remove open time variants
5. remove hard locks

"""
import Cui
import Errlog
import Select

import carmusr.rostering.Publish as Publish
import carmensystems.rave.api as R

from utils.performance import clockme
from utils.guiutil import UpdateManager
import traceback


def split_pacts_at_period_end(workarea):
    """
    Split pacts (crew_activity) crossing the publish period end into two parts;
    one in the current publish period, and one after.
    Note: Currently, the split occurs at 'fundamental.%publ_period_end_utc%',
          which is common to all crew, including Asian.
    """
    Errlog.log("Publish::in split_pacts_at_period_end")
    
    _split_pacts_at_period_border(workarea, 'publish.%split_pact_at_period_end%', "fundamental.%publ_period_end%")
    

def _split_pacts_at_period_border(workarea, rave_condition, rave_split_time):

    Errlog.log("Prepare::in split_pacts_at_period_border")
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, workarea, 'WINDOW')
    Select.select({
        'FILTER_METHOD': 'SUBSELECT',
        'FILTER_MARK': 'LEG',
        rave_condition: 'TRUE',
        'planning_area.%crew_is_in_planning_area_at_leg_start_hb%': 'TRUE',
        }, workarea, Cui.CrewMode)
    
    #return 0
    
    Cui.CuiSetCurrentArea(Cui.gpc_info, workarea)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, workarea, 'WINDOW')
    
    # This is the split time used by publish.%split_pact_at_period_end%.
    # We'll use it for the actual split operation, too.
    publ_period_border_hb, = R.eval(rave_split_time)
        
    # Get some useful info regarding the pacts to split.
    # The info will be used to recreate the pacts in split form.
    
    #return 0
    #import utils.rave
    #pact_iter = utils.rave.RaveIterator(
    #    R.iter('iterators.leg_set', where="marked"), {
    #        'crew_id':        'crew.%id%',
    #        'station':       'leg.%start_station%',
    #        'task_code':      'leg.%code%',
    #        'start_hb':      'leg.%start_hb%',
    #        'end_hb':        'leg.%end_hb%',
    #        }).eval('default_context')
     
    
    default_bag = R.context('default_context').bag()
    pact_list = []
    for roster_bag in default_bag.iterators.roster_set():
        crew_id = roster_bag.crew.id()
        for trip in roster_bag.iterators.trip_set(where="trip.%is_pact%"):
            for act in trip.iterators.leg_set(where="marked"):
                task_code = act.leg.code()
                station = act.leg.start_station()
                start_hb = act.leg.start_hb()
                end_hb = act.leg.end_hb()
                
                pact_list.append((crew_id, task_code, station, start_hb, end_hb))


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

    #Cui.CuiDeassignCrr(Cui.gpc_info, workarea, 0)
    try:
        Cui.CuiDeassignCrrs(Cui.gpc_info, workarea, "marked", 0)
    except:
        pass
    #return 0

    flags = Cui.CUI_CREATE_PACT_DONT_CONFIRM | Cui.CUI_CREATE_PACT_SILENT | Cui.CUI_CREATE_PACT_NO_LEGALITY | Cui.CUI_CREATE_PACT_FORCE | Cui.CUI_CREATE_PACT_TASKTAB
    task_code_suffix = ""
    for pact in pact_list:
        crew_id = pact[0]
        task_code = pact[1]
        station = pact[2]
        start_hb = pact[3]
        end_hb = pact[4]
        Cui.CuiCreatePact(Cui.gpc_info,
                          crew_id,
                          task_code,
                          task_code_suffix,
                          start_hb,
                          publ_period_border_hb,
                          station,
                          flags)
        Cui.CuiCreatePact(Cui.gpc_info,
                              crew_id,
                              task_code,
                              task_code_suffix,
                              publ_period_border_hb,
                              end_hb,
                              station,
                              flags)
        

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
    # Cui.CuiSyncModels(Cui.gpc_info) -- TODO: Check if this is needed
    return

# Function for converting certain ground duties to PACT:s
def convertGDtoPACT(current_area = Cui.CuiArea0):
    """
    This function loops over certain ground duty activities on the roster
    overlapping the publishing period and create PACT:s.
    The actual codes will be retained.

    Window 0 must contain rosters.
    """
    Errlog.log("Prepare::in convertGDtoPACT")    
        
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

                # TODO: This needs to be done in a database plan... disable for now.
                #if sby_after_publ_period and wop_start <> publ_wop_start:
                    # If the SBY wop started in publ period, we tag it with wop start,
                    # but only if this is necessary
                    #attr_vals = {"abs":wop_start}
                    #Attributes.SetCrewActivityAttr(crew_id, leg_start_utc, gd_code,
                    #                               "SBY", refresh=False,
                    #                               **attr_vals)
                    #print "Tagged %s at %s with %s" %(gd_code, leg_start_utc, wop_start)
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
    #Attributes._refresh("crew_activity_attr") # TODO: 
    Errlog.log("Publish::convertGDtoPACT finished (converted to %d PACTs)" % convertcount)


class RosterPrepare(Publish.RosterPublish):
    """
    Prepare file based plan for import to JCT
    using Fetch Assignments
    """
    def __init__(self):
        Publish.RosterPublish.__init__(self)
        self.warningMessage = "Performing this operation is irreversible and can not be undone.\n" +\
                               "Rosters for crew in plan for the"+\
                               " time period %s to %s will be prepared.\n" %  (self.start,self.end)+\
                               "All changes made to plan will be saved.\n\n"
        default_bag = R.context('sp_crew').bag()

    def splitPACTsAtPeriodEnd(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        split_pacts_at_period_end(self.currentArea)
        self._log("Splitting PACT:s at period end")
        Publish.timer("Splitting PACTS")

    def convertToPACT(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        convertGDtoPACT(self.currentArea)
        self._log("Converting GD:s to PACT:s")
        Publish.timer("Convert GD to PACTS")

    def disconnectVariants(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)
        disconnect_variants(self.crew_structs, self.currentArea)
        self._log("Removing base variants from assigned trips")
        Publish.timer("Removing base variants")

    def checkRosters(self):
        ok_to_publish, crew_structs, crew_messages = Publish.rosters_ok_for_publish(self.currentArea, self.start, self.end)
        self.crew_structs = crew_structs
        self.crewList = [crew.crewid  for crew in crew_structs]
        return True, ''

    def prepare(self):
        """
        Performs the actual prep steps
        """
        Publish.timer()
        # Check for holes and/or overlaps and create crew structs and crew list
        ok_to_publish, message  = self.checkRosters()
        #Publish.timer("Evaluate if rosters OK for prepare")
        
        self._log("About to prepare: %s with %d crews"%(self.getPlanningAreaString(), len(self.crewList)))

        UpdateManager.start()
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, self.currentArea, Cui.CrewMode,Cui.CrewMode, self.crewList)

        #self.markCrewModified()

        # Perform the different publishing steps
        #self.setCrewMealAttr()
        #self.tagInstructors()

        #self.splitPACTsAtPeriodStart()
        self.splitPACTsAtPeriodEnd()

        #self.publishCompensationDays()
        #self.publishAccumulators()
        self.convertToPACT()
        #self.moveAStoAH()
        self.disconnectVariants()
        self.removeOpenTimeVariants()
        #self.convertExtraSeatsInUnassignedTrips()
        self.removeHardLocks()
        #self.updateCrewFairnessHistory()
        #self.setCimberCabinCrewInCharge()

        #self.updateHalfFreedayCarryOver()
        #self.savePreprocessing()

        #save_ok = self.save("Save prep plan", "Saved plan")


@clockme
def prepare():
    """
    Prepare file based roster plan for fetching assignments from JCT
    """
    prep = RosterPrepare()
    return prep.prepare()

