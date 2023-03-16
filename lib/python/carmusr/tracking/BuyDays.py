##################################################

#
# This module contains functions for handling
# bought vacation, free- or compensation days. 
#

import carmensystems.rave.api as R
import Cui
import utils.Names as Names
import RelTime
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
BOUGHT_LABELS = [
            'Bought more than 6 hrs',
            'Bought 6 hrs or less',
        
            'OT comp, C/O on Fday']
LBL_COUNT_CC = 2
LBL_COUNT_FD = 3
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

    row_day_type = get_row_day_type(leg_type)
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
            #    current_row.account_name = bought_comp_account
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


def get_row_day_type(leg_type):
        # The activity code to save:
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
    pp_end += RelTime.RelTime('00:01')  # pp_end_time is inclusive 23:59..

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
        "parameters.%%fxx_boughtday_comp_valid_at_date%%(%s)" % start_time,
        'crew.%has_agmt_group_skd_cc%',
        "system_db_parameters.%%f3_compensation_skd_cc%%(%s)" % start_time,
        )
    print "  ## eval_result:", eval_result
    is_temp, is_cabin, is_valid, has_agmt_skd_cc, is_f3_valid = eval_result

    # for easy dev/test, set to True:
    if False:
        sel = cfhExtensions.choices("Crew type:", title="TESTING", choices=["SK_FD", "SK_CC"])
        is_cabin = sel[-2:] == "CC"

    if is_temp and is_cabin:
        cfhExtensions.show(
            "Not possible to buy days.\n"
            "Coll: FX not allowed for resource cabin crew",
            title="No change")
        return 1

    if is_buy:
        # Get crew activities in period
        activities_in_period = {}  # Key is tuple (starttime, code), value is endtime
        current_time = activity_start_time = start_time
        while current_time < end_time:
            code = R.eval('default_context',
                           R.foreach(R.iter('iterators.chain_set'),
                                     "bought_days.%%days_may_be_bought%%(%s, %s)"
                                     % (current_time, current_time.adddays(1))))[0][0][1]
            # Store activities
            key = (activity_start_time, (code or ""))
            if key in activities_in_period:
                activities_in_period[key] = current_time.adddays(1)  # increase period for activity
            else:
                key = (current_time, (code or ""))  # Create new activity period
                activities_in_period[key] = current_time.adddays(1)
                activity_start_time = current_time
            current_time = current_time.adddays(1)

        # Prepared to be able to buy a period of time, instead of single days
        comment = ""
        no_change = True
        for (start, code), end in activities_in_period.items():
            if code:
                if comment == "":
                    try:
                        comment, bought_type = BuyDayCommentForm(is_cabin, is_valid, "Buy_Day_Form")()
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
    
    Cui.CuiReloadTable('bought_days', 1)
    HF.redrawAllAreas(Cui.CrewMode)
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    Cui.CuiSyncModels(Cui.gpc_info)


class BuyDayCommentForm(Cfh.Box):

    def __init__(self, is_cabin, is_valid, *args):
        Cfh.Box.__init__(self, *args)
        self.setText('Buy Day / Overtime checkout on Fday')

        self.comment_label = Cfh.Label(self, "COMMENT_LABEL", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(0, 0)), "Please enter comment:")
        self.comment = Cfh.String(self, "COMMENT", Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(1, 0)), 20, "")
        self.button_area = Cfh.Area(Cfh.Loc(-1, -1))
        self.ok = CfhCheckDone(self, "OK", self.button_area, "Ok", "_Ok")

       
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
        BOUGHT_LABELS.index(self.bought_type.getValue())
        return self.comment.valof(), ACCOUNTS[selected_index]


if __name__ == "__main__":
    print "BuyDays:: The module is not for running as a standalone file."
