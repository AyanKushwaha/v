"""
Handler to update crew_flight_duty_attr based on files from the SYNC mechanism.
This is due to not enough information in TI3 to correctly recreateall training attributes from the dutycode.


This is a temporary interface that will begin to execute in parallel with Ti3. As soon as Ti3 is stopped,
so must this interface.

The implementation is split into two parts, a message handler and the class that does the update.
The class that does the update uses a somewhat generic baseclass and specializes it for
crew_flight_duty_attr. It was once meant that there would also be a specialized class for
crew_ground_duty_attr, but it was later deemed much to complicated and would fit better into
Ti3 anyway. Crew_flight_duty_attr is handled because in Ti3 it is impossible to differenciate between
a LIFUS and a ZFTT LIFUS.
"""


__author__ = "Christoffer Sandberg, Jeppesen"
__version__ = "$Revision$"

import time
import re
from carmensystems.dig.framework.handler import MessageHandlerBase,CallNextHandlerResult
from carmensystems.dig.framework import dave
from carmensystems.dig.messagehandlers.dave import DaveContentType
import Etab
import AbsTime
import RelTime


PRODUCTION_DATE = AbsTime.AbsTime("01May2009 00:00")

class TableUpdater(object):
    def __init__(self, services, etable, periodStart, periodEnd):
        self.daveConnector = services.getDaveConnector()
        self.logger = services.logger
        self.etable = etable
        self.periodStart = periodStart
        self.periodEnd = periodEnd

        self.etab_cache = {}
        self.dtab_cache = {}

        self.attrColName  = 'attr'        
        self.valueColName = 'value_str'
        
        # Override these
        self.crewColName = None
        self.tableName = None

    def initColVars(self):
        """
        Helper method for constructor, should be called from a subclass
        """
        self.crewCol  = self.etable.getColumnPos(self.crewColName) - 1
        self.attrCol  = self.etable.getColumnPos(self.attrColName) - 1
        self.valueCol = self.etable.getColumnPos(self.valueColName)- 1
        
    def doSearch(self):
        """
        This method must fill the self.dtab_cache with the attributes that are in
        the database.
        """
        raise NotImplementedError

    def legMatch(self, eitem, ditem):
        """
        Returns true if eitem and ditem is on the same leg
        """
        raise NotImplementedError

    def getRowAsObject(self, row):
        """
        Returns the etable row as a dictionary instead. Must convert items from strings
        to the same datatypes returned by a daveConnector().search
        """
        raise NotImplementedError

    def handleUpdate(self):
        """
        Method that performs the gathering of data and outputs a list of dave operations
        that when executed by a DaveWriter makes the database for the selected period
        match how the etable looks.
        """
        # Collect the DAVE data
        self.doSearch()

        # Collect the etable data
        for row in self.etable:
            rowObj = self.getRowAsObject(row)
            if not rowObj:
                continue
            try:
                self.etab_cache[rowObj[self.crewColName]].append(rowObj)
            except KeyError:
                self.etab_cache[rowObj[self.crewColName]] = [rowObj]

        ops = []
        for crew in self.etab_cache.keys():
            etab_list = self.etab_cache[crew]
            try:
                dtab_list = self.dtab_cache[crew]
            except KeyError:
                dtab_list = []

            e_remove_list = []
            # Sometimes the same row appears twice or more in etab file
            for eitem in etab_list:
                count = etab_list.count(eitem)
                if count > 1 and e_remove_list.count(eitem) == 0:
                    for x in [eitem]*(count-1):
                        e_remove_list.append(x)
            for item in e_remove_list:
                etab_list.remove(item)
                
            e_remove_list = []
            for eitem in etab_list:
                d_remove_list = []
                for ditem in dtab_list:
                    if self.legMatch(eitem, ditem):
                        #Now we know we are on the same leg, see if attr is the the same
                        if eitem[self.valueColName] != ditem[self.valueColName]:
                            ops.append(dave.createOp(self.tableName,'U',eitem))
                            self.logger.debug("Update! \nETABLE: %s\nDTABLE: %s\n---" %(eitem,ditem))
                        d_remove_list.append(ditem)
                        e_remove_list.append(eitem)
                        break
                for item in d_remove_list:
                    dtab_list.remove(item)
            for item in e_remove_list:
                etab_list.remove(item)

            for eitem in etab_list:
                ops.append(dave.createOp(self.tableName, 'W', eitem))
                etab_list.remove(eitem)
                self.logger.debug("Create! \nETABLE: %s\n---" %(eitem))

        for crew in self.dtab_cache.keys():
            dtab_list = self.dtab_cache[crew]
            for ditem in dtab_list:
                ops.append(dave.createOp(self.tableName, 'D', ditem))
                dtab_list.remove(ditem)
                self.logger.debug("Delete! \nDTABLE: %s\n---" %(ditem))

        return ops

                    
                    
