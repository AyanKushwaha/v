# The purpose of this module is to supply base classes with common
# functionalities for the crew info form tables. All tables used by the crew
# info form should be contained in classes which inherits one of the two base
# classes defined here.
#
# There are two types of tables in the crew info and thus two classes in this
# module:
# Restriction tables: The temporary restriction tables are used by the crew
#                     info form to control user input when there are no
#                     suitable _set table in the data base. This control is
#                     understood to be "convention" which is not explicit in
#                     the data base setup (thus no _set table). Deviations from
#                     this convention is not handled in a good manner by the
#                     form and thus the use of these kind of restrictions
#                     should be very limited.
#
# Data tables:        Data tables are used to display the data in the different
#                     tabs in the crew info form. Two exceptions exist:
#                     - Form Info table which contains data governing the
#                     behaviour of the form (see CrewInfoTables.py for more
#                     info).
#                     - Crew Summary table which holds the summary data which
#                     is shown at the top of the crew info form (see
#                     CrewInfoTables.py form more info).
#
#                     The data-table class contains common functionality which
#                     ensures that there are methods for copying, saving and
#                     doing simpler validation of the data in the tables. See
#                     the class for more details.
#                     NOTE: CrewInfo.py uses many of these functions directly!
#                     NOTE: It may be that the functions found in this file is
#                           not used by some of the tables as the table-specifc
#                           classes found in CrewInfoTables.py may redefine
#                           the functions.
#
# NOTE: The exact layout of each of the tables are not defined here (as this is
#       a general description of the tables). The tables are set up in
#       CrewInfoTables.py and this is where tables should be defined and
#       table-specific functionalities should be created

# Imports
from tm import TM
from tm import TempTable
from modelserver import EntityNotFoundError as EntityNotFoundError
from modelserver import FieldNotFoundError as FieldNotFoundError
from modelserver import ReferenceError as ReferenceError
from modelserver import EntityError as EntityError
import modelserver
import AbsTime
import AbsDate
import RelTime
import carmusr.TimeUtil as TimeUtil
import Errlog

import cmsadm.credentials
from utils.performance import log
import utils.wave
utils.wave.register()

### import time
### def startt(key):
###     global ta
###     try:
###         ta[key][0] = time.time()
###     except:
###         ta[key] = [time.time(), 0.0, 0]
###         
### def stopt(key):
###     global ta
###     ta[key][1] += time.time() - ta[key][0]
###     ta[key][2] += 1
### 
### def initt():
###     global ta
###     ta = {}
###     startt("TOTAL")
### 
### def printt():
###     global ta
###     stopt("TOTAL")
###     print "-------------- times --------------"
###     for t in sorted(ta.items(), lambda x,y: cmp(x[1],y[1])):
###         print t
###     print "-----------------------------------"
    
#### RESTRICTION TABLE CLASS ####
class CrewInfoResTable(TempTable):

    # Class variables
    __tableName = None

    def __init__(self, tableName, keys, values, cols=[]):
        self.__tableName = tableName

        TempTable.__init__(self, tableName, keys, cols)
        self.populateTable(values)
        return 
    
    def populateTable(self, values):
        self.removeAll()
        for value in values:
            row = self.create((value,))

    def getName(self):
        return self.__tableName

