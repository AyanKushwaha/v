
__version__ = "$Revision$"

import os
import sys
import time
import traceback

import Errlog
from AbsTime import *
import AbsDate
import RelTime
import tm  
import datetime
import modelserver
import utils.ServiceConfig as ServiceConfig
import carmusr.application as application

class _uninitialized:pass #Class used as flag
                              
class AccountBaselineUpdater:
    def __init__(self,database,schema):
        """
        @param database = Database for schema
        @param schema    = schema to update
        """
        self._db=database
        self._schema=schema
        self._tmHandle=_uninitialized
        self._account_baseline= _uninitialized
        self._account_entry= _uninitialized
        self._lastbaseline= _uninitialized
        self._recalcExistingBaseline=False
        
    def getTM(self):
        """
        Getter for TMC-object
        """
        if self._tmHandle is _uninitialized:
            self._tmHandle=tm.TMC(self._db,self._schema)
            
        return self._tmHandle
    def getTable(self,tablename):
        """
        Gets table from tablemanger object
        """
        return self.getTM().__getattr__(tablename)
    def getKey(*args):
        """
        Creates a string key from given pairs of row entity + column
        """
        key=''
        for entity,ref in [args[x:x+2] for x in  range(1,len(args),2)]:
            try:
                key=key+':'+entity.nget(ref)
            except:
                key=key+':'+str(entity.getRefI(ref))
        return key
    def getAccountBaseline(self):
        """
        Get account_baseline cache
        """
        if self._account_baseline is _uninitialized:
            self._account_baseline={}
        return self._account_baseline
    def getAccountEntry(self):
        """
        Get account_entry cache
        """
        if self._account_entry is _uninitialized:
            self._account_entry={}
        return self._account_entry
    
    def cacheAccountBaseline(self):
        """
        Loops through account_baseline and caches/hashes values using
        self.getKey(baseline,''id'',baseline,''crew'') 
        """
        # Hash get last account_baseline since constant search is slower than plain lookup
        for baseline in self.getTable("account_baseline"):
            # incase filters not initialized
            if baseline.tim == self.getLastBaseline():
                key = self.getKey(baseline,"id",baseline,"crew")
                self.getAccountBaseline()[key]=baseline
                
    def cacheAccountEntry(self,accumulate_to_date):
        """
        Loops through account_entry and caches/hashes values using
        self.getKey(baseline,''id'',baseline,''crew'') 
        """
        for entry in self.getTable("account_entry"):
            # incase filters not initialized
            if entry.tim>=self.getLastBaseline() and \
               entry.tim<accumulate_to_date:
                key=self.getKey(entry,"account",entry,"crew")
                if not self.getAccountEntry().has_key(key):
                    self.getAccountEntry()[key]=[entry]
                else:
                    self.getAccountEntry()[key].append(entry)

    def setLastBaseline(self,accumulate_to_date, recalculate, accumulate_daily=False, accumulate_short=False):
        """
        Finds the current baseline date from accumulator_int_run
        CMP separates between F(lightdeck) and C(abin)
        """
        row = None
        migration_row = None
        try:
            if not accumulate_daily:
                if accumulate_short:
                    row = self.getTM().accumulator_int_run[('balance','SHORT')]
                else:
                    try:
                        row = self.getTM().accumulator_int_run[('balance','F')]
                    except modelserver.EntityNotFoundError:
                        row = self.getTM().accumulator_int_run[('balance','C')]
            else:
                try:
                    row = self.getTM().accumulator_int_run[('balance','DAILY')]
                except modelserver.EntityNotFoundError:
                    row = self.getTM().accumulator_int_run[('balance','MIGRATION')]
            migration_row = self.getTM().accumulator_int_run[('balance','MIGRATION')]
        except modelserver.EntityNotFoundError:
            pass
        if row is None or migration_row is None or migration_row.accstart is None:
            #No previous baseline!
            self._lastbaseline = AbsTime('1jan1901')
        elif row.accstart is None:
            Errlog.log("AccumulateBaseLine.py:: Warning, accumulator_int_run "+\
                       " did''nt contain accstart-value for key balance+"+str(row.acckey)+\
                       ". Will accumulate from migration date")
            self._lastbaseline = migration_row.accstart
        elif accumulate_to_date <= migration_row.accstart:
            raise Exception('Error! AccumulateBaseline.py: Desired new baseline date'+\
                            ' ('+str(accumulate_to_date)+')'+\
                            ' is before or same as migration date'+\
                            ' ('+str(migration_row.accstart)+')')
        elif accumulate_to_date <=  row.accstart and recalculate:
            self._lastbaseline = migration_row.accstart
        elif accumulate_to_date <=  row.accstart and not recalculate:
            raise Exception('Error! AccumulateBaseline.py: Desired new baseline date'+\
                            ' ('+str(accumulate_to_date)+')'+\
                            ' is before or same as current baselinedate'+\
                            ' ('+str(row.accstart)+'), but no recalc option was set!')
        elif accumulate_to_date > row.accstart:
            #New baseline after old one, the "normal" case!
            self._lastbaseline = row.accstart
        else:
            raise Exception("AccumulateBaseline.py:: Error setting prevoius baseline!")
         
    def getLastBaseline(self):
        """
        Returns the set baseline-date
        """
        if self._lastbaseline is  _uninitialized:
            raise Exception("Error! AccumulateBaseline.py: Last baseline not initialized")
        return self._lastbaseline

    def clearPreviousAccountBaseLine(self, accumulate_to_date):
        """
        Deletes all previous entries 
        """
        try:
            migration_row = self.getTM().accumulator_int_run[('balance','MIGRATION')]
            migration_baseline = migration_row.accstart
        except:
            migration_baseline = AbsTime('1jan1901')
        try:
            daily_row = self.getTM().accumulator_int_run[('balance','DAILY')]
            daily_baseline = daily_row.accstart
        except:
            daily_baseline = AbsTime('1jan1901')
        try:
            c_row = self.getTM().accumulator_int_run[('balance','C')]
            c_baseline = c_row.accstart
        except:
            c_baseline = AbsTime('1jan1901')
        try:
            f_row = self.getTM().accumulator_int_run[('balance','F')]
            f_baseline = f_row.accstart
        except:
            f_baseline = AbsTime('1jan1901')
        try:
            o_row = self.getTM().accumulator_int_run[('balance','SHORT')]
            o_baseline = o_row.accstart
        except:
            o_baseline = AbsTime('1Jan1901')

        for account_baseline in self.getTable("account_baseline"):
            if account_baseline.tim not in (migration_baseline,daily_baseline,c_baseline, f_baseline, o_baseline) and \
                   account_baseline.tim != accumulate_to_date and account_baseline.tim == self.getLastBaseline():
                Errlog.log(self.__class__.__name__+" Removing row %s"%str(account_baseline))
                account_baseline.remove()
        Errlog.log(self.__class__.__name__+"::Cleared baselines not matching %s"%'/'.join([str(_) for _ in (migration_baseline,
                                                                                                            daily_baseline,
                                                                                                            c_baseline,
                                                                                                            f_baseline,
                                                                                                            o_baseline)]))
    def updateBaseLine(self,accumulate_to_date, recalculate=False, accumulate_daily=False, accumulate_short=False):
        """
        Runs the update for all crew in table crew and all accounts in table account_set
        @param: Date to accumulate to
        """
        try:
            self.setLastBaseline(accumulate_to_date, recalculate, accumulate_daily, accumulate_short)
        except Exception, err:
            Errlog.log(str(err))
            return
        Errlog.log(self.__class__.__name__+":: AccumulateBaseline.py: Accumulating from "+str(self.getLastBaseline())+\
                  " to " + str(accumulate_to_date))

        # Cache account_entry table and account_baseline
        self.cacheAccountBaseline()
        self.cacheAccountEntry(accumulate_to_date)
        
        self.setNewState()

        for crew in self.getTable("crew"):
            for account in self.getTable("account_set"):
                self.updateForCrewAndAccount(crew,account,accumulate_to_date)
        if accumulate_daily:
            self.createOrUpdateAccIntRun(accumulate_to_date,'DAILY') # Special user daily baseline
        elif accumulate_short:
            self.createOrUpdateAccIntRun(accumulate_to_date,'SHORT')
        else:
            self.createOrUpdateAccIntRun(accumulate_to_date,'C') #CMP separetes flightdeck and cabin
            self.createOrUpdateAccIntRun(accumulate_to_date,'F')

        if recalculate:
            self.clearPreviousAccountBaseLine(accumulate_to_date)

        self.doSave()

    def updateForCrewAndAccount(self,crew,account,accumulate_to_date):
        """
        Run the update for crew and account
        """
        key=self.getKey(account,"id",crew,"id")
        balance=0
        if self.getAccountBaseline().has_key(key):
            # Ok, we have an old baseline 
            old_baseline=self.getAccountBaseline()[key]
            if old_baseline.tim < accumulate_to_date: #In case we recalc
                balance=old_baseline.val
        try:
            for entry in self.getAccountEntry()[key]:
                if entry.tim>= self.getLastBaseline() and \
                   entry.tim<accumulate_to_date: #Need to be strictly lesser!!
                    try:
                        balance=balance+entry.amount
                    except:
                        Errlog.log("Failed to parse entry: %s" % str(entry))
                        Errlog.log("Aborting...")
                        sys.exit(1)
        except KeyError:
            pass # Account didn't have any account_entries
