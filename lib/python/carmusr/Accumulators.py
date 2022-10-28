#!/usr/bin/env python


"""
Functions for (daily) maintenance of different counters/accumulators.
"""

import os
import sys
import time
import traceback
import __main__

import Variable
import Cui
import Crs
import Errlog
import AbsTime
import RelTime

import carmensystems.rave.utils as rave_utils
import carmensystems.rave.api as R


from tm import TM


## Set this global for testgin/debugging, otherwise Accumulators will run as normal
SELECTED_ACCUMULATORS = "accumulators.a2lh_flights_sectors_daily_acc"]
## comment this out when done testing/debugging:
# SELECTED_ACCUMULATORS = ["accumulators.nr_planned_p_days_skn_cc_acc", "accumulators.nr_planned_sb_ln_days_cc_acc"]

## This one should be obvious:
DEBUG = False
#DEBUG = True


def debug_info(area=None):
    if DEBUG:
        print "  ### DEBUG START ### "
        print "              area: %s" % area
        print
        print "      acc_start_p:", R.param("accumulators.%acc_start_p%").value()
        print "        acc_end_p:", R.param("accumulators.%acc_end_p%").value()
        print " accumulator_mode:", R.param("accumulators.%accumulator_mode%").value()
        print "job_publication_p:", R.param("accumulators.%job_publication_p%").value()

        print "    is_publ_debug:", R.eval("accumulators.%is_publ_debug%")[0]
        print "             pp_start:", R.eval("fundamental.%pp_start%")[0]
        print "               pp_end:", R.eval("fundamental.%pp_end%")[0]
        print "         actual_acc_start:", R.eval("accumulators.%actual_acc_start%")[0]
        print "           actual_acc_end:", R.eval("accumulators.%actual_acc_end%")[0]
        print "               publ_acc_start:", R.eval("accumulators.%publ_acc_start%")[0]
        print "                 publ_acc_end:", R.eval("accumulators.%publ_acc_end%")[0]
        print "  ### DEBUG END ### "


def accumulatePublished(area=Cui.CuiArea0, select_accumulators=SELECTED_ACCUMULATORS):
    """
    The published accumulator expects a plan to be loaded and
    pp_start to be set, publ_period_end is calculated from pp_start.
    Only accumulators that are ran at publish shall be published.
    This shall be controlled with the job_publication_p parameter
    """
    Errlog.log("Accumulators::in accumulatePublished")
    # Set publication only
    R.param("accumulators.%accumulator_mode%").setvalue(True)
    R.param("accumulators.%job_publication_p%").setvalue(True)
    # Run all accumulators
    Errlog.log("Accumulators::accumulatePublished accumulating")
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
    try:
        if select_accumulators:
            Errlog.log("Accumulators::accumulatePublished SELECTED_ACCUMULATORS: %s" % select_accumulators)
            rave_utils.eval_selected_accumulators(select_accumulators)
        else:
            rave_utils.eval_accumulators()
    except:
        traceback.print_exc()
    debug_info(area)
    R.param("accumulators.%accumulator_mode%").setvalue(False)
    R.param("accumulators.%job_publication_p%").setvalue(False)
    Errlog.log("Accumulators::accumulatePublished finished")


def accumulate_rave_pub(ival_start, ival_end, area=Cui.CuiArea0):
    """Update Rave accumulators as if when publishing. (For DEV/Testing purposes.)"""

    R.param("accumulators.%acc_start_p%").setvalue(ival_start)
    R.param("accumulators.%acc_end_p%").setvalue(ival_end)
    R.param("accumulators.%is_publ_debug_p%").setvalue(True)

    Errlog.log("Accumulator.accumulate_rave_pub:: accumulating...")
    # load roster
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CuiShowAll)
    accumulatePublished()


