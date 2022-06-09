#! /usr/bin/env python

#
"""
Handover Report is used for creating a Handover Report linked
to a specific Selection of Main Category, Long/Shorthaul,
Region and Tracking/Mainteinance.
"""
########################################################################
#
# Handover Report
#
# -----------------------------------------------------
# Main module for the Handover Report.
# -----------------------------------------------------
# Created:    2008-03-01
# By:         Carmen Systems AB, Hugo Vazquez
#
# Major changes: 2008-11-24 Includes: bases, AC qualification and ranks.
# By:         Jeppesen Systems AB, A. Salvador
#
########################################################################

import carmensystems.rave.api as R
import carmensystems.publisher.api as p
from report_sources.include.SASReport import SASReport
from tm import TM
from utils.rave import RaveIterator

from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime

import Cui
import Localization

import time
from Airport import Airport

now = None

def setNow():
    global now
    now, = R.eval('fundamental.%now%')

#########################################################################
#
# PRT formatting functions
#
#########################################################################
   
def H1(*a, **k):
    """Header text level 1: size 11, bold, space above."""
    k['font'] = p.Font(size=11, weight=p.BOLD)
    # Add some space on top and bottom of the header.
    k['padding'] = p.padding(2, 12, 2, 8)
    return p.Text(*a, **k)


def H2(*a, **k):
    """Header text level 2: size 8 bold."""
    k['font'] = p.Font(size=8, weight=p.BOLD)
    return p.Text(*a, **k)

def H2R(*a, **k):
    """Header text level 2: size 8 bold
       aligned to the LEFT and with border
       in the RIGHT"""
    k['align'] = p.LEFT
    k['border'] = p.border(right=1)
    return H2(*a, **k)

def H2L(*a, **k):
    """Header text level 2: size 8 bold
       aligned to the RIGHT and with border
       in the LEFT"""
    k['align'] = p.RIGHT
    k['border'] = p.border(left=1)
    return H2(*a, **k)

def SmallText(*a, **k):
    """ text size 7"""
    k['font'] = p.Font(size=7)
    return p.Text(*a, **k)

def BCText(*a, **k):
    """Text aligned CENTER and BOLD"""
    k['align'] = p.CENTER
    return BText(*a, **k)

def TextLI(*a, **k):
    """left padding text italic"""
    k['padding'] = p.padding(30, 0, 0, 0)
    k['font'] = p.Font(size=9, style=p.ITALIC)
    return p.Text(*a, **k)

    
def ColH2(text, width):
    return p.Column(H2(text, width=width), width=width)

def ColText(text, width):
    return p.Column(p.Text(text, width=width), width=width)


def BText(*a, **k):
    """Bold text."""
    k['font'] = p.Font(weight=p.BOLD)
    return p.Text(*a, **k)

def RowSpacer(*a, **k):
    """An empty row of height 6."""
    k['height'] = 6
    return p.Row(*a, **k)

def PeriodRow(*a, **k):
    k['background'] = '#cdcdcd'
    k['border'] = p.border(bottom=1, top=1)
    k['font'] = p.Font(size=9, style=p.ITALIC)
    return p.Row(*a, **k)

def PeriodSubRow(*a, **k):
    k['border'] = p.border(bottom=1)
    k['font'] = p.Font(style=p.ITALIC)
    return p.Row(*a, **k)

def TableRow(*a, **k):
    k['background'] = '#cdcdcd'
    k['font'] = p.Font(size=6, weight=p.BOLD)
    return p.Row(*a, **k)

def ColumnSpacer(*a, **k):
    """An empty column of width 15"""
    k['width'] = 15
    return p.Column(*a, **k)

def TRow(*a, **k):
    k['font'] = p.Font(size=7)
    return p.Row(*a, **k)

def BlueL(*a, **k):
    k['colour'] = '#0000ff'
    return p.Text(*a, **k)

def Blue(*a, **k):
    k['colour'] = '#0000ff'
    return RText(*a, **k)

