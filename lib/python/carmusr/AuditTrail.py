import AbsTime
import AbsDate
import RelTime
from carmensystems.dave import baselib
import modelserver as M
from copy import deepcopy

class SearchType:
    '''
    Base class for diferent searches that are performed in a SQL WHERE clause
    Contains some standard formatting methods
    '''
    def __init__(self):
        pass
    def getSQL(self, table, columns, types):
        pass
    def quote(self, column, columns, types, value):
        if not hasattr(self, '_type'):
            try:
                i = columns.index(column)
            except ValueError:
                # Not very best error handling but better for debugging than not being there.
                print "ERROR::Column:",column,"do not exist."
                raise
            type = types[i]
        else:
            type = self._type
        if type in [baselib.TYPE_STRING, baselib.TYPE_CHAR, baselib.TYPE_UUID]:
            return "'%s'" % value
        elif type == baselib.TYPE_ABSTIME:
            return str(int(value))
        elif type == baselib.TYPE_DATE:
            return str(int(value)/1440)
        elif type == baselib.TYPE_INT:
            return str(value)
        elif type == baselib.TYPE_BOOL:
            if str(value) in ['Y','N']:
                return "'%s'" % value
            else:
                if value:
                    return "'Y'"
                else:
                    return "'N'"
        else:
            return value
        
    def columnDecorator(self,column, table):
        if len(column.split('.')) == 1:
            return table + '.' + column
        else:
            return column

class SearchBetween(SearchType):
    """
    Used for BETWEEN searches in SQL:
       table1.column1 BETWEEN lower AND upper
    """
    def __init__(self, column, lower, upper, type = None):
        self._column = column
        self._lower = lower
        self._upper = upper
        if type:
            self._type = type

    def getSQL(self, table, columns, types):
        column = self.columnDecorator(self._column, table)
        low = self.quote(column, columns, types, self._lower)
        high = self.quote(column, columns, types, self._upper)
        return column + ' BETWEEN ' + low + ' AND ' + high

class SearchSimple(SearchType):
    """
    Used for simple relation-like SQL searches:
      table1.column1 <relation operator> value
    """
    def __init__(self, column, relation, value, type = None):
        assert relation.upper() in ['=', '<>', '>', '<',
                                    '>=', '<=', 'LIKE']
        self._column = column
        self._relation = relation
        self._value = value
        if type:
            self._type = type

    def getSQL(self, table, columns, types):
        column = self.columnDecorator(self._column, table)
        val = self.quote(column, columns, types, self._value)
        return column + self._relation + val

class PointInTimeJoin:
    """
    Class to handle the more complicated PointInTime join
    This assumes that the two aliases at_dr_join and at_dr_main already exists
    and that they are correct.

    pkJoins are SQLJoin instances describing the PK join of the join-table and main-table
    """
    def __init__(self, pkJoins, joinTable, mainTable):
        self._pkJoins = pkJoins
        self._joinTable = joinTable
        self._mainTable = mainTable

    def getSQL(self):
        sql = ' at_dr_join.commitid = (select max(dave_revision.commitid) from %s, dave_revision' % self._joinTable
        sql += ' where dave_revision.commitid <= at_dr_main.commitid AND dave_revision.revid = %s.revid AND ' % self._joinTable
        sql += ' AND '.join([j.getSQL() for j in self._pkJoins])
        sql += ') '
        return sql

class SQLJoin:
    """
    Used for join-predicates of equality type:
       table1.column1 = table2.column2
    """
    def __init__(self, sCol, tCol):
        self._sCol = sCol
        self._tCol = tCol
        
    def getSQL(self):
        return  '%s = %s' % (self._sCol, self._tCol)
        
class JoinMethods:
    '''
    Data holding class to determine different methods of joining
    '''
    Persistent = 1
    PointInTime = 2
    def __init__(self, table, method):
        self.table = table
        self.method = method


