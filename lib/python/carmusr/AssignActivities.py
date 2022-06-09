
# A module for assigning various activities in rostering
#
# Contains:
# An assigner function for
# 1. Compdays from bid table
# 2. Freedays from contract for fixed group crew
# 3. Post-optimization freedays for variable group crew and 5/4-Flex crew
#
#

import Cui
import Gui
import AbsDate
import AbsTime
import RelTime
import Errlog
import carmstd.rave as rave
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as R
from utils.rave import RaveIterator
import utils.cfh_date_dialog  as CDD 
import tempfile
import random

(COMPDAYS,
 PREOP_FREEDAYS,
 POSTOP_FREEDAYS,
 BLANKDAYS,
 F36FREEDAYS,
 PUBLISH_FREEDAYS,
 XMAS_FREEDAYS,
 LEGAL_FREEDAYS,
 SPECIFIC_FREEDAYS,
 SELF_TRG_DAYS,
 SHORT_GROUND_ACTIVITIES) = range(11)

ASSIGN_TYPES = [
    "compdays",
    "preop-freedays",
    "postop-freedays",
    "blankdays",
    "f36freedays",
    "publish-freedays",
    "xmas-freedays",
    "legal-freedays",
    "specific-freedays",
    "self-training-days",
    "short-ground-activities"]

CONFIRM_TITLES = [
    "Assign compdays",
    "Assign pre-op freedays",
    "Assign post-op freedays",
    "Assign blank days",
    "Assign F36-freedays",
    "Assign publish freedays",
    "Assign xmas freedays",
    "Assign legal freedays",
    "Assign Freedays",
    "Assign web training",
    "Assign short ground activities"]

CONFIRM_MESSAGES = [
    "Assign bidded compensation days in window?",
    "Assign pre-optimization freedays in window?",
    "Assign post-optimization freedays in window?",
    "Assign blankdays in window?",
    "Assign F36-freedays in window?",
    "Assign maximum nr of freedays?",
    "Assign xmas freedays?",
    "Assign legal freedays?",
    "Assign maximum nr of freedays?",
    "Assign needed web training?",
    "Assign needed short ground activities?"]

ONE_MIN = RelTime.RelTime('00:01')
ONE_DAY = RelTime.RelTime(1 * 24, 0)
TWO_DAYS = RelTime.RelTime(2 * 24, 0)
THREE_DAYS = RelTime.RelTime(3 * 24, 0)
FOUR_DAYS = RelTime.RelTime(4 * 24, 0)
FIVE_DAYS = RelTime.RelTime(5 * 24, 0)
SIX_DAYS = RelTime.RelTime(6 * 24, 0)

# flag controlling how to handle single day gaps in wops 
PRIO_NOT_SINGLE_F = 's'		#prioritize blank days instead of single free days
PRIO_SINGLE_F = 'S' 		#priroritize single freedays over blank days

# prioritized days when assigning blank days
BL_PT_SINGLE = 0 # single days to be set first; single freedays not allowed or not preferred
BL_PT_BEFORE = 1 # Day before production wop; try assign sequence of blank days before wop
BL_PT_AFTER = 2  # Day after production wop; try assingn sequence of blank days after wop

# State of days
BL_ST_MISSING = 0         # Information missing about the day, equivavelent to not existing in dic
BL_ST_UNAVAIL = 1         # Day not available for assigning
BL_ST_HOLE = 3            # Day is a single day hole in wop. Changed in step 2.
BL_ST_ALW_HOLE = 4        # Day is a single day hole in wop, allowed as freeday. Changed in step 2.
BL_ST_ASSIGNED = 5        # Day was assigned
BL_ST_FDC15_UNKNOWN = 10  # Day possibly unassigned, in contract period where FDC15 is valid.
BL_ST_FDC15_LAST = 12     # Day should be tried after all other, in contract period where FDC15 is valid.
BL_ST_FDC15_FORCED = 13   # Single hole, not allowed as freeday, under FDC15 contract.
BL_ST_OTH_UNKNOWN = 20    # Day possibly unassigned, outside FDC15 control (=as many blankdays as possible assigned)
BL_ST_OTH_LAST = 22       # Day should be tried after all otgher, outside FDC15 control
        
def get_day(dic, d):
    if d in dic:
        return dic[d]
    return BL_ST_MISSING
    
def is_day(dic, d, stat):
    return get_day(dic, d) == stat
    
def set_day_range(dic, df, dt, stat):
    d = df
    while (d<dt):
        dic[d] =  stat
        d += ONE_DAY


def is_prio(attr, flag):
    return flag in attr