def RText(*a, **k):
    k['align'] = p.RIGHT
    return p.Text(*a, **k)

def EmptyCol(*a, **k):
    """Empty column of width 40"""
    k['width'] = 40
    return p.Column(*a, **k)

def DayRow(*a, **k):
    k['background'] = '#cdcdcd'
    k['border'] = p.border(bottom=1, top=1)
    k['font'] = p.Font(size=9, style=p.ITALIC)
    return p.Row(*a, **k)

##def TextPatch(*a, **k):
##    """A text added many times to every section for solving
##       a little problem with alignment in columns in PRT"""
##    k['rowspan'] = 1
##    k['padding'] = p.padding(0, 0, 0, 0)
##    k['background'] = "#cdcdcd"
##    return p.Text(*a, **k)



#########################################################################
#
# List of crew ids which match the current selection
# from the Handover Form.
#
#########################################################################

class Crew:
    """ class for storing information for every crew"""
    def __init__(self,id,empno,firstname,surname,login_name):
        self.id = id
        self.empno = empno
        self.firstname = firstname
        self.surname = surname
        self.login_name = login_name
        self.name = '%s, %s' % (surname,firstname)

    def __cmp__(self, other):
        """
        Compares two crew so that crew list may be sorted.
        """
        cmpSurname = cmp(self.surname, other.surname)
        if cmpSurname == 0:
            cmpFirstname = cmp(self.firstname, other.firstname)
            if cmpFirstname == 0:
                return cmp(self.empno, other.empno)
            return cmpFirstname
        return cmpSurname

    def __eq__(self, other):
        """
        Checks if two crew are equal.
        """
        if (self.id == other.id
            and self.empno == other.empno
            and self.firstname == other.firstname
            and self.surname == other.surname):
            return True
        return False

def getCrewList(region,category,haul):
    """
    This function returns the list of crew which match the selection
    from the Handover Form: Main category, Region, Long/Shorthaul
    """
    crewList = []
    crewDict = {}
    
    region_where = 'report_handover.%%region%% = "%s"' % region

    crewListIter, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.roster_set',
               where=('report_handover.%%category%%("%s")' % category,
                      region_where,
                      'report_handover.%%haul%%("%s")' % haul,
                      )),
        'report_handover.%crew_id%',
        'report_handover.%crew_empno%',
        'report_handover.%crew_firstname%',
        'report_handover.%crew_surname%',
        'report_handover.%crew_login_name%'))

    for (ix, id, empno, firstname, surname, login_name) in crewListIter:
        c = Crew(id, empno, firstname, surname, login_name)
        crewList.append(c)
        crewDict[id] = c

    crewList.sort()

    return crewList, crewDict



#########################################################################
#
# Handover Report Class
#
#########################################################################

