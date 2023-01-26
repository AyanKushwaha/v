#

#
"""
Crew Training Application
"""
l = []
count = 0
import time
import traceback

from tm import TempTable
from tm import TM
from utils.dave import EC
import Errlog

from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from modelserver import EntityError
from modelserver import DateColumn
from modelserver import StringColumn
from modelserver import RefColumn
from modelserver import BoolColumn
from modelserver import IntColumn
from modelserver import UUIDColumn
from modelserver import TimeColumn
import modelserver
import carmensystems.services.dispatcher as CSD
import utils.Names as Names

from modelserver import EntityNotFoundError as EntityNotFoundError
from modelserver import FieldNotFoundError as FieldNotFoundError
from modelserver import ReferenceError as ReferenceError
from modelserver import EntityError as EntityError

import carmusr.TimeUtil as TimeUtil
from utils.performance import log
import utils.wave
utils.wave.register()
if not utils.wave.STANDALONE:
    import Cui
    import carmensystems.rave.api as R
    import carmstd.cfhExtensions as cfhExtensions
    import HelperFunctions as HF
    import MenuState
    
global crewId
crewId = None

# These accumulators will be found and listed in the
# tab 'Crew Landings'. This view is constructed from
# reading the accumulator tables and finding the elements
# named in LANDING_DICT

LANDING_DICT = {}
# FLOWN AND LANDINGS
for ac_qual in ('A330','A340','A350','A320','B737','F50','MD80','Q400','CRJ'):
    LANDING_DICT['accumulators.last_flown_' +
                 ac_qual.lower()] = ('FLOWN', ac_qual)
    LANDING_DICT['accumulators.last_landing_' +
                 ac_qual.lower()] = ('LANDING', ac_qual)

VERBOSE = False
CREW_AREA = False
EXCLUDE_CONDITION_TUPLE = ('OPC', 'OTS', 'LPC', 'LC')

MAX_LENGTH_SI = None

class ValidationException(Exception):
    def __init__(self, message, errorTable=None):
        Exception.__init__(self, message)
        self.errorTable = errorTable

                
class SaveException(Exception):
    def __init__(self, message, errorTable=None):
        Exception.__init__(self, message)
        self.errorTable = errorTable
        

def getAndIncreaseRunningNo(table):
    runningNo = table.runningNo
    table.runningNo += 1
    return runningNo

def nullCompare(val1, val2):
    """
    This function compares two values.

    It will handle various null-cases and also comparison between AbsTime and
    other types.
    """
    nullVals = ("", " ", None)
    # First check, are the values the same?
    if val1 == val2:
        return True
    else:
        # AbsTime can't be compared with other types
        # so we need to except this
        try:
            # Next check, are the values null
            if val1 in nullVals and val2 in nullVals:
                return True
            else:
                return False
        except:
            return False


def findModifiedRows(tmptable):
    ## This function will find rows that were added or had values modified.
    ## Rows that were deleted will not be found, but should be handled
    ## through other functionality.

    debug = False
    
    sourceTable = tmptable.getSourceTable()
    keysStr = tmptable.getKeyNames()
    valuesStr = tmptable.getValueNames()

    modified_rows = []

    changes = False
    for row in tmptable:
        # Building a search-string based on non-zero values
        try:
            keys = tmptable.getKeys(row)
            searchKeysStr = ""
            skipthis = False
            for (string, value) in zip(keysStr, keys):
                if value:
                    searchKeysStr += "("+string+"=%s)" %value
                else:
                    skipthis = True
                    break
        
            if skipthis:
                continue
        except:
            continue
            
        values = tmptable.getValues(row)
        valueNames = tmptable.getValueNames()
        excludeList = tmptable.getValueExcludeNames()
        
        searchStr = "(&" + searchKeysStr + ")"
        # Ugly way to get length
        matching_keys = 0
        diff_vals = 0
        
        for source_row in sourceTable.search(searchStr):
            matching_keys += 1
            assert matching_keys < 2
            # A row in the source table with matching keys found
            # Lets compare values
            source_values = tmptable.getValues(source_row)
            
            # Is this row subject for excluded columns?
            excl = tmptable.excludeCondition(source_row)
            
            for (tmp, src, valname) in zip(values, source_values, valueNames):
                # Check for exclusion
                if excl and excludeList.count(valname) > 0:
                    continue
                
                if tmp == src:
                    continue
                else:
                    if nullCompare(tmp,src):
                        continue
                    else:
                        diff_vals += 1
                        break
                            
            # This should only happen once, or not at all
            #items += 1
            
        if ((matching_keys == 0) or (diff_vals > 0)):
            # The row couldn't be found in the DB.
            modified_rows.append(row.id)
            changes = True

    return (changes, modified_rows)
                

class FormInfo(TempTable):
    """
    The FormInfo class holds various information about the form.
    """

    _name = 'tmp_ctl_form_info'
    _keys = [StringColumn('id', 'Id')]
    _cols = [StringColumn("user", "User"),
             BoolColumn("w_rights", "Modification rights"),
             DateColumn("time", "Form Time"),
             StringColumn("status_message", "Status Bar Message"),
             StringColumn("status_color", "Status Bar Color"),
             StringColumn("error_table", "Table having validation errors"),
             BoolColumn("unsaved_changes", "Unsaved Changes Exist"),
             RefColumn("qual_filter", "crew_qualification_set", ""),
             RefColumn("res_filter", "crew_restriction_set", ""),
             RefColumn("sen_filter", "crew_sen_grp_set", ""),
             RefColumn("doc_filter", "crew_document_set", ""),
             BoolColumn("read_right", "Read Right"),
             BoolColumn("write_right", "Wright Right")]

    def __init__(self, crewId):
        self.runningNo = 0
        TempTable.__init__(self)
        self.populate(crewId)

    def populate(self, crewId):
        utils.wave.refresh_wave_values()
        now = utils.wave.get_now_utc()
        self.removeAll()
        index = getAndIncreaseRunningNo(self)
        row = self.create((str(index),))
        row.user = Names.username()
        row.w_rights = True
        row.time = now
        row.status_message = ""
        row.status_color = "transparent"
        if crewId is None:
            self.setStatusMessage("No or illegal crew selected", True)
        row.unsaved_changes = False
        
        for dbRow in TM.crew_qualification_set:
            row.qual_filter = dbRow
            break
        for dbRow in TM.crew_restriction_set:
            row.res_filter = dbRow
            break
        for dbRow in TM.crew_sen_grp_set:
            row.sen_filter = dbRow
            break
        for dbRow in TM.crew_document_set:
            row.doc_filter = dbRow
            if dbRow.typ == 'REC':
                break
        return

    def setStatusMessage(self, message='', isErrorMessage=False, errorTable=None):
        for row in self:
            row.status_message = message
            row.status_color = "transparent"
            if isErrorMessage:
                row.status_color = "red"
            if errorTable:
                row.error_table = errorTable
            break
        return

    def setUnsaved(self, status):
        for row in self:
            row.unsaved_changes = status
            break
        return

    def getTime(self):
        for row in self:
            return row.time
        return
        
    
