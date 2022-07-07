"""
Contains callback functions called by Studio upon opening and saving plans.

Resources that control which functions that are used:
    gpc.config.openPlanPreProcessing  -> openPlanPreProc()
    gpc.config.openPlanPostProcessing -> openPlanPostProc()
    gpc.config.savePlanPreProcessing  -> savePlanPreProc()
    gpc.config.savePlanPostProcessing -> savePlanPostProc()

Work will be dispatched to another module depending on which product is used.
"""

import carmusr.application as application
if application.isTracking:
    import carmusr.tracking.FileHandlingExt as module
elif application.isDayOfOps:
    import carmusr.tracking.FileHandlingExt as module
elif application.isPlanning:
    import carmusr.planning.FileHandlingExt as module
elif application.isPreplanning:
    import carmusr.preplanning.FileHandlingExt as module
elif application.isServer:
    module = None
else:
    import os
    print '\n'.join('%s = %s' % x for x in os.environ.items())
    raise Exception,"No application type set"

import carmusr.DaveFilterTool as DaveFilterTool
import __main__
import AbsTime
import RelTime
import Crs
import Errlog
import Cps
import signal 
import os

from Variable import Variable

MODULE = "carmusr.FileHandlingExt"

def openPlanPreProc():
    """
    Running functions after the CARMSYS function for
    opening a plan has been used.
    """
    Errlog.log(MODULE + "::openPlanPreProc:: Entered")
    if application.isServer:
        return
    __kill_jvm()
        
    module.openPlanPreProc()
    
def __kill_jvm():
    """
    Hack to kill the jvm in order to bring down forms to prevent studio crashes
    due to accessing old model
    """
    Errlog.log(MODULE+"::kill_jvm:: Entered")
    pid = Cps.Find('','Launcher')
    if pid>0:
        os.kill(pid,signal.SIGTERM) #First nicely!
        pid = Cps.Find('','Launcher')
        if pid>0:
            os.kill(pid,signal.SIGKILL) # Then not so nicely...
        Errlog.log(MODULE+"::kill_jvm:: Killed jvm with pid %s"%pid)
            
def openPlanPostProc():
    """
    Running functions after the CARMSYS function for
    opening a plan has been used.
    """
    Errlog.log(MODULE + "::openPlanPostProc:: Entered")
    if application.isServer:
        return
    module.openPlanPostProc()
    
def savePlanPostProc():
    """
    Running functions after the CARMSYS function for
    saving a plan has been used.
    """
    Errlog.log(MODULE + "::savePlanPostProc:: Entered")
    if application.isServer:
        return
    module.savePlanPostProc()

def savePlanPreProc():
    """
    Running functions before the CARMSYS function for
    saving a plan will be used.
    """
    Errlog.log(  MODULE + "::savePlanPreProc:: Entered")
    if application.isServer:
        return
    return module.savePlanPreProc()

def setDaveLoadFilters():
    """
    Running functions before the CARMSYS function for
    saving a plan will be used.
    """
    Errlog.log( MODULE + "::setDaveLoadFilters:: Entered")

    if application.isServer or os.environ.get('SIMULATED_REPORTSERVERNAME', ''):
        if application.isAlertGenerator:
            return setDaveLoadFiltersAlertGenerator()
        else:
            return setDaveLoadFiltersServer(application.isAccumulator)
    else:
        return module.setDaveLoadFilters()