def accumulate_rave(ival_start, ival_end, area=Cui.CuiArea0, select_accumulators=SELECTED_ACCUMULATORS):
    """Update Rave accumulators."""
    # The planning area is set to the interval in the tracking rule-set
    R.param("accumulators.%acc_start_p%").setvalue(ival_start)
    R.param("accumulators.%acc_end_p%").setvalue(ival_end)
    R.param("accumulators.%accumulator_mode%").setvalue(True)
    R.param("accumulators.%job_publication_p%").setvalue(False)

    Errlog.log("Accumulator.accumulate_rave:: accumulating...")
    # Display roster
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CuiShowAll)
    # Accumulate
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
    if select_accumulators:
        Errlog.log("Accumulators::accumulate_rave SELECTED_ACCUMULATORS: %s" % select_accumulators)
        rave_utils.eval_selected_accumulators(select_accumulators)
    else:
        rave_utils.eval_accumulators()
    debug_info()


def update_accounts():
    """Update crew accounts for all loaded crew."""
    # The planning area is already set in the tracking rule-set
    Errlog.log("Accumulator.update_accounts:: updating all crew accounts...")
    import carmusr.AccountHandler
    # Display roster
    currentArea = Cui.CuiArea0
    Cui.CuiDisplayObjects(Cui.gpc_info, currentArea, Cui.CrewMode, Cui.CuiShowAll)
    # Get list of all crew
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, currentArea, "window")
    crewList = Cui.CuiGetCrew(Cui.gpc_info, currentArea, "WINDOW")

    # Update all the accounts for crew in list
    carmusr.AccountHandler.updateChangedCrew(crewList)


def update_lifetime_block_hours():
    """Update lifetime_block_hours."""
    Errlog.log("Accumulator.update_lifetime_block_hours:: updating lifetime_block_hours...")
    import carmusr.CrewTableHandler as CTH
    CTH.update_lifetime_block_hours_orig()


def update_ctl():
    """Update crew training log."""
    # The planning area is already set in the tracking rule-set
    Errlog.log("Accumulator.update_ctl:: updating crew training log...")
    import carmusr.CrewTableHandler as CTH
    CTH.update_ctl_all_crew()


def update_rec(extraction_date=None):
    """Update recurrent crew documents."""
    if extraction_date is not None:
        extraction_date = AbsTime.AbsTime(extraction_date).day_floor()
    # The planning area is already set in the tracking rule-set
    Errlog.log("Accumulator.update_rec:: updating all recurrent documents...")
    R.param('fundamental.%debug_verbose_mode%').setvalue(True)
    import carmusr.CrewTableHandler as CTH
    CTH.update_rec(extraction_date=extraction_date)
    R.param('fundamental.%debug_verbose_mode%').setvalue(False)


def update_airport_qual():
    """Updates the airport qual"""
    Errlog.log("Accumulator.update_airport_qual:: Starting updating airport qualifications...")
    import carmusr.CrewTableHandler as CTH
    CTH.extendAirportQualifications()
    Errlog.log("Accumulator.update_airport_qual:: Finished updating airport qualifications...")

  
def update_new_hire_follow_up_table():
    """Update New-hire follow up."""
    # The planning area is already set in the tracking rule-set
    Errlog.log("Accumulator.update_new_hire_follow_up_table:: updating new_hire_follow_up...")

    import carmusr.NewHireFollowUpHandler as NHFUH
    NHFUH.update_new_hire_follow_up_table()
 

# HELP FUNCTIONS **************************************************************
def openPlan(plan, ival_start, ival_end, maincat=None, region=None):
    """Used to open the plan before accumulation"""
    Errlog.log("Accumulator.openPlan:: Opening plan '%s' interval '%s' to '%s'"%(plan,ival_start, ival_end))
    formData = {"FORM":"OPEN_DATABASE_PLAN", "PERIOD_START":" %s" % ival_start,"PERIOD_END":" %s" % ival_end}

    activateDaveFilters(ival_start, ival_end, maincat, region)
    
    lpString = os.path.dirname(plan)
    flags = Cui.CUI_OPEN_PLAN_FORCE
    print "DEBUG: ", formData, lpString, plan
    
    ret = Cui.CuiOpenSubPlan(formData, Cui.gpc_info, lpString, plan, flags)
    Errlog.log("Accumulator.start::load::opened subplan: %s ret = %s" % (plan,ret))
    Cui.CuiCrcLoadRuleset(Cui.gpc_info, "Tracking")
    R.param("fundamental.%is_report_server%").setvalue(True)
    #R.param('fundamental.%use_now_debug%').setvalue(True)
    #R.param('fundamental.%now_debug%').setvalue(AbsTime.AbsTime('31dec2009'))


