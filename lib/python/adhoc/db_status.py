"""
db_status

Creates a data integrety report on a selected schema.
Will automaticly check for referential errors aswell as
overlaps in validfrom-validto intervals

Usage:
    db_status <schema> <dburl>

"""

__verision__ = "$Revision$"

import os, sys, time, traceback
from optparse import OptionParser
from tm import TM
import AbsTime
import RelTime
import AbsDate
from carmensystems.dave import dmf, baselib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class TableScanner:
    ''' Base class for scanners operating on tables '''
    def __init__(self):
        '''Constructor, sets up some common basic things '''
        self._activeSQL = "next_revid = 0 and deleted = 'N'"
        minutesBackToCheck = 356 * 24 * 60 # Check entries this year
        self._nowMinutes = int((datetime.now() - datetime(1986, 1, 1)).total_seconds()/60)
        self._startTimeMinutes = self._nowMinutes - minutesBackToCheck
        self._startTimeDays = self._startTimeMinutes / (60 * 24)

    def tableValidForScan(self, ec, table):
        ''' If the table is to be scanned this method should return true'''
        return True

    def scan(self, conn, econn, table):
        ''' Scan method '''
        raise NotImplementedError

    def printFinalResult(self):
        ''' Method that will be called when all tables been gone through'''
        pass

    def __str__(self):
        ''' Returns the classname'''
        return self.__class__.__name__

    def _getPK(self, ec, table):
        '''Returns the Primary Key columns as a set of strings'''
        entitySpec = ec.getEntitySpec(table)
        PK = []
        for i in range(entitySpec.getKeyCount()):
            PK.append(entitySpec.getKeyColumn(i).getName())        
        return PK

    def _getColumns(self, ec, table):
        '''Returns the list of columns as a set of strings'''
        entitySpec = ec.getEntitySpec(table)
        columns = []
        for i in range(entitySpec.getColumnCount()):
            column = entitySpec.getColumn(i).getName()
            if not column in ['branchid', 'deleted', 'revid']:
                columns.append(column)
        return columns

    def _getColumnTypes(self, ec, table):
        '''Returns the column types in a dict'''
        entitySpec = ec.getEntitySpec(table)
        column_types = {}
        for i in range(entitySpec.getColumnCount()):
            column = entitySpec.getColumn(i).getName()
            if not column in ['branchid', 'deleted', 'revid']:
                column_types[column] = chr(entitySpec.getColumn(i).getApiType())
        return column_types

    def _convertTypes(self, raw, column_types):
        if isinstance(raw, list):
            converted = []
            for key, value in raw:
                if value == None:
                    converted.append((key, value))
                elif column_types[key] == 'A':
                    converted.append((key, AbsTime.AbsTime(value)))
                elif column_types[key] == 'D':
                    converted.append((key, AbsTime.AbsTime(value * 24 * 60)))
                else:
                    converted.append((key, value))
        elif isinstance(raw, dict):
            converted = {}
            for key in raw:
                value = raw[key]
                if value == None:
                    converted[key] = value
                elif column_types[key] == 'A':
                    converted[key] = AbsTime.AbsTime(value)
                elif column_types[key] == 'D':
                    converted[key] = AbsTime.AbsTime(value * 24 * 60)
                else:
                    converted[key] = value
        else:
            raise Exception("_convertTypes expects a list or dict but got: %s" % raw)

        return converted

    def _getFilterSQL(self, ec, table, prefix=None):
        column_types = self._getColumnTypes(ec, table)
        ignored_columns = [('course_activity', 'task_udor'),
                           ('crew_activity', 'trip_udor')]
        for candidate in ['validto', 'tim', 'udor', 'leg_udor', 'task_udor', 'trip_udor', 'rot_udor', 'flight_udor', 'load_flight_udor', 'cons_flight_udor', 'et', 'retirementdate', 'endofcourse', 'to_date', 'slotend', 'startdate', 'starttime', 'ca_st']:
            if candidate in column_types and not (table, candidate) in ignored_columns:
                if column_types[candidate] == 'A':
                    value = self._startTimeMinutes
                elif column_types[candidate] == 'D':
                    value = self._startTimeDays
                else:
                    continue

                if prefix == None:
                    return ' AND (%s IS NULL OR %s > %s)' % (candidate, candidate, value)
                else:
                    return ' AND (%s.%s IS NULL OR %s.%s > %s)' % (prefix, candidate, prefix, candidate, value)

        return ''



