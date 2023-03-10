"""
Overtime python module
"""

import carmensystems.rave.api as R
from utils.rave import RaveIterator
from utils.RaveData import DataClass
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
from time import clock
from tm import TM
import salary.conf as conf
from utils.performance import clockme, log


(   DUTIES ,
    SALARY_SYSTEM,
    HOME_CURRENCY ,
    CREW_ID ,
    FIRST_NAME ,
    LAST_NAME ,
    HOMEBASE ,
    RANK ,
    MONTH ,
    MAIN_FUNC ,
    IS_FULL_TIME ,
    IS_TEMPORARY ,
    IS_TEMPORARY_TWO_MONTHS ,
    MAITRE_DE_CABIN_SHORT_HAUL ,
    MAITRE_DE_CABIN_LONG_HAUL ,
    MAITRE_DE_CABIN,
    SENIOR_CC_ALLOWANCE ,
    SENIOR_CC_ALLOWANCE_NO_PURSER ,
    LOSS_OF_REST_LOW ,
    LOSS_OF_REST_HIGH ,
    TEMPORARY_CREW_HOURS ,
    ILL_TEMPORARY_CREW_HOURS ,
    EMPNO ,
    IS_SKD ,
    IS_SKN ,
    IS_SKS ,
    IS_FC,
    IS_FP,
    SUM_OT_FD_UNITS,
    SUM_OT_FD_NETTO,
    IS_CONVERTIBLE ,
    IS_FLIGHT_CREW ,
    FULLTIME_DT_MONTH ,
    EXCLUDED ,
    IS_CC_4EXNG,
    IS_FC_4EXNG,
    INST_LCI_SH,
    INST_LCI_LH,
    SNGL_SLIP_LONGHAUL,
    TEMPORARY_CREW_HOURS_DAILY,
) = range(40)
ROSTER_VALUES = ('salary.%salary_system%(salary.%salary_run_date%)',
                'report_per_diem.%per_diem_home_currency%',
                'report_common.%crew_id%',
                 'report_common.%crew_firstname%',
                 'report_common.%crew_surname%',
                 'report_common.%crew_homebase_salary%',
                 'report_common.%crew_rank_salary%',
                 'report_overtime.%month_start%',
                 'report_common.%crew_main_func_salary%',
                 'report_overtime.%is_full_time%',
                 'report_overtime.%is_temporary%',
                 'report_overtime.%is_temporary_two_months%',
                 'report_overtime.%maitre_de_cabin_short_haul%',
                 'report_overtime.%maitre_de_cabin_long_haul%',
                 'report_overtime.%maitre_de_cabin%',
                 'report_overtime.%senior_cc_allowance%',
                 'report_overtime.%senior_cc_allowance_no_purser%',
                 'report_overtime.%loss_of_rest_low%',
                 'report_overtime.%loss_of_rest_high%',
                 'report_overtime.%temporary_crew_hours%',
                 'report_overtime.%ill_temporary_crew_hours%',
                 'report_common.%employee_number_salary%',
                 'report_overtime.%is_skd%',
                 'report_overtime.%is_skn%',
                 'report_overtime.%is_sks%',
                 'report_overtime.%is_FC%',
                 'report_overtime.%is_FP%',
                 'report_overtime.%sum_OT_FD_units%',
                 'report_overtime.%sum_OT_FD_netto%',
                 'report_overtime.%is_convertible%',
                 'fundamental.%flight_crew%',
                 'report_overtime.%full_time_duty_in_month%',
                 'salary.%crew_excluded%',
                 'report_overtime.%4exng_cc_ot_valid%',
                 'report_overtime.%4exng_fc_ot_valid%',
                 'salary.%inst_lci_sh%',
                 'salary.%inst_lci_lh%',
                 'salary.%extra_salary_for_single_slipping_longhaul%',
                )

OT_PART_CALENDARWEEK = 0
OT_PART_DUTYPASS = 4
OT_PART_LATE_CHECKOUT = 8
OT_PART_7_CALENDARDAYS = 12
OT_PART_PARTTIME_CC_MONTH = 16
OT_PART_PARTTIME_CC_3_MONTHS = 20
MT_PART_PARTTIME_CC_MONTH = 24
MT_PART_PARTTIME_CC_3_MONTHS = 28
OT_PART_PARTTIME_MONTH = 32
OT_PART_MONTH = 36
DUTY_VALUES = ('report_overtime.%overtime_calendar_week_ot%',
               'report_overtime.%overtime_calendar_week_start%',
               'report_overtime.%overtime_calendar_week_end%',
               'report_overtime.%overtime_calendar_week_duty%',
               
               'report_overtime.%overtime_dutypass_ot%',
               'report_overtime.%overtime_dutypass_start%',
               'report_overtime.%overtime_dutypass_end%',
               'report_overtime.%overtime_dutypass_duty%',
               
               'report_overtime.%overtime_late_checkout_ot%',
               'report_overtime.%overtime_late_checkout_start%',
               'report_overtime.%overtime_late_checkout_end%',
               'report_overtime.%overtime_late_checkout_duty%',
               
               'report_overtime.%overtime_7_calendar_days_ot%',
               'report_overtime.%overtime_7_calendar_days_start%',
               'report_overtime.%overtime_7_calendar_days_end%',
               'report_overtime.%overtime_7_calendar_days_duty%',

               # 1 month part time CC overtime
               'report_overtime.%overtime_part_time_cc_one_month%',
               'report_overtime.%overtime_part_time_cc_one_month_start%',
               'report_overtime.%overtime_part_time_cc_one_month_end%',
               'report_overtime.%overtime_part_time_cc_one_month_duty%',

               #
               # Skipped from optimization run, set OT_OPT_SKIP_VALUES accordingly
               #

               # 3 month part time overtime and mertid go partly through the solver.
               # They shouldn't be compared to other overtimes and risk getting discarded
               # or cause another value to be discarded. But their values need to be 
               # gathered for later calculations.

               # 3 month part time CC overtime
               'report_overtime.%overtime_part_time_cc_three_months%',
               'report_overtime.%overtime_part_time_cc_three_months_start%',
               'report_overtime.%overtime_part_time_cc_three_months_end%',
               'report_overtime.%overtime_part_time_cc_three_months_duty%',

               # 1 month part time CC mertid
               'report_overtime.%mertid_part_time_cc_one_month%',
               'report_overtime.%mertid_part_time_cc_one_month_start%',
               'report_overtime.%mertid_part_time_cc_one_month_end%',
               'report_overtime.%mertid_part_time_cc_one_month_duty%',
                
               # 3 month part time CC mertid
               'report_overtime.%mertid_part_time_cc_three_months%',
               'report_overtime.%mertid_part_time_cc_three_months_start%',
               'report_overtime.%mertid_part_time_cc_three_months_end%',
               'report_overtime.%mertid_part_time_cc_three_months_duty%',

               # The below variables skip the solver entirely.

               # "Mertid"
               'report_overtime.%overtime_part_time_month_ot%',
               'report_overtime.%overtime_part_time_month_start%',
               'report_overtime.%overtime_part_time_month_end%',
               'report_overtime.%overtime_part_time_month_duty%',
               
               # Month balancing is hard-coded to keep optimization. Keep it last in this tuple
               'report_overtime.%overtime_month_ot%',
               'report_overtime.%overtime_month_start%',
               'report_overtime.%overtime_month_end%',
               'report_overtime.%overtime_month_duty%'
               )
