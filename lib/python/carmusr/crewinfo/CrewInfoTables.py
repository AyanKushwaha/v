# When creating a new tab, create a child class of the CrewInfoTempTable
# class to hold the table which the tab shall show. 
# 
# [acosta:08/095@11:57] Added Profile tab (see CR 101), note that Last flown is
# commented out, until we get full spec of this functionality.
#

import modelserver as M
from carmusr.crewinfo.CrewInfoClasses import *
from modelserver import ReferenceError as ReferenceError
from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
from tm import TM
from tm import TempTable
import traceback
import carmusr.TimeUtil as TimeUtil
import carmusr.crewinfo.crew_profile as crew_profile
import cmsadm.credentials
import time
import re
import CrewInfo
import Dates
import utils.wave
import utils.Names as Names
from carmusr.VirtualQualification import (virtual_to_real_quals,
        virtual_to_real_US_airport_quals)
from utils.dave import EC
from utils.performance import log
from utils.time_util import IntervalSet, TimeInterval

RE_EXTPERKEY = re.compile(r'\d\d\d\d\d')

############################## FUNCTIONS ######################################

# Emerging design element...
# Root object for all tables in the context of one crew.
# NowTime and CrewID could be moved here e.g.
# Every table has a reference to one Context object
# to gain access to common resources instead of storing
# them per table or in globals.
# If there need to be globals (to avoidGC), the context
# object should be the single one.
# Storing each table as an object attribute instead of
# looking up by table name would make sense; they are
# all known at design time.

def check_startdate_only(typ):
    """Limited qualifications with end date after the aircraft qualification are allowed for some types"""
    types_with_relaxed_check = ["AIRPORT"]
    return typ in types_with_relaxed_check


class CrewInfoContext(object):

    @staticmethod
    def create(nowTime, crewId, tmpTablesPrefix):
        return CrewInfoContext(
                   nowTime, crewId,
                   FormInfo(nowTime, crewId, tmpTablesPrefix),
                   ErrorInfo(tmpTablesPrefix),
                   CrewInfoTables.create(nowTime, crewId, tmpTablesPrefix))
                                                      

    def __init__(self, nowTime, crewId, formInfo, errorInfo, crewTables):
        self.nowTime = nowTime
        self.crewId = crewId
        self.formInfo = formInfo
        self.errorInfo = errorInfo
        self.tables = crewTables
        self.tm = M.TableManager.instance()
        self.initialize()

    def initialize(self):
        log("CrewInfo ========== GETTING CREW %s" % self.crewId)
        for t in self.tables:
            t.cxt = self
            t.formInfoTable = self.formInfo.getTable()
            
        [t.afterAllTablesLoaded() for t in self.tables]

    def refresh(self, nowTime=None, crewId=None):
        if nowTime:
            self.nowTime = nowTime
        if crewId:
            self.crewId = crewId
    
        for t in self.tables.regular():
            t.refresh(self.nowTime, self.crewId)
        
        self.initialize()

        
    def clear(self):
        [t.clear() for t in self.tables]


    def crewMainCategory(self, date):
        try:
            for row in CrewInfo.cxt.tables.CrewEmployment:
                # Please note that in the temp-tables, both validfrom and -to
                # are inclusive. (Not as in db, where validto is exclusive.)
                if row.validfrom<=date and row.validto>=date:
                    return row.crewrank.maincat.id
        except:
            raise Exception('Error in finding crew main category.')
        raise Exception('Could not find valid rank for crew. Check crew employment at %s.' % date.ddmonyyyy(True))
        
    def addError(self, error):
        self.errorInfo.handleError(error)

    def getNowTime(self):
        return self.formInfo.getTime()
        
        
class ValidationException(Exception):
    def __init__(self, message, errorTable=None):
        Exception.__init__(self, message)
        self.errorTable = errorTable
                

class SaveException(Exception):
    def __init__(self, message, errorTable=None):
        Exception.__init__(self, message)
        self.errorTable = errorTable
        

class CrewInfoTables(object):
    '''
    Table container where tables can be accessed as attributes
    (using the table class name as attribute name) or by indexing
    with the table name. There are methods to access derived or regular
    (non-derived) tables.
    '''
    @staticmethod
    def create(nowTime, crewId, tmpTablesPrefix):
        tablesToLoad = (
            CrewSummary(nowTime, crewId, tmpTablesPrefix),
            CrewAddress(nowTime, crewId, tmpTablesPrefix),
            CrewContact(nowTime, crewId, tmpTablesPrefix),
            CrewContract(nowTime, crewId, tmpTablesPrefix),
            CrewDocument(nowTime, crewId, tmpTablesPrefix),
            CrewEmployment(nowTime, crewId, tmpTablesPrefix),
            ProhibitedCrew(nowTime, crewId, tmpTablesPrefix),
            CrewQualification(nowTime, crewId, tmpTablesPrefix),
            CrewRestriction(nowTime, crewId, tmpTablesPrefix),
            CrewSeniority(nowTime, crewId, tmpTablesPrefix),
            CrewSpecSched(nowTime, crewId, tmpTablesPrefix),
            CrewQualAcqual(nowTime, crewId, tmpTablesPrefix),
            CrewRestAcQual(nowTime, crewId, tmpTablesPrefix),
            CrewProfile(nowTime, crewId, tmpTablesPrefix),
        )
        
        return CrewInfoTables(tablesToLoad, tmpTablesPrefix)
        
    def __init__(self, tables, tmpTablesPrefix):
        self.tablePrefix = tmpTablesPrefix
        d = {}
        for t in tables: d[t.getName()] = t
        self.__tablesDict = d
        [setattr(self, t.__class__.__name__, t) for t in d.itervalues()]

    def asDict(self):
        return self.__tablesDict

    def regular(self):
        return [t for t in self.__tablesDict.itervalues()]

    def __iter__(self):
        return self.__tablesDict.itervalues()

    def __getitem__(self, key):
        return self.__tablesDict[key]
        

def timeInInterval(time, startTime, endTime):
    return time >= startTime and time <= endTime

def isTouching(startTime1, endTime1, startTime2, endTime2):
    if startTime1 is None or endTime1 is None \
       or startTime2 is None or endTime2 is None:
        return False
    else:
        return startTime1 <= endTime2 and endTime1 >= startTime2

def overlappingRows(row1, row2):
    return isTouching(row1.validfrom, row1.validto,
                      row2.validfrom, row2.validto)
        
############################## SPECIAL TABLES #################################
        
class FormInfo(CrewInfoTempTable):
    # This class contains information regarding the form. The class is not
    # dependant on crewId

    TM_NAME = "form_info"

    def __init__(self, nowTime, crewId, tablePrefix="tmp_"):
        self.tablePrefix = tablePrefix
        tableName = tablePrefix + FormInfo.TM_NAME
            
        cols = [M.StringColumn("user", "User"),
                M.DateColumn("time", "Form Time"),
                M.StringColumn("status_message", "Status Bar Message"),
                M.StringColumn("status_color", "Status Bar Color"),
                M.StringColumn("error_table", "Table having validation errors"),
                M.BoolColumn("unsaved_changes", "Unsaved Changes Exist"),
                M.StringColumn("user_role", "User Role (for access rights)"),
                ]

        CrewInfoTempTable.__init__(self, tableName, cols)

        self.populateTable(nowTime, crewId)
        
    def populateTable(self, nowTime, crewId):
        self.clear()
        index = self.getAndIncreaseRunningNo()
        row = self.create((index,))
        row.user = Names.username()
        row.time = nowTime
        if crewId is None:
            row.status_message = \
              "No or illegal crew selected. Please select a valid crew"
        else:
            row.status_message = ""
        row.status_color = "transparent"
        row.user_role = cmsadm.credentials.getRole()
        row.unsaved_changes = False

    def setStatusMessage(self, message='', isErrorMessage=False, errorTable=None):
        for row in self:
            row.status_message = (message or "")[:200]
            row.status_color = "transparent"
            if isErrorMessage:
                row.status_color = "red"
            if errorTable:
                row.error_table = errorTable 
            break

    def setUnsaved(self, status):
        for row in self:
            row.unsaved_changes = status
            break

    def getTime(self):
        for row in self:
            return row.time
        