def setDaveLoadFiltersServer(isAccumulator = False):
    """
    Sets the filters for the Servers
    """
    Errlog.log( MODULE + "::setDaveLoadFiltersServer:: Entered")

    periodPre = 0
    periodPost = 0
    dbPeriodStart = AbsTime.AbsTime(str(__main__.PERIOD_START))
    dbPeriodEnd = AbsTime.AbsTime(str(__main__.PERIOD_END))

    if not application.isReportWorker:
        # Do not adjust the period start for report workers, use the configuration
        dbPeriodStart = dbPeriodStart.month_floor()

        # Add the pre resource buffer
        periodPre = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef,"DataPeriodDbPre")

    # Add the post resource buffers
    periodPost = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef,"DataPeriodDbPost")

    dbPeriodStart = dbPeriodStart - RelTime.RelTime(int(periodPre)*24*60)
    dbPeriodEnd = dbPeriodEnd + RelTime.RelTime(int(periodPost)*24*60) + RelTime.RelTime(24*60-1)

    __main__.PERIOD_START = Variable(dbPeriodStart)
    __main__.PERIOD_END = Variable(dbPeriodEnd)


    threeyrsbefstart = dbPeriodStart - RelTime.RelTime(3*366*24*60)
    oneyrbefstart = dbPeriodStart - RelTime.RelTime(366*24*60)
    threemonthsbefstart = dbPeriodStart - RelTime.RelTime(3*30*1440)
    threemonthsafterend = dbPeriodEnd + RelTime.RelTime(3*30*1440)
    max_trip_length = 5
    max_number_of_days_with_optional_variant_deadheads_before_trip = 1
    trip_start = dbPeriodStart - RelTime.RelTime(max_trip_length*1440)
    trip_end = dbPeriodEnd + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_start = trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_end = trip_end + RelTime.RelTime(max_trip_length*1440)

    filterTool = DaveFilterTool.DaveFilterTool()

    param_filters = []

    ## Very important to set the period filter!!
    param_filters += [("period", "start", str(dbPeriodStart)[0:9]),
                      ("period", "end", str(dbPeriodEnd)[0:9]),
                      ("period", "start_time", str(dbPeriodStart)),
                      ("period", "end_time", str(dbPeriodEnd)),
                      ("period", "threeyrsbefstart", str(threeyrsbefstart)),
                      ("period", "oneyrbefstart", str(oneyrbefstart)),
                      ("period", "threemonthsbefstart", str(threemonthsbefstart)),
                      ("period", "threemonthsafterend", str(threemonthsafterend)),
                      ("period", "trip_start", str(trip_start)),
                      ("period", "trip_end", str(trip_end)),
                      ("period", "leg_start", str(leg_start)),
                      ("period", "leg_end", str(leg_end))]

    if not isAccumulator:
        # Set also Accumulator filters for the report server
        one_yr_bef_start = dbPeriodStart - RelTime.RelTime(366*24*60)
        two_yrs_bef_start = dbPeriodStart - RelTime.RelTime(2*366*24*60)
        seven_yrs_bef_start = dbPeriodStart - RelTime.RelTime(7*366*24*60)
        one_month_bef_start = dbPeriodStart.adddays(-30)
        param_filters += [("accperiod", "start", str(dbPeriodStart)),
                          ("accperiod", "end", str(dbPeriodEnd)),
                          ("accperiod", "oneyrbefstart", str(one_yr_bef_start)),
                          ("accperiod", "twoyrsbefstart", str(two_yrs_bef_start)),
                          ("accperiod", "sevenyrsbefstart", str(seven_yrs_bef_start)),
                          ("accperiod", "onemonthbefstart", str(one_month_bef_start)),
                          ("accperiod", "threemonthsbefstart", str(threemonthsbefstart))]
        
        param_filters += [("report_server_filter", "preventload", '1')]
        param_filters += [("report_server_filter", "startdate", str(dbPeriodStart)[0:9])]
        param_filters += [("report_server_filter", "twoyrsbefstartdate", str(two_yrs_bef_start)[0:9])]
        param_filters += [("report_server_filter", "enddate", str(dbPeriodEnd)[0:9])]
        param_filters += [("report_server_filter", "starttime", str(dbPeriodStart))]
        param_filters += [("report_server_filter", "endtime", str(dbPeriodEnd))]                  

        reportserver_name = os.environ.get('SIMULATED_RESPORTSERVERNAME', '')
        if not reportserver_name:
            reportserver_name = os.environ.get('CARM_PROCESS_NAME', 'Obvious Error Code')

        if 'SAS_RS_WORKER_PUBLISH' in reportserver_name:
            # Must be after publish_future!
            filterTool.set_filter('report_srv_no_salary')

        elif 'SAS_RS_WORKER_LATEST_CUSTOM' in reportserver_name:
            # Must be before the 'latest' reportworkers!
            pass
        
        elif 'SAS_RS_WORKER_LATEST' in  reportserver_name:
            # Must be after all other reportworkers which start with this name...
            pass
                    
        elif 'SAS_RS_WORKER_SCHEDULED' in  reportserver_name:
            filterTool.set_filter('report_srv_no_salary')
            filterTool.set_filter('report_srv_no_tracking')
        
        else:
            pass

    # Set the server filter parameters
    if isAccumulator:
        param_filters += [("crew_user_filter_active", "start", str(dbPeriodStart)),
                          ("crew_user_filter_active", "end", str(dbPeriodEnd))]

        # Also check if a maincat and/or region is set and activate such a filter if needed
        # This can be done from Accumulators.py for instance
        num_attributes = 0
        if hasattr(__main__, 'SK_MAINCAT'):
            maincat = __main__.SK_MAINCAT
            num_attributes += 1
        else:
            maincat = '_'

        if hasattr(__main__, 'SK_REGION'):
            region = __main__.SK_REGION
            num_attributes += 1
        else:
            region = '___'

        # Check if anything was set and only apply a filter then
        if num_attributes > 0:
            empl_str = maincat+'|'+region
            param_filters += [("crew_user_filter_employment", "start", str(dbPeriodStart)),
                              ("crew_user_filter_employment", "end", str(dbPeriodEnd)),
                              ("crew_user_filter_employment", "rank_planning_group", empl_str)]
                              
            
    
    # account_entry filters, only use if current baseline is before plan start
    filterTool.set_baseline_filter(dbPeriodStart)    

    # Set the filters
    filterTool.set_param_filters(param_filters)

    filterTool.set_filter('studio_filter')
    return 0