# The number of 4-groups of Rave variables above to NOT include in the optimization.
# Typically all monthly values should be placed here.
OT_OPT_SKIP_VALUES = 1


class OvertimeSolver:
    """Solves the optimization problem of finding the largest non-overlapping
       contributions to overtime."""
    def __init__(self):
        self._list = []
        self._max = None
        self._iter = 0

    def addRange(self, tupls): #wrapper to old
        for (value, start, end, payload) in tupls:        
            self.add(start, end, value, payload)

    def add(self, start, end, value, payload):
        self._max = None
        self._list.append((int(start), int(end), int(value), payload))

    def tolist(self, lst):
        s = []
        for i in xrange(32):
            if (lst >> i) & 1: s.append(i)
        return s

    def solve(self):
        # Partition the problem and solve subproblems.
        # Assumes the problem is sufficiently partitionable, otherwise we have
        # a knapsack-like problem which is O(N!)
        l = len(self._list)
        if l == 0:
            return (0, [])
        partitions = self._partition()
        #partitions = [range(len(self._list))]
        maxl  = max(map(len,partitions))
        #print "Partitioned into", len(partitions), "regions of max size", maxl, "reduced from", l
        #print "Problem: ", partitions
        maxv = 0
        tl = []
        c1 = clock()
        for part in partitions:
            sub = OvertimeSolver()
            sub._list = [self._list[x] for x in part]
            idxs = range(len(sub._list))
            idxs.sort(cmp=lambda x,y: sub._list[x][0].__cmp__(sub._list[y][0]))
            sub._solve(0, idxs)
            self._iter += sub._iter
            maxv += sub._max[0]
            tl += [part[x] for x in self.tolist(sub._max[1])]
        #print "Solved the problem in ", self._iter, " iterations, took", clock()-c1
        tl.sort()
        return (maxv, tl)

    def _partition(self):
        # Prune obvious bad choices (and identical ones)
        inferior = 0
        i = len(self._list)
        # indexes of the
        idxs = range(len(self._list))
        while i > 0:
            i -= 1
            if self._isinferior(i, idxs):
                idxs.remove(i)

        partitions = []
        for i in idxs:
            for p in partitions:
                for j in p:
                    if i != j and self._overlaps(i,j):
                        p.add(i)
                        break
            partitions.append(set([i]))
        for p1 in xrange(len(partitions)):
            for p2 in xrange(p1+1,len(partitions)):
                for i in partitions[p1]:
                    if i in partitions[p2]:
                        partitions[p1] = partitions[p1].union(partitions[p2])
                        partitions[p2].clear()
        # Remove empty partitions and convert to list of lists
        partitions = filter(lambda x:len(x)>0, map(list, partitions))
        return partitions

    def _solve(self, l, idxs):
        if not l:
            sidx = range(len(idxs))
            self._olap = [[int(self._overlaps(i,j)) for j in sidx] for i in sidx]
            if not self._list:
                self._max = 0
                self._maxList = []
                return
            l = 0
            if len(self._list) > 40: raise Exception("Problem is too large = ", len(self._list))
        nchk = 0
        nm = 0
        self._iter += 1
        if self._iter % 100000 == 0:
            print "Looped %d times" % self._iter
        if self._iter > 500000:
            print "** This problem was too complex to solve **"
            print "Taking the best so far"
            return self._max
        for i in idxs:
            if l & (1<<i): continue
            bad = False
            for j in idxs:
                if l & (1<<j) and self._olap[i][j]:
                    bad = True
                    break
            if bad: continue
            nchk += 1
            val = self._solve(l | (1<<i), idxs)
            if val > nm: nm = val
        if not nchk:
            nm = 0
            for i in idxs:
                if l & (1<<i):
                    nm += self._value(i)
            if not self._max or self._max[0] < nm:
                self._max = (nm, l)
        return nm
            
    def _overlaps(self, i1, i2):
        s1,e1,_,_ = self._list[i1]
        s2,e2,_,_ = self._list[i2]
        return not (s1 > e2 or e1 < s2)
     
    def _isinferior(self, idx, idxs, infs=None, vsum=0):
        s1,e1,v1,_ = self._list[idx]
        if not infs: infs = []
        for i in idxs:
            if i == idx: continue
            s2,e2,v2,_ = self._list[i]
            if s1 <= s2 and e1 >= e2:
                if sum([self._overlaps(i, x) for x in infs]): continue
                vsum += v2
                infs.append(i)
                if v1 <= vsum:
                    return True
                else:
                    return self._isinferior(idx, idxs, infs, vsum)
        return False
        
    def _inferior(self, i1, i2):
        s1,e1,v1,_ = self._list[i1]
        s2,e2,v2,_ = self._list[i2]
        if s1 <= s2 and e1 >= e2 and v1 <= v2:
            return True
        return False

    def _value(self, idx):
        _,_,value,_ = self._list[idx]
        return value


