#! /usr/bin/env python

#######################################################
#
# Stand-by Report
#
# -----------------------------------------------------
# Main module for the Stand-by Report.
# -----------------------------------------------------
# Created:    2006-04-25
# By:         Carmen Systems AB, Leo Wentzel
#
# [acosta:08/045@15:01] Rewritten most of this report (See BZ 24267).
#
#######################################################

from carmensystems.publisher.api import *

import Cfh
import Cui
import Localization

from AbsTime import AbsTime
from RelTime import RelTime
from utils.rave import RaveIterator
from utils.time_util import Timer
from tm import TM
import carmensystems.rave.api as R
from Airport import Airport
from report_sources.include.SASReport import SASReport


def Black(*a, **k):
    k['colour'] = '#000000'
    return RText(*a, **k)


def BlueL(*a, **k):
    k['colour'] = '#0000ff'
    return Text(*a, **k)

def Blue(*a, **k):
    k['colour'] = '#0000ff'
    return RText(*a, **k)


def Red(*a, **k):
    k['colour'] = '#ff0000'
    return RText(*a, **k)


def EmptyCol(*a, **k):
    """Empty column."""
    k['width'] = 40
    return Column(*a, **k)


def H1(*a, **k):
    """Header text 1."""
    k['align'] = CENTER
    k['font'] = Font(weight=BOLD)
    return Text(*a, **k)


def DayRow(*a, **k):
    k['background'] = '#cdcdcd'
    k['border'] = border(bottom=1, top=1)
    k['font'] = Font(size=9, style=ITALIC)
    return Row(*a, **k)


def RText(*a, **k):
    k['align'] = RIGHT
    return Text(*a, **k)


def THRow(*a, **k):
    k['border'] = border(bottom=1)
    k['font'] = Font(style=ITALIC)
    return Row(*a, **k)


def TRow(*a, **k):
    k['font'] = Font(size=7)
    return Row(*a, **k)


class DateSelectionBox(Cfh.Box):
    def __init__(self, title):
        Cfh.Box.__init__(self, 'DATE_SELECTION_BOX', title)
        today = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, '', 'round_down(station_localtime("CPH", fundamental.%now%), 24:00)')

        self._st_txt = Cfh.Label(self, 'L_START_DATE', Localization.MSGR('Start date'))
        self._st_txt.setLoc(Cfh.CfhLoc(1, 0))

        self._et_txt = Cfh.Label(self, 'L_END_DATE', Localization.MSGR('End date'))
        self._et_txt.setLoc(Cfh.CfhLoc(2, 0))

        self._start_date = Cfh.Date(self, 'START_DATE', today)
        self._start_date.setLoc(Cfh.CfhLoc(1, 8))

        self._end_date = Cfh.Date(self, 'END_DATE', today)
        self._end_date.setLoc(Cfh.CfhLoc(2, 8))

        self._st_tz = Cfh.Label(self, 'L_START_TZ', Localization.MSGR('CET'))
        self._st_tz.setLoc(Cfh.CfhLoc(1, 20))

        self._et_tz = Cfh.Label(self, 'L_END_TZ', Localization.MSGR('CET'))
        self._et_tz.setLoc(Cfh.CfhLoc(2, 20))

        self._ok = Cfh.Done(self, "OK")
        self._ok.setText(Localization.MSGR("OK"))
        self._ok.setMnemonic(Localization.MSGR("_OK"))

        self._cancel = Cfh.Cancel(self, "Cancel")
        self._cancel.setText(Localization.MSGR("Cancel"))
        self._cancel.setMnemonic(Localization.MSGR("_Cancel"))

        self.build()
        self.show(True)
        self._choice = self.loop()

    def __nonzero__(self):
        return self._choice == Cfh.CfhOk

    @property
    def start_date(self):
        return AbsTime(self._start_date.valof())

    @property
    def end_date(self):
        return AbsTime(self._end_date.valof()) + RelTime(24, 0)