class CrewSummary(CrewInfoTempTable):
    """
    Crew information shown at the top of the crew info form.
    """

    TM_NAME = "crew_summary"

    __crewId = None
    __nowTime = None
    
    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewSummary.TM_NAME

        cols = [M.StringColumn("name", "Login Name"),
                M.StringColumn("id", "Employment Number + (Crew Id)"),
                M.StringColumn("crewid", "Crew Id"),
                M.StringColumn("empno", "Employment Number"),
                M.StringColumn("ph_primary", "Primary Phone Number"),
                M.StringColumn("ph_secondary", "Secondary Phone Number"),
                M.StringColumn("gender", "Gender"),
                M.StringColumn("forename", "Forname"),
                M.StringColumn("surname", "Surname"),
                M.StringColumn("birthday", "Date of Birth"),
                M.StringColumn("bcity", "Birth City"),
                M.StringColumn("bcountry", "Birth Country Code"),
                M.StringColumn("rank", "Rank"),
                M.StringColumn("maincat", "Main Category"),
                M.StringColumn("seniority", "Seniority"),
                M.StringColumn("base", "Home Base"),
                M.StringColumn("station", "Station"),
                M.StringColumn("pg_desc", "Planning Group"),
                M.StringColumn("acqual", "A/C Qual"),
                M.StringColumn("retday", "Retirement day"),
                M.StringColumn("company", "Company"),
                M.StringColumn("contract", "Contract"),
                M.StringColumn("bxmodule", "Module"),
                M.StringColumn("laborunion", "Labour Union"),
                M.StringColumn("cyclestart", "Cycle Start"),
                M.StringColumn("pattern", "Pattern"),
                M.StringColumn("grouptype", "Group Type")]
        
        CrewInfoTempTable.__init__(self, self.tableName, cols)
        if crewId is not None:
            self.__crewId = crewId
            self.__nowTime = nowTime
            self.populateTable()

    def populateTable(self):
        crewId = self.__crewId
        nowTime = self.__nowTime
        self.clear()
        index = self.getAndIncreaseRunningNo()
        row = self.create((index,))

        searchCriteria = "(&(crew.id=%s)(validfrom<=%s)(validto>%s))" \
                         %(crewId, nowTime, nowTime)

        # Prevent empty cells from turning blue
        ed = self.entityDesc()
        for i in range(ed.size()):
            setattr(row, ed.fieldname(i), " ")
            
        row.crewid = crewId
        try:
            info = TM.crew[(crewId,)]
            row.name = info.logname or " "
            row.forename = info.forenames or " "
            row.surname = info.name or " "
            row.gender = info.sex or " "
            row.retday = row.birthday = " "
            if info.retirementdate:
                row.retday = str(AbsDate(info.retirementdate))
            if info.birthday:
                row.birthday = str(AbsDate(info.birthday))
            row.bcity = info.bcity or " "
            row.bcountry = info.bcountry or " "            
            for info in info.referers('crew_extra_info', 'id'):
                if info.validfrom <= nowTime < info.validto:
                    row.name = info.logname or row.name
                    row.forename = info.forenames or row.forename
                    row.surname = info.name or row.surname
                    break
        except:
            pass
        
        for info in TM.crew_employment.search(searchCriteria):
            try:
                if info.extperkey is not None:
                    row.id = "%s (%s)" % (info.extperkey, crewId)
                    row.empno = info.extperkey
            
                row.rank = info.crewrank.id or " "
                row.base = info.base.id  or " "
                row.station = info.station  or " "
                row.pg_desc = "%s (%s)" % (info.planning_group.id or " ", info.planning_group.si or " ")
                # FIXED SO THAT THE CORRECT MAINCAT FOR CABIN IS "C"
                try:
                    row.maincat = {"F":"F","A":"C", "C":"C"}[info.crewrank.maincat.id]
                except KeyError:
                    row.maincat = info.crewrank.maincat.id or " "
                row.company = info.company.id or " "
            except M.ReferenceError, instance:
                self.addReferenceError(instance)

        try:
            c_info = [(x.which.which, x) for x in TM.crew_contact.search("(&(crew=%s)(|(typ=Tel)(typ=Mobile)))" % crewId)]
            c_info.sort()
            (got_primary, got_secondary) = (False, False)
            for (which, info) in c_info:
                phone = info.val.strip()
                if phone:
                    if which.lower() == "main":
                        row.ph_primary = phone
                        got_primary = True
                    elif which.lower()[:4] in ("home", "main"):
                        if got_primary:
                            row.ph_secondary = "%s (%s)" % (phone, info.typ.typ)
                            got_secondary = True
                        else:
                            row.ph_primary = "%s (%s)" % (phone, info.typ.typ)
                            got_primary = True
                if got_primary and got_secondary:
                    break
        except M.ReferenceError, instance:
            self.addReferenceError(instance)

        for contract in TM.crew_contract.search(searchCriteria):
            try:
                if contract.contract.agmtgroup:
                    ag = contract.contract.agmtgroup.id
                else:
                    ag = "?"
                row.contract = contract.contract.id + " (" + \
                               contract.contract.descshort + "," + ag + ")"
                row.cyclestart = str(contract.cyclestart)
                row.grouptype = str(contract.contract.grouptype)
                if contract.contract.pattern:
                    row.pattern = "%s (%s)" % (contract.contract.pattern.id,
                                               contract.contract.pattern.descshort)
                row.laborunion = contract.contract.laborunion or " "
                row.bxmodule = contract.contract.bxmodule or " "
            except M.ReferenceError, instance:
                self.addReferenceError(instance)
            break # There SHOULD be only one

        qualString = ""
        acqualCriteria = searchCriteria[:-1] + "(qual.typ=ACQUAL))"
        for acqual in TM.crew_qualification.search(acqualCriteria):
            try:
                qualString += acqual.qual.subtype + ", "
            except M.ReferenceError, instance:
                self.addReferenceError(instance)
        row.acqual = qualString[:-2]

        for seniority in TM.crew_seniority.search(searchCriteria):
            row.seniority = str(seniority.seniority)
            break # There should only be one
            

    def refresh(self, nowTime=None, crewId=None):
        if nowTime:
            self.__nowTime = nowTime
        if crewId:
            self.__crewId = crewId
        self.populateTable()
        
    def createRow(self):
        pass
    
    def createNewRow(self, *keys):
        pass
    
    def findAddedRows(self):
        return []

    def findRemovedRows(self):
        return []

    def findModifiedRows(self):
        return []

    def changesExist(self):
        return False

    def save(self):
        return ""
        
    def validate(self, nowTime, rows=[]):
        return  ""

            
class ErrorInfo(CrewInfoTempTable):
    """
    This class contains information regarding the form.
    The class is not dependant on crewId.
    """ 

    TM_NAME = "errors"

    def __init__(self, tablePrefix="tmp_"):
        self.tablePrefix = tablePrefix
        
        tableName = tablePrefix + ErrorInfo.TM_NAME
            
        cols = [M.StringColumn("error_desc", "Error Description")]

        CrewInfoTempTable.__init__(self, tableName, cols)
        self.clear()
        
    def handleError(self, errorInstance):
        error_desc = errorInstance.args[0].split(":")[-1]
        if not error_desc in [row.error_desc for row in self]:
            index = self.getAndIncreaseRunningNo()
            row = self.create((index,))
            row.error_desc = error_desc
        
    def clear(self):
        self.removeAll()
        
    def errorExist(self):
        for row in self:
            return True
        return False

    def errorMessage(self):
        message = ""
        if self.errorExist():
            message = "Data error found. Please check File->Errors for "
            message += "further information"
        return message
        
    def populateTable(self):
        self.clear()
    
############################### RESTRICTIONS ##################################

class CountryRestriction(CrewInfoResTable):
    """
    Contains the available countries for the Crew Employment table
    """
    TM_NAME = "country_set"
    def __init__(self, tablePrefix="tmp_"):

        tableName = tablePrefix + CountryRestriction.TM_NAME
        #"tmp_cbi_country_set"
        key = [M.StringColumn("id", "Country")]
        values = ["DK", "SE", "NO", "CN", "HK", "JP"]

        CrewInfoResTable.__init__(self, tableName, key, values)

############################### TABBED TABLES #################################