class OvertimeRosterManager:
    """
    A class that creates and holds OvertimeRosters.
    """

    def __init__(self, context, iterator='iterators.roster_set', crewlist=None):
        self.context = context
        self.rosterIterator = iterator
        self.crewlist = crewlist
        self.startDate = R.param(conf.startparam).value()
        self.endDate = R.param(conf.endparam).value()

    def getOvertimeRosters(self):
        overtimeRosters = []

        if self.crewlist:
            try:
                import Cui
                Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, self.crewlist)
                Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiScriptBuffer)
                Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
                self.context = "default_context"
            except:
                # CuiSetCurrentArea may fail (e.g. in report workers).
                # No real problem, just a bit slower. It is filtered later on anyway.
                pass

        # Add daily values for temporary crew hours
        dt = self.startDate
        day_offset = 0
        hour_values = []
        while(dt < self.endDate):
            hour_values.append("report_overtime.%%temporary_crew_hours_for_day%%(%s)" % dt)
            dt = dt.adddays(1)
        roster_values = list(ROSTER_VALUES) + hour_values

        duty_iterator_where = 'duty.%is_on_duty% or duty.%is_privately_traded%'
        duty_iterator = R.iter('iterators.duty_set', where=duty_iterator_where)
        duty_iteration = R.foreach(duty_iterator, *DUTY_VALUES)
        roster_iteration = R.foreach(self.rosterIterator, duty_iteration, *roster_values)

        # if instance of carmstd.rave.Context  else is string (or something else)
        rosters, = self.context.eval(roster_iteration) if hasattr(self.context, "eval") else \
            R.eval(self.context, roster_iteration)

        ### Or using bag-interface - and in this case with a simple roster-filter (where-clause)
        # for r in R.context(self.context).bag().iterators.roster_set('report_common.%crew_id% = "16159"'):
        #     roster = list(R.eval(r, *ROSTER_VALUES))
        #     duties = [(0,)+R.eval(d,*DUTY_VALUES) for d in r.iterators.duty_set(duty_iterator_where)]
        #     rx = self.createRoster(tuple([0]+[(duties)]+roster))

        for rosterItem in rosters:
            for r in rosterItem:
                if self.crewlist is None or str(r) in self.crewlist:
                    overtimeRosters.append(self.createRoster(rosterItem))
                    break

        return overtimeRosters

    def createRoster(self, rosterItem):
        rosterItem = rosterItem[1:]

        tempCrewHoursDaily = list(rosterItem[TEMPORARY_CREW_HOURS_DAILY:])

        overtimeRoster = OvertimeRoster(
            rosterItem[DUTIES],
            rosterItem[SALARY_SYSTEM],
            rosterItem[HOME_CURRENCY],
            rosterItem[CREW_ID],
            rosterItem[FIRST_NAME],
            rosterItem[LAST_NAME],
            rosterItem[HOMEBASE],
            rosterItem[RANK],
            rosterItem[MONTH],
            rosterItem[MAIN_FUNC],
            rosterItem[IS_FULL_TIME],
            rosterItem[IS_TEMPORARY],
            rosterItem[IS_TEMPORARY_TWO_MONTHS],
            rosterItem[MAITRE_DE_CABIN_SHORT_HAUL],
            rosterItem[MAITRE_DE_CABIN_LONG_HAUL],
            rosterItem[MAITRE_DE_CABIN],
            rosterItem[SENIOR_CC_ALLOWANCE],
            rosterItem[SENIOR_CC_ALLOWANCE_NO_PURSER],
            rosterItem[LOSS_OF_REST_LOW],
            rosterItem[LOSS_OF_REST_HIGH],
            rosterItem[TEMPORARY_CREW_HOURS],
            rosterItem[ILL_TEMPORARY_CREW_HOURS],
            rosterItem[EMPNO],
            rosterItem[IS_SKD],
            rosterItem[IS_SKN],
            rosterItem[IS_SKS],
            rosterItem[IS_FC],
            rosterItem[IS_FP],
            rosterItem[SUM_OT_FD_UNITS],
            rosterItem[SUM_OT_FD_NETTO],
            rosterItem[IS_CONVERTIBLE],
            rosterItem[IS_FLIGHT_CREW],
            rosterItem[FULLTIME_DT_MONTH],
            rosterItem[EXCLUDED],
            rosterItem[IS_CC_4EXNG],
            rosterItem[IS_FC_4EXNG],
            rosterItem[INST_LCI_SH],
            rosterItem[INST_LCI_LH],
            rosterItem[SNGL_SLIP_LONGHAUL],
            tempCrewHoursDaily,
            )

        return overtimeRoster
        