class HandoverReport(SASReport):

    def create(self):
        """
        Creates a Handover Report with the following information:
         - Summary of the available standbys
         - Summary of the pairings in open time
         - Summary of publication/notification alerts
         - Summary of ill crew that should report back the current day.
        """
       
        region = self.arg('REGION')
        category = self.arg('CATEGORY')
        haul = self.arg('HAUL')
        avvDisp = self.arg('AVVDISP')
        numDays = int(self.arg('NUMDAYS'))

        setNow()

        crewList = []
        crewDict = {}

        crewList, crewDict = getCrewList(region,category,haul)

        SASReport.create(self, 'Handover Report', showPlanData=False)

        # header selection from the Handover Form
        self.add(p.Row(
            p.Column(
            RowSpacer(),
            p.Isolate(p.Row(ColumnSpacer(),
                            handoverSelectionBox(region,category,haul,
                                                 avvDisp,numDays))))))
        if len(crewList)>0:
            for day in xrange(numDays+1):
                d_start_utc, = R.eval('station_utctime("CPH", round_down(station_localtime("CPH", fundamental.%now%), 24:00) + 24:00*' + str(day) + ')')
                d_end_utc, = R.eval('station_utctime("CPH", round_down(station_localtime("CPH", fundamental.%now%), 24:00) + 24:00*' + str(day + 1) + ')')
                if now > d_start_utc:
                    fromDate = now
                    toDate = d_end_utc
                else:
                    fromDate = d_start_utc
                    toDate = d_end_utc

                freeTextSection(self, region, category, haul,
                                avvDisp, fromDate, toDate)
                sby_summ = standbySection(self, region, category, haul, fromDate, toDate)
                blankDaysSection(self, region, category, haul, fromDate, toDate, sby_summ)
                openTripSection(self, region, category, haul, fromDate, toDate)
                illCrewSection(self, crewDict, fromDate, toDate)
                notificationSection(self, crewList, crewDict, fromDate, toDate)
                if not (numDays == 0 or day == numDays): self.newpage()
        else:
            self.add(p.Row(H1("No crew matches the selection:")))
            self.add(p.Row(H1("  Region: %s" % region)))
            self.add(p.Row(H1("  Category: %s" % category)))
            self.add(p.Row(H1("  Long/Shorthaul: %s" % haul)))

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
        if total_Standby <> 0:
            table.add(TRow(text, Blue('%s' % total_Standby)))
        return total_Standby

#########################################################################
#
# Header: Information about the selection from the Handover Form
#
#########################################################################
        

def handoverSelectionBox(*arg):
    """
    Creates an information box about selection from the
    Handover form.
    arg0 region (SKS,SKD,SKN,SKI)
    arg1 category (FC,CC,BOTH)
    arg2 haul (LONG,SHORT,BOTH)
    arg3 Tracking, Maintenance or both
    arg4 valid to date
    """

    arg_region = arg[0]
    if arg[1] == 'CC': category = 'CABIN CREW'
    elif arg[1] == 'FC': category = 'FLIGHT DECK'
    else: category = 'ALL CREW'

    if arg[2].startswith('SHORT'): haul = 'SHORTHAUL'
    elif arg[2].startswith('LONG'): haul = 'LONGHAUL'
    else: haul = 'BOTH'

    numDays = arg[4]
    p_end_utc, = R.eval('station_utctime("CPH", round_down(station_localtime("CPH", fundamental.%now%), 24:00) + 24:00*' + str(numDays+1) + ')')
    validTo = formatDate(p_end_utc)
    
    infoBox = p.Column(
        p.Row(p.Text('Handover Settings',
                     font=p.Font(size=9, weight=p.BOLD),
                     background='#cdcdcd',
                     align=p.CENTER,
                     colspan=2)),
        p.Row(BText('Region:'),
              p.Text(arg_region)),
        p.Row(BText('Main Category:'),
              p.Text(category)),
        p.Row(BText('Long/Shorthaul:'),
              p.Text(arg[2])),
        p.Row(BText('Tracking/Maintenance:'),
              p.Text(arg[3])),
        p.Row(BText('Report Run Time:'),
              p.Text(formatDate(now))),
        p.Row(BText('Report Period:'),
              p.Text("%s - %s" % (formatDate(now),
                                  formatDate(validTo)))),
        p.Row(p.Text('All times in UTC!',
                     colspan=2,
                     font=p.Font(weight=p.BOLD),
                     align=p.CENTER)),
        width=100,
        border=p.border_frame(1,colour="#ababab"))

    return infoBox

#########################################################################
#
# SECTION 1): Free Texts from the Handover tables in DB
#
#########################################################################