class CrewInfoTable(TempTable):
    """
    The CrewInfoTable holds information for the crew summary.
    """
    _name = 'tmp_ctl_crew_summary'
    _keys = [StringColumn('id', 'Id')]
    _cols = [StringColumn('crew_id', 'Crew Id'),
             StringColumn('emp_no', 'Employee Number'),
             StringColumn('last_name', 'Last Name'),
             StringColumn('first_name', 'First Name'),
             StringColumn('rank'),
             StringColumn('main_cat'),
             StringColumn('homebase'),
             StringColumn('ac_quals'),
             StringColumn('pattern'),
             StringColumn('part_time_factor')]

    def __init__(self, crewId):
        self.runningNo = 0
        TempTable.__init__(self)
        self.populate(crewId)

    def populate(self, crewId):
        self.removeAll()
        index = getAndIncreaseRunningNo(self)
        row = self.create((str(index),))

        # Prevent empty cells from turning blue
        row.crew_id = ' '
        row.emp_no = ' '
        row.last_name = ' '
        row.first_name = ' '
        row.rank = ' '
        row.main_cat = ' '
        row.homebase = ' '
        row.ac_quals = ' '
        row.pattern = ' '
        row.part_time_factor = ' '

        if crewId is None:
            return

        crew = TM.crew[crewId]
        utils.wave.refresh_wave_values()
        nowTime = utils.wave.get_now_utc()

        rows = []
        crewEmp = None
        ldap = '(|(crew.id=%s)(extperkey=%s))' % (crewId, crewId)
        for crewEmp in TM.crew_employment.search(ldap):
            try:
                if crewEmp.validfrom <= nowTime and crewEmp.validto >= nowTime:
                    crewId = crewEmp.crew.id
                    break
                else:
                    rows.append(crewEmp)  
            except:
                pass
        else:
            if rows:
                rows.sort(cmp = lambda x,y: cmp(x.validto, y.validto))
                crewId = rows[-1].crew.id
                crewEmp = rows[-1]
                nowTime = rows[-1].validfrom
        
        searchVars = (crewId, nowTime, nowTime)
            
        acQlns = ' '.join(
            [qual.qual.subtype for qual in TM.crew_qualification.search(
            '(&(crew=%s)(qual.typ=ACQUAL)(validfrom<=%s)(validto>=%s))' %searchVars)])
        for contract in TM.crew_contract.search(
            '(&(crew=%s)(validfrom<=%s)(validto>=%s))' %searchVars):
            break
        specSched = None
        for specSched in TM.special_schedules.search(
            '(&(crewid=%s)(typ=PartTime)(validfrom<=%s)(validto>=%s))' %searchVars):
            break
            
        for info in crew.referers('crew_extra_info', 'id'):
            if info.validfrom <= nowTime < info.validto:
                row.last_name = info.name
                row.first_name = info.forenames
                break

        row.crew_id = crew.id
        row.emp_no = crewEmp.extperkey
        if row.last_name is None or not row.last_name.strip():
            row.last_name = crew.name
        if row.first_name is None or not row.first_name.strip():
            row.first_name = crew.forenames
        row.rank = crewEmp.crewrank.id
        row.main_cat = crewEmp.crewrank.maincat.id
        row.homebase = crewEmp.base.id
        row.ac_quals = acQlns
        try:
            ok_contract = True
            row.pattern = str(contract.contract.pattern.id)
        except:
            ok_contract = False
            Errlog.log("CrewTraining::CrewInfoTable: " +\
                       "Crewid %s has invalid contract" %crew.id)
            row.pattern = "Invalid"
        if specSched:
            row.part_time_factor = str(specSched.int_to)
        elif ok_contract:
            row.part_time_factor = str(contract.contract.dutypercent)
        else:
            row.part_time_factor = "Invalid"
            
        
class TrainingLogTable(TempTable):
    """
    Temporary class for training logs.
    """
    _name = 'tmp_ctl_log'
    _keys = [StringColumn('typ', 'Type'),
             StringColumn('code', 'Code'),
             TimeColumn('tim', 'Time')]
    _cols = [StringColumn('attr', 'Attribute'),
             BoolColumn('onroster', 'On roster'),
             StringColumn('grp', 'Group')]
    
    def __init__(self, crewId):
        TempTable.__init__(self)
        self.populate(crewId)

    def populate(self, crewId):
        self.removeAll()
        if crewId is None:
            return

        # The db will typically include most data, but will not be updated with
        # the latest changes in Studio.
        #
        # Therefore we first (and only, if standalone) gather data from the db,
        # and then we gather data from the roster. There's no overlap, the period
        # gathered from db will not include the period open in Studio.
                
        if utils.wave.STANDALONE:
            # In this case we have no choice. All data in db should be included
            # The different formatting for search string for database can't be
            # explained (by me, EkG) but is needed to not crash studio.
            ecSearch = "crew='%s'" % (crewId)
        else:
            # In studio we should have the latest data possible, and we mark
            # what can be found on roster.
            pStart, = R.eval('pp_start_time')
            pEnd, = R.eval('pp_end_time')
            ecSearch = "crew='%s' and (tim < %d or tim > %d)" % (crewId, pStart, pEnd)

        self.getDataFromDB(ecSearch)
        if not utils.wave.STANDALONE:
            self.getDataFromStudio(crewId)
        
    def getDataFromDB(self, ecSearch):
        ec = None
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
            for row in ec.crew_training_log.search(ecSearch):
                grp = "MISC"
                key = (row.typ, row.code, row.tim)
                try:
                    for grprow in TM.training_log_set.search("(typ=%s)" % row.typ):
                        grp = grprow.grp
                        break
                except:
                    print traceback.print_exc()
                    
                self.createRow(key, row.attr, False, grp)
        finally:
            if ec:
                ec.close()

    def getDataFromStudio(self, crewId):
        crew_object = HF.CrewObject(crewId, CREW_AREA)
        ec = None
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
        
            training_log_expr = R.foreach(
                R.iter("iterators.leg_set",
                       where = 'training_log.%leg_is_valid%'),
                'leg.%start_utc%',
                'training_log.%leg_type%',
                'training_log.%leg_type2%',
                'training_log.%leg_code%',
                'training_log.%leg_attr%'
                )
            training_log, = crew_object.eval(training_log_expr)
        
            for (ix, act_start, act_type1, act_type2, act_code, act_attr) in training_log:
                for act_type in (act_type1, act_type2):
                    # Some things are logged as two items
                    if act_type is not None:
                        key = (act_type, act_code, act_start)
                        grp = ""
                        for grprow in TM.training_log_set.search("(typ=%s)" % act_type):
                            grp = grprow.grp
                            break
                        self.createRow(key, act_attr, True, grp)
        finally:
            if ec:
                ec.close()
                
    def createRow(self, key, attr, onroster, grp):
        try:
            logRow = self.create(key)
            logRow.attr = attr
            logRow.onroster = onroster
            logRow.grp = grp
        except EntityError:
            logMessage("Activity on roster already in db")
        except:
            Errlog.log("CrewTraining.py::TrainingLog::createRow: \
            Couldn't create entry with key = %s, onroster = %s" % (str(key), onroster))
                            
class SystemTable(TempTable):
    """
    Temporary class for misc data
    """
    _name = 'tmp_ctl_sys'
    _keys = [StringColumn('id', 'Id')]
    _cols = [DateColumn('timefr', 'TimeFr'),
             DateColumn('timeto', 'TimeTo')]
    
    def __init__(self):
        try:
            # Check if not already initiated
            TM.table("tmp_ctl_sys")
        except:
            TempTable.__init__(self)
            self.populate()
        
    def populate(self):
        self.removeAll()
        newSys = self.create(("0",))
        newSys.timefr = AbsTime("01Jan1986")
        newSys.timeto = AbsTime("31Dec2035")
      
