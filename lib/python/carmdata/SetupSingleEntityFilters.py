

"""
SetupSingleEntityFilters

Sets up predefined filters for single entity filtering.
These filters are used for filtering in the table editor from the launcher.

"""

__version__ = "$Revision$"
__author__ = "Christoffer Sandberg, Jeppesen"

import sys
from optparse import OptionParser
import modelserver as M
from carmensystems.dave import dmf, baselib
import Errlog
from tm import TM
import pdb

def _createParameters(selection, tDS, tDSP):
    """
    Creates the parameters for Table Editor filters.
    Table Editor filters require start, end, start_time and end_time
    One year before start parameter normally found in period filters
    is not used in table editor and therefore removed
    """
    try:
        startParam = tDSP.create((selection,1))
    except M.EntityError:
        startParam = tDSP[(selection,1)]
    startParam.name = "start"
    startParam.dtype = "D"
    startParam.lbl = "Start date"
    
    try:
        endParam = tDSP.create((selection,2))
    except M.EntityError:
        endParam = tDSP[(selection,2)]
    endParam.name = "end"
    endParam.dtype = "D"
    endParam.lbl = "End date"
    
    try:
        startTimeParam = tDSP.create((selection,3))
    except M.EntityError:
        startTimeParam = tDSP[(selection,3)]
    startTimeParam.name = "start_time"
    startTimeParam.dtype = "A"
    startTimeParam.lbl = "Start Time"
    
    try:
        endTimeParam = tDSP.create((selection,4))
    except M.EntityError:
        endTimeParam = tDSP[(selection,4)]
    endTimeParam.name = "end_time"
    endTimeParam.dtype = "A"
    endTimeParam.lbl = "End Time"

def _createSelection(tableName, tDS):
    """
    Creates/retrieves the selection entity for a table
    """
    try:
        selection = tDS.create(("te_period_"+tableName,))
    except M.EntityError:
        selection = tDS[("te_period_"+tableName,)]
    selection.lbl = "TableEditor Period filter for "+tableName
    
    return selection


def _old_period():
    tDES=TM.table('dave_entity_filter')
    tDFR=TM.table('dave_filter_ref')
    tDS=TM.table('dave_selection')
    tDSP=TM.table('dave_selparam')


    # Any selection starting with "te_period_" is assumed to be a Table Editor only filter
    # For these we must not copy any matching "period" filter if there exists any such filter
    table_editor_filters = []
    for filterEntity in tDES:
        tableName = filterEntity.entity
        sel = str(filterEntity.getRefI('selection'))
        if sel.startswith("te_period_"):
            # Add entity to known table editor only filters
            table_editor_filters.append(tableName)
            # Create the selection
            selection = _createSelection(tableName, tDS)
            # Create the parameters
            _createParameters(selection, tDS, tDSP)

    # Copy all the normal period filters and make a Table Editor version of them
    for filterEntity in tDES.search("(&(selection=period))"):
        tableName = filterEntity.entity

        # If this filter is already in place, don't do anything
        if tableName in table_editor_filters:
            continue

        # Create the selection
        selection = _createSelection(tableName, tDS)

        # Create the parameters
        _createParameters(selection, tDS, tDSP)

        # Add the actual dave_entity_filter entry
        try:
            entitySelection = tDES.create((selection, selection._id))
        except M.EntityError:
            entitySelection = tDES[(selection, selection._id)]
        entitySelection.where_condition = filterEntity.where_condition
        entitySelection.top_level = filterEntity.top_level


