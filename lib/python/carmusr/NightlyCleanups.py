#
# $Header
#

"""
This module is responsible for dispatching generic cleanup jobs

Usage:
   $CARMSYS\bin\mirador -s carmusr.NightlyCleanups -c $DB_URL -s $DB_SCHEMA

"""
__verision__ = "$Revision$"
__author__ = "Christoffer Sandberg, Jeppesen"

from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer
import RelTime
import AbsTime
import modelserver as M
import tm
import Errlog
import sys
import os
import time
import Crs
import carmensystems.mave.etab as Etab
from optparse import OptionParser


class Cleaner(object):
    """
    Base class for a cleaner object
    """
    def __init__(self):
        '''Default constructor'''
        pass
    
    def clean(self, TM):
        '''This method does the actual cleaning'''
        raise NotImplementedError


    def __str__(self):
        '''
        String representation of the cleaner job. Will be printed before executing
        '''
        return self.__class__.__name__


class MiradorCleaner(Cleaner):
    """
    Cleaning jobs which wants to use a table manager object should subclass this.
    The two methods getFilterParams and getTablesToLoad will automaticly be called before
    the clean method. One _must_ redefine getTablesToLoad in the subclass to return a list
    of tables that should be loaded.
    """
    def getFilterParams(self):
        '''
        Returns a list of tuples (selection, parameter, value) containing
        the filter that will be set
        '''
        return []

    def getTablesToLoad(self):
        '''
        Returns a list of tables that will be loaded to the TableManager before a call
        to 'clean(TM)'
        '''
        raise NotImplementedError


class DaveConnectorCleaner(Cleaner):
    """
    Cleaning jobs that issues SQL like searches to the database and operate
    on single records returned by these searches should subclass this.
    Convenience methods for searching is provided in 'dbsearch'.
    """
    
    def dbsearch(self, dc, entity, expr=[], withDeleted=False):
        """Search entity and return list of DCRecord objects."""
        if isinstance(expr, str):
            expr = [expr]
        return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))




########################################################################
# The Following cleaners are not done yet and therefore commented out
#
# Attribute cleaner does not work cause of a join in the filter against main table..
#
########################################################################

## class AttributeCleaner(Cleaner):
##     def __init__(self, table):
##         Cleaner.__init__(self)
##         if table not in ['crew_activity_attr',
##                          'crew_ground_duty_attr',
##                          'crew_flight_duty_attr']:
##             raise NotImplementedError("Cleaning not implemented for table %s" % (table))
##         self._table = table
##         self._tables_to_load = [self._table, "crew", self._table[:-5]]

##         self._attribute = {'crew_activity_attr':'ca',
##                            'crew_ground_duty_attr':'cgd',
##                            'crew_flight_duty':'cfd'}.get(self._table)

##         now = time.gmtime()
##         now = AbsTime.AbsTime(now[0], now[1], now[2], 0, 0)

##         self.periodStart = now - RelTime.RelTime(60*24*92) # Start is 3 months before now
##         self.periodEnd = now + RelTime.RelTime(60*24*92)   # End is 3 months from now

##     def clean(self, TM):
##         table = TM.table(self._table)
##         for row in table:
##             try:
##                 assignment = getattr(table, self._attribute).crew.id
##             except:
##                 print "Would remove: %s" % (str(row))

##     def getTablesToLoad(self):
##         return self._tables_to_load

##     def getFilterParams(self):
##         selAttrTable = 'period_' + self._table
##         selAssTable  = 'period_' + self._table[:-5]
##         return [(selAttrTable, "start", str(self.periodStart)[0:9]),
##                 (selAttrTable, "end", str(self.periodEnd)[0:9]),
##                 (selAttrTable, "start_time", str(self.periodStart)),
##                 (selAttrTable, "end_time", str(self.periodEnd)),
##                 (selAssTable, "start", str(self.periodStart)[0:9]),
##                 (selAssTable, "end", str(self.periodEnd)[0:9]),
##                 (selAssTable, "start_time", str(self.periodStart)),
##                 (selAssTable, "end_time", str(self.periodEnd))]

## class BidLeaveActivityCleaner(Cleaner):
##     def __init__(self):
##         Cleaner.__init__(self)

##     def getTablesToLoad(self):
##         return ["bid_leave_activity", "crew_activity", "crew"]