class LandingTable(TempTable):
    """
    Temporary class for landings.
    """
    _name = 'tmp_ctl_landing'
    _keys = [StringColumn('typ', 'Type'),
             StringColumn('code', 'Code'),
             TimeColumn('tim', 'Time')]
    _cols = [BoolColumn('onroster', 'On roster'),
             StringColumn('grp', 'Group')]

    def __init__(self, crewId):
        TempTable.__init__(self)
        self.populate(crewId)

    def populate(self, crewId):
        self.removeAll()
        if crewId is None:
            return

        # Landing and training log behaves similarly concering data, please
        # see comments above for explanations.

        if utils.wave.STANDALONE:
            ecSearch = "acckey='%s'" % (crewId)
        else:
            # We add a bit of overlap to handle flights starting outside loaded
            # interval, but landing inside
            pStart, = R.eval('pp_start_time + 24:00')
            pEnd, = R.eval('pp_end_time')
            ecSearch = "acckey='%s' and tim < %d" % (crewId, pStart)
            
        self.getDataFromDB(ecSearch)
        if not utils.wave.STANDALONE:
            self.getDataFromStudio(crewId)
    
    
    def getDataFromDB(self, ecSearch):
        ec = None
        global count
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
            for row in ec.accumulator_time.search(ecSearch):
                try:
                    if row.name == 'accumulators.last_flown_a320_lh':
                        typ = 'FLOWN'
                        code = 'A320 LH'
                        key = (typ, code, row.tim)
                        key_list = typ + str(row.tim)
                        if key_list not in l:
                            l.append(key_list)
                            self.createRow(key, False, typ)

                    elif row.name == 'accumulators.last_landing_a320_lh':
                        typ = 'LANDING'
                        code = 'A320 LH'
                        key = (typ, code, row.tim)
                        key_list = typ + str(row.tim)
                        if key_list not in l:
                            l.append(key_list)
                            self.createRow(key, False, typ)



                    else:
                        continue
 
    
                except KeyError:
                    # This means the accumulator row wasn't of interest
                    continue
            
            for row in ec.accumulator_time.search(ecSearch):
                #print "row->",row
                #pEnd, = R.eval('pp_end_time')
                try:
                    (typ, code) = LANDING_DICT[row.name]
                    key = (typ, code, row.tim)
                    key_list = typ + str(row.tim)
                    if key_list not in l:
                        l.append(key_list)
                        self.createRow(key, False, typ)
                    else:
                        pass
                       
    
                except KeyError:
                    # This means the accumulator row wasn't of interest
                    continue        
            
                 
        finally:
            if ec:
                ec.close()
            
    def getDataFromStudio(self, crewId):
        crew_object = HF.CrewObject(crewId, CREW_AREA)

        leg_expr = R.foreach(
            R.iter("iterators.leg_set",
                   where = "leg.%is_active_no_rtr_flight%"),
            "recency.%leg_qualifies_for_recency%",
            "leg.%ac_family%",
            "leg.%end_UTC%",
            "leg.%is_LH_with_NX_ac%",
            )
        legs, = crew_object.eval(leg_expr)
        
        for (ix, landing, acfam, tim,isLHNX) in legs:
            # First we add a simple FLOWN row, true for all active legs
            temp = "A320 LH" if isLHNX else acfam   
            key = ("FLOWN", temp, tim)
            key_list = 'FLOWN' + str(tim)
            if key_list not in l:
                l.append(key_list)
                self.createRow(key, True, "FLOWN")
            else:
                pass 
                
            # Next we add the landings
            if landing:
                key = ("LANDING", temp, tim)
                key_list = 'LANDING' + str(tim)
                if key_list not in l:
                    l.append(key_list)
                    self.createRow(key, True, "LANDING")
                else:
                    pass
        

    def createRow(self, key, onroster, grp):
        landRow = None
        try:
            landRow = self.create(key)            
        except EntityError:
            logMessage("Activity on roster already in db")
            landRow = self[key]
        except Exception, e:
            print e
            Errlog.log("CrewTraining.py::LandingTable::createRow: \
            Couldn't create entry with key = %s, onroster = %s" % (str(key), onroster))
            return
        # If we are here we have a landRow
        landRow.onroster = onroster
        landRow.grp = grp
            
class NeedMerge(TempTable):
    """
    Temporary class for training need merge.
    """
    _name = 'tmp_ctl_merge'
    _keys = [StringColumn('id', 'Id')]
    _cols = [IntColumn('part', 'Order'),
             DateColumn('validfrom', 'Training start'),
             DateColumn('validto', 'Training end'),
             RefColumn('course', 'course_type', 'Course Type'),
             RefColumn('course_subtype', 'course_subtype', 'Course Subtype'),
             RefColumn('attribute', 'crew_training_t_set', 'Type'),
             DateColumn('modvalidto', 'Visualized training end'),
             IntColumn('flights', 'Number Of Needed Flights'),
             IntColumn('maxdays', 'Max days'),
             StringColumn('acqual', 'Optional AC Qual'),
             DateColumn('completion', 'Completion Date'),
             StringColumn('si', 'SI'),
             RefColumn('orgcourse', 'course_type', 'Orig Course Type'),
             RefColumn('orgcourse_subtype', 'course_subtype', 'Orig Course Subtype'),
             IntColumn('orgpart', 'Orig Order'),
             RefColumn('orgattribute', 'crew_training_t_set', 'Orig Type'),
             DateColumn('orgvalidfrom', 'Orig Training start'),
             StringColumn('orgsi', 'Orig SI')]

    def __init__(self):
        TempTable.__init__(self)