class OvertimeRoster(DataClass):
    """
    A Roster item with overtime values.
    """

    def __init__(self,
                 duties,
                 salarySystem,
                 homeCurrency,
                 crewId,
                 firstName,
                 lastName,
                 homebase,
                 rank,
                 month,
                 mainFunc,
                 isFullTime,
                 isTemporary,
                 isTemporaryTwoMonths,
                 mDCShortHaul,
                 mDCLongHaul,
                 mDC,
                 sCC,
                 sCCNoPurser,
                 lossRestLow,
                 lossRestHigh,
                 tempCrewHours,
                 illTempCrewHours,
                 empNo,
                 isSKD,
                 isSKN,
                 isSKS,
                 isFC,
                 isFP,
                 sum_OT_FD_units,
                 sum_OT_FD_netto,
                 isConvertible,
                 isFlightCrew,
                 fulltimeDtMonth,
                 excluded,
                 isCC4EXNG,
                 isFC4EXNG,
                 inst_lci_sh,
                 inst_lci_lh,
                 sngl_slip_longhaul,
                 tempCrewHoursDaily,
                 ):
        

        self.salarySystem =  salarySystem
        self.homeCurrency = homeCurrency
        self.crewId = crewId
        self.firstName = firstName
        self.lastName = lastName
        self.homebase = homebase
        self.rank = rank
        self.month = month
        self.mainFunc = mainFunc
        self.empNo = empNo
        self.isSKD = isSKD
        self.isSKN = isSKN
        self.isSKS = isSKS
        self.isFC = isFC
        self.isFP = isFP

        self.isConvertible = isConvertible
        self.isFlightCrew = isFlightCrew
        self.isPartTime = not isFullTime
        self.isTemporary = isTemporary
        self.isTemporaryTwoMonths = isTemporaryTwoMonths
            
        self.mDCShortHaul = mDCShortHaul
        self.mDCLongHaul = mDCLongHaul
        self.mDC = mDC

        self.sCC = sCC
        self.sCCNoPurser = sCCNoPurser

        self.lossRestLow = lossRestLow
        self.lossRestHigh = lossRestHigh

        self.overtimeBalanced = None

        self.tempCrewHours = tempCrewHours
        self.tempCrewHoursDaily = tempCrewHoursDaily
        self.illTempCrewHours = illTempCrewHours
        self.fulltimeDtMonth = fulltimeDtMonth
        self.excluded = excluded

        self.isCC4EXNG = isCC4EXNG
        self.isFC4EXNG = isFC4EXNG

        self.inst_lci_sh = inst_lci_sh
        self.inst_lci_lh = inst_lci_lh

        self.sngl_slip_longhaul = sngl_slip_longhaul

        self.sum_OT_FD_units = sum_OT_FD_units
        self.sum_OT_FD_netto = sum_OT_FD_netto

        # Process balanced overtime
        self.overtimeBalancedContributors = None
        self.mertidContributors = []
        self.threeMonthOvertime = []
        otSolverSearchList = []
        idx = 0
        otime = None
        for dutyvalues in duties:
            if (len(dutyvalues)-1) % 4:
                raise Exception("Each balancing value needs (ot,start,stop,dutytime)")
            for i in xrange(1,len(dutyvalues)-OT_OPT_SKIP_VALUES*4,4):
                dtv = dutyvalues[i:i+3] + ((dutyvalues[i+3], i-1), )
                if dtv[0] and dtv[0] > RelTime('0:00'):
                    #print "l[%2d] = %s" % (idx, dtv)
                    idx += 1
                    otSolverSearchList.append(dtv)

        for dutyvalues in duties:
            for mertid_values in range(MT_PART_PARTTIME_CC_MONTH+1, MT_PART_PARTTIME_CC_3_MONTHS+3,4):
                mtv = dutyvalues[mertid_values:mertid_values+3] + ((dutyvalues[mertid_values+3]),(mertid_values-1), )
                # Save if there is a positive value for duty time as well as overtime
                if mtv[0] and mtv[1]:
                    if mtv[0] != RelTime('0:00'):
                        if mtv[1] != RelTime('0:00'):
                            # Filter out dates already saved
                            if not self.mertidContributors or \
                            not mtv in self.mertidContributors: 
                                self.mertidContributors.append(mtv)
                            else:
                                continue

        for dutyvalues in duties:
            for three_month_ot in range(OT_PART_PARTTIME_CC_3_MONTHS+1, OT_PART_PARTTIME_CC_3_MONTHS+3,4):
                tmo = dutyvalues[three_month_ot:three_month_ot+3] + ((dutyvalues[three_month_ot+3]),(three_month_ot-1),)
                # Save if there is a positive value for duty time as well as overtime
                if tmo[0] and tmo[1]:
                    if tmo[0] != RelTime('0:00'):
                        if tmo[1] != RelTime('0:00'):
                            # Filter out dates already saved
                            if not self.threeMonthOvertime or \
                            not tmo in self.threeMonthOvertime:
                                self.threeMonthOvertime.append(tmo)
                            else:
                                continue

        if otSolverSearchList:    
            # Changed the old functionality because it could not handle large problems (>4-5 items).
            # The new solver partitions the problem into distinct subproblems before solving. It is
            # also able to handle larger partitions without memory overflow.
            ots = OvertimeSolver()
            ots.addRange(otSolverSearchList)
            (otime, bestsol) = ots.solve()
            otime = RelTime(otime)
        
        if duties and duties[0][-4] and int(duties[0][-4]) > 0 and (not otime or duties[0][-4] > otime):
            #print "Monthly overtime wins"
            otime = duties[0][-4]
            bestsol = [[duties[0][-2], duties[0][-1], len(duties[0])-5, otime, duties[0][-3]]]
            #print "which means: ", bestsol
            self.overtimeBalancedContributors = bestsol
        elif otime:
            #print "best solution is to take: ", bestsol
            bestsol = [[otSolverSearchList[x][2], otSolverSearchList[x][3][0], otSolverSearchList[x][3][1],
                        otSolverSearchList[x][0], otSolverSearchList[x][1]] for x in bestsol]
            #print "which means: ", bestsol
            self.overtimeBalancedContributors = bestsol
        for i in xrange(OT_OPT_SKIP_VALUES-1):
            idx = -(i+2)*4
            if duties and duties[0][idx] and int(duties[0][idx]) > 0:
                if not self.overtimeBalancedContributors: self.overtimeBalancedContributors = []
                self.overtimeBalancedContributors.append([duties[0][idx+2], duties[0][idx+3], len(duties[0])+idx-1, duties[0][idx], duties[0][idx+1]])

        # Three month overtime for part time cc needs to be considered.
        # If it exists, the 'normal ot' needs to be substracted so that it's nor reported twice
        if self.threeMonthOvertime:
            count = 0
            for overtime_1, start_1, end_1, duty_1, type_1 in self.threeMonthOvertime:
                normal_ot = RelTime('0:00')
                if self.overtimeBalancedContributors:
                    for start_2, duty_2, type_2, overtime_2, end_2 in self.overtimeBalancedContributors:
                        if start_2 < end_1 and end_2 > start_1 and type_2 == OT_PART_7_CALENDARDAYS:
                            normal_ot += overtime_2
                    if overtime_1 > normal_ot:
                        overtime_1 -= normal_ot
                    else:
                        overtime_1 = RelTime('0:00')
                    # Replace three month overtime tuple with new overtime vlaue
                    self.threeMonthOvertime[count] = (overtime_1, start_1, end_1, duty_1, type_1)
                
                # The overall total overtime needs to add the 3 month part cc overtime
                if otime:
                    otime += overtime_1
                count += 1 

        self.overtimeBalanced = otime
     
    def getContributingPart(self, otType, dutyTime):
        """ Returns the part of the balancing solution that matches the otType, (any of OT_PART_XXX)
            if dutyTime is True, returns the total duty time. If False, returns the overtime. """
        if not self.overtimeBalancedContributors: return None
        
        if dutyTime:
            l = [int(x[1]) for x in self.overtimeBalancedContributors if x[2] == otType]
        else:
            l = [int(x[3]) for x in self.overtimeBalancedContributors if x[2] == otType]
        s = sum(l)
        if s > 0:
            return RelTime(s)
        return None
        
    # Salary code DK: 316, NO: 3405 
    def getMDCShortHaul(self):
        return self.mDCShortHaul

    # Salary code DK: 416, NO: 3765
    def getMDCLongHaul(self):
        return self.mDCLongHaul

    # Salary code SE: 351
    def getMDC(self):
        return self.mDC

    # Salary code DK: 317, NO: 3150
    def getSCC(self):
        return self.sCC

    # Salary code DK: 328, NO: 3412
    def getSCCNOP(self):
        return self.sCCNoPurser

    # Salary code SE: 351
    def getSCCAll(self):
        if self.sCC:
            if self.sCCNoPurser:
                return self.sCCNoPurser + self.sCC
            else:
                return self.sCC
        else:
            return self.sCCNoPurser

    # Salary code DK: 325, SE: 348, NO: 3143
    def getLossRestLow(self):
        return self.lossRestLow

    # Salary code DK: 326, NO: 3144?
    def getLossRestHigh(self):
        return self.lossRestHigh

    # Salary code DK: 409, 410   SE: 201   NO: 3770,3145   DK: 732, 733, 734
    def getOvertime(self):
        return self.overtimeBalanced

    # Salary code DK: 229 NO 6048
    def getTempCrewHours(self):
        return self.tempCrewHours
    
    def getTempCrewHoursDaily(self):
        return self.tempCrewHoursDaily
    
    # Salary code DK: 329
    def getIllTempCrewHours(self):
        return self.illTempCrewHours

    def getInstLciSh(self):
        return self.inst_lci_sh
    
    def getInstLciLh(self):
        return self.inst_lci_lh

    def getSnglSlipLonghaul(self):
        return self.sngl_slip_longhaul

    def get_OT_FD_hours100_netto(self):
        units = self.sum_OT_FD_netto
        # 1 unit == 0:30 ->
        #  0:30 -> 50, 1:00 -> 100, etc
        return units * 50

    # 'Mertid' and overtime for part time cc
    def getMertidParttimeCc(self, dutyTime=False):
        mertidDutyTime = RelTime('0:00')
        mertidOvertime = RelTime('0:00')
        mertid_cont = self.getMertidContributors()
        if mertid_cont:
            for otime, start, end, duty, otype in mertid_cont:
                if otype == MT_PART_PARTTIME_CC_MONTH:
                    mertidDutyTime += duty
                    mertidOvertime += otime
            if dutyTime:
                return mertidDutyTime
            else:
                return mertidOvertime

    def getMertidParttimeCcLong(self, dutyTime=False):
        mertidDutyTime = RelTime('0:00')
        mertidOvertime = RelTime('0:00')
        mertid_cont = self.getMertidContributors()
        if mertid_cont:
            for otime, start, end, duty, otype in mertid_cont:
                if otype == MT_PART_PARTTIME_CC_3_MONTHS:
                    mertidDutyTime += duty
                    mertidOvertime += otime
            if dutyTime:
                return mertidDutyTime
            else:
                return mertidOvertime

    def getOvertimeParttimeCc(self, dutyTime=False):
        return self.getContributingPart(OT_PART_PARTTIME_CC_MONTH, dutyTime)

    def getOvertimeParttimeCcLong(self, dutyTime=False):
        otDutyTime = RelTime('0:00')
        otOverTime = RelTime('0:00')
        ot_cont = self.getOtPartTimeCcContributors()
        if ot_cont:
            for otime, start, end, duty, otype in ot_cont:
                otDutyTime += duty
                otOverTime += otime
            if dutyTime:
                return otDutyTime
            else:
                return otOverTime

    def getOtPartTimeCcContributors(self):
        if not self.threeMonthOvertime: return None
        return self.threeMonthOvertime[:]

    def getMertidContributors(self):
        if not self.mertidContributors: return None
        return self.mertidContributors[:]

    # no Salary Code
    def getOtContributors(self, dutyTime=False):
        if not self.overtimeBalancedContributors: return None
        return self.overtimeBalancedContributors[:]

    # Salary code SE: 200 (part-time), 201 (full-time)
    def getCalendarMonth(self, dutyTime=False):
        return self.getContributingPart(OT_PART_MONTH, dutyTime)
    #Mertid
    def getCalendarMonthPartTimeExtra(self, dutyTime=False):
        return self.getContributingPart(OT_PART_PARTTIME_MONTH, dutyTime)

    # Salary code SE: 202
    def getCalendarWeek(self, dutyTime=False):
        return self.getContributingPart(OT_PART_CALENDARWEEK, False)

    def get7CalendarDays(self, dutyTime=False):
        return self.getContributingPart(OT_PART_7_CALENDARDAYS, dutyTime)
    
    # Salary code SE: 204
    def getDutyPass(self, dutyTime=False):
        return self.getContributingPart(OT_PART_DUTYPASS, dutyTime)
    
    # Salary code SE: 204
    def getLateCheckout(self):
        return self.getContributingPart(OT_PART_LATE_CHECKOUT, False)
        
    def isExcludedFromSalaryFiles(self):
        return self.excluded

    def is4ExngFCOt(self):
        return self.isFC4EXNG

    def is4ExngCCOt(self):
        return self.isCC4EXNG
    