################################################################################
class AssignerObject:
    def __init__(self, area= -1, verbose=False, interactive_mode=True):

        if area == -1:
            raise Exception("Undefined area")
        self.errorLogPath = tempfile.mktemp()
        self.errorLog = open(self.errorLogPath, "w")
        # currentArea is saved to avoid faulty behaviour when user moves mouse
        self.currentArea = area
        self.verbose = verbose
        self.interactive_mode = interactive_mode
        self.errors = 0
        (self.pp_start, self.pp_end, self.publ_end,
         self.pp_days, self.publ_days) = R.eval(
            'fundamental.%pp_start%',
            'fundamental.%pp_end%',
            'fundamental.%publ_period_end%',
            'pp.%days%',
            'pp.%days_in_published%')
        
        # Ready for call to assign method

    def setCrewObject(self, crewid, empno, crewstation, setContext=True):
            
        self.crewid = crewid # important to do this before call to updateContext!
        
        if setContext:
            # Sets the current crew/roster as default context so a parametrized
            # call to rave isn't necessary.
            self.updateContext()

        # First lets check for dates where postop freedays can be assigned:
        (self.vg_start,
         self.vg_end) = self.crewEval("freedays.%vg_start%",
                                      "freedays.%vg_end%")

        (self.emp_start, self.emp_end) = self.crewEval("crew.%emp_start%",
                                                       "crew.%emp_end%")
            
        self.empno = empno
        # Activities should be assigned at ARN, not STO
        if crewstation == "STO":
            self.crewstation = "ARN"
        else:
            self.crewstation = crewstation

    def setCrewObjectLight(self, crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end, setContext=True):
            
        self.crewid = crewid # important to do this before call to updateContext!
        
        if setContext:
            # Sets the current crew/roster as default context so a parametrized
            # call to rave isn't necessary.
            self.updateContext()

            
        self.empno = empno
        self.crewstation = crewstation
        self.vg_start = vg_start
        self.vg_end = vg_end
        
        self.emp_start = emp_start
        self.emp_end = emp_end
            
    def updateContext(self):
        # Sets the current crew/roster as default context so a parametrized
        # call to rave isn't necessary.
        Cui.CuiSetSelectionObject(
            Cui.gpc_info,
            self.currentArea,
            Cui.CrewMode,
            self.crewid)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
                                    self.currentArea,
                                    "OBJECT")
        self.objectContext = R.selected(R.Level.chain())
        
    def crewEval(self, *evalString):
        # This function just reduces the amount of typing needed at other places
        return R.eval(self.objectContext, *evalString)

    def crewCheckDate(self, date):
        checkVals = self.crewEval('roster.%%trip_code_at_date%%(%s)' % date,
                                  'roster.%%on_duty_at_date%%(%s)' % date)
        return checkVals
    
    def error(self, activity, date, message, enddate=None):
        # When encounting an error we want it in the Errlog, but also displayed
        # in an error log when the assignment has finished.
        strDate = str(AbsDate.AbsDate(date))
        if enddate:
            try:
                end_date_str = str(AbsDate.AbsDate(enddate))
                strDate = "(" + strDate + ", " + end_date_str + ")"
            except:
                pass # in case enddate wrong format or somefing
        errMess = self.empno + ", " + str(activity) + ", " + strDate + ", " + message
        Errlog.log("AssignActivities::assignInWindow:" + errMess)
        self.errorLog.write(errMess + "\n")
        self.errors += 1

    def tryAssign(self, date, activity, reportErrors=True,
                  legalAssignment=False, duration=ONE_DAY, okToFG=False):
        (tripcode, ondutyAtDate) = (activity, False)
        # We try to assign first and handles errors if they happen.
        # The safer way would be to check the roster first, but for
        # some cases (e.g. fixed freeday pre-op) this will be redundant
        # and only waste a lot of time.
        defFlags = Cui.CUI_CREATE_PACT_DONT_CONFIRM | \
                   Cui.CUI_CREATE_PACT_SILENT | \
                   Cui.CUI_CREATE_PACT_TASKTAB
        if legalAssignment:
            flags = defFlags
        else:
            flags = defFlags | Cui.CUI_CREATE_PACT_NO_LEGALITY
        # No assignments outside employment
        if (date < self.emp_start or date + duration > self.emp_end):
            return ("", False, False)
        # Most assignments should only be made to VG crew
        if (okToFG or (date >= self.vg_start and date + duration <= self.vg_end)):
            pass
        else:
            # If not okToFG we should return True to supress warnings.
            return ("", False, not okToFG)
        try:
            if not activity:
                if self.verbose:
                    message = "No code found for %s on %d" % (self.crewid, AbsDate.AbsDate(date))
                    Errlog.log("AssignActivities:: " + message)
                raise
            Cui.CuiCreatePact(
                Cui.gpc_info,
                self.crewid,
                activity,
                "",
                date,
                date + duration,
                self.crewstation,
                flags)
            assigned = True
            if self.verbose:
                 print "succeed assign ",self.crewid,date
        except:
            assigned = False
            # CuiCreatePact failed, lets find out the reason
            # Check if the assignment is already on roster.
            (tripcode, ondutyAtDate) = self.crewCheckDate(date)
            if self.verbose:
                print "except assign,  tripcode",self.crewid,date,tripcode, ondutyAtDate
            enddate = (date + duration - ONE_MIN)
            if (tripcode == "open" and reportErrors):

                message = self.get_overlap_message(date, duration, activity)
                if message:
                    self.error(activity, date,
                               message,
                               enddate=enddate)
                    return (tripcode, ondutyAtDate, False)
                if legalAssignment:
                    # This means we have an unknown reason, probably legality
                    # failure.
                    self.error(activity, date,
                               "fail: Broken legality")
                else:
                    self.error(activity, date,
                               "fail: Unknown reason")
            elif ondutyAtDate and reportErrors:
                # This means we had an overlap.
                # Errors wont automatically be reported.
                self.error(activity, date,
                           "fail: overlapping activity (" + tripcode + ",%s)" % date.ddmonyyyy(True),
                           enddate=enddate)
            else:
                # We had an overlap with off-duty, which we ignore,
                # or we didn't care about errors.
                pass
        return (tripcode, ondutyAtDate, assigned)

    def get_overlap_message(self, startdate, duration, activity):
        #Check lengthy PACT for overlaps
        loop_date = startdate + ONE_DAY
        while loop_date < (startdate + duration):
            (tripcode, ondutyAtDate) = self.crewCheckDate(loop_date)
            if tripcode != 'open':
                return   "fail: overlapping activity " + \
                       "(" + tripcode + ",%s)" % loop_date.ddmonyyyy(True)
            loop_date += ONE_DAY
        return ""
    
    def getRaveExpr(self):
        raise NotImplementedError
    def getWhereExpr(self):
        raise NotImplementedError
    
    def getCrew(self):
        # The crew tuple is dependent on assignment type.
        # Some values are the same for all types.
        windowContext = rave.Context("window", self.currentArea)

        # General crew values, always needed
        crewValues = ["crew.%id%",
                      "crew.%employee_number%",
                      "crew.%homestation%"]
        whereExpr = self.getWhereExpr()
        raveExpr = self.getRaveExpr()
        crewValues.extend(raveExpr)
        
        if self.verbose:
            print 'whereExpr', whereExpr
            print 'crewExpr', crewValues
        crew, = windowContext.eval(
            R.foreach(R.iter("iterators.roster_set", where=whereExpr),
                      *crewValues))
        return crew
   
    def getXmasCrew(self):
        # The crew tuple is dependent on assignment type.
        # Some values are the same for all types.
        windowContext = rave.Context("window", self.currentArea)
        
        pp_start = "fundamental.%pp_start%"
        crew_id = "crew.%id%"
        employee_number = "crew.%employee_number%"
        homestation = "crew.%homestation%"
        crew_region = "crew.%region%"
        main_cat = "fundamental.%main_cat%"
        
        season_start_date = "report_common.%x_xmas_season_start_date%(" + main_cat + "," + pp_start + ")"
        season_end_date = "report_common.%x_xmas_season_end_date%(" + main_cat + "," + pp_start + ")"
        
        # General crew values, always needed
        crewValues = [crew_id,
                      employee_number,
                      homestation,
                      crew_region,
                      main_cat,
                      season_start_date,
                      season_end_date]
        
        whereExpr = self.getWhereExpr()
        raveExpr = self.getRaveExpr()
        crewValues.extend(raveExpr)
        
        if self.verbose:
            print 'whereExpr', whereExpr
            print 'crewExpr', crewValues
        crew, = windowContext.eval(
            R.foreach(R.iter("iterators.roster_set", where=whereExpr),
                      *crewValues))
        return crew

    def assign_impl(self):
        raise NotImplementedError
    
    def assign(self):
        self.errorLog.write(
            "Error list in assigning of %s\n\n" % self.assign_type)
        # The main function for assigning activities.
        
        self.assign_impl()
            
        # The assignment process has finished and if there are errors we show
            # them.

        
        self.errorLog.close()
        if self.interactive_mode:
            if self.errors > 0:
                cfhExtensions.showFile(self.errorLogPath, "Error messages")
            else:
                if self.verbose:
                    cfhExtensions.show("No errors!")
        if self.verbose:
            Errlog.log(
                "AssignActivities::assignInWindow: Finished with "
                + str(self.errors) + " errors")

    def _possible_to_assign_freeday_on_date(self, date, check_two_day_gap=False):
        """
        Check that date is free and that there is an offduty before or after
        """
        
        (code_before_date,
         onduty_before_date) = self.crewCheckDate(date - ONE_DAY)
        (code_on_date,
         onduty_on_date) = self.crewCheckDate(date)
        (code_after_date,
         onduty_after_date) = self.crewCheckDate(date + ONE_DAY)
        if check_two_day_gap:
            return code_on_date == 'open' and code_after_date == 'open'
        else:
            return  code_on_date == 'open' and \
                   ((code_before_date != 'open' and not onduty_before_date) or \
                    (code_after_date != 'open' and not onduty_after_date))
    
    def get_empty_periods_in_roster(self, start_time, end_time):
        """ Return a dictionary with empty holes >= 1 day in period """ 
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, self.crewid)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'OBJECT')
        # Best guess, will work for all scandinavian crew
        start_hb_expr = 'default(trip.%start_hb%, station_localtime("CPH",trip.%start_utc%))'
        end_hb_expr = 'default(trip.%end_hb%, station_localtime("CPH",trip.%end_utc%))'
        trips = RaveIterator(R.iter('iterators.trip_set',
                                    where='%s<=%s and %s>=%s' % \
                                    (start_hb_expr, end_time,
                                     end_hb_expr, start_time),
                                    sort_by=start_hb_expr), {
            "start_hb":start_hb_expr,
            "end_hb":end_hb_expr
            }).eval("default_context")
        
        start_time = start_time.day_floor()
        end_time = end_time.day_ceil()
        possible_days = [True] * int((end_time - start_time) / ONE_DAY)
        if self.verbose:
            print "=== get empty periods in roster ===",start_time, end_time 
        for trip in trips:
            
            trip_start = max(trip.start_hb.day_floor(), start_time)
            trip_end = min(trip.end_hb.day_ceil(), end_time)

            start_index = int((trip_start - start_time) / ONE_DAY)
            end_index = int((trip_end - start_time) / ONE_DAY)
            
            possible_days[start_index:end_index] = [False] * (end_index - start_index)
            if self.verbose:
                print "impossible days:", trip_start, trip_end
        possible_periods = {}
        current_time = None
        for ix in range(0, len(possible_days)):
            time = start_time + ONE_DAY * ix

            if not current_time and possible_days[ix]:
                possible_periods[time] = time
                current_time = time
            elif current_time and not possible_days[ix]:
                possible_periods[current_time] = time
                current_time = None
            if ix == len(possible_days) - 1 and possible_days[ix] and current_time:
                possible_periods[current_time] = end_time
        return possible_periods

class CompdaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[COMPDAYS]
            self.assign_type = ASSIGN_TYPES[COMPDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        crew = self.getCrew()
        for ix, crewid, empno, crewstation, bids in crew:
            #if hasBidsToGrant:
            self.setCrewObject(crewid, empno, crewstation)
            #    bids, = self.crewEval(bidExpr)
            self.assignCompdays(bids)
            
    def assignCompdays(self, bids):
        # The bids tuple contains all the bids for the crew, not only compday
        # bids.
        
        for (ix, bidNo, toAssign, activity,
             startdate, enddate, days, fitsBalance, partly_granted) in bids:
            if toAssign:
                # toAssign checks to see if the bid is for a compday.
                if fitsBalance:
                    # fitsbalance isn't updated with every assignment, but
                    # can be used as an initial exclusion criteria.
                    # Need to update context to get correct evaluation of balance
                    self.updateContext()
                    updatedFitsBalance, = self.crewEval(
                        'compdays.%%bid_fits_balance%%(%s)' % bidNo)
                    
                    if not updatedFitsBalance:
                        # The bid (all days) must fit inside the current account
                        # balance.
                        self.error(activity, startdate, "fail: low saldo")
                    elif partly_granted:
                        for day_ix in xrange(days):
                            date = startdate + ONE_DAY * day_ix
                            (code, on_duty) = self.crewCheckDate(date)
                            if code == 'open':
                                (t1, t2, assigned) = self.tryAssign(date, activity,
                                                                  legalAssignment=True,
                                                                  duration=ONE_DAY, okToFG=True)
                    else:
                        
                        (t1, t2, assigned) = self.tryAssign(startdate, activity,
                                                          legalAssignment=True,
                                                          duration=ONE_DAY * days, okToFG=True)
                else:
                    self.error(activity, startdate, "fail: low saldo")

    def get_overlap_message(self, startdate, duration, activity):
        message = AssignerObject.get_overlap_message(self, startdate, duration, activity)
        if message and activity in message:
            # Don't warn on compdays assign e.g. F3 overlapping F3
            return ""
        else:
            return message

    def getRaveExpr(self):
        bidExpr = R.foreach(
            R.times("bid.%crew_num_bids%"),
            'fundamental.%py_index%',
            'compdays.%bid_should_be_assigned_ix%',
            'compdays.%compdaytype_ix%',
            'compdays.%start_time_ix%',
            'compdays.%end_time_ix%',
            'compdays.%bid_nr_days_ix%',
            'compdays.%bid_fits_balance_ix%',
            'compdays.%part_of_bid_granted_ix%')       
        return [bidExpr]
    
    def getWhereExpr(self):
        whereExpr = "compdays.%crew_has_unfulfilled_bid_in_pp%"
        return whereExpr
            
class PreOpFreeDaysAssigner(AssignerObject):
        def __init__(self, area= -1, verbose=False, interactive_mode=True):
            # Sets various assignment type independent variables
            try:
                self.assign_message = CONFIRM_TITLES[PREOP_FREEDAYS]
                self.assign_type = ASSIGN_TYPES[PREOP_FREEDAYS]
            except IndexError:
                self.assign_message = ""
                self.assign_type = ""
                pass
            AssignerObject.__init__(self,
                                    area=area,
                                    verbose=verbose,
                                    interactive_mode=interactive_mode)
        def assign_impl(self):
            # We collect the pattern activities in one sweep, but
            # only for crew with some fixed group in pp.
            _p_start = R.param('fundamental.%start_para%').value()
            _p_end = R.param('fundamental.%end_para%').value()
            _plan_start, = R.eval('fundamental.%plan_start%')
            _plan_end, = R.eval('fundamental.%plan_end%')
            try:
                _form = CDD.PeriodSelectionForm(dateForm=True)
                _form.assign_default_values(_p_start, _p_end)
                _form()
                (_start, _end) = _form.get_period()
            except CDD.CancelFormError:
                if self.verbose:
                    Errlog.log("AssignActivities:: Cancel in periodform when assigning pre-op freedays")
                return
            if AbsTime.AbsTime(_start) < _plan_start or AbsTime.AbsTime(_end) > _plan_end:
                Errlog.log("AssignActivities:: Chosen period outside loaded interval")
                cfhExtensions.show("Error: Chosen period outside loaded interval")
                return
            if self.verbose:
                Errlog.log("AssignActivities:: Assigning pre-op freedays with period %s to %s" % \
                           (str(_start), str(_end)))
            _pp_modifier = PPModifier(AbsTime.AbsTime(_start), AbsTime.AbsTime(_end) + ONE_DAY)

            patternExpr = R.foreach(
                R.times("pp.%days%"),
                "fundamental.%date_index%",
                "crew.%pattern_activity_at_date_ix%")

            crew = self.getCrew()
            for (ix, crewid, empno, crewstation,
                 assignFixed, groupChangeDate) in crew:
                if assignFixed or groupChangeDate > self.pp_start:
                    self.setCrewObject(crewid, empno, crewstation)
                    # We only do work if the crew has at least some FG in PP.
                    if assignFixed:
                        pattern, = self.crewEval(patternExpr)
                    else:
                        pattern = None
                    self.assignFixedFreedays(pattern, groupChangeDate)
        def assignFixedFreedays(self, pattern, groupChangeDate):
            # We should assign two freedays before changing from VG to FG, but we
            # assume that this is only needed in this planning period (i.e. if we
            # changed group at pp-start we would have assigned the "carry-ins" in
            # the previous planning process.
            if groupChangeDate > self.pp_start:
                # This means that there is a group change, from VG to FG and two
                # freedays should be assigned to enable a legal transition to fixed
                # pattern.
                # ASK ABOUT THIS
                (tmp1, tmp2, assigned) = self.tryAssign(groupChangeDate - TWO_DAYS,
                                                      "F", duration=TWO_DAYS, okToFG=True)
                if not assigned:
                    self.tryAssign(groupChangeDate - ONE_DAY, "F", okToFG=True)
                    self.tryAssign(groupChangeDate - TWO_DAYS, "F", okToFG=True)
            #self.tryAssign(groupChangeDate - ONE_DAY, "F")

            if not pattern is None:
                # It's possible that the pattern will be None, for crew that are
                # VG in all of the publ-pp. This functions will still be called if
                # they change to FG two days into the next publ-pp.
                # activity evaluates to false when crew is in variable
                # group. "P" is standard production days and "FP" is
                # flex days for 5/4-flex crew.
                possible_periods = self.get_periods_from_pattern(pattern,
                                                                 filter_expr=lambda x:x[2] \
                                                                 is not None and \
                                                                 x[2] not in ("P", "FP"))
                for (start_t, (end_t, activity)) in possible_periods.items():
                    duration = end_t - start_t
                    (tmp1, tmp2, assigned) = self.tryAssign(start_t, activity,
                                                          duration=duration,
                                                          reportErrors=False, okToFG=True)
                    if not assigned:
                        for ix in range(0, int((end_t - start_t) / ONE_DAY)):
                            self.tryAssign(start_t + ONE_DAY * ix, activity, okToFG=True)
        
        def get_periods_from_pattern(self, pattern, filter_expr=None):
            """
            Return dictionary start_time:[end_time, code],...
            """

            # activity evaluates to false when crew is in variable
            # group. "P" is standard production days and "FP" is
            # flex days for 5/4-flex crew.
            if filter_expr:
                pattern = filter(filter_expr, pattern)
            if len(pattern) == 0:
                return {}
            possible_days = {}
            for (ix, date, activity) in pattern:
                possible_days[date] = activity

            possible_periods = {}
            dates = possible_days.keys()
            dates.sort()
            date = dates[0]

            while date <= dates[-1]:
                next_start = date + ONE_DAY
                while possible_days[date] == possible_days.get(next_start) and \
                          next_start <= dates[-1]:
                    next_start += ONE_DAY
                possible_periods[date] = [next_start, possible_days[date]]
                date = next_start
                while not possible_days.has_key(date) and date <= dates[-1]:
                    date += ONE_DAY

            return possible_periods
        def getWhereExpr(self):
            whereExpr = "True"
            return whereExpr
        def getRaveExpr(self):
            crewValues = ["freedays.%assign_fixed_freedays%"]
            # group_change_date is used for carry-in freedays when
            # changing from vg to fg. The date will be 1jan1986 if
            # no change exists in pp.
            crewValues.append("freedays.%group_change_date%")
            return crewValues
        
class PostOpFreeDaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[POSTOP_FREEDAYS]
            self.assign_type = ASSIGN_TYPES[POSTOP_FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose= verbose,
                                interactive_mode=interactive_mode)
        _pp_modifier = PPModifier(AbsTime.AbsTime(self.pp_start), AbsTime.AbsTime(self.publ_end) + ONE_DAY)
        
    def assign_impl(self):
        crew = self.getCrew()
        # The wops are needed since we're going to assign F4 on all
        # valid free weekends, and also for carry-out freedays.
        wopExpr = R.foreach(
            "iterators.wop_set",
            "freedays.%wop_should_have_va_freedays_before%",
            "wop.%in_long_course_period%",
            "wop.%start_day%",
            "wop.%end_day%",
            )
        # The parttime expression is to get days that are valid for
        # assigning parttime freedays and parttime ill.
        # It is only evaluated for one month since the requirement
        # is in month.
        ptExpr = R.foreach(
            R.times('pp.%days_in_published%'),
            'fundamental.%date_index%',
            'freedays.%possible_pt_freeday_at_date_ix%',
            'freedays.trip_code_at_date_ix',
            )

        flexExpr = R.foreach(
            R.times("pp.%days% + 12"),
            "fundamental.%pp_start% + (fundamental.%py_index%-10)*24:00",
            "crew.%pattern_activity_at_date%(fundamental.%pp_start% + " + \
            "(fundamental.%py_index%-10)*24:00)")
        weekendExpr = R.foreach(
            R.times("freedays.%weekends_in_pp%"),
            "freedays.%saturday_ix%",
            "freedays.%f4_ok_on_weekend_ix%",
            "freedays.%f4_carry_out_needed%"
            )

        for (ix, crewid, empno, crewstation,
             VGinPP, parttimeInPP, FlexInPP) in crew:
            if self.verbose:
                print "handling crew ",crewid
            self.setCrewObject(crewid, empno, crewstation)
            # We assume that crew that have some fixed-group in pp already
            # have had their fixed freedays assigned.
            # Therefore we don't check group day-by-day.
            if FlexInPP:
                flexPattern, = self.crewEval(flexExpr)
                self.assignPostopFlexFreedays(flexPattern)
            if VGinPP:
                # We need to assign required freedays after wop before pt freedays
                # to get calculations for CC correct
                wops, = self.crewEval(wopExpr)
                weekends, = self.crewEval(weekendExpr)
                if self.verbose:
                    print weekends
                self.assignF4Freedays(weekends)
                if not parttimeInPP:
                    self.assign_legal_freedays(False)
                
            if parttimeInPP:
                (ptCode, reqPtDays, reqIlDays) = self.crewEval(
                    "default(freedays.%first_parttime_code_in_pp%, " + \
                    "freedays.%default_parttime_code%)",
                    "freedays.%parttime_freedays_left_to_assign%",
                    "freedays.%IL8_left_to_assign%")
                ilCode = "Il8"
                if reqPtDays > 0 or reqIlDays > 0:
                    parttimeOkAtDates, = self.crewEval(ptExpr)
                    if VGinPP:
                        partTimeIx = [e for e, dat in enumerate(parttimeOkAtDates) if (str(dat[3]) == str("open") and str(dat[2]) == str(ptCode) )]
                        openNotPartTimeIx = [e for e, dat in enumerate(parttimeOkAtDates) if (str(dat[3]) == str("open") and str(dat[2]) != str(ptCode) ) ]
                        pt_dff = reqPtDays - len(partTimeIx)
                        pt_pos2add = min(pt_dff, len(openNotPartTimeIx))
                        if len(partTimeIx) < reqPtDays and len(openNotPartTimeIx) > 0:
                            for i in range(0,pt_pos2add):
                                (a,b,c,d) = parttimeOkAtDates[openNotPartTimeIx[i]]
                                parttimeOkAtDates[openNotPartTimeIx[i]] = (a,b,str(ptCode),d)
                    self.assignParttimeFreedays(parttimeOkAtDates, ptCode,
                                                reqPtDays, ilCode, reqIlDays)
                self.assign_legal_freedays(False)
            if VGinPP:
                # End with assigning legal freedays, WP CCR 719
                self.assignVaLC(wops)
                self.assign_legal_freedays(True)

    def assignVaLC(self, wops):
        if self.verbose:
            print "Assign postop VA LC"

        for (ix, VAFreedays, LCFreedays, startDay, endDay) in wops:
            if VAFreedays:
                # This is for assigning two freedays before vacation.
                # Supporting rules_indust_ccr.ind_min_freedays_in_cnx_with_VA_ALL.
                self.tryAssign(startDay - ONE_DAY, "F")
                self.tryAssign(startDay - TWO_DAYS, "F")
            if LCFreedays:
                # This is for assigning two freedays before long course periods.
                # Supporting rules_soft_ccr.sft_min_freedays_before_long_course_ALL.
                self.tryAssign(startDay - ONE_DAY, "F")
                self.tryAssign(startDay - TWO_DAYS, "F")

    def assignF4Freedays(self, weekends):
        if self.verbose:
            print "assign f4",self.crewid
        for (ix, saturday, f4_ok, carry_out_needed) in weekends:
            # Only assign free weekend if the entire weekend is in the publication period.
	    # Crew with monthly freedays can have their F4 assigned outside published period
            if f4_ok and (saturday + TWO_DAYS < self.publ_end or carry_out_needed):
                (tmp1, tmp2, assigned) = self.tryAssign(saturday, "F4", duration=TWO_DAYS, reportErrors=False)
                if not assigned:
                    self.tryAssign(saturday, "F4", duration=ONE_DAY, reportErrors=False)
                    self.tryAssign(saturday + ONE_DAY, "F4", duration=ONE_DAY, reportErrors=False)

    def assignParttimeFreedays(self, parttimeOkAtDates, ptCode, reqPtDaysInit,
                               ilCode, reqIl8DaysInit):
        if self.verbose:
            print "assign pt"
        # SKN contracts doesn't have parttime code ATM.
        if ptCode is None:
            self.error("", "", "has no valid parttime code in contract")
            return
        reqPtDays = reqPtDaysInit
        reqIl8Days = reqIl8DaysInit
        for (ix, date, assignThisDate, notUsedHere) in parttimeOkAtDates:
            if reqPtDays > 0:
                if assignThisDate:
                    code = assignThisDate
                else:
                    code = ptCode
            elif reqIl8Days > 0:
                code = ilCode
            else:
                break
            if assignThisDate:
                (tripCode, onDuty, assigned) = self.tryAssign(date, code,
                                                             reportErrors=True)
                if assigned:
                    if (tripCode == ptCode) or (tripCode == assignThisDate):
                        reqPtDays -= 1
                    elif tripCode == ilCode:
                        reqIl8Days -= 1
                else:
                    # We couldn't assign this date
                    pass
        # The loop has finished
        if (reqPtDays > 0):
            openNotPartTimeIx = [iop for iop, dat in enumerate(parttimeOkAtDates) if (str(dat[3]) == str("open") and str(dat[2]) != str(ptCode) ) ] # TODO
            ptVars = (reqPtDaysInit - reqPtDays, reqPtDaysInit, len(openNotPartTimeIx))
            self.error(ptCode, self.pp_start,
                       "fail: %s of %s (%r) required parttime freedays assigned"
                       % ptVars)
        if (reqIl8Days > 0):
            ilVars = (reqIl8DaysInit - reqIl8Days, reqIl8DaysInit)
            self.error(ilCode, self.pp_start,
                       "fail: %s of %s required special schedule ill assigned"
                       % ilVars)

    def assignPostopFlexFreedays(self, pattern):
        # This is for crew in 5/4 flex group (SKBU) that should have their
        # flex-days covered by freedays.
        # Pattern:
        # F,F,X,X,P,P,P,X,X,F,F,X,X
        # .,.,0,1,2,3,4,5,6,7,8,9
        if len(pattern) == 0:
            # how did we get here?
            return
        # Create mock roster to count prod in!
        # F = Assigned off duty
        # X = Flex day, open for grabs
        # OP = Unassigned production day in pattern
        # P = Assigned production day in pattern
        if self.verbose:
            print "assign flex"

        roster = {}
        for ix, date, activity in pattern:
            # Get activity on date from actual roster
            (code, on_duty) = self.crewCheckDate(date)
            if code == 'open' and activity == 'FP':
                roster[date] = 'X'
            elif on_duty:
                roster[date] = 'P'
            elif (code == 'open' and activity == 'P'):
                roster[date] = 'OP'
            else:
                roster[date] = 'F'
        # Sort roster
        keys = roster.keys()
        keys.sort()

        # Get gap between offduty, in this gap we need xtra freedays and
        # five prod/empty days
        # Idea is to find a switch between F and !F, the loop forward until next F
        # Count number of P(roduction) dates inbetween
        current_date = keys[0]
        last_date = max(keys[-1], self.pp_end) # Only use current pp
        gap_periods = []
        while current_date <= last_date:
            if current_date < last_date and \
                   roster[current_date] == 'F' and \
                   roster[current_date + ONE_DAY] != 'F':
                # we found a pattern-gap-period
                forward_iter = current_date + ONE_DAY
                number_of_prods_in_gap = 0
                # Count number of days until next offduty
                while roster[forward_iter] != 'F' and \
                          forward_iter < last_date:
                    if roster[forward_iter] == 'P':
                        number_of_prods_in_gap += 1
                    forward_iter += ONE_DAY
                gap = (current_date + ONE_DAY, forward_iter, number_of_prods_in_gap)
                gap_periods.append(gap)
                current_date = forward_iter
            current_date += ONE_DAY
        # Loop over periods and assign F where needed
        for (start_t, end_t, nr_of_prods) in gap_periods:
            gap_length = int((end_t - start_t) / ONE_DAY)
            if nr_of_prods >= 5:
                # Assign as much as possible in period, all prod already filled!
                while start_t < end_t:
                    if roster[start_t] == 'X' and start_t < self.pp_end:
                        (tmp1, tmp2, assigned) = self.tryAssign(start_t, "F",
                                                              reportErrors=False, okToFG=True)
                    start_t += ONE_DAY
            elif gap_length > 5:
                # Possible dates, alternate between backward and
                # forwards to "grow" F-days in from edges
                possible_dates = []
                for i in xrange(int(round(gap_length / 2.0))):
                    possible_dates.append(start_t + ONE_DAY * i)
                    possible_dates.append(end_t - ONE_DAY * (i + 1))
                #   xtra +1 in backwards since
                #   end_t is non-inclusive

                # Alternate between forwards and
                # backwards to "grow" F-days in from edges
                nr_days = len(possible_dates)
                F_to_assign = gap_length - 5 # Five is the magic number

                for date_ix in xrange(nr_days):
                    date = possible_dates[date_ix]
                    assigned = False
                    if date and F_to_assign > 0:
                        if roster[date] == 'X' and date < self.pp_end:
                            (tmp1, tmp2,
                             assigned) = self.tryAssign(date, "F",
                                                        reportErrors=False, okToFG=True)
                    if assigned:
                        F_to_assign -= 1
                    else:
                        # Ok, this direction is dead,
                        # remove every other object
                        remove_indicies = (range(1, nr_days, 2),
                                           range(0, nr_days, 2))\
                                           [date_ix % 2 == 0]
                        for remove_ix in remove_indicies:
                            possible_dates[remove_ix] = None

                    if F_to_assign == 0:
                        break

    def assign_legal_freedays(self, fill_gaps=False):

        if self.verbose:
            print "assign legal f"

        date = self.pp_start
        end_date = date + ONE_DAY * self.publ_days

        crewStatus = RaveIterator(R.iter('iterators.roster_set',
                                         where=None), { 
            "assigned":"freedays.%nr_freedays_in_publ_period%",
            "need":"freedays.%req_freedays_in_month_incl_prev_month%"
            }).eval("default_context")

        needed_days = crewStatus[0].need
        assigned_days = crewStatus[0].assigned
        if self.verbose:
            print "need/assigned", needed_days, assigned_days, fill_gaps

        if needed_days <= assigned_days and fill_gaps:
            return

        if not fill_gaps:
            wops = RaveIterator(R.iter('iterators.wop_set',
                                       where='overlap(wop.%start_hb%, wop.%end_hb%,' + \
                                       '%s,%s)>00:00' % (date, end_date),
                                       sort_by="wop.%start_hb%"), {
                "on_duty":"freedays.%_wop_is_on_duty%",
                "end_hb":"freedays.%_wop_end_on_duty_hb%",
                "need_after_wop":"freedays.%min_required_freedays_after_wop_soft%",
                "freedays_overlaps_we":"freedays.%required_freedays_after_wop_contains_possible_f4_saturday%",
                "possible_freedays":"freedays.%number_of_days_until_next_on_duty_wop%"
                }).eval("default_context")

            for wop in wops:
                if not wop.on_duty:
                    continue
                duration = ONE_DAY * wop.need_after_wop
                days_start = wop.end_hb.day_ceil()
                days_end = days_start + duration

                (tmp1, tmp2, assigned) = self.tryAssign(days_start, "F",
                                                      reportErrors=False,
                                                      legalAssignment=False,
                                                      duration=duration)
                if assigned:
                    assigned_days += wop.need_after_wop
                else:
                    for ix in range(0, wop.possible_freedays):
                        this_day = days_start + ONE_DAY * ix
                        if duration < ONE_DAY:
                            break
                        (tmp1, tmp2, assigned) = self.tryAssign(this_day, "F",
                                                              reportErrors=False)
                        if assigned or (tmp1 and tmp1[0] == "F") :
                            duration -= ONE_DAY
            return
                            
        remaining_days = needed_days - assigned_days
        possible_periods = self.get_empty_periods_in_roster(date, end_date)
        periods_to_use = []
        for start_t, end_t in possible_periods.items():

            length = int((end_t - start_t) / ONE_DAY)
            if length > 1 and length <= remaining_days:
                periods_to_use.append((start_t, end_t))
                remaining_days -= length
            if remaining_days <= 0:
                break
        for (start_t, end_t) in periods_to_use:
            duration = (end_t - start_t)
            self.tryAssign(start_t, "F",
                           duration=duration,
                           reportErrors=False)
        if remaining_days > 0:
            for ix in range(0, self.publ_days):
                loop_date = date + ONE_DAY * ix
                self._possible_to_assign_freeday_on_date(loop_date)
                if self._possible_to_assign_freeday_on_date(loop_date):
                    (tmp1, tmp2, assigned) = self.tryAssign(loop_date,
                                                           "F",
                                                           duration=ONE_DAY,
                                                           reportErrors=False)
                    if assigned:
                        remaining_days -= 1
                elif self._possible_to_assign_freeday_on_date(loop_date, check_two_day_gap=True):
                    (tmp1, tmp2, assigned) = self.tryAssign(loop_date,
                                                           "F",
                                                           duration=TWO_DAYS,
                                                           reportErrors=False)
                    if assigned:
                        remaining_days -= 2
                if remaining_days == 0:
                    break
        if remaining_days > 0:
            self.error("Assign legal freedays",
                       date,
                       "Could only assign %s days, need %s" % \
                       (needed_days - remaining_days, needed_days))    

    def getWhereExpr(self):
        whereExpr = "True"
        return whereExpr

    def getRaveExpr(self):
        crewValues = ["freedays.%assign_vg_freedays%"]
        crewValues.append("freedays.%assign_parttime_freedays_midnight%")
        crewValues.append("freedays.%assign_flex_freedays%")
        return crewValues
    
class BlankdaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[BLANKDAYS]
            self.assign_type = ASSIGN_TYPES[BLANKDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose= verbose,
                                interactive_mode=interactive_mode)
        self.crews = []
        
    def getWhereExpr(self):
        whereExpr = "report_fdc15.%max_blankdays_to_assign% >= 0"
        return whereExpr

    def getRaveExpr(self):

        crewValues = ["crew.%country_at_plan_start%","report_fdc15.%max_blankdays_to_assign%","report_fdc15.%freedays_acc_balance%","report_fdc15.%freedays_year_bl_target%"]
        wopExpr = R.foreach(R.iter("iterators.wop_set",
                                   where=("report_fdc15.%wop_on_duty%")), # Including period conditions
                            "report_fdc15.%wop_start_day%",
                            "report_fdc15.%wop_end_day%",
                            "report_fdc15.%wop_hole1_date%",            # One or two holes in production wops, else minimum date
                            "report_fdc15.%wop_hole2_date%",
                            "report_fdc15.%wop_hole1_allowed_singlef%", # One or two holes in production wops, allowed as single F-days
                            "report_fdc15.%wop_hole2_allowed_singlef%")

        crewValues.append(wopExpr)
        contractPeriodExpr = R.foreach(
            R.times("report_fdc15.%contract_period_count%"),          
            'fundamental.%py_index%',
            'report_fdc15.%contract_period_start%(fundamental.%py_index%)',
            'report_fdc15.%contract_period_end%(fundamental.%py_index%)',
            'report_fdc15.%contract_period_is_fdc15%(fundamental.%py_index%)', # Fdc contract - freeday control of blank/freedays. Else as much as possible
            'report_fdc15.%contract_period_days%(fundamental.%py_index%)',
            'report_fdc15.%contract_period_prio%(fundamental.%py_index%)'      # flag indicating if single F-days is preferred
            )
            
        crewValues.append(contractPeriodExpr)
        return crewValues

    def assign_impl(self):
        if self.verbose:
            print "assign_impl started"
        crew = self.getCrew()
        total_target = 0
        lowBal = 999
        balDistr = {}
        for ix, crewid, empno, crewstation, country_code, fdcBlToAssign, balance, target, wops, contractPeriods in crew:
            self.setCrewObject(crewid, empno, crewstation)
            if self.verbose:
                print "read crew",crewid,", balance",balance,", target", target
                print "lookup for country ",country_code
            days, handleDays = self.init_assign(wops, contractPeriods)
            # days contain an entry for every possibly assignable day, with state about fdc contract and such things.
            # handleDays contains actions, dates to be tried first
            handleDays.sort()
            self.crews.append((balance, random.randint(0, 1000), False, crewid, empno, self.crewstation, self.vg_start, self.vg_end, self.emp_start, self.emp_end, days, handleDays ))
            total_target += target
            # save how many crew have each balance
            lowBal = min(balance, lowBal)
            if balance in balDistr:
                balDistr[balance] += 1
            else:
                balDistr[balance] = 1
        fdcBlToAssign = (total_target + 50) // 100 # Number of blank days to assign to all crew, in fdc controlled periods
        self.crews.sort()

        for i in range(len(self.crews)): # fill in no-fdc days, and forced (not allowed single freedays)
            balance, rand, full, crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end, days, handleDays = self.crews[i]
            self.setCrewObjectLight(crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end)
            ret = self.doAssign(True, 0, days, handleDays )
            if self.verbose:
                print "asg first",crewid, ret
            balance += ret
            fdcBlToAssign -= ret
            self.crews[i] = (balance, rand, full, crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end, days, handleDays)

        # after first run, all forced blank days have been set, and fdcBlToAssign adjusted
        # Calculate how a goal for balance, trying to give an even distribution of fdc balance if possible.
        # The first round will try to reach this goal for every crew. Following rounds will increase the goal with 1 until all days are
        # assigned, or no more crew can be assigned.
        floor = 0
        rosters_count = 0 
        goal = lowBal - 1
        for i in range(lowBal, lowBal + 100):
            floor += rosters_count
            goal = i
            if i in balDistr:
                rosters_count += balDistr[i]
            if floor + rosters_count> fdcBlToAssign:
                break
            print i, rosters_count, floor

        if self.verbose:
            print "fdc bl to assign: ",fdcBlToAssign,", floor",floor,", goal (first)",goal
            print "distr ",balDistr
        
        remains = True            
        while remains and fdcBlToAssign>0 and goal<100: #repeat assignement
            if self.verbose:
                print "remains",fdcBlToAssign,", goal",goal
            remains = False # assume no more crew have space for blankdays
            for i in range(len(self.crews)):
                balance, rand, full, crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end,days, handleDays = self.crews[i]
                self.setCrewObjectLight(crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end)
                if (not full) and (balance<goal):
                    ret = self.doAssign(False, goal-balance, days, handleDays )
                    if self.verbose:
                        print "asg 2",crewid,goal-balance, ret

                    if ret < goal-balance:
                        full =True # this crew need not be checked any more
                    else:
                        remains = True # at least one crew remains to be checked
                    balance += ret
                    fdcBlToAssign -= ret
                    self.crews[i] = (balance, rand, full, crewid, empno, crewstation, vg_start, vg_end, emp_start, emp_end, days, handleDays )
            goal += 1       # current balance target

               
                 
    def init_assign(self, wops, contractPeriods):
        days = {}
        handleDays = []
        # Phase 1: read all production wops, mark the days as unavailable, unless they are a hole.
        # The holes are marked BL_ST_HOLE= not usable is freedays, or BL_ST_ALW_HOLE: freeday allowed.
        # handleDays receive actions to check putting blankdays just before and after producion wops if legal,
        # as this sometimes is better than scattered production. 
        for wix, startDate, endDate, hole1Date, hole2Date, hole1AlwDate, hole2AlwDate in wops:
            if self.verbose:
                print "wop",wix,startDate,endDate,hole1Date,hole2Date,hole1AlwDate,hole2AlwDate
            set_day_range(days, startDate, endDate + ONE_DAY, BL_ST_UNAVAIL)
            handleDays.append((BL_PT_BEFORE, startDate - ONE_DAY ))
            handleDays.append((BL_PT_AFTER, endDate + ONE_DAY))                                         
            if hole1Date>=startDate:
                days[hole1Date] = BL_ST_HOLE
            if hole2Date>=startDate:
                days[hole2Date] = BL_ST_HOLE
            if hole1AlwDate>=startDate:
                days[hole1AlwDate] = BL_ST_ALW_HOLE
            if hole2AlwDate>=startDate:
                days[hole2AlwDate] = BL_ST_ALW_HOLE

        # Phase 2: read all contract periods, mainly to see if it's FG, FDC or non FDC
        for count, pix, startPeriod, endPeriod, isFdc15, noOfDaysInPeriod, prioAttr in contractPeriods:
            d = startPeriod
            while d<endPeriod:
                if self.verbose:
                    print "setp",d,get_day(days,d)     
                if is_day(days, d, BL_ST_MISSING): # candidate as blank day
                    days[d] = BL_ST_FDC15_UNKNOWN if isFdc15 else BL_ST_OTH_UNKNOWN
                elif is_day(days, d, BL_ST_HOLE): # hole which is not allowed for single f. Filled with blank days if only legal
                    days[d] = BL_ST_FDC15_FORCED if isFdc15 else BL_ST_OTH_UNKNOWN
                    handleDays.append((BL_PT_SINGLE, d))
                elif is_day(days, d, BL_ST_ALW_HOLE): # Allowed as freeday. Contract flag decides if preferred
                    if is_prio(prioAttr, PRIO_SINGLE_F): # single freedays on saturdays/holidays preferred, 
                        days[d] = BL_ST_FDC15_LAST if isFdc15 else BL_ST_OTH_LAST # Fill blankdays to hole last
                    elif is_prio(prioAttr, PRIO_SINGLE_F) or is_prio(prioAttr, PRIO_NOT_SINGLE_F): # it's not single freedays not preferred
                        days[d] = BL_ST_FDC15_UNKNOWN if isFdc15 else BL_ST_OTH_UNKNOWN
                        handleDays.append((BL_PT_SINGLE, d))
                    else:
                        days[d] = BL_ST_FDC15_UNKNOWN if isFdc15 else BL_ST_OTH_UNKNOWN # handle as ordinary gaps
                d += ONE_DAY   
        return days, handleDays


    def tryBlankAssign(self, date, days):
        if self.verbose:
            print "tryBlankAssign ",date
        (code, onDuty, assigned) = self.tryAssign(date, "BL",
                                            reportErrors=False,
                                            legalAssignment=True, okToFG=True)
        days[date] = BL_ST_ASSIGNED # either new, or old
        return assigned
   

    def doAssign(self, isFirst, fdcBlToAssign, days, handleDays):
        blAssigned = 0
        #fill holes and near production
        for pt, d in handleDays:
            if self.verbose:
                print "handle ",pt,d
            if pt == BL_PT_AFTER:    # try setting blankdays after production day
                lim = d + 31*ONE_DAY
                step = ONE_DAY
            elif pt == BL_PT_BEFORE: # try setting blankdays before production day
                lim = d + 31*ONE_DAY
                step = -ONE_DAY
            else:                # try setting blankdays at (hole) day
                lim = d+ ONE_DAY
                step = ONE_DAY
            while d!=lim:
                if self.verbose:
                    print "handledays ",d, pt, get_day(days, d)
                if is_day(days, d, BL_ST_FDC15_FORCED): # holes not allowed for single freedays, in fdc contracts
                    if self.tryBlankAssign(d, days):
                        blAssigned += 1                 # those should be assigned, but decreases need from someone else
                    else:
                        break
                elif is_day(days, d, BL_ST_FDC15_UNKNOWN) and not isFirst: #Normal FDC not set first phase
                    if self.tryBlankAssign(d,days):
                        blAssigned += 1
                        if blAssigned>fdcBlToAssign:
                            break
                    else:
                        break
                elif is_day(days, d, BL_ST_OTH_UNKNOWN):
                    if self.tryBlankAssign(d,days):
                        pass
                    else:
                        break
                else:
                    break
                d += step
            if blAssigned>=fdcBlToAssign and not isFirst:
                break
        # try all except holes to be filled last
        if blAssigned<fdcBlToAssign or isFirst:
            for d in days.keys():
                if is_day(days, d, BL_ST_OTH_UNKNOWN) and isFirst:
                    if self.tryBlankAssign(d, days):
                        pass
                elif is_day(days, d, BL_ST_FDC15_UNKNOWN) and not isFirst and blAssigned<fdcBlToAssign:
                    if self.tryBlankAssign(d, days):
                        blAssigned += 1
                        if blAssigned>fdcBlToAssign:
                            break
        # try last 
        if blAssigned<fdcBlToAssign or isFirst:
            for d in days.keys():
                if is_day(days, d, BL_ST_OTH_LAST) and isFirst:
                    if self.tryBlankAssign(d, days):
                        pass
                elif is_day(days, d, BL_ST_FDC15_LAST) and not isFirst and blAssigned<fdcBlToAssign:
                    if self.tryBlankAssign(d, days):
                        blAssigned += 1
                        if blAssigned>fdcBlToAssign:
                            break
        return blAssigned
 
class SelfTrgAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[SELF_TRG_DAYS]
            self.assign_type = ASSIGN_TYPES[SELF_TRG_DAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose= verbose,
                                interactive_mode=interactive_mode)
        self.crews = []
        
    def getWhereExpr(self):
        whereExpr = "report_training_fc.%missing_any_self_trg%"
        return whereExpr

    def getRaveExpr(self):

        crewValues = []
        #crewValues.append( = ["e%","report_fdc15.%freedays_year_bl_target%"]
        selfTrgExpr = R.foreach(
            R.times("report_training_fc.%self_trg_type_ix_max%"),
            "fundamental.%py_index%",
            "report_training_fc.%self_trg_valid%(fundamental.%py_index%)",                    
            "report_training_fc.%self_trg_missing%(fundamental.%py_index%)",                    
            "report_training_fc.%self_trg_code%(fundamental.%py_index%)",                    
            "report_training_fc.%self_trg_duration%(fundamental.%py_index%)")                    
        crewValues.append(selfTrgExpr)
        wopExpr = R.foreach(R.iter("iterators.wop_set",
                  where=("report_training_fc.%wop_on_duty%")), # Including period conditions
            "report_training_fc.%wop_start_day%", 
            "report_training_fc.%wop_end_day%",
            "report_training_fc.%wop_hole_day%",
            "report_training_fc.%wop_rest_before%", #latest time finishing a duty before this wop            
            "report_training_fc.%wop_rest_after%",  #first time starting a non fdp duty after this wop
            "report_training_fc.%wop_rest_in_hole%") # start time of a duty in a hole in wop, not acceptable as freedays

        crewValues.append(wopExpr)
        return crewValues

    def assign_impl(self):
        if self.verbose:
            print "assign_impl started"
        crew = self.getCrew()
        for ix, crewid, empno, crewstation, trg_types, wops in crew:
            self.setCrewObject(crewid, empno, crewstation)
            if self.verbose:
                print "read crew",crewid #,", alance",balance,", target", target
            trgTypes, timeslots = self.init_assign(trg_types, wops)
            timeslots.sort()

            self.doAssign(trgTypes, timeslots)
               
                 
    def init_assign(self, trg_types, wops):
        timeslots = []
        trgTypes = []

        for count, trix, trValid, trMissing, trCode, trDuration in trg_types:
            if trValid:
                if self.verbose:
                    print "trgType", trix, trValid, trMissing, trCode, trDuration
                trgTypes.append((trMissing, trCode, trDuration))
        
        for wix, startDate, endDate, holeDate, posBefore, posAfter, posInHole in wops:
            if self.verbose:
                print "wop",wix, posBefore, posAfter, posInHole
            if posBefore >= self.pp_start:
                timeslots.append((1,posBefore, True))
            if posAfter >= self.pp_start:
                timeslots.append((1,posAfter, False))
            if posInHole >= self.pp_start:
                timeslots.append((1,posInHole, False))

        return trgTypes, timeslots


    def tryTrAssign(self, trTime, trDuration, trCode):
        if self.verbose:
            print "tryTrgAssign ",trTime, trDuration, trCode
        (code, onDuty, assigned) = self.tryAssign(trTime, trCode,
                                              duration = trDuration, 
                                            reportErrors=False,
                                            legalAssignment=True, okToFG=True)
        return assigned
   
    def doAssignTrgType(self, trMissing, trCode, trDuration, timeslots):
        for i in range(trMissing):
            for prio, timeslot, bef in timeslots:
                t = timeslot - trDuration if bef else timeslot # assignment before gives time for end of activity
                if self.tryTrAssign(t, trDuration, trCode):
                    trMissing -= 1
                if trMissing<=0:
                    return 0
        return trMissing        

    def doAssign(self, trgTypes, timeslots):
        for trMissing, trCode, trDuration in trgTypes:
            ret = self.doAssignTrgType(trMissing, trCode, trDuration, timeslots)
            if self.verbose:
                print "remaining",ret," of code ",trCode                    


class ShortGroundActivitiesAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[SHORT_GROUND_ACTIVITIES]
            self.assign_type = ASSIGN_TYPES[SHORT_GROUND_ACTIVITIES]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose= verbose,
                                interactive_mode=interactive_mode)
        self.crews = []

    def getWhereExpr(self):
        whereExpr = "short_ground_training.%SGT_to_be_assigned%"
        return whereExpr

    def getRaveExpr(self):
        crewValues = ["short_ground_training.%SGT_activity_code%",
                      "short_ground_training.%chosen_start_time_for_SGT_activity%",
                      "short_ground_training.%SGT_activity_duration%"]
        return crewValues

    def assign_impl(self):
        if self.verbose:
            print "assign_impl started"
        crew = self.getCrew()
        for ix, crewid, empno, crewstation, activity_code, start_time, duration in crew:
            self.setCrewObject(crewid, empno, crewstation)
            if self.verbose:
                print "read crew",crewid
            self.tryAssign(start_time, activity_code, reportErrors=True,
                           legalAssignment=False, duration=duration, okToFG=True)