class ForeignKeyScanner(TableScanner):
    def tableValidForScan(self, ec, table):
        if table in ('accumulator_int', 'accumulator_time', 'accumulator_rel'):
            self._extraFK = [('acckey', 'crew', 'acckey', 'id', 'crew')]
        else:
            self._extraFK = []
        self._columns = self._getColumns(ec, table)
        self._column_types = self._getColumnTypes(ec, table)
        return True
        
    def scan(self, conn, ec, table):
        PK = self._getPK(ec, table)
        schema = ec.getSchema()
        ec.listForeignKeys(table)
        val = ec.readConfig()

#        spec = ec.getEntitySpec(table)
#        print "columns in table %s: %s" % (table, spec.getColumnCount())
#        for i in range(spec.getColumnCount()):
#            print "ix :%d, name: %s" %(i, spec.getColumn(i).getName())
        while(val):
            fkName, tgtEntityName, srcColumnList, tgtColumnList, _ = val.valuesAsList()
            self.setAdhoc(table, fkName, tgtEntityName, srcColumnList, tgtColumnList)
            self.checkFK(conn, ec, schema, table, tgtEntityName, srcColumnList, tgtColumnList, PK[:])
            val = ec.readConfig()
        for fk in self._extraFK:
            fkName, tgtEntityName, srcColumnList, tgtColumnList, _ = fk
            self.setAdhoc(table, fkName, tgtEntityName, srcColumnList, tgtColumnList)
            self.checkFK(conn, ec, schema, table, tgtEntityName, srcColumnList, tgtColumnList, PK[:])
            
    def checkFK(self, conn, ec, schema, table, fkTable, srcColumnList, fkColumnList, PK):
        DONT_CHECK = [('task_alert', 'alert_link_rtype,alert_link_id,alert_activity_atype,alert_activity_id,alert_rule')]
        ALLOW_EXTRA = {
            ('aircraft', 'actype'): ['14A', '221', '223', '290', '313', '315', '31R', '32M', '32V', '32X', '32Z', '33F', '732', '73X', '73Y', '744', '747', '74F', '74R', '74Y', '757', '75F', '75T', '767', '76B', '76F', '772', '773', '777', '789', '7M8', '7PC', '7S8', '8PA', 'AB6', 'A70', 'A72', 'A7H', 'A7N', 'A7S', 'A7U', 'A7W', 'ABA', 'AGH', 'AN4', 'ARJ', 'ATC', 'ATH', 'ATJ', 'ATK', 'BAE', 'CR1', 'CR7', 'CRB', 'CRC', 'CRE', 'CRG', 'CRH', 'CRI', 'CRL', 'CRM', 'CRK', 'CRP', 'DH2', 'E70', 'EMJ', 'EQV', 'ER9', 'FRJ', 'SWM'],
            ('hotel_booking', 'crew'): ['N/A'],
            ('transport_booking', 'transport'): ['default'],
            ('trip', 'base'): ['BLL', 'FRA', 'TLS']
        }

        if (table, srcColumnList) in DONT_CHECK:
            return

        for col in srcColumnList.split(','):
            if col not in PK:
                PK.append(col)
        selectSQL = ', '.join(self._columns)
        notnull = ""
        for col in srcColumnList.split(','):
            notnull += " AND %s is not null " % (col)

        if (table, srcColumnList) in ALLOW_EXTRA:
            allow_extra_sql = " AND %s NOT IN (%s)" % (srcColumnList, ', '.join(["'%s'" % ae for ae in ALLOW_EXTRA[(table, srcColumnList)]]))
        else:
            allow_extra_sql = ""

        SQL = "SELECT %s FROM %s.%s WHERE %s%s %s %sAND (%s) NOT IN (SELECT %s FROM %s WHERE %s)%s" % (
            selectSQL,
            schema,
            table,
            self._activeSQL,
            self._getFilterSQL(ec, table),
            notnull,
            self._adhoc,
            srcColumnList,
            fkColumnList,
            fkTable,
            self._activeSQL,
            allow_extra_sql)

        conn.rquery(SQL, None)
        r = conn.readRow()
        while(r):
            row = r.valuesAsList()
            values = zip(self._columns, row)
            values = self._convertTypes(values, self._column_types)
            print 'Error in reference from  %s to %s, entity: {%s}' % (table, fkTable, ', '.join(["%s: %s" % pair for pair in values]))
            r = conn.readRow()            

    def setAdhoc(self, table, fkName, tgtEntityName, srcColumnList, tgtColumnList):
        if table in ('trip_flight_duty', 'trip_ground_duty'):
            if fkName == 'base':
                self._adhoc = " AND base != '-' "
            else:
                self._adhoc = ''
        else:
            self._adhoc = ''