class ExtraValidations:
    """
    This adds overlap validation to CrewInfoTempTable
    """
    def overlapValidation(self):
        # Make sure there are no overlaps
        tm = M.TableManager.instance()
        tmp_table = tm.table(self.getName())
        changedRows = self.rowsToCheckValidity()
    
        for cmpRow in changedRows:
            for row in tmp_table:
                if self.docsSameType(cmpRow, row) and overlappingRows(cmpRow, row) and not row == cmpRow:
                    return (str(cmpRow.validfrom)[:-5], str(row.validfrom)[:-5]) 
        return (None, None)

    def docsSameType(self, row1, row2):
        return True


    def referenceValidation(self, column, label=None):
        label = label or column
        tm = M.TableManager.instance()
        tmp_table = tm.table(self.getName())
        changedRows = self.rowsToCheckValidity()
        for cmpRow in changedRows:
            for row in tmp_table:
                try:
                    if row.getRef(column) is None:
                        raise 'Err'
                except:
                    return "In %s, column %s must not be empty." \
                        % (self.getDisplayName(), label)
        return None


    def strLengthValidation(self, colname, dispname, limit):
        changedRows = self.rowsToCheckValidity()
        for cmpRow in changedRows:
            value = str(cmpRow.nget(colname))
            if len(value) > limit:
                if len(value) > 40:
                    value = value[:37]+"..."
                return "In %s, column %s is limited to %s characters." \
                       " The value '%s' is too long." \
                       % (self.getDisplayName(), dispname, limit, value)
        return None
    
    

# --> Address Tab Classes <-- #
class CrewAddress(CrewInfoTempTable):
    """
    Temporary table used to display the information of the "Address" tab
    """
    TM_NAME = "crew_address"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewAddress.TM_NAME
        
        countrySet = CountryRestriction(tablePrefix).getName()

        source = TM.crew_address
        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.StringColumn("street", "Street"),
                M.StringColumn("city", "City"),
                M.StringColumn("state", "State"),
                M.StringColumn("postalcode", "Postal Code"),
                M.StringColumn("country", "Country"),
                M.StringColumn("street1", "Second Street"),
                M.StringColumn("city1", "Second City"),
                M.StringColumn("state1", "Sceond State"),
                M.StringColumn("postalcode1", "Second Postal Code"),
                M.StringColumn("country1", "Second Country"),
                M.StringColumn("si", "Si")]
        
        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_address", defaultKeys)
        CrewInfoTempTable.__init__(self,
                                   self.tableName,
                                   cols,
                                   dispName='Address',
                                   isReadOnly=True)

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

# --> Contact Tab Classes <-- #
class CrewContact(CrewInfoTempTable):
    """
    Temporary table used to display the information of the "Contacts" tab
    """
    TM_NAME = "crew_contact"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewContact.TM_NAME
        
        source = TM.crew_contact
        cols = [M.RefColumn("typ", "crew_contact_set", "Type of Entry"),
                M.RefColumn("which", "crew_contact_which", "Where the Entry is to"),
                M.StringColumn("val", "Value of the Entry"),
                M.StringColumn("si", "Supplementory Information")]

        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        
        CrewInfoTempTable.addSourceInfo(self, "crew_contact", defaultKeys)
        CrewInfoTempTable.__init__(self,
                                   self.tableName,
                                   cols,
                                   dispName='Contact',
                                   isReadOnly=True)

    def createRow(self, nowTime):
        return self.createNewRow()

# --> Contract Tab Classes <-- #
class CrewContract(CrewInfoTempTable, ExtraValidations):
    """
    Temporary table used to display the information of the "Contracts" tab
    """
    TM_NAME = "crew_contract"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewContract.TM_NAME

        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("contract", "crew_contract_valid", "Contract Set"),
                M.IntColumn("cyclestart", "Cycle Start"),
                M.StringColumn("endreason", "End Reason"),           
                M.StringColumn("si", "SI")]
        
        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_contract", defaultKeys)

        referenceMap = {"id": "contract"}
        
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   referenceMap=referenceMap,
                                   dispName='Contract')

        self.contractDetails = ContractDetails(self, tablePrefix)

    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Contract:: %s" % message
            
        # Make sure there are no overlapping rows
        time1, time2 = self.overlapValidation()
        if time1 or time2:
            return "Only one contract may be valid at any given time. "\
                   "Contracts starting %s and %s overlap" % (time1, time2)
                   
        message = self.referenceValidation('contract','Contract')
        if message:
            return message
            
        rows = self.rowsToCheckValidity()
        if not rows:
            return ""
            
        for row in rows:
            try:
                id = row.contract.contract.id
            except M.ReferenceError:
                return "Contract starting %s "%row.validfrom.ddmonyyyy(True) +\
                       "has no valid contract in table crew_contract_set"
            
            # Validate cyclestart.
            
            if row.cyclestart is None:
                return "Contract starting %s has no Cycle start"%row.validfrom.ddmonyyyy(True)
            if row.contract.contract.id.upper().startswith('F') and row.cyclestart < 1:
                return "Contract starting %s is F-group but has Cycle Start less than 1"%\
                       row.validfrom.ddmonyyyy(True)
                       
            # Check for matching employment(s)s overlapping the contract period.
            # Note: Employment is not required for retirement contracts
            #       and similar (contracts with empty base and maincat).
            # Note: We don't check if the contract period is entirely covered
            #       with employment entries; partial covarage will do.

            hasemp = False            
            ldap = '(&(validto>=%s)(validfrom<=%s))'%(row.validfrom,row.validto)
            for erow in CrewInfo.cxt.tables.CrewEmployment.search(ldap):
                hasemp = True
                def checkeattr(eattr, cattr, dattr):
                    if str(eattr) != str(cattr):
                        return "Contract %s %s-%s (%s,%s,%s) does not match employment %s-%s (%s)." % (
                                row.contract.contract.id,
                                str(row.validfrom).split(" ")[0],
                                str(row.validto).split(" ")[0],
                                (row.contract.maincat) or "",
                                (row.contract.base and row.contract.base.id) or "",
                                (row.contract.company and row.contract.company.id) or "",
                                str(erow.validfrom).split(" ")[0],
                                str(erow.validto).split(" ")[0],
                                dattr,
                                )
                message = (
                    (row.contract.maincat and
                     checkeattr(erow.crewrank.maincat.id, row.contract.maincat,
                                "crew main category %s" % erow.crewrank.maincat.id))
                    or (row.contract.base and
                        checkeattr(erow.base.id, row.contract.base.id,
                                   "base %s" % erow.base.id))
                    or (row.contract.company and
                        checkeattr(erow.company.id, row.contract.company.id,
                                   "company %s" % erow.company.id))
                    )
                if message:
                    return message
                    
            if not hasemp:
                ldap = ("(&(contract=%s)"
                          "(validfrom<=%s)(validto>=%s)"
                          "(!(maincat=*))(!(base=*))"
                        ")") % (row.contract.contract.id,
                                row.validfrom, row.validto + RelTime(24,0))
                for validrow in TM.crew_contract_valid.search(ldap):
                    break
                else:
                    return "Contract %s %s-%s is outside valid contract period." % (
                           row.contract.contract.id,
                           str(row.validfrom).split(" ")[0],
                           str(row.validto).split(" ")[0])
        
        return ""
        
    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        newRow.cyclestart = 0
        CrewInfoTempTable.merge_new_row_with_last(self, newRow, True)
        return newRow

    def showDetails(self, runningNo):
        return self.contractDetails.refresh(runningNo)

class ContractDetails(CrewInfoTempTable):
    
    TM_NAME = "crew_contract_details"
    
    def __init__(self, parentTable, tablePrefix):
        self.parentTable = parentTable._table
        tableName = tablePrefix + ContractDetails.TM_NAME
        
        cols = [M.StringColumn("id", "Id"),
                M.StringColumn("grouptype", "Group type"),
                M.StringColumn("pattern", "Pattern"),
                M.StringColumn("dutypercent", "Duty percent"),
                M.StringColumn("descshort", "Short description"),
                M.StringColumn("noofvadays", "Number of VA Days in Summer"),
                M.StringColumn("bxmodule", "Module"),
                M.StringColumn("laborunion","Labour Union"),
                M.StringColumn("agmtgroupid","Agreement Group Id"),
                M.StringColumn("agmtgroupdesc","Agreement Group"),
                ]
        
        CrewInfoTempTable.__init__(self, tableName, cols)
        self.clear()
    
    def clear(self):
        try:
            self._row = self.create((0,))
        except:
            self._row = self[(0,)]
        self._row.id = " "
        self._row.grouptype = " "
        self._row.pattern = " "
        self._row.dutypercent = " "
        self._row.descshort = " "
        self._row.noofvadays = " "
        self._row.bxmodule = " "
        self._row.laborunion = " "
        self._row.agmtgroupid = " "
        self._row.agmtgroupdesc = " "

    def populateTable(self):
        self.clear()

    def refresh(self, contract):
        self.clear()

        if contract == "NULL":
            return
            
        id = contract.split('+')[0] 
        self._row.id = id
        
        crew_contract_set_row = TM.crew_contract_set[(id,)]
        self._row.grouptype = crew_contract_set_row.grouptype
        try:
            self._row.pattern = crew_contract_set_row.pattern.descshort
        except:
            self._row.pattern = "(Not found: %s)" % crew_contract_set_row.pattern
        self._row.dutypercent = str(crew_contract_set_row.dutypercent)
        self._row.descshort = crew_contract_set_row.descshort
        self._row.noofvadays = str(crew_contract_set_row.noofvadays)
        self._row.bxmodule = crew_contract_set_row.bxmodule or " "
        self._row.laborunion = crew_contract_set_row.laborunion or " "
        if crew_contract_set_row.agmtgroup:
      	    self._row.agmtgroupid = crew_contract_set_row.agmtgroup.id or " "
            self._row.agmtgroupdesc = crew_contract_set_row.agmtgroup.si or " "
        else:
            self._row.agmtgroupid = " "
            self._row.agmtgroupdesc = " "