def dutyvals(crew, *exprs):
    rosterSequence = R.foreach(
        'iterators.roster_set',
        R.foreach(
            R.iter('iterators.duty_set'),
            *exprs),
        'crew.%id%')
    
    rosters, =  R.eval('default_context', rosterSequence)
    l = []
    for r in rosters:
        if r[2] == crew:
            for d in r[1]:
                l.append(d[1:])
    return l

# constants to be used for indenting text in report
T1 = " " * 3
T2 = T1 * 2
T3 = T1 * 3
T4 = T1 * 4


def create_writeln(fd):
    def writeln(s):
        return fd.write(s + "\n")
    return writeln


def writeovertimecalc(fd, salmon, crewlist):

    om = OvertimeRosterManager('default_context', crewlist=crewlist)
    for crew in om.getOvertimeRosters():
        fd.write("Crew %s (%s %s)  %s:\n" % (crew.crewId, crew.firstName, crew.lastName, salmon))
        if crew.isExcludedFromSalaryFiles():
            fd.write("  ** Is excluded from Overtime salary file by manual filter **\n")
        fd.write(T1 + "Total overtime: %s\n" % (crew.getOvertime()))
        fd.write(T2 + "Breakdown:\n")
        cont = crew.getOtContributors()
        mertid_cont = crew.getMertidContributors()
        three_month_ot_cont = crew.getOtPartTimeCcContributors()
        is4ExngValid = crew.is4ExngFCOt() or crew.is4ExngCCOt()
        if cont or mertid_cont or three_month_ot_cont:
            if cont:
                for end, duty, otyp, otime, start in cont:
                    if is4ExngValid and otyp == OT_PART_7_CALENDARDAYS:
                        tname = "7 Calendar days"
                    elif otyp == OT_PART_CALENDARWEEK:
                        tname = "Week"
                    elif otyp == OT_PART_DUTYPASS:
                        tname = "Duty pass"
                    elif otyp == OT_PART_LATE_CHECKOUT:
                        tname = "Late C/O"
                    elif otyp == OT_PART_MONTH:
                        tname = "Monthly"
                    elif otyp == OT_PART_PARTTIME_MONTH:
                        tname = "Mertid"
                    elif otyp == OT_PART_PARTTIME_CC_MONTH:
                        tname = "Overtime part time cc single month"
                    else:
                        tname = "Other"
                    fd.write(T3 + "%s-%s (%9s) %6s (Duty: %6s)\n" % (start, end, tname, otime, duty))

            if mertid_cont:
                for otime, start, end, duty, otype in mertid_cont:
                    if otype == MT_PART_PARTTIME_CC_MONTH:
                        tname = "Mertid part time cc single month"
                    elif otype == MT_PART_PARTTIME_CC_3_MONTHS:
                        tname = "Mertid part time cc three months"
                    fd.write(T3 + "%s-%s (%9s) %6s (Duty: %6s)\n" % (start,end,tname,otime,duty))
            if three_month_ot_cont:
                for otime, start, end, duty, otype in three_month_ot_cont:
                    if otype == OT_PART_PARTTIME_CC_3_MONTHS:
                        tname = "Overtime part time cc three months"
                    fd.write(T3 + "%s-%s (%9s) %6s (Duty: %6s)\n" % (start,end,tname,otime,duty))

        else:
            fd.write(T3 + "(none)\n")
        if True:
            from utils.selctx import SingleCrewFilter
            ctx = SingleCrewFilter(crew.crewId).context()
            trips = []
            duties = []
            dutyperiods = []
            salStart = R.eval("report_overtime.%month_start%")[0]
            salEnd = R.eval("report_overtime.%month_end%")[0]
            for _, startT, endT, timeT in R.eval(ctx, R.foreach("iterators.trip_set", "trip.%start_utc%", "trip.%end_utc%", "salary_overtime.%temp_duty_time_component%"))[0]:
                if timeT and int(timeT) > 0:
                    trips.append((startT, endT, timeT))
            for _, startDP, endDP, timeDP in R.eval(ctx, R.foreach(
                    "iterators.duty_set", "duty_period.%start_utc%", "duty_period.%end_utc%", "salary_overtime.%temp_crew_hours_per_duty_period_NKF_SNK_CC%"))[0]:
                if (timeDP and int(timeDP) > 0) and (endDP >= salStart and endDP < salEnd):
                    dutyperiods.append((startDP, endDP, timeDP))
            if len(duties) > 0:
                fd.write("  Temporary crew days %s:\n")
                for startD, endD, daysD in duties:
                    fd.write("    %s-%s %s\n" %(startD, endD, daysD))
            if len(trips) > 0:
                fd.write("  Temporary crew hours:\n")
                for startT, endT, timeT in trips:
                    fd.write("    %s-%s %s\n" %(startT, endT, timeT))
            if len(dutyperiods) > 0:
                fd.write("  Temporary crew hours DP:\n")
                for startDP, endDP, timeDP in dutyperiods:
                    fd.write("    %s-%s %s\n" %(startDP, endDP, timeDP))
        fd.write(T2 + "Summary:\n")
        
        fd.write(T3 + "7 Calendar days  : %6s (%6s)\n" % (crew.get7CalendarDays(False) or RelTime(0), crew.get7CalendarDays(True) or RelTime(0)))
        fd.write(T3 + "Calendar week    : %6s (%6s)\n" % (crew.getCalendarWeek(False) or RelTime(0), crew.getCalendarWeek(True) or RelTime(0)))
        fd.write(T3 + "Duty pass        : %6s (%6s)\n" % (crew.getDutyPass(False) or RelTime(0), crew.getDutyPass(True) or RelTime(0)))
        fd.write(T3 + "Mertid part cc   : %6s/%6s (%6s/%6s)\n" % (crew.getMertidParttimeCc(False) or RelTime(0), crew.getMertidParttimeCcLong(False) or RelTime(0), crew.getMertidParttimeCc(True) or RelTime(0), crew.getMertidParttimeCcLong(True) or RelTime(0)))
        fd.write(T3 + "Overtime part cc : %6s/%6s (%6s/%6s)\n" % (crew.getOvertimeParttimeCc(False) or RelTime(0), crew.getOvertimeParttimeCcLong(False) or RelTime(0), crew.getOvertimeParttimeCc(True) or RelTime(0), crew.getOvertimeParttimeCcLong(True) or RelTime(0)))
        fd.write("\n" + T1 + "Other compensation:\n")

        showDutyValues = False
        if (crew.getTempCrewHours() or RelTime(0)) > RelTime(0):
            fd.write("    Duty (temp.crew) : %6s\n" % (crew.getTempCrewHours() or RelTime(0)))
        if (crew.getIllTempCrewHours() or RelTime(0)) > RelTime(0):
            showDutyValues = True
            fd.write("    Ill (temp.crew)  : %6s\n" % (crew.getIllTempCrewHours() or RelTime(0)))
        if (crew.getMDC() or RelTime(0)) > RelTime(0):
            fd.write("    MDC              : %6s\n" % (crew.getMDC() or RelTime(0)))
        if (crew.getMDCShortHaul() or RelTime(0)) > RelTime(0):
            fd.write("    MDC SH           : %6s\n" % (crew.getMDCShortHaul() or RelTime(0)))
        if (crew.getMDCLongHaul() or RelTime(0)) > RelTime(0):
            fd.write("    MDC LH           : %6s\n" % (crew.getMDCLongHaul() or RelTime(0)))
        if (crew.getSCC() or RelTime(0)) > RelTime(0):
            fd.write("    SCC              : %6s\n" % (crew.getSCC() or RelTime(0)))
        if (crew.getSCCNOP() or RelTime(0)) > RelTime(0):
            fd.write("    SCC (no purser)  : %6s\n" % (crew.getSCCNOP() or RelTime(0)))
        if crew.getLossRestLow() or crew.getLossRestHigh():
            showDutyValues = True
            fd.write("    Loss of rest Low : %6s\n" % (crew.getLossRestLow() or 0))
            fd.write("    Loss of rest High: %6s\n" % (crew.getLossRestHigh() or 0))
        if (crew.getInstLciSh() or RelTime(0)) > RelTime(0):
            fd.write("    Instructor LCI SH: %6s\n" % (crew.getInstLciSh() or 0))
        if (crew.getInstLciLh() or RelTime(0)) > RelTime(0):
            fd.write("    Instructor LCI LH: %6s\n" % (crew.getInstLciLh() or 0))
        
        write_overtime_after_midnight(fd, crew)

        if showDutyValues:
            for dt in dutyvals(
                    crew.crewId,
                    'duty.%start_UTC%',
                    'duty.%end_UTC%',
                    'salary_loss_of_rest.%is_loss_of_rest_high%',
                    'salary_loss_of_rest.%is_loss_of_rest_low%',
                    'salary_overtime.%temp_ill_code%'):
                if dt[1] <= R.eval("report_overtime.%month_end%")[0]:
                    if sum(bool(x) for x in dt[2:-1]) or dt[-1] != "ID00":
                        if showDutyValues:
                            fd.write("Details:\n")
                            showDutyValues = False
                        fd.write("  %s-%s: " % (dt[0], dt[1]))
                        if dt[2]: fd.write("Loss rest High ")
                        if dt[3]: fd.write("Loss rest Low ")
                        if dt[-1] != "ID00": fd.write(dt[4])
                        fd.write("\n")
        cm = TM.crew[(crew.crewId,)]
        pub = len(cm.referers("crew_publish_info", "crew"))
        if pub == 0:
            fd.write(" ** NOTE ** : There is no rescheduling information for the specified\n")
            fd.write("              crew member. Information about loss of rest and illness\n")
            fd.write("              may be wrong or missing.\n")