class Need(TempTable):
    """
    Temporary class for training need.
    """
    _name = 'tmp_ctl_need'
    _keys = [StringColumn('id', 'Id')]
    _cols = [IntColumn('part', 'Order'),
             DateColumn('validfrom', 'Training start'),
             DateColumn('validto', 'Training end'),
             RefColumn('course', 'course_type', 'Course Type'),
             RefColumn('course_subtype', 'course_subtype', 'Course Subtype'),
             RefColumn('attribute', 'crew_training_t_set', 'Type'),
             IntColumn('flights', 'Number Of Needed Flights'),
             IntColumn('maxdays', 'Max days'),
             StringColumn('acqual', 'Optional AC Qual'),
             DateColumn('completion', 'Completion Date'),
             StringColumn('si', 'SI'),
             DateColumn('modvalidto', "Visualized training end"),
             RefColumn('orgcourse', 'course_type', 'Orig Course Type'),
             RefColumn('orgcourse_subtype', 'course_subtype', 'Orig Course Subtype'),
             RefColumn('orgattribute', 'crew_training_t_set', 'Orig Type'),
             IntColumn('orgpart', 'Orig Order'),
             StringColumn('orgsi', 'Orig SI'),
             DateColumn('orgvalidfrom', 'Orig Training start')]
             

    @staticmethod
    def getSourceTable():
        return TM.crew_training_need
    
    @staticmethod
    def getKeyNames():
        return ("crew","part","validfrom")

    @staticmethod   
    def getKeys(row):
        global crewId
        return (crewId, row.orgpart, AbsDate(row.orgvalidfrom))

    @staticmethod
    def getValueNames():
        return ("course", "course_subtype", "validfrom", "validto")

    @staticmethod
    def getValueExcludeNames():
        return ("")

    @staticmethod
    def excludeCondition(row):
        return False

    @staticmethod   
    def getValues(row):
        try:
            valto = TimeUtil.inclDateToExclTime(row.validto)
        except:
            valto = row.validto
        return (row.course, row.course_subtype, row.validfrom, valto)
    
    @staticmethod   
    def getTypAndCtype(row):
        try:
            crs = row.course
        except ReferenceError:
            crs = row.getRefI("course")
        try:
            attr = row.attribute
        except ReferenceError:
            attr = row.getRefI("attribute")
        return (attr, crs)

    @staticmethod   
    def getTypAndCtypeValue(row):
        try:
            crs = row.course.id
        except ReferenceError:
            crs = row.getRefI("course")
        try:
            attr = row.attribute.id
        except ReferenceError:
            attr = row.getRefI("attribute")
        return (attr, crs)

    _table_search = '(crew=%s)'
    
    def __init__(self, crewId):
        self.runningNo = 0
        TempTable.__init__(self)
        self.populate(crewId)
        self.unsavedChanges = False

    def populate(self, crewId):
        global NeedRowTable
        self.removeAll()
        if crewId is None:
            return
        
        searchStr = Need._table_search % crewId
        for row in TM.crew_training_need.search(searchStr):
            if row.part == 1:
                index = getAndIncreaseRunningNo(self)
                need = self.create((str(index),))
        
                need.part = row.part
                (attr, crs) = self.getTypAndCtype(row)
                need.attribute = attr
                need.course = crs
                need.course_subtype = row.course_subtype
                need.validfrom = row.validfrom
                need.validto = row.validto
                need.modvalidto = TimeUtil.exclTimeToInclTime(row.validto)
                need.flights = row.flights
                need.maxdays = row.maxdays
                need.acqual = row.acqual
                need.completion = row.completion
                need.si = row.si
    
                need.orgpart = row.part
                need.orgattribute = attr
                need.orgcourse = crs
                need.orgcourse_subtype = row.course_subtype
                need.orgvalidfrom = row.validfrom
                need.orgsi = row.si
                
    def createRow(self, validfrom, rowid):
        global NeedRowTable
        #if not utils.wave.STANDALONE:
        #    validto, = R.eval('fundamental.%pp_end%')
        #else:
            #validto = AbsTime(validfrom).addmonths(1)

        # adddays(1) to make sure that we skip 1:st of month 00:00
        # to make month_ceil() work OK, adddys(-1) to get to last day 
        # in month.
        validto = validfrom.adddays(1).month_ceil().adddays(-1)
            
        modvalidto = TimeUtil.exclTimeToInclTime(validto)
    
        # Look for previous rows in Need table to prevent
        # overlapping dates
        maxFrom = AbsTime(validfrom)
        maxTo = AbsTime(validto)
        for prevNeed in TM.tmp_ctl_need:
            if (prevNeed.validto and prevNeed.validto > maxFrom):
                maxFrom = AbsTime(prevNeed.validto)
                maxTo   = maxFrom.adddays(1).month_ceil().adddays(-1)
        
        index = getAndIncreaseRunningNo(self)
        newNeed = self.create((str(index),))
            
        newNeed.part = 1
        newNeed.validfrom = maxFrom
        newNeed.modvalidto = maxTo
        newNeed.validto = TimeUtil.inclDateToExclTime(maxTo)
        
        self.setUnsaved()
        NeedRowTable.createRow(index)
        
        return

    def checkForChanges(self):
        mod_rows = None
        if not self.unsavedChanges:
            # This means no rows have been added or removed
            (self.unsavedChanges, mod_rows) = findModifiedRows(self)
            
        return (self.unsavedChanges, mod_rows)
    
    def setUnsaved(self, status=True):
        self.unsavedChanges = status

    def save(self):
        global crewId
        global NeedRowTable
        global MAX_LENGTH_SI
        
        # copy modvalidto to validto so that findModifiedRows()
        # can detect changes in validto
        for tmpNeed in TM.tmp_ctl_need:
            if tmpNeed.part == 1:
                tmpNeed.validto = TimeUtil.inclDateToExclTime(tmpNeed.modvalidto)
                
        (changes, foo) = self.checkForChanges()
        if not (changes or NeedRowTable.unsavedChanges):
            # No changes to save
            return False
                
        if utils.wave.STANDALONE:
            TM.newState()
            
        # Create a "sum" table; need and needrows merged,
        NeedMergeTable = NeedMerge()
        NeedMergeTable.removeAll()
        mergerownum = 0
        
        for tmprowNeed in TM.tmp_ctl_rows:
            # Check that tmprowNeed.id exists in tmp_ctl_need
            for item_need in TM.tmp_ctl_need.search("(id=%s)" % tmprowNeed.id):
                for item in (tmprowNeed.attribute,):
                    if item is None:
                        raise ValidationException('Please enter all required fields',
                                                  'tmp_ctl_need')
                break

        # Check for overlaps
        for tmpNeed in TM.tmp_ctl_need:
            for cmpNeed in TM.tmp_ctl_need:
                if (cmpNeed.id > tmpNeed.id and
                    ((tmpNeed.validfrom >= cmpNeed.validfrom and 
                     tmpNeed.validfrom < cmpNeed.validto) or
                    (tmpNeed.validto > cmpNeed.validfrom and
                     tmpNeed.validto <= cmpNeed.validto))):
                         raise ValidationException('Overlapping training periods',
                                              'tmp_ctl_need')

        # MAX_LENGTH_SI
        if MAX_LENGTH_SI == None:
            entity_description =  TM.crew_training_need.entityDesc()
            MAX_LENGTH_SI = entity_description.maxsize(entity_description.column('si'))

        for tmpNeed in TM.tmp_ctl_need:
            for item in (tmpNeed.course, tmpNeed.validfrom, tmpNeed.validto):
                if item is None:
                    raise ValidationException('Please enter all required fields',
                                              'tmp_ctl_need')
                      
            for rowNeed in TM.tmp_ctl_rows.search("(id=%s)" % tmpNeed.id):
                # Check for correct acqual.
                # Can't be reference due to set table including too much
                if rowNeed.acqual:
                    try:
                        qual = TM.crew_qualification_set[("ACQUAL",rowNeed.acqual)]
                    except:
                        raise ValidationException('Invalid acqual [%s]' %rowNeed.acqual,
                                                  'tmp_ctl_need')
                if rowNeed.si and len(rowNeed.si) > MAX_LENGTH_SI:
                     raise ValidationException('Comment field is max %s characters' %MAX_LENGTH_SI,
                                               'tmp_ctl_need')
                mergerownum += 1
                merge_row = TM.tmp_ctl_merge.create((str(mergerownum),))
                merge_row.course = tmpNeed.course
                merge_row.course_subtype = tmpNeed.course_subtype
                merge_row.validfrom = tmpNeed.validfrom
                merge_row.validto = tmpNeed.validto
                merge_row.modvalidto = tmpNeed.modvalidto
                merge_row.completion = tmpNeed.completion

                merge_row.orgcourse= tmpNeed.orgcourse
                merge_row.orgcourse_subtype= tmpNeed.orgcourse_subtype
                merge_row.orgpart = tmpNeed.part
                merge_row.orgattribute = rowNeed.orgattribute
                merge_row.orgvalidfrom = tmpNeed.orgvalidfrom
                merge_row.orgsi = rowNeed.orgsi
                
                merge_row.part = rowNeed.part
                merge_row.attribute = rowNeed.attribute
                merge_row.flights = rowNeed.flights
                merge_row.maxdays = rowNeed.maxdays
                merge_row.acqual = rowNeed.acqual
                merge_row.si = rowNeed.si

        searchStr_db = Need._table_search % crewId
        
        # Finding duplicate rows ????
        for need in TM.crew_training_need.search(searchStr_db):
            (attribute, course) = Need.getTypAndCtypeValue(need)
            
            searchStr_tmp = (
                '(&(course=%s)(part=%s)(attribute=%s)(validfrom=%s))' % (
                course, need.part, attribute, need.validfrom))
            
            items = 0
            for row in TM.tmp_ctl_merge.search(searchStr_tmp):
                items += 1
            if items == 0:
                # The row in source wasn't found in tmp, lets remove it
                need.remove()
                log("CrewTraining: REMOVED %s" % need)
            elif items == 1:
                continue
            else:
                raise ValidationException('Please remove duplicate rows',
                                          'tmp_ctl_need')

        for mergeNeed in TM.tmp_ctl_merge:            
            crew = TM.crew[(crewId,)]
            key = (crew, mergeNeed.part, mergeNeed.validfrom)
            
            orig_need = None
            try:
                need = TM.crew_training_need.create(key)
            except EntityError:
                need = TM.crew_training_need[key]
                orig_need = str(need)
                
            need.course = mergeNeed.course
            need.course_subtype = mergeNeed.course_subtype
            need.attribute = mergeNeed.attribute
            need.validto = mergeNeed.validto
            need.flights = mergeNeed.flights
            need.maxdays = mergeNeed.maxdays
            need.acqual = mergeNeed.acqual
            need.si = mergeNeed.si
            if orig_need:
                log("CrewTraining: UPDATED ORIG %s" % orig_need)
                log("CrewTraining:          REV %s" % need)
            else:
                log("CrewTraining: ADDED %s" % need)
            
        return True