##     def getFilterParams(self):
##         return [("mppcategory", "cat", self.cat),
##                 ("mppcategory", "start", str(self.periodStart)[0:9]),
##                 ("mppcategory", "end", str(self.periodEnd)[0:9]),
##                 ("mppcategory", "trainingstart", str(self.periodStart)[0:9]),
##                 ("mppcategory", "actuals_cut", str(self.periodEnd)[0:9])]

##     def clean(self, TM):
##         raise NotImplementedException
##         for rec in TM.bid_leave_activity:
##             try:
##                 rec.crew
##             except ReferenceException:
##                 rec.remove()

class AbortException(Exception):
    """
    A cleaner can throw this during clean() to abort this cleaning
    """
    def __init__(self, errDescription):
        self._err = errDescription

    def __str__(self):
        return self._err


class StudioDefaultFlightLegCleaner(DaveConnectorCleaner):
    """
    Find actual and estimated times which are 1Jan1986 00:00, and set them to Null/None.
    interfaces use times <> Null as information carrier, and studio changes Null->1986 upon saving
    after a legset properties dialog and fetching NOP legs.
    """
    def clean(self, dc):
        ops = []
        columns = ['aobt', 'aibt', 'eibt', 'eobt']
        s = ['%s = 0' % c for c in columns]
        search = ' or '.join(s) 
        cutoff = time.gmtime()
        cutoff = AbsTime.AbsTime(cutoff[0], cutoff[1], cutoff[2], cutoff[3], cutoff[4]).adddays(-7)
        cutoff = int(cutoff)/1440
        
        for entry in self.dbsearch(dc, 'flight_leg', 'udor > %d and (%s)' % (cutoff, search)):
            for c in columns:
                if entry[c] is not None and entry[c] == 0:
                    entry[c] = None
            del entry['revid']
            
            ops.append(createOp('flight_leg', 'U', entry))
        return ops
        

class LinkCleaner(MiradorCleaner):
    '''
    A cleaner to remove un-needed activity_link and resource_link objects
    '''
    def clean(self, TM):
        used_activity_links = set()
        used_resource_links = set()
        
        for row in TM.track_alert:
            try:
                alink,rlink = self.getLinks(row)
            except M.ReferenceError, err:
                # We can't go on in this case
                raise AbortException(str(err))
            
            used_activity_links.add(alink)
            used_resource_links.add(rlink)

        rlink_count = 0
        alink_count = 0

        for row in TM.activity_link:
            try:
                s = '+'.join([row.atype.id, row.id])
            except M.ReferenceError:
                continue
            if s not in used_activity_links:
                row.remove()
                alink_count += 1

        for row in TM.resource_link:
            try:
                s = '+'.join([row.rtype.id, row.id])
            except M.ReferenceError:
                continue
            if s not in used_resource_links:
                row.remove()
                rlink_count += 1

        Errlog.log("Removed %d activity links and %d resource links" % (alink_count, rlink_count))
        
    def getLinks(self, row):
        alink = '+'.join([row.activity.atype.id, row.activity.id])
        rlink = '+'.join([row.link.rtype.id, row.link.id])
        return alink, rlink
    
    def getTablesToLoad(self):
        return ["track_alert", "activity_link", "resource_link"]
    
class TaskCleaner(MiradorCleaner):
    def __init__(self):
        now = time.gmtime()
        self._cutoff = AbsTime.AbsTime(now[0], now[1], now[2], now[3], now[4]).adddays(-1)

    def clean(self, TM):
        """
        Run through task and clean out closed task older than two days.
        Also clean out task_alert from unsafe references
        """
        try:
            closed_stat = TM.task_status_set[('C',)]
        except M.EntityNotFoundError:
            Errlog.log("%s: Could not find task_status with code C, aborting clean"%self.__class__.__name__)
            return 1

        # Collect rows to remove, use audit trail to get committime since not in model row
        rows_to_remove = []
        for row in TM.task:
            try:
                if row.status == closed_stat:
                    audit = TM.auditTrail(row)
                    for record in audit:
                        ci = record.commitInfo()
                        ci_time = ci.getCommitTime()
                        if ci_time > self._cutoff:
                            break # This row should stay
                    else:
                       rows_to_remove.append(row) 
            except M.ReferenceError:
                rows_to_remove.append(row)

        # Remove the rows
        for row in rows_to_remove:
            row.remove()

        
        # Check task_alert for usafe references and remove if no task found
        unsafe = 0
        for row in TM.task_alert:
            try:   
                row.task
                row.alert
            except M.ReferenceError:
                row.remove()
                unsafe += 1
        # Log result
        Errlog.log("%s: Removed %d closed tasks and %d unsafe task_alerts (older then %s)" % (self.__class__.__name__,
                                                                                              len(rows_to_remove),
                                                                                              unsafe, 
                                                                                              str(self._cutoff)))
        
                
    
    def getTablesToLoad(self):
        return ["task", "task_alert", "task_status_set", "track_alert"]
    