class F36freedaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[F36FREEDAYS]
            self.assign_type = ASSIGN_TYPES[F36FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        crew = self.getCrew()
        for ix, crewid, empno, crewstation, f36ToAssign, wops in crew:
            self.setCrewObject(crewid, empno, crewstation)
            self.assignF36days(f36ToAssign, wops)

    def assignF36days(self, f36ToAssign, wops):

        occupiedDays = dict()
        # We need to iterate over the wops multiple times since we want to
        # prioritize the assingment inter-wop

        # 1. Fill holes in wops
        for jx, startDate, endDate, hole1Date, hole2Date in wops:
            date = startDate
            while date <= endDate:
                occupiedDays[date] = True
                date += ONE_DAY
            for date in (hole1Date, hole2Date):
                if f36ToAssign > 0:
                    if date >= self.pp_start and date < self.publ_end:
                        result = self.tryAssign(date, "F36",
                                                reportErrors=False,
                                                legalAssignment=True, okToFG=True)
                        (code, onDuty, assigned) = result
                        if assigned:
                            f36ToAssign -= 1
        # 2. Add at the end of wop
        for jx, d1, endDate, h1, h2 in wops:
            code = "F36"
            date = endDate + ONE_DAY
            while code == "F36" and f36ToAssign > 0 and date < self.publ_end:
                if not occupiedDays.get(date, False):
                    result = self.tryAssign(date, "F36",
                                            reportErrors=False,
                                            legalAssignment=True, okToFG=True)
                    (code, onDuty, assigned) = result
                    occupiedDays[date] = True
                    if assigned:
                        f36ToAssign -= 1
                date += ONE_DAY
        # 3. Add before wop
        for jx, startDate, d2, h1, h2 in wops:
            code = "F36"
            date = startDate - ONE_DAY
            while code == "F36" and f36ToAssign > 0 and date >= self.pp_start:
                if not occupiedDays.get(date, False):
                    result = self.tryAssign(date, "F36",
                                            reportErrors=False,
                                            legalAssignment=True, okToFG=True)
                    (code, onDuty, assigned) = result
                    occupiedDays[date] = True
                    if assigned:
                        f36ToAssign -= 1
                date -= ONE_DAY
        # 4. Fill roster until illegal
        date = self.pp_start
        randomOffset = random.randint(0, self.publ_days - 1)
        dayIx = randomOffset
        while dayIx < self.publ_days and f36ToAssign > 0:
            date = self.pp_start + RelTime.RelTime(dayIx * 24, 0)
            if occupiedDays.get(date, False):
                # Date is occupied
                pass
            else:
                result = self.tryAssign(date, "F36",
                                        reportErrors=False,
                                        legalAssignment=True, okToFG=True)
                (code, onDuty, assigned) = result
                if assigned:
                    f36ToAssign -= 1
            dayIx += 1
            if dayIx == self.publ_days:
                # We've reached the end, lets start over from pp_start
                dayIx = 0
            if dayIx == randomOffset:
                # We have completed the iteration through the published period
                dayIx = self.publ_days

    def getWhereExpr(self):
        whereExpr = "crew.%monthly_f36_target% > 0"
        return whereExpr

    def getRaveExpr(self):

        crewValues = ["crew.%monthly_f36_target%"]
        wopExpr = R.foreach(R.iter("iterators.wop_set",
                                   where=("wop.%in_pp%",
                                          "not void(wop.%start_day%)",
                                          "not void(wop.%end_day%)"
                                          )),
                            "wop.%start_day%",
                            "wop.%end_day%",
                            "wop.%hole_1_date%",
                            "wop.%hole_2_date%")
        crewValues.append(wopExpr)
        return crewValues
    
class PublishFreedaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[PUBLISH_FREEDAYS]
            self.assign_type = ASSIGN_TYPES[PUBLISH_FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        carry_out = bool(Gui.GuiYesNo('assigning_freeday',
                                      'Assign one carry out freeday into next month\n' + \
                                      'if single empty day on last day in publ. period?'))
        crew = self.getCrew()
        for ix, crewid, empno, crewstation in crew:
            self.setCrewObject(crewid, empno, crewstation)
            self.assignPublishFreedays(assign_carry_out=carry_out)

    def assignPublishFreedays(self, assign_carry_out=False):
        """
        Tries to fill holes with freeday object
        """
        date = self.pp_start
        end_date = date + ONE_DAY * self.publ_days
        possible_periods = self.get_empty_periods_in_roster(date, end_date)
        if self.verbose:
            "assign publ freed",possible_periods

        for start_t, end_t in possible_periods.items():
            duration_int = int((end_t - start_t) / ONE_DAY)
            assigned = False
            if duration_int > 0:
                (tmp1, tmp2, assigned) = self.tryAssign(start_t, "F",
                                                        reportErrors=False,
                                                        legalAssignment=False,
                                                        duration=ONE_DAY * duration_int, okToFG=False)
            # If single day or more than on day, check each indidual day
            if duration_int == 0:
                if self._possible_to_assign_freeday_on_date(start_t):
                    # One day freeday assignment, not to popular (in fact, it's illegal)
                    # check if adjecent to freedays 
                    (tmp1, tmp2, assigned) = self.tryAssign(start_t, "F",
                                                            reportErrors=False,
                                                            legalAssignment=False,
                                                            duration=ONE_DAY, okToFG=False)
                elif assign_carry_out and not assigned and duration_int == 1 and \
                         start_t == (end_date - ONE_DAY) and \
                         self._possible_to_assign_freeday_on_date(start_t,
                                                                  check_two_day_gap=True):
                    (tmp1, tmp2, assigned) = self.tryAssign(start_t, "F",
                                                            reportErrors=False,
                                                            legalAssignment=False,
                                                            duration=ONE_DAY * 2, okToFG=False)
            if not assigned:
                self.error("F", start_t, "Not possible to assign freeday to period %s-%s" % \
                           (start_t.ddmonyyyy(True), end_t.ddmonyyyy(True)))

    def getWhereExpr(self):
        return "True"
    def getRaveExpr(self):
        return []


class SpecificFDaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[SPECIFIC_FREEDAYS]
            self.assign_type = ASSIGN_TYPES[SPECIFIC_FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        #get parameters set by the user
        _get_freeday_code = "freedays.%freeday_assigner_task_code%"
        _freeday_code_valid = "freedays.%freeday_assigner_task_code_valid%"
        _24_hour_blocks = "freedays.%freeday_assigner_assign_24_hour_blocks%"

        self.tc, = R.eval(_get_freeday_code)
        self.assign_24_hour_blocks, = R.eval(_24_hour_blocks)

        crew = self.getCrew()
        for ix, crewid, empno, crewstation in crew:
            self.setCrewObject(crewid, empno, crewstation)
            tcv, = self.crewEval(_freeday_code_valid)
            if not tcv:
                #User has entered non freeday code in parameter form
                #tell them and bail
                Gui.GuiMessage(self.tc + " not a valid Freeday code for crew " + str(crewid))
                return

        carry_out = bool(Gui.GuiYesNo('assigning_specific_freeday',
                                      'Assign one carry out fnday into next month\n' + \
                                      'if single empty day on last day in publ. period?'))
        for ix, crewid, empno, crewstation in crew:
            self.setCrewObject(crewid, empno, crewstation)
            self.assignFDays(assign_carry_out=carry_out)
    
    def report_error(self, start_t, end_t):
        self.error(self.tc, start_t, "Not possible to assign %s to period %s-%s" % (self.tc, start_t.ddmonyyyy(True), end_t.ddmonyyyy(True)))

    def assignFDays(self, assign_carry_out=False):
        """
        Tries to fill holes with freeday object
        """
        date = self.pp_start
        end_date = date + ONE_DAY * self.publ_days
        possible_periods = self.get_empty_periods_in_roster(date, end_date)
        for start_t, end_t in possible_periods.items():
            if assign_carry_out and \
            self._possible_to_assign_freeday_on_date(end_t):
                end_t += ONE_DAY
            duration_int = int((end_t - start_t) / ONE_DAY)
            if self.assign_24_hour_blocks:
                for n in xrange(duration_int):
                    _, _, assigned = self.tryAssign(start_t + (n * ONE_DAY),
                                                    self.tc,
                                                    reportErrors=False,
                                                    legalAssignment=False,
                                                    duration=ONE_DAY,
                                                    okToFG=False)
                    if not assigned:
                        self.report_error(start_t + (n * ONE_DAY),
                                         start_t + ((n + 1) * ONE_DAY))
            else:
                _, _, assigned = self.tryAssign(start_t,
                                                reportErrors=False,
                                                legalAssignment=False,
                                                duration=ONE_DAY * duration_int,
                                                okToFG=False)
                if not assigned:
                    self.report_error(start_t, end_t)

    def getWhereExpr(self):
        return "True"
    def getRaveExpr(self):
        return []


class XmasFreedaysAssigner(AssignerObject):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[XMAS_FREEDAYS]
            self.assign_type = ASSIGN_TYPES[XMAS_FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        carry_out = True
        crew = self.getXmasCrew()
        for ix, crewid, empno, crewstation, crewregion, main_cat, season_start_date, season_end_date in crew:
            self.setCrewObject(crewid, empno, crewstation)
            self.assignXmasFreedays(crewid, crewregion, main_cat, season_start_date, season_end_date, carry_out)

    def assignXmasFreedays(self, crew_id, crew_region, main_cat, season_start_date, season_end_date, assign_carry_out=False):
        """
        Tries to fill holes with freeday object
        """
        
        # crew is inactive 
        if crew_region == None:
            return
        
        i = 1
        start_input = '"' + str(crew_id) + '","' + str(crew_region) + '","' + str(main_cat) + '",' + str(season_start_date) + ',' + str(i)
        s_start_xmas_freeday = "report_common.%x_start_xmas_date%(" + start_input + ")" 
        start_xmas_freeday, = R.eval(s_start_xmas_freeday)
        start = start_xmas_freeday

        group_at_date, = R.eval('crew.%grouptype_at_date%("' + str(crew_id) + '",' + str(start) + ')')
        fg = (group_at_date == "F")
        
        done = False
        while not fg and start and start >= season_start_date and start < season_end_date and not done:
            assigned = False
                  
            nbr_input = s_start_xmas_freeday + ',"' + str(crew_id) + '","' + str(crew_region) + '","' + str(main_cat) + '",' + str(season_start_date)
            s_nbr_of_xmas_freedays = 'report_common.%x_nbr_of_xmas_freedays%(' + nbr_input + ')'
            s_activity_type = "report_common.%x_xmas_activity_type%(" + nbr_input + ")"
       
            (nbr_of_xmas_freedays, activity_type) = R.eval(s_nbr_of_xmas_freedays,
                                                           s_activity_type)
       
            if nbr_of_xmas_freedays > 0:
                duration_int = nbr_of_xmas_freedays 
                end_date = start + ONE_DAY * duration_int
                
                (tmp1, tmp2, assigned) = self.tryAssign(start, activity_type,
                                                        reportErrors=False,
                                                        legalAssignment=False,
                                                        duration=ONE_DAY * duration_int, okToFG=True)
                
                if not assigned:
                    self.error(activity_type, start, "Not possible to assign xmas freeday to period %s-%s" % \
                               (start.ddmonyyyy(True), end_date.ddmonyyyy(True)))

            else:
                end_date = start + ONE_DAY * 0
                self.error(activity_type, start, "Not possible to assign zero xmas freeday to %s" % \
                           (start.ddmonyyyy(True)))
                
            i += 1 
            start_input = '"' + str(crew_id) + '","' + str(crew_region) + '","' + str(main_cat) + '",' + str(season_start_date) + ',' + str(i) 
            s_start_xmas_freeday = "report_common.%x_start_xmas_date%(" + start_input + ")" 
            start, = R.eval(s_start_xmas_freeday)   
                
            # Is there no more Xmas days to add
            if not start:
                done = True
            else:
                group_at_date, = R.eval('crew.%grouptype_at_date%("' + str(crew_id) + '",' + str(start) + ')')
                fg = (group_at_date == "F")

    def getWhereExpr(self):
        return "True"
    
    def getRaveExpr(self):
        return []    
    
class LegalFreedaysAssigner(AssignerObject, PostOpFreeDaysAssigner):
    def __init__(self, area= -1, verbose=False, interactive_mode=True):
        # Sets various assignment type independent variables
        try:
            self.assign_message = CONFIRM_TITLES[LEGAL_FREEDAYS]
            self.assign_type = ASSIGN_TYPES[LEGAL_FREEDAYS]
        except IndexError:
            self.assign_message = ""
            self.assign_type = ""
            pass
        AssignerObject.__init__(self,
                                area=area,
                                verbose=verbose,
                                interactive_mode=interactive_mode)
    def assign_impl(self):
        crew = self.getCrew()
        for ix, crewid, empno, crewstation in crew:
            self.setCrewObject(crewid, empno, crewstation)
            PostOpFreeDaysAssigner.assign_legal_freedays(self)
            
    def getWhereExpr(self):
        whereExpr = "crew.%has_some_variable_group_in_publ%"
        return whereExpr
    def getRaveExpr(self):
        return []

ASSIGN_OBJECTS = {COMPDAYS:CompdaysAssigner,
                  PREOP_FREEDAYS:PreOpFreeDaysAssigner,
                  POSTOP_FREEDAYS:PostOpFreeDaysAssigner,
                  BLANKDAYS:BlankdaysAssigner,
                  F36FREEDAYS:F36freedaysAssigner,
                  PUBLISH_FREEDAYS:PublishFreedaysAssigner,
                  XMAS_FREEDAYS:XmasFreedaysAssigner,
                  LEGAL_FREEDAYS:LegalFreedaysAssigner,
                  SPECIFIC_FREEDAYS:SpecificFDaysAssigner,
                  SELF_TRG_DAYS:SelfTrgAssigner,
                  SHORT_GROUND_ACTIVITIES:ShortGroundActivitiesAssigner}

def assignInWindow(assignTypeString, interactive_mode=True):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    logPrefix = "AssignActivities::assignInWindow: "
    if not assignTypeString in ASSIGN_TYPES:
        raise ValueError, "Function called with illegal argument"
    assignType = ASSIGN_TYPES.index(assignTypeString)
    
    if interactive_mode:
        if not cfhExtensions.confirm(CONFIRM_MESSAGES[assignType],
                                     title=CONFIRM_TITLES[assignType]):
            if verbose:
                Errlog.log(logPrefix + "Cancelled by the user.")
            return None

        if verbose:
            Errlog.log(logPrefix + "Assigning " + assignTypeString + "...")

    assigner = ASSIGN_OBJECTS[assignType](area=area, verbose=(verbose and interactive_mode))
    # The actual assignment is separated to a function
    # Propagate possible return value
    return assigner.assign()

class PPModifier:
    def __init__(self, new_start_para, new_end_para):
        self.start_para, self.end_para = R.eval(
            'fundamental.%start_para%',
            'fundamental.%end_para%',
            )
        self.set_pp_para(new_start_para)
        self.set_pp_para(new_end_para, False)
        Errlog.log("AssignActivities::PPModifier: Planning period set to %s %s" % \
                   (new_start_para, new_end_para))
        
    def __del__(self):
        self.set_pp_para(self.start_para)
        self.set_pp_para(self.end_para, False)
        Errlog.log("Activities::PPModifier: Planning period reset to %s %s" % \
                   (self.start_para, self.end_para))

    def set_pp_para(self, new_para, start=True):
        if start:
            R.param('fundamental.%start_para%').setvalue(new_para)
        else:
            R.param('fundamental.%end_para%').setvalue(new_para)