class NeedRow(TempTable):
    """
    Temporary class for training need rows.
    """
    _name = 'tmp_ctl_rows'
    _keys = [StringColumn('rowid', 'Id')]
    _cols = [StringColumn('id', 'HeadId'),
             IntColumn('part', 'Order'),
             RefColumn('attribute', 'crew_training_t_set', 'Type'),
             IntColumn('flights', 'Number Of Needed Flights'),
             IntColumn('maxdays', 'Max days'),
             StringColumn('acqual', 'Optional AC Qual'),
             StringColumn('si', 'SI'),
             IntColumn('orgpart', 'Orig Order'),
             DateColumn('orgvalidfrom', 'Orig Training start'),
             RefColumn('orgcourse', 'course_type', 'Orig Course Type'),
             RefColumn('orgcourse_subtype', 'course_subtype', 'Orig Course Subtype'),
             RefColumn('orgattribute', 'crew_training_t_set', 'Orig Type'),
             IntColumn('orgflights', 'Orig Number Of Needed Flights'),
             IntColumn('orgmaxdays', 'Orig Max days'),
             StringColumn('orgacqual', 'Optional AC Qual'),
             StringColumn('orgsi', 'Orig SI'),]

    @staticmethod
    def getSourceTable():
        return TM.crew_training_need
    
    @staticmethod
    def getKeyNames():
        return ("crew", "part", "validfrom")

    @staticmethod
    def getKeys(row):
        global crewId
        try:
            ctype = row.orgcourse.id
        except ReferenceError:
            ctype = row.getRefI("orgcourse")
        try:
            attr = row.orgattribute.id
        except ReferenceError:
            attr = row.getRefI("orgattribute")
            
        return (crewId, row.orgpart, AbsDate(row.orgvalidfrom))

    @staticmethod
    def getValueNames():
        return ("attribute", "flights","maxdays","acqual","si")

    @staticmethod
    def getValueExcludeNames():
        return ("")

    @staticmethod
    def excludeCondition(row):
        return False
        
    @staticmethod   
    def getValues(row):
        return (row.attribute, row.flights, row.maxdays, row.acqual, row.si)
    
    @staticmethod   
    def getTyp(row):
        try:
            attr = row.attribute
        except ReferenceError:
            attr = row.getRefI("attribute")
        return (attr)

    @staticmethod   
    def getTypValue(row):
        try:
            attr = row.attribute.id
        except ReferenceError:
            attr = row.getRefI("attribute")
        return (attr)

    _table_search = '(crew=%s)'
    
    def __init__(self, crewId):
        self.runningNo = 0
        TempTable.__init__(self)
        self.populate(crewId)
        self.unsavedChanges = False

    def populate(self, crewId):
        self.removeAll()
        if crewId is None:
            return
        
        searchStr = NeedRow._table_search % crewId
        
        ctnrows = 0
        for row in TM.crew_training_need.search(searchStr):
            #populate needrow
            #find the header row in NeedTable
            ctnrows += 1
            (attribute, xtype) = Need.getTypAndCtype(row)
            search_str = "(&(validfrom=%s)(part=1))" % (row.validfrom)
            for header_row in TM.tmp_ctl_need.search(search_str):
                self.createRow(header_row.id, row.part, attribute, row.flights, row.maxdays, row.acqual, row.si)
                break

    def createRow(self, rowid, part=0, attribute=None, flights=None, maxdays=None, acqual=None, si=None):
        master_row = TM.tmp_ctl_need[(str(rowid),)]
        index = getAndIncreaseRunningNo(self)
        newNeedrow = self.create((str(index),))
        # A new detail row is created
        if part==0:
            #row is created from the wave form
            part += 1
            searchStr = "(id=%s)" % (master_row.id)
            for slave_row in TM.tmp_ctl_rows.search(searchStr):
                part += 1
            self.setUnsaved()
        else:
            #row is created from self.populate()
            newNeedrow.attribute = attribute
            newNeedrow.flights = flights
            newNeedrow.maxdays = maxdays
            newNeedrow.acqual = acqual
            newNeedrow.si = si
            # Orig columns
            newNeedrow.orgattribute = attribute
            newNeedrow.orgflights = flights
            newNeedrow.orgmaxdays = maxdays
            newNeedrow.orgacqual = acqual
            newNeedrow.orgsi = si
            
        newNeedrow.orgcourse = master_row.course
        newNeedrow.orgcourse_subtype = master_row.course_subtype
        newNeedrow.orgvalidfrom = master_row.validfrom
        
        newNeedrow.part = part
        newNeedrow.orgpart = part
        newNeedrow.id = str(rowid)
        
        return

    def checkForChanges(self):
        mod_rows = None
        if not self.unsavedChanges:
            # This means no rows have been added or removed
            (self.unsavedChanges, mod_rows) = findModifiedRows(self)
        return (self.unsavedChanges, mod_rows)
    
    def setUnsaved(self, status=True):
        global NeedTable
        self.unsavedChanges = status
        NeedTable.setUnsaved(status)

    def save(self):
        (changes, foo) = self.checkForChanges()
        if changes:
            self.setUnsaved()

class ValidDocno(TempTable):
    """
    ...
    """
    _name = 'tmp_ctl_valid_docno'
    _keys = [StringColumn('acqual', 'AC qualification')]
    _cols = []

    def __init__(self, crewid):
        TempTable.__init__(self)
        self.populate(crewid)

    def populate(self, crewid):
        self.removeAll()
        
        main_cat = "F"
        try:
            crew_sum = TM.tmp_ctl_crew_summary[("0",)]
            main_cat = crew_sum.main_cat
        except:
            pass
            
        for row in TM.ac_qual_map:
            if main_cat == "F":
                try:
                    doc = TM.tmp_ctl_valid_docno[(row.ac_qual_fc,)]
                except:
                    self.create((row.ac_qual_fc,))
            else:
                try:
                    doc = TM.tmp_ctl_valid_docno[(row.ac_qual_cc,)]
                except:
                    self.create((row.ac_qual_cc,))
            

    @staticmethod
    def getDocno(docno):
        if (docno == "" or docno is None):
            docno = " "
        try:
            docno_ref = TM.tmp_ctl_valid_docno[(docno,)]
            docno_res = docno_ref.acqual
        except EntityNotFoundError:
            # Junk data in table
            docno_res = " "
        return docno_res

        
