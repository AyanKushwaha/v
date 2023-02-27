##################################################

#
# This module contains functions for handling
# bought vacation, free- or compensation days. 
#

import carmensystems.rave.api as R
import Cui
import utils.Names as Names
from RelTime import RelTime
import tm
from modelserver import EntityNotFoundError
import carmusr.HelperFunctions as HF
import carmstd.cfhExtensions as cfhExtensions
import carmusr.modcrew as modcrew
import carmusr.ActivityManipulation as ActivityManipulation
import Cfh
import Gui
import Airport
import carmensystems.studio.Tracking.CreateActivity as CreateActivity
from carmusr.tracking.OpenPlan import CfhCheckDone

TM = tm.TM()

ACCOUNTS = ['BOUGHT', 'BOUGHT_8', 'BOUGHT_FORCED']
ACCOUNTS_SVS = ['BOUGHT_SBY', 'BOUGHT_PROD', 'BOUGHT_DUTY']
BOUGHT_LABELS = [
            'Bought more than 6 hrs',
            'Bought 6 hrs or less',
        
            'OT comp, C/O on Fday']
BOUGHT_LABELS_SVS = [
            'Bought Day Off',
            'Standby',
            'Production',
            'Bought Additional Duty']
LBL_COUNT_CC = 5
LBL_COUNT_FD = 5
LBL_MAX_LEN = 22


class CancelBuyDay(Exception):
    def __str__(self):
        return "Buy Day Cancelled by user"


def days_has_production(start_time, end_time, crew_id):
    return R.eval('default_context',
                  R.foreach(R.iter('iterators.leg_set'),
                            'bought_days.%%crew_has_bought_prod_in_period%%(%s,%s,"%s")' % 
                            (str(start_time), str(end_time), str(crew_id))))[0][0][1]

def activity_shall_be_recreated(activity_code):
    return R.eval('bought_days.%%type_shall_be_recreated%%("%s")' % activity_code)[0]

def activity_shall_be_recreated_svs(activity_code):
    return R.eval('bought_days.%%type_shall_be_recreated_svs%%("%s")' % activity_code)[0]

def get_overlap(start1, end1, start2, end2):
    return int(R.eval("overlap(%s,%s,%s,%s)" % (str(start1), str(end1), str(start2), str(end2)))[0])
 

def buy_days(crew_id, start_time, end_time, leg_type, comment="", bought_day_type="", has_agmt_skd_cc=False, is_valid=False):

    bought_account, bought_8_account,bought_forced_account = ACCOUNTS

    #############################################################
    # This is a "conversion table" for SKD CC to be used once the validity agreement is fullfilled.
    # The idea is that old values should be used until 1Jan2019 after that the new day_type and account
    # for bought F3 days should be used.
    # /oscargr
    is_type_bought_f3 = False
    is_type_bought_f3_2 = False
    if has_agmt_skd_cc and is_valid:
        if bought_day_type == bought_account:
            bought_day_type = "BOUGHT_F3_2"
            bought_f3_2_account = "BOUGHT_F3_2"
            is_type_bought_f3_2 = True
        elif bought_day_type == bought_8_account:
            bought_day_type = "BOUGHT_F3"
            bought_f3_account = "BOUGHT_F3"
            is_type_bought_f3 = True
    #############################################################

    is_type_bought_8 = bought_day_type == bought_8_account
    #is_type_bought_comp = bought_day_type == bought_comp_account
   # is_type_bought_comp_f3s = bought_day_type == bought_comp_f3s_account
    is_type_bought_forced = bought_day_type == bought_forced_account
    

    crew = TM.crew.getOrCreateRef((crew_id,))
    main_cat, = R.eval('crew.%%main_cat_of_crew_id%%("%s",%s)' % (crew_id, start_time))
    is_cabincrew = main_cat == 'C'
    uname = Names.username()

    row_day_type = get_row_day_type(leg_type,start_time)
    # Cache current existing rows, since we might need to loop through these more than once
    periods_to_merge = {}
    touch_start = None
    
    for row in TM.bought_days.search('(crew='+crew_id+')'):
        # If row touches period,  we might need to modify it
        if row.start_time <= start_time <= row.end_time:
            touch_start = row  # Touch start_time
        elif row.start_time == end_time:
            periods_to_merge[row.start_time] = row  # Touch end_time
        elif get_overlap(row.start_time, row.end_time, start_time, end_time) > 0:
            periods_to_merge[row.start_time] = row

    # periods_to_merge.sort(cmp=lambda x,y:cmp(x.start_time,y.start_time))
    finished = False  # Finished when all days covered!
    current_row = touch_start
    while not finished:
        if current_row:
            if current_row.end_time in periods_to_merge:
                next_row = periods_to_merge[current_row.end_time]
                if next_row.day_type == current_row.day_type and next_row.account_name == current_row.account_name:
                    # Merge found period into current
                    current_row.end_time = next_row.end_time
                    next_row.remove()
                    del periods_to_merge[next_row.start_time]
                else:
                    current_row = next_row
            elif current_row.end_time >= end_time:
                break
            elif current_row.day_type == row_day_type and current_row.account_name == bought_day_type:
                # Increase period
                current_row.end_time = current_row.end_time.adddays(1)
            else:
                # Start new period
                start_time = current_row.end_time
                current_row = None
        else:  # Start in empty period!
            current_row = TM.bought_days.create((crew, start_time))
            current_row.day_type = row_day_type
            if row_day_type[:2] == "BL" and not is_cabincrew:
                current_row.account_name = "BOUGHT_BL"
            # elif is_type_bought_comp:
                #   current_row.account_name = bought_comp_account
            elif is_type_bought_8:
                current_row.account_name = bought_8_account
            #elif is_type_bought_comp_f3s:
                #   current_row.account_name = bought_comp_f3s_account
            elif is_type_bought_f3:
                current_row.account_name = bought_f3_account
            elif is_type_bought_f3_2:
                current_row.account_name = bought_f3_2_account
            elif is_type_bought_forced:
                current_row.account_name = bought_forced_account
            else:
                current_row.account_name = bought_account
            current_row.end_time = start_time.adddays(1)
            current_row.uname = uname
            current_row.si = comment
            finished = current_row is not None and \
            current_row.end_time >= end_time and \
            current_row.end_time not in periods_to_merge  # Don't forget to merge end if needed