class CrewFlightDutyAttrUpdater(TableUpdater):
    """
    Specialized updater for flight assignment attributes
    """
    def __init__(self, services, etable, periodStart, periodEnd):
        TableUpdater.__init__(self, services, etable, periodStart, periodEnd)
        self.crewColName  = 'cfd_crew'
        self.tableName = 'crew_flight_duty_attr'
        self.initColVars()
        
        self.etabCrewCol  = self.etable.getColumnPos('ca_crew') - 1
        
    def legMatch(self, eitem, ditem):
        return (eitem['cfd_leg_udor'] == ditem['cfd_leg_udor']) and \
               (eitem['cfd_leg_adep'] == ditem['cfd_leg_adep']) and \
               (eitem['cfd_leg_fd']   == ditem['cfd_leg_fd'])

    def getRowAsObject(self, row):
        if row[self.attrCol] == 'TRAINING':
            legTime = AbsTime.AbsTime(row[self.etable.getColumnPos('cfd_leg_udor') - 1])
            if legTime < self.periodStart or legTime >= self.periodEnd:
                return None
            d = {}
            d[self.crewColName]  = row[self.crewCol]
            d[self.valueColName] = row[self.valueCol]
            d[self.attrColName]  = row[self.attrCol]
            d['cfd_leg_udor'] = int(AbsTime.AbsTime(row[self.etable.getColumnPos('cfd_leg_udor') - 1]))/1440
            d['cfd_leg_adep'] = row[self.etable.getColumnPos('cfd_leg_adep') - 1] 
            d['cfd_leg_fd']   = row[self.etable.getColumnPos('cfd_leg_fd') - 1] 
            return d
        else:
            return None
        pass
    
    def doSearch(self):
        search = dave.DaveSearch('crew_flight_duty_attr', [('cfd_leg_udor','>=',int(self.periodStart)/1440),
                                                           ('cfd_leg_udor','<', int(self.periodEnd)/1440),
                                                           ('attr', '=', 'TRAINING')])
    
        for r in self.daveConnector.runSearch(search):
            try:
                self.dtab_cache[r[self.crewColName]].append(r)
            except KeyError:
                self.dtab_cache[r[self.crewColName]] = [r]


class Ti5(MessageHandlerBase):
    """
    Attempts to find crew_flight_duty_attr.etab and, and if
    found will apply a diff to the database so that it matches the table.

    This messagehandler does not care for referential integrity.
    """
    def __init__(self, name=None):
        super(Ti5, self).__init__(name)

    def handle(self, message):
        # Find the filename of input file
        try:
            meta = message.metadata['carmensystems.dig.readers.file.type.FileForMessage']
        except KeyError:
            raise MessageError("Key not found in metadata: %s" % str(KeyError))
        
        file = None
        for obj in meta:
            if isinstance(obj, str):
                file = obj
                break

        if not file:
            raise MessageError("Message have no file associated with it")

        self._services.logger.debug("Using file: %s as input" % (file))


        # Get the start and end dates of the period to sync, lets start the sync at the 1st of the previous month
        # and sync all the way till PRODUCTION_START, which must be set to where Rostering starts to make
        # rosters in our CMS system
        timeObj = time.gmtime()
        currentTime = AbsTime.AbsTime(timeObj[0], timeObj[1], timeObj[2], timeObj[3], timeObj[4])
        periodStart = (currentTime.month_floor() - RelTime.RelTime("00:01")).month_floor()
        periodEnd = PRODUCTION_DATE

        if 'crew_flight_duty_attr.etab' in file:
            etab = Etab.Etable(file)
            updater = CrewFlightDutyAttrUpdater(self._services, etab, periodStart, periodEnd)
            ops = updater.handleUpdate()
            message.setContent((None, None,ops), DaveContentType())
        else:
            self._services.logger.debug("Unknown file: %s" % (file))
        
        return CallNextHandlerResult()
    