class RevidScanner(TableScanner):
    def scan(self, conn, ec, table):
        selects = self._getPK(ec, table)
        selects.append('revid')
        schema = ec.getSchema()
        SQL = 'SELECT %s FROM %s.%s WHERE revid NOT IN (SELECT revid FROM dave_revision)' % (
            ', '.join(selects),
            schema,
            table)
        conn.rquery(SQL, None)
        r = conn.readRow()
        while(r):
            row = r.valuesAsList()
            print "Blocking error in table %s, revid not in dave_revision: %s" % (table, dict(zip(selects,row)))
            r = conn.readRow()
        
class OverlapScanner(TableScanner):
    def __init__(self):
        TableScanner.__init__(self)
        self._activeSQL = " %s.deleted = 'N' and %s.next_revid = 0 "
        
    def tableValidForScan(self, ec, table):
        self._PK = self._getPK(ec, table)
        self._column_types = self._getColumnTypes(ec, table)
        self._validfrom = None
        self._validto = None
        # dst_rule table have only validfrom and no validto and thus can not overlap
        if 'validfrom' in self._PK and table != 'dst_rule':
            self._validfrom = 'validfrom'
            self._validto = 'validto'
            return True
        elif 'valid_from' in self._PK:
            self._validfrom = 'valid_from'
            self._validto = 'valid_to'
            return True
        return False
        
    def scan(self, conn, ec, table):
        schema = ec.getSchema()
        selects = ['t1.%s' % (col) for col in self._PK]
        if table == 'crew_document':
            selects += ['t1.ac_qual', 't2.ac_qual']
        selects += ['t1.%s' % self._validto,
                    't2.%s' % self._validfrom,
                    't2.%s' % self._validto]
        
        overlap = "((t1.%s >= t2.%s and t1.%s < t2.%s) OR  (t1.%s > t2.%s and t1.%s <= t2.%s))" % (
            self._validfrom,
            self._validfrom,
            self._validfrom,
            self._validto,
            self._validto,
            self._validfrom,
            self._validto,
            self._validto,
            )
        same = ['t1.%s = t2.%s' % (t1,t2) for (t1,t2) in zip (self._PK,self._PK) if t1 != self._validfrom]
        notidentical = 'NOT t1.%s = t2.%s' % (self._validfrom, self._validfrom)
        SQL = "SELECT %s FROM %s WHERE %s AND %s AND %s AND %s%s%s AND %s" % (
            ', '.join(selects),
            ' %s.%s t1, %s.%s t2 ' % (schema, table, schema, table),
            ' AND '.join(same),
            notidentical,
            self._activeSQL % ('t1','t1'),
            self._activeSQL % ('t2','t2'),
            self._getFilterSQL(ec, table, 't1'),
            self._getFilterSQL(ec, table, 't2'),
            overlap
            )
        
        conn.rquery(SQL, None)
        r = conn.readRow()
        while(r):
            row = r.valuesAsList()
            # Double qual crew have overlapping REC but with different ac_qual field
            if table == 'crew_document':
                t1dict = dict(zip([s for s in self._PK]+['ac_qual','t2.ac_qual',self._validto],row[:-2]))

                if t1dict['doc_typ'] == 'MEDICAL' and t1dict['doc_subtype'] in ('-', 'C'):
                    # MEDICAL+- documents are allowed to overlap
                    r = conn.readRow()
                    continue

                differ = t1dict['ac_qual'] != t1dict['t2.ac_qual']
                exists = t1dict['ac_qual'] != None and t1dict['ac_qual'] != None
                if differ and exists:
                    r = conn.readRow()
                    continue
                del t1dict['t2.ac_qual']
            else:
                t1dict = dict(zip([s for s in self._PK]+[self._validto],row[:-2]))
            t2dict = dict(zip([self._validfrom,self._validto], row[-2:]))

            t1dict = self._convertTypes(t1dict, self._column_types)
            t2dict = self._convertTypes(t2dict, self._column_types)
            print 'Overlap in %s: %s with other period: %s' % (table, t1dict, t2dict)
            r = conn.readRow()      