def setDaveLoadFiltersAlertGenerator():
    """
    Sets the filters for the Alert Generator - Same filters as Tracking
    Only works because the Aler Generator hook changed the Resource 'LoadFilter'
    """
    Errlog.log( MODULE + "::setDaveLoadFiltersAlertGenerator:: Entered")
    Errlog.log( MODULE + "::setDaveLoadFiltersAlertGenerator:: __main__" + str(__main__))
    
    dbPeriodStart = AbsTime.AbsTime(str(__main__.PERIOD_START))
    dbPeriodEnd = AbsTime.AbsTime(str(__main__.PERIOD_END))
    
    # Add the pre and post resource buffers
    periodPre = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef,"DataPeriodDbPre")
    periodPost = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef,"DataPeriodDbPost")

    # stefanh 23Mar2009: modified dbPeriodStart to be the same as calculated in
    #   carmusr.tracking.FileHandlingExt. There, month start becomes 00:00 on
    #   the day before. I.e. if current day is after the 6th in a month, then
    #   the db load period will start 00:00 on the last day of the privious
    #   month: 31Jan, 28/29Feb, 31Mar, ..., 31Dec.
    dbPeriodStart = min(dbPeriodStart.month_floor() - RelTime.RelTime(24*60),
                        dbPeriodStart - RelTime.RelTime(int(periodPre)*24*60))
    dbPeriodEnd = dbPeriodEnd + RelTime.RelTime(int(periodPost)*24*60) + RelTime.RelTime(24*60-1)
    #Errlog.log( MODULE + "::setDaveLoadFiltersAlertGenerator:: DB_PERIOD_START " + str(dbPeriodStart))
    #Errlog.log( MODULE + "::setDaveLoadFiltersAlertGenerator:: DB_PERIOD_END   " + str(dbPeriodEnd))
    threeyrsbefstart = dbPeriodStart - RelTime.RelTime(3*366*24*60)
    oneyrbefstart = dbPeriodStart - RelTime.RelTime(366*24*60)
    threemonthsbefstart = dbPeriodStart - RelTime.RelTime(3*30*1440)
    threemonthsafterend = dbPeriodEnd + RelTime.RelTime(3*30*1440)

    # We are not going to load any extra data for alert generator,
    # so we set these parameters to 0!
    max_trip_length = 5
    max_number_of_days_with_optional_variant_deadheads_before_trip = 1

    trip_start = dbPeriodStart - RelTime.RelTime(max_trip_length*1440)
    trip_end = dbPeriodEnd + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_start = trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
    leg_end = trip_end + RelTime.RelTime(max_trip_length*1440)

    # Calculate the accumulator parameters
    one_yr_bef_start = dbPeriodStart - RelTime.RelTime(366*24*60)
    two_yrs_bef_start = dbPeriodStart - RelTime.RelTime(2*366*24*60)
    seven_yrs_bef_start = dbPeriodStart - RelTime.RelTime(7*366*24*60)
    one_month_bef_start = dbPeriodStart.adddays(-30)
    filterTool = DaveFilterTool.DaveFilterTool()

    param_filters = []

    ## Very important to set the period filter!!
    param_filters += [("period", "start", str(dbPeriodStart)[0:9]),
                      ("period", "end", str(dbPeriodEnd)[0:9]),
                      ("period", "start_time", str(dbPeriodStart)),
                      ("period", "end_time", str(dbPeriodEnd)),
                      ("period", "threeyrsbefstart", str(threeyrsbefstart)),
                      ("period", "oneyrbefstart", str(oneyrbefstart)),
                      ("period", "threemonthsbefstart", str(threemonthsbefstart)),
                      ("period", "threemonthsafterend", str(threemonthsafterend)),
                      ("period", "trip_start", str(trip_start)),
                      ("period", "trip_end", str(trip_end)),
                      ("period", "leg_start", str(leg_start)),
                      ("period", "leg_end", str(leg_end))]

    # Geographical region split - this is needed to filter in crew employment
    param_filters += [("crew_user_filter_active", "start", str(dbPeriodStart)),
                      ("crew_user_filter_active", "end", str(dbPeriodEnd))]

    # Accumulator filters
    param_filters += [("accperiod", "start", str(dbPeriodStart)),
                      ("accperiod", "end", str(dbPeriodEnd)),
                      ("accperiod", "oneyrbefstart", str(one_yr_bef_start)),
                      ("accperiod", "twoyrsbefstart", str(two_yrs_bef_start)),
                      ("accperiod", "sevenyrsbefstart", str(seven_yrs_bef_start)),
                      ("accperiod", "onemonthbefstart", str(one_month_bef_start)),
                      ("accperiod", "threemonthsbefstart", str(threemonthsbefstart))]

    # account_entry filters, only use if current baseline is before plan start
    filterTool.set_baseline_filter(dbPeriodStart)

    # Set the filters
    filterTool.set_param_filters(param_filters)
    filterTool.set_filter('studio_filter')

    return 0