##         Errlog.log(self.__class__.__name__+':: Crew %s account %s has on date %s : balance %d '\
##                    %(crew.id,account.id,str(accumulate_to_date),balance))
        
        self.createOrUpdateAccountBaseline(crew,account,accumulate_to_date,balance)
        
    def createOrUpdateAccountBaseline(self,crew,account,accumulate_to_date,amount):
        """
        Creates a new account_baseline-row or updates exiting on date
        """
        # Only store non-zero baselines to reduce memory-consumtion
        new_baseline_row=None
        try:
            new_baseline_row=self.getTable("account_baseline")[(account.id,
                                                                crew,
                                                                accumulate_to_date)]
            if amount == 0:
                # Ok, new amount on day is zero, thus remove row
                new_baseline_row.remove()
            elif new_baseline_row.val != amount:
                #only change if needed!
                new_baseline_row.val = amount
        except modelserver.EntityNotFoundError:
            if amount != 0:
                new_baseline_row=self.getTable("account_baseline").create((account.id,
                                                                           crew,
                                                                           accumulate_to_date))
                new_baseline_row.val=amount


        
    def createOrUpdateAccIntRun(self, accumulate_to_date,category):
        """
        Creates or updates the row in accumulator_int_run
        """
        try:
            row=self.getTM().accumulator_int_run[('balance',category)]
        except  modelserver.EntityNotFoundError, err:
            row=self.getTM().accumulator_int_run.create(('balance',category))
        
        row.accstart=accumulate_to_date
        row.accend=accumulate_to_date
        row.lastrun=AbsTime(datetime.date.today().strftime('%d%b%Y' ))    
                               
    def setNewState(self):
        """
        Sets the tablemanager in newstate
        """
        self.getTM().newState()
    def doSave(self):
        """
        Saves the tablemanager changes
        """
        self.getTM().save()