class DocExcludeCondition(TempTable):
    """
    Temporay class that holds document exclude condition type+subtype.
    """
    _name = 'doc_exclude_condition'
    _keys = [RefColumn("doctyp", "crew_document_set", "DocuType")]

    def __init__(self):
        TempTable.__init__(self)
        self.populate()
        
    def populate(self):
        self.removeAll()
        for val in TM.crew_document_set:
            if val.subtype in EXCLUDE_CONDITION_TUPLE:
                rec = self.create((val._id))

class Document(TempTable):
    """
    Temporay class that holds document info for crew.
    """
    _name = 'tmp_ctl_document'
    _keys = [StringColumn('id', 'Id')]
    _cols = [RefColumn("doc", "crew_document_set", "Document"),
             DateColumn("validfrom", "Valid From"),
             DateColumn("validto", "Valid To"),
             DateColumn("modvalidto", "Visualized valid to"),
             StringColumn("docno", "Document Number"),
             StringColumn("ac_qual", "AC Qualification"),
             #RefColumn("docno", "tmp_ctl_valid_docno", "Document Number"),
             StringColumn("issuer", "Issuer"),
             StringColumn("si", "SI")]

    @staticmethod
    def getSourceTable():
        return TM.crew_document

    @staticmethod
    def getKeyNames():
        return ("crew","doc","validfrom")
    
    @staticmethod   
    def getKeys(row):
        global crewId
        try:
            doc = row.doc._id
        except ReferenceError:
            # This catches data errors where the doc can't be found in the
            # referred table.
            doc = row.getRefI("doc")
        return (crewId, doc, row.validfrom)

    @staticmethod
    def getValueNames():
        return ("validto","docno","ac_qual","issuer","si")

    @staticmethod
    def getValueExcludeNames():
        # A list of columns that we don't handle if excludeCondition is True
        return ("ac_qual")

    @staticmethod
    def excludeCondition(row):
        if (row.doc.subtype in EXCLUDE_CONDITION_TUPLE):
            return False
        else:
            return True

    @staticmethod   
    def getValues(row):
        try:
            validto = TimeUtil.inclDateToExclTime(row.modvalidto)
        except:
            validto = row.validto
        return (validto, row.docno, row.ac_qual, row.issuer, row.si)

    @staticmethod   
    def getDoc(row):
        try:
            doc = row.doc
        except ReferenceError:
            # This catches data errors where the doc can't be found in the
            # referred table.
            doc = row.getRefI("doc")
        return doc

    _table_search = "(&(crew=%s)(doc.typ=REC))"

    def __init__(self, crewId):
        self.runningNo = 0
        TempTable.__init__(self)
        self.populate(crewId)
        self.unsavedChanges = False

    def populate(self, crewId):
        self.removeAll()
        if crewId is None:
            return

        searchStr = Document._table_search % crewId
        
        for row in TM.crew_document.search(searchStr):
            index = getAndIncreaseRunningNo(self)
            doc = self.create((str(index),))
            doc.doc = Document.getDoc(row)
            doc.validfrom = row.validfrom
            doc.validto = row.validto
            doc.modvalidto = TimeUtil.exclTimeToInclTime(row.validto)
            doc.docno = row.docno
            if not Document.excludeCondition(doc):
                doc.ac_qual = row.ac_qual
            doc.issuer = row.issuer
            doc.si = row.si

    def createRow(self, nowTime):
        index = getAndIncreaseRunningNo(self)
        newDoc = self.create((str(index),))
        newDoc.validfrom = nowTime
        newDoc.modvalidto = TimeUtil.exclTimeToInclTime(nowTime)
        self.setUnsaved()
        return

    def checkForChanges(self):
        mod_rows = None
        
        if not self.unsavedChanges:
            # This means no rows have been added or removed
            (self.unsavedChanges, mod_rows) = findModifiedRows(self)
        return (self.unsavedChanges, mod_rows)

    def setUnsaved(self, status=True):
        self.unsavedChanges = status

    def validateDocForModifiedRows(self, mod_rows):
        DOCUMENT_BLACKLIST = ['LC', 'LPC', 'LPCA3', 'LPCA3A5', 'LPCA4','LPCA5','OPC', 'OPCA3', 'OPCA3A5', 'OPCA4','OPCA5',
                              'OTS', 'OTSA3', 'OTSA3A5', 'OTSA4','OTSA5','CRM', 'CRMC', 'REC', 'PGT']

        errorText = None
        if self is None or mod_rows is None:
            return errorText
        for s in self:
            if s._id in mod_rows and s.doc.subtype in DOCUMENT_BLACKLIST:
                errorText = "WARNING: " + str(s.doc.subtype) + " is not supposed to be updated manually. Press 'Refresh' to undo or 'Apply' to force update."
        return errorText

    def save(self):
        DOCUMENT_BLACKLIST = ['LC', 'LPC', 'LPCA3', 'LPCA3A5', 'LPCA4','LPCA5','OPC', 'OPCA3', 'OPCA3A5', 'OPCA4','OPCA5',
                              'OTS', 'OTSA3', 'OTSA3A5', 'OTSA4','OTSA5','CRM', 'CRMC', 'REC', 'PGT'] # TODO move somewhere relevant

        global crewId

        (changes, mod_rows) = self.checkForChanges()
        if not changes:
            # No changes to save
            return False

        errorText = self.validateDocForModifiedRows(mod_rows)
        if errorText is not None:
            raise ValidationException(errorText, 'tmp_ctl_document')

        crew = TM.crew[(crewId,)]

        if utils.wave.STANDALONE:
            TM.newState()

        searchStr = Document._table_search % crewId


        dryRun = True  # Try to save once and do the actual save the second turn if no exception occurs.  HiQ - SKCMS-83 - 2014-06-24
        while True:
            removed_rows = []
            added_rows = []
            modified_rows = []
        
                  
            # Finding duplicate rows
            for document in TM.crew_document.search(searchStr):

                (crew_key, doc_key, validfrom_key) = Document.getKeys(document)
            
                searchStr2 = '(&(doc=%s)(validfrom=%s))' % (doc_key, validfrom_key) #(doc, document.validfrom)
                     
                items = 0
                for row in TM.tmp_ctl_document.search(searchStr2):
                    items += 1
                
                if items == 0:
                    if not dryRun:
                        if document.doc.subtype in DOCUMENT_BLACKLIST and (document.si is None or "FORCE" not in document.si):
                            errorText = "WARNING: " + str(document.doc.subtype) + " is not supposed to be removed. To enforce: 1) Press 'Refresh'. 2) Write 'FORCE' in the 'SI' and press 'Apply' twice. 3) Press 'Remove' and then 'Apply' "
                            raise ValidationException(errorText, 'tmp_ctl_document')
                        removed_rows.append(str(document))
                        document.remove()
                        changes = True
                elif items == 1:
                    continue
                else:
                    errorText = "Please remove duplicate rows (Document=" +  str(doc_key) + ", Valid From=" + str(validfrom_key) + ")" 
                    raise ValidationException(errorText,
                                              'tmp_ctl_document')
            
            
            
            crew_sum = TM.tmp_ctl_crew_summary[("0",)]
            docs = []
            for tmpDoc in TM.tmp_ctl_document:
                
                for item in (tmpDoc.doc, tmpDoc.validfrom):
                    if item is None:
                        raise ValidationException('Please enter all required fields',
                                                  'tmp_ctl_document')


                if(tmpDoc.validfrom > tmpDoc.modvalidto):
                    (crew_key, doc_key, validfrom_key) = Document.getKeys(tmpDoc)
                    errorText = "Valid To must be less than Valid From (Document=" +  str(doc_key) + ", Valid From=" + str(validfrom_key) + ")"   
                    raise ValidationException( errorText, 'tmp_ctl_document') 
                       
                              
                for check_doc in docs:               
                    if (check_doc.doc      == tmpDoc.doc       and
                        check_doc.ac_qual  == tmpDoc.ac_qual   and
                        check_doc.modvalidto   > tmpDoc.validfrom and 
                        check_doc.validfrom < tmpDoc.modvalidto):
                       
                        (crew_key, doc_key, validfrom_key) = Document.getKeys(tmpDoc)
                        errorText = "Documents not allowed to overlap (Document=" +  str(doc_key) + ", Valid From=" + str(validfrom_key) + ")"   
                        raise ValidationException( errorText, 'tmp_ctl_document')
            
                docs.append(tmpDoc)
                added = False
            
            
                doc = Document.getDoc(tmpDoc)
                if not dryRun:
                    try:
                        document = TM.crew_document.create((crew, doc, tmpDoc.validfrom))
                        if document.doc.subtype in DOCUMENT_BLACKLIST and (document.si is None or "FORCE" not in document.si):
                            errorText = "WARNING " + str(document.doc.subtype) + "is not supposed to be created manually. Write 'FORCE' in 'SI' to force."
                            raise ValidationException( errorText, 'tmp_ctl_document')
                        added = True
                    except EntityError:
                        document = TM.crew_document[(crew, doc, tmpDoc.validfrom)]
                        orig_document = str(document)
                        
                    changes = True
                    document.validto =  TimeUtil.inclDateToExclTime(tmpDoc.modvalidto)
                
                    # Check ac qualification
                    # if LC and longhaul crew or if LPC/OPC/OTS and 737 crew:
                    #   check that ac qual for sim type matches crew ac qual.
                
                    ac_qual = ValidDocno.getDocno(tmpDoc.ac_qual)
                
                    if (doc.subtype in EXCLUDE_CONDITION_TUPLE):
                        document.ac_qual = ac_qual
                
                    document.docno = tmpDoc.docno
                    document.issuer = tmpDoc.issuer
                    document.si = tmpDoc.si
                
                    rev_document = str(document)
                    if added:
                        added_rows.append(rev_document)
                    else:
                        if rev_document != orig_document:
                            modified_rows.append((orig_document, rev_document))
                #end if
                
            if dryRun:
                dryRun = False
            else:
                break 
            
        #end while 
         
        # Logging             
        for row in removed_rows:
            if row not in added_rows:
                log("CrewTraining: REMOVED %s" % row)
        for row in added_rows:
            if row not in removed_rows:
                log("CrewTraining: ADDED %s" % row)
        for orig,rev in modified_rows:
            log("CrewTraining: UPDATE ORIG %s" % orig)
            log("CrewTraining:         REV %s" % rev)
            
        return changes