def freeTextSection(self, region, category, haul, avvDisp, fromDate, toDate): 
    """
    The free text messages included in the Handover Report are
    the ones matching the criteria specified in the Settings
    section in the Handover Report Form.
    """
    self.add(p.Isolate(H1('Free Text Messages %s - %s' \
                          % (formatDate(fromDate),
                             formatDate(toDate)))))

    catStr = '|(main_category=ALL)'
    if category=='ALL':
        catStr += '(main_category=CC)(main_category=FC)'
    else:
        catStr += '(main_category=%s)' % category

    haulStr = '|(long_short_haul=BOTH)'
    if haul == 'BOTH':
        haulStr += '(long_short_haul=LONG)(long_short_haul=SHORT)' 
    else:
        haulStr += '(long_short_haul=%s)' % haul

    avvDispStr = '|(avv_disp=BOTH)'
    if avvDisp == 'BOTH':
        avvDispStr += '(avv_disp=TRACKING)(avv_disp=MAINTENANCE)'
    else:
        avvDispStr += '(avv_disp=%s)' % avvDisp
    
    searchStr = '(&(region.id=%s)(%s)(%s)' % (region,catStr,haulStr)

    fromDateAbs = AbsDate(fromDate)
    toDateAbs = AbsDate(toDate)
    searchStr += '(%s)(|(valid_day=%s)' % (avvDispStr,fromDateAbs)
    searchStr += '(&(valid_day<=%s)(validto>=%s))))' % (toDateAbs,fromDate)

    freeTextList = TM.handover_message.search(searchStr)
    if not freeTextList:
        self.add(p.Row(TextLI('- No free text messages for this day')))
    else:
        self.add(p.Isolate(p.Row(
            ColH2('Creator', 35),
            ColH2('Create Time', 65),
            ColH2('Valid Day', 40),
            ColH2('Valid To', 65),
            ColH2('Editor', 35),
            ColH2('Edit Time', 65),
            ColH2('Free Text', 235),
            background='#cdcdcd')))
        bgColour = "#e5e5e5"
        for text in freeTextList:
            bgColour = changeColour(bgColour)
            creator = text.created_by or ''
            created_time = formatDate(text.created_time or '')
            validFrom = formatDate(AbsDate(text.valid_day))
            validTo = formatDate(text.validto or '')
            editor = text.edited_by or ''
            edited_time = formatDate(text.edited_time or '')
            region_text = text.free_text
            if region == 'SKN':
                region_text = text.region.id+': '+text.free_text
            for tline in region_text.split('\n'):
                self.add(p.Isolate(p.Row(
                    ColText(creator, 35),
                    ColText(created_time, 65),
                    ColText(validFrom, 40),
                    ColText(validTo, 65),
                    ColText(editor, 35),
                    ColText(edited_time, 65),
                    ColText(tline, 235),
                    background=bgColour)))
                creator=created_time=validFrom=validTo=editor=edited_time = ''
            self.page0()
    self.add(p.Row(p.Column(colspan=5), height=20))


#########################################################################
#
# SECTION 2): Standby Summary within 24 hours
#
#########################################################################

def blankDaysSection(self, region, category, haul, fromDate, toDate, sby_summ):
    """
    Creates a Summary of the available standbys. The summary
    will show the number of standbys starting within 24 hrs.
    The standby summation will be ordered under main category
    and morning/evening stanbys.It will contain also blank days.
    """
    blankDayContent = p.Row()

    start = fromDate
    end = toDate

    region_where = 'report_handover.%%region%% = "%s"' % region
    blankDayList, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.trip_set',
               where=('report_handover.%trip_blankday%',
                      'report_handover.%%trip_overlaps%%(%s,%s)' % (start,end),
                      region_where,
                      'report_handover.%%haul%%("%s")' % haul
                      )),
        'crew.%is_cabin%'
        ))
    blank_days_cc = 0
    blank_days_fc = 0
    for ix,blankDayIsCC in blankDayList:
        if blankDayIsCC == True:
            blank_days_cc += 1
        else:
            blank_days_fc += 1
        
    blankDaysSection = p.Row()
    blankDaysContent = p.Row()
    blankDaysContent.add(sby_summ)
    blankDaysContent.add(ColumnSpacer())
    
    blankDaysTitle = p.Isolate(p.Row(H1('Standby/Blank Days Summary %s - %s' % \
                                      (formatDate(fromDate),
                                       formatDate(toDate)), colspan=4)))

    if category == 'FC' or category == 'ALL':
        title = 'Flight Deck Blank Days'
        bl_table_fc = p.Column(PeriodRow(p.Column(BCText(title), colspan=2)))
        bl_table_fc.add(PeriodSubRow('Blank Days', 'Available'))
        bl_table_fc.add(p.Row('Number of blank days:',
                              blank_days_fc))
        
        blankDaysContent.add(bl_table_fc)
        blankDaysContent.add(ColumnSpacer())

    if category == 'CC' or category == 'ALL':
        title = 'Cabin Crew Blank Days'
        bl_table_cc = p.Column(PeriodRow(p.Column(BCText(title), colspan=2)))
        bl_table_cc.add(PeriodSubRow('Blank Days', 'Available'))
        bl_table_cc.add(p.Row('Number of blank days:',
                              blank_days_cc))
        
        blankDaysContent.add(bl_table_cc)
        

    blankDaysSectionColumn = p.Column()
    blankDaysSectionColumn.add(blankDaysTitle)
    blankDaysSectionColumn.add(blankDaysContent)
    
    self.add(p.Isolate(blankDaysSectionColumn))
        