#### DATA TABLE CLASSES ####
class CrewInfoTempTable(TempTable):

    def __init__(self,
                 tmpTableName,
                 tmpTableCols,
                 cmsView="crewinfo",
                 referenceMap={},
                 dispName=None,
                 isReadOnly=False):
        '''
        The goal of this function is to create a temporary table and populate
        it if there is data with which to populate.
        The inparameters are the name and desired columns of the temporary 
        table (the key is always a running number managed by the class), some
        keys which should be the same for all rows in the temporary table
        (these will not be a part of the temporary table but will be used when
        interfacing with the DB table) and the source-table from which to
        gather the data.
        The function does not return anything
        '''
        # The key of the temp table
        self.__runningNo = 0
        # A dictionary used to keep a snapshot of the DB data:
        # {runningNumber:DB-keys}. Used to find added/removed/modified rows.
        self.__rnToKey = {}
        # A dictionary used to keep track on which rows in the temporary table
        # that originated from which DB table.
        self.__rnToSourceTable = {}
        # The name of the temporary table.
        self.__tableName = tmpTableName
        # The display name of the table
        self.__dispName = dispName
        # Access right group this table belongs to
        self.__cmsView = cmsView
        # Mapping between different columns if the DB table and temp table
        # referes to different tables.
        self.__referenceMap = referenceMap
        # This value should be used for all defaulted endTimes:
        self.endTime = AbsTime.AbsTime("31Dec2035")
        # Errors found when populating the table
        self.errors = []

        self.cxt = None
        self.formInfoTable = None
        
        # The key-column is always just a running number
        tmpTableKey = [modelserver.IntColumn("running_no", "Running Number")]
        tmpTableCols.append(modelserver.StringColumn("db_source",
                                                     "DB source table"))
        # Create the temporary table:
        TempTable.__init__(self, tmpTableName, tmpTableKey, tmpTableCols)
        self.__tmpTable = TM.table(tmpTableName)
            
        clrTmp = True
        try:
            self.__sourceInfo = self.__sourceInfo
            self.__sourceUnique = self.__sourceUnique
        except AttributeError:
            self.__sourceInfo = {}
            self.__sourceUnique = {}

        for sourceName in self.__sourceInfo.keys():
            self.populateTable(sourceName, clrTmp)
            clrTmp = False
            
        role = cmsadm.credentials.getRole()
        if role == 'Administrator':
            self.read_access = self.write_access = True
        else:
            self.read_access = self.write_access = False
            if cmsView:
                try:
                    cms_view_acl = TM.cms_views[(role, cmsView)].cms_view_acl or 0
                    self.read_access  = (4 & cms_view_acl == 4)
                    self.write_access = (2 & cms_view_acl == 2) and (not isReadOnly)
                except:
                    pass


    #### PUBLIC FUNCTIONS ####
    # These functions may be called from other modules
    def addSourceInfo(self, sourceName, permanentKeys={}, uniqueColumn=None):
        """
        The function adds the source tables from which the temporary table
        should get its information. It also adds the corresponding permanent
        keys for that source table. This should only be set before
        initialization.
        """
        try:
            self.__sourceInfo[sourceName] = permanentKeys
            self.__sourceUnique[sourceName] = uniqueColumn
        except AttributeError:
            self.__sourceInfo = {sourceName: permanentKeys}
            self.__sourceUnique = {sourceName : uniqueColumn}

        return

    def refresh(self, nowTime, crewId):
        return self.__init__(nowTime, crewId, self.tablePrefix)

    def createNewRow(self):
        '''
        This function creates a new row in the temporary table and returns the
        row. The row is initialized with the values of one of the other
        rows in the DB.
        '''
        number = self.getAndIncreaseRunningNo()
        newRow = self.__tmpTable.create((number,))

        return newRow
    
    def make_column_upper_case(self, *column):
        for row in self:
            for col in column:
                value = self.ownGet(row, col)
                if value and type(value) == str:
                    self.ownSet(row, col, value.upper())
                
                
    def merge_new_row_with_last(self, new_row, copy_values = False):
        '''
        Close previous row and possibly copy values to newly created row!
        '''
        
        if not 'validto' in  self.columnNames():
            Errlog.log('CrewInfoClasses.py:: No column named validto in table %s'% self.TM_NAME)
            return None
        rows = [row for row in self if row.validfrom != new_row.validfrom]
        if not rows:
            return new_row
        rows.sort(cmp = lambda x,y: cmp(x.validto, y.validto))
        last_row = rows[-1]
        if last_row.validto < new_row.validfrom or \
               last_row.validfrom >= new_row.validfrom:
            Errlog.log('CrewInfoClasses.py:: Unable to merge rows in table %s' % self.TM_NAME)
            return None
        else:
            last_row.validto = new_row.validfrom.adddays(-1)

        if copy_values:
            for columnName in self.columnNames():
                if columnName not in ('db_source','running_no', 'validto','validfrom'):
                    self.ownSet(new_row, columnName, self.ownGet(last_row, columnName))
        return new_row
        
    def checkForChanges(self):
        '''
        A function for finding any changes made to the temporary table. The
        function returns a boolean, true if the table has been changed,
        otherwise false
        '''
        return self.write_access and (
                   self.findAddedRows() or
                   self.findRemovedRows() or
                   self.findModifiedRows())

    def rowsToCheckValidity(self):
        '''
        Returns a tuple of all the rows which needs to be validate.
        '''
        return self.findModifiedRows() + self.findAddedRows()

    def save(self):
        '''
        A function for saving changes made to the temporary table to the DB.
        If any errors are found in the temporary table data (such as empty
        fields which are keys in the DB), the function aborts and returns an
        error message. Otherwise an empty string is returned.
        '''

        message = ""        
        if self.write_access:
            removedRows = self.findRemovedRows()
            addedRows = self.findAddedRows()
            for row in addedRows:
                self.setSourceTable(row)
    
            rowsToValidate = addedRows + self.findModifiedRows()
            if rowsToValidate or removedRows:
                if removedRows:
                    # Do not bother with errors when removing rows.
                    self.deleteRemovedRows(removedRows)
    
                message = self.validate(utils.wave.get_now_utc(True), rowsToValidate)

                TM.createState()
                if not message:
                    message = self.saveModifiedRows()
                if not message:
                    message = self.saveAddedRows()
                
        return message

    def getTable(self):
        '''
        This function returns the table created by the class.
        '''
        return self.__tmpTable

    def getTabName(self):
        return self.getName()
    
    def getName(self):
        '''
        This function returns the name of the temporary table created by the
        class instance.
        '''
        return self.__tableName

    def getDisplayName(self):
        '''
        This function returns the name to display of the temporary table created
        by the class instance.
        '''
        if self.__dispName is None:
            return self.__tableName
        else:
            return self.__dispName
    
    def resetRunningNo(self):
        self.__runningNo = 0
        return

    def clear(self):
        self.__tmpTable.removeAll()
        self.resetRunningNo()
        return
        
    def addReferenceError(self, referenceErrorInstance):
        self.errors.append(referenceErrorInstance)

    #### FUNCTIONS ONLY AFFECTING THE TMP TABLES ####

    def populateTable(self, sourceName, clearTmp=True):
        '''
        Function used to populate the temporary table with data from the source
        table. It will populate the temporary table with all rows
        corresponding to the fixed keys set in CrewInfoTables.
        '''
        if clearTmp:
            self.clear()

        # There is only one source table name in .keys() and only one
        # dictionary in .values()
        dbSource = TM.table(sourceName)
        permanentKeys = self.__sourceInfo[sourceName]
        if not permanentKeys:
            return
        
        # Create the DB search criteria depending on the permanent keys.
        searchCriteria = "".join( ["(%s=%s)" % (key, value) for key, value in permanentKeys.iteritems()] )
        if not searchCriteria:
            return

        searchCriteria = "(&" + searchCriteria + ")"
        for dbRow in dbSource.search(searchCriteria):
            row = None
            try:
                runningNo = self.getAndIncreaseRunningNo()
                row = self.__tmpTable.create((runningNo,))
                # The following must be set before the copy function is run
                row.db_source = sourceName
                dbKeyNames = self.getKeyNames(sourceName)
                dbColumnNames = self.getColumnNames(sourceName)
            
                for column in self.columnNames():
                    if column in dbColumnNames + dbKeyNames:
                        self.copyValueToTmp(dbRow, row, column)
            
                self.__rnToKey[runningNo] = []
                for key in dbKeyNames:
                    value = self.ownGet(dbRow, key)
                    self.__rnToKey[runningNo].append(value)            
                self.__rnToSourceTable[runningNo] = sourceName
            except ReferenceError, instance:
                if row:
                    row.remove()
                self.addReferenceError(instance)

    def addHiddenAWBQualification(self, sourceName):
        """
        Background: crew with A/C qual 'A3', 'A4', and/or 'A5' can also use the combined 'AWB' A/C qual for their qualifications.
        The Crew Info dialog uses the crews existing qualifications to validate new qualifications as well as populating
        drop down menus with ACQUAL suggestions (see the 'Limitation' column under 'Limited Qualifications').
        For these features (validation and suggestions) to work properly with the AWB qualification,
        this function adds a hidden AWB A/C qual for crew that already holds either 'A3', 'A4' and/or 'A5' qualifications.
        The AWB A/C qual will only be added to the tmp tables, it will be filtered from being displayed in the
        Crew Info dialog and also ignored when saving changes to the database.
        :param sourceName: temporary table name where the hidden AWB ACQUAL qualification row will be added to.
        :type sourceName: str
        :return: None
        """
        # Retrieve the AWB qualification set that will be used in the 'qual' column in the hidden AWB row.
        dbSourceCrewQualSet = TM.table("crew_qualification_set")
        searchCriteria = "(subtype=AWB)"

        hiddenAWBRowQualValue = None
        for crew_qual_set in dbSourceCrewQualSet.search(searchCriteria):
            hiddenAWBRowQualValue = crew_qual_set

        dbSource = TM.table(sourceName)
        permanentKeys = self.__sourceInfo[sourceName]
        if not permanentKeys:
            return

        # Create the DB search criteria depending on the permanent keys.
        templateDbRow = None
        searchCriteria = "".join(["(%s=%s)" % (key, value) for key, value in permanentKeys.iteritems()])
        if not searchCriteria:
            return

        # Find a row with either A3, A4 or A5 qualification with the highest 'validto' value. This row will be used
        # as a 'template' when creating the AWB qualification row.
        searchCriteria = "(&" + searchCriteria + ")"
        for dbRow in dbSource.search(searchCriteria):
            try:
                qual_typ, qual_subtype = str(dbRow.getRefI('qual')).split('+')
                if qual_typ == "ACQUAL" and qual_subtype in ("A2", "A3", "A4", "A5"):
                    if templateDbRow is None or (dbRow.getAbsTime('validto') > templateDbRow.getAbsTime('validto')):
                        templateDbRow = dbRow
            except ReferenceError, instance:
                self.addReferenceError(instance)

        if templateDbRow is None or hiddenAWBRowQualValue is None:
            return

        runningNo = self.getAndIncreaseRunningNo()
        hiddenAWBRow = self.__tmpTable.create((runningNo,))
        hiddenAWBRow.db_source = sourceName

        dbKeyNames = self.getKeyNames(sourceName)
        dbColumnNames = self.getColumnNames(sourceName)

        for column in self.columnNames():
            if column in dbColumnNames + dbKeyNames:
                if 'si' in str(column):
                    # Set hidden_row to filter the row to be displayed in the Crew Info dialog and
                    # to prevent the row to be saved to the database when applying changes from the Crew Info dialog.
                    self.ownSet(hiddenAWBRow, column, '__hidden_row__')
                elif 'qual' in str(column):
                    # Replace the 'qual' column with the AWB qual set row.
                    self.ownSet(hiddenAWBRow, column, hiddenAWBRowQualValue)
                else:
                    # For other columns, use the same values as present in the 'template' row.
                    self.copyValueToTmp(templateDbRow, hiddenAWBRow, column)
        # Temporary row shouldn't have any source table.
        self.ownSet(hiddenAWBRow, 'db_source', '')

    def afterAllTablesLoaded(self):
        '''
        Hook fired after all tables are loaded. 
        '''
        for error in self.errors:
            self.cxt.addError(error)
    

    def isEmpty(self):
        return self.__runningNo == 0


    # Functions for validating rows:

    def validate(self, nowTime=None, rows=[]):
        '''
        A function which performs a simple validation of the rows in the
        temporary tables. The function validates that any columns in the
        temporary table which corresponds to a key-field in the DB is not
        empty. The function returns an error message, identifying the specific
        table and row if an error is found. Otherwise an empty string is
        returned.
        '''
        if not self.write_access:
            return ""
            
        # Check that there are rows which need validation
        rows = rows or self.rowsToCheckValidity()

        for row in rows or []:
            keys = self.getKeyNames(row.db_source)
            permanentKeys = self.getPermanentKeys(row)
            for key in keys:
                if key not in permanentKeys \
                and (self.ownGet(row, key) is None
                     or str(self.ownGet(row, key)) == ''):
                    return "In %s, the field '%s' may not be empty." \
                           % (self.__dispName, key)
                      
            if "validto" in self.columnNames() and row.validfrom:
                if not row.validto:
                    return "In %s, the field 'validto' may not be empty." % self.__dispName
                elif row.validfrom > row.validto:
                    return "In %s, validity period must start before it ends." % self.__dispName

        return ""
    

    # Functions for handling added rows:

    def findAddedRows(self):
        '''
        Finds all rows added to the temporary table and returns a list of
        their identifiers (running number).
        '''
        addedRows = []
        for row in self.__tmpTable:
            if not row.running_no in self.__rnToKey:
                if row.getString('si') == '__hidden_row__':
                    # Rows added to tmp tables. Do not add these rows to the database.
                    continue
                else:
                    addedRows.append(row)

                
        return addedRows

    def saveAddedRows(self, addedRows=[]):
        '''
        Saves all rows that has been added to the temporary table to the DB.
        Any errors when saving a row (such as a row with the same keys already
        existing in the DB) will cause the function to skip that row and
        continue with the next.
        The function returns a string which is empty if there were no errors
        when saving. If there were one or more errors the string will contain
        the error message for the last error found.
        '''
        message = ""
        # Get the running numbers for the rows added to the temp table
        if not addedRows:
            addedRows = self.findAddedRows()            
            if not addedRows:
                return message

        for row in addedRows:
            if not row.db_source:
                message = self.setSourceTable(row)
                if message:
                    return message
            
            sourceTable = TM.table(row.db_source)
            permanentKeys = self.getPermanentKeys(None, row.db_source)
            
            # Get the names of the columns which are keys in the DB table
            keys = self.getKeyNames(row.db_source)
            newRowKeyValues = []
            # Get the values for the keys from the temp table.
            for key in keys:
                try:
                    # Since the conversion is to a DB-value, the DB-row
                    # argument is not necessary
                    value = self.convertValue(row, key, sourceTable, True)
                    newRowKeyValues.append(value)
                    if newRowKeyValues[-1] is None:
                        message = "The column %s in %s may not be empty" \
                                  %(key, self.__tableName)
                        return message
                              
                except FieldNotFoundError:
                    # If the values are not present in the temp-table then 
                    # they may be default values:
                    try:
                        newRowKeyValues.append(permanentKeys[key])
                    except KeyError:
                        # If there are no default values nor any column in
                        # the temp table something is wrong in the setup.
                        # Notify the user.
                        message = "Error when attempting to save new row in "+\
                                  "%s. Notify Jeppesen Support" \
                                  %self.__tableName
                        return message

            newRowKeyValues = tuple(newRowKeyValues)

            # The keys have been collected an may now be used to create the
            # new row:
            try:
                record = sourceTable.create((newRowKeyValues))
            except EntityError:
                # Multiple rows with the same keys exist. Notify the user
                message = "Unable to save. Multiple rows with the same keys "
                message += "exist in the table: %s. " %self.__tableName
                message += "Se documentation for further information"
                return message

            # Fill in the rest of the columns according to the temp table
            for column in self.getColumnNames(row.db_source):
                if column in keys:
                    continue
                try:
                    self.copyValueToDB(record, row, column)
                except EntityNotFoundError:
                    # If there was no such column in the DB, just continue
                    message = "Column in the temp-table not found in the DB"
                    continue
                    
            log("CrewInfo: ADDED %s" % record)
            self.addRowToDict(row.running_no, record, sourceTable)

        return message

    # Functions for handling removed rows:

    def findRemovedRows(self):
        '''
        Finds all rows removed from the temporary table and returns a list of
        their identifiers (running number).
        '''
        removedRows = []
        for runningNo in self.__rnToKey:
            try:
                row = self.__tmpTable[(runningNo,)]
            except EntityNotFoundError:
                removedRows.append(runningNo)
        return removedRows

    def deleteRemovedRows(self, removedRows=[]):
        '''
        Removes all the rows listed in the argument removedRows (list of
        running numbers) from the DB. If no rows are given as argument, the
        function finds the rows removed from the temporary table and removes
        them from the DB. If any error occurs, the function will skip that row
        and continue with the next. If no errors occurs the function returns an
        empty string, otherwise it returns the error message of the last
        message.
        '''
        DOCUMENT_BLACKLIST = ['LC', 'LPC', 'LPCA3', 'LPCA3A5', 'LPCA4','LPCA5', 'OPC', 'OPCA3', 'OPCA3A5', 'OPCA4','OPCA5',
                              'OTS', 'OTSA3', 'OTSA3A5', 'OTSA4','OTSA5', 'CRM', 'CRMC']
        message = ""
        if not removedRows:
            removedRows = self.findRemovedRows()
            if not removedRows:
                return message
        
        for runningNo in removedRows:
            try:
                keys = self.__rnToKey[runningNo]
                dbTable = TM.table(self.__rnToSourceTable[runningNo])
            except KeyError:
                # The row was not found in the tmp table. Ignore it
                continue

            try:
                dbRow = dbTable[tuple(keys)]
                if ("crew_document" in self.__tableName and dbRow.doc.subtype in DOCUMENT_BLACKLIST) and (dbRow.si is None or "FORCE" not in dbRow.si):
                    continue
            except EntityNotFoundError:
                message = "Row removed from temporary table %s can not be "+\
                          "found in DB table. It has been ignored"
                continue
                
            dbRow.remove()
            log("CrewInfo: REMOVED %s" % dbRow)
            
            self.removeRowFromDict(runningNo)

        return message
            

    # Functions for handling modified rows. If a key-field has been changed
    # the row in the DB must be removed and added again.

    def isRowModified(self, tmpRow):
        """
        Checks if a temporary row is modified by comparing it with the corresponding row in the database.
        Will return true for new rows.
        """
        try:
            key = self.__rnToKey[tmpRow.running_no]
            dbTable = TM.table(tmpRow.db_source)
            dbRow = dbTable[tuple(key)]

            for column in self.columnNames():
                if not self.ownIsEqual(column, dbRow, tmpRow):
                    return True

        except:
            # If the running number doesn't exist in self.__rnToKey dictionary it's a new qualification.
            return True

        return False

    def findModifiedRows(self):
        '''
        Finds all rows that has been modified (but not removed or added) in the
        temporary table. Returns a list of their identifiers (running number).
        '''
        modifiedRows = []
        for row in self.__tmpTable:
            if row.db_source is None:
                # This will occur if a previous change has been undone in Studio
                continue
            try:
                if row.getString('si') == '__hidden_row__':
                    # Rows added to tmp tables. Ignore any changes made to these rows.
                    continue
                key = self.__rnToKey[row.running_no]
                dbTable = TM.table(row.db_source)
                dbRow = dbTable[tuple(key)]
            except (KeyError, EntityNotFoundError):
                # Either the row was added to the temp table and does not
                # exist in the DB or the row has been removed from the DB.
                # Ignore this.
                continue
            
            dbColumns = self.getColumnNames(row.db_source) + \
                        self.getKeyNames(row.db_source)
            
            for column in self.columnNames():
                if column in dbColumns and \
                       not self.ownIsEqual(column, dbRow, row):
                    modifiedRows.append(row)
                    break

        return modifiedRows


    def saveModifiedRows(self, modifiedRows=[]):
        '''
        Saves all modifications made to the rows listed in the argument. If no
        argument is given, all rows which have been modified in the temporary
        table are found and the modifications saved to the DB. Added and
        removed rows are not regarded. If a field which is a key in the DB has
        been modified, the row is removed and the row from the temporary table
        is created in the DB. If an error occurs the function disregards this
        row and continues with the next. The function returns an empty string
        if no errors occurs, otherwise the last error message is returned.
        '''
        modifiedColumns = []
        rowsToBeAdded = []
        message = ""
        
        if not modifiedRows:
            modifiedRows = self.findModifiedRows()
            
        for tmpRow in modifiedRows:
            try:
                key = self.__rnToKey[tmpRow.running_no]
                dbTable = TM.table(tmpRow.db_source)
                dbRow = dbTable[tuple(key)]
            except (KeyError, EntityNotFoundError):
                # If either row was not found or if the row only exist in the
                # temporary table, ignore the situation and move on
                continue
                
            keyNames = self.getKeyNames(tmpRow.db_source)
            origDbRow = None
            for column in self.columnNames():
                if not self.ownIsEqual(column, dbRow, tmpRow):
                    
                    if column in keyNames:
                        dbRow.remove()
                        log("CrewInfo: REMOVED %s" % dbRow)
                        rowsToBeAdded.append(tmpRow)
                        break
                    else:
                        origDbRow = origDbRow or str(dbRow)
                        self.copyValueToDB(dbRow, tmpRow, column)
            else:
                log("CrewInfo: UPDATE ORIG %s" % origDbRow)
                log("CrewInfo:         REV %s" % dbRow)

        self.saveAddedRows(rowsToBeAdded)
        return message
    
    #### SUPPORT FUNCTIONS. USES THE MODELSERVER API ####
    # These functions should only be used within this file
    def ownGet(self, row, columnName):
        '''
        A wrapper for the modelserver "get" function". Takes a row and a column
        name and returns the value for that column in the row.
        '''
        if row is None:
            return None

        try:
            value = row.nget(columnName)
        except ReferenceError, instance:
            value = row.getRefI(columnName)
            self.addReferenceError(instance)
        return value

    def ownSet(self, row, columnName, value):
        '''
        Wrapper for the modelserver set function. The following arguments are
        necessary:
        row - the row which shall be set
        columnName - the name of the column which shall be set
        value - the value which shall be set.
        The type of the value must correspond to the type of the column in the
        row.
        '''
        columnNr = row.desc().column(columnName)
        row.set(columnNr, value)

    def copyValueToDB(self, dbRow, tmpRow, columnName):
        if columnName == "db_source":
            return None

        return self.copyValue(dbRow, tmpRow, columnName, True)

    def copyValueToTmp(self, dbRow, tmpRow, columnName):
        return self.copyValue(dbRow, tmpRow, columnName, False)
  
    def convertValue(self, sourceRow, columnName, dbTable, toDB):
        '''
        Function which copies a row from/to the temporary tables to/from the
        DB tables. The toDB inparameter decides which direction to copy and
        the columnName inparameter decides which column in the rows to copy.
        The following situations may occur for a column:
        tmpTable     dbTable    Needed action  
        --------     -------    -------------
        non-ref      non-ref    ordinary copy
        ref-tabX     ref-tabX   ordinary copy
        ref-tabX     non-ref    convert to/from reference then copy
        ref-tabX     ref-tabY   convert between references

        If the reference table for the temp-table differs from that of the DB
        it is assumed that the reference table for the temp-table only contains
        one column (the key column) which holds the interessting data.
        '''
        dbReference = self.getReferenceTable(dbTable, columnName)
        tmpReference = self.getReferenceTable(self.__tmpTable, columnName)

        # Get the value from the source
        value = self.ownGet(sourceRow, columnName)
        
        if True and columnName == "validto":
            if toDB:
                # We are moving data from tmp-table to db
                # Adjust time: 30sep2007 > 1oct2007
                value = TimeUtil.inclTimeToExclTime(value)
            else:
                # We are moving data from db to tmp
                # Adjust time: 1oct2007 > 30sep2007
                value = TimeUtil.exclTimeToInclTime(value)
        
        # Check if the reference did not exist:
        if type(value) == modelserver.GenericEntityI:
            return None
        
        # Check if the references match.
        if dbReference == tmpReference:
            # References match. Ordinary copy possible
            pass
        
        elif not dbReference:
            # References do not match. The temporary table contains a reference
            # while the DB table does not. Convert as necessary.
            # Assume that the temp-reference table only contains one key column
            # which contains the interesting values
            refTable = TM.table(tmpReference)
            key, = self.getKeyNames(refTable)
            if toDB:
                value = self.ownGet(value, key)
            else:
                for refRow in refTable:
                    if self.ownGet(refRow, key).lower() == value.lower():
                        value = refRow
                        break
            
        else:
            # Both tables contains a reference but not to the same table
            dbRefTable = TM.table(dbReference)
            tmpRefTable = TM.table(tmpReference)
            keys = self.getKeyNames(dbRefTable)

            if toDB:
                refTable = dbRefTable
            else:
                refTable = tmpRefTable
                
            searchCriteria = ""
            for key in keys:
                # Check if the columns are named different in the two reference
                # tables. If they are, use the self.__referenceMap dictionary
                # to translate the column names.
                try:
                    otherTableKey = self.__referenceMap[key]
                except KeyError:
                    otherTableKey = key
                if toDB:
                    value = self.ownGet(value, otherTableKey)
                else:
                    value = self.ownGet(value, key)
                    key = otherTableKey
                
                # if ownGet returned reference, get key value
                if type(value) in [modelserver.GenericEntity,
                                   modelserver.GenericEntityI]:
                    try:
                        value = str(value.getRefI(str(key)))
                    except:
                        value = str(value.nget(str(key)))
                searchCriteria += "(%s=%s)" %(key, value)
            if self.has_valid_period(entity=sourceRow) \
            and self.has_valid_period(table=refTable):
                searchCriteria += " (validto>%s)" % sourceRow.validfrom
                searchCriteria += " (validfrom<=%s)" % sourceRow.validto
            
            for row in refTable.search("(&%s)" % searchCriteria):
                value = row
                break
            else:
                self.addReferenceError(ReferenceError(
                  "Not found in %s - %s." % (refTable, searchCriteria.replace(":","").replace(" 0000",""))))
                return None

        return value
        
    def has_valid_period(self, table=None, entity=None):
        global table_has_valid_period
        if entity is not None:
            edesc = entity.desc()
            table = edesc.genericTable()
        else:
            edesc = table.entityDesc()
        try:
            return table_has_valid_period[table.table_name()]
        except:
            try:
                table_has_valid_period
            except:
                table_has_valid_period = {}
            try:
                edesc.column("validfrom")
                edesc.column("validto")
                table_has_valid_period[table.table_name()] = True
                return True
            except:
                table_has_valid_period[table.table_name()] = False
                return False
        

    def copyValue(self, dbRow, tmpRow, columnName, toDB): 
        '''
        Copies elements between the tmp-table and the DB-table. Uses the
        convertValue function.
        '''
        dbColumns = self.getKeyNames(tmpRow.db_source) + \
                    self.getColumnNames(tmpRow.db_source)
        tmpColumns = self.columnNames()

        if not columnName in dbColumns or columnName not in tmpColumns:
            return
        
        toRow = dbRow
        sourceRow = tmpRow
        if not toDB:
            toRow = tmpRow
            sourceRow = dbRow

        dbTable = TM.table(tmpRow.db_source) 
        value = self.convertValue(sourceRow, columnName, dbTable, toDB)
                    
        self.ownSet(toRow, columnName, value)
   
    def getReferenceTable(self, object, columnName):
        '''
        Takes a table and a column name and returns the table name which is
        referenced in that column. If the column does not reference another
        table, an empty string is returned.
        '''

        # Check whether the object is a table or a table row
        if type(object) in [modelserver.GenericEntity,
                            modelserver.GenericEntityI]:
            # It is a row
            columnNr = object.desc().column(columnName)
            return object.desc().reference(columnNr)
        else:
            # It is a table
            columnNr = object.entityDesc().column(columnName)
            return object.entityDesc().reference(columnNr)

        return ""

    def ownIsEqual(self, columnName, dbRow, tmpRow):
        '''
        This function compares one column in one DB row and one temp-table row
        and returns a boolean (true if they are equal, otherwise false). The
        function handles when the temporary table-cell contains a refernece and
        the DB-cell does not. The order of the rows given as arguments are
        of importance (DB row followed by temp-table row).
        '''
        if columnName == "db_source":
            return True

        dbValue = self.ownGet(dbRow, columnName)
        dbTable = TM.table(tmpRow.db_source)
        tmpValue = self.convertValue(tmpRow, columnName, dbTable,  True)

        if not dbValue:
            if tmpValue:
                return False
            else:
                return True
        elif tmpValue is None:
            return False
        elif type(tmpValue) != type(dbValue):
            # This might be the case when a broken DB reference has been fixed
            return False
        elif tmpValue == dbValue:
            # For some reason testing tmpValue != dbValue returns 1 when they
            # are the same. Testing with "==" seems to work though.
            return True
        else:
            # Make the comparison case insensitive in the case of strings:
            if type(dbValue)==type("str") and type(tmpValue)==type("str") and \
               dbValue.lower() == tmpValue.lower():
                return True
            return False

        return False

    def getKeyNames(self, tableName):
        '''
        Returns the names of the key-columns of the table given as argument.
        '''
        return self.getFieldNames(tableName, True)

    def columnNames(self):
        return self.getColumnNames(self.__tableName)

    @staticmethod
    def getColumnNames(table):
        '''
        Returns the names of the columns which are not keys in the table given
        as argument.
        '''
        return CrewInfoTempTable.getFieldNames(table, False)

    __field_names = {}

    @staticmethod
    def getFieldNames(table, keyColumnSwitch):
        '''
        Returns either the names of the non-key columns or the key-columns of
        the table given as argument. If keyColumnSwitch is true, the key-column
        names are returned otherwise the non-key column names are returned.
        '''
        tname = str(table)
        try:
            fields = CrewInfoTempTable.__field_names[(tname, keyColumnSwitch)]
        except:
            fields = []
            for row in TM._field.search("(entity=%s)" % tname):
                if not row.pk ^ keyColumnSwitch:
                    fields.append(row.name)
            CrewInfoTempTable.__field_names[(tname, keyColumnSwitch)] = fields
            
        return fields

    def getAndIncreaseRunningNo(self):
        '''
        Returns the running number and then increases it by 1.
        '''
        self.__runningNo = self.__runningNo + 1
        return self.__runningNo - 1

    def addRowToDict(self, runningNo, dbRow, sourceTableName):
        dbKeyInfo = self.getKeyNames(sourceTableName)
        self.__rnToKey[runningNo] = []
        for key in dbKeyInfo:
            value = self.ownGet(dbRow, key)
            self.__rnToKey[runningNo].append(value)

    def removeRowFromDict(self, runningNo):
        self.__rnToKey.pop(runningNo, 0)

    def getSourceName(self):
        return self.__sourceInfo.keys()[:]
        
    def setSourceTable(self, tmpRow):
        if len(self.__sourceInfo) == 1:
            tmpRow.db_source = self.__sourceInfo.keys()[0]
            return ""
        else:
            defaultTable = None
            for table in self.__sourceUnique:
                column = self.__sourceUnique[table]
                if column and self.ownGet(tmpRow, column):
                    self.ownSet(tmpRow,"db_source", table)
                    return ""
                elif not column:
                    defaultTable = table

            if not self.ownGet(tmpRow, "db_source") and defaultTable:
                self.ownSet(tmpRow, "db_source", defaultTable)
            else:
                value = self.ownGet(tmpRow, "validfrom")
                return "Unkown source for row starting: %s" %value

        return ""
                
    def getPermanentKeys(self, tmpRow, sourceTable=None):
        """
        Returns the permanent keys (as a dictionary) for a selected source
        table.
        """
        try:
            return self.__sourceInfo[sourceTable or tmpRow.db_source]
        except KeyError:
            return {}