class FilterHandler(object):
    """
    Class responsible for seting up filters
    """
    def __init__(self, schema, dburl, debug=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._entityConn = None
        self._debug = debug
        self._creators = self._createFilterCreators()

    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        self._entityConn = dmf.EntityConnection()
        self._entityConn.open(self._dburl, self._schema)

    def _createFilterCreators(self):
        """
        Instantiates the filter creators
        """
        c = CrewFilterCreator(self._debug)
        f = FlightFilterCreator(self._debug)
        return [c,f]

    def _remove_stupid_filters(self):
        '''
        Filters whoose where_condition is exactly "1=1" does not contribute to anything
        usefull except performance losses
        '''
        count_removed = 0
        for filter in TM.dave_entity_filter:
            if filter.where_condition == "1=1":
                filter.remove()
                count_removed += 1
        if count_removed > 0:
            Errlog.log("Detected %d filters which were removed due to being unnecessary" % (count_removed))

    def run(self):
        self.connect()
        tables = self.getTables()
        TM.loadTables(['dave_entity_filter','dave_filter_ref', 'dave_selection','dave_selparam'])
        TM.newState()
    
        for creator in self._creators: 
            creator.createFilters(TM, self._entityConn, tables)

        _old_period()

        self._remove_stupid_filters()

        nof = TM.save()
        print "Saved %s entities" % (nof)
        
    def getTables(self):
        '''Returns a list of tables to check in the schema'''
        self._entityConn.listTables(self._schema)
        tables = []
        val = self._entityConn.readConfig()
        while(val):
            row = val.valuesAsList()
            tables.append(row[0])
            val = self._entityConn.readConfig()

        res =  [t for t in tables if t != 'util_status' and not t.endswith('_tmp')]
        res.extend(['dave_entity_filter', 'dave_filter_ref', 'dave_selparam', 'dave_selection'])
        res.sort()
        return res


class FilterCreator(object):
    """
    Base class for automatic creation of filters where you have areference to a specific entity.
    """
    def __init__(self, debug=False):
        self._debug = debug

    def createFilters(self, ec, tables):
        raise NotImplementedError

    def findReferenceRecursive(self, ec, table, target, lvl):
        if self._debug:
            Errlog.log("[%d]Called findReferenceRecursive with %s and %s" % (lvl,table, target))
        value_list = []
        if self._debug:
            Errlog.log("[%d] Calling list Foreign keys" % (lvl))
        ec.listForeignKeys(table)
        val = ec.readConfig()
        while(val):
            fkName, tgtEntityName, srcColumnList, tgtColumnList, entityName = val.valuesAsList()
            value = (fkName, tgtEntityName, srcColumnList, tgtColumnList, entityName)
            value_list.append(value)
            val = ec.readConfig()

        if self._debug:
            Errlog.log("[%d] Retrieving PK" % (lvl))
        try:
            PK = self._getPK(ec, table)
        except baselib.StaticError:
            if self._debug:
                Errlog.log("Table %s is not a first class DAVE table, just treat it as a non-reference" % (table))
            return None
        if self._debug:
            Errlog.log("[%d] PK: %s" % (lvl, str(PK)))
        if self._debug:
            Errlog.log("[%d] Iterating over fk values" % (lvl))
        for val in value_list:
            fkName, tgtEntityName, srcColumnList, tgtColumnList, entityName = val
            if self._debug:
                Errlog.log("[%d]  Evaluating on %s" % (lvl,fkName))
            if self._colListInSet(srcColumnList, PK):
                if tgtEntityName == target:
                    # We have a reference
                    if self._debug:
                        Errlog.log("[%d]   Found the reference, returning" % (lvl))
                    return fkName
                else:
                    # Lets check the reference if it is refering
                    if self._debug:
                        Errlog.log("[%d]   Checking through recursion if %s references the target" % (lvl, tgtEntityName))
                    res=self.findReferenceRecursive(ec, tgtEntityName, target, lvl+1)
                    if res is None:
                        # The reference did not refer to our target
                        if self._debug:
                            Errlog.log("[%d]   Did not find a reference to target in the reference" % (lvl))
                    else:
                        # The reference did in fact reference our target, build the reference name!
                        if self._debug:
                            Errlog.log("[%d]    The reference did have the target as a reference!, building up reference name" % (lvl))
                        return fkName + '_' + res
        if self._debug:
            Errlog.log("[%d]Nothing to return" % (lvl))
        return None

    def _colListInSet(self, l, s):
        ll = l.split(',')
        num = len(ll)
        for item in ll:
            if item in s:
                num -= 1
        return num == 0
        
    def _getPK(self, ec, table):
        '''Returns the Primary Key columns as a set of strings'''
        entitySpec = ec.getEntitySpec(table)
        PK = []
        for i in range(entitySpec.getKeyCount()):
            PK.append(entitySpec.getKeyColumn(i).getName())        
        return set(PK)

    def createSelection(self, tableName, filterType, tDS):
        """
        Creates/retrieves the selection entity for a table
        """
        try:
            selection = tDS.create(("te_" + filterType + "_" + tableName,))
        except M.EntityError:
            selection = tDS[("te_" + filterType + "_" + tableName,)]
        selection.lbl = "%s filter for %s" % (filterType,tableName) 
        return selection


class CrewFilterCreator(FilterCreator):
    def __init__(self, debug=False):
        FilterCreator.__init__(self, debug)
        self._target = 'crew'

        self._exclusions = ['mcl', 'crew_rehearsal_rec', 'salary_convertable_data', 'crew_contact']
        self._extra_filters = [('accumulator_rel','acckey'), ('accumulator_int', 'acckey'), ('accumulator_time', 'acckey'),
                               ('account_entry','crew'), ('salary_basic_data','crewid'), ('track_alert', 'link_id')]

    def createFilters(self, tm, ec, tables):
        filters = []
        for table in tables:
            res = self.findReferenceRecursive(ec, table, self._target,0)
            if self._debug:
                Errlog.log("")
            if res is not None:
                if self._debug:
                    Errlog.log("Found reference to %s: %s.%s" % (self._target, table, res))
                filters.append((table,res))

        tDES=tm.table('dave_entity_filter')
        tDFR=tm.table('dave_filter_ref')
        tDS=tm.table('dave_selection')
        tDSP=tm.table('dave_selparam')

        filters.extend(self._extra_filters)
        for table, res in filters:
            if table in self._exclusions:
                continue
            # We will always filter on ourself
            filterExpr = self._getFilterExpr(table,res)
            print " Will create a selection for %s using %s" % (table, filterExpr)
            selection = self.createSelection(table, 'crew', tDS)
            self._createParameters(selection, tDSP)
            
            
            # Add the actual dave_entity_filter entry
            try:
                #print selection.id
                entitySelection = tDES.create((selection, selection._id))
            except M.EntityError:
                entitySelection = tDES[(selection, selection._id)]
            entitySelection.entity = table
            entitySelection.top_level = True 
            entitySelection.where_condition = filterExpr

    def _getFilterExpr(self, table, res):
        # Ugly hack to get proper crew filtering in track alert
        if table == "track_alert":
            return "$.link_rtype='C' and $." + res + "=%:1"
        else:
            return "$." + res + "=%:1"
        
    def _createParameters(self, selection, tDSP):
        try:
            crewParam = tDSP.create((selection,1))
        except M.EntityError:
            crewParam = tDSP[(selection,1)]
        crewParam.name = "crew"
        crewParam.dtype = "S"
        crewParam.lbl = "Crew"


class FlightFilterCreator(FilterCreator):
    def __init__(self, debug=False):
        FilterCreator.__init__(self, debug)
        self._target = 'flight_leg'
        self._exclusions = ['crew_need_exception']
        self._extra_filters = [('flight_leg', '')]

    def createFilters(self, tm, ec, tables):
        filters = []
        for table in tables:
            if self._debug:
                Errlog.log("")
            res = self.findReferenceRecursive(ec, table, self._target, 0)
            if res is not None:
                if self._debug:
                    Errlog.log("Found reference to %s: %s.%s" % (self._target, table, res))
                filters.append((table,res))

        tDES=tm.table('dave_entity_filter')
        tDFR=TM.table('dave_filter_ref')
        tDS=tm.table('dave_selection')
        tDSP=tm.table('dave_selparam')


        filters.extend(self._extra_filters)

        for table, res in filters:
            if table in self._exclusions:
                continue
            # We will always filter on ourself, and quick hack to allow filter on flight_leg itself...
            if res != "":
                filterExpr = "$." + res + "_udor=%:1 and $." + res + "_adep=%:3 and substr($." + res + "_fd,0,%:4)=%:2"
            else:
                # Will only get here if we are the flight leg table  itself
                filterExpr = "$.udor=%:1 and $.adep=%:3 and substr($.fd,0,9)=%:2"
                
            print " Will create a selection for %s using %s" % (table, filterExpr)
            selection = self.createSelection(table, 'flight', tDS)
            self._createParameters(selection, tDSP)
            
            # Add the actual dave_entity_filter entry
            try:
                entitySelection = tDES.create((selection, selection._id))
            except M.EntityError:
                entitySelection = tDES[(selection, selection._id)]
            entitySelection.entity = table
            entitySelection.top_level = True 
            entitySelection.where_condition = filterExpr

    def _createParameters(self, selection, tDSP):
        try:
            udorParam = tDSP.create((selection,1))
        except M.EntityError:
            udorParam = tDSP[(selection,1)]
        udorParam.name = "udor"
        udorParam.dtype = "D"
        udorParam.lbl = "original date of departure"

        try:
            fdParam = tDSP.create((selection,2))
        except M.EntityError:
            fdParam = tDSP[(selection,2)]
        fdParam.name = "fd"
        fdParam.dtype = "S"
        fdParam.lbl = "Flight descriptor"

        try:
            adepParam = tDSP.create((selection,3))
        except M.EntityError:
            adepParam = tDSP[(selection,3)]
        adepParam.name = "adep"
        adepParam.dtype = "S"
        adepParam.lbl = "Departure Airport"
        
        try:
            suffixParam = tDSP.create((selection,4))
        except M.EntityError:
            suffixParam = tDSP[(selection,4)]
        suffixParam.name = "comp_length"
        suffixParam.dtype = "I"
        suffixParam.lbl = "Length of FD string, 9 without suffix, 10 with."

if __name__ == 'carmdata.SetupSingleEntityFilters':
    parser = OptionParser()
    parser.add_option('-c', '--connect', 
            dest="connect", 
            help="Database connect string.")
    parser.add_option('-s', '--schema', 
            dest="schema", 
            help="Database schema string.")
    parser.add_option('-d', '--debug',
            dest="debug",
            action="store_true",
            default=False,
            help="debug mode, even more verbose output")
    opts, args = parser.parse_args(list(sys.argv[1:]))

    if opts.schema is None:
        parser.error("Must supply option 'schema'.")
    if opts.connect is None:
        parser.error("Must supply option 'connect'.")

    FH = FilterHandler(opts.schema, opts.connect, opts.debug)
    FH.run()
    
    del FH