def standbySection(self, region, category, haul, fromDate, toDate):

    start = fromDate
    end = toDate

    region_where = 'report_handover.%%region%% = "%s"' % region
    standbyList, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.duty_set',
               where=('report_handover.%duty_standby%',
                      'report_handover.%%duty_overlaps%%(%s,%s)' % (start,end),
                      region_where,
                      'report_handover.%%standby_haul%%("%s",duty.%%start_UTC%%)' % haul,
                      'report_handover.%%category%%("%s")' % category
                      )),
        'crew.%id%',
        ))
    
    # Group standby crew ids in duty. 
    idList = []
    for i, id in standbyList:
        idList.append(id)

    standbyTitle = p.Isolate(p.Row(H1('Standby Summary %s - %s' % \
                                      (formatDate(fromDate),
                                       formatDate(toDate)))))
    sb_table = p.Column(PeriodRow(p.Column(BCText("By Base, AC Qualification and Rank"), \
                                           colspan=7)))

    sb_table.add(PeriodSubRow('Category', 'Base', 'Standbys', 'AC Qualification', 'AC Qual Standbys', \
                              'Rank', ' Rank Standbys'))
    
    sbs_table = p.Column(PeriodRow(p.Column(BCText('Standby Summary'), colspan=2)))
    sbs_table.add(PeriodSubRow('Category', 'Standbys'))
            
    #Get all data that is necessary for the report
    sbyDict = {'sby_morning_sh' : [{}],
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
            #Does the crew exist in standby?
            if not crewAcQual.crew.id in idList:
                continue
            #Collect crew rank
            for crew in crewAcQual.crew.referers("crew_employment","crew"):
                crew_base = Airport(crew.base.airport.id)
                if crew_base.getUTCTime(crew.validfrom) < toDate and\
                   crew_base.getUTCTime(crew.validto) > fromDate:
                    crewRank = crew.crewrank.id
       
            crewAcQualValidFrom = crew_base.getUTCTime(crewAcQual.validfrom)
            crewAcQualValidTo = crew_base.getUTCTime(crewAcQual.validto)
            # Collect all crew that has valid ac qualification in the present period
            if crewAcQualValidFrom < toDate and crewAcQualValidTo > fromDate:
                #All crew that has a valid ac qual and has a crew activity is of interset and stored in crew_activities
                crew_activities = crewAcQual.crew.referers("crew_activity", "crew") 
                for activity in crew_activities:
                    try:
                        if activity.activity.grp.cat.id == "SBY":
                            airport = Airport(activity.adep.id)
                            st_local = airport.getLocalTime(activity.st)
                            #All standbys are of interest
                            if activity.st < toDate and activity.et > fromDate:
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
                                            self.collectBaseACandRank(sbyDict, 'sby_morning_ap', activity, ac, crewRank)                                                         
                                        else:
                                            self.collectBaseACandRank(sbyDict, 'sby_evening_ap', activity, ac, crewRank)
                                    else:
                                        if haulType == "SH":
                                            if dayType == morningType:
                                                self.collectBaseACandRank(sbyDict, 'sby_morning_sh', activity, ac, crewRank)
                                            else:
                                                self.collectBaseACandRank(sbyDict, 'sby_evening_sh', activity, ac, crewRank)
                                        else:
                                            if dayType == morningType:
                                                self.collectBaseACandRank(sbyDict, 'sby_morning_lh', activity, ac, crewRank)
                                            else:
                                                self.collectBaseACandRank(sbyDict, 'sby_evening_lh', activity, ac, crewRank)
                    except:
                        pass

    total_standby = 0
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_morning_sh', 'Morning short haul standbys:')
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_evening_sh', 'Evening short haul standbys:')
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_morning_lh', 'Morning long haul standbys:')
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_evening_lh', 'Evening long haul standbys:')
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_morning_ap', 'Morning airport standbys:')
    self.writeTableDataToPDFFile(sb_table, sbyDict, 'sby_evening_ap', 'Evening airport standbys:')
    sb_table.add(TRow("", "", "","","","","", border=p.border(top=1)))
    #Write to summary table
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_morning_sh', 'Morning short haul standbys:')
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_evening_sh', 'Evening short haul standbys:')
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_morning_lh', 'Morning long haul standbys:')
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_evening_lh', 'Evening long haul standbys:')
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_morning_ap', 'Morning airport standbys:')
    total_standby += self.writeSummaryTableToPDFFile(sbs_table, sbyDict, 'sby_evening_ap', 'Evening airport standbys:')
    sbs_table.add(TRow("Total Standby's:", Blue('%s' % total_standby), border=p.border(top=1)))
    
    self.add(p.Row(standbyTitle, EmptyCol()))
    self.add(p.Row(p.Isolate(sb_table)))
    self.add(p.Row(p.Column(colspan=5), height=20))
    #self.page()
    return sbs_table

#########################################################################
#
# SECTION 3): Summary of open time Trips 
#
#########################################################################

def openTripSection(self, region, category, haul, fromDate, toDate):
    """
    Creates a Summary of the pairings in open time. The summary
    contains the number of pairings ordered under the number of
    duty days, main category and morning/evening start. The definition
    for morning/evening start is the same as for the standbys.
    The summary includes pairings that start fromDate to toDate.
    """
    if haul.startswith('LONG'): haulStr = 'longhaul'
    elif haul.startswith('SHORT'): haulStr = 'shorthaul'
    else: haulStr = ''

    openTripSection = p.Column()
    openTripSection.add(p.Isolate(p.Row(H1('Open Trips Summary %s %s - %s' \
                                           % (haulStr,
                                              formatDate(fromDate),
                                              formatDate(toDate))))))
    start = fromDate
    end = toDate

    region = '"%s"' % region
    category = '"%s"' % category
    haul = '"%s"' % haul

    openTripContent = p.Column()
    openTripContent.add(TableRow(
        H2R('Days'),
        H2L('1'),H2('2'),H2('3'),H2('4'),H2('5'),H2('6'),H2('7'),
        H2L('Sum')))

    region_where = 'report_handover.%%trip_region%% = %s' % region
    openTripList, = R.eval('sp_crrs', R.foreach(
        R.iter('iterators.trip_set',
               where=('trip.%%start_utc%% >= %s' % start,
                      'trip.%%start_utc%% < %s' % end,
                      region_where,
                      'report_handover.%%trip_haul%%(%s)' % haul,
                      'report_handover.%open_trip%'
                      )),
        'report_handover.%trip_days%',
        'report_handover.%trip_morning%',
        'report_handover.%%trip_assigned%%(%s)' % category
         ))

    open_trips_morning_t = [0,0,0,0,0,0,0]
    open_trips_evening_t = [0,0,0,0,0,0,0]
    open_trips_total_t = [0,0,0,0,0,0,0]
    
    for (ix,trip_days,is_morning_trip,num_trips) in openTripList:
        index = trip_days - 1
        
        if is_morning_trip:
            open_trips_morning_t[index] += num_trips
        else:
            open_trips_evening_t[index] += num_trips
        open_trips_total_t[index] += num_trips
            
    totalDaysMorning = 0
    for days in xrange(6): totalDaysMorning += open_trips_morning_t[days]
    totalDaysEvening = 0
    for days in xrange(6): totalDaysEvening += open_trips_evening_t[days]
    totalDays = totalDaysMorning + totalDaysEvening
    
    openTripContent.add(p.Row(
        p.Text('Morning',
               font=p.Font(size=7,weight=p.BOLD),
               align=p.LEFT,
               border=p.border(right=1)),
        p.Text(open_trips_morning_t[0]),
        p.Text(open_trips_morning_t[1]),
        p.Text(open_trips_morning_t[2]),
        p.Text(open_trips_morning_t[3]),
        p.Text(open_trips_morning_t[4]),
        p.Text(open_trips_morning_t[5]),
        p.Text(open_trips_morning_t[6]),
        p.Text('%s' % totalDaysMorning,
               font=p.Font(size=7,weight=p.BOLD),
               align=p.RIGHT,
               border=p.border(left=1))))

    openTripContent.add(p.Row(
        p.Text('Evening',
               font=p.Font(size=7,weight=p.BOLD),
               align=p.LEFT,
               border=p.border(right=1)),
        p.Text(open_trips_evening_t[0]),
        p.Text(open_trips_evening_t[1]),
        p.Text(open_trips_evening_t[2]),
        p.Text(open_trips_evening_t[3]),
        p.Text(open_trips_evening_t[4]),
        p.Text(open_trips_evening_t[5]),
        p.Text(open_trips_evening_t[6]),
        p.Text('%s' % totalDaysEvening,
               font=p.Font(size=7,weight=p.BOLD),
               align=p.RIGHT,
               border=p.border(left=1))))

    openTripContent.add(p.Row(
        p.Text('Total',
               font=p.Font(size=7,weight=p.BOLD),
               align=p.LEFT,
               border=p.border(right=1, top=1)),
        p.Text(open_trips_total_t[0]),
        p.Text(open_trips_total_t[1]),
        p.Text(open_trips_total_t[2]),
        p.Text(open_trips_total_t[3]),
        p.Text(open_trips_total_t[4]),
        p.Text(open_trips_total_t[5]),
        p.Text(open_trips_total_t[6]),
        p.Text('%s' % totalDays,
               font=p.Font(size=7,weight=p.BOLD),
               align=p.RIGHT,
               border=p.border(left=1)),
        border=p.border(top=1)))

    openTripSection.add(p.Isolate(p.Row(openTripContent)))
    
##    if not len(openTripList)>0:
##        openTripSection.add(p.Row(TextLI(
##            '- No open trips for crew selected')))
    
    self.add(p.Isolate(p.Row(openTripSection)))

    
##########################################################################
#
# SECTION 4): Summary of ill crew which should report back the current day
#
##########################################################################

def illCrewSection(self, crewDict, fromDate, toDate):
    """
    Creates a summary of ill crew that should report back the current
    day. The list includes the departure time of the next duty for the crew.
    """

    rosters = 'fundamental.%is_roster%'
    rosters += ' and (crew.%id% = "'\
               + '" or crew.%id% = "'.join(crewDict.keys()) + '")'
    
    illCrewList, = R.eval('sp_crew', R.foreach(
        R.iter('iterators.leg_set',
               where=('leg.%%end_utc%% >= %s' % fromDate,
                      'leg.%%start_utc%% < %s' % toDate,
                      'leg.%is_report_back%',
                      rosters),
               sort_by=('report_handover.%crew_surname%')),
        'report_handover.%crew_id%',
        'report_handover.%%next_duty_after_illness%%(%s)' % fromDate))

    self.add(p.Isolate(p.Row(H1(
        'Crew Illness with Report Back %s - %s' \
        % (formatDate(fromDate), formatDate(toDate))))))

    if illCrewList:
        self.add(p.Isolate(p.Row(
            ColH2('Emp No', 40),
            ColH2('Name', 120),
            ColH2('Next Departure', 70),
            background='#cdcdcd')))

    else:
        self.add(p.Row(TextLI(
            '- No ill crew with report back')))

    bgColour = '#e5e5e5'
    for (ix,id,nextDutyAfterIll) in illCrewList:
        c = crewDict[id]
        self.add(p.Isolate(p.Row(
            ColText(c.empno, 40),
            ColText(c.name, 120),
            ColText(formatDate(nextDutyAfterIll), 70),
            background = bgColour)))
        self.page0()

        
#########################################################################
#
# SECTION 5): Summary of notification alerts with deadline 
#
#########################################################################

def notificationSection(self, crewList, crewDict, fromDate, toDate):
    """
    Creates a summary of publication/notification alerts and their
    deadline. The deadlines within fromDate - toDate will be listed.
    """
    self.add(p.Isolate(p.Row(H1('Notification Alerts %s - %s' \
                                % (formatDate(fromDate),
                                   formatDate(toDate))))))
    notifications=[]
    for id in crewDict.keys():
        crew_ref = TM.crew[(id,)]
        for notification in crew_ref.referers('crew_notification','crew'):
            if (not notification.delivered
                and notification.deadline >= fromDate
                and notification.deadline < toDate):
                notifications.append(notification)

    if not notifications:
        self.add(p.Isolate(p.Row(TextLI('- No notifications for this day'))))
    else:
        self.add(p.Isolate(p.Row(
            ColH2('Emp No', 40),
            ColH2('Name', 120),
            ColH2('Deadline', 70),
            ColH2('Notification', 320),
            background='#cdcdcd')))

        bgColour='#e5e5e5'
        for notification in sorted(notifications, key=lambda n: n.deadline):
            bgColour = changeColour(bgColour)
                
            crewId = notification.crew.id
            crewObj = crewDict[crewId]
                
            if notification.typ.typ == 'Automatic':
                message = notification.failmsg
            else:
                uuid = "(idnr=%s)" % notification.idnr
                message = "\n".join(
                    txt for (seqno, txt)
                        in sorted((row.seq_no, row.free_text) for row
                                  in TM.notification_message.search(uuid)))
    
            empno = crewObj.empno
            login_name = crewObj.login_name
            deadline = formatDate(notification.deadline)
            for msg_row in message.split('\n'):
                self.add(p.Isolate(p.Row(
                    ColText(empno, 40),
                    ColText(login_name, 120),
                    ColText(deadline, 70),
                    ColText(msg_row, 320),
                    background=bgColour)))
                empno = login_name = deadline = ""
            self.page0()


#########################################################################
#
# Help Functions
#
#########################################################################

def changeColour(bgColour):
    if bgColour == '#ffffff':
        return '#e5e5e5'
    else:
        return '#ffffff'
        
def formatDate(date):
    """
    Formats a date to a more beautiful format.
    Ex: from '03MAY2007 3:00' to '03May2007 3:00'
    """
    date = str(date)
    if date == '':
        return date
    else:
        day = str(date)[:2]
        month = str(date)[2:5].capitalize()
        year = str(date)[5:]
        return "%s%s%s" % (day,month,year)    

def formatMonth(date):
    """
    Formats a date to a date without year.
    Ex: from '03MAY2007 3:00' to '03May 3:00'
    """
    date = str(date)
    if date == '':
        return date
    else:
        day = str(date)[:2]
        month = str(date)[2:5].capitalize()
        hour = str(date)[10:]
        return "%s%s %s" % (day,month,hour)