# --> Document Tab Classes <-- #    
class CrewDocument(CrewInfoTempTable, ExtraValidations):
    '''
    crew_document temp table.
    Uses temporary column "docno_masked" to handle formatting
    of certain license document numbers. The document number
    is  copied/formatted from source to temp column before
    being displayed, and copied back before saving to DB. 
    '''

    TM_NAME = "crew_document"
    DOCUMENT_BLACKLIST = ['LC', 'PC', 'PCA3', 'PCA3A5', 'PCA4', 'PCA5', 'OPC', 'OPCA3', 'OPCA3A5', 'OPCA4', 'OPCA5', 'CRM', 'CRMC', 'REC', 'PGT']
    
    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewDocument.TM_NAME
        
        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("doc", "crew_document_set", "Document"),
                M.StringColumn("maindocno", "Main Document Number"),
                M.StringColumn("docno", "Document Number"),
                M.StringColumn("docno_masked", "Document Number for display"),
                M.StringColumn("issuer", "Issuer"),
                M.StringColumn("ac_qual","Aircraft Qual"),
                M.StringColumn("si", "SI")]

        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_document", defaultKeys)
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Document')
    
    def columnNames(self):
        return [n for n in CrewInfoTempTable.columnNames(self) if n != "docno_masked"] 

    def checkForChanges(self):
        self.make_column_upper_case('ac_qual', 'issuer')
        self.moveTempColumnsData()
        return CrewInfoTempTable.checkForChanges(self)
        
    def save(self):
        self.make_column_upper_case('ac_qual', 'issuer')
        self.moveTempColumnsData()
        result = CrewInfoTempTable.save(self)
        self.formatRows()
        return result

    def afterAllTablesLoaded(self):
        CrewInfoTempTable.afterAllTablesLoaded(self)
        self.formatRows()
    
    def moveTempColumnsData(self):
        for row in self:
            docNo = row.docno_masked
            masked = docNo and '*' in docNo
            if not masked:
                row.docno = docNo
                
    def formatRows(self):
        map(self.formatDocNo, self)

            
    def formatDocNo(self, docRow):
        docNo = docRow.docno
        try:
            # CR62
            if docNo and docRow.doc and \
               docRow.doc.typ in ("LICENCE","MEDICAL"):
                docNo = self.maskLicenseDocNo(docRow.docno)
        except M.ReferenceError, instance:
                docNo = self.cxt.errorInfo.errorMessage() + " "
        docRow.docno_masked = docNo
        
    def maskLicenseDocNo(self, docNo):
        unmasked = docNo[0:-4]
        maskLength = len(docNo) - len(unmasked)
        return unmasked + ("*" * maskLength)    

            
    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow
    
    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Document:: %s" % message
        
        passports = []
        rows = self.rowsToCheckValidity()
        black_message = ''
        for rv in rows:
            document_rv = str(rv.getRefI("doc"))
            doc_subtyp = document_rv.split('+')[1]
            si_comment = str(rv.getString("si"))
            if document_rv.split('+')[0] == "REC" and set(CrewDocument.DOCUMENT_BLACKLIST).intersection(set([doc_subtyp])) and "FORCE" not in si_comment:
                black_message = str(doc_subtyp) + " is not supposed to be updated manually. Write 'FORCE' in 'SI' to force."

        # Make sure there are no overlaps
        time1, time2 = self.overlapValidation()

        if time1 or time2:
            return "Overlap for documents starting %s and %s" % (time1, time2) 
        
        tmp_table = self.cxt.tm.table(self.tableName)

        for row in tmp_table:
            try:
                typ = str(row.getRefI("doc")).split('+')[0]
                if typ and typ.upper() == "PASSPORT":
                    if timeInInterval(nowTime,
                                      row.validfrom,
                                      TimeUtil.inclDateToInclTime(row.validto)):
                        passports.append(str(row.docno))
            except AttributeError:
                continue
                
        if passports:
            for row in self:
                typ = str(row.getRefI("doc")).split('+')[0]
                if typ and typ.upper() == "VISA":
                    if row.maindocno not in passports:
                        return "Document:: The main document number for " \
                               "the VISA must be the passport number"
                               
        message = self.referenceValidation('doc') or \
                  self.acQualValidation() or \
                  self.strLengthValidation('ac_qual', 'Aircraft Qual', 10) or \
                  self.docNumberValidation() or \
                  self.issuerValidation() or \
                  self.tempPcPeriodValidation();
        if message:
            return "Document:: %s" % message
        elif black_message:
            return "Document:: %s" % black_message
            
        return ""


    def docRequiresAcQual(self, row):
        return ((row.doc.typ == 'REC' and row.doc.subtype in ['PC', 'OPC', 'LC']) or
                (row.doc.typ == 'LICENCE' and row.doc.subtype == 'Temp PC'))

            
    def acQualValidation(self):
        tm = M.TableManager.instance()
        changed_rows = self.rowsToCheckValidity()
        ac_quals = [row.subtype for row in TM.crew_qualification_set.search('(typ=ACQUAL)')]

        for row in changed_rows:
            if self.docRequiresAcQual(row) and not row.ac_qual in ac_quals:
                return 'Document starting at %s has invalid aircraft qualification "%s"' % (row.validfrom, row.ac_qual)
        return None


    def docRequiresDocNumber(self, row):
        return ((row.doc.typ in ('VISA', 'PASSPORT')) or
                ((row.doc.typ == 'LICENCE') and (row.doc.subtype != 'Temp PC')))


    def docNumberValidation(self):
        tm = M.TableManager.instance()
        changed_rows = self.rowsToCheckValidity()

        for row in changed_rows:
            if self.docRequiresDocNumber(row) and ((row.docno == None) or (len(row.docno) == 0)):
                return 'Document starting at %s must have document number' % row.validfrom
        return None


    def docRequiresIssuer(self, row):
        return ((row.doc.typ in ('VISA', 'PASSPORT')) or
                ((row.doc.typ == 'LICENCE') and (row.doc.subtype != 'Temp PC')))


    def issuerValidation(self):
        tm = M.TableManager.instance()
        changed_rows = self.rowsToCheckValidity()
        issuers = [row.id for row in TM.country]

        for row in changed_rows:
            if self.docRequiresIssuer(row) and not row.issuer in issuers:
                return 'Document starting at %s has invalid issuer "%s": must be two letter ISO code' % (row.validfrom, row.issuer)
        return None


    def tempPcPeriodValidation(self):
        tm = M.TableManager.instance()
        changed_rows = self.rowsToCheckValidity()

        for row in changed_rows:
            if (row.doc.typ == 'LICENCE' and row.doc.subtype == 'Temp PC' and
                (row.validto - row.validfrom) > (61 * RelTime('24:00'))):
                return 'Temp PC document starting at %s has too long validity period' % (row.validfrom)
        return None


    def docsSameType(self, row1, row2):
        if row1.doc.typ == row2.doc.typ and row1.doc.subtype == row2.doc.subtype:
            if row1.doc.typ == 'MEDICAL' and (row1.doc.subtype in ('-', 'C')):
                # Some documents are allowed to overlap
                return False
            elif self.docRequiresAcQual(row1):
                if row1.ac_qual == row2.ac_qual:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    
# --> Employment Tab Classes <-- #    
  