class ChkFileScanner(TableScanner):
    def __init__(self):
        TableScanner.__init__(self)
        self.chkFiles = None

    def tableValidForScan(self, ec, table):
        self._columns = self._getColumns(ec, table)
        self._column_types = self._getColumnTypes(ec, table)
        if self.chkFiles == None:
            self.setChkFiles(ec)
        return True
        
    def scan(self, conn, ec, table):
        schema = ec.getSchema()

        for tree in self.chkFiles:
            chk_root = tree.getroot()
            for child in chk_root:
                if child.tag == 'entity':
                    self.handleChkEntity(conn, ec, schema, table, child)
                else:
                    print 'ERROR: Could not handle tag %s' % child.tag


    def handleChkEntity(self, conn, ec, schema, table, elem):
        entity_name = elem.attrib['name']

        if entity_name == table:
            # print elem.tag, elem.attrib
            for child in elem:
                self.handleChkRule(conn, ec, schema, table, child)

    def handleChkRule(self, conn, ec, schema, table, elem):
        operation = elem.tag
        if operation == 'check':
            self.handleCheck(conn, ec, schema, table, elem.attrib)
        elif operation == 'ref':
            self.handleRef(conn, ec, schema, table, elem.attrib)
        elif operation == 'unique':
            self.handleUnique(conn, ec, schema, table, elem.attrib)
        elif operation == 'pattern' and elem.attrib['name'] == 'ValidityPeriod':
            pass # This is handled by OverlapScanner
        else:
            print "ERROR: Don't know how to check", elem.tag, elem.attrib

    def handleCheck(self, conn, ec, schema, table, attrib):
        # print "Check", table, attrib

        condition = attrib['cond'].replace('$', table).replace('==', '=')
        condition_name = attrib['name']
        selectSQL = ', '.join(self._columns)
        SQL = "SELECT %s FROM %s.%s WHERE %s%s AND NOT (%s)" % (
            selectSQL,
            schema,
            table,
            self._activeSQL,
            self._getFilterSQL(ec, table),
            condition)

        conn.rquery(SQL, None)
        r = conn.readRow()
        while(r):
            values = zip(self._columns, r.valuesAsList())
            values = self._convertTypes(values, self._column_types)
            print 'Broken condition "%s" in table %s: {%s} [%s]' % (condition_name, table, ', '.join(["%s: %s" % pair for pair in values]), condition)
            r = conn.readRow()            
        

    def handleRef(self, conn, ec, schema, table, attrib):
        # print "Ref", table, attrib

        NULL_REF_ALLOWED = [('aircraft', 'nationality')]

        selectSQL = ', '.join(self._columns)
        if ('refname' in attrib) and (attrib['refname'] in self._getColumns(ec, attrib['tgtname'])):
            refname = attrib['refname']
        else:
            refname = 'id'
        tgtname = attrib['tgtname']
        key = attrib['key']
        if ',' in key:
            print "Warning: Can't handle reference checks with multiple keys. Ignoring %s.(%s) -> %s.(%s)" % (table, key, tgtname, refname)
            return

        if 'cond' in attrib:
            condition = attrib['cond'].replace('$', 't1').replace('==', '=')
            condSQL = "AND (%s) " % condition
        else:
            condSQL = ''

        if (table, key) in NULL_REF_ALLOWED:
            null_sql = "AND (NOT t1.%s IS NULL) " % key
        else:
            null_sql = ""

        SQL = "SELECT %s FROM %s.%s t1 WHERE %s%s%s %sAND NOT EXISTS (SELECT * FROM %s.%s t2 WHERE %s%s AND t1.%s = t2.%s)" % (
            selectSQL,
            schema,
            table,
            self._activeSQL,
            self._getFilterSQL(ec, table),
            null_sql,
            condSQL,
            schema,
            tgtname,
            self._activeSQL,
            self._getFilterSQL(ec, table),
            key,
            refname)

        try:
            conn.rquery(SQL, None)
            r = conn.readRow()
            while(r):
                values = zip(self._columns, r.valuesAsList())
                values = self._convertTypes(values, self._column_types)
                print 'Broken reference %s.%s -> %s.%s in table %s: {%s}' % (table, key, tgtname, refname, table, ', '.join(["%s: %s" % pair for pair in values]))
                r = conn.readRow()
        except baselib.StaticError, e:
            print "Warning: Reference check %s for table %s gave the following error: %s" % (attrib, table, e)
        

    def handleUnique(self, conn, ec, schema, table, attrib):
        # print "Unique", table, attrib

        key = attrib['key']
        selectSQL = ', '.join(self._columns)
        filterSQL = self._getFilterSQL(ec, table)
        SQL = "SELECT %s FROM %s.%s WHERE %s%s and (%s) IN (SELECT %s FROM %s.%s WHERE %s%s GROUP BY %s HAVING COUNT(*) > 1) ORDER BY %s" % (selectSQL, schema, table, self._activeSQL, filterSQL, key, key, schema, table, self._activeSQL, filterSQL, key, key)
        conn.rquery(SQL, None)
        r = conn.readRow()
        while(r):
            values = zip(self._columns, r.valuesAsList())
            values = self._convertTypes(values, self._column_types)
            print 'Values not unique in column(s) %s in table %s: {%s}' % (key, table, ', '.join(["%s: %s" % pair for pair in values]))
            r = conn.readRow()            


    def setChkFiles(self, ec):
        # Find interesting model versions

        self.chkFiles = []
        modules = set()
        ec.selectSchemaConfig()
        val = ec.readConfig()
        while(val):
            _, _, attr_name, version = val.valuesAsList()
            if attr_name in ['version'] and not version.startswith('udmair.'): # Avoid 'duplicates'
                modules.add(version)
            val = ec.readConfig()

        # print "ChkFileScanner: modules %s" % modules

        # print "ChkFileScanner: Looking for .chk files"
        chk_dirs = [os.path.join(os.environ['CARMUSR'], 'current_carmsys/data/config/models'),
                    os.path.join(os.environ['CARMUSR'], 'data/config/models')]
        for chk_dir in chk_dirs:
            for root, dirs, files in os.walk(chk_dir):
                for file in files:
                    if file.endswith(".chk"):
                        tree = ET.parse(os.path.join(root, file))
                        chk_root = tree.getroot()
                        module_version = chk_root.attrib['model_version']
                        if chk_root.tag == 'dave_model_check' and module_version in modules or module_version=='':
                            # print "File %s is interesting" % file
                            self.chkFiles.append(tree)

        
