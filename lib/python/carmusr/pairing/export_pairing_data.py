

from modelserver import EntityNotFoundError
from AbsTime import AbsTime
import carmensystems.rave.api as R
import Gui
from utils.rave import RaveIterator as RI
from utils.rave import RaveEvaluator as RE
from utils.time_util import Period
from utils.time_util import copy
from time import sleep
import sys
import os
from subprocess import call
from RelTime import RelTime
from AbsTime import AbsTime
from tm import TM, TMC
import carmensystems.common.ServiceConfig as ServiceConfig
from utils import dataConverter
PRNGS = 'PRNGS'
TMTBL = 'TMTBL'
CLCTD = 'CLCTD'
CONTEXT = 'sp_crrs'

CURRENTDATE = 'CURRENTDATE'
PAIRING_GROUP = 'PAIRING_GROUP'
BLOCKTIME = 'BLOCKTIME'
MANDAYS = 'MANDAYS'
PRODUCTIVITY = 'PRODUCTIVITY'
LONGHAULSTARTS = 'LONGHAULSTARTS'
LAYOVERS = 'LAYOVERS'
STANDBYDAYS = 'STANDBYDAYS'
NO6DAYTRIPS = 'NO6DAYTRIPS'
NO12HOURDUTY = 'NO12HOURDUTY'
DRIVERNAME = 'Pairings'
ABSTIME = 'AbsTime'
BOOLEAN = 'Boolean'
INTEGER = 'Integer'
RELTIME = 'RelTime'
STRING = 'String'
ADAY = RelTime('24:00')