def write_overtime_after_midnight(fd, crew):
    if crew.sum_OT_FD_units == 0:
        return

    def comp(unit):
        """converts unit to 1.0 for DK, else 0.5"""
        return unit * 0.5 * (2 if crew.isSKD else 1)

    wln = create_writeln(fd)

    wln(T2 + """"CO after 00:00"  total netto comp: %2.2f""" % comp(crew.sum_OT_FD_netto))
    wln(T2 + "Breakdown:")

    rel_zero = RelTime('0:00')
    month_start, month_end = R.eval('salary_overtime.%month_start%', 'salary_overtime.%month_end%')

    for start, end, end_hb, otime, units, r_balance, source_str in dutyvals(
        crew.crewId,
        'duty.%start_UTC%',
        'duty.%end_UTC%',
        'duty.%end_HB%',
        "report_overtime.%OT_FD_time%",
        "report_overtime.%OT_FD_units%",
        "report_overtime.%OT_FD_F3_balance%",
        "report_overtime.%OT_FD_F3_source_str%"
    ):
        if otime != rel_zero and month_start <= start <= month_end:
            time = end - start
            wln(T3 + "%s - %s  duty: %5s, overtime: %5s,  comp: %2.2f" % (start, end, time, otime, comp(units)))

            tm_balance = 0
            query_str = "(& (crew=%s) (tim=%s) (account=F3) (source=%s))" % (
                crew.crewId, end_hb.day_floor(), source_str)
            for entry in TM.account_entry.search(query_str):
                tm_balance += entry.amount

            if tm_balance > 0:
                wln(T4 + "Replaced by F3 upon crew request")
            if tm_balance != r_balance:
                wln(T4 + "WARNING! F3 replacement update may not be saved to DB yet.")