class AuditTrailBase:
    '''
    search is a list of subclassed SearchType`s

    pointInTimeJoinTable is the full name of a table in the table`s
    PK that use a PointInTime join instead of the default method, which
    is a PersistentJoin

    A Persistent join will join towards the last revision of that table, while
    a PointInTimeJoin will use the revision that was commited at the same time
    or latest before the main table`s entity itself
    
    '''
    def __init__(self, entityConn, table, periodStart, periodEnd,
                 search = None,
                 watchFields = None,
                 timeFields = None,
                 noJoinTables = ['crew'],
                 pointInTimeJoinTable = None,
                 overrides = None):
        self._sql = AuditSQL(entityConn, table, periodStart, periodEnd, search,
                             noJoinTables, pointInTimeJoinTable,
                             overrides)
        if timeFields:
            self.setTimeFields(timeFields)
        self._watchFields = watchFields
        self._changeStringCallback = None
        self._entityTextCallback = None
        self._dataConverter = None

    def setDataConverter(self, converter):
        '''
        Sets a method that can do the dataconversion, will be calles once before
        any data is returned from created change objects. Can be used to transform
        integer status to text-reprecentations, or locktpye="L" to locktype="Locked".

        The method must take thisRevision, prevRevision as arguments, and must return
        them in the same order
        '''
        self._dataConverter = converter

    def getAuditTrail(self, conn):
        
        results = self._sql.getTransactions(conn)
        changes = []
        
        # Don't make SQL queries when we know that it is an add or delete
        for result in results:
            changeObj = ChangeObject(result, self._watchFields, self._dataConverter)
            if result.prev_revid == 0 or result.deleted == 'Y':
                # Either an added or removed row, no futher analasys needed
                pass
            else:
                # This one either is added (prev revision was deleted) or we
                # have to fetch changes done
                changeObj.prevRevision = self._sql.getChanges(conn, result)
            changeObj.setChangeStringCallback(self._changeStringCallback)
            changeObj.setEntityTextCallback(self._entityTextCallback)
            changes.append(changeObj)
        return changes
    
    def debug(self):
        print "SQL for ", self.__class__.__name__, ":"
        print self._sql._getSQL()
        return self

    def setEntityTextClass(self, callback):
       self._entityTextCallback = callback

    def setChangeStringClass(self, callback):
       self._changeStringCallback = callback

    def setTimeFields(self, times):
        ''' Sets the column names that represents the entity time (eg: validfrom, validto)'''
        self._sql.setTimeFields(times)
    def setWatchFields(self, fields):
        ''' list of column names to watch changes for'''
        self._watchFields = fields

    def locktypeConverter(self, thisRevision, prevRevision):
        '''Standard converter for locktype'''
        if thisRevision:
            if thisRevision.locktype in (None, ' '):
                thisRevision.locktype = 'Unlocked'
            elif thisRevision.locktype == 'L':
                thisRevision.locktype = 'Locked'
        if prevRevision:
            if prevRevision.locktype in (None, ' '):
                prevRevision.locktype = 'Unlocked'
            elif prevRevision.locktype == 'L':
                prevRevision.locktype = 'Locked'
        return thisRevision, prevRevision
    
    def getEntityPrefix(self, changeObj):
        return ""