class StationSet(TempTable):
    """
    Set of crew_employment.station values for use as reference table in the
    CrewEmployment temporary table. This enables a dropdown box in the wave form.
    Station is not a reference column in the db, so we'll have to do it this way.
    Will be created and populated in CrewEmployment.__init__().
    """
    _name = 'tmp_cbi_station_set'
    _keys = [M.StringColumn('id','')]
    _cols = [M.TimeColumn('validto','')]
    
class CivicstationSet(StationSet):
    """
    Same as StationSet, but for crew_employment.civicstation.
    """
    _name = 'tmp_cbi_civicstation_set'
            
class CrewEmployment(CrewInfoTempTable, ExtraValidations):
    """
    Temporary table used to display the information of the "Employment" tab.
    """

    TM_NAME = "crew_employment"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):
        self.station_set = StationSet()
        self.civicstation_set = CivicstationSet()
        if self.station_set.size() <= 0:
            mindate = AbsTime("01Jan1901 00:00")
            maxdate = AbsTime("31Dec2099 23:59")
            stations = {}
            civicstations = {}
            for emprec in TM.crew_employment:
                if emprec.station:
                    stations[emprec.station] = \
                       max(stations.setdefault(emprec.station, mindate),
                           emprec.validto or maxdate)
                if emprec.civicstation:
                    civicstations[emprec.civicstation] = \
                       max(civicstations.setdefault(emprec.civicstation, mindate),
                           emprec.validto or maxdate)
            for station, validto in stations.items():
                if validto > mindate:
                    self.station_set.create((station,)).validto = validto
            for civicstation, validto in civicstations.items():
                if validto > mindate:
                    self.civicstation_set.create((civicstation,)).validto = validto

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewEmployment.TM_NAME
        self.__crewId = None # Needed for refresh
        self.__nowTime = nowTime
        countrySet = CountryRestriction(tablePrefix).getName()

        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("carrier", "crew_carrier_set", "Carrier"),
                M.RefColumn("company", "crew_company_set", "Company"),
                M.RefColumn("base", "crew_base_set", "Base"),
                M.RefColumn("country", countrySet, "Country"),
                M.RefColumn("crewrank", "crew_rank_set", "Rank"),
                M.RefColumn("titlerank", "crew_rank_set", "Title Rank"),
                M.RefColumn("planning_group", "planning_group_set", "Planning Group"),
                M.RefColumn("region", "crew_region_set", "Region"),
                M.RefColumn("civicstation", "tmp_cbi_civicstation_set", "Civic Station"),
                M.RefColumn("station", "tmp_cbi_station_set", "Station"),
                M.StringColumn("extperkey", "Employment Number"),
                M.StringColumn("si", "SI")]

        defaultKeys = None
        if crewId is not None:
            self.__crewId = crewId
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_employment", defaultKeys)
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Employment')

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        CrewInfoTempTable.merge_new_row_with_last(self, newRow, True)
        return newRow

    def save(self):
        # validate remove, Crew needs at least one employment row
        if len(self) < 1:
            # Restore to DB values
            self.populateTable(CrewEmployment.TM_NAME, clearTmp=True)
            return "Crew Employment:: Crew must have at least one crew employment row"
        # super class save
        message = CrewInfoTempTable.save(self)
        self.make_column_upper_case('station', 'civicstation')
        return message

    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Employment:: %s" % message
        
        # Make sure there are no overlaps
        time1, time2 = self.overlapValidation()

        if time1 or time2:
            message = "Only one employment may be valid at any given time. "
            message += "Employments starting %s and %s overlap" %(time1, time2)
            return message
        
        if not rows:
            rows = self.rowsToCheckValidity()
            if not rows:
                return message
                
        # Check input
        for col in ['carrier','company','base','country','crewrank','titlerank','planning_group',
                    'region','civicstation','station']:
            message = self.referenceValidation(col)
            if message:
                return message
        
        def mcat(rank):
            """Get maincat corresponding to a rank id."""
            if rank:
                for cat in TM.crew_rank_set.search("(id=%s)" % rank):
                    maincat = str(cat.getRefI('maincat'))
                    return (maincat == "A" and "C") or maincat
            return ""

        def mcstr(maincat):
            """Get maincat presentation string."""
            if str(maincat) == "F":
                return "Flight Crew"
            elif str(maincat) == "C":
                return "Cabin Crew"
            else:
                return "'%s'" % maincat
        
        for row in rows:
            # Validate that titlerank and crewrank are set,
            # and that they are within the same maincat
            maincat = mcat(row.titlerank.id)
            if not maincat:
                return "Employment: Data error: Title Rank %s does not have"\
                       + " a valid maincat in crew_rank_set"\
                       % str(row.titlerank.id).upper()
            crewcat = mcat(row.crewrank.id)
            if not crewcat:
                return "Employment: Data error: Crew Rank %s does not have"\
                       + " a valid maincat in crew_rank_set"\
                       % str(row.crewrank.id).upper()
            if maincat != crewcat:
                return "Employment: Title and Crew Rank must be in the same"\
                       " category (%s/%s)" % (mcstr(maincat), mcstr(crewcat))

            # Validate that the country and base match
            if row.base and row.country:
                if row.base.country:
                    if row.base.country.id != row.country.id:
                        return "Employment: Base %s does not correspond to Country %s"\
                               % (row.base.id, row.country.id)
                else:
                    return "Employment: Data error: Base %s does not have"\
                           + " a valid country in crew_base_set "\
                           % str(row.base.id).upper()
                           
            # Validate that contracts overlapping the employment period match
            ldap = '(&(validto>=%s)(validfrom<=%s))'%(row.validfrom,row.validto)
            for crow in CrewInfo.cxt.tables.CrewContract.search(ldap):
                def checkcattr(cattr, eattr, dattr):
                    if str(cattr) != str(eattr):
                        return "Employment: The contract %s %s-%s is only valid for %s." % (
                                crow.contract.contract.id,
                                str(crow.validfrom).split(" ")[0],
                                str(crow.validto).split(" ")[0],
                                dattr,
                                )
                    else:
                        return ""
                c = crow.contract
                message = (
                    (c.maincat and checkcattr(c.maincat, maincat, mcstr(c.maincat)))
                    or (c.base and checkcattr(c.base.id, row.base.id, "base %s" % c.base.id))
                    or (c.company and checkcattr(c.company.id, row.company.id, "company %s" % c.company.id))
                    )
                if message:
                    return message

        # Validate extperkey format and uniqueness
        extperkeys = set([row.extperkey for row in rows if row.extperkey is not None])
        for epk in extperkeys:
            if not RE_EXTPERKEY.match(epk):
                return "Employment: Invalid External Perkey '%s'; expected five digits." % (epk or ' ') 
        ldap = "(&(!(crew.id=%s))(|%s))" % (
          self.__crewId, "".join(["(extperkey=%s)" % epk for epk in extperkeys]))
        for emprow in TM.crew_employment.search(ldap):
            return "Employment: External Perkey '%s' already in use by %s (%s)" \
                   % (emprow.extperkey, emprow.crew.logname, emprow.crew.id)
            
        return ""

