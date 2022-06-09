'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import time

class data_002_ReferenceIntegrity(DaveTestFixture):
    """
    Tests schema consistency.
    """
    
    #@REQUIRE("NotMigrated")
    def __init__(self):
        self.from_revid = 0
    
    def setRevIdFromTime(self, the_time = None):
        """ Sets the revid id from a time by looking backwards from the the_time 
            argument e.g. "01May2012"
            If no argument supplied, we will look one month back.
            May be used to only look for inconsistencies later than a certain time.
        """

        if the_time is None:
            from_time = int(AbsTime(time.strftime("%d%b%Y", time.localtime())).addmonths(-1))*60
        else:
            from_time = int(AbsTime(the_time))*60
         
        statement = "SELECT revid FROM dave_revision WHERE committs BETWEEN %s AND %s ORDER BY revid DESC" % (from_time - 10*24*60*60*10, from_time) 
                 
        for revid in self.sql(statement):
            self.from_revid = revid[0]
            break
                 
    
    def checkReferenceIntegrity(self, ptable):
        for table, col, tcol in self.sql("select c_ent_name,c_fk_keycols,c_fk_tgtcols from dave_entity_fks where c_fk_tgtname = '%s'" % ptable):
            self.log("Checking %s against %s" % (table,ptable))
            #sql = "SELECT distinct %(col)s FROM %(table)s WHERE deleted='N' and next_revid=0 AND %(col)s NOT IN (SELECT %(tcol)s FROM %(ptable)s WHERE deleted='N' and next_revid=0)" % locals()
            comp = ' and '.join('%s.%s=%s.%s' % (ptable, y,table, x) for x,y in zip(col.split(','),tcol.split(',')))
            scomp = ' and not ' + ' and not '.join('%s.%s is null' % (table, x) for x in col.split(','))
            oldest_valid_revid = self.from_revid 
            sql = "SELECT distinct %(col)s FROM %(table)s WHERE deleted='N' and revid >= %(oldest_valid_revid)s and next_revid=0 %(scomp)s AND NOT EXISTS(SELECT %(tcol)s FROM %(ptable)s WHERE deleted='N' and next_revid=0 and %(comp)s)" % locals()
            #print sql
            rows = self.sql(sql)
            if len(rows) > 0:
                self.log("%d Row(s) %s in %s without parent %s" % (len(rows),','.join(map(lambda x:'+'.join(map(str,x)), rows)), table, ptable), severity="warning")

    def test_001_crew(self):
        return self.checkReferenceIntegrity('crew')

    def test_002_flight_leg(self):
        return self.checkReferenceIntegrity('flight_leg')

    def test_003_trip(self):
        return self.checkReferenceIntegrity('trip')

    def test_004_airport(self):
        return self.checkReferenceIntegrity('airport')

    def test_005_region(self):
        return self.checkReferenceIntegrity('region')

    def test_006_crew_category_set(self):
        return self.checkReferenceIntegrity('crew_category_set')

    def test_010_account(self):
        return self.checkReferenceIntegrity('account_set')

    def test_011_salary_article(self):
        return self.checkReferenceIntegrity('salary_article')
    
    def test_012_hotel(self):
        return self.checkReferenceIntegrity('hotel')

    def test_013_meal_order(self):
        return self.checkReferenceIntegrity('meal_order')

    def test_014_meal_update_order(self):
        return self.checkReferenceIntegrity('meal_order_update')

    def test_015_ground_task(self):
        return self.checkReferenceIntegrity('ground_task')

    def test_016_crew_activity(self):
        return self.checkReferenceIntegrity('crew_activity')