class AccumulatorRelCleaner(MiradorCleaner):
    '''
    Cleaning job for accumulator_rel. Remove rows so that the accumulators stay
    sane in size.
    '''
    def __init__(self):
        now = time.gmtime()
        now = AbsTime.AbsTime(now[0], now[1], now[2], now[3], now[4])

        self.periodStart = now - RelTime.RelTime(60*24*366*3) # Start is three years before now
        self.periodEnd = now -  RelTime.RelTime(60*24*120) # End is 120 days from now
       
    def getTablesToLoad(self):
        return ["accumulator_rel"]


    def getFilterParams(self):
        return [("te_period_accumulator_rel", "start", str(self.periodStart)[0:9]),
                ("te_period_accumulator_rel", "end", str(self.periodEnd)[0:9]),
                ("te_period_accumulator_rel", "start_time", str(self.periodStart)),
                ("te_period_accumulator_rel", "end_time", str(self.periodEnd))]

    def clean(self, TM):

        start_time = time.time()
        count = 0
        for row in TM.accumulator_rel:
            if row.name in ('accumulators.subq_duty_time_acc','accumulators.block_time_daily_acc','accumulators.duty_time_acc'):
                row.remove()
                count += 1

        Errlog.log("Removed %d rows" %(count))
        exec_time = time.time() - start_time
        Errlog.log("Finished in %.2f s" %(exec_time))
        
                
class AccumulatorTimeCleaner(MiradorCleaner):
    '''
    Cleaning job for accumulator_time. 
    '''
    def __init__(self):
        now = time.gmtime()
        now = AbsTime.AbsTime(now[0], now[1], now[2], now[3], now[4])

        self.periodStart = now - RelTime.RelTime(60*24*366) # Start is a year before now
        self.periodEnd = now

        self._reset1 = set(['accumulators.last_simulator',
                           'accumulators.lower_rank_date_acc',
                           'accumulators.last_ski_airp_landing_EWR',
                           'accumulators.last_ski_airp_landing_ORD',
                           'accumulators.last_ski_airp_landing_IAD',
                           'accumulators.last_ski_airp_landing_SEA',
                           'accumulators.last_ski_airp_landing_BKK',
                           'accumulators.last_ski_airp_landing_PEK',
                           'accumulators.last_ski_airp_landing_NRT'])

        self._reset2 = set(['accumulators.last_course_office_acc'])
        
        self._reset3 = set(['accumulators.last_landing_a320',
                           'accumulators.last_landing_a330',
                           'accumulators.last_landing_a340',
                           'accumulators.last_landing_a350',
                           'accumulators.last_landing_b737',
                           'accumulators.last_landing_f50',
                           'accumulators.last_landing_md80',
                           'accumulators.last_landing_crj',
                           'accumulators.cons_us_flight_acc',
                           'accumulators.lh_flight_acc'])

        self._reset6 = set(['accumulators.last_flown_a320',
                           'accumulators.last_flown_a330',
                           'accumulators.last_flown_a340',
                           'accumulators.last_flown_a350',
                           'accumulators.last_flown_b737',
                           'accumulators.last_flown_f50',
                           'accumulators.last_flown_md80',
                           'accumulators.last_flown_crj'])

    def getTablesToLoad(self):
        return ["accumulator_time"]


    def getFilterParams(self):
        return [("te_period_accumulator_time", "start", str(self.periodStart)[0:9]),
                ("te_period_accumulator_time", "end", str(self.periodEnd)[0:9]),
                ("te_period_accumulator_time", "start_time", str(self.periodStart)),
                ("te_period_accumulator_time", "end_time", str(self.periodEnd))]

    def clean(self, TM):
        all_accs = self.getAllAccs()

        count = 0
        acc_cache = {}

        Errlog.log("Building accumulator_time cache")
        start_time = time.time()

        for row in TM.accumulator_time:
            try:
                if row.name in all_accs:
                    acc_cache[(row.acckey, row.name)].append(row)
                    count += 1
            except KeyError:
                acc_cache[(row.acckey, row.name)] = [row]
                count += 1
            except KeyboardInterrupt:
                raise
            except:
                Errlog.log("Can't handle %s" % str(row))

        Errlog.log("Finished building accumulator_time cache")
        Errlog.log("Size of accumulator_time cache: %s" % (count))
        exec_time = time.time() - start_time
        Errlog.log("Finished in %.2f s" %(exec_time))

        Errlog.log("Starting cleaning. Will remove filt value when needed")
        start_time = time.time()

        # item are list of database rows partitioned on crew and accumulator
        for item in acc_cache.values():
            rows = []
            # decorate the rows, so we can sort on tim
            for row in item:
                rows.append((int(row.tim),row))
            rows.sort()

            # clean up the last-X by setting filt = None
            if len(rows) > 0:
                (_,row) = rows[0]
                reset_amount = self.getAmountToReset(row.name)
                for (_,row) in rows[-reset_amount:]:
                    if row.filt is not None:
                        Errlog.log("Removing filt on %s:" % (str(row)))
                        row.filt = None
                        
        exec_time = time.time() - start_time
        Errlog.log("Finished in %.2f s" %(exec_time))

    def getAllAccs(self):
        ''' Returns a set of all accumulator names that needs to be cleaned up '''
        return self._reset1 | self._reset2 | self._reset3 | self._reset6

    def getAmountToReset(self, name):
        '''
        Given name of an accumulator, return how meny entries we should remove
        'filt' values from
        '''
        if name in self._reset1:
            return 1
        elif name in self._reset2:
            return 2
        elif name in self._reset3:
            return 3
        elif name in self._reset6:
            return 6
        else:
            return 0

