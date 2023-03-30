###################################################################

###################################################################

__version__ = "$Revision$"
"""
Filterhandler

Module for doing:
Keep the table crew_user_filter in database populated with correct data!
Updating cmp filter 
@date:20May2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import tm 
import AbsTime
import RelTime
import time
from modelserver import EntityNotFoundError
from modelserver import ReferenceError
import utils.ServiceConfig as ServiceConfig
import sys
import Errlog
import time
import utils.time_util as time_util
import utils.TimeServerUtils as TimeServerUtils
import copy
import getopt

country2planning_group_map = {"NO":"SKN", "SE":"SKS", "DK":"SKD"}


#Filter properties

_PLANNING_GROUP = 'PLANNING_GROUP'
_ACQUAL = 'ACQUAL'
_MAINCAT = 'MAINCAT'
_ACTIVE = 'ACTIVE'
_RETIRED = 'RETIRED'
_MISMATCH = 'MISMATCH'

_CONTRACT='CONTRACT'
_EMPL = 'EMPLOYMENT'
_EMPL_TMP = 'EMPLOYMENT_TMP'
_ACTIVE = 'ACTIVE'
_RETIRED = 'RETIRED'
_MISMATCH = 'MISMATCH'

_FILTER_DICT = {_ACTIVE:_CONTRACT,
                _MISMATCH:_CONTRACT,
                _RETIRED:_CONTRACT,
                _EMPL:_EMPL,
                _ACQUAL:_ACQUAL}

_ONE_DAY = RelTime.RelTime('24:00')
class _uninitialized:
    pass

class FilterHandler(dict):
    def __init__(self, dbcnx=None, schema=None):
        self['tm'] = _uninitialized
        self['schema'] = schema
        self['dbcnx'] = dbcnx
        self['errors'] = set()
        self['today'] = TimeServerUtils.now_AbsTime().day_floor()
        self['now'] = TimeServerUtils.now_AbsTime()
        self['tables']=set()
        
    def __getattr__(self, attr):
        if attr == 'TM':
            if self['tm'] is _uninitialized:
                if self['schema'] and self['dbcnx']:
                    Errlog.log(self.__class__.__name__+\
                               ':: Connecting to %s'%(self['dbcnx']))
                    self['tm'] = tm.TMC(self['dbcnx'], self['schema'])
                else:
                    self['tm'] = tm.TM
            return self['tm']
        elif attr in self['tables']:
            return self.table_iterator(attr)
        elif self.has_key(attr):
            return self[attr]
        else:
            raise Exception(self.__class__.__name__+\
                            ":: Error, attribute %s not implemented"\
                            %(attr))
    def add_error(self, err):
        self.errors.add('%s:: %s'%(self.__class__.__name__,err))

    def print_errors(self):
        if self.errors:
            Errlog.log(self.__class__.__name__+':: Errors in run! :(')
            for err in self.errors:
                Errlog.log(err)
        else:
            Errlog.log(self.__class__.__name__+':: No errors in run! :)')
            
    def set_newstate_if_needed(self):
        """
        If schema and dbcnx is set, if run as stand alone
        """

        # Load all tables before newstate, otherwise it wouldn't save!!
        self.TM(list(self.tables))
        
        if self['schema'] and self['dbcnx']:
            self.TM.newState()
        
    def do_save_if_needed(self):
        """
        If schema and dbcnx is set, it is run as stand alone
        """

        if self['schema'] and self['dbcnx']:
            Errlog.log(self.__class__.__name__+":: Saving to database") 
            self.TM.save()
    
    def table_iterator(self, table_name):
        return self.TM.table(table_name)

    def update_run(self):
        Errlog.log(self.__class__.__name__+":: Running update %s"%self.now)
        # If ran as standalone, we need to set newstate
        self.set_newstate_if_needed()
        # Do the update
        self.update_impl()
        # If ran as standalone, we need to save
        self.do_save_if_needed()
        self.print_errors()
        Errlog.log(self.__class__.__name__+":: Update done!")
        
    def update_impl(self):
        pass
    
class CrewUserFilterHandler(FilterHandler):
    """
    Class for updating the crew_user_filter table
    Can be run as part of studio if created without arguments
    or as stand alone via mirador if called with db-connection and schema

    Currently handles:

    PLANNING_GROUP = crew planning_group from crew_employment
    ACQUAL = crew acqual from crew_qualification
    """
    def __init__(self, dbcnx=None, schema=None, crew_id=None):
        FilterHandler.__init__(self, dbcnx, schema)
        self['crew_cache'] = None
        self['crew_id'] = crew_id
        self['tables']=set(['crew_user_filter',
                            'crew_qualification',
                            'crew_employment',
                            'crew_contract',
                            'crew'])
    def __getattr__(self, attr):
        if attr == 'crew_cache':
            return self.__crew_cache()
        else:
            return FilterHandler.__getattr__(self, attr)

    def __crew_cache(self):
        if self['crew_cache'] is None:
            self['crew_cache'] = {}
            t1 = time.time()
            self.__populate_interval_cache(self['crew_cache'])
            Errlog.log('CrewUserFilterUpdate:: '+\
                       'populate of crew_cache took %f s for %d crew'%\
                       (time.time()-t1, len(self['crew_cache'])))
        return self['crew_cache']
   

    
    def table_iterator(self, table_name):
        if self.crew_id:
            try:
                crew_ref = self.TM.crew[(self.crew_id,)]
                if table_name == 'crew':
                    return {self.crew_id:crew_ref}
                return crew_ref.referers(table_name,'crew')
            except EntityNotFoundError:
                return self.TM.table(table_name).search('(crew='+self.crew_id+')')
        else:
            return self.TM.table(table_name)

    def set_crew_id(self, crew_id):
        self['crew_id'] = crew_id
        


    def update_impl(self):
        """
        Method to run as part of batch process during night!
        """
        self.remove_non_valid_rows()
        self.populate_crew_user_filter()
        self.update_crew_retirement_date()
        
    def __update_crew_with_set(self, crew, retirement_set):
        """
        Uses retired interval set to update property crew.retirementdate
        """
        ret_date = None
        for ret_interval in retirement_set:
            ret_date_candidate = ret_interval.first.adddays(-1)
            # Check contract 
            if ret_interval.first <= self.today and \
                   ret_interval.last > self.today:
                ret_date = ret_date_candidate 
                break
            elif ret_interval.first > self.today:
                if ret_date is None or ret_date <= ret_date_candidate:
                    ret_date = ret_date_candidate
            
        # We found a retired contract valid now or in the future, let's update the crew table
        if not ret_date is None and \
               (crew.retirementdate is None or crew.retirementdate != ret_date):
            Errlog.log('CrewUserFilterHandler:: Setting retirementdate for crewid %s to %s'% (crew.id, ret_date))
            crew.retirementdate = ret_date
        # Crew has some retired contract but not valid now and not in the future (i.e. historic)
        if ret_date is None and not (crew.retirementdate is None):
            crew.retirementdate = None
            Errlog.log('CrewUserFilterHandler:: '+\
                       'Setting retirementdate for crewid %s to %s'% (crew.id, 'NONE'))
            
        
    def update_crew_retirement_date(self):
        """
        Updates crew.retirementdate using RETIRED contracts collected in crew_cache
        as follows:
        
        if crew is retired now:
           then start of the contract 
        else if a future retirement contract exist:
           then start of that contract
        else
           null

        """
        for crew_id, cache in self.crew_cache.items():
            crew = self.crew[crew_id]
            retired_intervals_tmp =cache.get(_RETIRED,[]) 
            retired_intervals = sorted(retired_intervals_tmp, reverse=True)
            emp_period_tmp = cache.get(_EMPL_TMP,[])
            emp_period = sorted(emp_period_tmp, reverse=True)
            if not retired_intervals:
                if  crew.retirementdate is None:
                    continue #No update needed
                else:
                    #Crew has no retired contract
                    crew.retirementdate = None
                    Errlog.log('CrewUserFilterHandler:: '+\
                               'Setting retirementdate for crewid %s to %s'% (crew.id, 'NONE'))
            else: 
                            
                update_crew_retirement = True
                ret_end_date = None
                emp_end_date = None
                # Only consider the latest retirement interval
                for (start,end) in retired_intervals:
                    ret_end_date = end
                    break
                # Only consider the latest emp period
                for (start,end) in emp_period:
                    emp_end_date = end
                    break
                # Check if a valid emp contract exists after retirement (rehire)
                if emp_end_date > ret_end_date and emp_end_date > self.today:
                    update_crew_retirement = False
                    if crew.retirementdate is None:
                        # Do nothing
                        continue
                    else:
                        # Valid emp contract after retirement - Make retirement date empty
                        print ("Updating Crew : " + str(crew.id) + " Emp End : " + str(emp_end_date) + " Ret End : " + str(ret_end_date))
                        crew.retirementdate = None
                if update_crew_retirement :        
                    self.__update_crew_with_set(crew, retired_intervals)
                    
                        

    def populate_crew_user_filter(self):
        """
        Populates the crew_user_filter table with implemented properties,
        currently
        PLANNING_GROUP
        ACQUAL
        ACTIVE
        RETIRED
        MAINCAT
        MISMATCH
        """
        
        for crew_id, cache in self.crew_cache.items():
            # log active contracts
            self.__cache_to_table_insert(crew_id, cache, _ACTIVE)
            #log retired contracts
            self.__cache_to_table_insert(crew_id, cache, _RETIRED)
            #log mismatches between active and employed
            self.__cache_to_table_insert(crew_id, cache, _MISMATCH)
            # log maincat  & planning_group
            self.__cache_to_table_insert(crew_id, cache, _EMPL, nested=True)
            #log ac_quals
            self.__cache_to_table_insert(crew_id, cache, _ACQUAL, nested=True)

    def remove_non_valid_rows(self):
        """
        Matches all rows agains existing crew properties in db
        Only run this method when running night job with unfiltered data,
        otherwise we might remove due to no having loaded all data!
        """
        # ADD MORE PROPERTIES HERE
        tests = {_ACQUAL:self.__test_nested_row,
                 _EMPL:self.__test_nested_row,
                 _CONTRACT:self.__test_row}
        
        removed_rows = 0
        for filter_row in self.crew_user_filter:
            try:
                test = tests.get(filter_row.filt.upper(),None)
                if test:
                    if not test(filter_row):
                        #Row removed
                        removed_rows += 1
                else:
                    raise Exception("No test found for row %s"%str(filter_row))
            except Exception, err:
                filter_row.remove()
                self.add_error(err)
        Errlog.log('CrewUserFilterHandler :: Removed %d non-valid filter rows'%removed_rows)
        
    def __cache_to_table_insert(self, crew_id, cache, key, nested=False):
        try:
            crew_ref = self.TM.crew[(crew_id,)]
            for value in cache.get(key,{}):
                if nested:
                    for interval in cache[key].get(value,[]):
                        self.__update_crew_filter_table(crew_ref,
                                                        _FILTER_DICT[key],
                                                        value,
                                                        interval.first,
                                                        interval.last)
                else:
                    self.__update_crew_filter_table(crew_ref,
                                                    _FILTER_DICT[key],
                                                    key,
                                                    value.first,
                                                    value.last)
        except Exception, err:
            self.add_error('__cache_to_table_insert: %s'%err)
                
    def __update_crew_filter_table(self, crew, filter, value, validfrom, validto):
        """
        Updates the crew_user_filter table with arguments
        creates row if needed
        """
        key = (crew, filter.upper(), value, validfrom)
        
        try:
            filter_row = self.TM.crew_user_filter[key]
        except:
            filter_row = self.TM.crew_user_filter.create(key)
            
        if filter_row.validto is None or \
               filter_row.validto != validto:
            filter_row.validto = validto
            filter_row.si = 'Updated '+ time.strftime('%d%b%Y %H:%M',time.gmtime())
            
        
    
    def __test_row(self, filter_row):
        """
        Test if row still is valid
        """
        cache = self.crew_cache.get(filter_row.crew.id,[])
        for period in cache.get(filter_row.val,[]):
            if   period.first == filter_row.validfrom and \
                   period.last == filter_row.validto:
                # match found, keep this row!
                return True
        #No match found, remove row!
        filter_row.remove()
        return False
        
    def __test_nested_row(self, filter_row):
        """
        Test if row still is valid, this tests handles the'nested' data structure in crew_cache
        """
        cache = self.crew_cache.get(filter_row.crew.id,[])
        for value in cache.get(filter_row.filt,[]):
            for period in cache[filter_row.filt].get(value,[]):
                if filter_row.val == value and \
                       period.first == filter_row.validfrom and \
                       period.last == filter_row.validto:
                    # match found, keep this row!
                    return True
        #No match found, remove row!
        filter_row.remove()
        return False
      
    def __populate_interval_cache(self, crew_cache):
        """
        crew_cache structure is
        dictionaries like:

        [crew_ref][_RETIRED]  = IntervalSet where crew is retired
                  [_ACTIVE]   = IntervalSet where crew has active contract
                  [_MISMATCH] = Intervalset where crew has active contarct but no employment
                  [_EMPL][maincat|planning_group] = Intervalset where crew has maincat and planning_group
                  [_ACQUAL][qual] = Interval where crew has qual
                  
        e.g. [(10033)]['RETIRED'] = (1dec2015 - 31dec2035)
                      ['ACTIVE'] = (1jan1998 - 1dec2015)
                      ['MISMATCH'] = (1jan1998 - 1dec1998),(1jan2000 - 1dec 2000)
                      ['EMPLOYMENT']['F|SKS'] = (1dec1998 - 1jan2000)(1dec2000 -1dec2015)
                      ['ACQUAL']['37|38'] = (2feb1999 - 1jan2005)
                      ['ACQUAL']['A4'] = (2feb2005 - 1jan2035)
                      
        """
        empty_interval_set = time_util.IntervalSet()
        org_crew_id = self.crew_id
        try:
            self.__collect_contract_data(crew_cache)
        except Exception, err:
            self.add_error('__get_populate_cache: collect contract data: %s'%err)
        for crew_id in crew_cache:
            self.set_crew_id(crew_id) #Make update work only on this crew
            try:
                self.__collect_employment_data(crew_cache)
            except Exception, err:
                self.add_error('__get_populate_cache: collect employment data: %s'%err)   
            # Get diff
            #Find period where crew has active contract but no employment
            active_interval_set = crew_cache[crew_id].get(_ACTIVE, empty_interval_set)
            retired_interval_set = crew_cache[crew_id].get(_RETIRED, empty_interval_set)
            empl_set = crew_cache[crew_id].get(_EMPL_TMP, empty_interval_set)
            active_cut_empl = active_interval_set.difference(empl_set)
            empl_cut_active = empl_set.difference(active_interval_set)
            # Cuts all retired contract periods as you are allowed to have employment then
            empl_cut_contract = empl_cut_active.difference(retired_interval_set)
            crew_cache[crew_id][_MISMATCH] = active_cut_empl.union(empl_cut_contract)
            try:   
                self.__collect_ac_qual_data(crew_cache)
            except Exception, err:
                self.add_error('__get_populate_cache: collect acqual data: %s'%err)
        self.set_crew_id(org_crew_id)
        return crew_cache
    
    def __collect_contract_data(self, crew_cache):
        # Lookup intervals in crew contract and merge using time_util interval class
        for contract in self.crew_contract:
            try:
                active = [_RETIRED,_ACTIVE][contract.contract.grouptype.upper() != "R"]
                self.__add_to_cache(crew_cache, contract.crew,
                                time_util.DateInterval(contract.validfrom,
                                                       contract.validto),
                                key1=active,
                                key2=None)
            except ReferenceError, e:
                self.add_error('__collect_contract_data: %s' % e)
                # Catch problematic records from SKJMP-1407 causing SKS-516
            except AttributeError, attribute_error:
                self.add_error('__collect_contract_data: %s' % attribute_error)
        return crew_cache
    
    def __collect_employment_data(self, crew_cache):
        #Gather all employment data in set
        for empl in self.crew_employment:
            self.__add_to_cache(crew_cache, empl.crew,
                                 time_util.DateInterval(empl.validfrom,
                                                        empl.validto),
                                 key1=_EMPL_TMP,
                                 key2=None)
            #Store maincat interval!
            #lets use the most info we can
            # Catch problematic records from SKJMP-1407 causing SKS-516
            try:
                maincat = str(empl.titlerank.getRefI('maincat')).upper()
            except AttributeError, attribute_error:
                self.add_error('__collect_employment_data: %s' % attribute_error)
            #self.__add_to_cache(crew_cache, empl.crew,
            #                    time_util.DateInterval(empl.validfrom,
            #                                           empl.validto),
            #                    key1=_MAINCAT,
            #                    key2=maincat)
            #Store planning_groups
            planning_group = str(empl.getRefI("planning_group")).upper()
            country = str(empl.getRefI("country")).upper()
            if planning_group:
                key2=[maincat, planning_group]
                self.__add_to_cache(crew_cache, empl.crew,
                                     time_util.DateInterval(empl.validfrom,
                                                            empl.validto),
                                     key1=_EMPL, key2='|'.join(key2))
            if country and planning_group != "SVS":
                #  NO->SKN,SE->SKS or DK->SKD else SKI
                second_planning_group = country2planning_group_map.get(country,"SKI")
                if second_planning_group != planning_group:
                    second_planning_group = second_planning_group+'_CCT'
                    key2=[maincat, second_planning_group]
                    self.__add_to_cache(crew_cache, empl.crew,
                                        time_util.DateInterval(empl.validfrom,
                                                               empl.validto),
                                        key1=_EMPL, key2='|'.join(key2))
                                            
    def __collect_ac_qual_data(self, crew_cache):
        for ac_qual in self.crew_qualification:
            (typ, subtype) = str(ac_qual.getRefI('qual')).upper().split('+')
            if typ != 'ACQUAL':
                continue
            self.__add_to_cache(crew_cache, ac_qual.crew,
                                time_util.DateInterval(ac_qual.validfrom,
                                                       ac_qual.validto),
                                key1=_ACQUAL, key2=subtype)
        self.__merge_ac_quals(crew_cache)
        return crew_cache
    
    def __merge_ac_quals(self, crew_cache):
        cache = crew_cache[self.crew_id]
        crew_quals = set()
        for ac_qual in cache[_ACQUAL]:
            crew_quals.add(ac_qual)
        # Loop through quals and check 'em against each other
        for qual1 in crew_quals:
            for qual2 in [qual for qual in crew_quals if qual != qual1]:
                # Get sets
                if not cache[_ACQUAL].has_key(qual1) or \
                   not cache[_ACQUAL].has_key(qual2):
                    continue
                ac_qual1_set = cache[_ACQUAL][qual1]
                ac_qual2_set = cache[_ACQUAL][qual2]
                if ac_qual1_set == ac_qual2_set:
                    #Identical sets, lets merge 'em
                    del cache[_ACQUAL][qual1]
                    del cache[_ACQUAL][qual2]
                    key = [qual1, qual2]
                    key.sort() # Make sure val is sorted
                    cache[_ACQUAL]['|'.join(key)] = ac_qual1_set
                        
    def __add_to_cache(self, crew_cache, crew, interval, key1=None, key2=None):
        """
        Checks if struct is setup otherwise creates dicts before insert
        """
        crew_id = crew.id
        #Crew not in dict
        if not crew_cache.has_key(crew_id):
            crew_cache[crew_id] = {}
        # key1 not in dict
        if key1 and not crew_cache[crew_id].has_key(key1):
            if key2 is None:
                # not nested dict
                crew_cache[crew_id][key1] = time_util.IntervalSet()
            else:
                # nested dict
                crew_cache[crew_id][key1] = {}
        if key1 and key2 and not crew_cache[crew_id][key1].has_key(key2):
            # create nested dict
            crew_cache[crew_id][key1][key2] = time_util.IntervalSet()
        # insert into dicts
        if key1 and not key2:
            #not nested
            crew_cache[crew_id][key1].add(interval)
            crew_cache[crew_id][key1].merge()
        elif key1 and key2:
            #nested
            crew_cache[crew_id][key1][key2].add(interval)
            crew_cache[crew_id][key1][key2].merge()
        return crew_cache

class CMPFilterHandler(FilterHandler):
    """
    Updates the dave filter for crew_actitvity in dave_entity_filter.
    Needed because of lack of support for global joins in the dave filetering framework.
    """
    def __init__(self, dbcnx=None, schema=None):
        FilterHandler.__init__(self, dbcnx, schema)
        #Reset used tables
        self['tables'] = set(['dave_entity_filter',
                              'dave_filter_ref',
                              'dave_selection',
                              'leave_reduction_group'])

    def update_impl(self):
        """
        Method to run as part of batch process during night!
        """
        self.create_cmp_crew_activity_filter()
        
    def create_cmp_crew_activity_filter(self):
        """
        Take all reducing activities -2 to +1 year and create a large oracle in-clause, i.e. code in ('LA1',LA2',...)
        """
        # Table to filter
        table_name = 'crew_activity'
        # Time filters
        small_interval_expr="$.st <= (%:3+30)*1440 AND $.et >= (%:1-1)*1440"
        large_intervall_expr="$.st <= (%:3+366)*1440 AND $.et >= (%:1-366*2)*1440"
        
        
        # Create in-clause
        reduction_codes=set()
        
        for red_row in self.leave_reduction_group:
            try:
                reduction_codes.add("'%s'"%red_row.activity.id)
            except ReferenceError, err:
                self.add_error('create_cmp_crew_activity_filter::'+\
                               'Reduction table contains unsafe ref, %s'%str(err))
            
        if len(reduction_codes)>=1000:
            self.add_error('create_cmp_crew_activity_filter::'+\
                           'To long filter string, max 1000 in ORACLE in-clause')
            return

        if len(reduction_codes) == 0:
            reduction_codes.add("''")
            
        
        reduction_codes= list(reduction_codes)
        reduction_codes.sort()

        activity_expr='$.activity in ('+', '.join(reduction_codes[0:1000])+')'

        #Combine statements
        final_expr = '(%s) OR (%s AND (%s))'%(small_interval_expr,
                                              activity_expr,
                                              large_intervall_expr)

        try:
            selection = self.dave_selection[('mppperiod')]
            filter = self.dave_entity_filter[(selection, 'mppperiod'+"_"+table_name)]
            if filter.where_condition != final_expr:
                filter.where_condition = final_expr
                Errlog.log('CMPFilterHandler:: Updated cmp filter definition' )
        except Exception, err:
            self.add_error('create_cmp_crew_activity_filter::'+\
                           'Error setting where_condition in dave_entity_filter, %s'%str(err))
   
# If called from script via mirador

def script_run():
    c = ServiceConfig.ServiceConfig()
    try:
        mode = sys.argv[2].lower()
    except:
        mode = 'all'   
    try:
        schema = sys.argv[3].lower()
    except:
        (key,schema) = c.getProperty("data_model/schema")
    try:
        database = sys.argv[4].lower()
    except:
        (key,database)=c.getProperty("data_model/interface@url")

    Errlog.log("DB: " + database)
    Errlog.log("schema: " + schema)
    Errlog.log("Running FilterHandler")
    database = str(database)
    schema = str(schema)
    runs=[]
    
#   if mode == "cmp":
#       runs.append(CMPFilterHandler(database,schema))
#   else:
    runs.append(CrewUserFilterHandler(database,schema))
#       runs.append(CMPFilterHandler(database,schema))

    for updater in runs:
        updater.update_run()

    Errlog.log("FilterHandler Finished")

# Main entry

if len(sys.argv)>1 and sys.argv[1].lower() == 'standalone':
    script_run() 




# end-of-file 