def askSalaryPeriod(sal_start, sal_end):
    import utils.DisplayReport as display
    import Cfh

    class reportFormDatePlan(display.reportFormDate):

        def __init__(self, hdrTitle):
            display.reportFormDate.__init__(self, hdrTitle)

        def setDefaultDates(self):
            return (int(sal_start),int(sal_end))

    try: del rptForm
    except: pass
    rptForm = reportFormDatePlan('Show overtime calculation')
    rptForm.show(1)
    if rptForm.loop() == Cfh.CfhOk:
        return (AbsTime(rptForm.getStartDate()), AbsTime(rptForm.getEndDate()))
    return None


def getCompensationCalc(crewId, salaryMonthStart):
    from tempfile import mkstemp
    salaryMonthStart = AbsTime(salaryMonthStart)
    salaryMonthEnd = AbsTime(str(salaryMonthStart))
    salaryMonthEnd.addmonths(1)

    sal_start0 = R.param(conf.startparam).value()
    sal_end0 = R.param(conf.endparam).value()
    try:
        import os
        from utils.selctx import SingleCrewFilter
        R.param(conf.startparam).setvalue(salaryMonthStart)
        R.param(conf.endparam).setvalue(salaryMonthEnd)
        fd, filename = mkstemp('.txt')
        fd = os.fdopen(fd,'w')
        print SingleCrewFilter(crewId).context()
        writeovertimecalc(fd, salaryMonthStart)
        import salary.PerDiem as pd
        pd.writeperdiemcalc(fd)
        fd.close()
        fd = None
        return '\n'.join(list(file(filename, 'r')))
    finally:
        R.param(conf.startparam).setvalue(sal_start0)
        R.param(conf.endparam).setvalue(sal_end0)