class ActiveEntryScanner(TableScanner):
    def __init__(self):
        TableScanner.__init__(self)
        self._activeSQL = " %s.deleted = 'N' and %s.next_revid = 0 "
        
    def tableValidForScan(self, ec, table):
        if table in ['crew_address']:
            return True
        else:
            return False

    def scan(self, conn, ec, table):
        schema = ec.getSchema()

        emp_crew_ids = self.find_active_entries(conn, schema, 'crew_employment', 'crew', 'validfrom', 'validto', self._nowMinutes)

        table_ids = self.find_active_entries(conn, schema, table, 'crew', 'validfrom', 'validto', self._nowMinutes)

        for emp_crew_id in sorted(emp_crew_ids):
            if not emp_crew_id in table_ids:
                print "There is no active entry in table %s for crewid %s" % (table, emp_crew_id)

    def find_active_entries(self, conn, schema, table, id_field, validfrom_field, validto_field, now):
        sql = 'SELECT ' + id_field + ' FROM ' + schema + '.' + table + ' where ' + (self._activeSQL % (table, table)) + ' and ' + validfrom_field + ' <= ' + str(now) + ' and (' + validto_field + ' is null or ' + validto_field + ' > ' + str(now) +')'
        conn.rquery(sql, None)
        r = conn.readRow()
        found_entries = []
        while(r):
            row = r.valuesAsList()
            found_entries.append(row[0])
            r = conn.readRow()
        return found_entries