def getDbPeriodStart(startTime):
    """
    DataDbPeriodPreFunc calls this function to calculate the DbPeriodStart
    This function takes an integer time as argument and return the number of days
    before the planningperiod start that should be loaded. Default the SYS function
    returns the value of the resource DataDbPeriodPre.
    
    Pointed out as a callback by the gpc.config.DataPeriodDbPreFunc resource,
    which normally is set to this function only in "Server.etab". However,
    just to be sure, the logic valid for the <tracking> FileHandlingExt is
    applied here also (using the CARMUSINGAM environment variable).
    """
    dbPrePeriod = int(Crs.CrsGetModuleResource(
                        "config", Crs.CrsSearchAppDef, "DataPeriodDbPre"))
    if int(startTime) > -1:
        Errlog.log("%s::getDbPeriodStart CARMUSINGAM=%s, isServer=%s, isAlertGenerator=%s" % (MODULE,bool(os.environ.get('CARMUSINGAM')),application.isServer,application.isAlertGenerator))
        if bool(os.environ.get('CARMUSINGAM')) or (application.isServer and application.isAlertGenerator):
            try:
                dayOfMonth = int(AbsTime.AbsTime(startTime).ddmonyyyy(True)[0:2])
                Errlog.log("%s::getDbPeriodStart-->DataPeriodDbPre adjusted=%d"
                           % (MODULE, max(dayOfMonth, dbPrePeriod)))
                return max(dayOfMonth, dbPrePeriod)
            except:
                pass

        elif application.isReportWorker:
            # Workaround for reportworker periods, no pre-buffer!
            dbPrePeriod = 0 
          
    Errlog.log("%s::getDbPeriodStart-->DataPeriodDbPre=%d"
               % (MODULE,dbPrePeriod))
    return dbPrePeriod