def integer_to_reltime_hour(val):
    if val is None:
        return RelTime('00:00')
    else:
        val = ("%02d" % val) + ":00"
        val = RelTime(val)
    return val

def integer_to_reltime_min(val):
    if val is None:
        return RelTime('00:00')
    else:
        val = "00:" + ("%02d" % val)  
        val = RelTime(val)
    return val

def buy_days_svs(crew_id, start_time, end_time, leg_type, comment="",time_hh_sby="", time_mm_sby="", time_hh_prod="", time_mm_prod="",time_hh="", time_mm="", bought_day_type="", has_agmt_skd_cc=False, is_valid=False):

    time_hh_Sby, = R.eval('bought_days.%%hr_udor%%("%s")' % str(time_hh_sby))
    time_mm_Sby, = R.eval('bought_days.%%mn_udor%%("%s")' % str(time_mm_sby))
    time_mm_Prod, = R.eval('bought_days.%%mn_udor%%("%s")' % str(time_mm_prod))
    time_hh_Prod, = R.eval('bought_days.%%hr_udor%%("%s")' % str(time_hh_prod))
    time_MM, = R.eval('bought_days.%%mn_udor%%("%s")' % str(time_mm))
    time_HH, = R.eval('bought_days.%%hr_udor%%("%s")' % str(time_hh))
    bought_sby, bought_prod, bought_duty = ACCOUNTS_SVS
    
    is_type_bought_sby = bought_day_type == bought_sby
    is_type_bought_prod = bought_day_type == bought_prod
    is_type_bought_duty = bought_day_type == bought_duty

    crew = TM.crew.getOrCreateRef((crew_id,))
    main_cat, = R.eval('crew.%%main_cat_of_crew_id%%("%s",%s)' % (crew_id, start_time))
    is_cabincrew = main_cat == 'C'
    uname = Names.username()
    
    row_day_type = get_row_day_type(leg_type,start_time)
    # Cache current existing rows, since we might need to loop through these more than once
    periods_to_merge = {}
    touch_start = None
    
    for row in TM.bought_days_svs.search('(crew='+crew_id+')'):
        # If row touches period,  we might need to modify it
        if row.start_time <= start_time <= row.end_time:
            touch_start = row  # Touch start_time
        elif row.start_time == end_time:
            periods_to_merge[row.start_time] = row  # Touch end_time
        elif get_overlap(row.start_time, row.end_time, start_time, end_time) > 0:
            periods_to_merge[row.start_time] = row

    # periods_to_merge.sort(cmp=lambda x,y:cmp(x.start_time,y.start_time))
    finished = False  # Finished when all days covered!
    current_row = touch_start
    while not finished:
        if current_row:
            if current_row.end_time in periods_to_merge:
                next_row = periods_to_merge[current_row.end_time]
                if next_row.day_type == current_row.day_type and next_row.account_name == current_row.account_name:
                    # Merge found period into current
                    current_row.end_time = next_row.end_time
                    next_row.remove()
                    del periods_to_merge[next_row.start_time]
                else:
                    current_row = next_row
            elif current_row.end_time >= end_time:
                if is_type_bought_sby:
                    temp_hour_sby = time_hh_Sby[0:2]
                    if temp_hour_sby[1] == ':':
                        temp_hour_sby = '0' +temp_hour_sby
                    time_hour_Sby = integer_to_reltime_hour(int(temp_hour_sby[0:2]))
                
                    temp_min_sby = time_mm_Sby
                    if temp_min_sby[-2] == ':':
                        temp_min_sby = temp_min_sby[0:3] +  '0' +temp_min_sby[-1]
                    time_minute_Sby = integer_to_reltime_min(int(temp_min_sby[3:]))
                    current_row.hours = time_hour_Sby
                    current_row.minutes = time_minute_Sby
                elif is_type_bought_prod:
                    temp_hour_prod = time_hh_Prod[0:2]
                    if temp_hour_prod[1] == ':':
                        temp_hour_prod = '0' +temp_hour_prod
                    time_hour_Prod = integer_to_reltime_hour(int(temp_hour_prod[0:2]))
                
                    temp_min_prod = time_mm_Prod
                    if temp_min_prod[-2] == ':':
                        temp_min_prod = temp_min_prod[0:3] +  '0' +temp_min_prod[-1]
                    time_minute_Prod = integer_to_reltime_min(int(temp_min_prod[3:]))
                    current_row.hours = time_hour_Prod
                    current_row.minutes = time_minute_Prod
                else:
                    temp_hour = time_HH[0:2]
                    if temp_hour[1] == ':':
                        temp_hour = '0' +temp_hour
                    time_HH_hour = integer_to_reltime_hour(int(temp_hour[0:2]))
                
                    temp_min = time_MM
                    if temp_min[-2] == ':':
                        temp_min = temp_min[0:3] +  '0' +temp_min[-1]
                    time_MM_minute = integer_to_reltime_min(int(temp_min[3:]))
                    current_row.hours = time_HH_hour
                    current_row.minutes = time_MM_minute
                
                break
            elif current_row.day_type == row_day_type and current_row.account_name == bought_day_type:
                # Increase period
                current_row.end_time = current_row.end_time.adddays(1)
                if is_type_bought_sby:
                    temp_hour_sby = time_hh_Sby[0:2]
                    if temp_hour_sby[1] == ':':
                        temp_hour_sby = '0' +temp_hour_sby
                    time_hour_Sby = integer_to_reltime_hour(int(temp_hour_sby[0:2]))
                
                    temp_min_sby = time_mm_Sby
                    if temp_min_sby[-2] == ':':
                        temp_min_sby = temp_min_sby[0:3] +  '0' +temp_min_sby[-1]
                    time_minute_Sby = integer_to_reltime_min(int(temp_min_sby[3:]))
                    current_row.hours = time_hour_Sby
                    current_row.minutes = time_minute_Sby
                if is_type_bought_prod:
                    temp_hour_prod = time_hh_Prod[0:2]
                    if temp_hour_prod[1] == ':':
                        temp_hour_prod = '0' +temp_hour_prod
                    time_hour_Prod = integer_to_reltime_hour(int(temp_hour_prod[0:2]))
                
                    temp_min_prod = time_mm_Prod
                    if temp_min_prod[-2] == ':':
                        temp_min_prod = temp_min_prod[0:3] +  '0' +temp_min_prod[-1]
                    time_minute_Prod = integer_to_reltime_min(int(temp_min_prod[3:]))
                    current_row.hours = time_hour_Prod
                    current_row.minutes = time_minute_Prod
            else:
                # Start new period
                start_time = current_row.end_time
                current_row = None
        else:  # Start in empty period!
            current_row = TM.bought_days_svs.create((crew, start_time))
            current_row.day_type = row_day_type
            if is_type_bought_sby:
                current_row.account_name = bought_sby
                
            elif is_type_bought_prod:
                current_row.account_name = bought_prod
                
                
            else:
                current_row.account_name = bought_duty
            current_row.end_time = start_time.adddays(1)
            if is_type_bought_sby:
                temp_hour_sby = time_hh_Sby[0:2]
                if temp_hour_sby[1] == ':':
                    temp_hour_sby = '0' +temp_hour_sby
                time_hour_Sby = integer_to_reltime_hour(int(temp_hour_sby[0:2]))
                
                temp_min_sby = time_mm_Sby
                if temp_min_sby[-2] == ':':
                    temp_min_sby = temp_min_sby[0:3] +  '0' +temp_min_sby[-1]
                time_minute_Sby = integer_to_reltime_min(int(temp_min_sby[3:]))
                current_row.hours = time_hour_Sby
                current_row.minutes = time_minute_Sby
            if is_type_bought_prod:
                temp_hour_prod = time_hh_Prod[0:2]
                if temp_hour_prod[1] == ':':
                    temp_hour_prod = '0' +temp_hour_prod
                time_hour_Prod = integer_to_reltime_hour(int(temp_hour_prod[0:2]))
                
                temp_min_prod = time_mm_Prod
                if temp_min_prod[-2] == ':':
                    temp_min_prod = temp_min_prod[0:3] +  '0' +temp_min_prod[-1]
                time_minute_Prod = integer_to_reltime_min(int(temp_min_prod[3:]))
                current_row.hours = time_hour_Prod
                current_row.minutes = time_minute_Prod
            if is_type_bought_duty:
                temp_hour = time_HH[0:2]
                if temp_hour[1] == ':':
                    temp_hour = '0' +temp_hour
                time_HH_hour = integer_to_reltime_hour(int(temp_hour[0:2]))
                
                temp_min = time_MM
                if temp_min[-2] == ':':
                    temp_min = temp_min[0:3] +  '0' +temp_min[-1]
                time_MM_minute = integer_to_reltime_min(int(temp_min[3:]))
                current_row.hours = time_HH_hour
                current_row.minutes = time_MM_minute
            
            current_row.uname = uname
            current_row.si = comment
        finished = current_row is not None and \
            current_row.end_time >= end_time and \
            current_row.end_time not in periods_to_merge  # Don't forget to merge end if needed


