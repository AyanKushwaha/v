"""
 $Header$
 
 Lists information about short and long stops to be used for hotel and transport bookings
  
 Created:    February 2013
 By:         Niklas Johansson, STOOJ SAS

"""

# imports
import carmensystems.rave.api as R
import carmusr.ground_duty_handler as gdh
import carmusr.SBHandler as sbh
from carmensystems.publisher.api import *

from report_sources.include.SASReport import SASReport


# constants
CONTEXT = 'default_context'
TITLE = 'CPE Standby distribution'
FONTSIZEHEAD = 9
FONTSIZEBODY = 8
THINMARGIN = 2
THICKMARGIN = 8
REGION = ""
CAT = ""
WeekDayLookup = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}

class Context(object):
    def __init__(self, base, homebase, acFam, cat, region):
        self.base = base
        self.homebase = homebase
        self.acFam = acFam
        self.cat = cat
        self.region = region
    

def getContexts():
    return [Context("STO", R.enumval("planning_area.ANY_STATION"), R.enumval("planning_area.B737_FAM"), R.enumval("planning_area.FD_CAT"), R.enumval("planning_area.SKS_PG")),
            Context("OSL", R.enumval("planning_area.ANY_STATION"), R.enumval("planning_area.B737_FAM"), R.enumval("planning_area.FD_CAT"), R.enumval("planning_area.SKN_PG")),
            Context("CPH", R.enumval("planning_area.ANY_STATION"), R.enumval("planning_area.A320_FAM"), R.enumval("planning_area.FD_CAT"), R.enumval("planning_area.SKD_PG")),
            Context("CPH", R.enumval("planning_area.ANY_STATION"), R.enumval("planning_area.CRJ_FAM"), R.enumval("planning_area.FD_CAT"), R.enumval("planning_area.SKD_PG")),
            Context("CPH", R.enumval("planning_area.ANY_STATION"), R.enumval("planning_area.CRJ_FAM"), R.enumval("planning_area.FD_CAT"), R.enumval("planning_area.QA_PG"))]

def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)
    
def formatWeekday(int_weekday):
    return WeekDayLookup[int_weekday]
# Hotel

def toList(item):
    return [item]
class CpeStandbyDistribution(SASReport):

    def getCompl(self):
        return {'FC': 1, 'FP': 2, 'AP': 5, 'AH': 7}

    def initReport(self):
        # Basic setup
        SASReport.create(self, TITLE, orientation=LANDSCAPE)

        

    
    def presentData(self, data, outputReport, _context, is_dated):
        self.add(Row(Text("r %s b %s acFam %s cat %s b %s" %(_context.region, _context.homebase, _context.acFam, _context.cat, _context.base))))
        iter = 0
        if not is_dated:
            weekly_dict = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
            for dtc in data:
                weekly_dict[dtc.weekDay].append(dtc)
            dtc_lists =  weekly_dict.values()
        else:
            dtc_lists = list(map(toList, data))
        for dtc_list in dtc_lists:
            if (iter % 7 == 0):
                row = Row()
                self.add(row)
                self.page0()
            dateColumn = Column()
            self.presentDTCList(dtc_list, dateColumn, is_dated, False)
            row.add(dateColumn)
            iter+=1
        self.page()


    def presentDTCList(self, dtc_list, col, is_dated, weekly):
        row = Row()
        sbCol = Column(Text())
        sbs = []
        first = True
        for dtc in dtc_list:
            if first:
                if weekly:
                    col.add(Row(Text(formatWeekday(dtc.weekDay))))
                else:
                    col.add(Row(Text(str(dtc.date))))
                first = False
            sbs.extend(dtc.SBAssignments)
        potentialProblemDict = {}
        for sba in sorted(sbs):
            if not (sba.sb_specialStation is None):
                sp_list = potentialProblemDict.setdefault(sba.sb_specialStation, [])
                sp_list.append(sba)
            if (sba.code == 'A'):
                asb_list = potentialProblemDict.setdefault(sba.code, [])
                asb_list.append(sba)
        for key in potentialProblemDict.keys():
            items = potentialProblemDict[key]
            if (len(items) > 1):
                for sba in items:
                    self.presentSBA(sba, sbCol, weekly)
        row.add(sbCol)
        col.add(row)
            


    def presentSBA(self, sba, col, weekly):
        col.add(Row(Text("%s:%s-%s" %(sba.code, str(sba.startTime), str(sba.endTime)))))
        col.add(Row(Text("%s" %(sba.sb_info))))
        col.add(Row(Text("ss:%s st:%s" %(str(sba.sb_specialStation), str(sba.sb_type)))))

    def setContext(self, context):
        try:
            region = R.param("planning_area.planning_area_trip_planning_group_p")
            region.setvalue(context.region)
            homebase = R.param("planning_area.planning_area_trip_homebase_p")
            homebase.setvalue(context.homebase)
            ac_fam = R.param("planning_area.planning_area_trip_ac_fam_p")
            ac_fam.setvalue(context.acFam)
            cat = R.param("planning_area.planning_area_trip_category_p")
            cat.setvalue(context.cat)
            base = R.param("sb_handling.sb_base")
            base.setvalue(context.base)
        except  Exception as e:
            print str(e) + str(context)

    def getContext(self):
        return Context(R.param("sb_handling.sb_base").value(), R.param("planning_area.planning_area_trip_homebase_p").value(), R.param("planning_area.planning_area_trip_ac_fam_p").value(), R.param("planning_area.planning_area_trip_category_p").value(), R.param("planning_area.planning_area_trip_planning_group_p").value())
     
    def presentForContext(self, outputReport, _context, is_dated):
        data, _, _ = sbh.getData(CONTEXT)
        self.presentData(data, outputReport, _context, is_dated)
    
    def create(self, reportType):
        outputReport = (reportType == "output")
        self.initReport()
        is_dated, iterate, = R.eval('keywords.%global_is_dated_mode%', 'studio_cpe.%cpe_iterate_groups%')
        orgContext = self.getContext()
        if iterate:
            for _context in getContexts():
                self.setContext(_context)
                self.presentForContext(outputReport, _context, is_dated)
            self.setContext(orgContext)
        else:
            self.presentForContext(outputReport, orgContext, is_dated)
            


# End of file