# --> Prohibited Tab Classes <-- #
class ProhibitedCrew(CrewInfoTempTable, ExtraValidations):
    # This class contains the temporary table used to display the information
    # of the "Prohibited" tab

    TM_NAME = "crew_not_fly_with"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + ProhibitedCrew.TM_NAME
       
        source = TM.crew_not_fly_with
        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.StringColumn("crew2", "Crew Empno"),
                M.StringColumn("si", "SI")]
        self.__crewIs = None
        defaultKeys = None
        if crewId is not None:
            self.__crewId = crewId
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew1": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_not_fly_with", defaultKeys)

        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Prohibited')
        self.prohibitedDetails = ProhibitedDetails(self, tablePrefix)

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return 'Prohibited Crew:: %s ' % message
  
        message = self.strLengthValidation('crew2', 'Second Crew Empno', 10)
        if message:
            return 'Prohibited Crew:: %s' % message
        message = self.strLengthValidation('si', 'SI', 40)
        if message:
            return 'Prohibited Crew:: %s' % message
        
        # Use EC to validate rows against non-loaded in DB
        message = self.__validate_EC(rows)
        if message:
            return 'Prohibited Crew:: %s' % message    
        return ""
            
    def __validate_EC(self, rows):
        """
        Validate each tmp-row by finding the matching exptperkey in db
        and subtracting the overlap so we know whole period is covered in total
        (same extperkey can be defined on more that one row)
        """
        def __get_overlap(row1,row2):
            return max(min(int(row1.validto),int(row2.validto))-
                       max(int(row1.validfrom),int(row2.validfrom)),0)
        ec = None
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
            for tmp_row in rows:
                # get length of tmp-row
                row_length = int(tmp_row.validto)-int(tmp_row.validfrom)
                # search for this extperkey in db
                search_str = "extperkey='%s' and validfrom < %s and validto >= %s"%\
                             (tmp_row.crew2,int(tmp_row.validto),
                              int(tmp_row.validfrom))
                for db_row in ec.crew_employment.search(search_str):
                    # subtract overlap for each found row
                    row_length -= __get_overlap(tmp_row,db_row)
                if row_length == (int(tmp_row.validto)-int(tmp_row.validfrom)):
                    # No change to length -> no matching rows found
                    return "Found no crew with empno %s in given period (%s,%s)"%\
                           (tmp_row.crew2,tmp_row.validfrom.ddmonyyyy(True),
                            tmp_row.validto.ddmonyyyy(True))
                if row_length > 0:
                    # Not whole length covered
                    return "Crew Empno %s is not defined for whole period (%s,%s)"%\
                           (tmp_row.crew2,tmp_row.validfrom.ddmonyyyy(True),
                            tmp_row.validto.ddmonyyyy(True))
            ec.close()
        except:
            # make sure we close db-connection
            if ec:
                ec.close()
        return ""

    def showDetails(self, runningNo):
        return self.prohibitedDetails.refresh(runningNo)
    
class ProhibitedDetails(CrewInfoTempTable):

    TM_NAME = "prohibited_details"
    def __init__(self, parentTable, tablePrefix):
        tableName = tablePrefix + ProhibitedDetails.TM_NAME
        self.parent = parentTable
        self.parentTable = parentTable._table
        source = None
        cols = [M.StringColumn("id", "empno (crewid)"),
                M.StringColumn("name", "Name")]
        defaultKeys = {}
        CrewInfoTempTable.__init__(self, tableName, cols)
        self.clear()
    
    def clear(self):
        try:
            self._row = self.create((0,))
        except:
            self._row = self[(0,)]
        self._row.id = " "
        self._row.name = " "

    def populateTable(self):
        self.clear()
    
    def refresh(self, empno):

                
        
        self.populateTable()
        
        if empno == "NULL":
            return
        
        # Defaults
        self._row.id = empno
        self._row.name = "Not found"
        
        ec = None
        ec2 = None
        try:
            ec = EC(TM.getConnStr(), TM.getSchemaStr())
            ec2 = EC(TM.getConnStr(), TM.getSchemaStr())
            #break outer loop hack
            def _set_fields():
                for db_row in ec.crew_employment.search("extperkey='%s'"%empno):
                    crew_id = str(db_row.crew)
                    for crew in ec2.crew.search("id='%s'"%crew_id):
                        self._row.id = "%s (%s)"%(crew_id, empno) # Real values
                        self._row.name = str(crew.logname)# Real values 
                        return
            _set_fields()
        finally:
            # make sure we close db-connection(s)
            if ec:
                ec.close()  
            if ec2:
                ec2.close()
           

# --> Qualification Tab Classes <-- #
class CrewQualification(CrewInfoTempTable):
    """
    Temporary table used to display the information of the "Qualifications" tab.
    """

    TM_NAME = "crew_qualification"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewQualification.TM_NAME

        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("qual", "crew_qualification_set", "Crew Qual"),
                M.StringColumn("acstring", "AC quals"),
                M.StringColumn("si", "SI")]

        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_qualification",
                                        defaultKeys)
                                        
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Qualification')
        try:
            CrewInfoTempTable.addHiddenAWBQualification(self, "crew_qualification")
        except:
            # Adding A/C qual AWB is not a critical feature, just ignore if this fail for any reason.
            log("CrewQualification.init: Failed to add A/C qual AWB to tmp table %s." % str(self.tableName))
            pass

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

    def _crewHasActiveAircraftQual(self, ac, fromTime, toTime):
        for row in self:
            if self._isAcQual(row) and row.qual.subtype == ac \
               and fromTime >= row.validfrom and toTime <= row.validto:
                return True
        return False
        
    def _validateAcStrings(self):
        for row in self:
            if row.acstring is None or not row.acstring.strip():
                continue
            acstring = row.acstring = row.acstring.upper() # Convert to upper case
            if not row.qual or row.qual.typ != 'INSTRUCTOR':
                return 'Aircraft types are only applicable to INSTRUCTOR qualifications.'

            invalidACs = [ac.strip() for ac in acstring.split(',') \
                          if not self._crewHasActiveAircraftQual(ac.strip(),
                                                                 row.validfrom,
                                                                 row.validto)] 
            if invalidACs:
                return "INSTRUCTOR qualification refers to non-existing "+\
                       "or inactive aircraft qualifications %s." \
                       % ', '.join(["'%s'" % ac for ac in  invalidACs])
                        
        return ''

    def countAcQualsAt(self, time):
        ACs = set()
        for row in self:
            if self._isAcQual(row) and row.validfrom and row.validto \
               and timeInInterval(time, row.validfrom, row.validto):
                ac = row.qual.subtype
                if ac != virtual_to_real_quals(ac)[0]:
                    continue # Ignore virtual quals: it's the real quals that we want to count

                # (A3,A4,A5), (37,38) and (M0,M9,M8) counted as one
		ac = {'A3':'A4', 'A5':'A4' , '37':'38', 'M8':'M9', 'M0':'M9'}.get(ac, ac)
                ACs.add(ac)
        return len(ACs)


    @staticmethod
    def _isAcQual(row):
        q = row.qual
        return q and q.typ == 'ACQUAL' #typ is part of key, i.e. must be present

    @staticmethod
    def _isInstructorQual(row):
        q = row.qual
        return q and q.typ == 'INSTRUCTOR' #typ is part of key, i.e. must be present

    

    def validateAircraftQuals(self):
        try:
            for acQual in filter(self._isAcQual, self):
                max_concurrent = {"C":3, "F":2}[self.cxt.crewMainCategory(acQual.validfrom)]
                FORMAT = 'Max number of concurrent ACQUALs (%s) exceeded at %s.'
                if max_concurrent < self.countAcQualsAt(acQual.validfrom):
                    return FORMAT % (max_concurrent, acQual.validfrom)
                elif max_concurrent < self.countAcQualsAt(acQual.validto):
                    return FORMAT % (max_concurrent, acQual.validto)
        except Exception, err:
            return 'Crew Qualification:: %s'%err
        return ''
            
    
    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Qualification:: %s" % message

        # Validity of acstring depends on time + the contents of
        # other qualifications -> dirty + non-dirty rows need validation.
        return (self._validateAcStrings()
                or self.validateAircraftQuals()
                or CrewInfo.cxt.tables.CrewQualAcqual.validate(nowTime)
                or "")
    
