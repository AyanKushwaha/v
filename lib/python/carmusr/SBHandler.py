"""
 $Header$
 
 SB Handler this 

 Lists a number of KF for all trips in
 a plan summarized by calendar day in the planning period.
 The time base is home base time
 
 Created:    February 2013
 By:         Niklas Johansson, SAS

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
import carmusr.ground_duty_handler as gdh
#from carmensystems.publisher.api import *
#from report_sources.include.SASReport import SASReport
#from report_sources.include.ReportUtils import DataCollection, OutputReport
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from Cui import CuiReloadTables
import Errlog
import Cui
import tempfile
import Csl
from subprocess import call
#import sys
import os
#import os.path
from tm import TM
from AbsTime import *
from RelTime import *
#import base64
#from datetime import datetime
#import copy


# constants =============================================================={{{1
CONTEXT = 'default_context'
CatDict = {}
BaseDict = {}
RegionDict = {}
RankDict = {}
AirpDict = {}
PlanningGroupDict = {}
#CONTEXT = 'sp_crrs'



csl = Csl.Csl()


def show_file(title, filepath):
    """
    Displays a file in a nice Studio pop-up window.
    @param title : Text to show in the window frame
    @type  title : str
    @param text  : Text to display in the window.
    @type  text  : str
    """
    csl.evalExpr('csl_show_file("%s","%s")' % (title, filepath))


def show_text(title, text):
    """
    Displays a text in a nice Studio pop-up window.
    @param title : Text to show in the window frame
    @type  title : str
    @param text  : Text to display in the window.
    @type  text  : str
    """

    fn = tempfile.mktemp()
    f = open(fn, "w")
    f.write(text)
    f.close()
    show_file(title, fn)
    os.unlink(fn)

def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatEnum(myEnum):
    try:
        tmp = str(myEnum).split(".")[1]
        return tmp
    except:
        return str(myEnum)
    
def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)

def formatDateStrLong(date):
    try:
        return str(date)
    except:
        return str(date)

def format_time(rel_time):
    if rel_time is None:
        return "void"
    else:
        return str(rel_time)


def format_string(aStr):
    if aStr is None:
        return "void"
    else:
        return "\"%s\"" %str(aStr)
    
def itrStr(lst):
    try:
        return str(lst)
    except:
        try:
            retVal = "["
            for item in lst:
                retVal+=str(item)
            retVal+="]"
            return retVal
        except:
            return "Unable to convert"

def convertDate(dateStr):
    return AbsTime(dateStr)

def convertActCode(rawActCode):
    return TM.activity_set[rawActCode]

def convertCat(rawCat):
    retVal = CatDict.get(rawCat, None)
    if not retVal:
        retVal = TM.crew_category_set[rawCat]
        CatDict[rawCat]= retVal
    return retVal

def convertBase(rawBase):
    if (len(rawBase) == 3):
        retVal = BaseDict.get(rawBase, None)
        if not retVal:
            retVal = TM.crew_base_set[rawBase]
            BaseDict[rawBase]= retVal
        return retVal
    return None

def convertAirport(rawBase):
    retVal = AirpDict.get(rawBase, None)
    if not retVal:
        retVal = TM.airport[rawBase]
        AirpDict[rawBase]= retVal
    return retVal

def convertRegion(rawRegion):
    retVal = RegionDict.get(rawRegion, None)
    if not retVal:
        retVal = TM.crew_planning_group_set[rawRegion]
        RegionDict[rawRegion]= retVal
    return retVal

def convertPlanningArea(rawPlanningGroup):
    retVal = PlanningGroupDict.get(rawPlanningGroup, None)
    if not retVal:
        retVal = TM.planning_group_set[rawPlanningGroup]
        RegionDict[rawPlanningGroup]= retVal
    return retVal

def convertRank(rawRank):
    retVal = RankDict.get(rawRank, None)
    if not retVal:
        retVal = TM.crew_rank_set[rawRank]
        RankDict[rawRank]= retVal
    return retVal
# classes ================================================================{{{1

# PairingStatsDaily----------------------------------------------------------{{{2
class SBDistributor(object):
    def __init__(self):
        self.__completeComplementDict = {'FC':0, 'FP': 1, 'FR': 2,'FU':3, 'AP': 4, 'AS': 5, 'AH': 6, 'AU': 7, 'TL': 8, 'TU': 9, 'XS': 10}
        self.dateDict = {}
        self.init()

    def init(self):
        transport, sblength, interval, apSBLength, base, upper, lower, sb_code, etab_name, sb_duty_time, sb_block_time, double_ap_sb_margin, main_cat, ac_type, = R.eval('studio_sb_handling.%sb_travel_time%',
               'studio_sb_handling.%sb_length%',
               'sb_handling.%time_interval%',
               'studio_sb_handling.%ap_sb_length%',
               'sb_handling.%sb_base%',
               'sb_handling.%upper_cat%',
               'sb_handling.%lower_cat%',
               'studio_sb_handling.%sb_code%',
               'fundamental.%sb_activity_details_p%',
               'sb_handling.%sb_default_duty_time%',
               'sb_handling.%sb_default_block_time%',
               'studio_sb_handling.%double_ap_sb_margin%',
               'fundamental.%main_cat%',
               'studio_sb_handling.%ac_type%')
        self.transportTime = transport
        self.sbLength = sblength
        self.timeInterval = interval
        self.apSBLength = apSBLength
        self.__base = base
        self.__sb_code = sb_code
        self.upper_cat = upper
        self.lower_cat = lower
        self.__complement = {upper: self.allPosDict[upper], lower: self.allPosDict[lower]}
        self.reducedStr = False
        self.sbDetailsEtabPath = "%s/%s/%s" %(os.environ['CARMDATA'], 'ETABLES', etab_name)
        Errlog.log("sbDetailsEtabPath=%s" % self.sbDetailsEtabPath)
        self.duty_time = sb_duty_time
        self.block_time = sb_block_time
        self.__double_ap_sb_margin = double_ap_sb_margin
        self.__main_cat = main_cat
        self.__ac_type = ac_type
        self.__catDict = {}
        self.__baseDict = {}
        self.__actCodeDict = {}

    @property
    def main_cat(self):
        return self.__main_cat

    @property
    def ac_type(self):
        return self.__ac_type
    @property
    def complement(self):
        return self.__complement

    @property
    def allPosDict(self):
        return self.__completeComplementDict
    
    @property
    def sb_code(self):
        return self.__sb_code
    
    @property
    def double_ap_sb_margin(self):
        return self.__double_ap_sb_margin
    
    
    @property
    def base(self):
        return self.__base
    @property
    def station(self):
        if self.base == "STO":
            return "ARN"
        return self.__base
    @property
    def categories(self):
        return self.__complement.keys()

    @property
    def timebase(self):
        return 'LDOP'

    def to_utc(self, time):
        """Return UTC time (if time is LDOP)."""
        rval = None
        if self.timebase == 'LDOP' and (time is not None):
            rval = R.eval('station_utctime("%s", %s)' % (self.station, time))[0]
        if rval is None:
            errString = "Error conv time: t: %s e:%s c:%s" %(str(time), str(self.base), str(rval))
            raise SBError(errString)
        return rval
        

    
    def __getitem__(self, date):
        return self.dateDict[date]

    def __iter__(self):
        return iter(sorted(self.dateDict.values()))

    def initiate(self, data):
        missing_critical = []
        for (_, start_date, upper_need, lower_need, maxTime, first_sb_start, _totComplement, _times, new_times, _critical, _criticalix) in data:
            
            if (not start_date in self.dateDict):
                # If it doesn't exist we create it
                try:
                    dtc = DateTimeComplement(start_date, upper_need, lower_need, maxTime, first_sb_start, self)
                    dtc.initiate(_totComplement, _times, new_times, _critical, _criticalix, missing_critical)
                    #Errlog.log("dtc created"
                    self.dateDict[start_date] = dtc
                except Exception as e:
                    Errlog.log("Error: dtc creation failed %s %s %s %s er: %s" %(str(start_date), str(upper_need), str(lower_need), str(maxTime), str(e)))
            else:
                #Errlog.log("dtc reused"
                dtc = self.dateDict[start_date]
        return missing_critical
            #Errlog.log("dtc:%s", (str(dtc))
            
    def distributeSBDays(self):
        gtp_list = []
        etabSBs = []
        for dtc in self:
            #dtc.calculateSBAssignments()
            for sba in dtc.SBAssignments:
                if sba.isActive and not sba.exists:
                    gtp_list.append(sba.gtp)
                if sba.critical:
                    etabSBs.append(sba)
        #for gtp in gtp_list:
        #    Errlog.log("%s" %str(gtp)
        self.exportSBDetailEtab(etabSBs)
        self.exportToDB(etabSBs)
        gdh.create_ground_duty_list_func(gtp_list)

    def initEtabList(self):
        etabRows = []
        etabRows.append("9")
        etabRows.append("SBase,")
        etabRows.append("SActivityCode,")
        etabRows.append("AStartTime,")
        etabRows.append("AEndTime,")
        etabRows.append("RDutyTime,")
        etabRows.append("RBlockTime,")
        etabRows.append("SSBType,")
        etabRows.append("SSBInfo,")
        etabRows.append("SSBSpecailStation,")
        return etabRows
        
    def presentRawData(self, data, etab_path):
        # build report
        etabRows = self.initEtabList()
        for sb in data:
            self.presentSBDetails(sb.station, sb.code, sb.startDateUtc, sb.endDateUtc, sb.duty_time, sb.block_time, sb.sb_type, sb.sb_info, sb.sb_specialStation, etabRows)
        csvFile = open(str(etab_path), "w")
        for row in etabRows:
            csvFile.write(row + "\n")
        csvFile.close()
        Errlog.log("The output data is saved in %s" %etab_path)



    def convertActCode(self, rawActCode):
        retVal = self.__actCodeDict.get(rawActCode, None)
        if not retVal:
            retVal = TM.activity_set[rawActCode]
            self.__actCodeDict[rawActCode]= retVal
        return retVal

    def convertToEntries(self, rawData):
        return (convertCat(rawData[0]), convertAirport(rawData[1]), self.convertActCode(rawData[2]), rawData[3],rawData[4], str(rawData[5]), rawData[6])

    def getSearchString(self, details):
        return  '(&(category=%s)(base=%s)(activity_code=%s)(sby_start=%s)(sby_end=%s)(strattribute=%s)(intattribute=%s))' %(tuple(map(str, details)))

    def storeSBinDB(self, sb):
        try:
            details = sb.ActDetails
            act_detail = None
            for tmp_detail in TM.sb_activity_details.search(self.getSearchString(details)):
                act_detail = tmp_detail
                break
            if not act_detail:
                pk = self.convertToEntries(details)
                act_detail = TM.sb_activity_details.create(pk)
            act_detail = sb.update_act_details(act_detail)
        except  Exception as e:
            print "Error for sb " + str(sb) + str(e)

    def exportToDB(self, data):
        # build report
        try:
            for sb in data:
                self.storeSBinDB(sb)
            Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
        except Exception as e:
            Errlog.log("Init attribute failed: %s" % e)

    def presentSBDetails(self, station, code, start_time, end_time, duty_time, block_time, type, sb_info, sb_specialStation, csvRows):
        try:
            csvRows.append("\"%s\", \"%s\", %s, %s, %s, %s, \"%s\",\"%s\",%s," %(station, code, formatDateStrLong(start_time), formatDateStrLong(end_time), format_time(duty_time), format_time(block_time), formatEnum(type), str(sb_info), format_string(sb_specialStation)))
        except:
            Errlog.log("No data for %s, %s, %s, %s, %s, %s, %s" %(station, code, formatDateStr(start_time), formatDateStr(end_time), duty_time, block_time, type))
            
    def exportSBDetailEtab(self, sbList):
        self.presentRawData(sbList, self.sbDetailsEtabPath)
        
    def convertCompDictToList(self, dict):
        complement = [0]*12
        for (key, item) in self.complement.items():
            complement[item] = dict[key]
        return complement
    
class DateTimeComplement(object):
    def __init__(self, date, upper_need, lower_need, maxTime, first_sb_start, sbd):
        self.__times = []
        self.__timesDict = {}
        self.__sbAssignments =  []
        self.__sbTimes = []
        self.__date = date
        self.__maxTime = maxTime
        self.__first_sb_start = first_sb_start
        self.__upper_need = upper_need
        self.__lower_need = lower_need
        self.__remain_upper_need = upper_need
        self.__remain_lower_need = lower_need
        self.__reduction = {}
        self.__upperReduction = 0
        self.__lowerReduction = 0
        self.__restUpperReduction = 0
        self.__restLowerReduction = 0
        self.__totCompl = {}
        self.__sbd = sbd
        self.__sbACalculated = False
        self.__totalNeed = {self.sbd.upper_cat:upper_need, self.sbd.lower_cat: lower_need}
        
    def initiate(self, totComplement, times, sb_times, critical, criticalIx, missing_critical):
        self.initiateTotComplement(totComplement)
        sugestedSBs = []
        try:
            self.initiateTimes(times)
        except Exception as e:
            Errlog.log("Error c TimesC:s:%s c:%s er:%s" %(str(self.date),str(times), str(e)))
        sugestedSBs.extend(self.initiateCritical(critical, missing_critical))
        sugestedSBs.extend(self.initiateCritical(criticalIx, missing_critical))
        existingSBs = [i for i in sugestedSBs if i.exists]
        prevAirportSB = None
        for sbAssignment in sorted(sugestedSBs):
            if not sbAssignment.exists:
                sbAssignment.reduceForExistingSBs(existingSBs)
            if sbAssignment.code == "A":
                if not prevAirportSB is None:
                    if (prevAirportSB.start + self.__sbd.double_ap_sb_margin) < sbAssignment.start:
                        prevAirportSB = sbAssignment
                    else:
                        sbAssignment.reduceForSB(prevAirportSB)
                else:
                    prevAirportSB = sbAssignment
            if ((self.remain_upper_need < sbAssignment.upperComp) or (self.remain_lower_need < sbAssignment.lowerComp)):
                _sbAssignment = SBAssignment(self, sbAssignment.start, sbAssignment.end, sbAssignment.code, sbAssignment.exists, sbAssignment.duty_time, sbAssignment.block_time, sbAssignment.sb_placement, sbAssignment.sb_type, sbAssignment.upperComp, sbAssignment.lowerComp, sbAssignment.critical, sbAssignment.name, sbAssignment.sb_info, sbAssignment.sb_specialStation, sbAssignment.backWardReduction, sbAssignment.priority)
                missing_critical.append(_sbAssignment)
            sbAssignment.setMaxNeed(self.remain_upper_need, self.remain_lower_need)
            self.addSBAssignment(sbAssignment, sbAssignment.backWardReduction)
        self.calculateSBAssignments(sb_times)
        
        
    def initiateTotComplement(self,_complement):
        try:
            complement = []
            for (key, item) in _complement:
                complement.append(item)
            for (key, item) in self.complement.items():
                #Errlog.log("key:%s, item:%s comp:%s" %(key, item, str(complement))
                self.__totCompl[key] = complement[item]
                totNeed = self.__totalNeed[key]
                if (totNeed == 0):
                    totNeed = 1
                self.__reduction[key] = complement[item]/totNeed
            self.__upperReduction = self.__reduction[self.sbd.upper_cat]
            self.__lowerReduction = self.__reduction[self.sbd.lower_cat]
        except Exception as e:
            Errlog.log("Error c TotC:s:%s c:%s er:%s" %(str(self.date),str(_complement), str(e)))

    def initiateCritical(self, critical, missing_critical):
        sugestedSBs = []
        #Errlog.log("init critical  %s" %str(critical)
        for (_, start_time, end_time, type, _upper, _lower, backWards, exists, duty_time, block_time, priority, sb_placement, sb_type, sb_info, sb_specialStation, latest_possible_start) in critical:
            #Errlog.log("s: %s e:%s t:%s comp %i %i" %(str(start_time), str(end_time), type, _upper, _lower))
            ## for (kx, complementNo) in _complement:
##                 complement.append(complementNo)
            try:
                #A SB will only be created if there remains a SB need on the day in question for either upper or lower
                upper = min(_upper, self.remain_upper_need)
                lower = min(_lower, self.remain_lower_need)
                sbAssignment = None
                if max(upper, lower) > 0:
                    if type != "A":
                        sb_start_time = max(min(start_time, self.maxTime), latest_possible_start)
                    else:
                        sb_start_time = start_time
                    if sb_start_time < start_time:
                        sb_end_time = max(self.maxTime, latest_possible_start) + self.sbd.sbLength
                    else:
                        sb_end_time = end_time
                    sbAssignment = SBAssignment(self, sb_start_time, sb_end_time, type, exists, duty_time, block_time, sb_placement, sb_type, upper, lower, critical = True, name = 'crit', sb_info = sb_info, sb_specialStation = sb_specialStation, backWardReduction = backWards, priority = priority)
                    sugestedSBs.append(sbAssignment)
                if ((sbAssignment is not None) and ((_upper > sbAssignment.upperComp) or (_lower > sbAssignment.lowerComp))):
                    sbAssignment = SBAssignment(self, start_time, end_time, type, exists, duty_time, block_time, sb_placement, sb_type, upper, lower, critical = True, name = 'crit', sb_info = sb_info, sb_specialStation = sb_specialStation, backWardReduction = backWards, priority = priority)
                    missing_critical.append(sbAssignment)
            except SBError as e:
                Errlog.log("Error c SB:s:%s e:%s t:%s e:%s er:%s" %(str(start_time), str(end_time), type, str(exists), str(e)))
        return sugestedSBs

    def addSBAssignment(self, sbAssignment, backWards = True):
        try:
            self.reduceForSBAssignment(sbAssignment, backWards)
            self.__sbAssignments.append(sbAssignment)
        except Exception as e:
            Errlog.log(str(e))


    def reduceForSBAssignment(self, sbAssignment, backWards = True):
##         sbAssignment.upperRestComplement += self.__restUpperReduction
##         sbAssignment.lowerRestComplement += self.__restLowerReduction
        self.sbd.reducedStr = True
        #Errlog.log("rd for sb:%s bw:%s tms: %s" %(str(sbAssignment), str(backWards), itrStr(self.__times))
        self.sbd.reducedStr = False
        reductionSet = []
        upperRed = 0
        lowerRed = 0
        self.__remain_upper_need -= sbAssignment.upperComp
        self.__remain_lower_need -= sbAssignment.lowerComp
        for tc in sorted(self.times, reverse = backWards):
            #Errlog.log("b rd for tc:%s cov:%s" %(str(tc), str(tc.isCoveredBy(sbAssignment)))
            #print "cover tc: %s cov: %s completly covered %s" %(str(tc), str(tc.isCoveredBy(sbAssignment)), str(tc.isCompletelyCovered))
            if tc.isCoveredBy(sbAssignment) and not tc.isCompletelyCovered:
                #Errlog.log("b rd for tc:%s" %(str(tc))
                reductionSet.append(tc)
                upperRed += tc.upperRestComplement
                lowerRed += tc.lowerRestComplement
        #red = max(len(reductionSet),1)
        upperRed = min(upperRed, sbAssignment.upperRestComplement)
        lowerRed = min(lowerRed, sbAssignment.lowerRestComplement)
        for tc in reductionSet:
            sbAssignment.reduceFor(tc, upperRed, lowerRed)
            #Errlog.log("a rd for tc:%s, ur:%i lr:%i" %(str(tc), upperRed, lowerRed))
            if (sbAssignment.isCompletelyReduced):
                break
        #Errlog.log("af rd for sb:%s" %(str(sbAssignment)))

    def convertToSugestedSBs(self, sb_times):
        sugestedSBs = []
        for (_, _start_time, _end_time, _complement) in sb_times:
            start = min(max(_start_time, self.minTime),  self.maxTime)
            end = start + self.sbd.sbLength
            sbAssignment = SBAssignment(self, start, end, self.sbd.sb_code, duty_time = self.sbd.duty_time, block_time = self.sbd.block_time, upper = 0, lower = 0, critical = False, name = 'calc')
            sugestedSBs.append(sbAssignment)
        return sugestedSBs

    def initiateTimes(self, times):
        for (_, start_time, end_time, _complement) in times:
            complement = []
            if start_time < self.__first_sb_start:
                start_time = self.__first_sb_start
                end_time = start_time + self.sbd.sbLength
            for (_, complementNo) in _complement:
                complement.append(complementNo)
            if (not start_time in self):
                # If it doesn't exist we create it
                tc = TimeComplement(self, start_time, end_time, complement)
                #Errlog.log("tc%sdtc%sst%scmp%s" %(str(tc),str(tc), str(start_time), str(complement)))
                self.add(tc)
            else:
                Errlog.log("should not happen")
                self + complement
        self.times.sort(reverse=True)
        #There should be no gaps in the times list all times must be created some with a zero need
        if (len(self.times)> 0):
            self.fillTimeHolesWithNoComp()
        self.times.sort(reverse=True)
            
    def fillTimeHolesWithNoComp(self):
        start = self.times[len(self.times)-1].time
        end = self.times[0].time
        time = start
        noComp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        while (time < end):
            time = time + self.sbd.timeInterval
            if not self.__timesDict.has_key(time):
                tc = TimeComplement(self, time, end, noComp)
                #Errlog.log("tc%sdtc%sst%scmp%s" %(str(tc),str(tc.SBStart()), str(time), str(noComp)))
                self.add(tc)
                
    def __lt__(self, other):
        return self.date < other.date
    
    @property
    def has_remain_need(self):
        return max(self.remain_upper_need, self.remain_lower_need) > 0
    
    @property
    def has_remain_tc_need(self):
        for tc in self.times:
            if not tc.isCompletelyCovered:
                return True
        return False
    
    @property
    def remain_upper_need(self):
        return self.__remain_upper_need
        
    @property
    def remain_lower_need(self):
        return self.__remain_lower_need
    
    @property
    def sbd(self):
        return self.__sbd
    
    @property
    def times(self):
        return self.__times
    
    @property
    def sbTimes(self):
        if (len(self.__sbTimes) <= 0):
            for tc in self.times:
                if tc.SBStart <= self.maxTime + self.sbd.timeInterval:
                    self.__sbTimes.append(tc)
        return self.__sbTimes
    @property
    def maxTime(self):
        return self.__maxTime
    
    @property
    def minTime(self):
        return self.__first_sb_start

    @property
    def upperReduction(self):
        return self.__upperReduction

    @property
    def lowerReduction(self):
        return self.__lowerReduction
    
    @property
    def SBAssignments(self):
        if (not self.__sbACalculated):
            self.calculateSBAssignments()
        #self.__sbAssignments = self.cleanSBAssignments(self.__sbAssignments)
        return self.__sbAssignments
    
    def cleanSBAssignments(self, sbs):
        sbsList = []
        oldSB = None
        for sb in sorted(sbs):
            if (oldSB is not None and sb == oldSB):
                oldSB.merge(sb)
            else:
                sbsList.append(sb)
                oldSB = sb
        return sbsList
                
    @property
    def date(self):
        return self.__date

    @property
    def weekDay(self):
        return int(self.date.time_of_week() / RelTime(24, 0))

    @property
    def station(self):
        return self.sbd.station

    @property
    def complement(self):
        return self.sbd.complement

    @property
    def totalNeed(self):
        return self.__totalNeed
    
    def calcSBNeed(self, need):
        if need < 0:
            return 0
        else:
            return min(1, need)

    def calculateForSBTimes(self, sugested_sbs, margin = 1):
        for sbAssignment in sugested_sbs:
            newSbAssignment =  sbAssignment.copyAndRecalculateComp(self.calcSBNeed(self.remain_upper_need), self.calcSBNeed(self.remain_lower_need), margin)
            #sbAssignment = SBAssignment(self, sb.SBStartForSBCreation, sb.SBCalcEndForSBCreation, self.sbd.sb_code, duty_time = self.sbd.duty_time, block_time = self.sbd.block_time, upper = self.calcSBNeed(self.remain_upper_need), lower = self.calcSBNeed(self.remain_lower_need), critical = False, name = 'calc', saftyMargin = margin)
            if newSbAssignment.hasRemainingNeed and newSbAssignment.isActive:
                self.addSBAssignment(newSbAssignment)
            if not self.has_remain_need:
                break
                
                
    def calculateSBAssignments(self, sugested_sb_times):
        self.__sbACalculated = True
        iter = 0
        sugested_sbs = self.convertToSugestedSBs(sugested_sb_times)
        while (self.has_remain_need and self.has_remain_tc_need and iter < 20):
            self.calculateForSBTimes(sugested_sbs, 1 - 0.05*iter)
            iter += 1
        if (self.has_remain_need and self.has_remain_tc_need):
            self.calculateForSBTimes(sugested_sbs, 0)
#                    if (not sbAssignment.isCompletelyReduced):
#                        break #It is not possible to cover SB assignment and additionSB assignments is unnecesary
#                if not self.has_remain_need:
#                    break

    def getTotalNeedFor(self, cat):
        try:
            if cat == self.sbd.upper_cat:
                return self.__upper_need
            elif cat == self.sbd.lower_cat:
                return self.__lower_need
            else:
                return 0
        except:
            Errlog.log("Error get need cat:%s need:%s" %(cat, str(self.totalNeed)))
            return 0

    def getTotAssignedFor(self, cat):
        tot = 0
        for sb in self.__sbAssignments:
            tot+= sb.getComplementFor(cat)
        return tot

    def getTotalCompFor(self, cat):
        try:
            return self.__totCompl[cat]
        except:
            Errlog.log("Error tc cat:%s compl:%s" %(cat, str(self.__totCompl)))
            return 0
        
    def __contains__(self, time):
        return time in self.__timesDict
        ## for tc in self.times:
##             if tc.time == time:
##                 return True
##         return False
    
    def __getitem__(self, time):
        return self.__timesDict[time]

    def __iter__(self):
        return iter(sorted(self.times))

    def add(self, tc):
        self.times.append(tc)
        self.__timesDict[tc.time] = tc

    def sort(self):
        self.times.sort()

    def __str__(self):
        try:
            return "date:%s un:%s ln:%s" %(str(self.date),str(self.remain_upper_need),str(self.remain_lower_need))
        except:
            return "date:%s, no times:%i" %(str(self.date), len(self.times))
    
    def __repr__(self):
        return self.__str__()

    def getSugestedSBDistrubution(self):
        groundTasks = []
        for sba in self.__sbAssignments:
            if sba.isActive:
                groundTasks.append(sba)
        return groundTasks

class SBError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SBAssignment(object):
    #TODO remove hardcoded 6:00
    def __init__(self, dtc, start, end, code, exists = False, duty_time = "6:00", block_time = "6:00", sb_placement = "EveryWhereSB", sb_type = "NoneType",upper = 0, lower = 0, critical = False, name = '', sb_info = "", sb_specialStation = None, saftyMargin = 1, backWardReduction = True, priority = 0):
        if (start is None or end is None):
            errString = "Error sb init: s: %s e:%s c:%s u:%sl:%s dtc:%s" %(str(start), str(end), code, str(upper), str(lower), str(dtc))
            Errlog.log(errString)
            raise SBError(errString)
        self.__dtc = dtc
        self.__critical = critical
        self.__start = start
        self.__end = end
        self.__code = code
        self.__name = name
        self.__sb_info = sb_info
        self.__sb_specialStation = sb_specialStation
        self.__exists = exists
        self.__coveredTCs = self.initTCs()
        self.__duty_time = duty_time
        self.__block_time = block_time
        self.__priority = priority
        self.__sb_placement = sb_placement
        self.__sb_type = sb_type
        self.__backWardReduction = backWardReduction
        self.recalculateComp(upper, lower, saftyMargin)

    def recalculateComp(self, upper, lower, saftyMargin):
        self.__saftyMargin = saftyMargin
        if not self.critical and (upper > 0 or lower > 0) and not self.__exists:
            upper, lower = self.calculateNeed(upper, lower)
        self.__upperComp = upper
        self.__lowerComp = lower
        self.__complement  = {}
        self.__complement[self.sbd.upper_cat] = upper
        self.__complement[self.sbd.lower_cat] = lower
        self.upperRestComplement = self.__dtc.upperReduction * upper
        self.lowerRestComplement = self.__dtc.lowerReduction * lower

    def copyAndRecalculateComp(self, upper, lower, saftyMargin):
        return SBAssignment(self.__dtc, self.__start, self.__end, self.__code, self.__exists, self.__duty_time, self.__block_time, self.__sb_placement, self.__sb_type, upper, lower, self.__critical, self.__name, self.__sb_info, self.__sb_specialStation, saftyMargin, self.__backWardReduction, self.__priority)


    def initTCs(self):
        tcs = []
        for tc in self.__dtc.times:
            if tc.isCoveredBy(self):
                tcs.append(tc)
        return tcs
    
    def calculateNeed(self, upper, lower):
        _upper = 0
        _lower = 0
        tempUpperCov = 0
        tempLowerCov = 0
        for tc in self.__coveredTCs:
            tempUpperCov += tc.upperRestComplement
            tempLowerCov += tc.lowerRestComplement
        if tempUpperCov >= (self.__dtc.upperReduction * self.saftyMargin):
            if (self.__dtc.upperReduction * self.saftyMargin) > 0:
                _upper = min(upper, int(tempUpperCov / (self.__dtc.upperReduction * self.saftyMargin)))
            else:
                _upper = upper
        if tempLowerCov >= (self.__dtc.lowerReduction * self.saftyMargin):
            if (self.__dtc.lowerReduction * self.saftyMargin) > 0:
                _lower = min(lower, int(tempLowerCov / (self.__dtc.lowerReduction * self.saftyMargin)))
            else:
                _lower = lower
## if not tc.isUpperCompletelyCovered:
##                 _upper = upper 
##             if not tc.isLowerCompletelyCovered:
##                 _lower =  lower
##             if (_lower > 0 and _upper > 0):
##                 return _upper, _lower    
        return _upper, _lower

    def reduceForExistingSBs(self, existingSBs):
        if not self.exists:
            for eSB in existingSBs:
                self.reduceForExistingSB(eSB)
                
    def reduceForExistingSB(self, existingSB):
        if not self.exists and existingSB.exists and self == existingSB:
            self.upperComp -= existingSB.upperComp
            self.lowerComp -= existingSB.lowerComp
   
    def reduceForSB(self, existingSB):
        if not self.exists:
            self.upperComp -= existingSB.upperComp
            self.lowerComp -= existingSB.lowerComp
            
    def hasRemainingNeed(self):
        #TODO should only return true if SB assignment has lower need than covered tc:s, or we will have over covered tc:s
        return self.isActive
    
    def __lt__(self, other):
        return ((self.priority < other.priority) or
                (self.start < other.start))
    
    def __gt__(self, other):
        return ((self.priority > other.priority) or
                (self.start > other.start))

    def __le__(self, other):
        return ((self.priority < other.priority) or
                (self.start <= other.start))

    def __ge__(self, other):
        return ((self.priority > other.priority) or
                (self.start >= other.start))

    def __eq__(self, other):
        return (self.station == other.station and
                self.code == other.code and
                self.sb_specialStation == other.sb_specialStation and
                self.name == other.name and
                self.start == other.start and
                self.end == other.end and
                self.priority == other.priority)
    
    def merge(self, other):
        if (self == other):
            self.upperComp += other.upperComp
            self.lowerComp += other.lowerComp
        else:
            raise SBError("Equality is required for merge")
        
    def isActiveForCat(self, cat):
        try:
            return self.__complement[cat] > 0
        except:
            Errlog.log("Error for cat:%s, com:%s" %(cat, str(self.__complement)))
            return False

    def __str__(self):
        return "sb s: %s pr: %s cp: %s ur: %i lr:%i" %(str(self.start),str(self.priority), str(self.complement), self.upperRestComplement, self.lowerRestComplement)
    
    def __repr__(self):
        return self.__str__()

    def update_act_details(self, ent):
        ent.ac_type = self.ac_type
        ent.duty_time = self.duty_time
        ent.block_time = self.block_time
        ent.sb_type = self.removeModuleName(str(self.sb_type))
        ent.sb_info = self.sb_info
        ent.special_stations = self.sb_specialStation
        return ent

    def removeModuleName(self, str):
        try:
            return str.split('.')[1]
        except:
            return str

    @property
    def ActDetails(self):
        return (self.main_cat, self.station, self.code, self.sbd.to_utc(self.start), self.sbd.to_utc(self.end), self.sb_specialStation, self.int_atr)

    @property
    def saftyMargin(self):
        #To handle round error a safty margin is needed to correct bug
        return self.__saftyMargin

    @property
    def main_cat(self):
        return self.sbd.main_cat

    @property
    def int_atr(self):
        return 1

    @property
    def ac_type(self):
        return self.sbd.ac_type

    @property
    def backWardReduction(self):
        #Each time a SB is added the need is reduced this is the direction how the reduction is done, First to Last or backwards (ie last covered interval and backwards)
        return self.__backWardReduction
    
    @property
    def isActive(self):
        for item in self.__complement.values():
            if (item > 0) and (self.startDate is not None) and (self.endDate is not None):
                return True
        return False
    
    @property
    def exists(self):
        return self.__exists

    @property
    def sb_info(self):
        return self.__sb_info

    @property
    def sb_specialStation(self):
        return self.__sb_specialStation

    @property
    def hasSpecialQual(self):
        return not (self.__sb_specialStation is None)

    @property
    def gtp(self):
        ground_task_properties = {}
        ground_task_properties['st'] = self.startDateUtc
        ground_task_properties['et'] = self.endDateUtc
        ground_task_properties['tripname'] = self.name
        ground_task_properties['airport'] = self.station
        ground_task_properties['taskcode'] = self.code
        ground_task_properties['statcode'] = False
        ground_task_properties['complement'] =  self.complement
        #A extra attribute needs to be set to be able to handle multiple activities starting at same time
        if self.hasSpecialQual:
            ground_task_properties['attr'] =  self.sb_specialStation
        return ground_task_properties

    @property
    def startDateUtc(self):
        return self.sbd.to_utc(self.startDate)

    @property
    def endDateUtc(self):
        return self.sbd.to_utc(self.endDate)

    @property
    def duty_time(self):
        return self.__duty_time

    @property
    def block_time(self):
        return self.__block_time

    @property
    def priority(self):
        return self.__priority

    @property
    def sb_placement(self):
        return self.__sb_placement

    @property
    def sb_type(self):
        return self.__sb_type

    @property
    def critical(self):
        return self.__critical
    
    @property
    def isCompletelyReduced(self):
        return (self.isUpperCompletelyReduced and self.isLowerCompletelyReduced)

    @property
    def isUpperCompletelyReduced(self):
        return self.upperRestComplement <= 0

    @property
    def isLowerCompletelyReduced(self):
        return self.lowerRestComplement <= 0
    
    @property
    def complement(self):
        return self.sbd.convertCompDictToList(self.__complement)

##     @property
##     def lowerRestComplement(self):
##         return self.__lowerRestComplement
    
##     @property
##     def upperRestComplement(self):
##         return self.__upperRestComplement
    @property
    def upperComp(self):
        return self.__upperComp
    
    @upperComp.setter
    def upperComp(self, value):
        self.__upperComp = value
        self.__complement[self.sbd.upper_cat] = self.upperComp
    
    @property
    def lowerComp(self):
        return self.__lowerComp
    
    @lowerComp.setter
    def lowerComp(self, value):
        self.__lowerComp = value
        self.__complement[self.sbd.lower_cat] = self.lowerComp


    def setMaxNeed(self, max_upper_need, max_lower_need):
        self.upperComp = max(min(self.upperComp, max_upper_need), 0)
        self.lowerComp = max(min(self.lowerComp, max_lower_need), 0)

    @property
    def station(self):
        return self.__dtc.station

    @property
    def sbd(self):
        return self.__dtc.sbd

    @property
    def code(self):
        return self.__code

    @property
    def name(self):
        return self.__name

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def startDate(self):
        try:
            return self.__dtc.date + self.start
        except:
            return self.start

    @property
    def endDate(self):
        try:
            return self.__dtc.date + self.end
        except:
            return self.end

    @property
    def startTime(self):
        return self.__start.time_of_day()

    @property
    def endTime(self):
        return self.__end.time_of_day()
    
    @property
    def hasUpperComplement(self):
        return self.__upperComp > 0
    @property
    def hasLowerComplement(self):
        return self.__lowerComp > 0
    
    def getComplementFor(self, cat):
        try:
            return self.__complement[cat]
        except:
            Errlog.log("Error comp: cat:%s pos:%i comp %s" %(cat, self.__dtc.complement[cat], str(self.complement)))
            return 0


    def reduceFor(self, tc, maxUpperRed = 999999, maxLowerRed = 999999):
        if (self.hasUpperComplement and not self.isUpperCompletelyReduced and maxUpperRed > 0):
            upperReduction = min(tc.upperRestComplement, self.upperRestComplement, maxUpperRed)
            self.upperRestComplement -= upperReduction
            tc.upperRestComplement -= upperReduction
        if (self.hasLowerComplement and not self.isLowerCompletelyReduced and maxLowerRed > 0):
            lowerReduction = min(tc.lowerRestComplement, self.lowerRestComplement, maxLowerRed)
            self.lowerRestComplement -= lowerReduction
            tc.lowerRestComplement -= lowerReduction
    
class TimeComplement(object):
    #TimeComplement is a class to handle production in a certain time period
    def __init__(self, dtc, start_time, end_time, complement):
        self.__dtc = dtc
        self.time = start_time
        #self.__sbStart = start_time
        #self.__sbEnd = end_time
        #self.time = start_time
        self.__complement = {}
        for (key, item) in self.__dtc.complement.items():
            #Errlog.log("key:%s, item:%s comp:%s" %(key, item, str(complement))
            self.__complement[key] = complement[item]
        self.__restComplement = self.__complement
        self.upperRestComplement = self.__restComplement[self.sbd.upper_cat]
        self.lowerRestComplement = self.__restComplement[self.sbd.lower_cat]
         
    def __lt__(self, other):
        return self.time < other.time

    def __add__(self, other):
        if (len(self.__complement) == len(other)):
            for (key, item) in self.sbd.complement.items:
                self.__complement[key] += other[item]

    def __str__(self):
        if self.sbd.reducedStr:
            return "tc s: %s e: %s ur: %s lr: %s" %(str(self.SBStart), str(self.SBEnd), self.upperRestComplement, self.lowerRestComplement)
        else:
            return "tc err s: %s e: %s cmp:%s ur: %s lr: %s" %(str(self.SBStart), str(self.SBEnd), str(self.complement), self.upperRestComplement, self.lowerRestComplement)
    
    def __repr__(self):
        return self.__str__()
    @property
    def sbd(self):
        return self.__dtc.sbd

    @property
    def notCoveredLowerCompl(self):
        if not self.isLowerCompletelyCovered:
            return min(self.__dtc.remain_lower_need, 1)
        return 0
    
    @property
    def notCoveredUpperCompl(self):  
        if not self.isUpperCompletelyCovered:
            return min(self.__dtc.remain_upper_need, 1)
        return 0
    
    @property
    def notCoveredComplement(self):
        upper = 0
        lower = 0
        if not self.isUpperCompletelyCovered:
            upper = 1
        if not self.isLowerCompletelyCovered:
            lower = 1
        return {self.sbd.upper_cat:upper, self.sbd.lower_cat:lower}
        
    @property
    def isCompletelyCovered(self):
        return (self.isUpperCompletelyCovered and self.isLowerCompletelyCovered)

    @property
    def isUpperCompletelyCovered(self):
        return self.upperRestComplement <= 0

    @property
    def isLowerCompletelyCovered(self):
        return self.lowerRestComplement <= 0

    ## @property
##     def lowerRestComplement(self):
##         return self.__lowerRestComplement
    
##     @property
##     def upperRestComplement(self):
##         return self.__upperRestComplement
    def isCoveredBy(self, sbAssignment):
        return sbAssignment.start <= self.SBStart and sbAssignment.end >= self.SBEnd

    @property
    def SBStartForSBCreation(self):
        return min(self.__sbStart, self.__dtc.maxTime)
    
    @property
    def SBStart(self):
        return self.__sbStart

    @property
    def SBEnd(self):
        return self.__sbEnd
    
    @property
    def SBCalcStart(self):
        return self.SBEnd - self.sbd.sbLength
    
    @property
    def SBCalcEndForSBCreation(self):
        return self.SBStartForSBCreation + self.sbd.sbLength
    
    @property
    def time(self):
        return self.__time
    
    @time.setter
    def time(self, value):
        self.__time = value
        self.__sbStart = self.__time + self.sbd.timeInterval - self.sbd.transportTime
        self.__sbEnd = self.__time - self.sbd.transportTime

    @property
    def complement(self):
        return self.sbd.convertCompDictToList(self.__complement)

    def getComplementFor(self, cat):
        try:
            return self.__complement[cat]
        except:
            Errlog.log("Error: cat:%s pos:%i comp %s" %(cat, self.sbd.complement[cat], str(self.complement)))
            return 0
    
##     def reduceFor(self, sbAssignment):
##         if !sbAssignment.isUpperCompletelyReduced:
##             self.__upperRestComplement -= sbAssignment.upperRestComplement
##         if !sbAssignment.isLowerCompletelyReduced:
##             self.__lowerRestComplement -= sbAssignment.lowerRestComplement
##         sbAssignment.reduceFor(self)
    
def getRawData(context = CONTEXT):
    #################
    ## Data collecting
    #################        

    # This report should always use home base times (Scandinavian times)
    # Therefore make sure that the time mode parameter is set accordingly
    # Also save the previous value so that it can be reset
    #tm_old, = R.eval('crg_trip.time_mode')
    #tm_hb, = R.eval('crg_basic.timemode_HB')
    #R.param('crg_trip.time_mode').setvalue(tm_hb)
    

    # The Rave API expression that gives the trip and duty values that we need
    fe = R.foreach(R.iter('studio_sb_handling.sb_alt_date_set', where=('studio_sb_handling.%consider_duty_for_sb_calculation%')),
                   'sb_handling.%duty_start_date%',
                   'sb_handling.%duty_upper_need_for_date%',
                   'sb_handling.%duty_lower_need_for_date%',
                   'studio_sb_handling.%last_possible_sb_start%',
                   'studio_sb_handling.%first_possible_sb_start%',
                   R.foreach(R.times(12),
                             'studio_sb_handling.%no_crew_assigned_for%',
                             ),
                   R.foreach(R.iter('studio_sb_handling.sb_alt_set', where=('leg.%is_flight_duty%', 'not leg.%is_standby%', 'not leg.%is_deadhead%', 'studio_sb_handling.%leg_starts_at_sb_base%')),
                   'sb_handling.%leg_start_time%',
                   'studio_sb_handling.%leg_end_time_new%',
                   R.foreach(R.times(12),
                             'studio_sb_handling.%no_crew_assigned_for%',
                             ),
                   ),
                   R.foreach(R.iter('studio_sb_handling.sb_alt_set_new', where=('leg.%is_flight_duty%', 'not leg.%is_standby%', 'not leg.%is_deadhead%', 'studio_sb_handling.%leg_starts_at_sb_base%')),
                   'studio_sb_handling.%leg_start_time_new%',
                   'studio_sb_handling.%leg_end_time_new%',
                   R.foreach(R.times(12),
                             'studio_sb_handling.%no_crew_assigned_for%',
                             ),
                   ),
                   R.foreach(R.iter('studio_sb_handling.sb_critical_alt_set', where=('studio_sb_handling.%duty_is_sb_critical%')),
                   'studio_sb_handling.%sb_start_time%',
                   'studio_sb_handling.%sb_end_time%',
                   'studio_sb_handling.%Special_sb_code%',
                   'studio_sb_handling.%Special_sb_upper_comp%',
                   'studio_sb_handling.%Special_sb_lower_comp%',
                   'studio_sb_handling.%Special_sb_from_end%',
                   'studio_sb_handling.%Special_sb_exists%',
                   'studio_sb_handling.%sb_duty_time%',
                   'studio_sb_handling.%sb_block_time%',
                   'studio_sb_handling.%Special_sb_priority%',
                   'studio_sb_handling.%sb_placement%',
                   'studio_sb_handling.%duty_special_sb_type%',
                   'studio_sb_handling.%sb_info%',
                   'studio_sb_handling.%sb_special_station%',
                   'studio_sb_handling.%latest_possible_sb_start_time%',
                   ## R.foreach(R.times(12),
##                              'studio_sb_handling.%no_creew_assigned_for%',
##                              ),
                   ),
                   R.foreach(R.times(4, where = ('studio_sb_handling.%is_sb_type_active_ix%')),
                             'studio_sb_handling.%sb_start_time_ix%',
                             'studio_sb_handling.%sb_end_time_ix%',
                             'studio_sb_handling.%Special_sb_code_ix%',
                             'studio_sb_handling.%Special_sb_upper_comp_ix%',
                             'studio_sb_handling.%Special_sb_lower_comp_ix%',
                             'studio_sb_handling.%Special_sb_from_end_ix%',
                             'studio_sb_handling.%Special_sb_exists_ix%',
                             'studio_sb_handling.%sb_duty_time_ix%',
                             'studio_sb_handling.%sb_block_time_ix%',
                             'studio_sb_handling.%Special_sb_priority_ix%',
                             'studio_sb_handling.%sb_placement_ix%',
                             'studio_sb_handling.%duty_special_sb_type_ix%',
                             'studio_sb_handling.%sb_info_ix%',
                             'studio_sb_handling.%sb_special_station_ix%',
                             'studio_sb_handling.%latest_possible_sb_start_time_ix%',
                   ),
                   )

    # Evaluate the RAVE expression
    Errlog.log("eval for context:%s" %context)
    trips, = R.eval(context, fe)
    trip_expr = R.foreach(
            R.iter('studio_sb_handling.sb_trip_length_date_set',
                   where=('studio_sb_handling.%consider_trip_for_sb_calculation%'),
                   sort_by = ('trip.%homebase%', 'trip.%start_scheduled_day%', 'trip.%days%')
                   ),
            'trip.%homebase%',
            'trip.%start_scheduled_day%',
            'trip.%days%',
            R.foreach(R.times(10, where = ('studio_sb_handling.%assigned_cat_name_ix_to_consider%')),
            'studio_sb_handling.%assigned_cat_name_ix%',
            'studio_sb_handling.%tot_no_assigned_for_pos_ix%'),
            )

    trip_lengths, = R.eval(context, trip_expr)

    return trips, trip_lengths


def getData(context = CONTEXT):
    #################
    ## Data processing
    #################
    # Master data structure
    Errlog.log("Entering getData")
    sbd = SBDistributor()
    Errlog.log("Time to initate")
    trips, trip_lengths = getRawData(context)
    missing_critical = sbd.initiate(trips)
    return sbd, trip_lengths, missing_critical
    # Iterate over the results and collect daily data

def getNeedSearchString(cat, qual, planning_group, base, sbyDate):
    return  '(&(category=%s)(crew_qual=%s)(planning_group=%s)(base=%s)(sby_date=%s))' %(cat, qual, planning_group, base, sbyDate)

def _getInfoFromCSVLine(line, separator):
    base, date, upper_need, lower_need = line.strip().split(separator)
    return base, date, upper_need, lower_need

def getInfoFromCSVLine(line):
    try:
        return _getInfoFromCSVLine(line, ',')
    except:
        return _getInfoFromCSVLine(line, ';')

def import_sb_need_to_db_from_samba(filename, cat, qual, planning_group):
    Errlog.log("Importing SB need to d-table()")
    catEnt = convertCat(cat)
    planning_groupEnt = convertPlanningArea(planning_group)
    samba_path = os.getenv('SAMBA', "/samba-share")
    filepath = "%s/reports/SBHandling/CMSInput/%s.csv" % (samba_path, filename)
    csvFile = open(filepath, "r")
    lines = 0
    newlines = 0
    oldlines = 0
#TODO: causes system crash but I think this is a system bug as the tables should be upto date
    TM.newState()
    #TM.refresh()
    sb_daily_need_table = TM.sb_daily_needs
    baseEnt = None
    for line in csvFile.readlines():
        baseEnt = None
        base, date, upper_need, lower_need = getInfoFromCSVLine(line)
        baseEnt = convertBase(base)
        if baseEnt is None:
            print "Error on line %s" %line
            continue
        sby_need_ent = None
        lines += 1
        sbyStr = getNeedSearchString(cat, qual, planning_group, base, date)
        print sbyStr
        for tmp_need in sb_daily_need_table:
            print str(tmp_need)
        for tmp_need in sb_daily_need_table.search(sbyStr):
            print str(tmp_need)
            sby_need_ent = tmp_need
            break
        if not sby_need_ent:
            newlines += 1
            sbyDate = convertDate(date)
            pk = None
            try:
                pk = (catEnt, qual, planning_groupEnt, baseEnt, sbyDate)
                Errlog.log(str(pk))
                sby_need_ent = sb_daily_need_table.create(pk)
            except Exception as e:
                print str(pk) + str(e)
        else:
            oldlines += 1
        sby_need_ent.upper = int(upper_need)
        sby_need_ent.lower = int(lower_need)
    Errlog.log("Importing SB need new %i, old %i tot %i lines to db %s" %(newlines, oldlines, lines, "niklas"))
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    Errlog.log("Importing SB need to d-table() finished OK")


def import_sb_length_to_db_from_data(data, qual, planning_group):
    try:
        planning_groupEnt = convertPlanningArea(planning_group)
        if (len(data) > 0):
            TM.newState()
            import_sb_length_to_db_from_ent(data, qual, planning_groupEnt)
            Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    except Exception as e:
        print "Unable to store sb lengths in database" + str(e)


def import_sb_length_to_db_from_ent(sb_lengths, qual, planning_groupEnt):
    for (_, base, date, days, _comp) in sb_lengths:
        for (_, rank, no_assigned) in _comp:
            insertIntoDB(base, date, days, rank, no_assigned, qual, planning_groupEnt)

def getLengthSearchString(rank, planning_group, qual, base, sbyDate, length):
    return  '(&(rank=%s)(planning_group=%s)(crew_qual=%s)(base=%s)(sby_date=%s)(length=%s))' %(rank, planning_group, qual, base, sbyDate, str(length))

def insertIntoDB(base, date, days, rank, no_assigned, qual, planning_groupEnt):
    #Errlog.log("Importing SB length to d-table() starting")
    sby_need_ent = None
    searchStr = getLengthSearchString(rank, planning_groupEnt.id, qual, base, date, days)
    for tmp_need in TM.sb_daily_lengths.search(searchStr):
        sby_need_ent = tmp_need
        break
    try:
        if not sby_need_ent:
            rankEnt = convertRank(rank)
            baseEnt = convertBase(base)
            sbyDate = convertDate(date)
            pk = (rankEnt, planning_groupEnt, qual, baseEnt, sbyDate, days)
            sby_need_ent = TM.sb_daily_lengths.create(pk)
        sby_need_ent.no_of_starts = no_assigned
    except Exception as e:
        Errlog.log("Unable to create length for %s %s %s %s %s %s %s" %(base, str(date), str(days), rank, str(no_assigned), qual, str(e)))
    #Errlog.log("Importing SB length to d-table() finished OK")



def load_sb_needtable_from_samba(cat, qual, planning_group):
    sb_need_file_str, = R.eval('sb_handling.%sb_handling_table_p%')
    Errlog.log("sb_handling.sb_handling_table_p=%s" % sb_need_file_str)
    try:
        Errlog.log("Executing external script to import SB")
        cmd = "$CARMUSR/bin/ImportSB.sh "+ sb_need_file_str
        Errlog.log("Run script %s" % cmd)
        retcode = call(cmd, shell=True)
        if retcode < 0:
            Errlog.log("Child was terminated by signal %s" % -retcode)
        else:
            Errlog.log("Child returned %s" % retcode)
    except OSError as e:
        Errlog.log("Execution failed: %s" % e)
    try:
        import_sb_need_to_db_from_samba(sb_need_file_str, cat, qual, planning_group)
    except Exception as e:
        Errlog.log("Importing SB to DB failed: %s" % e)
    Errlog.log("Calling CuiReloadTables()")
    CuiReloadTables()
    
def getAttrSearchStr(id):
    return  '(&(id=%s))' %(id)

def init_attribute_func():
    #for _tmp in TM.sb_activity_details:
    #    _tmp.remove()
    #Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    task = None
    searchStr = getAttrSearchStr('QualType')
    for tmp_attr in TM.leg_attr_set.search(searchStr):
        task = tmp_attr
        break
    try:
        if not task:
            task = TM.leg_attr_set.create(('QualType'))
        task.category = 'general'
        task.si = 'SB attribute'
        Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)
    except Exception as e:
        Errlog.log("Init attribute failed: %s" % e)

def showProblemToUser(sbAssignment):
        return "Missing assignment %s need %i/%i\n" %(str(sbAssignment))

def create_sb_ground_duty():
    try:
        #addRTToDataBase()
        Errlog.log("Entering create_sb_ground_duty")
        CuiContextLocator(Cui.CuiWhichArea, "window").reinstate()
        cat, qual, planning_group = R.eval(
               'fundamental.%main_cat%',
               'studio_sb_handling.%ac_type%',
               'planning_area.%crew_planning_group%')
        load_sb_needtable_from_samba(cat, qual, planning_group)
        Errlog.log("SP Need table loaded")
        sbd, trip_lengths, missing_critical = getData(CONTEXT)
        import_sb_length_to_db_from_data(trip_lengths, qual, planning_group)
        text = ""
        for sb in missing_critical:
            text += "%s %s-%s covering %s comp: %s:%d %s:%d\n" %(sb.code, str(sb.start), str(sb.end), sb.sb_info, sb.sbd.upper_cat, sb.upperComp, sb.sbd.lower_cat, sb.lowerComp)
        try:
            if len(text) > 0:
                show_text("Missing critical standbys", text)
        except Exception as e:
            print "failed to print non critical function so continue"
        Errlog.log("Distribute SB Days")
        TM.newState()
        sbd.distributeSBDays()

    except Exception as e:
        Errlog.log("Execution failed: %s" % e)

### End of file