class Rehearse(TempTable):
    """
    Temporay class that rehearsel rec info for crew.
    """
    _name = 'tmp_ctl_rehearse'
    _keys = [RefColumn('id', 'crew', 'CrewId')]
    _cols = [BoolColumn("is_allowed", "Crew is valid for rehearsel rec")]

    @staticmethod
    def getSourceTable():
        return TM.crew_rehearsal_rec

    @staticmethod
    def getKeyNames():
        return ("crew")
    
    @staticmethod   
    def getKeys(row):
        global crewId
        return (crewId)

    @staticmethod
    def getValueNames():
        return ("is_allowed")

    @staticmethod   
    def getValues(row):
        return (row.is_allowed)

    _table_search = "(crew=%s))"

    def __init__(self, crewId):
        TempTable.__init__(self)
        self.populate(crewId)
        self.unsavedChanges = False

    def populate(self, crewId):
        self.removeAll()
        if crewId is None:
            return

        crew_ent = TM.crew[(crewId,)]
        
        rehearse_doc = self.create((crew_ent,))
        try:
            rehearse_rec = TM.crew_rehearsal_rec[(crew_ent,)]
            rehearse_doc.is_allowed = True
        except:
            rehearse_doc.is_allowed = False
            
    def setUnsaved(self, status=True):
        self.unsavedChanges = status

    def save(self):

        global crewId
        add = False
        delete = False
        
        crew = TM.crew[(crewId,)]        
         
        rehearse_doc = TM.tmp_ctl_rehearse[(crew,)] 
        
        exist_in_table = True
        try:
            rehearse_rec = TM.crew_rehearsal_rec[(crew,)]
        except:
            exist_in_table = False
            
        if (exist_in_table and not rehearse_doc.is_allowed):
            delete = True
        elif (not exist_in_table and rehearse_doc.is_allowed):
            add = True
        else:
            return False
            
        if utils.wave.STANDALONE:
            TM.newState()
            
        if add:
            rehearse_rec = TM.crew_rehearsal_rec.create((crew,))
            log("CrewTraining: ADDED %s" % rehearse_rec)
            
        if delete:
            rehearse_rec.remove()
            log("CrewTraining: REMOVED %s" % rehearse_rec)
            
        return True
            

def refresh(plan, table):
    """
    Refreshes the specified table.
    """
    global crewId
    global DocumentTable
    global NeedTable
    global NeedRowTable
    
    error = False
    message = " "
    #Refresh with DB
    TM.refresh()
    if crewId is None:
        message = "Can't refresh without crew specified"
        error = True
    elif table == 'tmp_ctl_log':
        TrainingLogTable(crewId)
        message = "Training log was refreshed"
    elif table == 'tmp_ctl_landing':
        LandingTable(crewId)
        message = "Landing log was refreshed"
    elif table == 'tmp_ctl_need':
        NeedTable = Need(crewId)
        NeedRowTable = NeedRow(crewId)
        message = "Need table was reloaded"
    elif table == 'tmp_ctl_document':
        DocumentTable = Document(crewId)
        message = "Document table was reloaded"
    else:
        message = "Not implemented for the current view"
    setStatusMessage(plan, message, error)


def addRow(plan, table, rowid):
    """
    Adds a row to the specified table.
    """
    global crewId
    global FormInfoTable
    global DocumentTable
    global NeedTable
    global NeedRowTable

    if utils.wave.STANDALONE:
        time = FormInfoTable.getTime()
    else:
        time, = R.eval('fundamental.%pp_start%')
        
    error = False
    message = " "
    if crewId is None:
        message = "Can't add without crew specified"
        error = True
    elif table == 'tmp_ctl_need' or table == 'tmp_ctl_need_head':
        message = "New need added"
        NeedTable.createRow(time, rowid)
    elif table == 'tmp_ctl_need_row':
        message = "New need row added"
        NeedRowTable.createRow(rowid)
    elif table == 'tmp_ctl_document':
        message = "New document added"
        DocumentTable.createRow(time)
    else:
        message = "Not implemented for the current view"
    setStatusMessage(plan, message, error)