# --> Acqual acqual <--- #
class CrewQualAcqual(CrewInfoTempTable, ExtraValidations):

    TM_NAME = "crew_qual_acqual"
    
    COLUMNS = [M.DateColumn("validfrom", "Valid From"),
               M.DateColumn("validto", "Valid To"),
               M.RefColumn("qual", "crew_qualification_set", "AcQual"),
               M.RefColumn("acqqual", "crew_qual_acqual_set", "Qualification"),
               M.StringColumn("si", "SI")]

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewQualAcqual.TM_NAME

        crewRef = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)

        CrewInfoTempTable.addSourceInfo(self, "crew_qual_acqual",
                                        {"crew": crewRef})
        CrewInfoTempTable.__init__(self, self.tableName, self.COLUMNS,
                                   dispName='Limited Qualifications')

    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Limitation:: %s" % message            
        
        for col,label in (('acqqual',"Qualification"),('qual',"Limitation")):
            message = self.referenceValidation(col, label)
            if message:
                return message

        day = RelTime('24:00')
        limited_rows = []
        def get_overlap(t1, t2, d1, d2):
            return max(0,int((min(t2,d2)-max(t1,d1))/day))

        # List of qualifications that should use the combined AWB (Airbus Wide Body) subtype which covers
        # A3, A4 and A5 subtypes. It also covers A2 for US airport qualifications.
        AWB_VALID_QUALS = ['INSTRUCTOR+LIFUS', 'AIRPORT']

        for limited_row in self:
            # Only validate added or modified rows.
            if not CrewInfoTempTable.isRowModified(self, limited_row):
                continue

            acqqual = str(limited_row.getRefI('acqqual'))
            lim_qual, lim_subtype = str(limited_row.getRefI('qual')).split('+')
            lim_acqqual, _ = str(limited_row.getRefI('acqqual')).split('+')
            if acqqual == "AIRPORT+US":
                lim_subtypes = virtual_to_real_US_airport_quals(lim_subtype)
            else:
                lim_subtypes = virtual_to_real_quals(lim_subtype)
            lim_valid_from = limited_row.validfrom
            lim_valid_to = TimeUtil.inclTimeToExclTime(limited_row.validto)
            days = int((lim_valid_to - lim_valid_from) / day)

            # AWB is used for all US airport qualifications
            if acqqual == "AIRPORT+US" and lim_subtype != "AWB":
                return "In %s, %s is not allowed with %s+%s. Only valid for ACQUAL+AWB" % \
                           (self.getDisplayName(), acqqual, lim_qual, lim_subtype)

            # Qualifications in listed in AWB_VALID_QUALS should not use Airbus types A3, A4 or A5.
            if lim_subtype in ('A3', 'A4', 'A5') and any(qual in acqqual for qual in AWB_VALID_QUALS):
                return "In %s, %s is not allowed with %s+%s." % \
                           (self.getDisplayName(), acqqual, lim_qual, lim_subtype)
            
            # Check that only allowed qualifications uses subtype AWB.
            if lim_subtype == 'AWB' and not any(qual in acqqual for qual in AWB_VALID_QUALS):
                return "In %s, %s is not allowed with %s+%s." % \
                       (self.getDisplayName(), acqqual, lim_qual, lim_subtype)

            qual_periods = IntervalSet()
            for qual_row in CrewInfo.cxt.tables.CrewQualification:
                qual_typ, qual_subtype = str(qual_row.getRefI('qual')).split('+')
                if qual_typ == 'ACQUAL' and \
                       qual_subtype in lim_subtypes:
                    # Maybe a match, save dates for later
                    qual_validto = TimeUtil.inclTimeToExclTime(qual_row.validto)
                    qual_validfrom = qual_row.validfrom
                    qual_periods.add(TimeInterval(qual_validfrom, qual_validto))
            qual_periods.merge()

            if check_startdate_only(lim_acqqual):
                for qual_validfrom, qual_validto in qual_periods:
                    if lim_valid_from >= qual_validfrom and lim_valid_from < qual_validto:
                        days = 0 # Signal OK by setting days to no more to cover
                        break
            else:
                for qual_validfrom, qual_validto in qual_periods:
                    overlap = get_overlap(lim_valid_from, lim_valid_to,
                                          qual_validfrom, qual_validto)
                    days -= overlap # ok, we got this much covered!
                    if days <= 0:
                        break

            if days > 0:
                return "In %s, %s starting %s has no matching Crew Qualification (%s+%s)." %\
                       (self.getDisplayName(),
                        limited_row.getRefI('acqqual'),
                        str(lim_valid_from).split()[0],
                        lim_qual,
                        lim_subtype)
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Limitation:: %s" % message            
        return ""
                    
        
    def getTabName(self):
        return self.tablePrefix + CrewQualification.TM_NAME
    
    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

# --> Qual Restriction <--- #
class CrewRestAcQual(CrewInfoTempTable, ExtraValidations):

    TM_NAME = "crew_restr_acqual"
    
    COLUMNS = [M.DateColumn("validfrom", "Valid From"),
               M.DateColumn("validto", "Valid To"),
               M.RefColumn("qual", "crew_qualification_set", "AcQual"),
               M.RefColumn("acqrestr", "crew_restr_acqual_set", "Restriction"),
               M.StringColumn("si", "SI")]

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewRestAcQual.TM_NAME

        crewRef = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
        
        CrewInfoTempTable.addSourceInfo(self, "crew_restr_acqual",
                                        {"crew": crewRef})
        CrewInfoTempTable.__init__(self, self.tableName, self.COLUMNS,
                                   dispName='Qualification Restrictions')

    def validate(self,nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Restriction:: %s" % message            

        for col,label in (('acqrestr',"Restriction"),('qual',"Limitation")):
            message = self.referenceValidation(col, label)
            if message:
                return message
            
        day = RelTime('24:00')
        limited_rows = []
        def get_overlap(t1, t2, d1, d2):
            return max(0,int((min(t2,d2)-max(t1,d1))/day))
        
        for limited_row in self:
            lim_qual, lim_subtype = str(limited_row.getRefI('qual')).split('+')
            lim_valid_from = limited_row.validfrom
            lim_valid_to = TimeUtil.inclTimeToExclTime(limited_row.validto)
            days = int((lim_valid_to - lim_valid_from) / day)
            for qual_row in CrewInfo.cxt.tables.CrewQualification:
                qual_typ, qual_subtype = str(qual_row.getRefI('qual')).split('+')
                if qual_typ == 'ACQUAL' and \
                       lim_subtype == qual_subtype:
                    #maybe a match, let's check dates!
                    qual_validto = TimeUtil.inclTimeToExclTime(qual_row.validto)
                    qual_validfrom = qual_row.validfrom
                    overlap = get_overlap(lim_valid_from,lim_valid_to,
                                          qual_validfrom, qual_validto)
                    days -= overlap # ok, we got this much covered!
                    if days <= 0:
                        break
            if days > 0:
                return "In %s, %s starting %s has no matching Crew Qualification (%s+%s)." %\
                       (self.getDisplayName(),
                        limited_row.getRefI('acqrestr'),
                        str(lim_valid_from).split()[0],
                        lim_qual,
                        lim_subtype)
                        
        return ""
    
    def getTabName(self):
        return self.tablePrefix + CrewQualification.TM_NAME

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

# --> Restriction Tab Classes <-- #
class CrewRestriction(CrewInfoTempTable):

    TM_NAME = "crew_restriction"
    
    COLUMNS = [M.DateColumn("validfrom", "Valid From"),
               M.DateColumn("validto", "Valid To"),
               M.RefColumn("rest", "crew_restriction_set", "Crew Rest"),
               M.StringColumn("si", "SI")]

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewRestriction.TM_NAME

        crewRef = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
        
        CrewInfoTempTable.addSourceInfo(self, "crew_restriction",
                                        {"crew": crewRef})
        
        CrewInfoTempTable.__init__(self, self.tableName, self.COLUMNS,
                                   dispName='Restriction')

        self.restrictionDetails = RestrictionDetails(self, tablePrefix)

    def showDetails(self, runningNo):
        return self.restrictionDetails.refresh(runningNo)

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        return newRow

class RestrictionDetails(CrewInfoTempTable):

    TM_NAME = "restriction_details"
    def __init__(self, parentTable, tablePrefix):
        self.parentTable = parentTable._table
        tableName = tablePrefix + RestrictionDetails.TM_NAME
        cols = [M.StringColumn("typ", "Type"),
                M.StringColumn("subtype", "Sub Type"),
                M.StringColumn("descshort", "Short Description"),
                M.StringColumn("desclong", "Long Description"),
                M.StringColumn("si", "SI")]

        CrewInfoTempTable.__init__(self, tableName, cols)
        self.clear()

    def clear(self):
        try:
            self._row = self.create((0,))
        except:
            self._row = self[(0,)]
        self._row.typ = " "
        self._row.subtype = " "
        self._row.descshort = " "
        self._row.desclong = " "
        self._row.si = " "
        
    def populateTable(self):
        self.clear()
    
    def refresh(self, rest):
        self.clear()
        
        if rest == "NULL":
            return
        
        typ, subtype = rest.split('+')
        self._row.typ = typ
        self._row.subtype = subtype

        crew_restriction_set_row = TM.crew_restriction_set[(typ, subtype)]
        self._row.descshort = crew_restriction_set_row.descshort
        self._row.desclong = crew_restriction_set_row.desclong
        self._row.si = crew_restriction_set_row.si

# --> Seniority Tab Classes <-- #
class CrewSeniority(CrewInfoTempTable):
    """
    Temporary table used to display the information of the "Seniority" tab.
    """

    TM_NAME = "crew_seniority"
    
    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewSeniority.TM_NAME

        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("grp", "crew_sen_grp_set", "Group"),
                M.IntColumn("seniority", "Seniority"),
                M.StringColumn("si", "SI")]

        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crew": crewRef}
        CrewInfoTempTable.addSourceInfo(self, "crew_seniority", defaultKeys)
        
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Seniority')

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime) 
        return newRow
        
    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Seniority:: %s" % message            

        for outerrow in rows:
            for innerrow in self:
                if not outerrow == innerrow and \
                       str(outerrow.getRefI('grp')) == str(innerrow.getRefI('grp')) and \
                       overlappingRows(outerrow,innerrow):
                    return "Seniority: row starting %s overlaps row starting %s" \
                           % (outerrow.validfrom,innerrow.validfrom)
            try:
                int(outerrow.seniority)
            except:
                return "Seniority: row starting %s has no valid seniority number" % outerrow.validfrom
                
        return ""