def get_row_day_type(leg_type,start_time):
        # The activity code to save:
    is_svs, = R.eval(
        R.selected('levels.leg'),
        "crew.%%has_agmt_group_svs_at_date%%(%s)" % start_time,
        )
    print '##Is SVS##:',is_svs    
    if is_svs:
        if not leg_type:
            return "F"
        elif activity_shall_be_recreated_svs(leg_type):
            return leg_type
        else:
            return "P"
    else:
        if not leg_type:
            return "F"
        elif activity_shall_be_recreated(leg_type):
            return leg_type
        elif leg_type[0] == "F":
            return "F"
        else:
            # Unknown...well save as it is for now...
            return leg_type


def unbuy_days(crew_id, start_time, end_time, area):
    try:
        crew = TM.crew[(crew_id,)]
    except EntityNotFoundError:
        return
    uname = Names.username()
    periods_to_remove = []
    for row in TM.bought_days.search('(crew='+crew_id+')'):
        if get_overlap(row.start_time, row.end_time, start_time, end_time) > 0:
            periods_to_remove.append(row)

    recreate_periods = []
    for period in periods_to_remove:
        overlap_start = max(period.start_time, start_time)
        overlap_end = min(period.end_time, end_time)
        account = period.account_name
        if activity_shall_be_recreated(period.day_type):
            if days_has_production(overlap_start, overlap_end, crew_id):
                cfhExtensions.show("Not possible to unbuy %s " % period.day_type + "days which has production")
                continue
            else:
                recreate_periods.append((overlap_start, overlap_end, period.day_type))

        # Merge 
        if overlap_start == period.start_time and overlap_end == period.end_time:
            # Remove entire period!
            period.remove()
        elif overlap_start > period.start_time and overlap_end < period.end_time:
            # Clicked inside entire period, cut into two!
            new_period = TM.bought_days.create((crew, end_time))
            new_period.day_type = period.day_type
            new_period.end_time = period.end_time
            period.end_time = start_time
            new_period.uname = uname
            new_period.account_name = account
            new_period.si = period.si
        elif overlap_start == period.start_time and overlap_end == end_time:
            # cut away beginning of period
            new_period = TM.bought_days.create((crew, end_time))
            new_period.end_time = period.end_time
            new_period.day_type = period.day_type
            new_period.uname = uname
            new_period.account_name = account
            new_period.si = period.si
            period.remove()
        elif overlap_start == start_time and overlap_end == period.end_time:
            period.end_time = start_time
        
    for startTime, endTime, code in recreate_periods:
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crew_id)
        airport = Cui.CuiCrcEvalString(Cui.gpc_info, area, 'object',
                                       'bought_days.%%crew_station_at_date%%(%s)' % startTime)
        # recreate PACT
        crew_ref = TM.crew.getOrCreateRef((crew_id,))
        after_airport_ref = TM.airport.getOrCreateRef(str(airport))
        after_ref = TM.activity_set.getOrCreateRef((str(code),))
        airport_inst = Airport.Airport(airport)
        Cui.CuiSyncModels(Cui.gpc_info)
        CreateActivity.CreateCrewActivity(TM.crew_activity,
                                          startTime,
                                          crew_ref,
                                          after_ref,
                                          endTime,
                                          after_airport_ref,
                                          airport_inst)
    if len(recreate_periods) > 0:
        modcrew.add(crew_id)


