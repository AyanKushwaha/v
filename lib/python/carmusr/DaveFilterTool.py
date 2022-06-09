"""
DaveFilterTool
Module for doing:
Sets dave load filter before load of plan.
Verifies that filter exists before apllying it!
Uses an EC object to check filters before setting them in tm
"""


from utils.dave import EC, RW
import AbsTime
import RelTime
import Errlog
import traceback
import carmusr.application as application
stand_alone = False
try:
    import Cui
    import Variable
except ImportError:
    stand_alone = True

import tm


baseline_zero_date = '1Jan1901' # year "zero"

class DaveFilterTool:
    """
    Class which handles dave filtering by peeking in database before actual opening of database
    """
    def __init__(self, db="", schema=""):
        
            
        self._filter_names = set()
        self._filter_entities = set()
        self._filter_params = set()
        if db and schema:
            self._db = db
            self._schema = schema
        elif not stand_alone:
            (self._db, self._schema) = self.get_cnx_and_schema() 
        if not self._db or not self._schema:
            raise Exception("DaveFilterTool.py:: Could not set connectionstring "+\
                            "or schema name")
        self._used_filters = set()
        
        # Preload data
        ec = None
        try:
            ec = self._get_EC()
            for ds in ec.dave_entity_filter:
                self._filter_names.add(ds.selection)
                self._filter_entities.add((str(ds.selection), str(ds.entity)))
            for dp in ec.dave_selparam:
                self._filter_params.add((str(dp.selection), dp.name))
        finally:
            if ec:
                ec.close()
        
    def get_cnx_and_schema(self):
        """
        Lookup db connection details from subplan
        """
        connstr = Variable.Variable("")
        schema = Variable.Variable("")
        Cui.CuiGetSubPlanDBPath(Cui.gpc_info, connstr, schema)
        return (connstr.value, schema.value)

    
    
    def check_crew_empno_id(self, crew, date=None):
        ec = None
        try:
            ec = self._get_EC()
            for row in ec.crew_employment.search("(extperkey='%s')"%crew):
                if date:
                    if row.validfrom <= date and row.validto>=date:
                        return str(row.crew)
                else:
                    return str(row.crew)
                
            for row in ec.crew.search("(id='%s')"%crew):
                return str(row.id)
            return ""
        finally:
            if ec:
                ec.close()


    def get_baseline(self, list):
        """ BASELINE, We need to use EC to peek in database ###########
        """
        baselineTime = AbsTime.AbsTime(baseline_zero_date)
        ec = None
        try:
            ec = self._get_EC()
            for baseline in ec.accumulator_int_run.search("(accname='balance')"):
                if baseline.acckey in list:
                    if  baseline.accstart is not None: # Just a safe-guard
                        baselineTime = AbsTime.AbsTime(baseline.accstart)
                    else:
                        self.__log("accumulator_int_run had"+\
                                   " no acctart-value for key balance+"+\
                                   str(baseline.acckey))
            return baselineTime
        finally:
            if ec:
                ec.close()
                
    def set_baseline_filter(self, period_start_time,
                            period_end_time=AbsTime.AbsTime('31DEC2099 23:59'),
                            studio=False):
        """
        Special handling of baseline filter.
        A user operated studio will only load account_entries inside roster period
        For the day of operations tracker operated studio only a narrow margin is needed
        Server studios will used shared baseline with manpower
        """
        #commented out pending some pd development -pergr 
##         if studio and not stand_alone:
##             # To avoid boundry issues add one day,
##             # but let's add some robustness in case period_end is end of rave time
##             try:
##                 new_period_end_time = period_end_time.adddays(1)
##                 period_end_time = new_period_end_time
##             except:
##                 pass
##             baseline = self.get_baseline(['DAILY'])
##             if baseline != AbsTime.AbsTime(baseline_zero_date) and baseline <= period_start_time:
##                 self.set_param_filters([("baseline", "start_time", str(baseline)),
##                                         ("baseline", "end_time", str(period_end_time))]) 
##                 return
        if application.isDayOfOps:
            baseline = self.get_baseline(['SHORT'])
        else:
            baseline = self.get_baseline(['C','F'])
            if baseline > period_start_time:
                baseline = self.get_baseline(['MIGRATION'])
            if baseline > period_start_time:
                baseline = AbsTime.AbsTime(baseline_zero_date)

        # not user studio 
        self.set_param_filters([("baseline", "start_time", str(baseline)),
                                ("baseline", "end_time", str(period_end_time))])

    def set_filter(self, name):
        """
        Sets a filter without params!
        """
        self.set_param_filter(name)

    def set_param_filters(self, param_filters):
        """
        Need to be list of tuples (name, param, value)
        """
        for name, param, value in param_filters:
            self.set_param_filter(name, param, value)


    
    def set_param_filter(self, name, param='', value=''):
        """
        Sets given filter to table manager object
        """
        try:
            #Validate filters by dave lookup
            msg = self._verify_filter_name_and_param(name,param)
            if msg == "":
                if param != '':
                    tm.TM.presetSelection(name,param,value)
                else:
                    tm.TM.presetSelection(name)
                if param != '':
                    self.__log("Set Filter: "+name+\
                               "."+param+" = "+value)
                else:
                    self.__log("Set Filter: "+name)
                self._used_filters.add(name)
            else:
                log_string = "Warning!, setting Filter: %s failed: %s "
                if param != '':
                    self.__log(log_string%(name+"."+param+" = "+value, msg))
                else:
                    self.__log(log_string%(name, msg))
        except Exception, err:
            traceback.print_exc()
            self.__log("Error setting filter: "+str(err))

    def check_tables_for_filter_use(self, tables_to_check):
        """
        Checks tables for filter usage. PRints which used filter affects which tables
        """
        print_dict = {}
        for filter in self._used_filters:
            print_dict[filter] = []
        print_dict['no filter'] = []
        filter_setup = {}
        for selection,table in self._filter_entities:
            if selection not in self._used_filters:
                continue
            if not filter_setup.has_key(selection):
                filter_setup[selection] = set()
            filter_setup[selection].add(table)
           
        for table in tables_to_check:
            match_found = False
            for selection in filter_setup:
                if table in filter_setup[selection]:
                    print_dict[selection].append(table)
                    match_found = True
            if not match_found:
                print_dict['no filter'].append(table)
        for filter, tables in print_dict.items():
            self.__log("Filter '%s' affects tables: %s"%(filter,", ".join(tables )))
                        
    def _verify_filter_name_and_param(self,name,param):
        """
        Check that filter exists in schema before setting it
        """
        if not name in self._filter_names:
            for _n in sorted(self._filter_names): print "  ",_n
            return "Found no filter called %s" % name
        if param != '':
            if not (name,param) in self._filter_params:
                return "Found no filter called %s with param %s" % (name, param)
        return ""
    
    def _verify_filter_name(self,name):
        """
        Check that filter exists in schema before setting it
        """
        if not name in self._filter_names:
            for _n in sorted(self._filter_names): print "  ",_n
            return "Found no filter called %s" % name
        return ""
            
    def _get_EC(self):
        """
        Returns an EntityConnection to schema in database
        """
        return EC(self._db,self._schema)
    
    def __log(self, message):
        """
        Log to errlog, but prepend class name
        """
        Errlog.log("%s: %s"%(self.__class__.__name__, message))
# end of file