def main(argv):
    c = ServiceConfig.ServiceConfig()
    
    database = c.getPropertyValue("data_model/interface@url")
    schema = c.getPropertyValue("data_model/schema")
    Errlog.log("DB:" + database)
    Errlog.log("schema:" + schema)
    print argv
    try:
        date = AbsTime(argv[1])
    except:
        raise ValueError("Running accumulatebaseline update, no valid date option given! Arguments: %s"%str(argv))
    
    try:
        recalc = argv[2].upper() == "RECALC"
    except:
        recalc = False
    
    #commented out pending some pd development -pergr  
    ## try:
    ##     daily = argv[3].upper() == "DAILY"
    ## except:
    ##     daily = False
    
    ## if daily:
    ##     (_, __, day, ___, ____) = date.split()
    ##     date = date.month_floor()
    ##     if day >= 16:
    ##         date = date.addmonths(-2, PREV_VALID_DAY)
    ##     else:
    ##         date = date.addmonths(-3, PREV_VALID_DAY)
    
    try:
        acc_short = argv[3].upper() == "SHORT"
    except:
        acc_short = False

    daily = False
    short = False

    if application.isDayOfOps or acc_short:
        short=True
    
    Errlog.log("Running accumulatebaseline with date:"+ str(date))
    Errlog.log("Running accumulatebaseline with recalc-option: "+ str(recalc))
    Errlog.log("Running accumulatebaseline with daily-option: "+ str(daily))
    Errlog.log("Running accumulatebaseline with short-option: "+ str(short))
    updater=AccountBaselineUpdater(database,schema)
    updater.updateBaseLine(date, recalc, daily, short)        

if __name__== "__main__":
    main(sys.argv)
elif len(sys.argv)>1 and sys.argv[1]=='main':
    argv = sys.argv
    argv.remove('main')
    main(argv)