def deleteRow(plan, table):

    global crewId
    global DocumentTable
    global NeedTable
    global NeedRowTable
    
    error = False
    message = " "
    if crewId is None:
        message = "Can't delete row without crew specified"
        error = True
    elif table == 'tmp_ctl_need' or table == 'tmp_ctl_need_head' or table == 'tmp_ctl_need_row':
        message = "Need removed"
        NeedTable.setUnsaved()
    elif table == 'tmp_ctl_document':
        message = "Document removed"
        DocumentTable.setUnsaved()
    else:
        message = "Not implemented for the current view"
    setStatusMessage(plan, message, error)

    
def setCrew(plan, id):
    """
    Sets crew used in form.
    """
    global crewId
    id = id.encode("latin-1")
    utils.wave.refresh_wave_values()
    nowTime = utils.wave.get_now_utc(True)

    rows = []
    ldap = '(|(crew.id=%s)(extperkey=%s))' % (id, id)
    for crew in TM.crew_employment.search(ldap):
        try:
            if crew.validfrom <= nowTime and crew.validto >= nowTime:
                crewId = crew.crew.id
                break
            else:
                rows.append(crew)  
        except:
            pass
    else:
        if rows:
            rows.sort(cmp = lambda x,y: cmp(x.validto, y.validto))
            crewId = rows[-1].crew.id

    if crewId is None:
        message = ("Crew '%s' not found."
                   "Please enter a valid employment number and press enter."
                  ) % id
        setStatusMessage(plan, message, error=True)
    else:
        initTables(plan)


def setStatusMessage(plan, message=" ", error=False):
    global FormInfoTable
    print "setStatusMessage::",type(message),message
    FormInfoTable.setStatusMessage(message, error)


def initTables(plan):
    """
    Initiates tables in form.
    """

    global crewId

    global FormInfoTable
    global DocumentTable
    global NeedTable
    global RehearseTable
    global NeedRowTable

    # Set the menu state OpenWaveForms to hide Undo buttons in Studio
    # on opening wave forms (Crew Info, Crew Accounts, Crew Training,
    # Crew Block Hours). SASCMS-4562
    if not utils.wave.STANDALONE:
        MenuState.setMenuState('OpenWaveForms', 1, forceMenuUpdate = True)
    
    log("CrewTraining ========== GETTING CREW %s" % crewId)
    
    logMessage("Building forminfo temptable")
    FormInfoTable = FormInfo(crewId)
    logMessage("Building crewinfo temptable")
    CrewInfoTable(crewId)
    logMessage("Building temptable for docno")
    ValidDocno(crewId)
    logMessage("Building document temptable")
    DocumentTable = Document(crewId)
    logMessage("Building training log temptable")
    TrainingLogTable(crewId)
    logMessage("Building landing temptable")
    LandingTable(crewId)
    logMessage("Building training need temp table")
    NeedTable = Need(crewId)
    NeedRowTable = NeedRow(crewId) 
    logMessage("Building rehearsel table")
    RehearseTable = Rehearse(crewId)
    logMessage("Done creating temptables")
    logMessage("Building system temptable")
    SystemTable()
    DocExcludeCondTable = DocExcludeCondition()

def logMessage(messageString):
    if VERBOSE:
        Errlog.log(messageString)

def start():
    """
    Starts the leave account view within studio.
    """
    import StartTableEditor
    global crewId
    global MAX_LENGTH_SI

    assert not utils.wave.STANDALONE

    formHeader = "Crew Training"
    formName = "crew_training.xml"
    fullFormPath = '$CARMUSR/data/form/'+formName
    
    if str(StartTableEditor.getFormState(fullFormPath)).lower() not in ('none', 'error'):
        cfhExtensions.show("Crew Training Form is open,\nplease reuse already open form!")
        return 
        
    VERBOSE, = R.eval('fundamental.%debug_verbose_mode%')
    CREW_AREA = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # Get crew id
    #crewId = Cui.CuiCrcEvalString(
    #    Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%id%')

    # MAX_LENGTH_SI
    entity_description =  TM.crew_training_need.entityDesc()
    MAX_LENGTH_SI = entity_description.maxsize(entity_description.column('si'))
    
    crewId = Cui.CuiCrcEvalString(
        Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crr_crew_id')

    # Start the form
    StartTableEditor.StartTableEditor(['-f', fullFormPath])


def saveChanges(plan, inputErrors):
    global crewId
    global FormInfoTable
    global DocumentTable
    global NeedTable
    global NeedRowTable
    global RehearseTable
    
    if int(inputErrors):
        message = "Error in user input. Erroneous data outlined in red."
        message += " Note: The error may be located in another tab."
        FormInfoTable.setStatusMessage(message=message, isErrorMessage=True)
        return
    try:
        log("CrewTraining ---------- SUBMIT CREW %s" % crewId)
        changes = False
        
        for table in (DocumentTable, NeedRowTable, NeedTable, RehearseTable):
            changes |= not not table.save()

        if not changes:
            msg = "There are no changes."
            FormInfoTable.setStatusMessage()
        else:
            for table in ('tmp_ctl_document', 'tmp_ctl_need', 'tmp_ctl_rows'):
                refresh(plan, table)
            if not utils.wave.STANDALONE:
                Cui.CuiReloadTable('crew_document', 1)
                Cui.CuiReloadTable('crew_training_need', 1)
                Cui.CuiReloadTable('crew_rehearsal_rec', 1)
                HF.redrawAllAreas(Cui.CrewMode)
            else:
                TM.save()
            msg = "Changes successfully applied."
            
        log("CrewTraining ---------- %s" % msg)
        FormInfoTable.setStatusMessage(msg)
        FormInfoTable.setUnsaved(False)
          
    except ValidationException, ex:
        FormInfoTable.setStatusMessage(message=str(ex), isErrorMessage=True, errorTable=ex.errorTable)
    except SaveException, ex:
        FormInfoTable.setStatusMessage(message=str(ex), isErrorMessage=True, errorTable=ex.errorTable)


def checkChanges(plan):
    global FormInfoTable
    global DocumentTable
    global NeedTable
    global NeedRowTable
    
    (unsavedDocs, mod_docs) = DocumentTable.checkForChanges()
    (unsavedNeed, mod_need) = NeedTable.checkForChanges()
    (unsavedNeedRow, mod_needrow) = NeedRowTable.checkForChanges()
    
    unsaved = (unsavedNeed or unsavedDocs or unsavedNeedRow)
    if unsaved:
        message = "There are changes in"
        addmsg  = ""
        if unsavedDocs:
            message += " document"
            addmsg   = " and"
        if unsavedNeed or unsavedNeedRow:
            message += "%s need" % addmsg
    else:
        message = "There are no changes"
    FormInfoTable.setUnsaved(unsaved)
    setStatusMessage(plan, message, unsaved)
        

# Register functions
from utils.wave import LocalService, unicode_args_to_latin1 as u2l
class ctl_init_tables(LocalService):       func = initTables
class ctl_save_changes(LocalService):      func = saveChanges
class ctl_check_for_changes(LocalService): func = checkChanges
class ctl_set_crew(LocalService):          func = u2l(setCrew)
class ctl_add_row(LocalService):           func = addRow
class ctl_del_row(LocalService):           func = deleteRow
class ctl_refresh(LocalService):           func = refresh
class ctl_set_message(LocalService):       func = u2l(setStatusMessage)