class AuditSQL:
    '''
    Base class for Audit trail sql
    '''
    stdColumns = ['dave_revision.commitid', 'dave_revision.committs',
                  'dave_revision.cliuser']
    stdTypes = [baselib.TYPE_INT, baselib.TYPE_INT, baselib.TYPE_STRING]

    def __init__(self, entityConn, table, periodStart, periodEnd,
                 search = None,
                 noJoinTables = ['crew'],
                 pointInTimeJoinTable = None,
                 overrides = None):
        '''
        Currently the limit is to only select from other table if it is an FK
        in the PK of the main table...
        '''
        self._table = table
        self._pk = []
        self._columns = []
        self._columns += AuditSQL.stdColumns
        self._types = []
        self._types += AuditSQL.stdTypes
        self._join = []
        self._joinTables = []
        self._periodStart = periodStart
        self._periodEnd = periodEnd
        self._timeFields = []
        self._noJoinTables = noJoinTables
        self._search = []
        if search:
            self._search += search
        self._overrides = overrides

        self._transactionSQLcache = None
        self._schema = entityConn.getSchema()
        
        # Build up Columns/PKs and Joins
        self._generateSQLData(entityConn, pointInTimeJoinTable)
        
        
    def _generateSQLData(self, entityConn, pointInTimeJoinTable = None):
        '''
        Helper method for the setup phase. Will generate all column and entity
        information needed to automiticly build an SQL statement that fetches all transactions
        for the table in the specified intervall
        '''

        pointInTimePKJoins = []
        overrideRow = None
        
        entitySpec = entityConn.getEntitySpec(self._table)
        for i in range(entitySpec.getKeyCount()):
            self._types.append(entitySpec.getKeyColumn(i).getApiType())
            self._columns.append('%s.%s' % (self._table,
                                            entitySpec.getKeyColumn(i).getName()))
            self._pk.append(entitySpec.getKeyColumn(i).getName())

        entityConn.listForeignKeys(self._table)
        val = entityConn.readConfig()
        while(val):
            row = val.valuesAsList()
            fkName, tgtEntityName, srcColumnList, tgtColumnList, _ = row
            for sCol, tCol in zip(srcColumnList.split(','),
                                  tgtColumnList.split(',')):
                if sCol in self._pk:
                    if tgtEntityName in self._noJoinTables:
                        continue
                    sourceCol = self._table + '.' + sCol
                    if self._overrides and tgtEntityName in self._overrides[0]:
                        overrideRow = row
                        continue
                    targetCol = tgtEntityName + '.' + tCol
                    # Change to support PointInTime structure
                    # These predicates remains the same even with PointInTime
                    # queries
                    sqlJoin = SQLJoin(sourceCol, targetCol)
                    if tgtEntityName == pointInTimeJoinTable:
                        pointInTimePKJoins.append(sqlJoin)
                    self._join.append(sqlJoin)
                    if not tgtEntityName in self._joinTables:
                        self._joinTables.append(tgtEntityName)
            val = entityConn.readConfig()

        if overrideRow != None:
            colMap = {}
            tmpColMap = {}
            fkName, tgtEntityName, srcColumnList, tgtColumnList, _ = overrideRow
            for sCol, tCol in zip(srcColumnList.split(','), tgtColumnList.split(',')):
                tmpColMap[tCol] = sCol
            entityConn.listForeignKeys(self._overrides[0])
            val = entityConn.readConfig()
            while(val):
                row = val.valuesAsList()
                fkName, tgtEntityName, srcColumnList, tgtColumnList, _ = row
                if tgtEntityName == self._overrides[1]:
                    for sCol, tCol in zip(srcColumnList.split(','), tgtColumnList.split(',')):
                        if sCol in tmpColMap.keys():
                            colMap[tmpColMap[sCol]] = tCol
                val = entityConn.readConfig()
            for sCol in colMap.keys():
                sourceCol = '%s.%s' %(self._table, sCol)
                targetCol = '%s.%s' %(self._overrides[1], colMap[sCol])
                sqlJoin = SQLJoin(sourceCol, targetCol)
                self._join.append(sqlJoin)
                if self._overrides[1] == pointInTimeJoinTable:
                    pointInTimePKJoins.append(sqlJoin)
            if not self._overrides[1] in self._joinTables:
                self._joinTables.append(self._overrides[1])
                                        
        for i in range(entitySpec.getColumnCount()):
            self._types.append(entitySpec.getColumn(i).getApiType())
            self._columns.append('%s.%s' % (self._table,
                                            entitySpec.getColumn(i).getName()))

        # for some reason dave don't return 'prev_revid' and 'next_revid'
        self._types.append(baselib.TYPE_INT)
        self._types.append(baselib.TYPE_INT)
        self._columns.append('%s.next_revid' % self._table)
        self._columns.append('%s.prev_revid' % self._table)

        
        # Create a temporary list with the _joinTables, as any poinInTime join
        # will polute self._joinTables with an alias-join on dave_revision
        joinTables = deepcopy(self._joinTables)
        for table in joinTables:
            # Change to support PointInTime structure
            if table == pointInTimeJoinTable:
                # if PointInTime
                # Since we don't support Alias's we hack around it by joining to
                # dave_revision twice, calling the second one for 'at_dr' (AuditTrail_DaveRevision)
                # We use this one for the IN operation
                # this will only be allowed on ONE table for now (limitation)
                self._join.append(SQLJoin('%s.revid' % table, 'at_dr_join.revid'))
                self._join.append(SQLJoin('%s.revid' % self._table, 'at_dr_main.revid'))
                self._joinTables.append('dave_revision at_dr_join')
                self._joinTables.append('dave_revision at_dr_main')
                self._join.append(PointInTimeJoin(pointInTimePKJoins, table, self._table))
                
            else:
                # PeristentJoin, easy, just join against latest revision.
                self._search.append(SearchSimple(table + '.next_revid', '=', 0, baselib.TYPE_INT))
                        
            # Read the join'ed table's data
            entitySpec = entityConn.getEntitySpec(table)
            for i in range(entitySpec.getColumnCount()):
                name = entitySpec.getColumn(i).getName()
                if name in ['revid', 'deleted', 'next_revision', 'prev_revid', 'branchid']: # change to next_revid
                    continue
                self._types.append(entitySpec.getColumn(i).getApiType())
                self._columns.append('%s.%s' % (table, name))

        # Predicate for the dave_revision join (We always do this)
        self._join.append(SQLJoin('dave_revision.revid', self._table + '.revid'))

    def setTimeFields(self, times):
        '''
        Sets the entity time fields, which will be used for Period searching.
        The first string in the list is assumed to be the start time. The second
        element in the list is optional, and will be interpeted as end time.
        '''
        self._timeFields = []

        for field in times:
            if len(field.split('.')) == 1:
                self._timeFields.append(self._table + '.' + field)
            else:
                self._timeFields.append(field)
        
    def getTransactions(self, conn):
        '''
        Executes the search SQL and returns a list of QueryResults that contains
        all database transactions for the search.
        '''
        result = []

        startField = None
        if self._timeFields:
            startField = self._timeFields[0]

        q = self._getSQL()
        conn.rquery(q, None)
        r = conn.readRow()
        while r:
            result.append(QueryResult(self._table,self._columns, self._types,
                                      r.valuesAsList(), self._pk, startField))
            r = conn.readRow()
        return result
    
    def getChanges(self, conn, transResult):
        '''
        Executes another SQL statement so that given an QueryResult, we can see how
        the previous data looked like. Only items belonging to the MAIN table will be selected!
        This means that an attribute may be present in the thisRevid QueryResult, but not in the
        prevRevision QueryResult!
        '''

        startField = None
        if self._timeFields:
            startField = self._timeFields[0]
            
        q = self._getDetailSQL(transResult.prev_revid, transResult.getPK())
        conn.rquery(q, None)
        r = conn.readRow()
        if not r:
            raise Exception, 'read error. Query: %s\n transResult %s' % (q,transResult)
        row = r.valuesAsList()
        conn.endQuery()
    
        # Create a row as ValuesAsList from r
        return QueryResult(self._table, self._columns, self._types, row,
                           self._pk, startField)
    
    def _getSQL(self):
        '''
        Creates the SQL statement that returns all transactions. Uses data
        from the setup phase, but also dynamicly creates sql depending if time
        fields are set.
        '''

        if self._transactionSQLcache:
            return self._transactionSQLcache
        
        selectValues = []
        selectValues += self._columns
        sqlSelections = ", ".join(selectValues)
        
        sqlFrom = ' FROM %s.dave_revision, %s.%s ' % (self._schema, self._schema, self._table)

        # We should create aliases for tables, since this will fail if a table
        # is joined in twice
        if self._joinTables:
            sqlFrom += ', ' + ', '.join(['%s.%s' % (self._schema, t) for t in self._joinTables])

        timeConds = []
        if len(self._timeFields) == 1:
            timeConds.append(SearchSimple(self._timeFields[0], '>=', self._periodStart))
            timeConds.append(SearchSimple(self._timeFields[0], '<', self._periodEnd))
        elif len(self._timeFields) >= 2:
            timeConds.append(SearchSimple(self._timeFields[0], '<', self._periodEnd))
            timeConds.append(SearchSimple(self._timeFields[1], '>', self._periodStart))
            
        conditions = []
        for cond in self._search:
            conditions.append(cond.getSQL(self._table, self._columns, self._types))
        for cond in self._join:
            conditions.append(cond.getSQL())
        for cond in timeConds:
            conditions.append(cond.getSQL(self._table, self._columns, self._types))
        sqlWhere = ' WHERE ' + ' AND '.join(conditions)

        self._transactionSQLcache = ''.join(['SELECT ', sqlSelections, sqlFrom, sqlWhere])
        return self._transactionSQLcache
    
    def _getDetailSQL(self, revid, pk):
        '''
        Creates the SQL statement that returns the transaction that was previous in time
        '''

        selectValues = []
        selectValues += self._columns
        sqlSelections = ", ".join(selectValues)
        
        sqlFrom = ' FROM %s.dave_revision, %s.%s ' % (self._schema, self._schema, self._table)

        # We should create aliases for tables, since this will fail if a table
        # is joined in twice
        if self._joinTables:
            sqlFrom += ', ' + ', '.join(['%s.%s' % (self._schema, t) for t in self._joinTables])
        keyConds = []
        for key in pk.keys():
            keyConds.append(SearchSimple(key, '=', pk[key]))
        conditions = []

        for cond in self._join:
            conditions.append(cond.getSQL())
        for cond in keyConds:
            conditions.append(cond.getSQL(self._table, self._columns, self._types))
        conditions.append(SearchSimple('revid', '=', revid, baselib.TYPE_INT).getSQL(self._table,
                                                                                 self._columns,
                                                                                 self._types))
        sqlWhere = ' WHERE ' + ' AND '.join(conditions)
        return ''.join(['SELECT ', sqlSelections, sqlFrom, sqlWhere])
    