def savePlan():
    """Saves the plan"""
    try:
        Errlog.log("Accumulator.savePlan: Saving plan...")
        Cui.CuiSavePlans(Cui.gpc_info, 0)
    except:
        Errlog.log("Accumulator.savePlan: Error: Could not save plan")
        traceback.print_exc()


def activateDaveFilters(ival_start, ival_end, maincat=None, region=None):
    """
    Activates DAVE filters
    Set Periods in python so they can be retreived in the setDaveLoadFilters
    hook function

    Valid values for maincat are F or C
    Valid values for region are SKD, SKS, SKN or SKI
    If None is given there will be no filtering on that particular attribute,
    i.e ALL will be loaded
    """
    __main__.PERIOD_START = Variable.Variable(ival_start)
    __main__.PERIOD_END   = Variable.Variable(ival_end)
    if maincat is not None:
        __main__.SK_MAINCAT = maincat
    if region is not None:
        __main__.SK_REGION = region

    
# start ***********************************************************************
def start(plan, time_arg, run_mode, extraction_date=None, maincat=None, region=None, accumulator=None):
    """This is the accumulator main process as started from bin/accumuator.sh The
    accumulator process shall run once each night when the system load is
    low."""
    # NOTE: The arguments region, extraction_date and run_mode are optional.
    # All arguments are strings, this transformation happens when the arguments
    # are passed from the start script via Studio to this module.
    if extraction_date == 'None':
        extraction_date = None
    if maincat == 'None':
        maincat = None
    if region == 'None':
        region = None

    # Open up Previous month, the current month, and the coming month.
    # Open up a day longer just to be able to set acc_end for rave accumulators so that
    # we can write a value for whats accumulated during the coming month
    given_time = AbsTime.AbsTime(time_arg).day_floor()
    ival_start = (given_time.month_floor() - RelTime.RelTime("00:01")).month_floor()
    ival_end = (given_time+RelTime.RelTime("00:01")).month_ceil().addmonths(1, AbsTime.PREV_VALID_DAY).adddays(1)

    Errlog.log("Accumulator.start:: Running accumulators '%s' on plan: %s. Accumulates from %s to %s" % (run_mode, plan, "%i-%02i" % ival_start.split()[:2], "%i-%02i" % ival_end.split()[:2]))

    # Recreate all rave-trips
    if run_mode in ("trip", "installation"):
        Crs.CrsSetModuleResource("config", "useRaveDefinedTrips", "false","")

    # Open plan
    try:
        openPlan(plan, ival_start, ival_end, maincat, region)
    except Exception, e:
        Errlog.log("Accumulator.start:: Error: Failed to load plan: %s" % plan)
        traceback.print_exc()
        sys.exit()

    # Since we do all the operations in one state we need an explicit
    # call to newState after all tables we intend to change are loaded.
    # Otherwise the changes are not detected
    # [acosta:07/351@14:15] Bugzilla #22606. Load tables explicitely, compare
    # with Bugzilla #11123.
    TM('account_entry', 'crew_document', 'crew_log_acc', 'crew_training_log',
       'crew_qualification','crew_employment', 'crew_training_need',
       'crew_ground_duty_attr', 'crew_flight_duty_attr', 'crew_activity_attr', 'bought_days', 'new_hire_follow_up', 'lifetime_block_hours')
    TM.newState()

    # Show all crew for trip calculation
    if run_mode in ("trip", "installation"):
        currentArea = Cui.CuiArea0
        Cui.CuiDisplayObjects(Cui.gpc_info, currentArea, Cui.CrewMode, Cui.CuiShowAll)
        # Activate rave-trips
        Crs.CrsSetModuleResource("config", "useRaveDefinedTrips", "true","")
        Cui.CuiUpdateLevelsAccordingToRaveAreaId(Cui.gpc_info, currentArea)
        Cui.CuiSyncModels(Cui.gpc_info)
        # end of recalculated trips
        savePlan()

    if run_mode in ("rave", "all", "installation"):
        try:
            # Run the rave accumulators
            accumulate_rave(ival_start, ival_end)
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to run Rave-accumulators ")
            traceback.print_exc()

    if run_mode in ("specific"):
        try:
            # Try running specific accumulater
            global SELECTED_ACCUMULATORS
            SELECTED_ACCUMULATORS = [accumulator]
            accumulate_rave(ival_start, ival_end)
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to run specific Rave accumulator %s", accumulator)
            traceback.print_exc()

    if run_mode is "ravepub":
        # For DEV/testing purposes
        try:
            # accumulate_rave_pub(given_time.month_floor(), (given_time + RelTime.RelTime("00:01")).month_ceil().adddays(1))
            accumulate_rave_pub(ival_start, ival_end)
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to run Rave Publish-accumulators ")
            traceback.print_exc()

    if run_mode in ("account", "all", "installation"):
        try:
            # Run update all accounts
            update_accounts()
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update Accounts ")
            traceback.print_exc()
            
    if run_mode in ("ctl", "all", "installation"):
        try:
            # Run update the crew_training_log
            update_ctl()
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update crew training log ")
            traceback.print_exc()
            
    if run_mode in ("rec", "all", "installation"):
        # Update the recurrent document due dates
        try:
            update_rec(extraction_date)
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update the recurrent document due dates")
            traceback.print_exc()
            
    if run_mode in ("airport", "all", "installation"):
        # Update the airport qualifications
        try:
            update_airport_qual()
            savePlan()        
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update the airport qualifications")
            traceback.print_exc()