class StatisticsScanner(TableScanner):
    ''' Provides simple statistics on the tables'''
    def __init__(self):
        TableScanner.__init__(self)
        self.tableStats = []
    
    def scan(self, conn, ec, table):
        schema = ec.getSchema()
        res = {'name': table}

        # Gather the amount of rows in table
        SQL = 'SELECT count(1) FROM %s.%s' % (schema, table)
        res['count'] = self.execSQL(SQL, conn)

        # Gather amount of active rows in table
        SQL = 'SELECT count(1) FROM %s.%s where %s' % (schema, table, self._activeSQL)
        res['active'] = self.execSQL(SQL, conn)

        # Gather the number of modifications to the table
        SQL = 'SELECT count(1) FROM (SELECT DISTINCT revid FROM %s.%s)' % (schema, table)
        res['revid'] = self.execSQL(SQL, conn)

        self.tableStats.append(res)

    def execSQL(self, sql, conn):
        ''' Helper metrhod, expects the query to generate a single integer'''
        conn.rquery(sql, None)
        r = conn.readRow()
        row = r.valuesAsList()
        conn.endQuery()
        return row[0]

    def printFinalResult(self):
        ''' Prints the information gathered previously'''
        print ""
        print "Top 20 largest tables (with deleted/old revisions)"
        l = self.sortList('count')
        self.printList(l[:20], 'count', ' rows')

        print ""
        print "Top 20 largest tables (with only active rows)"
        l = self.sortList('active')
        self.printList(l[:20], 'active', ' rows')

        print ""
        print "Top 20 modified tables"
        l = self.sortList('revid')
        self.printList(l[:20], 'revid', ' revisions')
        
    def sortList(self, key):
        l = [(x[key], i, x) for i,x in enumerate(self.tableStats)]
        l.sort()
        l.reverse()
        return [item for _,_,item in l]

    def printList(self, list, key, text):
        for i, item in enumerate(list):
            print "%02d: %s: %d %s" % (i+1, item['name'], item[key], text) 
            

    