def dumpovertimecalc(askDateRange, includePerDiem=True):
    import Cui
    from tempfile import mkstemp
    import os
    import carmstd.studio.cfhExtensions as ext
    crewlist = Cui.CuiGetCrew(Cui.gpc_info, Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), "MARKEDLEFT")
    sal_start0 = R.param(conf.startparam).value()
    sal_end0 = R.param(conf.endparam).value()
    if askDateRange:
        salStart = R.eval("report_overtime.%month_start%")[0]
        salEnd = AbsTime(salStart)
        salEnd = salEnd.addmonths(1)
        if salEnd > R.eval("fundamental.%pp_end%")[0] or salStart < R.eval("fundamental.%pp_start%")[0]:
            salStart = R.eval("fundamental.%pp_start%")[0]
            salEnd = AbsTime(salStart)
            salEnd = salEnd.addmonths(1)
        l = askSalaryPeriod(salStart, salEnd)
        if not l: return
        sal_start, sal_end = l
        print sal_start, sal_end
    else:
        sal_start = R.eval("report_overtime.%month_start%")[0]
        sal_end = R.eval("report_overtime.%month_end%")[0]
    
    salmon = str(AbsDate(sal_start))[2:]
    fd, filename = mkstemp('.txt')
    fd = os.fdopen(fd,'w')
    print "Saving to ", filename
    try:
        R.param(conf.startparam).setvalue(sal_start)
        R.param(conf.endparam).setvalue(sal_end)
        writeovertimecalc(fd, salmon, crewlist)
        if includePerDiem:
            import salary.PerDiem as pd
            fd.write("\nPer diem compensation:\n")
            pd.writeperdiemcalc(fd, crewlist)
        fd.close()
        fd = None
        if includePerDiem: typ = "Compensation"
        else: typ = "Overtime"
        ext.showFile(filename, "%s breakdown for salary month %s" % (typ, salmon))
    finally:
        R.param(conf.startparam).setvalue(sal_start0)
        R.param(conf.endparam).setvalue(sal_end0)
        if fd: fd.close()
        os.remove(filename)