class ChangeObject:
    '''
    Represents a change in the database between two revisions.
    Normaly you optimise it in such a way though that for an
    added or removed revision, you don`t care what happend before.
    Thus the prevRevision is not always calculated!
    '''
    def __init__(self, result, watchFields, dataConverter):
        self.thisRevision = result
        self.prevRevision = None
        if watchFields:
            self._watchFields = [field.replace('.','_') for field in watchFields]
        else:
            self._watchFields = []
        self._entityTextCallback = None
        self._changeStringCallback = None
        self._dataConverter = dataConverter
   
    def isRemoved(self):
        '''
        Returns true if the row is removed    
        '''
        return self.thisRevision.deleted == 'Y'
    
    def isAdded(self):
        '''
        A row is counted as added if prev_revid = 0 or if the row that
        prev_revid is pointing towards have deleted = "Y"
        '''
        if self.thisRevision.prev_revid == 0:
            return True
        elif self.thisRevision.deleted == 'Y':
            return False
        else:
            # Now we have to verify towards the prevRevision to know if it
            # was added it not
            if not self.prevRevision:
                raise Exception, 'ChangeObject needs to have a prevRevision!'
            return self.prevRevision.deleted == 'Y'

    def getChangeType(self):
        if self.isRemoved():
            return 'removed'
        elif self.isAdded():
            return 'added'
        else:
            return 'changed'

    def setChangeStringCallback(self, callback):
        ''' Sets an other class to format the change string '''
        self._changeStringCallback = callback

    def setEntityTextCallback(self, callback):
        ''' Sets another class to format the entity description '''
        self._entityTextCallback = callback

    def getChangeString(self):
        ''' Returns a string describing the changes made. Custom formatting is
        done via first setting a class that can do the formatting using
        setChangeStringCallback
        '''

        assert self.prevRevision
        if self._dataConverter:
            self.thisRevision, self.prevRevision = self._dataConverter(self.thisRevision, self.prevRevision)
            self._dataConverter = None
        
        if self._changeStringCallback:
            return self._changeStringCallback.getChangeString(self)
        
        changedColumns = self.getChangedColumns()
        if changedColumns:
            changeStrings = [col + ': ' + str(old) + ' -> ' + str(new) for
                             (col, old, new) in changedColumns]
            return ', '.join(changeStrings)
        else:
            return None

    def getChangedColumns(self, toWhiteSpace = False):
        '''
        Returns changed columns

        with toWhiteSpace set to false, we will not detect when a string column
        changes from empty string to a whitespace-only string. This is something
        studio typicaly does with some fields 
        '''
        if self._dataConverter:
            self.thisRevision, self.prevRevision = self._dataConverter(self.thisRevision, self.prevRevision)
            self._dataConverter = None
        
        # list of tuples (column, from, to)
        changedColumns = []
        if self._watchFields:
            fieldList = self._watchFields
        else:
            fieldList = self.thisRevision.getColumns().keys()
            
        for field in fieldList:
            old = getattr(self.prevRevision, field)
            new = getattr(self.thisRevision, field)
            if not toWhiteSpace:
                if (isinstance(new,str) and not old):
                    old = ""
                    new = new.strip()
                if new != old:
                    changedColumns.append((field, old, new))
        return changedColumns
    
    def getEntityText(self):
        ''' Returns a string describing the entity. Custom formatting is
        supplied by setting a class that can do the formatting via
        setGetEntityTextCallback
        '''

        if self._dataConverter:
            self.thisRevision, self.prevRevision = self._dataConverter(self.thisRevision, self.prevRevision)
            self._dataConverter = None
            
        if self._entityTextCallback:
            try:
                prefix = self._entityTextCallback.getEntityPrefix(self)
            except AttributeError:
                prefix = "?" #str(self._entityTextCallback)
        else:
            prefix = ""
            
        try:
            commitTime = str(AbsTime.AbsTime(self.thisRevision.committs/60))[-5:]
        except:
            commitTime = 'XX:XX'
        retString = "   %-6s" % prefix + commitTime + ' ' + "%-8s" % self.thisRevision.cliuser + ' ' + \
                    self.getChangeType().ljust(7) + ' '

        # Format it using the callback
        if self._entityTextCallback:
            return retString + self._entityTextCallback.getEntityText(self)

        # Default formatting
        pkDict = self.thisRevision.getPK()
        for key in pkDict.keys():
            retString += str(pkDict[key]).ljust(6)
        retString += '('
        fieldStrings = []
        if self._watchFields:
            for field in self._watchFields:
                fieldStrings.append(str(getattr(self.thisRevision, field)))
        else:
            # Use all non-PK fields
            fieldDict = self.thisRevision.getColumns()
            for key in fieldDict.keys():
                fieldStrings.append(str(fieldDict[key]))
            
        retString += ', '.join(fieldStrings) + ')'
        return retString

    def getWatchFields():
        '''
        Returns a list of fieldnames that are the oens to watch for
        changes in
        '''
        return self._watchFields

    @staticmethod
    def compare(obj1, obj2):
        '''
        Compares twp ChangeObjects with eachother.
        if obj1 < obj2 then -1
        if obj1 > obj2 then 1
        else 0

        Sort order:
        1 commitid,
        2 add/change/delete
        3 time (start time)
        
        '''
        t1 = obj1.thisRevision
        t2 = obj2.thisRevision
        
        if t1.commitid < t2.commitid: return -1
        elif t1.commitid > t2.commitid: return 1
        else:
            o1 = ChangeObject.getChangePrioFromType(obj1)
            o2 = ChangeObject.getChangePrioFromType(obj2)
            if o1 < o2: return -1
            elif o1 > o2: return 1
            else:
                t1Start = t1.getStartTime()
                t2Start = t2.getStartTime()
                # Special sorting for objects without time fields, let them come before objects
                # who have time fields
                if t1Start is None:
                    return 1
                elif t2Start is None:
                    return -1
                else:
                    t1Time = int(t1Start)
                    t2Time = int(t2Start)
                    if t1Time < t2Time: return -1
                    elif t1Time > t2Time: return 1
                    return 0

    @staticmethod
    def getChangePrioFromType(obj):
        if obj.getChangeType() == 'deleted':
            return 3
        elif obj.getChangeType() == 'changed':
            return 2
        else:
            return 1
        