def markDaysAsBought(buy):
    """ 
    This function is used in other modules. don't change name or signature.
    """
    # Get days, area and crew id
    # Get start time and end time
    try:
        sel = HF.RosterDateSelection(hb=True)
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    except:
        # User cancelled
        return
    crew_id = sel.crew
    is_buy = buy.lower() == "true"

    # Use home base time instead
    start_time = HF.utc2hb(sel.crew, sel.st)
    end_time = HF.utc2hb(sel.crew, sel.et)
    # Truncate period to fit planning period
    pp_start, = R.eval('fundamental.%loaded_data_period_start%')
    pp_end, = R.eval('fundamental.%loaded_data_period_end%')
    pp_end += RelTime('00:01')  # pp_end_time is inclusive 23:59..

    if is_buy and (start_time < pp_start or pp_end < end_time):
        cfhExtensions.show(
            "Selected period outside loaded data period.\n"
            "Will shorten bought period to fit loaded data period!")
        if start_time < pp_start:
            start_time = pp_start
        if end_time > pp_end:
            end_time = pp_end
        
    # Move crew to script buffer
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               Cui.CuiScriptBuffer,
                               Cui.CrewMode,
                               Cui.CrewMode,
                               [str(crew_id)],
                               0)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
                                Cui.CuiScriptBuffer,
                                'WINDOW')

    eval_result = R.eval(
        R.selected('levels.leg'),
        'crew.%is_temporary%',
        'crew.%is_cabin%',
        'crew.%has_agmt_group_qa%',
        "crew.%%has_agmt_group_svs_at_date%%(%s)" % start_time,
        "salary_overtime.%is_CJ%",
        "salary_overtime.%is_EMJ%",
        "parameters.%%fxx_boughtday_comp_valid_at_date%%(%s)" % start_time,
        'crew.%has_agmt_group_skd_cc%',
        "system_db_parameters.%%f3_compensation_skd_cc%%(%s)" % start_time,
        )
    print "  ## eval_result:", eval_result
    is_temp, is_cabin, is_qa, is_svs, is_cj, is_emj, is_valid, has_agmt_skd_cc, is_f3_valid = eval_result

    # for easy dev/test, set to True:
    if False:
        sel = cfhExtensions.choices("Crew type:", title="TESTING", choices=["QA_FD", "QA_CC", "SK_FD", "SK_CC", "SVS_FD", "SVS_CC"])
        is_qa = sel[:2] == "QA"
        is_svs = sel[:3] == "SVS"
        is_cabin = sel[-2:] == "CC"

    if is_temp and is_cabin:
        cfhExtensions.show(
            "Not possible to buy days.\n"
            "Coll: FX not allowed for resource cabin crew",
            title="No change")
        return 1

    if is_qa and not is_cabin and not is_valid:
        # tread QA FD as SK FD before valid date
        is_qa = False

    if is_buy:
        # Get crew activities in period
        activities_in_period = {}  # Key is tuple (starttime, code), value is endtime
        current_time = activity_start_time = start_time
        while current_time < end_time:
            code = R.eval('default_context',
                           R.foreach(R.iter('iterators.chain_set'),
                                     "bought_days.%%days_may_be_bought%%(%s, %s)"
                                     % (current_time, current_time.adddays(1))))[0][0][1]

            code_duty = R.eval('default_context',
                           R.foreach(R.iter('iterators.chain_set'),
                                     "bought_days.%%duty_may_be_bought_svs%%(%s, %s)"
                                     % (current_time, current_time.adddays(1))))[0][0][1]

            code_svs = R.eval('default_context',
                           R.foreach(R.iter('iterators.chain_set'),
                                     "bought_days.%%days_may_be_bought_svs%%(%s, %s)"
                                     % (current_time, current_time.adddays(1))))[0][0][1]
            # Store activities
            key = (activity_start_time, (code or code_duty or code_svs or ""))
            if key in activities_in_period:
                activities_in_period[key] = current_time.adddays(1)  # increase period for activity
            else:
                key = (current_time, (code or code_duty or code_svs or ""))  # Create new activity period
                activities_in_period[key] = current_time.adddays(1)
                activity_start_time = current_time
            current_time = current_time.adddays(1)

        # Prepared to be able to buy a period of time, instead of single days
        comment = ""
        time_hh_sby=""
        time_mm_sby=""
        time_hh_prod=""
        time_mm_prod=""
        time_hh=""
        time_mm=""
        no_change = True
        flag = True
        day_bought = False
        day_bought_duty = False
        is_active_flightduty=False

        if code_duty == "FLT":
            is_active_flightduty = True
        else:
            is_active_flightduty = False

        if code is None:
            flag = False
        # Check if day is already bought and entry is there in table
        if is_svs:
            if "bought_days.%%leg_is_bought_svs%%" and code_svs is None:
                day_bought = True
            if "bought_days.%%leg_is_bought_svs%%" and is_active_flightduty:
                day_bought_duty = True
        
        print '##Active LEG##:',is_active_flightduty
        print '##code_duty##:',code_duty
        print '##code##:',code
        print '##code_svs##:',code_svs
        if is_svs:
            #Buy F days as Standby or Production    
            for (start, code), end in activities_in_period.items():        
                if flag or day_bought and not is_active_flightduty:
                    print 'flag:',flag
                    print 'day_bought:',day_bought
                    if comment == "":
                        try:
                            if is_svs:
                                comment, time_hh_sby,time_mm_sby,time_hh_prod,time_mm_prod,time_hh,time_mm,bought_type = BuyDayCommentForm(crew_id,is_cabin, is_qa, is_svs, is_cj, is_emj, is_valid, start_time, end_time, "Buy_Day_Form")()     
                        except CancelBuyDay:
                            return
                    # Addition duty cann't be bought on F days
                    if bought_type is "BOUGHT_DUTY":
                        cfhExtensions.show(
                            "Not possible to buy Additional duty on day-off.\n"
                            "The current assignment(s) do not permit this\n"
                            "type of operation.", title="No change")
                        return 1
                    else:
                        if bought_type is "BOUGHT_SBY" and time_hh_sby is "" and  time_mm_sby is "":
                            cfhExtensions.show(
                                "Please enter HH and MM.\n"
                                "The current assignment(s) do not permit this\n"
                                "type of operation.", title="No change")
                            return 1
                        elif bought_type is "BOUGHT_PROD" and time_hh_prod is "" and  time_mm_prod is "":
                            cfhExtensions.show(
                                "Please enter HH and MM.\n"
                                "The current assignment(s) do not permit this\n"
                                "type of operation.", title="No change")
                            return 1
                        else:
                            buy_days_svs(crew_id, start, end, code, comment, time_hh_sby, time_mm_sby, time_hh_prod, time_mm_prod, time_hh, time_mm, bought_type, has_agmt_skd_cc, is_f3_valid)
                            # Remove activity from roster
                            ActivityManipulation.deleteActivityInPeriod(crew_id, start, end, area=area)
                            no_change = False

            #Buy Addtional Duty on a day with active Flight duty
            if code_duty is None:
                flag = False
            else:
                flag = True
            for (start, code_duty), end in activities_in_period.items():
                if flag or day_bought_duty and is_active_flightduty:
                    print 'flag:',flag
                    print 'day_bought_duty:',day_bought_duty
                    if comment == "":
                        try:
                            if is_svs:
                                comment,time_hh_sby,time_mm_sby,time_hh_prod,time_mm_prod,time_hh,time_mm,bought_type = BuyDayCommentForm(crew_id,is_cabin, is_qa, is_svs, is_cj, is_emj, is_valid, start_time, end_time, "Buy_Day_Form")()
                        except CancelBuyDay:
                            return                   
                    if bought_type is "BOUGHT_SBY" or bought_type is "BOUGHT_PROD":
                        cfhExtensions.show(
                            "Not possible to buy stand by and production on a day with duty.\n"
                            "The current assignment(s) do not permit this\n"
                            "type of operation.", title="No change")
                        return 1    
                    else:
                        if bought_type is "BOUGHT_DUTY" and time_hh is "" and  time_mm is "":
                            cfhExtensions.show(
                                "Please enter HH and MM.\n"
                                "The current assignment(s) do not permit this\n"
                                "type of operation.", title="No change")
                            return 1
                        else:
                            buy_days_svs(crew_id, start, end, code, comment, time_hh_sby, time_mm_sby, time_hh_prod, time_mm_prod, time_hh, time_mm, bought_type, has_agmt_skd_cc, is_f3_valid)
                            no_change = False
        else:
            #For SK it will work as is
            for (start, code), end in activities_in_period.items():
                if code:
                    if comment == "":
                        try:
                            comment,bought_type = BuyDayCommentForm(crew_id,is_cabin, is_qa, is_svs, is_cj, is_emj, is_valid, start_time, end_time, "Buy_Day_Form")()
                        except CancelBuyDay:
                            return
                    # Do the actual "buy"
                    buy_days(crew_id, start, end, code, comment, bought_type, has_agmt_skd_cc, is_f3_valid)
                    # Remove activity from roster
                    ActivityManipulation.deleteActivityInPeriod(crew_id, start, end, area=area)
                    no_change = False

        if no_change:
            cfhExtensions.show(
                "Not possible to buy days.\n"
                "The current assignment(s) do not permit this\n"
                "type of operation.", title="No change")
            return 1
    else:
        unbuy_days(crew_id, start_time, end_time, area)
        Gui.GuiCallListener(Gui.RefreshListener)
        Gui.GuiCallListener(Gui.ActionListener)
    if is_svs:    
        Cui.CuiReloadTable('bought_days_svs', 1)
    else:    
        Cui.CuiReloadTable('bought_days', 1)
    HF.redrawAllAreas(Cui.CrewMode)
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    Cui.CuiSyncModels(Cui.gpc_info)