class InvalidNullValuesCleaner(DaveConnectorCleaner):
    """
    Find null base values and replace them with default values. 
    Null values where found in the trip table base column and might reappear. 
    In this class these faulty values should be replaced with the default base.
    """
    def clean(self, dc):
        ops = []
        columns = ['base']
        s = ['%s is null' % c for c in columns]
        search = ''.join(s)
        defaultBase = self.getDefaultBase()

        if not defaultBase:
            Errlog.log("The default base is missing, nothing will be done.")
            return ops

        Errlog.log("Default base %s found. Proceeding to replace null values..." % defaultBase)
        for entry in self.dbsearch(dc, 'trip', '(%s)' % search):
            for c in columns:
                entry[c] = defaultBase

            ops.append(createOp('trip', 'U', entry))
                
        return ops
        
    def getDefaultBase(self):
        """
        Returns the default base specified in the DefaultBaseDefinitions etab file.
        """
        baseDefinitionsLoc = Crs.CrsGetAppModuleResource("default",Crs.CrsSearchAppExact,"default",Crs.CrsSearchModuleExact,"BASE_FILES_DIR")
        baseDefinitionsName = Crs.CrsGetAppModuleResource("default",Crs.CrsSearchAppExact,"default",Crs.CrsSearchModuleExact,"BASE_DEF_DIR")
        baseDefinitionsEtab = '/'.join((baseDefinitionsLoc, baseDefinitionsName, 'DefaultBaseDefinitions'))

        if not os.path.exists(baseDefinitionsEtab):
            Errlog.log("Could not find Base definitions file.")
            return ""
        else:
            Errlog.log("Found Base definitions file: " + baseDefinitionsEtab)
            etable = Etab.load(Etab.Session(), baseDefinitionsEtab)
            for row in etable:
                if row[2]: 
                    return row[0] 
                else: 
                    continue
            return ""


# Cleanup of old entries in the new_hire_follow_up table
# A crew is removed if ILC is performed more than 18 month ago
# and the latest follow up is scheduled more than 3 month ago.
# 2014-09-17 - Mikael Larsson (HiQ)
class NewHireFollowUpCleaner(MiradorCleaner):
    '''
    Cleaning job for new_hire_follow_up. Removes rows when a crew is no longer considerd new-hired.
    '''

    def getTablesToLoad(self):
        return ["new_hire_follow_up"]


    def clean(self, TM):

        now = time.gmtime()
        today = AbsTime.AbsTime(now[0], now[1], now[2], now[3], now[4]).day_floor()
        eighteen_months_ago = today.addmonths(-18)
        three_months_ago    = today.addmonths(-3)

        for row in TM.new_hire_follow_up :
            if (row.ilc_date < eighteen_months_ago          and 
                row.follow_up_3_end_date < three_months_ago and  
                row.follow_up_2_end_date < three_months_ago and  
                row.follow_up_1_end_date < three_months_ago) :

                Errlog.log("Removing crew %s from new_hire_follow_up table." %str(row.crew.id)) 
                
                row.remove()