class DBChecker:
    """
    Framework for performing DAVE level 1 API queries on a database.
    Initiates scanners that will be given the opertunity to perform a
    scan on each first class table in the provided schema
    """
    def __init__(self, schema, dburl, tables, excludedtables, quiet):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._entityConn = None
        self._conn = None
        self._tablesToScan = tables
        self._tablesNotToScan = excludedtables
        self._quiet = quiet
        self._tableScanners = self._createTableScanners()
        
        
    def _createTableScanners(self):
        ''' Helper method that initializes all scanners and adds them to the list'''
        scanners = []
        scanners.append(RevidScanner())
        scanners.append(ForeignKeyScanner())
        scanners.append(OverlapScanner())
        scanners.append(ChkFileScanner())
        scanners.append(ActiveEntryScanner())
        if not self._quiet:
            scanners.append(StatisticsScanner())
        return scanners
        
    def __del__(self):
        """
        Deconstructor, closes down connections to the DAVE database
        """
        TM.disconnect()

    def run(self):
        """
        Performs the schema integrity check
        """
        self.connect()

        daveVersion = self._entityConn.findDAVEVersion()

        if self._tablesToScan != ['']:
            t = self.getTables()
            tables = [tab for tab in t if tab in self._tablesToScan]
        else:
            tables = self.getTables()

        for table in tables:
            if table in self._tablesNotToScan:
                continue
            if not self._quiet:
                print 'Scanning table: %s' % table
            for scanner in self._tableScanners:
                try:
                    if scanner.tableValidForScan(self._entityConn, table):
                        scanner.scan(self._conn, self._entityConn, table)
                except baselib.StaticError, e:
                    print "Warning: Table %s gave the following error for scanner %s: %s" % (table, scanner.__class__.__name__, e)
                    continue
        for scanner in self._tableScanners:
            scanner.printFinalResult()
        
    def getTables(self):
        '''Returns a list of tables to check in the schema'''
        self._entityConn.listTables(self._schema)
        tables = []
        val = self._entityConn.readConfig()
        while(val):
            row = val.valuesAsList()
            tables.append(row[0])
            val = self._entityConn.readConfig()

        # listTables gives us all tmp tables as well as the internal table util_status
        res =  [t for t in tables if t != 'util_status' and not t.endswith('_tmp')]
        # listTables will not give us any table that starts with dave by default
        for table in ['dave_entity_select', 'dave_selparam', 'dave_selection']:
            res.append(table)
        # Lets have it all alphabetically for ease of use
        res.sort()
        return res
        
    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        self._entityConn = dmf.EntityConnection()
        self._entityConn.open(self._dburl, self._schema)
        self._conn = dmf.Connection(self._dburl)

def usage():
    print __doc__

if __name__ == "adhoc.db_status":
    parser = OptionParser()
    parser.add_option('-t', '--tables', 
            dest="tables", 
            default="", 
            help="Comma separated list of tables to scan")
    parser.add_option('-e', '--exclude-tables', 
            dest="excludedtables", 
            default="", 
            help="Comma separated list of tables to exclude from scan")
    parser.add_option('-q', '--quiet',
            action="store_true",
            dest="quiet", 
            default=False, 
            help="More quiet output (no statistics)")
    parser.add_option('-c', '--connect', 
            dest="connect", 
            help="Database connect string.")
    parser.add_option('-s', '--schema', 
            dest="schema", 
            help="Database schema string.")
    opts, args = parser.parse_args(list(sys.argv[1:]))

    if opts.schema is None:
        parser.error("Must supply option 'schema'.")
    if opts.connect is None:
        parser.error("Must supply option 'connect'.")


    tables = opts.tables.split(",")
    tables = [t.strip() for t in tables]

    exctables = opts.excludedtables.split(",")
    exctables = [t.strip() for t in exctables]

    checker = DBChecker(opts.schema, opts.connect, tables, exctables, opts.quiet)
    checker.run()
    del checker