class ExportPairingData(object):
    
    def __init__(self, start, end, driverName = 'Pairings', crew_cat = 'F', toDataBase = True, etabFileName = None):
        self._tm = None
        self.startDate = start
        self.endDate = end
        self.timeTableDates = []
        self._bases = None
        self._categories = None
        self._ac_types = None
        self.toDataBase = toDataBase
        self.crew_cat = crew_cat
        if driverName is None or len(driverName) <= 0:
            self.driverName = DRIVERNAME
        else:
            self.driverName = driverName
        if etabFileName is None:
            self.etabFileName = self.getCARMTMP() + '/pairing_volume.etab'
        else:
            self.etabFileName = etabFileName
        self.etabFile = None
        self._categoriesDict = {'FC': 'F', 'FP': 'F', 'FR': 'F', 'AS': 'C', 'AP': 'C', 'AH': 'C'}

    def getTM(self):
        if self._tm is None:
            c = ServiceConfig.ServiceConfig()
            (key,database) = c.getProperty("db/url")
            (key,schema) = c.getProperty("db/schema")
            self._tm = TMC(database, schema)
        return self._tm

    def getBases(self):
        if self._bases is None:
            try:
                self._bases = R.set('crg_cmp_report.bases_to_export').members()
            except:
                print "could not get bases from rave" 
                self._bases = ['STO', 'OSL', 'CPH']
            self._bases = ['STO', 'OSL', 'CPH']
        return self._bases

    def getCategories(self):
        if self._categories is None:
            try:
                self._categories = R.set('crg_cmp_report.categories_to_export').members()
            except:
                print "could not get categories from rave" 
                self._categories = ['FC', 'FP', 'FR', 'AS', 'AP', 'AH']
            
        return self._categories

    def getAcTypes(self):
        if self._ac_types is None:
            try:
                self._ac_types = R.set('crg_cmp_report.aircraft_types_to_export').members()
            except:
                print "could not get ac from rave" 
                self._ac_types = ['F50', "Q400",  "B737", "MD90", "MD80", "A320", "A330", "A340", "CRJ"]
        return self._ac_types
        

    def export(self):
        if self.toDataBase:
            self.exportToDataBase()
        else:
            self.exportToEtab()

    def exportToEtab(self):
        self.etabFile = open(self.etabFileName, 'w')
        try:
            self.generateEtabHeader()
            self.exportData()
        finally:
            self.etabFile.close()
        command =  "$CARMSYS/bin/$ARCH/etabdiff -c $DB_URL -s $DB_SCHEMA -n -a " + self.etabFileName
        try:
            os.system(command)
        except OSError, e:
            print command + " gave exception:\n" + str(e)
            
    def exportToDataBase(self):
        #There is no longer a need to remove old data as the new data will overwritten
        #self.deleteOldData()
        self.getTM().pairing_volume
        self.getTM().newState()
        self.exportData()
        self.getTM().save()
        

    def getCARMTMP(self):
        return os.getenv('CARMTMP')

    def getPairingGroupSearchString(self):
        searchString = '(|'
        for cat in self.getCategories():
            crew_cat = self.getCrewCatForCategory(cat)
            for base in self.getBases():
                for ac_type in self.getAcTypes():
                    searchString += '(&(pairinggroup.id = '+ cat + base + ac_type + ')( pairinggroup.cat = ' + crew_cat + '))'
        searchString += ')'
        return searchString

    def generateEtabHeader(self):
        self.etabFile.write('8\n\
Spairinggroup_cat,\n\
Spairinggroup_id,\n\
Adt,\n\
Sdrivername,\n\
Smetadata,\n\
Ssource,\n\
Svaluetype,\n\
Sdata,\n')

    def addPairingData(self, pairinggroup, category, aDate, drivername, metadata, source, valuetype, data):
        crew_cat = self.getCrewCatForCategory(category)
        if self.toDataBase:
            self.addPairingDataToDataBase(pairinggroup, crew_cat, aDate, drivername, metadata, source, valuetype, data)
        else:
            self.addPairingDataToEtab(pairinggroup, crew_cat, aDate, drivername, metadata, source, valuetype, data)

    def addPairingDataToDataBase(self, pairinggroup, crew_cat, aDate, drivername, metadata, source, valuetype, data):
        if (not data) or (data == '0'):
            print "returning..  ", data
            return
        print data
        pairinggroupEnt = self.getPairingGroupEnt(pairinggroup, crew_cat)
        metadataEnt = self.getMetaDataEnt(metadata)
        sourceEnt = self.getSourceEnt(source)
        valuetypeEnt = self.getValueTypeEnt(valuetype)
        try:
            ent = self.getTM().pairing_volume[(pairinggroupEnt, aDate, drivername, metadataEnt)]
        except EntityNotFoundError:
            ent = self.getTM().pairing_volume.create((pairinggroupEnt, aDate, drivername, metadataEnt))
        ent.source = sourceEnt
        ent.valuetype = valuetypeEnt
        ent.data = data
        
    def getPairingGroupEnt(self, pairinggroup, crew_cat):
        try:
            ent = self.getTM().pairing_group_set[(pairinggroup,crew_cat)]
        except:
            ent = self.getTM().pairing_group_set.create((pairinggroup,crew_cat))
        return ent
    
    def getMetaDataEnt(self, metadata):
        try:
            ent = self.getTM().pairing_metadata_set[(metadata,)]
        except:
            ent = self.getTM().pairing_metadata_set.create((metadata,))
        return ent
            
    def getSourceEnt(self, source):
        try:
            ent = self.getTM().source_set[(source,)]
        except:
            ent = self.getTM().source_set.create((source,))
        return ent
            
    def getValueTypeEnt(self, valuetype):
        try:
            ent = self.getTM().param_type_set[(valuetype,)]
        except:
            ent = self.getTM().param_type_set.create((valuetype,))
        return ent
            
    def addPairingDataToEtab(self, pairinggroup, crew_cat, aDate, drivername, metadata, source, valuetype, data):
        self.etabFile.write('"' + crew_cat + '","' + str(pairinggroup)+ '", ' + aDate.ddmonyyyy() + ', "' + str(drivername)+'", "' + str(metadata) +'", "'+ str(source) + '", "' + str(valuetype) +'", "'+ str(data) +'";\n')

    def exportData(self):
        currentDate = copy(self.startDate)
        while (currentDate <= self.endDate):
            self.exportDataForDate(currentDate)
            currentDate = currentDate.adddays(1)
        self.exportDataForTimeTable()

    def getExportTypeForDate(self, aDate):
        return R.eval('crg_cmp_report.%period_type_for_date%('+ str(aDate) + ')')[0]

    def exportDataForDate(self, curDate):
        exportType = self.getExportTypeForDate(curDate)
        if exportType == PRNGS:
            self.exportDataForPairingsDate(curDate)
        elif exportType == TMTBL:
            self.timeTableDates.append(curDate)
        elif exportType == CLCTD:
           self.exportDataForFleetPlanDate (curDate)
        else:
            Gui.GuiWarning('There is no valid type for date %s, Please change in CMP/CMP_period_types etab' % curDate.ddmonyyyy())
            print 'unknown type' + str(exportType)
            
    def exportDataForPairingsDate(self, curDate):
        for category in self.getCategories():
            self.exportDataForPairingsCategoryDate(curDate, category)

    def getCrewCatForCategory(self, category):
        return self._categoriesDict[category]
    
    def exportDataForPairingsCategoryDate(self, curDate, category):
        trip_select = 'crg_cmp_report.%trip_to_export%'
        trips_on_date = RI(R.iter('crg_cmp_report.homebase_acqual_group_trip_set', where = trip_select),{
            PAIRING_GROUP: 'crg_cmp_report.%pairing_group_pairing%("' + category + '")',
            MANDAYS: 'crg_cmp_report.%mandays_on_date_from_pairings%(' + str(curDate) + ', "' + category + '")'}).eval(CONTEXT)
        for trip_with_same_base_acqual_on_date in trips_on_date:
            self.addPairingData(trip_with_same_base_acqual_on_date.PAIRING_GROUP, category, curDate, self.driverName,  MANDAYS, PRNGS,
                                dataConverter.INTEGER,
                                dataConverter.DataConverter.convertToData(dataConverter.INTEGER, trip_with_same_base_acqual_on_date.MANDAYS))
    
    def exportDataForTimeTable(self):
        periods = self.getTimeTablePeriods()
        for period in periods:
            self.exportDataForTimeTablePeriod(period)

    def getTimeTablePeriods(self):
        periods = []
        startDate = None
        endDate = None
        prevDate = None
        sortedDates = self.timeTableDates.sort()
        if self.timeTableDates is not None and len(self.timeTableDates) > 0:
            for date in self.timeTableDates:
                if startDate is None:
                    startDate = date
                    endDate = date
                    if prevDate is not None and (date - prevDate > ADAY):
                        periods.append(Period(startDate, prevDate))
                        startDate = date
                        prevDate = None
                else:
                    prevDate = date
                    endDate = date
            periods.append(Period(startDate, endDate))
        return periods

    def exportDataForTimeTablePeriod(self, period):
        for category in self.getCategories():
            self.exportDataForTimeTableCategoryPeriod(period, category)

    def exportDataForTimeTableCategoryPeriod(self, period, category):
        for base in self.getBases():
            self.exportDataForTimeTableCategoryBasePeriod(period, category, base)
            
    def exportDataForTimeTableCategoryBasePeriod(self, period, category, base):
        leg_select = 'crg_cmp_report.%%leg_in_period%%(%s,%s)' \
                     % (period.start(),period.end())
        legs_on_dates = RI(R.iter('crg_cmp_report.start_date_leg_set',where= leg_select),{
            CURRENTDATE: 'carmen_manpower_crew_need.%leg_start_date%',
            PAIRING_GROUP: 'crg_cmp_report.%pairing_group_time_table%("' + category + '","' + base + '")',
            MANDAYS: 'crg_cmp_report.%mandays_from_timetable_leg_set_func%("' + category + '","' + base + '")',
            }).eval(CONTEXT)
        for legs_on_date in legs_on_dates:
            self.addPairingData(legs_on_date.PAIRING_GROUP, category, legs_on_date.CURRENTDATE, self.driverName,  MANDAYS, TMTBL,
                                dataConverter.INTEGER,
                                dataConverter.DataConverter.convertToData(dataConverter.INTEGER, legs_on_date.MANDAYS))
        
    def exportDataForFleetPlanDate(self, curDate):
        for category in self.getCategories():
            self.exportDataForFleetPlanCategoryDate(curDate, category)

    def exportDataForFleetPlanCategoryDate(self, curDate, category):
        for base in self.getBases():
            self.exportDataForFleetPlanCategoryBaseDate(curDate, category, base)

    def exportDataForFleetPlanCategoryBaseDate(self, curDate, category, base):
        for acType in self.getAcTypes():
            self.exportDataForFleetPlanCategoryBaseAcTypeDate(curDate, category, base, acType)

    def exportDataForFleetPlanCategoryBaseAcTypeDate(self, curDate, category, base, acType):
        if self.exportDataForFleetPlan(category, base, acType):
            evalDict = {
                PAIRING_GROUP: 'crg_cmp_report.%pairing_group_fleet_plan%("' + category + '","' + acType + '","' + base + '")',
                MANDAYS: 'crg_cmp_report.%mandays_on_date_from_calculation%('  + str(curDate) + ',"' + category + '","' + acType + '","' + base + '")'}
            dataForDateAndCategory = RE.rEvalDict(context=CONTEXT, **evalDict)
            self.addPairingData(dataForDateAndCategory[PAIRING_GROUP], category, curDate, self.driverName,  MANDAYS, CLCTD,
                                dataConverter.INTEGER,
                                dataConverter.DataConverter.convertToData(dataConverter.INTEGER, dataForDateAndCategory[MANDAYS]))
        else:
            pass

    def exportDataForFleetPlan(self, category, base, acType):
        return R.eval('crg_cmp_report.%export_data_for_fleet_plan%("' + category + '","' + acType + '","' + base + '")')[0]