class CleaningHandler(object):
    '''
    Cleaning framework. Will instansiate all cleaners, and then execute them one by one,
    setting up and cleaning up their respective environment. This to make each cleaner
    independant of eachother
    '''
    def __init__(self, dburl, schema):
        '''
        Constructors, creates the TableManager object and instansiates all cleaners
        '''
        self._dburl = dburl
        self._schema = schema
        self.TM = tm.TMC(self._dburl, self._schema)

        self._cleaners = []
        self._cleaners.append(StudioDefaultFlightLegCleaner())
        self._cleaners.append(LinkCleaner())
        self._cleaners.append(TaskCleaner())
        self._cleaners.append(AccumulatorTimeCleaner())
        self._cleaners.append(AccumulatorRelCleaner())
        self._cleaners.append(InvalidNullValuesCleaner())
        self._cleaners.append(NewHireFollowUpCleaner())

    def setFilters(self, cleaner):
        ''' Applies DAVE filters to the model '''
        Errlog.log("Applying filters for %s" % (str(cleaner)))
        for (selection, param, value) in cleaner.getFilterParams():
            Errlog.log("\t Setting Filter: %s.%s = %s" % (selection, param, value))
            self.TM.addSelection(selection, param, value)

    def run(self):
        ''' Loops over all cleaners and executes them'''
        for cleaner in self._cleaners:
            Errlog.log(" *** Working on %s ***" % str(cleaner))

            if isinstance(cleaner,MiradorCleaner):
                self.handleMiradorCleaner(cleaner)
            elif isinstance(cleaner,DaveConnectorCleaner):
                self.handleDaveConnectorCleaner(cleaner)


    def handleMiradorCleaner(self, cleaner):
        """
        Deals with all MiradorCleaner objects
        """
        # Apply filters
        self.setFilters(cleaner)

        # Load tables
        tables = cleaner.getTablesToLoad()
        Errlog.log("Loading tables: %s" % ", ".join(tables))
        start_time = time.time()
        
        self.TM(tables)
        exec_time = time.time() - start_time
        Errlog.log("Finished in %.2f s" %(exec_time))
        
        # To be honest, don't know why or if it should be there.
        self.TM.newState()
            
        # Clean
        try:
            cleaner.clean(self.TM)
            # Save
            Errlog.log("Saving...")
            start_time = time.time()
            self.TM.save()
            exec_time = time.time() - start_time
            Errlog.log("Save finished in %.2f s" %(exec_time))
                
        except AbortException, err:
            Errlog.log("Cleaning aborted due to: %s" % str(err))
                

        # Unload tables
        self.TM.unloadTables(tables)


    def handleDaveConnectorCleaner(self, cleaner):
        """
        Deals with all DaveConnector cleaners
        """
        dc = DaveConnector(self._dburl, self._schema)
        now = time.gmtime()
        now = str(AbsTime.AbsTime(now[0], now[1], now[2], now[3], now[4]))
        dc.getConnection().setProgram(str(cleaner) + '(' + now + ')')
        try:
            start_time = time.time()
            ops = cleaner.clean(dc)
            exec_time = time.time() - start_time
            Errlog.log("Finished in %.2f s" %(exec_time))

            Errlog.log("Produced %d operations" % (len(ops)))
            if len(ops) > 0:
                start_time = time.time()
                commitid = DaveStorer(dc, reason="Nightly cleanup").store(ops, returnCommitId=True)
                exec_time = time.time() - start_time
                Errlog.log("Saved the %d operations with commitid %d (took %.2f s)" % (len(ops), commitid, exec_time))
                
        except AbortException, err:
            Errlog.log("Cleaning aborted due to: %s" % str(err))
            
        dc.close()
        


if __name__ == 'carmusr.NightlyCleanups':
    
    now = time.strftime("%d%b%Y %H:%M:%S",time.gmtime())
    Errlog.log("%s, running at %s"%(__name__, now))
    
    parser = OptionParser()
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

    ch = CleaningHandler(opts.connect, opts.schema)
    ch.run()
    del ch
