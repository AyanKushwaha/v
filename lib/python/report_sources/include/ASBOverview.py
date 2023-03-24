"""
 $Header$
 
 SBOverview

 Used for input to get a overview of resource availability in released schedule, it is not meant for this report to be displayed only a text version is implemented 
  
 Created:    Dec 2014
 By:         Niklas Johansson, SAS

"""

# imports
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import OutputReport
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import os
import os.path
import ast
import sys
from datetime import datetime


# constants
#CONTEXT = 'default_context'
CONTEXT = 'sp_crew_chains'
TITLE = 'SB Overview'
Total = 'Total'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8
REGION = ""
CAT = ""
SB_overview_types = ['sbactivity', 'manko', 'sick', 'resourcepool', 'overnighting', 'short_sickprognosis', 'sla', 'useable', 'morning', 'evening', 'short_sick_new', 'long_sickprognosis', 'long_sick_new', 'child_sickprognosis', 'child_sick_new', 'production', 'blank', 'ca1']
SB_intervals = {Total: [RelTime(0,0), RelTime(24,0)]
##                 '04:00-06:00': [RelTime(4,0), RelTime(6,0)],
##                 '06:00-08:00': [RelTime(6,0), RelTime(8,0)],
##                 '08:00-10:00': [RelTime(8,0), RelTime(10,0)],
##                 '10:00-12:00': [RelTime(10,0), RelTime(12,0)],
##                 '12:00-14:00': [RelTime(12,0), RelTime(14,0)],
##                 '14:00-16:00': [RelTime(14,0), RelTime(16,0)],
##                 '16:00-18:00': [RelTime(16,0), RelTime(18,0)],
##                 '18:00-20:00': [RelTime(18,0), RelTime(20,0)]
##                 '20:00-22:00': [RelTime(20,0), RelTime(22,0)],
##                 '22:00-24:00': [RelTime(22,0), RelTime(24,0)]
                }
def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatEnum(enm):
    try:
        return enm.name.split(".")[1]
    except:
        return str(enm).split(".")[1]

def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)