class StandbySummaryReport(SASReport):

    def create(self):
        SASReport.create(self, 'Standby Summary Report', orientation=LANDSCAPE, showPlanData=False, headers=True)

        col_width = 120
        col_space = 40
        
        # String "12314144" which is an integer repr of AbsTime
        context = self.arg('CONTEXT')
        sday = int(self.arg('START')) / 1440
        eday = int(self.arg('END')) / 1440
        
        if context == 'default_context':
            crewInWindow = Cui.CuiGetCrew(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')

        for day in xrange(sday, eday):
            # Day is in scandinavian time. Need it in UTC to compare with table values.
            sday_text = str(AbsTime(day*1440)).split()[0]
            day, = R.eval('station_utctime("CPH", %s)' % str(AbsTime(day*1440)))
            s = day
            e = day.adddays(1)
            
            self.add(Row(
                Column(H1("Standby Summary by Base , AC Qualification and Rank"), width=col_width, colspan=7),
                EmptyCol(),
                Column(H1("Standby Summary"), width=col_width, colspan=2),
                EmptyCol()
            ))
            
            self.sb_table = Column(DayRow(Column(H1(sday_text), colspan=7)))
            self.sbs_table = Column(DayRow(Column(H1(sday_text), colspan=2)))   
                        
            self.sb_table.add(THRow('Category', 'Base', 'Standbys', 'AC Qualification', 'AC Qual Standbys', 'Rank', ' Rank Standbys'))
            self.sbs_table.add(THRow('Category', 'Standbys'))
            
            #Get all data that is necessary for the report
            self.sbyDict = {'sby_morning_sh' : [{}],
                               'sby_evening_sh' : [{}],
                               'sby_morning_lh' : [{}],
                               'sby_evening_lh' : [{}],
                               'sby_morning_ap' : [{}],
                               'sby_evening_ap' : [{}]
                               }
            #Get all data from the tables
            TM.loadTables(["crew_qualification_set"])
            acqual_set = TM.table("crew_qualification_set")
            ac_quals = []
            shortHaul = []        
            for ac in acqual_set:
                if ac.typ == "ACQUAL":
                    if ac.subtype in ["AL","A3","A4","A5"]:
                        ac_quals.append(ac)
                    else:
                        shortHaul.append(ac)
            ac_quals.extend(shortHaul)
            
            crewSelected = {}
            #The ac_quals is sorted so the long haul flights are first
            for ac in ac_quals:
                crewRank = []
                morningType = "morning"
                eveningType = "evening"
                if ac.subtype in ["AL","A3","A4","A5"]:
                    haulType = "LH"
                else:
                    haulType = "SH"
                #All crew that has an ac qual is saved in the crewIterator        
                crewIterator = ac.referers("crew_qualification", "qual")
                for crewAcQual in crewIterator:
                    #Does the crew exist in the window
                    if context == 'default_context' and not crewAcQual.crew.id in crewInWindow:
                        continue
                    #Collect crew rank
                    for crew in crewAcQual.crew.referers("crew_employment","crew"):
                        crew_base = Airport(crew.base.airport.id)
                        if crew_base.getUTCTime(crew.validfrom) < e and\
                           crew_base.getUTCTime(crew.validto) > s:
                            crewRank = crew.crewrank.id
               
                    crewAcQualValidFrom = crew_base.getUTCTime(crewAcQual.validfrom)
                    crewAcQualValidTo = crew_base.getUTCTime(crewAcQual.validto)
                    # Collect all crew that has valid ac qualification in the present period
                    if crewAcQualValidFrom < e and crewAcQualValidTo > s:
                        #All crew that has a valid ac qual and has a crew activity is of interset and stored in crew_activities
                        crew_activities = crewAcQual.crew.referers("crew_activity", "crew") 
                        for activity in crew_activities:
                            try:
                                if activity.activity.grp.cat.id == "SBY":
                                    airport = Airport(activity.adep.id)
                                    st_local = airport.getLocalTime(activity.st)
                                    #All standbys are of interest
                                    if activity.st < e and activity.et > s:
                                        if activity.st <= crewAcQualValidTo and activity.et >= crewAcQualValidFrom:
                                            crewSelected[crewAcQual.crew.id] = crewSelected.setdefault(crewAcQual.crew.id,0) + 1
                                            if crewSelected[crewAcQual.crew.id] > 1:
                                                continue
                                            sbyType=haulType
                                            if activity.activity.grp.id == "SBA":
                                                sbyType = "Airport Standby"
                                            if st_local.time_of_day() < RelTime('13:00'):
                                                dayType = morningType
                                            else:
                                                dayType = eveningType
                                            if sbyType == "Airport Standby":
                                                if dayType == morningType:
                                                    self.collectBaseACandRank(self.sbyDict, 'sby_morning_ap', activity, ac, crewRank)                                                         
                                                else:
                                                    self.collectBaseACandRank(self.sbyDict, 'sby_evening_ap', activity, ac, crewRank)
                                            else:
                                                if haulType == "SH":
                                                    if dayType == morningType:
                                                        self.collectBaseACandRank(self.sbyDict, 'sby_morning_sh', activity, ac, crewRank)
                                                    else:
                                                        self.collectBaseACandRank(self.sbyDict, 'sby_evening_sh', activity, ac, crewRank)
                                                else:
                                                    if dayType == morningType:
                                                        self.collectBaseACandRank(self.sbyDict, 'sby_morning_lh', activity, ac, crewRank)
                                                    else:
                                                        self.collectBaseACandRank(self.sbyDict, 'sby_evening_lh', activity, ac, crewRank)
                            except:
                                pass

            total_standby = 0
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_morning_sh', 'Morning short haul standbys:')
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_evening_sh', 'Evening short haul standbys:')
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_morning_lh', 'Morning long haul standbys:')
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_evening_lh', 'Evening long haul standbys:')
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_morning_ap', 'Morning airport standbys:')
            self.writeTableDataToPDFFile(self.sb_table, self.sbyDict, 'sby_evening_ap', 'Evening airport standbys:')
            self.sb_table.add(TRow("", "", "","","","","", border=border(top=1)))
            #Write to summary table
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_morning_sh', 'Morning short haul standbys:')
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_evening_sh', 'Evening short haul standbys:')
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_morning_lh', 'Morning long haul standbys:')
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_evening_lh', 'Evening long haul standbys:')
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_morning_ap', 'Morning airport standbys:')
            total_standby += self.writeSummaryTableToPDFFile(self.sbs_table, self.sbyDict, 'sby_evening_ap', 'Evening airport standbys:')
            self.sbs_table.add(TRow("Total Standby's:", Blue('%s' % total_standby), border=border(top=1)))
            
            self.add(Row(self.sb_table, EmptyCol(), self.sbs_table, EmptyCol()))#, self.sbs_table))
            self.add(Row(Column(colspan=5), height=40))
            self.page()
    
    #Get the dictionary in order to find the special crew at station, acqual and rank
    def collectBaseACandRank(self, sbyDict, key, activity, ac, crewRank):
        
        for typeList in sbyDict[key]:
            #Look for base key
            if typeList.has_key(activity.adep.id):
               pass 
            else:
                typeList[activity.adep.id] = [[],{}]
            #Add base specific data like ac qual and rank
            for baseList in typeList[activity.adep.id]:
                if baseList.__class__ == list:
                    if baseList.count(activity) < 1:
                        baseList.append(activity)
                else:
                    if baseList.has_key(ac.subtype):
                        pass
                    else:
                        baseList[ac.subtype] = [[],{}]
                    #add the rank data    
                    for acqual in baseList[ac.subtype]:
                        if acqual.__class__ == list:
                            acqual.append(activity)
                        else:
                            if acqual.has_key(crewRank):
                                pass
                            else:
                                acqual[crewRank] = []
                            #Add rank
                            acqual[crewRank].append(activity)
                        
        
                
    #The pdf specific text is written here
    def writeTableDataToPDFFile(self, table, sbyDict, key, text, summary=False):
        total_standby = 0
        #print to the different tables
        for baselist in sbyDict[key]:            
            for base in baselist.keys():
                for basedata in baselist[base]:
                    if basedata.__class__ == list:
                        #print "Base : %s ..... %s" %(base, len(basedata))
                        baseStandby = len(basedata)
                    else:   
                        ACQualStandby = ""
                        noACQualStandby = ""
                        rankStandby = ""
                        noRankStandby = ""
                        for acquallist in basedata.keys():
                            for acqual in basedata[acquallist]:
                                rank_dict = {'FC':None,'FP':None,'FR':None,'FU':None,'AP':None, 'AS':None, 'AH':None, 'AU':None,'TL':None,'TR':None}
                                if acqual.__class__ == list:
                                    #print "Base: %s ... AC qualification: %s ... standbys: %s" %(base,acquallist, len(acqual))
                                    ACQualStandby += "%s//" % acquallist
                                    noACQualStandby += "%s//" % len(acqual)
                                else:
                                    for rank in acqual.keys():
                                        rank_dict[rank] = "%s" % len(acqual[rank])
                                        #print "The rank of the above are: %s ..... %s" %(rank, len(acqual[rank]))
                                    for pos in ['FC','FP','FR','FU','AP', 'AS', 'AH', 'AU','TL','TR']:
                                        if rank_dict[pos] is not None:
                                            rankStandby += '%s/' % pos
                                            noRankStandby += "%s/" % rank_dict[pos]
                                        
                            #Add a delimeter between the different AQ qual's crew
                            rankStandby += '/' 
                            noRankStandby += '/'
                        #Fix the string so the delimeters are deleted at the end of the string
                        ACQualStandby = ACQualStandby[:ACQualStandby.rfind('//')]
                        noACQualStandby = noACQualStandby[:noACQualStandby.rfind('//')]
                        rankStandby = rankStandby[:rankStandby.rfind('//')]
                        noRankStandby = noRankStandby[:noRankStandby.rfind('//')]

                        ACQualStandby = ACQualStandby.replace('//','  ')
                        noACQualStandby = noACQualStandby.replace('//','  ')
                        rankStandby = rankStandby.replace('//','  ')
                        noRankStandby = noRankStandby.replace('//','  ')
                        table.add(TRow(text, base, Blue('%s' % baseStandby), ACQualStandby, BlueL('%s' % noACQualStandby), rankStandby, BlueL('%s' % noRankStandby)))
                        
    def writeSummaryTableToPDFFile(self, table, sbyDict, key, text):
        #print to the different tables
        total_Standby = 0
        for baselist in sbyDict[key]:            
            for base in baselist.keys():
                for basedata in baselist[base]:
                    if basedata.__class__ == list:
                        total_Standby += len(basedata)
        table.add(TRow(text, Blue('%s' % total_Standby)))
        return total_Standby
                    

def runReport(context):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    crewInWindow = None
    dsb = DateSelectionBox('Standby Summary Report')
    
    if context == 'default_context':
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
        #Put all crew that has a standby in the scriptbuffer
        crewInWindow = Cui.CuiGetCrew(Cui.gpc_info, area, 'WINDOW')
        Cui.CuiClearArea(Cui.gpc_info, Cui.CuiScriptBuffer)       
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, crewInWindow)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')

    if dsb:
        args = 'START=%d END=%d CONTEXT=%s' % (int(dsb.start_date), int(dsb.end_date), context)
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, 'window', '../lib/python/report_sources/include/StandbySummaryReport.py', 0, args)


if __name__ == '__main__':
    runReport()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