# --> Special Schedule Tab Classes <-- #
class CrewSpecSched(CrewInfoTempTable, ExtraValidations):
    """
    Temporary table used to display the information of the "Special Schedule" tab.
    """

    TM_NAME = "special_schedules"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):

        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewSpecSched.TM_NAME

        source = TM.special_schedules
        cols = [M.DateColumn("validfrom", "Valid From"),
                M.DateColumn("validto", "Valid To"),
                M.RefColumn("typ", "special_schedules_set", "Type"),
                M.StringColumn("str_val", "Note"),
                M.IntColumn("int_from", "From"),
                M.IntColumn("int_to", "To"),
                M.RelTimeColumn("time_val", "Time"),
                M.StringColumn("si", "Comment")]

        defaultKeys = None
        if crewId is not None:
            crewRef = TM.crew.getOrCreateRef(crewId)
            defaultKeys = {"crewid": crewRef}
        
        CrewInfoTempTable.addSourceInfo(self, "special_schedules", defaultKeys)

        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   dispName='Special Schedule')
        

    def createRow(self, nowTime):
        newRow = self.createNewRow()
        newRow.validfrom = nowTime
        newRow.validto = newRow.validfrom.adddays(1).month_ceil().adddays(-1)
        #newRow.validto = TimeUtil.exclTimeToInclTime(self.endTime)
        newRow.str_val = '*'
        return newRow

    def save(self):
        self.make_column_upper_case('str_val')
        return CrewInfoTempTable.save(self)
        
    def validate(self, nowTime, rows=[]):
        message = CrewInfoTempTable.validate(self, nowTime, rows)
        if message:
            return "Special schedule:: %s" % message

        for row in self:
            if not row.typ:
                return 'Special schedule:: Field Type in Special Schedule may not be VOID'
            if not row.str_val:
                return 'Special schedule:: Field Note in Special Schedule may not be VOID'

            _type = str(row.getRefI('typ'))

            if _type == 'SpecialMealCode':
                invalid_col = {'From': row.int_from, 'To': row.int_to, 'Time': row.time_val, 'SI': row.si}
                columns = [k for k, v in invalid_col.iteritems() if v is not None]
                if len(columns):
                    return 'Special schedule:: %s fields should be VOID for Type %s' % (', '.join(columns), _type)

                codes = [r.id for r in TM.meal_special_code_set.search('(&(id=*))')]
                if row.str_val not in codes:
                    return 'Special schedule:: %s is not a valid meal code, valid are %s' % (row.str_val, ', '.join(codes))

            if _type.lower() in ('forbiddendest','forbiddenact','forbiddenacfam') and row.str_val == '*':
                return 'Special schedule:: Field Type in Special Schedule has value %s which needs a Note' % _type
            if _type.lower() in ('triplength','timeoff','checkin','checkout'):
                if row.int_from is None or row.int_to is None:
                    return 'Special schedule:: Fields From and To in Special Schedule may not be VOID'+\
                           ' for Type %s'%_type
                if row.int_from < 1 or row.int_to < 1:
                    return 'Special schedule:: Fields From and To in Special Schedule must be larger than zero'+\
                           ' for Type %s'%_type
                if row.int_from > row.int_to:
                    return 'Special schedule:: Fields From must be smaller or equal to Field To for Type %s' % _type
            if _type.lower() in ('checkin', 'checkout','maxblh','maxduty') and row.time_val is None:
                return 'Special schedule:: Fields Time in Special Schedule may not be VOID for Type %s' % _type
            if _type.lower() in ('maxlegs','parttime') and row.int_to is None:
                return 'Special schedule:: Fields To in Special Schedule may not be VOID for Type %s' % _type

        message = self.strLengthValidation('str_val', "Note", 5)
        if message:
            return "Special schedule:: %s" % message
        return ""
    

class CrewProfile(CrewInfoTempTable):
    """Summary information, see specification CR101 "Crew Info - Profile Page"."""

    TM_NAME = "crew_profile"

    def __init__(self, nowTime, crewId=None, tablePrefix="tmp_"):
        self.tablePrefix = tablePrefix
        self.tableName = tablePrefix + CrewProfile.TM_NAME
        cols = [
            M.DateColumn("start_date", "Start Date"),
            M.StringColumn("title_rank", "Title Rank"),
            M.StringColumn("crew_rank", "Crew Rank"),
            M.StringColumn("qual_1", "Qualification 1"),
            M.StringColumn("qual_2", "Qualification 2"),
            M.StringColumn("qual_3", "Qualification 3"),
            M.StringColumn("qual_4", "Qualification 4"),
            M.StringColumn("rest_1", "Restriction 1"),
            M.StringColumn("rest_2", "Restriction_2"),
            #M.StringColumn("last_flown_fam_1", "Last Flown A/C fam 1"), # XXX
            #M.DateColumn("last_flown_1", "Last Flown Date 1"),          # XXX
            #M.StringColumn("last_flown_fam_2", "Last Flown A/C fam 2"), # XXX
            #M.DateColumn("last_flown_2", "Last Flown Date 2"),          # XXX
            M.StringColumn("agmtgroup", "Agreement Group"),
            M.StringColumn("contract", "Contract"),
            M.StringColumn("grouptype", "Group Type"),
            M.StringColumn("cyclestart", "Cycle Start"),
            M.StringColumn("station", "Station"),
            M.StringColumn("base", "Home Base"),
            M.StringColumn("planning_group", "Planning Group"),
            M.StringColumn("region", "Region"),
        ]
        CrewInfoTempTable.__init__(self, self.tableName, cols,
                                   isReadOnly=True)
        self.__crewId = crewId
        self.__nowTime = nowTime
        if crewId is not None:
            self.populateTable()

    def populateTable(self):
        def NVL(value):
            """To avoid "blue" fields in table."""
            if value is None:
                return " "
            return str(value)

        self.clear()
        try:
            p = crew_profile.profile(self.__crewId, self.__nowTime)
            for x in p:
                newRow = self.createNewRow()
                newRow.start_date = x.startdate
                newRow.title_rank = NVL(x.titlerank)
                newRow.crew_rank = NVL(x.crewrank)
                newRow.qual_1 = NVL(x.qual_1)
                newRow.qual_2 = NVL(x.qual_2)
                newRow.qual_3 = NVL(x.qual_3)
                newRow.qual_4 = NVL(x.qual_4)
                newRow.rest_1 = NVL(x.rest_1)
                newRow.rest_2 = NVL(x.rest_2)
                #newRow.last_flown_1 = x.last_flown_1            # XXX
                #newRow.last_flown_fam_1 = x.last_flown_fam_1    # XXX
                #newRow.last_flown_2 = x.last_flown_2            # XXX
                #newRow.last_flown_fam_2 = x.last_flown_fam_2    # XXX
                newRow.agmtgroup = NVL(x.agmtgroup)
                newRow.contract = NVL(x.contract)
                newRow.grouptype = NVL(x.grouptype)
                newRow.station = NVL(x.station)
                if x.cyclestart == 0 or x.cyclestart is None:
                    newRow.cyclestart = ' '
                else:
                    newRow.cyclestart = str(x.cyclestart)
                newRow.base = NVL(x.base)
                newRow.planning_group = NVL(x.planning_group)
                newRow.region = NVL(x.region)
        except ReferenceError, instance:
            self.addReferenceError(instance)
        
    def refresh(self, nowTime=None, crewId=None):
        if not nowTime is None:
            self.__nowTime = nowTime
        if not crewId is None:
            self.__crewId = crewId
        self.populateTable()

    def checkForChanges(self):
        """Since this table is non-editable, always return False."""
        return False

    def save(self):
        """Nothing to save, this is a temporary table."""
        return ""