class QueryResult:
    '''
    Wrapper object for a result from a DAVE SQL query.
    basicly each column becomes an attribute of the class instance

    pk is a list of column names
    startTimeField is the field name that represents the startTime
    '''

    STANDARD_COLUMNS = ['revid', 'deleted', 'next_revid', 'prev_revid', 'branchid']

    def __str__(self):
        """
        Pretty print of object for debug
        """
        l = []
        l.append("Table: %s" % self._table)
        l.append("startTime: %s" % self._startTime)
        for val in self._pkDict:
            l.append(" (PK) %s: %s" % (val, self._pkDict[val]))
        for val in self._columns:
            l.append("      %s: %s" % (val, self._columns[val]))
        for val in self._other:
            l.append("      %s: %s" % (val, self._other[val]))
            
        return "\n".join(l)
    
    def __init__(self, table, columns, types, values, pk, startTimeField = None):
        """
        Constructor, creates all the apropriate attributes and tries to do the value typecasting
        """
        self._pkDict = {}
        self._table = table
        self._columns = {}
        self._other = {}
        for col, type, val in zip(columns, types, values):
            if val is not None:
                if type == baselib.TYPE_BOOL:
                    # note that deleted column is of type CHAR, not BOOL
                    val = (False,True)[val == 'Y'] 
                elif type == baselib.TYPE_ABSTIME:
                    val = AbsTime.AbsTime(val)
                elif type == baselib.TYPE_DATE:
                    val = AbsDate.AbsDate(val*1440)
            
            splitCol = col.split('.')
            if  splitCol[0] == table:
                setattr(self, splitCol[1], val)
                if splitCol[1] in pk:
                    self._pkDict[splitCol[1]] = val
                else:
                    if splitCol[1] not in QueryResult.STANDARD_COLUMNS:
                        self._columns[splitCol[1]] = val
            elif splitCol[0] == 'dave_revision':
                setattr(self, splitCol[1], val)
                self._other[splitCol[1]] = val
            else:
                setattr(self, col.replace('.','_'), val)
                self._other[col.replace('.','_')] = val

            if startTimeField and col == startTimeField:
                self._startTime = val
                
        if not hasattr(self, '_startTime'):
            self._startTime = None

    def getPK(self):
        '''  Returns the PK as a dict, where column names are keys '''
        return self._pkDict

    def getStartTime(self):
        ''' Returns whats considered to be the start time of this result '''
        return self._startTime

    def getColumns(self):
        ''' returns a dict of non-PK columns for this table'''
        return self._columns