class ASBOverview(SASReport):
    my_region = ""
    my_cat = ""
    
    def headerRow(self, dates):
        tmpRow = self.getCalendarRow(dates,leftHeader='Rooms for',rightHeader='Tot')
        tmpCsvRow = self.getCalendarRow(dates,leftHeader='Rooms for',rightHeader='tot', csv=True)
        return tmpRow, tmpCsvRow

    def sumRow(self, data, dates):
        tmpRow = Row(border=border(top=0), font=Font(weight=BOLD))
        tmpRow.add(Text('Total', border=border(right=0)))
        tmpCsvRow = "total"
        sum = 0
        for date in dates:
            tmp = data.get(date,0)
            sum += tmp
            tmpRow.add(Text(tmp,align=RIGHT))
            tmpCsvRow += ";" + str(tmp)
        tmpRow.add(Text(sum, border=border(left=0),align=RIGHT))
        tmpCsvRow += ";"+str(sum)
        return tmpRow,tmpCsvRow

    def getRankDict(self, rank_vector):
        temp_dict_str = ""
        try:
            temp_dict_str = ("{" + rank_vector + "}")
            return ast.literal_eval(temp_dict_str)
        except ValueError:
            print "Valerr %s"  %temp_dict_str
    
    def initRetDict(self, quals_list, rank_list, overview_types, dates, planning_groups):
        retDict = {}
        for pg in planning_groups:
            retDict[pg] = retDict.get(pg, {})
            for curentDate in dates:
                retDict[pg][curentDate] = retDict[pg].get(curentDate, {})
                for qual in quals_list:
                    retDict[pg][curentDate][qual] = retDict[pg][curentDate].get(qual, {})
                    for rank in rank_list:
                        retDict[pg][curentDate][qual][rank] = retDict[pg][curentDate][qual].get(rank, {})
                        for interval in SB_intervals.keys():
                            retDict[pg][curentDate][qual][rank][interval]  = retDict[pg][curentDate][qual][rank].get(interval, {})
                            for type in overview_types:
                                retDict[pg][curentDate][qual][rank][interval][type] = retDict[pg][curentDate][qual][rank][interval].get(type, 0)
        return retDict

    def updateRetDict(self, retDict, quals_list, rank_dict, activities, ov_type, start_day, days, is_roster, planning_group):
        estr = ''
        try:
            for qual in quals_list:
                for rank, val in rank_dict.iteritems():
                    for (_,  start, end, days, _, overnighting, useable, morning_sb, ca1) in activities:
                        for interval, st_ed in SB_intervals.iteritems():
                            try:
                                addition = val
                                estr = "d:%s q:%s r:%s t:%s i:%s" %(str(start_day), qual, rank, ov_type, interval)
                                if ov_type == 'sick':    
                                    for numday in xrange(0, days):
                                        curentDate = start_day + RelTime(numday * 24, 0)
                                        retDict[planning_group][curentDate][qual][rank][interval][ov_type] = retDict[planning_group][curentDate][qual][rank][interval][ov_type] + addition
                                else:
                                    for numday in xrange(0, days):
                                        curentDate = start_day + RelTime(numday * 24, 0)
                                        cur = retDict[planning_group][curentDate][qual][rank][interval][ov_type]
                                        int_strt = curentDate + st_ed[0]
                                        int_end = curentDate + st_ed[1]
                                        if ov_type == 'manko' and not ((int_strt < end) and (int_end > start)):
                                            addition = 0
                                        if ov_type == 'sbactivity':
                                            if not (((int_end <= end) and (int_strt >= start)) or interval == 'Total'):
                                                addition = 0
                                            if overnighting:
                                                retDict[planning_group][curentDate][qual][rank][interval]['overnighting'] = retDict[planning_group][curentDate][qual][rank][interval]['overnighting'] + addition
                                            if useable:
                                                retDict[planning_group][curentDate][qual][rank][interval]['useable'] = retDict[planning_group][curentDate][qual][rank][interval]['useable'] + addition
                                                if morning_sb:
                                                    retDict[planning_group][curentDate][qual][rank][interval]['morning'] = retDict[planning_group][curentDate][qual][rank][interval]['morning'] + addition
                                                else:
                                                    retDict[planning_group][curentDate][qual][rank][interval]['evening'] = retDict[planning_group][curentDate][qual][rank][interval]['evening'] + addition
                                            if ca1:
                                                retDict[planning_group][curentDate][qual][rank][interval]['ca1'] = retDict[planning_group][curentDate][qual][rank][interval]['ca1'] + addition
                                        retDict[planning_group][curentDate][qual][rank][interval][ov_type] = cur + addition
                            except Exception as e:
                                print "Err:  d:%s q:%s r:%s t:%s i:%s e:%s" %(str(start_day), qual, rank, ov_type, interval, str(e))
            return retDict
        except:
            print "Err in update ret dict" + estr

    def updateRetDictWithProduction(self, retDict, interval, production):
        for (_, _, date, planning_group, num_assigned_fc, num_assigned_fp, num_assigned_ap, num_assigned_ah, sla_fc, sla_fp, sla_ap, sla_ah) in production:
            dateDict = retDict[planning_group][date]
            qualDict = dateDict['SH']
            qualDict['FC'][interval]['production'] = qualDict['FC'][interval].get('production', 0) + num_assigned_fc
            qualDict['FP'][interval]['production'] = qualDict['FP'][interval].get('production', 0) + num_assigned_fp
            qualDict['AP'][interval]['production'] = qualDict['AP'][interval].get('production', 0) + num_assigned_ap
            qualDict['AH'][interval]['production'] = qualDict['AH'][interval].get('production', 0) + num_assigned_ah
            qualDict['FC'][interval]['sla'] = qualDict['FC'][interval].get('sla', 0) + sla_fc
            qualDict['FP'][interval]['sla'] = qualDict['FP'][interval].get('sla', 0) + sla_fp
            qualDict['AP'][interval]['sla'] = qualDict['AP'][interval].get('sla', 0) + sla_ap
            qualDict['AH'][interval]['sla'] = qualDict['AH'][interval].get('sla', 0) + sla_ah
        return retDict
            
    def updateRetDictWithEstimatedSickness(self, retDict, interval, estimated_sickness):
        estr = ''
        for (_, estimate_for_rank) in estimated_sickness:
            for (_, planning_group, rank, qual, date, no_est_short_sick, no_short_sick, no_est_long_sick, no_long_sick, no_est_child_sick, no_child_sick, no_blank) in estimate_for_rank:
                try:
                    estr = "%s%s%s" %(rank, date, no_short_sick)
                    dateDict = retDict[planning_group][date]
                    shQualDict = None
                    qualDict = None
                    qualDict = dateDict[qual]
                    if qual == 'LH':
                        shQualDict = dateDict['SH']
                    else:
                        shQualDict = qualDict
                    if no_est_short_sick > 0:
                        shQualDict[rank][interval]['short_sickprognosis'] = shQualDict[rank][interval].get('short_sickprognosis', 0) + no_est_short_sick
                    if no_short_sick > 0:
                        shQualDict[rank][interval]['short_sick_new'] = shQualDict[rank][interval].get('short_sick_new', 0) + no_short_sick
                    if no_est_long_sick > 0:
                        shQualDict[rank][interval]['long_sickprognosis'] = shQualDict[rank][interval].get('long_sickprognosis', 0) + no_est_long_sick
                    if no_long_sick > 0:
                        shQualDict[rank][interval]['long_sick_new'] = shQualDict[rank][interval].get('long_sick_new', 0) + no_long_sick
                    if no_est_child_sick > 0:
                        shQualDict[rank][interval]['child_sickprognosis'] = shQualDict[rank][interval].get('child_sickprognosis', 0) + no_est_child_sick
                    if no_child_sick > 0:
                        shQualDict[rank][interval]['child_sick_new'] = shQualDict[rank][interval].get('child_sick_new', 0) + no_child_sick
                    if no_blank > 0:
                        shQualDict[rank][interval]['blank'] = shQualDict[rank][interval].get('blank', 0) + no_blank
                        
                except Exception as e:
                    print "Error in u est sicknes" + estr + str(e)
        return retDict
        

    def getRankList(self):
        ranks = []
        upper_cat, lower_cat = R.eval('fundamental.%upper_cat%', 'fundamental.%lower_cat%')
        ranks.append(upper_cat)
        ranks.append(lower_cat)
        return ranks

    def getTrackingRankList(self):
        return ['FC', 'FP', 'AH', 'AP']

    def getPlanningGroups(self):
        return ['SKI', 'SKN', 'SKS', 'SKD', 'SKK', 'SKJ', 'SVS', 'SZS']

    
    def getQualList(self):
        return ['SH', 'LH', 'Qual']

    def convertToDict(self, duties, estimated_sickness, production):
        # Create a dictionary to hold the values from the planning period
        #region, type, = R.eval('planning_area.%trip_planning_group%', 'planning_area.%_crew_category%')
        # Loop over all the 'bags' that comes from the RAVE expression and collect the data
        retDict = self.initRetDict(self.getQualList(), self.getTrackingRankList(), SB_overview_types, self.getDates(), self.getPlanningGroups()) 
        quals_list = None
        for (_, _, qual_vector, rank_vector, sb_overview_type, no_duties, start_day, days, is_roster, duty_planning_group, activities) in duties:
            quals_list = qual_vector.split(";")     
            ov_type = formatEnum(sb_overview_type)
            rank_dict = self.getRankDict(rank_vector)
            retDict = self.updateRetDict(retDict, quals_list, rank_dict, activities, ov_type, start_day, days, is_roster, duty_planning_group)
        retDict = self.updateRetDictWithEstimatedSickness(retDict, Total, estimated_sickness)
        retDict = self.updateRetDictWithProduction(retDict, Total, production)
        return retDict



    def timeInReportInterval(self, tmpDate):
        return True
    
    def getDates(self):
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        #pp_length = (pp_end - pp_start) / RelTime(24, 00)
        date = pp_start.day_floor()
        dates = []
        while date < pp_end:
            dates.append(date)
            date += RelTime(24,0)
        return dates
    
    def getData(self, context):
        # build rave expression
        source, days_in_pp = R.eval('report_sb_overview.%report_source_string%','fundamental.%nr_days_in_pp%')
        duty_expr = R.foreach(
            R.iter('report_sb_overview.duty_sb_overview_set', sort_by=('report_sb_overview.%duty_start_scheduled_day_in_pp%'), where=('report_sb_overview.%consider_duty_for_sb_overview_report%')),
            'report_sb_overview.%consider_duty_for_sb_overview_report%',
            'report_sb_overview.%duty_qualification_vector%',
            'report_sb_overview.%duty_rank_vector%',
            'report_sb_overview.%sb_overview_type%',
            'report_sb_overview.%no_duties%',
            'report_sb_overview.%duty_start_scheduled_day_in_pp%',
            'report_sb_overview.%duty_days_in_pp%',
            'fundamental.%is_roster%',
            'report_sb_overview.%duty_planning_group%',
            R.foreach(R.iter('iterators.duty_set', where=('report_sb_overview.%duty_starts_in_pp%')),
                   'report_sb_overview.%duty_start_scheduled_hb_in_pp%',
                   'report_sb_overview.%duty_end_scheduled_hb_in_pp%',
                   'report_sb_overview.%duty_days_in_pp%',
                   'duty.%code%',
                   'report_sb_overview.%overnighting_sb%',
                   'report_sb_overview.%sb_is_useable%',
                    'report_sb_overview.%morning_sb%',
                    'report_sb_overview.%ca1_duty_start%')
            )
        sick_expr = R.foreach(R.times(days_in_pp),
                  R.foreach(R.iter('report_sb_overview.sb_rank_overview_set'),
                            'crew.%planning_group%',
                            'report_sb_overview.%sb_rank%',
                            'report_sb_overview.%sb_crew_qualification%',
                            'report_sb_overview.%pp_date_ix%',
                            'report_sb_overview.%no_est_short_sick_on_date_ix%',
                            'report_sb_overview.%no_short_sick_on_date_ix%',
                            'report_sb_overview.%no_est_long_sick_on_date_ix%',
                            'report_sb_overview.%no_long_sick_on_date_ix%',
                            'report_sb_overview.%no_est_child_sick_on_date_ix%',
                            'report_sb_overview.%no_child_sick_on_date_ix%',
                            'report_sb_overview.%no_bl_on_date_ix%'
                            )
        )
        crew_duties, = R.eval("sp_crew", duty_expr)
        crew_est_sicknes, = R.eval("sp_crew", sick_expr)
        #crew_duties, = R.eval("default_context", duty_expr)
        crrs, = R.eval("sp_crrs", duty_expr)
        duties = crew_duties + crrs
        leg_expr = R.foreach(
            R.iter('report_sb_overview.leg_sb_overview_set', sort_by=('report_sb_overview.%leg_start_scheduled_day%'), where=('report_sb_overview.%consider_leg_for_sb_overview_report%')),
            'report_sb_overview.%consider_leg_for_sb_overview_report%',
            'report_sb_overview.%leg_start_scheduled_day%',
            'report_sb_overview.%leg_planning_group%',
            'report_sb_overview.%num_assigned_fc%',
            'report_sb_overview.%num_assigned_fp%',
            'report_sb_overview.%num_assigned_ap% ',
            'report_sb_overview.%num_assigned_ah%',
            'report_sb_overview.%sla_fc%',
            'report_sb_overview.%sla_fp%',
            'report_sb_overview.%sla_ap% ',
            'report_sb_overview.%sla_ah%')
        crew_legs, = R.eval("sp_crew", leg_expr)
        unassigned_legs, = R.eval("sp_crrs", leg_expr)
        legs = crew_legs + unassigned_legs
        #dataExists = False
        dataExists = (len(duties) > 0)
        if dataExists:
            return self.convertToDict(duties, crew_est_sicknes, legs), dataExists, source
        else:
            return {}, dataExists, source

    
    def presentData(self, stopData, outputReport, dataExists, dates, source):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)
        sp_name, _name, periodName, version, period, tracking  = R.eval('crg_info.%plan_name%','global_sp_name', 'global_fp_name', 'global_fp_version', 'crg_info.%period%', 'base_product.%is_tracking%')
        if tracking:
            _name, = R.eval('planning_area.%filter_company_p%')
        if source == "Planned" or tracking:
            periodName = version
        elif source == "DB_Planned":
            periodName = period
        name = "%s_%s" %(periodName,_name )
        #print samba_path,raw,sp_name
        self.presentRawData(stopData, dataExists, dates, sp_name, name, source, periodName)
        # self.presentNormalData(stopData, outputReport, dataExists, dates)
        # Get Planning Period start and end

    def presentSBTypesForIntervalRankQualAndDate(self, typeList, pg, date, qual, rank, interval, csvRows, sp_name, source):
        try:
            ## dateData     = stopData[station][stop][date]
            csvRows.append("\"%s\";%s;\"%s\";%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;" %(pg, formatDate(date), interval, rank, qual, str(typeList[0]), str(typeList[1]),str(typeList[10]),str(int(typeList[3])),str(typeList[4]),str(typeList[5]),str(int(round(typeList[6], 0))),str(typeList[7]),str(typeList[8]),str(typeList[9]),str(typeList[2]),str(typeList[11]),str(typeList[12]),str(typeList[13]),str(typeList[14]),str(typeList[16]),str(typeList[17])))
        except Exception as e:
            #dateData = 0
            print "No data for %s;%s;%s;%s;%s;%s" %(formatDate(date), interval, rank, qual, str(typeList), str(e))
        #csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;" %(sp_name, station, stopType, formatDate(date), str(dateData), region, type, source))

    @property
    def ResourcePoolMultiplier(self):
        return 0.66

    @property
    def SLAProductionMultiplier(self):
        return 1000

    def presentIntervalForRankQualAndDate(self, data, pg, date, qual, rank, interval, csvRows, sp_name, source):
        intervalData = data[interval]
        list = []
        #dates = typeData.keys()
        type = ""
        try:
            for type in SB_overview_types:
                if type == 'resourcepool':
                    list.append(intervalData[type]*self.ResourcePoolMultiplier)
                elif type == 'sla':
                    list.append((((intervalData[type])*1.0)/self.SLAProductionMultiplier))
                else:
                    list.append(intervalData[type])
        except Exception as e:
            print "Error pifrqd t:%s d:%s d:%s" %(type, str(intervalData), str(e))
        self.presentSBTypesForIntervalRankQualAndDate(list, pg, date, qual, rank, interval, csvRows, sp_name, source)

    def presentRankForQualAndDate(self, data, pg, date, qual, rank, csvRows, sp_name, source):
        rankData = data[rank]
        for interval in rankData.keys():
            self.presentIntervalForRankQualAndDate(rankData,  pg, date, qual, rank, interval, csvRows, sp_name, source)

    def presentQualForDate(self, data, pg, date, qual, csvRows, sp_name, source):
        qualData = data[qual]
        for rank in qualData.keys():
            self.presentRankForQualAndDate(qualData, pg, date, qual, rank, csvRows, sp_name, source)

    def presentDate(self, data, pg, date, csvRows, sp_name, source):
        dateData = data[date]
        for qual in dateData.keys():
            self.presentQualForDate(dateData, pg, date, qual, csvRows, sp_name, source)

    def presentPlanningGroup(self, data, pg, csvRows, sp_name, source):
        pgData = data[pg]
        for date in pgData.keys():
            self.presentDate(pgData, pg, date, csvRows, sp_name, source)

    def presentRawData(self, data, dataExists, dates, sp_name, name, source, periodString = ""):
        # build report
        csvRows = []
        csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;" %("planning_group", "Date", "Time", "Category", "Qualification", "Available SB:s", "manko","short_sick", "resource_pool", 'overnightting', 'short_sickprognosis', 'sla', 'useable', 'morning', 'evening', 'sick old def', 'longterm_sickprognosis','longterm_sick', 'child_sickprognosis', 'child_sick', 'blank', 'ca1' ))
        #stations = data.keys()
        samba_path = os.getenv('SAMBA', "/samba-share")
        if dataExists:
            for pg in data.keys():
                self.presentPlanningGroup(data, pg, csvRows, sp_name, source)
        else:
            csvRows.append("No trips")
        #mypath = "%s/%s/%s_%s/" %(samba_path, 'reports/SBHandling/CMSOutput/Overview', source, periodString)
        mypath = "%s/%s/" %(samba_path, 'reports/SBHandling/CMSOutput/Overview')
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        if source == "Planned":
            timeStamp = ""
        else:
            timeStamp = str(datetime.now().date())
        reportName = "SB_Overview_%s_%s-%s_%s" %(name , formatDateStr(dates[0]),formatDateStr(dates[len(dates)-1]),timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        for row in csvRows:
            csvFile.write(row + "\n")
        csvFile.close()
        self.add("The output data is saved in %s" %myFile)
    
    def create(self, reportType, context = CONTEXT, tracking = False):
        outputReport = (reportType == "output")
        #if tracking:
        #    duties,dataExists, source  = self.getTrackingData(context)
        #else:, 
        duties,dataExists, source  = self.getData(context)
        self.presentData(duties, outputReport, dataExists, self.getDates(), source)

# End of file