#    if run_mode in ("all", "lifeblockhrs", "installation"):
    if run_mode in ("lifeblockhrs", "installation"):  # "hot-fix":  remove "all" so it doesn't run every night.
        # TODO: add call to crontab tasks as a monthly job.
        # TODO: discover the true/original functionality fo this and revert.
        # Update the lifetime block hours
        try:
            update_lifetime_block_hours()
            savePlan()
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update lifetime_block_hours table")
            traceback.print_exc()

    if run_mode in ("new-hire", "all", "installation"):
        # Update the new_hire_follow_up
        try:
            update_new_hire_follow_up_table()
            savePlan()        
        except:
            Errlog.log("Accumulator.start:: Error: Failed to update new_hire_follow_up table")
            traceback.print_exc()

    Errlog.log("Accumulator.start:: done. Exiting...")
    Cui.CuiExit(Cui.gpc_info,Cui.CUI_EXIT_SILENT) 


def profileStart(planI=None, time_argI=None, run_modeI=None):
    """
    Entry point for a profiling run, will create a file in $CARMTMP/logfiles named profiling.Accumulators
    which can be examined using the pstats class in python
    """
    import hotshot, hotshot.stats
    logfile = os.getenv("CARMTMP", ".")
    logfile += "/logfiles/hotshot.Accumulators.%s.stats" % (time.strftime("%Y%m%d.%H%M%S", time.gmtime()))
    print "hotshot stats file for profiling results: ", logfile
    prof = hotshot.Profile(logfile)
    res = prof.runcall(start, plan = planI, time_arg=time_argI, run_mode = run_modeI)
    prof.close()
    stats = hotshot.stats.load(logfile)
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(40)
#    profile.runctx("start(plan='%s',time_arg='%s',run_mode='%s')" % (plan, time_arg, run_mode), globals(), locals(), logfile)
    sys.exit()


if __name__ == "__main__":
    print "Accumulators::running self test"
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
    rave_utils.eval_accumulators()