class BuyDayCommentForm(Cfh.Box):

    def __init__(self, crew_id, is_cabin, is_qa, is_svs, is_cj, is_emj, is_valid, start_time, end_time, *args):
        Cfh.Box.__init__(self, *args)
        self.setText('Buy Day / Overtime checkout on Fday')
        if is_svs or is_emj:
            self.svs_type_label = Cfh.Label(self, "SVS_TYPE_LABEL", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(0, 0)), "Please enter comment:")
            self.comment = Cfh.String(self, "COMMENT", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(1, 0)), 20, "")
            change = True
            #self.Bought_day_off_label = Cfh.Label(self, "Bought_day_Off", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(2, 0)), "Bought Day Off")
            for row in TM.bought_days_svs.search('(crew='+crew_id+')'):
                if row.start_time == start_time:
                    hr_sby = " "
                    min_sby = " "
                    hr_prod = " "
                    min_prod = " "
                    hr= " "
                    min = " "
                    if row.account_name == 'BOUGHT_SBY':
                        hr_sby=str(row.hours)
                        min_sby=str(row.minutes)
                        hr_sby = hr_sby.split(':')[0]
                        min_sby = min_sby.split(':')[1]
                    elif row.account_name == 'BOUGHT_PROD':
                        hr_prod = str(row.hours)
                        min_prod = str(row.minutes)
                        hr_prod = hr_prod.split(':')[0]
                        min_prod = min_prod.split(':')[1]
                    else:
                        hr= str(row.hours)
                        min = str(row.minutes)
                        hr = hr.split(':')[0]
                        min = min.split(':')[1]

                    self.time_hh_sby = Cfh.String(self, "HH_sby", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(3, 9)), 2, hr_sby)
                    self.time_mm_sby = Cfh.String(self, "MM_sby",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(3, 13)), 2, min_sby)
                                  
                    self.time_hh_prod = Cfh.String(self, "HH_prod", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(4, 9)), 2, hr_prod)
                    self.time_mm_prod = Cfh.String(self, "MM_prod",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(4, 13)), 2, min_prod)

                    self.time_hh = Cfh.String(self, "HH_duty", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(6, 9)), 2, hr)
                    self.time_mm = Cfh.String(self, "MM_duty",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(6, 13)), 2, min)

               
                    change = False 
            if change:
                self.time_hh_sby = Cfh.String(self, "HH_sby", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(3, 9)), 2, " ")
                self.time_mm_sby = Cfh.String(self, "MM_sby",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(3, 13)), 2, " ")
                self.time_hh_prod = Cfh.String(self, "HH_prod", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(4, 9)), 2, " ")
                self.time_mm_prod = Cfh.String(self, "MM_prod",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(4, 13)), 2, " ")
                self.time_hh = Cfh.String(self, "HH_duty", Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(6, 9)), 2, " ")
                self.time_mm = Cfh.String(self, "MM_duty",  Cfh.Area(Cfh.Dim(3, 1), Cfh.Loc(6, 13)), 2, " ")
        
            #self.comment_label = Cfh.Label(self, "COMMENT_LABEL", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(0, 0)), "Please enter comment:")
            #self.comment = Cfh.String(self, "COMMENT", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(1, 0)), 20, "")
            #self.time_hh = Cfh.String(self, "HH", Cfh.Area(Cfh.Dim(2, 1), Cfh.Loc(4, 6)), 2, "")
            #self.time_mm = Cfh.String(self, "MM", Cfh.Area(Cfh.Dim(2, 1), Cfh.Loc(4, 10)), 2, "")
            self.button_area = Cfh.Area(Cfh.Loc(-1, -1))
            self.ok = CfhCheckDone(self, "OK", self.button_area, "Ok", "_Ok")

            num_entries = LBL_COUNT_CC if is_cabin else LBL_COUNT_FD
            self.bought_type = Cfh.String(self, "Compensation", Cfh.Area(Cfh.Dim(20, num_entries), Cfh.Loc(2, 0)), LBL_MAX_LEN, "Bought")
            bought_type_options_str = "Select;" + ";".join(BOUGHT_LABELS_SVS[:num_entries])
            self.bought_type.setMenuString(bought_type_options_str)
            self.bought_type.setStyle(Cfh.CfhSChoiceRadioCol)

            def enforce_selection_fn():
                # self.bought_type.compute()
                if self.bought_type.getValue() not in BOUGHT_LABELS_SVS:
                    cfhExtensions.show("Please select a bought type", title="Missing selection")
                    return "Warning: No bought type selected"
                return ""

            self.ok.register_check(enforce_selection_fn)
        
        else:
            self.comment_label = Cfh.Label(self, "COMMENT_LABEL", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(0, 0)), "Please enter comment:")
            self.comment = Cfh.String(self, "COMMENT", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(1, 0)), 20, "")
            self.button_area = Cfh.Area(Cfh.Loc(-1, -1))
            self.ok = CfhCheckDone(self, "OK", self.button_area, "Ok", "_Ok")

        
            if is_qa or (is_cj and is_valid):
                description = "Bought day %s" % ("QA CC" if is_cabin else "QA FD" if is_qa else "CJ FD (QA)")
                self.qa_type_label = Cfh.Label(self, "QA_TYPE_LABEL", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(2, 0)), description)
            else:
                num_entries = LBL_COUNT_CC if is_cabin else LBL_COUNT_FD
                self.bought_type = Cfh.String(self, "Compensation", Cfh.Area(Cfh.Dim(20, num_entries), Cfh.Loc(2, 0)), LBL_MAX_LEN, "Bought")
                bought_type_options_str = "Select;" + ";".join(BOUGHT_LABELS[:num_entries])
                self.bought_type.setMenuString(bought_type_options_str)
                self.bought_type.setStyle(Cfh.CfhSChoiceRadioCol)

            def enforce_selection_fn():
                # self.bought_type.compute()
                if self.bought_type.getValue() not in BOUGHT_LABELS:
                    cfhExtensions.show("Please select a bought type", title="Missing selection")
                    return "Warning: No bought type selected"
                return ""

            self.ok.register_check(enforce_selection_fn)

        self.cancel = Cfh.Cancel(self, "CANCEL", self.button_area, "Cancel", "_Cancel")
        self.build()
        
    def __call__(self):
        """
        Returns the comment for the buy day
        """
        self.show(1)
        if self.loop() != Cfh.CfhOk:
            raise CancelBuyDay
        is_svs = hasattr(self, "svs_type_label")
        is_qa = hasattr(self, "qa_type_label")
        if is_qa:
            selected_index = 0
            return self.comment.valof(), ACCOUNTS[selected_index]
        elif is_svs:
            selected_index = BOUGHT_LABELS_SVS.index(self.bought_type.getValue())
            return self.comment.valof(), self.time_hh_sby.valof(), self.time_mm_sby.valof(),self.time_hh_prod.valof(), self.time_mm_prod.valof(),self.time_hh.valof(), self.time_mm.valof(), ACCOUNTS_SVS[selected_index - 1] 
        else:
            selected_index = BOUGHT_LABELS.index(self.bought_type.getValue())

            return self.comment.valof(), ACCOUNTS[selected_index]
        



if __name__ == "__main__":
    print "BuyDays:: The module is not for running as a standalone file."
